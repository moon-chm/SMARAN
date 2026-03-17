import os
import logging
import uuid
from pathlib import Path
from app.core.config import settings
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
except ImportError:
    ElevenLabs = None
    save = None

logger = logging.getLogger("smaran.voice.tts_engine")

TEMP_OUT_DIR = Path("data/voice_temp")
TEMP_OUT_DIR.mkdir(parents=True, exist_ok=True)

class ElevenLabsDefaultPipeline:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        if self.api_key and ElevenLabs:
            self.client = ElevenLabs(api_key=self.api_key)
        else:
            self.client = None

    def synthesize_speech(self, text: str) -> str:
        """
        Synthesizes speech using the ElevenLabs default voice.
        Returns the absolute Path string to the .wav output.
        """
        out_filename = f"gen_eleven_{uuid.uuid4().hex[:8]}.wav"
        out_path = str(TEMP_OUT_DIR / out_filename)
        
        if self.client:
            logger.info("Running ElevenLabs synthesize (default voice)...")
            try:
                audio = self.client.generate(
                    text=text,
                    voice="Rachel", 
                    model="eleven_multilingual_v2"
                )
                save(audio, out_path)
            except Exception as e:
                logger.error(f"ElevenLabs API error: {e}")
                raise RuntimeError(f"TTS generation failed: {e}")
        else:
            logger.error("ElevenLabs client missing or no API key")
            raise RuntimeError("ElevenLabs client missing or no API key")
            
        return out_path
        


tts_pipeline = ElevenLabsDefaultPipeline()
