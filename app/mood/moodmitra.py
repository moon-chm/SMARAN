import logging
from typing import Dict, Any, Optional
from app.graph.connection import neo4j_manager

logger = logging.getLogger("smaran.mood.moodmitra")

GET_BEST_CONTENT = """
MATCH (c:ContentItem)
WHERE c.elder_id = $elder_id OR c.elder_id = "global"
// Optionally filter based on past effectiveness mapping
// E.g., Match elder -> CALMED_BY -> ContentItem
// For now, sorting by an abstract effectiveness_score property
RETURN c.id as id, c.title as title, c.url as url, c.media_type as type, coalesce(c.effectiveness_score, 1.0) as score
ORDER BY score DESC LIMIT 1
"""

UPDATE_CONTENT_SCORE = """
MATCH (c:ContentItem {id: $content_id})
SET c.effectiveness_score = coalesce(c.effectiveness_score, 1.0) + $adjustment
RETURN c.effectiveness_score as new_score
"""

class MoodMitra:
    def __init__(self):
        self.trigger_moods = {"sad", "lonely", "anxious"}
        self.consecutive_negative_moods: Dict[str, int] = {}
        
    async def evaluate_trigger(self, elder_id: str, detected_mood: str) -> Optional[Dict[str, Any]]:
        """
        If mood matches triggers, queries Neo4j for the most effective ContentItem to recommend.
        """
        alert_flag = False
        if detected_mood in self.trigger_moods:
            self.consecutive_negative_moods[elder_id] = self.consecutive_negative_moods.get(elder_id, 0) + 1
            if self.consecutive_negative_moods[elder_id] >= 3:
                alert_flag = True
        else:
            self.consecutive_negative_moods[elder_id] = 0

        if detected_mood not in self.trigger_moods and not alert_flag:
            return None
            
        try:
            async with await neo4j_manager.get_session(elder_id) as session:
                res = await session.run(GET_BEST_CONTENT, elder_id=elder_id)
                record = await res.single()
                
                content = None
                if record:
                    content = {
                        "id": record["id"],
                        "title": record["title"],
                        "url": record["url"],
                        "media_type": record["type"],
                        "effectiveness_score": record["score"]
                    }
                    logger.info(f"MoodMitra triggered for {detected_mood}. Recommending content {content['id']}")
                else:
                    logger.warning("No ContentItems found in Graph for MoodMitra.")
                
                if content or alert_flag:
                    result = {}
                    if content: result.update(content)
                    if alert_flag: result["alert_triggered"] = True
                    return result if result else None
                return None
        except Exception as e:
            logger.error(f"MoodMitra evaluation error: {e}")
            return None

    async def register_feedback(self, elder_id: str, content_id: str, success: bool):
        """
        Allows caregiver or elder UI to adjust the graph's effectiveness score.
        """
        adjustment = 0.5 if success else -0.5
        try:
            async with await neo4j_manager.get_session(elder_id) as session:
                await session.run(UPDATE_CONTENT_SCORE, content_id=content_id, adjustment=adjustment)
                logger.info(f"Updated effectiveness for content {content_id} by {adjustment}")
        except Exception as e:
            logger.error(f"MoodMitra feedback error: {e}")


mood_mitra = MoodMitra()
