import logging
from app.graph.connection import neo4j_manager
from app.graph.queries import (
    CREATE_ELDER_INDEX,
    CREATE_GENERIC_NODE_ELDER_INDEX,
    CREATE_ELDER_CONSTRAINT,
    CREATE_NODE_CONSTRAINT,
    CREATE_USER_USERNAME_CONSTRAINT,
    CREATE_USER_EMAIL_CONSTRAINT
)

logger = logging.getLogger("smaran.graph.init")

async def initialize_graph():
    """Run initialization scripts against Neo4j to build indices and constraints."""
    logger.info("Initializing Neo4j Graph schema...")
    
    queries = [
        CREATE_ELDER_INDEX,
        CREATE_GENERIC_NODE_ELDER_INDEX,
        CREATE_ELDER_CONSTRAINT,
        CREATE_NODE_CONSTRAINT,
        CREATE_USER_USERNAME_CONSTRAINT,
        CREATE_USER_EMAIL_CONSTRAINT
    ]

    try:
        await neo4j_manager.connect()
        async with await neo4j_manager.get_session("system") as session:
            for query in queries:
                try:
                    await session.run(query)
                except Exception as query_err:
                    # Depending on Neo4j version/edition, constraint creation requires enterprise or similar handling
                    # We just log a warning if it fails because it already exists or not supported in Aura free tier
                    logger.warning(f"Query execution warning for {query}: {query_err}")
                    
        logger.info("Graph schema initialization completed.")
    except Exception as e:
        logger.error(f"Failed to initialize graph: {e}")
        # Note: Depending on strategy, we might not abort app startup if graph is temporarily down
