from abc import abstractmethod

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction, OllamaEmbeddingFunction, OpenAIEmbeddingFunction

from .base import BaseVectorDB

class ChromaWebVectorDB(BaseVectorDB):
    def __init__(self, host: str, port: int, collection_name: str, embedding_function = DefaultEmbeddingFunction()):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.embedding_function = embedding_function
        
        self.client = None
        self.collection: chromadb.Collection|None = None
        
    async def _get_client(self) -> None:
        if self.client is None:
            self.client = await chromadb.AsyncHttpClient(
                host=self.host,
                port=self.port,
                ssl=False,
            )
            
    async def _get_collection(self) -> None:
        if self.collection is None:
            await self._get_client()

            self.collection = await self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
            )

    async def add_chunks(self, chunks: list[dict]) -> None:
        await self._get_collection()
        await self.collection.add(
            ids = [chunk["id"] for chunk in chunks],
            documents=[chunk["text"] for chunk in chunks],
            metadatas=[chunk["metadata"] for chunk in chunks]
        )

    async def delete_document(self, id: str) -> None:
        await self._get_collection()
        await self.collection.delete(where={"document_id": id})
        
    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        await self._get_collection()
        result = await self.collection.query(query_texts=query, n_results=top_k)

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
    

class ChromaWebVectorDBOpenAIEmbedding(ChromaWebVectorDB):
    def __init__(self, host: str, port: int, collection_name: str, api_key: str, model_name: str):
        super().__init__(
            host, port, collection_name, 
            embedding_function=OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name=model_name,
            )
        )
          
class ChromaWebVectorDBOllamaEmbedding(ChromaWebVectorDB):
    def __init__(self, host: str, port: int, collection_name: str, model_name: str, url: str = "http://localhost:11434/api/embeddings"):
        super().__init__(
            host, port, collection_name, 
            embedding_function=OllamaEmbeddingFunction(
                url=url,
                model_name=model_name,
            )
        )