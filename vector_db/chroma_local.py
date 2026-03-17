from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction, OllamaEmbeddingFunction, OpenAIEmbeddingFunction

from .base import BaseVectorDB

class ChromaLocalVectorDB(BaseVectorDB):
    def __init__(self, db_dir: Path, collection_name: str):
        self.client = chromadb.PersistentClient(path=db_dir)
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=DefaultEmbeddingFunction(),
        )
        
    async def add_chunks(self, chunks: list[dict]) -> None:
        self.collection.add(
            ids = [chunk["id"] for chunk in chunks],
            documents=[chunk["text"] for chunk in chunks],
            metadatas=[chunk["metadata"] for chunk in chunks]
        )

    async def delete_document(self, id: str) -> None:
        self.collection.delete(where={"document_id": id})
        
    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        result = self.collection.query(query_texts=query, n_results=top_k)

        result = [
            {
                "id": chunk_id,
                "text": text,
                "metadata": metadata,
                "distance": distance,
            }
            for chunk_id, text, metadata, distance in zip(
                result.get("ids", [[]])[0],
                result.get("documents", [[]])[0],
                result.get("metadatas", [[]])[0],
                result.get("distances", [[]])[0]
            )
        ]

        return result
        

class ChromaLocalVectorDBOpenAIEmbedding(ChromaLocalVectorDB):
    def __init__(self, db_dir: Path, collection_name: str, api_key: str, model_name: str):
        super().__init__(db_dir, collection_name)
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name=model_name,
            )
        )

class ChromaLocalVectorDBOllamaEmbedding(ChromaLocalVectorDB):
    def __init__(self, db_dir: Path, collection_name: str, model_name: str, url: str = "http://localhost:11434/api/embeddings"):
        super().__init__(db_dir, collection_name)
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=OllamaEmbeddingFunction(
                url=url,
                model_name=model_name,
            )
        )