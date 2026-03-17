from abc import ABC, abstractmethod


class BaseLLMService(ABC):
    @abstractmethod
    async def answer(self, question: str, chunks: list[dict], prompt: str) -> str:
        pass
