from fastapi import APIRouter, Depends, Body

import document.main
import llm.base

import config
from pydantic import BaseModel, Field



class AskRequest(BaseModel):
    text: str = Field(
        ...,
        description="User question about the uploaded document(s).",
        examples=["What should I build for this technical task?"],
    )
    top_k: int = Field(
        5,
        ge=1,
        le=20,
        description="Number of most relevant chunks to retrieve from the vector database.",
        examples=[5],
    )
    
router = APIRouter()


    
@router.post(
    "/ask",
    summary="Ask a question about uploaded documents",
    description=(
        "Receives a user question, retrieves the top-k most relevant chunks from the vector database, "
        "passes them to the LLM as context, and returns both the generated answer and the source chunks used."
    ),
    responses={
        200: {
            "description": "Question answered successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful answer",
                            "value": {
                                "response": "The task is to build a minimal RAG API with document upload, retrieval, and grounded answers with sources.",
                                "sources": [
                                    {
                                        "document_id": "2e38463f-8885-48ec-ba39-caf235df5e7f",
                                        "chunk_index": 5,
                                        "filename": "technical_task.docx",
                                        "text": "Build a minimal RAG (Retrieval-Augmented Generation) API that allows users to upload documents",
                                        "score": 1.63,
                                    }
                                ],
                            },
                        }
                    }
                }
            },
        },
        422: {
            "description": "Validation error in request body.",
        },
    },
)
async def ask(
    query: AskRequest = Body(
        ...,
        description="Question payload with the user query and retrieval depth.",
        examples=[
            {
                "text": "What are the main requirements of this technical task?",
                "top_k": 5,
            }
        ],
    ),
    document_service: document.main.DocumentService = Depends(config.get_document_service),
    llm_service: llm.base.BaseLLMService = Depends(config.get_llm_service)
):
    chunks = await document_service.get(query.text, query.top_k)

    response = await llm_service.answer(
        query, 
        chunks,
        '''Answer only from the provided context. If the answer is not in the context, say it was not found.'''
    )
    
    return {
        "response": response,
        "sources": chunks
    }