from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import logging
import os
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Dict, Any

from app.core.config import settings
from app.api import memory, chat, auth
from app.voice import upload as voice_upload
from app.graph.init_graph import initialize_graph
from app.graph.connection import neo4j_manager
from app.background.decay_engine import decay_engine
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("smaran")

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    logger.info("Starting SMARAN API...")
    os.makedirs("data/faiss_indexes", exist_ok=True)
    os.makedirs("data/voice_profiles", exist_ok=True)
    
    try:
        await initialize_graph()
    except Exception as e:
        logger.error(f"Failed during Neo4j graph init, moving on: {e}")
        
    try:
        # Schedule Decay Engine Daily at 02:00 AM (server time)
        scheduler.add_job(decay_engine.run_daily_decay, 'cron', hour=2, minute=0)
        scheduler.start()
        logger.info("APScheduler started: Daily Memory Decay active.")
    except Exception as e:
        logger.error(f"Failed to start APScheduler: {e}")
        
    yield
    # Shutdown: Clean up resources
    try:
        scheduler.shutdown()
        await neo4j_manager.close()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    logger.info("Shutting down SMARAN API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="Graph-Based Emotionally Intelligent Memory System for Elder Care"
)

# Add rate limiter state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routers
app.include_router(auth.router)
app.include_router(memory.router)
app.include_router(chat.router)
app.include_router(voice_upload.router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Time: {process_time:.4f}s"
    )
    return response

@app.get("/health", response_model=Dict[str, Any])
@limiter.limit("5/minute")
async def health_check(request: Request):
    """
    Health check endpoint returning app status.
    """
    logger.info("Health check endpoint called")
    return {
        "status": "online",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }
