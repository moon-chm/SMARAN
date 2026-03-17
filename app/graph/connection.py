from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings
import logging

logger = logging.getLogger("smaran.graph")

class Neo4jConnectionManager:
    def __init__(self):
        self.driver: AsyncDriver | None = None

    async def connect(self):
        try:
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_pool_size=50,
                connection_acquisition_timeout=60.0,
                connection_timeout=30,
                max_connection_lifetime=3600,
            )

            # Verify connectivity
            await self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j AuraDB.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def close(self):
        if self.driver is not None:
            await self.driver.close()
            logger.info("Neo4j connection closed.")

    async def get_session(self, elder_id: str):
        """
        Returns an async session.
        In Neo4j AuraDB, physical databases per tenant aren't easily supported on free/starter tiers.
        We enforce per-elder graph isolation primarily via labels and query parameter boundaries (`elder_id`).
        """
        if self.driver is None:
            await self.connect()
        return self.driver.session(default_access_mode="WRITE")


neo4j_manager = Neo4jConnectionManager()
