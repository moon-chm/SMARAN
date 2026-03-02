import logging
from datetime import datetime
from app.graph.connection import neo4j_manager

logger = logging.getLogger("smaran.audit_log")

LOG_EVENT_QUERY = """
MERGE (e:Elder {id: $elder_id})
CREATE (a:AuditLog {
    id: randomUUID(),
    elder_id: $elder_id,
    event_type: $event_type,
    detail: $detail,
    timestamp: $timestamp
})
MERGE (e)-[:HAS_AUDIT_LOG]->(a)
"""

async def log_event(elder_id: str, event_type: str, detail: str, timestamp: str = None):
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()
    try:
        async with await neo4j_manager.get_session(elder_id) as session:
            await session.run(
                LOG_EVENT_QUERY,
                elder_id=elder_id,
                event_type=event_type,
                detail=detail,
                timestamp=timestamp
            )
    except Exception as e:
        logger.error(f"Failed to write audit log to Neo4j: {e}")


class AuditLogger:
    async def log_event(self, elder_id: str, event_type: str, detail: str, timestamp: str = None):
        await log_event(elder_id, event_type, detail, timestamp)


audit_logger = AuditLogger()