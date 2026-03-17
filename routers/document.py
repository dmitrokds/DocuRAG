from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse

import document.main
import config

router = APIRouter()

    

@router.post(
    "/upload",
    summary="Upload a document",
    description=(
        "Uploads a document, parses it, splits it into chunks, stores the chunks in the vector database, "
        "and saves document metadata. If the same file was already uploaded before, it will be detected "
        "as a duplicate and skipped."
    ),
    responses={
        200: {
            "description": "Document uploaded successfully or duplicate detected.",
            "content": {
                "application/json": {
                    "examples": {
                        "uploaded": {
                            "summary": "Successful upload",
                            "value": {
                                "document_id": "2e38463f-8885-48ec-ba39-caf235df5e7f",
                                "filename": "test.pdf",
                                "duplicate": False,
                                "chunks_stored": 24,
                            },
                        },
                        "duplicate": {
                            "summary": "Duplicate file",
                            "value": {
                                "document_id": "2e38463f-8885-48ec-ba39-caf235df5e7f",
                                "filename": "test.pdf",
                                "duplicate": True,
                                "chunks_stored": 0,
                            },
                        },
                    }
                }
            },
        },
        415: {
            "description": "Unsupported file format.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "description": "Your file format (image/png) is invalid - please upload file in .txt, .pdf, .docx, .xlsx",
                    }
                }
            },
        },
    },
)
async def upload(
    file: UploadFile = File(...),
    service: document.main.DocumentService = Depends(config.get_document_service)
):
    content = await file.read()
    if file.content_type not in [
        "text/plain",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]:
        return JSONResponse(content = {
            "status": "error",
            "description": f"Your file format ({file.content_type}) is invailid - please upload file in .txt, .pdf, .docx, .xlsx"
        }, status_code=415)
    
    return await service.upload(file.filename, file.content_type, content)

@router.delete(
    "/remove",
    summary="Remove a document",
    description=(
        "Removes a document from both metadata storage and vector database using its document ID."
    ),
    responses={
        200: {
            "description": "Document removed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "is_ok": True
                    }
                }
            },
        },
        404: {
            "description": "Document not found.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "description": "Document not found",
                    }
                }
            },
        },
    },
)
async def remove(
    file_id: str,
    service: document.main.DocumentService = Depends(config.get_document_service)
):
    return await service.remove(file_id)