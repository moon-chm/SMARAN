import os
import shutil
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.core.security import get_current_user, TokenData, verify_elder_self_access

logger = logging.getLogger("smaran.voice.upload")

router = APIRouter(prefix="/api/voice", tags=["voice"])

VOICE_DIR = Path("data/voice_profiles")
VOICE_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_voice_sample(
    elder_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Secure voice sample upload for Coqui TTS cloning.
    Must be a valid audio file.
    """
    verify_elder_self_access(elder_id, current_user)

    # 1. Validation
    if file.content_type not in ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/webm"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Upload .wav or .mp3")
        
    # Check estimated size (rough check for 30s)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size < 300_000:
        logger.warning(f"Voice upload for {elder_id} is suspiciously small ({file_size} bytes)")

    # 2. Secure Storage Isolation
    elder_voice_dir = VOICE_DIR / elder_id
    elder_voice_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique profile ID
    voice_profile_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1]
    safe_filename = f"{voice_profile_id}.{extension}"
    file_path = elder_voice_dir / safe_filename
    
    # 3. Store
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Successfully uploaded voice profile {voice_profile_id} for elder {elder_id}")
        return {
            "status": "success",
            "voice_profile_id": voice_profile_id,
            "elder_id": elder_id,
            "format": extension
        }
    except Exception as e:
        logger.error(f"Failed to save voice profile: {e}")
        raise HTTPException(status_code=500, detail="Internal file storage error.")