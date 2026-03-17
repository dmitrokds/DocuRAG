class ChunckingService:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    async def split(self, text: str):
        left = 0
        text_len = len(text)
        iterations = 0
        
        while left < text_len:
            right = left+self.chunk_size
            
            chunk = text[left: right].strip()
            if chunk: yield iterations, chunk
            
            if right >= text_len:
                break
            
            left = right - self.chunk_overlap
            iterations+=1