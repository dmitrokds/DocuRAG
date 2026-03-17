from .base import BaseLLMService

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage


class LangChainLLMService(BaseLLMService):
    async def answer(self, question: str, chunks: list[dict], prompt: str) -> str:
        context = "\n\n".join(
            f"[Source - {chunk['filename']}, {chunk['chunk_index']}]\n{chunk['text']}"
            for chunk in chunks
        )


        response = await self.client.ainvoke([
            SystemMessage(
                content=prompt
            ),
            HumanMessage(
                content=f'''Question:
{question}

Context:
{context}'''
            ),
        ])

        return response.text()
    
    
class OpenAILangChainLLMService(LangChainLLMService):
    def __init__(self, api_key: str, model: str = "gpt-5-mini"):
        self.client = ChatOpenAI(
            model=model,
            api_key=api_key,
            use_responses_api=True,
        )
    
    
class GeminiLangChainLLMService(LangChainLLMService):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = ChatGoogleGenerativeAI(
            model=model,
            api_key=api_key
        )
    
    
class ClaudeLangChainLLMService(LangChainLLMService):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
        self.client = ChatAnthropic(
            model=model,
            api_key=api_key
        )