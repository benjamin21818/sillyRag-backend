import os
from pickle import NONE
import uuid
import wave
import numpy as np
import time
import aiofiles
import asyncio
from fastapi import UploadFile
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.ext.asyncio import AsyncSession
from src.handler.voice.asr.sherpa_onnx_asr import VoiceRecognition
from src.handler.voice.voice_history_handler import VoiceHistoryHandler
from src.handler.search.fulltext_search_chunk import FulltextSearchChunk
from src.handler.search.vector_search_chunk import VectorSearchChunk
from src.handler.search.reranker import Reranker
from src.core.llm.deepseek_llm import DeepSeekLLM
from src.core.llm.openai_llm import OpenAILLM
from src.core.prompts.rag_prompt import RAGPrompt
from src.services.user_service import UserService
from src.services.chunk_service import ChunkService
from src.handler.voice.tts.edge_tts import TTSEngine
from src.utils.conf import BASE_DIR
from src.db.pg_db import get_db
from src.utils.logger import get_logger

logger = get_logger(__name__)

class VoiceHandler:
    _instance = None
    _recognizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoiceHandler, cls).__new__(cls)
            cls._instance._initialize_recognizer()
        return cls._instance



    async def init_llm_response(self,user,llm_model:str):
        if llm_model == "deepseek":
            llm = await DeepSeekLLM().init_llm_model(user)
        elif llm_model == "openai":
            llm = await OpenAILLM().init_llm_model(user)
        return llm

    async def init_chain(self,user,llm_model:str,space_id:str = None):
            llm = await self.init_llm_response(user,llm_model)
            prompt = await RAGPrompt().init_voice_prompt(user,space_id)
            chain = prompt | llm

            return chain

    async def _get_chunks_by_space_id(self,message:str,search_mode:str,top_n:int,threshold_vector:float,threshold_fulltext:float,space_id:str):
        if search_mode == "vector":
            chunk_ids = await VectorSearchChunk().vector_search_chunk(message,top_n,threshold_vector,space_id)
            return chunk_ids
        elif search_mode == "fulltext":
            chunk_ids = await FulltextSearchChunk().fulltext_search_chunk(message,top_n,threshold_fulltext,space_id)
            return chunk_ids
        elif search_mode == "hybrid":
            vec_chunk_ids,fulltext_chunk_ids = await asyncio.gather(
                VectorSearchChunk().vector_search_chunk(message,top_n,threshold_vector,space_id),
                FulltextSearchChunk().fulltext_search_chunk(message,top_n,threshold_fulltext,space_id)
            )
            # 使用 dict.fromkeys 保持顺序，[:top_n] 确保最终数量符合预期
            chunk_ids = list(dict.fromkeys(vec_chunk_ids + fulltext_chunk_ids))[:top_n]
            chunk_ids = await Reranker().rerank(message,chunk_ids,top_n)
            return chunk_ids
        
    async def get_llm_response(self,user_id:str,message:str,llm_model:str,space_id:str = None):
         async for session in get_db():
            try:
                user_service = UserService(session)
                user = await user_service.get_by_primary_key(user_id)
                chain = await self.init_chain(user,llm_model,space_id)

                search_mode = user.search_mode if user.search_mode else "hybrid"                  # 检索模式
                top_n = user.top_n if user.top_n else 3                                           # Top-N
                threshold_vector = user.threshold_vector if user.threshold_vector else 0.7        # 向量搜索阈值
                threshold_fulltext = user.threshold_fulltext if user.threshold_fulltext else 0.5  # 全文搜索阈值
                
                result = {}

                if space_id:
                    reranked_chunk_ids = await self._get_chunks_by_space_id(message,search_mode,top_n,threshold_vector,threshold_fulltext,space_id)
                    chunks = []
                    if reranked_chunk_ids:
                        chunks = await ChunkService(session).get_chunks_by_primary_keys(reranked_chunk_ids)
                        chunks = [doc.context for doc in chunks] if chunks else []
                    
                    context_str = "\n".join(chunks) if chunks else ""
                    response = await chain.ainvoke({"question":message,"context":context_str})      
                    if isinstance(response,AIMessage):
                        result["content"] = response.content
                    else:
                        raise ValueError("返回的不是AIMessage")
                    return result
                else:
                    response = await chain.ainvoke({"question":message})
                    if isinstance(response,AIMessage):
                        result["content"] = response.content
                    else:
                        raise ValueError("返回的不是AIMessage")
                    return result
            finally:
                pass 



    async def save_upload_file(self, file: UploadFile, upload_dir: str, session_id: str) -> str:
        os.makedirs(upload_dir, exist_ok=True)
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".wav" # Default to wav if no extension
            
        filename = session_id + ext
        file_path = os.path.join(upload_dir, filename)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # 1MB chunks
                await out_file.write(content)
        
        await file.seek(0)
        return file_path

    def _initialize_recognizer(self):
        path = os.path.join(BASE_DIR, "src/handler/voice/models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17")
        model_path = f"{path}/model.onnx"
        tokens_path = f"{path}/tokens.txt"
        logger.info(f"加载ASR模型中: {model_path}")
        try:
            self._recognizer = VoiceRecognition(
                model_type="sense_voice",
                sense_voice=model_path,
                tokens=tokens_path,
                num_threads=4,
                use_itn=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize VoiceRecognition: {e}")
            raise e

    def load_audio_file(self, file_path: str, target_sample_rate: int = 16000) -> np.ndarray:
        try:
            with wave.open(file_path, 'rb') as wf:
                num_channels = wf.getnchannels()
                sample_rate = wf.getframerate()
                sample_width = wf.getsampwidth()
                num_frames = wf.getnframes()
                data = wf.readframes(num_frames)
                
                # Convert to numpy array
                if sample_width == 2:
                    audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                elif sample_width == 4:
                    audio_data = np.frombuffer(data, dtype=np.int32).astype(np.float32) / 2147483648.0
                elif sample_width == 1:
                    audio_data = (np.frombuffer(data, dtype=np.uint8).astype(np.float32) - 128) / 128.0
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")
                
                # Convert to mono if stereo
                if num_channels > 1:
                    audio_data = audio_data.reshape(-1, num_channels)
                    audio_data = audio_data.mean(axis=1)
                
                # Simple resampling if needed (linear interpolation)
                if sample_rate != target_sample_rate:
                    logger.info(f"Resampling audio from {sample_rate} to {target_sample_rate}")
                    duration = len(audio_data) / sample_rate
                    new_num_frames = int(duration * target_sample_rate)
                    # Use numpy generic interpolation
                    x_old = np.linspace(0, duration, len(audio_data))
                    x_new = np.linspace(0, duration, new_num_frames)
                    audio_data = np.interp(x_new, x_old, audio_data).astype(np.float32)
                
                return audio_data
        except wave.Error:
             # Fallback or error if not a WAV file
             logger.error(f"File {file_path} is not a valid WAV file or unsupported format.")
             raise ValueError("Only WAV files are currently supported.")

    def build_session_id(self, user_id: str, space_id: str = None) -> str:
        timestamp = int(time.time())
        if space_id:
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}_{space_id}_{timestamp}"))
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}_{timestamp}"))


    async def handle_voice_chat(
        self,
        file: UploadFile,
        user_id: str,
        llm_model: str,
        space_id: str,
        session: AsyncSession
    ):
        upload_relative_path = "uploads/asr_voice"
        upload_dir = os.path.join(BASE_DIR, upload_relative_path)
        try:
            session_id = self.build_session_id(user_id, space_id)
            file_path = await self.save_upload_file(file, upload_dir, session_id)

            user_audio_url = f"/uploads/asr_voice/{os.path.basename(file_path)}"
            
            # 2. ASR 识别
            audio_np = self.load_audio_file(file_path)
            user_audio_duration = len(audio_np) / 16000.0 # 计算时长 (采样率 16000)
            
            transcript = await self._recognizer.async_transcribe_np(audio_np)
            logger.info(f"用户语音转换成文字: {transcript}")
            
            if not transcript:
                logger.warning("语音识别结果为空")
                return None
            
            # 3. LLM 对话
            if space_id:
                response_data = await self.get_llm_response(user_id, transcript, llm_model, space_id)
            else:
                response_data = await self.get_llm_response(user_id, transcript, llm_model)
            if not response_data:
                logger.error("Failed to get LLM response")
                return None
            response_content = response_data.get("content", "")
            
            # 4. (可选) TTS 生成
            ai_audio_url = None
            ai_audio_duration = 0.0
            ai_audio_path, ai_audio_duration = await TTSEngine().generate_audio(response_content, user_id, space_id)
            if ai_audio_path:
                ai_audio_url = f"/uploads/tts_voice/{os.path.basename(ai_audio_path)}"


            # 5. 保存历史记录到数据库
            await VoiceHistoryHandler().add_voice_history(
                session=session,
                user_id=user_id,
                space_id=space_id,
                session_id=session_id,
                transcript=transcript,
                response=response_content,
                user_audio_url=user_audio_url,
                ai_audio_url=ai_audio_url,
                user_audio_duration=user_audio_duration,
                ai_audio_duration=ai_audio_duration
            )
            
            return {
                "user_audio_url": user_audio_url,
                "ai_audio_url": ai_audio_url
            }
            
        except Exception as e:
            logger.error(f"Error processing voice chat: {e}")
            raise e
