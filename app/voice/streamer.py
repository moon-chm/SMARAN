import os
import aiofiles
from fastapi.responses import StreamingResponse
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger("smaran.voice.streamer")

async def audio_file_streamer(file_path: str):
    """
    Asynchronous generator to yield audio chunks.
    Ensures memory efficiency for large synthesis files.
    """
    chunk_size = 1024 * 64 # 64KB chunks
    try:
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(chunk_size):
                yield chunk
    except Exception as e:
        logger.error(f"Error streaming audio file {file_path}: {e}")
        yield b""

def remove_temp_file(file_path: str):
    """
    Background task to aggressively scrub temporary clone generation files.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted temp audio: {file_path}")
    except Exception as e:
        logger.error(f"Failed to delete temp audio {file_path}: {e}")

def create_audio_response(audio_path: str, background_tasks: BackgroundTasks, headers: dict = None) -> StreamingResponse:
    """
    Packages the streamer into a standard FastAPI Response with dynamic cleanups.
    """
    response = StreamingResponse(
        audio_file_streamer(audio_path),
        media_type="audio/wav",
        headers=headers
    )
    
    # We add cleanup to run *after* the stream successfully completes closing
    background_tasks.add_task(remove_temp_file, audio_path)
    
    return response
