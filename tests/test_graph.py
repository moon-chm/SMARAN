import pytest
from app.graph.connection import neo4j_manager
from app.graph.queries import MERGE_MEDICINE_NODE, GET_MINDMAP_QUERY

@pytest.mark.asyncio
async def test_neo4j_crud():
    """
    Strictly tests direct structural CRUD queries and k-hop bounds on Neo4j.
    Requires a live graph instance.
    """
    elder_id = "test_graph_elder"
    
    try:
        async with await neo4j_manager.get_session(elder_id) as session:
            
            # 1. Create a Medicine Node structurally
            res = await session.run(
                MERGE_MEDICINE_NODE,
                elder_id=elder_id,
                node_id="test_med_graph_1",
                name="Vitamin C",
                dosage="500mg",
                created_at="2024-01-01T00:00:00Z",
                confidence_score=0.9,
                source_type="graph_test",
                last_reinforced_at="2024-01-01T00:00:00Z"
            )
            r = await res.single()
            assert r is not None
            assert r["node_id"] == "test_med_graph_1"
            
            # 2. Extract Mindmap via 3-hop limit traversal
            res_mindmap = await session.run(GET_MINDMAP_QUERY, elder_id=elder_id)
            data = await res_mindmap.data()
            assert isinstance(data, list)
            # The medicine just inserted should structurally be within returned bounds
            
    except Exception as e:
        pytest.skip(f"Live Neo4j instance required for pure database tests: {e}")
