import aiofiles
from pathlib import Path
import mimetypes

import uuid

class TempFile:
    def __init__(self, cached_folder: Path, content_type: str, content: bytes):
        self.content_type = content_type
        self.content = content  
        
        self.path = cached_folder / f"{str(uuid.uuid4())}{mimetypes.guess_extension(content_type)}"
        
    async def __aenter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.path, "wb") as f:
            await f.write(self.content)
        
        return self
    
    def get(self) -> Path:
        return self.path

    async def __aexit__(self, exc_type, exc, tb):
        self.path.unlink(missing_ok=True)