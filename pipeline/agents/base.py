from langchain_anthropic import ChatAnthropic

from pipeline.config import settings


def get_llm() -> ChatAnthropic:
    """Shared LLM configuration for all agents."""
    return ChatAnthropic(
        model=settings.model,
        anthropic_api_key=settings.anthropic_api_key,
        temperature=0.2,
    )
