from langchain_community.document_loaders import CSVLoader
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.conf import PROJECT_DIR,BASE_DIR
from langchain_huggingface import HuggingFaceEmbeddings
import torch
import os
import re



class PartitionCSV:
    def __init__(self):
        # 加载本地向量模型
        model_path = os.path.join(BASE_DIR, "uploads", "bge-large-zh-v1.5")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_kwargs = {"device": device}
        self.emodel = HuggingFaceEmbeddings(
                    model_name=model_path,
                    model_kwargs=model_kwargs,
                )

    # 根据标点符号拆分文本
    def split_text(self, text):
        # 增加更多中文标点支持，保留换行符作为重要分割点
        sentences = re.split(r'([。！？.!?\n])', text)
        # 重新组合标点到句子中
        new_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            s = sentences[i].strip()
            p = sentences[i+1].strip()
            if s:
                new_sentences.append(s + p)
        if sentences[-1].strip():
            new_sentences.append(sentences[-1].strip())
        return new_sentences

    # 向量化文本
    def embed_text(self, text):
        embeddings = self.emodel.embed_documents([text])
        return embeddings

    # 计算余弦相似度
    def calculate_similarity(self, v1, v2):
        similarity = cosine_similarity(v1, v2)
        return similarity



    async def partition_csv(self, file_path):

        loader = CSVLoader(
                    file_path=file_path,
                    encoding='utf-8',
                    csv_args={
                        'delimiter': ',',
                        'quotechar': '"',
                    })
        docs = loader.load()


        final_chunks = []
        print(f"正在处理 {len(docs)} 条 CSV 记录...")

        for doc_idx, doc in enumerate(docs):
            original_content = doc.page_content
            content_pattern = r'content: (.*)'
            match = re.search(content_pattern, original_content, re.DOTALL)
            if match:
                original_content = match.group(1).strip()
            
            # 如果内容较短，直接作为一个 Chunk
            if len(original_content) < 500:
                final_chunks.append(original_content)
                continue
                
            # 内容较长，尝试语义拆分
            print(f"记录 {doc_idx} 内容较长 ({len(original_content)} chars)，尝试语义拆分...")
            splits = self.split_text(original_content)
            
            if len(splits) <= 1:
                final_chunks.append(original_content)
                continue

            # 对子句进行向量化
            embeddings = [self.embed_text(split) for split in splits]
            
            # 语义合并逻辑
            current_chunk_splits = [splits[0]]
            
            for i in range(len(embeddings)-1):
                sim = self.calculate_similarity(embeddings[i], embeddings[i+1])
                # 相似度阈值，或者简单的长度合并策略
                # 这里演示：如果相似度高，或者当前块太短，就合并
                if sim > 0.6 or len("".join(current_chunk_splits)) < 50:
                    current_chunk_splits.append(splits[i+1])
                else:
                    final_chunks.append("".join(current_chunk_splits))
                    current_chunk_splits = [splits[i+1]]
                    
            if current_chunk_splits:
                final_chunks.append("".join(current_chunk_splits))
        
        return final_chunks
