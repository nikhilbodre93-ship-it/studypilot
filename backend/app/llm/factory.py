import logging
from app.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.mock import MockLLMProvider
from app.llm.gemini import GeminiProvider
from app.llm.openai_compat import OpenAICompatProvider
from app.llm.anthropic import AnthropicProvider
from app.llm.ollama import OllamaProvider

logger = logging.getLogger("studypilot.llm.factory")


def get_llm_provider(override_provider: str = None) -> BaseLLMProvider:
    """Factory to retrieve the configured LLM provider according to environment settings."""
    provider_type = (override_provider or settings.LLM_PROVIDER).lower()

    # Smart auto-detection: If provider is still default 'mock', but user supplied an API key
    if provider_type == "mock":
        if settings.GEMINI_API_KEY:
            provider_type = "gemini"
        elif settings.GROQ_API_KEY:
            provider_type = "groq"
        elif settings.OPENAI_API_KEY:
            provider_type = "openai"
        elif settings.ANTHROPIC_API_KEY:
            provider_type = "anthropic"

    if provider_type == "gemini":
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. Falling back to MockLLMProvider.")
            return MockLLMProvider()
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.GEMINI_MODEL,
            timeout=settings.LLM_TIMEOUT_SECONDS
        )

    elif provider_type == "groq":
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set. Falling back to MockLLMProvider.")
            return MockLLMProvider()
        return OpenAICompatProvider(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            model_name=settings.GROQ_MODEL,
            timeout=settings.LLM_TIMEOUT_SECONDS
        )

    elif provider_type == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY is not set. Falling back to MockLLMProvider.")
            return MockLLMProvider()
        return AnthropicProvider(
            api_key=settings.ANTHROPIC_API_KEY,
            model_name=settings.ANTHROPIC_MODEL,
            timeout=settings.LLM_TIMEOUT_SECONDS
        )

    elif provider_type in ("openai", "openai_compat"):
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY is not set. Falling back to MockLLMProvider.")
            return MockLLMProvider()
        return OpenAICompatProvider(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model_name=settings.OPENAI_MODEL,
            timeout=settings.LLM_TIMEOUT_SECONDS
        )

    elif provider_type == "ollama":
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=settings.OLLAMA_MODEL,
            timeout=settings.LLM_TIMEOUT_SECONDS
        )

    else:
        # Default mock provider for safe offline dev and test suites
        return MockLLMProvider()
