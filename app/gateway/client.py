import logfire
from langchain_openai import ChatOpenAI
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL

from app.config import settings


def get_langchain_llm(feature: str = "rag") -> ChatOpenAI:
    """
    Returns a LangChain LLM routed through Portkey Gateway for telemetry using Virtual Key.
    """
    portkey_headers = createHeaders(
        api_key=settings.PORTKEY_API_KEY,
        virtual_key="groq-slug-2"
    )

    return ChatOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=portkey_headers,
        model=settings.GROQ_MODEL,
        temperature=0
    )


def extract_cache_status(response) -> str:
    """
    Cache status helper.
    """
    return "MISS"