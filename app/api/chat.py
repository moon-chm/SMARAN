from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
import time
from datetime import datetime
from pydantic import BaseModel

from app.core.security import get_current_user, TokenData, verify_elder_self_access
from app.mood.classifier import mood_classifier
from app.mood.tracker import behavioral_tracker
from app.mood.moodmitra import mood_mitra
from app.retrieval.retriever import hybrid_retriever
from app.llm.groq_client import groq_client
from app.background.audit_log import log_event
from app.graph.connection import neo4j_manager
from app.graph.queries import MERGE_MEMORY_NODE
import os
import uuid
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from app.voice.tts_engine import tts_pipeline
from app.voice.openvoice import openvoice_pipeline
from app.voice.streamer import create_audio_response

logger = logging.getLogger("smaran.api.chat")

router = APIRouter(prefix="/api/chat", tags=["chat"], redirect_slashes=False)

# Fallback: fetch top memories directly from Neo4j when FAISS index is empty
FALLBACK_MEMORY_QUERY = """
MATCH (n)
WHERE n.elder_id = $elder_id
  AND (n.description IS NOT NULL OR n.name IS NOT NULL)
RETURN n, labels(n) as labels
ORDER BY n.confidence_score DESC
LIMIT $limit
"""

class ChatMessageRequest(BaseModel):
    elder_id: str
    message: str
    hour_of_day: Optional[int] = None
    return_audio: bool = False

class ChatMessageResponse(BaseModel):
    elder_id: str
    detected_mood: str
    mood_confidence: float
    reply: str
    moodmitra_recommendation: Optional[Dict[str, Any]] = None
    retrieval_time_ms: float = 0.0


async def get_fallback_memories(elder_id: str, top_k: int = 3) -> List[Dict]:
    """Fetch memories directly from Neo4j when FAISS returns nothing."""
    try:
        async with await neo4j_manager.get_session(elder_id) as session:
            result = await session.run(FALLBACK_MEMORY_QUERY, elder_id=elder_id, limit=top_k)
            records = await result.data()
            fallback = []
            for r in records:
                props = dict(r["n"])
                text = props.get("description") or props.get("name", "")
                if text:
                    # Build a dict that matches what groq_client expects from retrieved_context
                    fallback.append({
                        "id": props.get("id", ""),
                        "content": {
                            "labels": r.get("labels", []),
                            "properties": props
                        },
                        "similarity_score": props.get("confidence_score", 0.5),
                        "graph_distance": 0,
                        "final_score": props.get("confidence_score", 0.5)
                    })
            logger.info(f"Graph fallback returned {len(fallback)} memories for {elder_id}")
            return fallback
    except Exception as e:
        logger.error(f"Fallback memory fetch failed: {e}")
        return []


@router.post("")
@router.post("/")
async def process_chat(
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    verify_elder_self_access(request.elder_id, current_user)
    logger.info(f"Processing chat for elder {request.elder_id}")

    # 1. Detect Mood
    try:
        hour = request.hour_of_day if request.hour_of_day is not None else datetime.utcnow().hour
        mood_label, confidence = mood_classifier.detect_mood(request.message, hour)

        # 2. Track Mood
        await behavioral_tracker.track_mood(request.elder_id, mood_label, confidence, source_type="chat")

        # 3. MoodMitra Check
        recommendation = await mood_mitra.evaluate_trigger(request.elder_id, mood_label)

        # Ingest alert node if 3 consecutive negative moods
        if recommendation and recommendation.get("alert_triggered"):
            try:
                async with await neo4j_manager.get_session(request.elder_id) as session:
                    mem_id = str(uuid.uuid4())
                    await session.run(
                        MERGE_MEMORY_NODE,
                        elder_id=request.elder_id,
                        memory_id=mem_id,
                        description=f"Automated Alert: Elder has expressed {mood_label} mood for 3 consecutive interactions.",
                        emotion_tag=mood_label,
                        created_at=datetime.utcnow().isoformat(),
                        confidence_score=1.0,
                        source_type="mood_alert",
                        last_reinforced_at=datetime.utcnow().isoformat()
                    )
            except Exception as e:
                logger.error(f"Failed to ingest mood alert: {e}")

    except Exception as e:
        logger.error(f"Error in mood pipeline: {e}")
        mood_label, confidence = "neutral", 0.5
        recommendation = None

    # Emergency flag
    if request.message.startswith("EMERGENCY:"):
        background_tasks.add_task(log_event, request.elder_id, "EMERGENCY", request.message)

    # 4. Hybrid RAG retrieval
    start_time = time.time()
    try:
        retrieved_memories = await hybrid_retriever.retrieve(request.elder_id, request.message, top_k=3)
    except Exception as e:
        logger.error(f"Error retrieving FAISS memories: {e}")
        retrieved_memories = []

    # FIX: If FAISS returns nothing, fall back to direct Neo4j graph fetch
    if not retrieved_memories:
        logger.warning(f"FAISS returned 0 results for {request.elder_id} — using graph fallback.")
        fallback = await get_fallback_memories(request.elder_id, top_k=3)
        retrieved_context = fallback
    else:
        retrieved_context = [m.dict() for m in retrieved_memories]

    retrieval_time_ms = round((time.time() - start_time) * 1000, 2)

    # 5. Generate LLM response
    elder_name = current_user.full_name or current_user.username
    try:
        sys_reply = await groq_client.generate_response(
            message=request.message,
            retrieved_context=retrieved_context,
            detected_mood=mood_label,
            elder_name=elder_name
        )
    except Exception as e:
        logger.error(f"Groq generating error: {e}")
        sys_reply = "I'm having trouble thinking right now. Please try again."

    # Audit log
    background_tasks.add_task(log_event, request.elder_id, "CHAT", f"Elder: {request.message} | SMARAN: {sys_reply}")

    response_data = {
        "elder_id": request.elder_id,
        "detected_mood": mood_label,
        "mood_confidence": confidence,
        "reply": sys_reply,
        "moodmitra_recommendation": recommendation,
        "retrieval_time_ms": retrieval_time_ms
    }

    # 6. Voice generation
    if request.return_audio:
        try:
            voice_dir = os.path.join("data/voice_profiles", request.elder_id)
            profile_audio_path = None
            if os.path.exists(voice_dir):
                for f in os.listdir(voice_dir):
                    if f.endswith(('.wav', '.mp3', '.webm', '.mpeg')):
                        profile_audio_path = os.path.join(voice_dir, f)
                        break

            if profile_audio_path:
                logger.info("Using ElevenLabs Voice Cloning for profile.")
                final_wav = openvoice_pipeline.apply_tone_color(request.elder_id, sys_reply, profile_audio_path)
            else:
                logger.info("No valid audio profile found, falling back to ElevenLabs default.")
                final_wav = tts_pipeline.synthesize_speech(sys_reply)

            headers = {
                "X-Detected-Mood": mood_label,
                "X-Mood-Confidence": str(confidence),
                "X-Reply-Text": sys_reply.replace("\n", " "),
                "X-Retrieval-Time-Ms": str(retrieval_time_ms)
            }
            if recommendation:
                headers["X-MoodMitra-Triggered"] = str(recommendation.get('id', ''))

            return create_audio_response(final_wav, background_tasks, headers=headers)
        except Exception as e:
            logger.error(f"Voice generation failed: {e}. Falling back to text-only.")
            # Fall through to return JSONResponse

    return JSONResponse(content=response_data)