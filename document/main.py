from . import chunking, parsing, temporary, metadata_storage
from vector_db.base import BaseVectorDB

from fastapi.responses import JSONResponse

from pathlib import Path
import hashlib
import uuid


class DocumentService:
    def __init__(self, parser_service: parsing.ParserService, chunking_service: chunking.ChunckingService, vector_db: BaseVectorDB, metadata_db: metadata_storage.MetaDataDB):
        self.parser_service = parser_service
        self.chunking_service = chunking_service
        self.vector_db = vector_db
        
        self.metadata_db = metadata_db
    
    async def upload(self, filename: str, content_type: str, content: bytes):        
        hash_id = hashlib.sha256(content).hexdigest()
        existing = await self.metadata_db.get_document_by_hash_id(hash_id)
        if existing:
            return {
                "document_id": existing["document_id"],
                "filename": existing["filename"],
                "duplicate": True,
                "chunks_stored": 0,
            }
            
        
        async with temporary.TempFile(Path("cached"), content_type, content) as temp_document:
            text = await self.parser_service.read(
                temp_document.get(),
                content_type
            )
            
        document_id = str(uuid.uuid4())
        chunks_stored = 0
        async for i, chunk in self.chunking_service.split(text):
            chunk = {
                "id": f"{document_id}_chunk_{i}",
                "text": chunk,
                "metadata": {
                    "document_id": document_id,
                    "chunk_index": i,
                    "filename": filename,
                },
            }
            await self.vector_db.add_chunks([chunk])
            chunks_stored+=1

        await self.metadata_db.create_document(
            document_id=document_id,
            filename=filename,
            hash_id=hash_id,
            content_type=content_type,
            chunk_count=chunks_stored,
        )

        return {
            "document_id": document_id,
            "filename": filename,
            "duplicate": False,
            "chunks_stored": chunks_stored,
        }
        
        
    async def remove(self, document_id: str) -> None:
        existing = await self.metadata_db.get_document_by_id(document_id)
        if not existing:
            return JSONResponse(content = {
                "status": "error",
                "description": f"Document not found"
            }, status_code=404)
            
        await self.vector_db.delete_document(document_id)
        await self.metadata_db.delete_document(document_id)
        
        return {"ok": True}
    
    
    async def get(self, query: str, top_k: int):
        chunks = await self.vector_db.search(
            query=query,
            top_k=top_k,
        )
        
        chunks = [{
            "chunk_index": chunk["metadata"]["chunk_index"],
            "document_id": chunk["metadata"]["document_id"],
            "text": chunk["text"],
            "filename": chunk["metadata"]["filename"],
            "score": 1 / (1 + chunk["distance"])
        } for chunk in chunks]
        
        return chunks