# Requires transformers>=4.51.0
import torch
import asyncio
import os
from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
from src.db.pg_db import get_db
from src.services.chunk_service import ChunkService
from src.utils.conf import BASE_DIR
from src.utils.logger import get_logger
logger = get_logger(__name__)



class Reranker:
    def __init__(self, model_path=os.path.join(BASE_DIR, "uploads/Qwen3-Reranker-0.6B"), device=None):
        """
        初始化 Reranker 模型。
        
        Args:
            model_path (str): 模型路径。
            device (str, optional): 运行设备 ('cuda', 'cpu', 'mps' 等)。如果不指定，会自动检测。
        """
        self.model_path = model_path
        
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
            
        print(f"Loading model from {self.model_path} on {self.device}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, padding_side='left')
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path).to(self.device).eval()
        
        # 获取 "yes" 和 "no" token 的 ID
        self.token_false_id = self.tokenizer.convert_tokens_to_ids("no")
        self.token_true_id = self.tokenizer.convert_tokens_to_ids("yes")
        self.max_length = 8192
        
        # 定义提示模板的前缀和后缀
        self.prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
        self.suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        self.prefix_tokens = self.tokenizer.encode(self.prefix, add_special_tokens=False)
        self.suffix_tokens = self.tokenizer.encode(self.suffix, add_special_tokens=False)

    async def _format_instruction(self, instruction, query, doc):
        """
        格式化指令、查询和文档，生成符合模型输入要求的字符串。
        """
        if instruction is None:
            instruction = 'Given a web search query, retrieve relevant passages that answer the query'
        output = "<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}".format(instruction=instruction, query=query, doc=doc)
        return output

    async def _process_inputs(self, pairs):
        """
        处理输入对，进行分词和张量转换。
        """
        inputs = self.tokenizer(
            pairs, padding=False, truncation='longest_first',
            return_attention_mask=False, max_length=self.max_length - len(self.prefix_tokens) - len(self.suffix_tokens)
        )
        # 为每个输入添加前缀和后缀 token
        for i, ele in enumerate(inputs['input_ids']):
            inputs['input_ids'][i] = self.prefix_tokens + ele + self.suffix_tokens
        # 进行 padding 并转换为 PyTorch 张量
        inputs = self.tokenizer.pad(inputs, padding=True, return_tensors="pt")
        # 将数据移动到模型所在的设备
        for key in inputs:
            inputs[key] = inputs[key].to(self.model.device)
        return inputs

    @torch.no_grad()
    async def _compute_logits(self, inputs):
        """
        计算相关性分数。
        """
        # 获取模型输出的 logits，关注最后一个 token 的输出
        batch_scores = self.model(**inputs).logits[:, -1, :]
        # 提取 "yes" 和 "no" 对应的 logits
        true_vector = batch_scores[:, self.token_true_id]
        false_vector = batch_scores[:, self.token_false_id]
        # 堆叠 logits
        batch_scores = torch.stack([false_vector, true_vector], dim=1)
        # 计算 log_softmax
        batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
        # 取出 "yes" (索引为1) 的概率作为相关性分数
        scores = batch_scores[:, 1].exp().tolist()
        return scores

    async def rerank(self, query: str, chunk_ids: list[str], instruction: str = None,top_n:int = 3) -> list[float]:
        """
        对给定的查询和文档列表进行重排序打分。
        
        Args:
            query (str): 用户查询。
            documents (list[str]): 待打分的文档片段列表。
            instruction (str, optional): 任务指令。如果为 None，使用默认指令。
            
        Returns:
            list[float]: 每个文档的相关性分数列表，顺序与输入 documents 一致。
        """

        async for session in get_db():
            docs = await ChunkService(session).get_chunks_by_primary_keys(chunk_ids)
            documents = [doc.context for doc in docs]
            if not documents:
                return []
            
        # 构造 (query, doc) 对，这里是一个 query 对应多个 doc
        pairs = [await self._format_instruction(instruction, query, doc) for doc in documents]
        
        # 处理输入
        inputs = await self._process_inputs(pairs)
        
        # 计算分数
        scores = await self._compute_logits(inputs)
        
        # 按分数降序排序
        sorted_scores = sorted(zip(chunk_ids, scores), key=lambda x: x[1], reverse=True)
        
        # 取 top_n 个文档
        top_docs = sorted_scores[:top_n]
        logger.info(f"经过重排筛选出的文档ID为：{top_docs}")
        ids = [doc_id for doc_id, score in top_docs]
        
        return ids

