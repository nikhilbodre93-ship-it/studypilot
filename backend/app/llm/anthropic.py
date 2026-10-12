import json
import logging
from typing import AsyncIterator, Optional, List, Dict
import httpx
from app.llm.base import BaseLLMProvider, LLMError

logger = logging.getLogger("studypilot.llm.anthropic")


class AnthropicProvider(BaseLLMProvider):
    """Provider for Anthropic Claude models via raw HTTP client."""

    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022", timeout: float = 30.0):
        super().__init__(model_name=model_name, provider_name="anthropic")
        self.api_key = api_key
        self.timeout = timeout
        self.endpoint = "https://api.anthropic.com/v1/messages"

    async def _raw_completion(self, system_prompt: str, prompt: str, json_mode: bool = False) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self.endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                raise LLMError(f"Anthropic API returned {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["content"][0]["text"]

    async def generate_stream(
        self,
        system_prompt: str,
        prompt: str,
        user_id: Optional[int] = None,
        feature_name: str = "tutor",
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        messages = []
        if history:
            for h in history:
                role = "assistant" if h.get("role") in ("assistant", "ai") else "user"
                messages.append({"role": role, "content": h.get("content", "")})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": messages,
            "stream": True,
            "temperature": 0.5
        }

        total_content = ""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", self.endpoint, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_msg = await response.aread()
                    raise LLMError(f"Anthropic streaming error {response.status_code}: {err_msg.decode()}")
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        try:
                            event = json.loads(data_str)
                            if event.get("type") == "content_block_delta":
                                delta_text = event.get("delta", {}).get("text", "")
                                if delta_text:
                                    total_content += delta_text
                                    yield delta_text
                        except Exception:
                            continue

        await self.log_usage(
            user_id=user_id,
            feature_name=feature_name,
            prompt_tokens=max(1, len(prompt + system_prompt) // 4),
            completion_tokens=max(1, len(total_content) // 4)
        )
