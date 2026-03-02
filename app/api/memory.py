from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from datetime import datetime

from app.graph.schema import MemoryIngestRequest, MindmapResponse, EmotionalMemoryNode, MedicineNode, AppointmentNode, SymptomNode
from app.graph.connection import neo4j_manager
from app.graph.queries import MERGE_MEMORY_NODE, GET_MINDMAP_QUERY, MERGE_MEDICINE_NODE, MERGE_APPOINTMENT_NODE, MERGE_SYMPTOM_NODE, GET_APPOINTMENTS_QUERY, GET_SYMPTOMS_QUERY, GET_MEDICINES_QUERY, REINFORCE_NODE_QUERY
from app.core.security import get_current_user, TokenData, Role, require_role, verify_elder_self_access
from app.services.nlp_extractor import NLPExtractor
from app.services.entity_classifier import classify_entities
from app.retrieval.embedder import embedder
from app.retrieval.faiss_index import faiss_manager
from app.retrieval.retriever import hybrid_retriever
from app.services.conflict_guard import conflict_guard
from app.utils.graph_visualizer import graph_visualizer

logger = logging.getLogger("smaran.api.memory")

nlp_extractor = NLPExtractor()

router = APIRouter(prefix="/api/memory", tags=["memory"])

# Fallback query: fetch all memories from graph when FAISS returns nothing
FALLBACK_SEARCH_QUERY = """
MATCH (n)
WHERE n.elder_id = $elder_id
  AND (n.description IS NOT NULL OR n.name IS NOT NULL)
RETURN n, labels(n) as labels
ORDER BY n.confidence_score DESC
LIMIT $limit
"""

@router.post("/ingest", response_model=Dict[str, Any])
async def ingest_memory(
    request: MemoryIngestRequest, 
    current_user: TokenData = Depends(require_role(Role.CAREGIVER))
):
    logger.info(f"Ingesting memory for elder {request.elder_id}")
    
    extracted_data = nlp_extractor.extract(request.text)
    nodes = classify_entities(extracted_data, request.elder_id, request.source_type)
    
    created_nodes = []
    conflict_alerts = []

    try:
        async with await neo4j_manager.get_session(request.elder_id) as session:
            memory_node = EmotionalMemoryNode(
                elder_id=request.elder_id,
                description=request.text,
                emotion_tag="Neutral",
                source_type=request.source_type
            )
            result = await session.run(
                MERGE_MEMORY_NODE,
                elder_id=request.elder_id,
                memory_id=memory_node.id,
                description=memory_node.description,
                emotion_tag=memory_node.emotion_tag,
                created_at=memory_node.created_at,
                confidence_score=memory_node.confidence_score,
                source_type=memory_node.source_type,
                last_reinforced_at=memory_node.last_reinforced_at
            )
            record = await result.single()
            if record:
                created_nodes.append({"type": "EmotionalMemory", "id": record["node_id"], "confidence": record["confidence"]})
                mem_vector = embedder.embed_text(memory_node.description)
                faiss_manager.add_vector(request.elder_id, memory_node.id, mem_vector)
            
            for node in nodes:
                if isinstance(node, MedicineNode):
                    res = await session.run(MERGE_MEDICINE_NODE, elder_id=node.elder_id, node_id=node.id, name=node.name, dosage=node.dosage, created_at=node.created_at, confidence_score=node.confidence_score, source_type=node.source_type, last_reinforced_at=node.last_reinforced_at)
                    r = await res.single()
                    if r: 
                        node_id = r["node_id"]
                        created_nodes.append({"type": "Medicine", "id": node_id})
                        alert = await conflict_guard.check_medicine_conflict(request.elder_id, node_id, node.name, node.dosage)
                        if alert:
                            conflict_alerts.append(alert)
                
                elif isinstance(node, AppointmentNode):
                    res = await session.run(MERGE_APPOINTMENT_NODE, elder_id=node.elder_id, node_id=node.id, title=node.title, datetime=node.datetime_str, created_at=node.created_at, confidence_score=node.confidence_score, source_type=node.source_type, last_reinforced_at=node.last_reinforced_at)
                    r = await res.single()
                    if r: created_nodes.append({"type": "Appointment", "id": r["node_id"]})
                
                elif isinstance(node, SymptomNode):
                    res = await session.run(MERGE_SYMPTOM_NODE, elder_id=node.elder_id, node_id=node.id, name=node.name, severity=node.severity, created_at=node.created_at, confidence_score=node.confidence_score, source_type=node.source_type, last_reinforced_at=node.last_reinforced_at)
                    r = await res.single()
                    if r: created_nodes.append({"type": "Symptom", "id": r["node_id"]})
                
                elif isinstance(node, EmotionalMemoryNode):
                    res = await session.run(MERGE_MEMORY_NODE, elder_id=node.elder_id, memory_id=node.id, description=node.description, emotion_tag=node.emotion_tag, created_at=node.created_at, confidence_score=node.confidence_score, source_type=node.source_type, last_reinforced_at=node.last_reinforced_at)
                    r = await res.single()
                    if r: created_nodes.append({"type": "EmotionalMemory", "id": r["node_id"]})

        return {
            "status": "success",
            "elder_id": request.elder_id,
            "memory_text": request.text,
            "created_nodes": created_nodes,
            "conflict_alerts": conflict_alerts
        }

    except Exception as e:
        logger.error(f"Error ingesting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{elder_id}", response_model=Dict[str, Any])
