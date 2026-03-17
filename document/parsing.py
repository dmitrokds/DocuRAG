from docx import Document
from pypdf import PdfReader
from docx import Document
import pandas as pd

from pathlib import Path
import asyncio


from abc import ABC, abstractmethod



class BaseParser(ABC):
    async def read(self, path: Path) -> str:
        return await asyncio.to_thread(self.read_sync, path)
    
    @abstractmethod
    def read_sync(self, path: Path) -> str:
        pass
    
    @abstractmethod
    def supports(self, content_type: str) -> bool:
        pass


class TxtParser(BaseParser):
    def read_sync(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")
        
    def supports(self, content_type: str) -> str:
        return content_type=="text/plain"
    
    
class PdfParser(BaseParser):
    def read_sync(self, path: Path) -> str:
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
        
    def supports(self, content_type: str) -> str:
        return content_type=="application/pdf"
    
    
class DocxParser(BaseParser):
    def read_sync(self, path: Path) -> str:
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
        
    def supports(self, content_type: str) -> str:
        return content_type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
class XlsxParser(BaseParser):
    def read_sync(self, path: Path) -> str:
        excel_file = pd.ExcelFile(str(path))
        parts = []

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(str(path), sheet_name=sheet_name).fillna("")
            parts.append(f"Sheet: {sheet_name}")

            for row in df.astype(str).values.tolist():
                parts.append(" | ".join(row))

        return "\n".join(parts)
        
    def supports(self, content_type: str) -> str:
        return content_type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    
class ParserService:
    def __init__(self):
        self.parsers = [
            TxtParser(),
            PdfParser(),
            DocxParser(),
            XlsxParser(),
        ]

    async def read(self, path: Path, content_type: str) -> str:
        for parser in self.parsers:
            if parser.supports(content_type):
                return await parser.read(path)
            
        raise ValueError(f"Unsupported content type: {content_type}")