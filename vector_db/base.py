from abc import ABC, abstractmethod


class BaseVectorDB(ABC):
    @abstractmethod
    async def add_chunks(self, chunks: list[dict]) -> None:
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> None:
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int) -> None:
        pass