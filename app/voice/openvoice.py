import logging
import uuid
import ssl
import httpx
from pathlib import Path
from app.core.config import settings

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
except ImportError:
    ElevenLabs = None
    save = None

logger = logging.getLogger("smaran.voice.openvoice")
TEMP_OUT_DIR = Path("data/voice_temp")
VOICE_DIR = Path("data/voice_profiles")
TEMP_OUT_DIR.mkdir(parents=True, exist_ok=True)


def _get_elevenlabs_client(api_key: str):
    """Create ElevenLabs client with SSL-tolerant httpx transport."""
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        transport = httpx.HTTPTransport(ssl=ssl_context)
        http_client = httpx.Client(transport=transport, timeout=30.0)
        return ElevenLabs(api_key=api_key, httpx_client=http_client)
    except TypeError:
        # Older SDK versions don't accept httpx_client parameter
        logger.warning("ElevenLabs SDK does not support httpx_client, using default client.")
        return ElevenLabs(api_key=api_key)


class ElevenLabsClonePipeline:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.client = None
        if self.api_key and ElevenLabs:
            try:
                self.client = _get_elevenlabs_client(self.api_key)
                logger.info("ElevenLabs client initialized successfully.")
            except Exception as e:
                logger.error(f"ElevenLabs client init failed: {e}")
                raise RuntimeError(f"ElevenLabs client init failed: {e}")

    def apply_tone_color(self, elder_id: str, text: str, profile_audio_path: str) -> str:
        """
        Synthesize speech using a cloned voice of the elder.
        If a voice_id is already cached for the elder, reuses it.
        Otherwise creates a new cloned voice and caches the voice_id.
        Raises an error on failure.
        """
        out_filename = f"final_{elder_id}_{uuid.uuid4().hex[:8]}.wav"
        final_out_path = str(TEMP_OUT_DIR / out_filename)

        client = self.client
        if not client:
            logger.error("ElevenLabs client unavailable.")
            raise RuntimeError("ElevenLabs client unavailable")

        elder_voice_dir = VOICE_DIR / elder_id
        elder_voice_dir.mkdir(parents=True, exist_ok=True)
        voice_id_file = elder_voice_dir / "elevenlabs_voice_id.txt"

        # Load cached voice_id if available
        voice_id = None
        if voice_id_file.exists():
            cached = voice_id_file.read_text().strip()
            if cached:
                voice_id = cached
                logger.info(f"Using cached ElevenLabs voice_id {voice_id} for elder {elder_id}")

        # Clone voice if no cached voice_id
        if not voice_id:
            logger.info(f"Cloning voice for elder {elder_id} using {profile_audio_path}")
            try:
                with open(profile_audio_path, "rb") as audio_file:
                    voice = client.voices.add(
                        name=f"Elder_{elder_id}_{uuid.uuid4().hex[:4]}",
                        description=f"Cloned voice for elder {elder_id}",
                        files=[audio_file]
                    )
                voice_id = voice.voice_id
                voice_id_file.write_text(voice_id)
                logger.info(f"Voice cloned successfully. voice_id={voice_id}")
            except Exception as e:
                logger.error(f"ElevenLabs voice cloning failed: {e}")
                raise RuntimeError(f"ElevenLabs voice cloning failed: {e}")

        # Generate speech with cloned voice
        logger.info(f"Generating speech with voice_id={voice_id} for elder {elder_id}")
        try:
            audio = client.generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2"
            )
            save(audio, final_out_path)
            logger.info(f"Audio saved to {final_out_path}")
        except Exception as e:
            logger.error(f"ElevenLabs speech generation failed: {e}")
            raise RuntimeError(f"ElevenLabs speech generation failed: {e}")

        return final_out_path




openvoice_pipeline = ElevenLabsClonePipeline()