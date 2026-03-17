from datetime import datetime, timezone

from sql_db.sqlite import SqliteDB


class MetaDataDB:
    def __init__(self, sql_db: SqliteDB):
        self.sql_db = sql_db
        self._initialized = False

    async def create_table(self) -> None:
        if self._initialized:
            return
        
        await self.sql_db.create_table("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL,
                hash_id TEXT NOT NULL UNIQUE,
                content_type TEXT NOT NULL,
                uploaded_at TEXT NOT NULL,
                chunk_count INTEGER NOT NULL
            )
        """)
        self._initialized = True

    async def create_document(
        self,
        document_id: int,
        filename: str,
        hash_id: str,
        content_type: str,
        chunk_count: int,
    ) -> int:
        await self.create_table()
        await self.sql_db.insert(
            """
            INSERT INTO documents (
                document_id, filename, hash_id, content_type, uploaded_at, chunk_count
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                filename,
                hash_id,
                content_type,
                datetime.now(timezone.utc).isoformat(),
                chunk_count,
            ),
        )
        


    async def get_document_by_id(self, hash_id: str) -> dict | None:
        await self.create_table()
        return await self.sql_db.get_one(
            "SELECT * FROM documents WHERE document_id = ?",
            (hash_id,),
        )
        
    async def get_document_by_hash_id(self, hash_id: str) -> dict | None:
        await self.create_table()
        return await self.sql_db.get_one(
            "SELECT * FROM documents WHERE hash_id = ?",
            (hash_id,),
        )

    async def delete_document(self, document_id: str) -> None:
        await self.create_table()
        await self.sql_db.remove(
            "DELETE FROM documents WHERE document_id = ?",
            (document_id,),
        )
    