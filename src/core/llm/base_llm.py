from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def init_llm_model(self):
        pass