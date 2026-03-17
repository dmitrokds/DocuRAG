from .base import BaseSqlDB
from pathlib import Path

import aiosqlite



class SqliteDB(BaseSqlDB):
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def _execute(self, query: str, params: tuple = ()):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.lastrowid


    async def get_one(self, query: str, params: tuple) -> dict|None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
            
        return dict(row) if row else None

    async def get(self, query: str, params: tuple) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            rows = await db.execute_fetchall(query, params)
            
        return [dict(row) for row in rows]
    
    async def create_table(self, query: str) -> None:
        return await self._execute(query)

    async def insert(self, query: str, params: tuple) -> int:
        return await self._execute(query, params)
    
    async def update(self, query: str, params: tuple) -> None:
        await self._execute(query, params)
        
    async def remove(self, query: str, params: tuple) -> None:
        await self._execute(query, params)
