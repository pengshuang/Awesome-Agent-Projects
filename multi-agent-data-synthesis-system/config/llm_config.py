"""LLM configuration and initialization."""

from langchain_openai import ChatOpenAI
from .settings import settings


def get_llm(
    model_name: str = None,
    temperature: float = None,
    max_tokens: int = None
) -> ChatOpenAI:
    """
    Get configured LLM instance.
    
    Args:
        model_name: Model name to use (defaults to settings)
        temperature: Temperature for generation (defaults to settings)
        max_tokens: Maximum tokens to generate (defaults to settings)
    
    Returns:
        Configured ChatOpenAI instance
    """
    return ChatOpenAI(
        model=model_name or settings.proposer_model,
        temperature=temperature or settings.temperature,
        max_tokens=max_tokens or settings.max_tokens,
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
    )
