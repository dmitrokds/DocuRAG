FASTAPI_API_KEY = "test"


import document.main
from document import chunking, parsing, metadata_storage
from vector_db.chroma_web import ChromaWebVectorDB
from sql_db.sqlite import SqliteDB
from pathlib import Path


sql_db_path = Path("db_data/sql_storage.db")
sql_db_path.parent.mkdir(parents=True, exist_ok=True)
sql_db = SqliteDB(sql_db_path)

document_service = document.main.DocumentService(
    parsing.ParserService(),
    chunking.ChunckingService(chunk_size=100, chunk_overlap=10),
    ChromaWebVectorDB(host="chroma", port=8000, collection_name="documents"),
    metadata_storage.MetaDataDB(sql_db)
)

def get_document_service() -> document.main.DocumentService:
    return document_service


from llm.langchain import OpenAILangChainLLMService

llm_service = OpenAILangChainLLMService(
    "api-key"
)

def get_llm_service() -> OpenAILangChainLLMService:
    return llm_service