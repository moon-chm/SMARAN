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
                self._write_dummy(out_path)
        else:
            logger.warning("Mocking TTS generation - ElevenLabs client missing or no API key")
            self._write_dummy(out_path)
            
        return out_path
        
    def _write_dummy(self, path: str):
        with open(path, "wb") as f:
            # minimal valid wav header so frontend doesn't crash
            import wave
            import struct
            with wave.open(path, "w") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                wav_file.writeframesraw(struct.pack('<h', 0))

tts_pipeline = ElevenLabsDefaultPipeline()
