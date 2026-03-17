from abc import ABC, abstractmethod


class BaseSqlDB(ABC):
    @abstractmethod
    async def create_table(self, query: str) -> None:
        pass

    @abstractmethod
    async def get_one(self, query: str) -> dict|None:
        pass
    @abstractmethod
    async def get(self, query: str) -> list[dict]:
        pass

    @abstractmethod
    async def insert(self, query: str) -> int:
        pass
    
    @abstractmethod
    async def remove(self, query: str) -> None:
        pass

    @abstractmethod
    async def update(self, query: str) -> None:
        pass