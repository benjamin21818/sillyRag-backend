import sys
import os
import uuid
import edge_tts
import time
import json
from src.utils.conf import BASE_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Check out doc at https://github.com/rany2/edge-tts
# Use `edge-tts --list-voices` to list all available voices

class TTSEngine():
    def __init__(self, voice="zh-CN-XiaoxiaoNeural", rate="+0%", volume="+0%"):
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.file_extension = "mp3"


        upload_relative_path = "uploads/tts_voice"
        self.new_audio_dir = os.path.join(BASE_DIR, upload_relative_path)
        if not os.path.exists(self.new_audio_dir):
            os.makedirs(self.new_audio_dir)


    async def build_session_id(self, user_id: str, space_id: str = None) -> str:
        timestamp = int(time.time())
        if space_id:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}_{space_id}_{timestamp}"))
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}_{timestamp}"))


    async def generate_audio(self, text, user_id: str, space_id: str = None):
        if not text:
            logger.warning("TTS generation requested with empty text.")
            return None, 0.0

        session_id = await self.build_session_id(user_id, space_id)
        file_name = f"{session_id}.{self.file_extension}"
        file_path = os.path.join(self.new_audio_dir, file_name)
        metadata_path = f"{file_path}.json"

        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume)
            await communicate.save(file_path, metadata_path)
            logger.info(f"Audio generated successfully: {file_path}")
        except Exception as e:
            logger.error(f"Error: edge-tts unable to generate audio: {e}")
            logger.error("It's possible that edge-tts is blocked in your region.")
            return None, 0.0

        duration_seconds = 0.0
        try:
            with open(metadata_path, "r", encoding="utf-8") as metadata_file:
                for line in metadata_file:
                    if not line.strip():
                        continue
                    payload = json.loads(line)
                    offset = payload.get("offset", 0.0)
                    duration = payload.get("duration", 0.0)
                    duration_seconds = max(duration_seconds, (offset + duration) / 10_000_000)
        except Exception as e:
            logger.error(f"Error: failed to parse metadata for duration: {e}")
        finally:
            if os.path.exists(metadata_path):
                os.remove(metadata_path)

        return file_path, duration_seconds
