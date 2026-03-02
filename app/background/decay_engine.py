import logging
import asyncio
from typing import List
from datetime import datetime, timezone
from app.graph.connection import neo4j_manager
from app.background.audit_log import audit_logger

logger = logging.getLogger("smaran.background.decay")

# Query to find nodes that haven't been reinforced in >= 30 days
# And where confidence score hasn't hit absolute floor (0.1)
FIND_STAGNANT_MEMORIES = """
MATCH (e:Elder)-[]-(n)
WHERE n.last_reinforced_at IS NOT NULL 
  AND duration.between(datetime(n.last_reinforced_at), datetime()).days >= 30
  AND n.confidence_score > 0.1
RETURN e.id as elder_id, n.id as node_id, n.confidence_score as old_score
"""

DECAY_RATE = 0.05 # Drop confidence by 5%

UPDATE_NODE_CONFIDENCE = """
MATCH (n {id: $node_id})
SET n.confidence_score = $new_score
"""

class DecayEngine:
    async def run_daily_decay(self):
        """
        Executes the Memory Decay background job.
        For every elder, finds stagnant memories, decays them by 5%, and logs the audit.
        """
        logger.info("Starting Daily Memory Decay Engine run.")
        
        try:
            # Note: A real deployment would query Elders sequentially to get proper isolated sessions.
            # We'll mock a "global" system-wide sweep query on the default graph for now, then handle updates individually.
            # Assuming single Aura instance for all elders.
            
            stagnant_nodes = []
            
            # Since our architecture strictly uses per-elder databases via multi-schema maps (potentially), 
            # we must iterate over active elders. For demo, we assume aura DB handles unified graph with elder_id prop.
            # Let's perform a unified read.
            async with await neo4j_manager.get_session("system") as session:
                res = await session.run(FIND_STAGNANT_MEMORIES)
                async for record in res:
                    stagnant_nodes.append(dict(record))
                    
            if not stagnant_nodes:
                logger.info("No stagnant memories found today.")
                return
                
            logger.info(f"Found {len(stagnant_nodes)} nodes eligible for decay.")
            
            # Process Decays
            for node in stagnant_nodes:
                old_score = float(node["old_score"])
                new_score = max(0.1, old_score - DECAY_RATE)
                
                async with await neo4j_manager.get_session(str(node["elder_id"])) as session:
                    await session.run(UPDATE_NODE_CONFIDENCE, node_id=node["node_id"], new_score=new_score)
                    
                # Audit
                await audit_logger.log_decay(
                    elder_id=str(node["elder_id"]),
                    node_id=str(node["node_id"]),
                    old_score=old_score,
                    new_score=new_score
                )
                
            logger.info("Daily Memory Decay Run Complete.")
            
        except Exception as e:
            logger.error(f"Error executing Decay Engine: {e}")

decay_engine = DecayEngine()
