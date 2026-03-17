import asyncio

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.security import APIKeyHeader
import uvicorn

from routers.document import router as document_router
from routers.chat import router as chat_router

import config


api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
async def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key != config.FASTAPI_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

async def main():
    app = FastAPI(title="Boosta Task API", dependencies=[Depends(verify_api_key)])
    app.include_router(document_router, prefix="/document", tags=["Upload document"])
    app.include_router(chat_router, prefix="/chat", tags=["Chat"])
    
    

    api_config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=3000,
        log_level="info",
    )

    api_server = uvicorn.Server(api_config)
    
    await api_server.serve()
    
    

if __name__ == "__main__":
    # Create folders
    folders = ["logs"]
    for f in folders:
        Path(f).mkdir(exist_ok=True, parents=True)



    # SETTING LOGS

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),    
            RotatingFileHandler(
                filename="logs/app.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8"
            ),
        ],
    )



    # RUN

    asyncio.run(main())