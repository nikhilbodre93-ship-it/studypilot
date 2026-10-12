import abc
import asyncio
import json
import logging
import hashlib
from typing import Type, TypeVar, Optional, AsyncIterator, Dict, Any, List
from pydantic import BaseModel, ValidationError

from app.database import SessionLocal
from app.models.llm_log import LLMUsageLog

logger = logging.getLogger("studypilot.llm")

T = TypeVar("T", bound=BaseModel)

# Simple in-memory response cache for identical (model, system_prompt, prompt, schema_name)
_GENERATION_CACHE: Dict[str, Any] = {}


class LLMError(Exception):
    """Raised when LLM call fails after all retries or receives fatal error."""
    pass


class BaseLLMProvider(abc.ABC):
    """Abstract Base Class for all LLM providers in StudyPilot."""

    def __init__(self, model_name: str, provider_name: str):
        self.model_name = model_name
        self.provider_name = provider_name

    def _get_cache_key(self, system_prompt: str, prompt: str, schema_name: str) -> str:
        raw = f"{self.provider_name}:{self.model_name}:{schema_name}:{system_prompt}:{prompt}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def log_usage(
        self,
        user_id: Optional[int],
        feature_name: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        """Asynchronously log token usage to llm_usage_logs table."""
        if not user_id:
            return
        try:
            with SessionLocal() as db:
                log_entry = LLMUsageLog(
                    user_id=user_id,
                    provider=self.provider_name,
                    model=self.model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    feature_name=feature_name,
                )
                db.add(log_entry)
                db.commit()
        except Exception as e:
            logger.warning(f"Failed to record LLM usage log: {e}")

    @abc.abstractmethod
    async def _raw_completion(self, system_prompt: str, prompt: str, json_mode: bool = False) -> str:
        """Call the provider API and return raw completion string."""
        pass

    @abc.abstractmethod
    async def generate_stream(
        self,
        system_prompt: str,
        prompt: str,
        user_id: Optional[int] = None,
        feature_name: str = "tutor",
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        """Yield text tokens as an async generator for Server-Sent Events (SSE)."""
        pass

    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        response_model: Type[T],
        max_retries: int = 3,
        user_id: Optional[int] = None,
        feature_name: str = "general",
        use_cache: bool = True
    ) -> T:
        """
        Generate structured output adhering to a Pydantic schema.
        Includes prompt caching, JSON validation with exponential backoff retries,
        and automatic token usage logging.
        """
        schema_name = response_model.__name__
        cache_key = self._get_cache_key(system_prompt, prompt, schema_name)

        if use_cache and cache_key in _GENERATION_CACHE:
            logger.info(f"Cache hit for {schema_name} [{cache_key[:8]}]")
            cached_raw = _GENERATION_CACHE[cache_key]
            return response_model.model_validate_json(cached_raw)

        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        system_augmented = (
            f"{system_prompt}\n\n"
            f"CRITICAL: You must respond ONLY with a single valid JSON object satisfying this JSON Schema:\n"
            f"{schema_json}\n"
            f"Do not include markdown code block backticks (like ```json), commentary, or preambles."
        )

        current_prompt = prompt
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                raw_response = await self._raw_completion(
                    system_prompt=system_augmented,
                    prompt=current_prompt,
                    json_mode=True
                )

                # Clean potential backticks or markdown fences
                cleaned = raw_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:].strip()
                elif cleaned.startswith("```"):
                    cleaned = cleaned[3:].strip()
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3].strip()

                parsed = response_model.model_validate_json(cleaned)

                # Estimate token counts for logging
                est_prompt_tokens = max(1, len(prompt + system_augmented) // 4)
                est_completion_tokens = max(1, len(cleaned) // 4)
                await self.log_usage(
                    user_id=user_id,
                    feature_name=feature_name,
                    prompt_tokens=est_prompt_tokens,
                    completion_tokens=est_completion_tokens
                )

                if use_cache:
                    _GENERATION_CACHE[cache_key] = cleaned

                return parsed

            except (ValidationError, json.JSONDecodeError) as err:
                last_error = err
                logger.warning(
                    f"LLM output validation failed (attempt {attempt}/{max_retries}): {err}"
                )
                if attempt < max_retries:
                    # Exponential backoff
                    await asyncio.sleep(0.5 * (2 ** (attempt - 1)))
                    # Append error details to guide model retry
                    current_prompt = (
                        f"{prompt}\n\n"
                        f"PREVIOUS ATTEMPT PRODUCED INVALID JSON SCHEMA ERROR:\n{str(err)}\n"
                        f"Please correct the output so that it conforms strictly to the {schema_name} JSON schema."
                    )
            except Exception as e:
                last_error = e
                logger.error(f"Provider API communication failure on attempt {attempt}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1.0 * (2 ** (attempt - 1)))

        raise LLMError(f"Failed to generate valid {schema_name} after {max_retries} attempts: {last_error}")
