import time
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class VoiceHistoryHandler:

    def __init__(self):
        pass

    
    async def add_voice_history(
        self,
        session: AsyncSession,
        user_id: str,
        space_id: str,
        session_id: str,
        transcript: str,
        response: str,
        user_audio_url: str,
        ai_audio_url: str,
        user_audio_duration: float,
        ai_audio_duration: float,
    ):
       
        if not session_id:
            session_id = self.build_session_id(user_id, space_id)
        await session.execute(
            text(
                """
                INSERT INTO voice_history
                (user_id, space_id, session_id, transcript, response, user_audio_url, ai_audio_url, user_audio_duration, ai_audio_duration)
                VALUES (:user_id, :space_id, :session_id, :transcript, :response, :user_audio_url, :ai_audio_url, :user_audio_duration, :ai_audio_duration)
                """
            ),
            {
                "user_id": user_id,
                "space_id": space_id,
                "session_id": session_id,
                "transcript": transcript,
                "response": response,
                "user_audio_url": user_audio_url,
                "ai_audio_url": ai_audio_url,
                "user_audio_duration": user_audio_duration,
                "ai_audio_duration": ai_audio_duration,
            },
        )
        await session.commit()


    async def get_voice_history(
        self,
        session: AsyncSession,
        user_id: str,
        space_id: str = None,
    ):
        if space_id:
            result = await session.execute(
                text(
                    """
                    SELECT user_id, space_id, session_id, transcript, response,
                           user_audio_url, ai_audio_url, user_audio_duration, ai_audio_duration
                    FROM voice_history
                    WHERE user_id = CAST(:user_id AS UUID)
                      AND space_id = CAST(:space_id AS UUID)
                    """
                ),
                {
                    "user_id": user_id,
                    "space_id": space_id,
                },
            )
        else:
            result = await session.execute(
                text(
                    """
                    SELECT user_id, space_id, session_id, transcript, response,
                           user_audio_url, ai_audio_url, user_audio_duration, ai_audio_duration
                    FROM voice_history
                    WHERE user_id = CAST(:user_id AS UUID)
                      AND space_id IS NULL
                    """
                ),
                {
                    "user_id": user_id,
                },
            )
        rows = result.mappings().all()
        return [dict(row) for row in rows]


    async def clear_voice_history(
        self,
        session: AsyncSession,
        user_id: str,
        space_id: str = None,
    ):
        if space_id:
            await session.execute(
                text(
                    """
                    DELETE FROM voice_history
                    WHERE user_id = CAST(:user_id AS UUID)
                      AND space_id = CAST(:space_id AS UUID)
                    """
                ),
                {
                    "user_id": user_id,
                    "space_id": space_id,
                },
            )
        else:
            await session.execute(
                text(
                    """
                    DELETE FROM voice_history
                    WHERE user_id = CAST(:user_id AS UUID)
                      AND space_id IS NULL
                    """
                ),
                {
                    "user_id": user_id,
                },
            )
        await session.commit()
