import time
import logging
from typing import List, Dict, Any
from datetime import datetime
from app.retrieval.embedder import embedder
from app.retrieval.faiss_index import faiss_manager
from app.graph.connection import neo4j_manager
from pydantic import BaseModel

logger = logging.getLogger("smaran.retrieval.hybrid")

class RetrievedMemory(BaseModel):
    id: str
    content: Dict[str, Any]
    similarity_score: float
    graph_distance: int
    final_score: float

RETRIEVE_NODE_BY_ID = """
MATCH (n {id: $node_id}) 
WHERE n.elder_id = $elder_id
RETURN n as node, labels(n) as labels
"""

class HybridRetriever:
    def __init__(self):
        self.k_hop = 2
        
    def _calculate_recency_score(self, created_at: str, last_reinforced_at: str) -> float:
        """
        Calculates a rapid decay recency score based on reinforcement.
        """
        try:
            now = datetime.utcnow()
            target_time = datetime.fromisoformat(last_reinforced_at)
            days_diff = (now - target_time).days
            # Exponential decay: fresher memories score closer to 1.0, older taper off
            return max(0.1, 1.0 / (1.0 + (days_diff / 30.0)))
        except ValueError:
            return 0.5
            
    async def retrieve(self, elder_id: str, query: str, top_k: int = 5) -> List[RetrievedMemory]:
        """
        Executes a High-Performance Hybrid Retrieval:
        1. Embed the search query
        2. Fetch Semantic Matches from FAISS (Step 1)
        3. Fetch Neo4j Context (Step 2)
        4. Ranking (Step 3) 
        """
        start_time = time.time()
        
        # Step 1: FAISS semantic search
        query_vector = embedder.embed_text(query)
        faiss_results = faiss_manager.search(elder_id, query_vector, top_k=top_k*2)
        
        if not faiss_results:
            logger.info("Hybrid Retrieval took %.2fms (0 results from FAISS)", (time.time() - start_time)*1000)
            return []

        # FIX: Deduplicate FAISS results by node_id, keeping highest score per node
        seen_ids = {}
        for node_id, score in faiss_results:
            if node_id not in seen_ids or score > seen_ids[node_id]:
                seen_ids[node_id] = score

        faiss_candidates = seen_ids  # {node_id: best_score}
        
        # Step 2: Neo4j k-hop node data population
        hydrated_nodes: List[RetrievedMemory] = []
        try:
            async with await neo4j_manager.get_session(elder_id) as session:
                for node_id, sim_score in faiss_candidates.items():
                    res = await session.run(RETRIEVE_NODE_BY_ID, node_id=node_id, elder_id=elder_id)
                    record = await res.single()
                    
                    if record:
                        graph_node = record["node"]
                        props = dict(graph_node)
                        
                        # Step 3: Ranking Calculation
                        # (Similarity 40%) + (Graph Confidence 30%) + (Recency 30%)
                        
                        similarity_weight = sim_score * 0.4
                        confidence_weight = props.get("confidence_score", 1.0) * 0.3
                        
                        recency = self._calculate_recency_score(
                            str(props.get("created_at", "")),
                            str(props.get("last_reinforced_at", ""))
                        )
                        recency_weight = recency * 0.3
                        
                        final_score = similarity_weight + confidence_weight + recency_weight
                        
                        # Pack it
                        hydrated_nodes.append(RetrievedMemory(
                            id=node_id,
                            content={
                                "labels": record["labels"],
                                "properties": props
                            },
                            similarity_score=sim_score,
                            graph_distance=0,
                            final_score=final_score
                        ))
                        
        except Exception as e:
            logger.error(f"Error during graph hydration: {e}")
            
        # Sort by final score descending
        hydrated_nodes.sort(key=lambda x: x.final_score, reverse=True)
        final_list = hydrated_nodes[:top_k]
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Hybrid Retrieval completed in {elapsed:.2f}ms. Found {len(final_list)} results.")
        
        # Logging constraint >100ms warning
        if elapsed > 100:
            logger.warning("Retrieval time exceeded 100ms budget limit.")

        return final_list

hybrid_retriever = HybridRetriever()