from app.graph.schema import MoodNode
from app.graph.connection import neo4j_manager
import logging
from datetime import datetime

logger = logging.getLogger("smaran.mood.tracker")

MERGE_MOOD_NODE = """
MERGE (e:Elder {id: $elder_id})
CREATE (m:Mood {
    id: $node_id, 
    elder_id: $elder_id,
    state: $state, 
    intensity: coalesce($intensity, 5), 
    confidence_score: $confidence_score, 
    source_type: $source_type, 
    created_at: $created_at, 
    last_reinforced_at: $last_reinforced_at
})
MERGE (e)-[r:FEELS_MOOD]->(m)
RETURN m.id as node_id
"""

class BehavioralTracker:
    async def track_mood(self, elder_id: str, state: str, confidence: float, source_type: str = "chat"):
        """
        Stores isolated MoodNode instances dynamically attached to the Elder.
        Unlike single entities (like a specific Medicine), moods are point-in-time sequential,
        so we CREATE rather than MERGE on the exact same state node, tracking trends.
        """
        # Convert confidence to heuristic intensity 1-10
        intensity = max(1, min(10, int(confidence * 10)))
        
        try:
            node = MoodNode(
                elder_id=elder_id,
                state=state,
                intensity=intensity,
                confidence_score=confidence,
                source_type=source_type
            )
            
            async with await neo4j_manager.get_session(elder_id) as session:
                res = await session.run(
                    MERGE_MOOD_NODE,
                    elder_id=node.elder_id,
                    node_id=node.id,
                    state=node.state,
                    intensity=node.intensity,
                    confidence_score=node.confidence_score,
                    source_type=node.source_type,
                    created_at=node.created_at,
                    last_reinforced_at=node.last_reinforced_at
                )
                r = await res.single()
                if r:
                    logger.info(f"Stored mood '{state}' for elder {elder_id} as node {r['node_id']}")
                return node.id
        except Exception as e:
            logger.error(f"Failed to track mood in Neo4j: {e}")
            return None

behavioral_tracker = BehavioralTracker()
