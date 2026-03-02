import logging
from typing import Dict, Any, Optional
from app.graph.connection import neo4j_manager

logger = logging.getLogger("smaran.services.conflict")

# Check for existing node of same type and name, but different critical attributes (e.g. dosage, datetime)
# For Phase 6, we focus specifically on Medicine Dosage conflicts
DETECT_MEDICINE_CONFLICT = """
MATCH (e:Elder {id: $elder_id})-[r:TAKES_MEDICINE]->(m:Medicine {name: $name})
WHERE m.id <> $new_node_id AND m.dosage <> $new_dosage
RETURN m.id as old_id, m.dosage as old_dosage, m.created_at as old_created_at
ORDER BY m.created_at DESC LIMIT 1
"""

CREATE_CONTRADICTS_REL = """
MATCH (old {id: $old_id}), (new {id: $new_id})
MERGE (new)-[r:CONTRADICTS {reason: $reason}]->(old)
RETURN r
"""

class ConflictGuard:
    async def check_medicine_conflict(self, elder_id: str, new_node_id: str, medicine_name: str, new_dosage: str) -> Optional[Dict[str, Any]]:
        """
        Scans graph for conflicting medicine entries (same name, different dosage).
        If found, establishes a CONTRADICTS relationship and returns alert context.
        """
        if not new_dosage:
            return None
            
        try:
            async with await neo4j_manager.get_session(elder_id) as session:
                res = await session.run(
                    DETECT_MEDICINE_CONFLICT, 
                    elder_id=elder_id, 
                    name=medicine_name, 
                    new_node_id=new_node_id,
                    new_dosage=new_dosage
                )
                record = await res.single()
                
                if record:
                    old_id = record["old_id"]
                    old_dosage = record["old_dosage"]
                    
                    reason = f"Dosage contradiction: {old_dosage} vs {new_dosage}"
                    
                    # Create contradiction tie
                    await session.run(
                        CREATE_CONTRADICTS_REL,
                        old_id=old_id,
                        new_id=new_node_id,
                        reason=reason
                    )
                    
                    logger.warning(f"Conflict Guard Triggered: {reason} on Medicine {medicine_name}")
                    return {
                        "conflict_detected": True,
                        "entity": medicine_name,
                        "old_value": old_dosage,
                        "new_value": new_dosage,
                        "resolution_rule": "Timestamp (Newer Wins)",
                        "caregiver_alert_required": True
                    }
                    
        except Exception as e:
            logger.error(f"Error in Conflict Guard: {e}")
            
        return None

conflict_guard = ConflictGuard()
