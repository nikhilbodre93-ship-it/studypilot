import json
import logging
from typing import AsyncIterator, Optional, List, Dict
from app.llm.openai_compat import OpenAICompatProvider

logger = logging.getLogger("studypilot.llm.gemini")


class GeminiProvider(OpenAICompatProvider):
    """
    Provider for Google Gemini models using Google's official OpenAI-compatible endpoint.
    Compatible with: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash, etc.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-flash",
        timeout: float = 30.0
    ):
        # Google Generative AI provides a full OpenAI-compatible API endpoint
        super().__init__(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            model_name=model_name,
            timeout=timeout
        )
        self.provider_name = "gemini"