async def search_memories(
    elder_id: str,
    query: str,
    top_k: int = 5,
    current_user: TokenData = Depends(get_current_user)
):
    verify_elder_self_access(elder_id, current_user)
    logger.info(f"Hybrid search requested by elder {elder_id}: '{query}'")
    
    try:
        results = await hybrid_retriever.retrieve(elder_id, query, top_k)

        # FIX: If FAISS returns nothing (e.g. after index clear), fallback to full graph fetch
        if not results:
            logger.warning(f"FAISS returned 0 results for {elder_id}, falling back to graph scan.")
            async with await neo4j_manager.get_session(elder_id) as session:
                res = await session.run(FALLBACK_SEARCH_QUERY, elder_id=elder_id, limit=top_k)
                records = await res.data()
                fallback_results = []
                for r in records:
                    props = dict(r["n"])
                    text = props.get("description") or props.get("name", "")
                    fallback_results.append({
                        "id": props.get("id", ""),
                        "semantic_score": props.get("confidence_score", 0.5),
                        "context": text,
                        "labels": r.get("labels", [])
                    })
                return {"status": "success", "query": query, "results": fallback_results}

        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "id": r.id,
                    "semantic_score": r.similarity_score,
                    "context": r.content.get("properties", {}).get("description")
                              or r.content.get("properties", {}).get("name", ""),
                    "labels": r.content.get("labels", [])
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"Search retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/mindmap/{elder_id}")
async def get_mindmap(
    elder_id: str, 
    current_user: TokenData = Depends(require_role(Role.CAREGIVER))
):
    logger.info(f"Fetching mindmap for elder {elder_id}")
    nodes: Dict[str, Any] = {}
    edges: List[Dict[str, Any]] = []

    try:
        async with await neo4j_manager.get_session(elder_id) as session:
            result = await session.run(GET_MINDMAP_QUERY, elder_id=elder_id)
            records = await result.data()

        path_nodes = []
        path_rels = []
        for record in records:
            path_nodes.extend(record.get("path_nodes", []))
            path_rels.extend(record.get("path_rels", []))

        for n in path_nodes:
            node_id = str(n.get("node_id") or n.get("id") or "")
            if node_id and node_id not in nodes:
                nodes[node_id] = {
                    "id": node_id,
                    "labels": n.get("labels", []),
                    "properties": {k: v for k, v in n.items() if k != "labels"}
                }

        for r in path_rels:
            edges.append({
                "id": str(r.get("id")),
                "type": r.get("type"),
                "source": str(r.get("source")),
                "target": str(r.get("target")),
                "properties": r
            })

        nodes_list = list(nodes.values())
        graph_html = graph_visualizer.generate_html(nodes_list, edges) if nodes_list else ""

        return {"elder_id": elder_id, "nodes": nodes_list, "edges": edges, "graph_html": graph_html}

    except Exception as e:
        logger.error(f"Error fetching mindmap: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving graph data")


@router.get("/appointments/{elder_id}")
async def get_appointments(elder_id: str, current_user: TokenData = Depends(get_current_user)):
    verify_elder_self_access(elder_id, current_user)
    try:
        async with await neo4j_manager.get_session(elder_id) as session:
            result = await session.run(GET_APPOINTMENTS_QUERY, elder_id=elder_id)
            records = await result.data()
            return {"status": "success", "data": records}
    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symptoms/{elder_id}")
async def get_symptoms(elder_id: str, current_user: TokenData = Depends(get_current_user)):
    verify_elder_self_access(elder_id, current_user)
    try:
        async with await neo4j_manager.get_session(elder_id) as session:
            result = await session.run(GET_SYMPTOMS_QUERY, elder_id=elder_id)
            records = await result.data()
            return {"status": "success", "data": records}
    except Exception as e:
        logger.error(f"Error fetching symptoms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/medicines/{elder_id}")
async def get_medicines(elder_id: str, current_user: TokenData = Depends(get_current_user)):
    verify_elder_self_access(elder_id, current_user)
    try:
        async with await neo4j_manager.get_session(elder_id) as session:
            result = await session.run(GET_MEDICINES_QUERY, elder_id=elder_id)
            records = await result.data()
            return {"status": "success", "data": records}
    except Exception as e:
        logger.error(f"Error fetching medicines: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reinforce/{node_id}")
async def reinforce_node(
    node_id: str,
    current_user: TokenData = Depends(require_role(Role.CAREGIVER))
):
    """
    FIX: was calling get_session() with no elder_id argument.
    Reinforce doesn't filter by elder so we use a global session approach —
    fetch the node first to get its elder_id, then reinforce.
    """
    # Step 1: find which elder owns this node
    FIND_ELDER_QUERY = "MATCH (n {id: $node_id}) RETURN n.elder_id AS elder_id LIMIT 1"
    
    try:
        # Use any valid elder session to find the node (node id is globally unique)
        async with await neo4j_manager.get_session("elder_123") as session:
            lookup = await session.run(FIND_ELDER_QUERY, node_id=node_id)
            record = await lookup.single()
            if not record:
                raise HTTPException(status_code=404, detail="Node not found")
            elder_id = record["elder_id"]

        # Step 2: reinforce using the correct elder session
        async with await neo4j_manager.get_session(elder_id) as session:
            result = await session.run(
                REINFORCE_NODE_QUERY,
                node_id=node_id,
                now=datetime.utcnow().isoformat()
            )
            record = await result.single()
            if record:
                return {
                    "status": "success",
                    "node_id": record["node_id"],
                    "new_confidence": record["confidence"]
                }
            else:
                raise HTTPException(status_code=404, detail="Node not found")

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error reinforcing node {node_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))