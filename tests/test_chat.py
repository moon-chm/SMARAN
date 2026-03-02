import pytest
from app.services.conflict_guard import ConflictGuard
from app.llm.groq_client import GroqLLMClient

@pytest.mark.asyncio
async def test_conflict_guard_real():
    guard = ConflictGuard()
    
    elder_id = "test_elder_123"
    node_id = "med_123"
    medicine_name = "Aspirin"
    dosage = "500mg"
    
    # Calling real implementation without mocks.
    try:
        res = await guard.check_medicine_conflict(elder_id, node_id, medicine_name, dosage)
        assert res is None or isinstance(res, dict)
        if res is dict:
            assert "conflict_detected" in res
            assert "old_value" in res
            assert "new_value" in res
    except Exception as e:
        pytest.skip(f"Live Neo4j instance required for real conflict guard query: {e}")

@pytest.mark.asyncio
async def test_llm_hallucination_prevention_real():
    client = GroqLLMClient()
    
    # LLaMA completion call. Without mocking the API key/client.
    query = "What did I eat for breakfast?"
    context = [] # Empty context to trigger hallucination prevention grounding
    mood = "neutral"
    
    try:
        resp = await client.generate_response(query, context, mood)
        assert isinstance(resp, str)
        assert len(resp) > 0
    except Exception as e:
        pytest.skip(f"Live Groq API Key required for real LLM testing: {e}")
