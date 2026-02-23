import torch
import os
from src.utils.conf import BASE_DIR
from langchain_huggingface import HuggingFaceEmbeddings

_embedding_model = None
async def init_embedding_model():
    global _embedding_model
    try:
        model_path = os.path.join(BASE_DIR,"uploads","bge-large-zh-v1.5")
        print(model_path)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            model_kwargs = {"device": "cpu",'trust_remote_code': True}
            encode_kwargs = {'normalize_embeddings': True,'batch_size': 32}
            if hasattr(torch, 'set_num_threads'): # 如果可能，启用多线程
                torch.set_num_threads(os.cpu_count())
        else:
            model_kwargs = {"device": "cuda"}
            encode_kwargs = {'normalize_embeddings': True}

        _embedding_model = HuggingFaceEmbeddings(
            model_name=model_path,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    except Exception as e:
        print(e)
        raise

async def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        await init_embedding_model()
    return _embedding_model