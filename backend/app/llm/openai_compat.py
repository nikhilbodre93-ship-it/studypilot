import json
import logging
from typing import AsyncIterator, Optional, List, Dict
import httpx
from app.llm.base import BaseLLMProvider, LLMError

logger = logging.getLogger("studypilot.llm.openai")


class OpenAICompatProvider(BaseLLMProvider):
    """Provider for OpenAI and OpenAI-compatible endpoints (Groq, OpenRouter, Together, LocalAI, vLLM)."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model_name: str = "gpt-4o-mini", timeout: float = 30.0):
        super().__init__(model_name=model_name, provider_name="openai_compat")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _raw_completion(self, system_prompt: str, prompt: str, json_mode: bool = False) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            if resp.status_code != 200:
                raise LLMError(f"OpenAI-compatible API returned {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def generate_stream(
        self,
        system_prompt: str,
        prompt: str,
        user_id: Optional[int] = None,
        feature_name: str = "tutor",
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history:
                role = "assistant" if h.get("role") in ("assistant", "ai") else "user"
                messages.append({"role": role, "content": h.get("content", "")})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.5,
            "stream": True
        }

        total_content = ""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_msg = await response.aread()
                    raise LLMError(f"OpenAI streaming error {response.status_code}: {err_msg.decode()}")
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_json = json.loads(data_str)
                            delta = chunk_json["choices"][0]["delta"].get("content", "")
                            if delta:
                                total_content += delta
                                yield delta
                        except Exception:
                            continue

        await self.log_usage(
            user_id=user_id,
            feature_name=feature_name,
            prompt_tokens=max(1, len(prompt + system_prompt) // 4),
            completion_tokens=max(1, len(total_content) // 4)
        )
