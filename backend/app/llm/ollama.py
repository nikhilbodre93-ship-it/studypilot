import json
import logging
from typing import AsyncIterator, Optional, List, Dict
import httpx
from app.llm.base import BaseLLMProvider, LLMError

logger = logging.getLogger("studypilot.llm.ollama")


class OllamaProvider(BaseLLMProvider):
    """Provider for local Ollama instances."""

    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3.2", timeout: float = 60.0):
        super().__init__(model_name=model_name, provider_name="ollama")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _raw_completion(self, system_prompt: str, prompt: str, json_mode: bool = False) -> str:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
        }
        if json_mode:
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            if resp.status_code != 200:
                raise LLMError(f"Ollama API returned {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["message"]["content"]

    async def generate_stream(
        self,
        system_prompt: str,
        prompt: str,
        user_id: Optional[int] = None,
        feature_name: str = "tutor",
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for h in history:
                role = "assistant" if h.get("role") in ("assistant", "ai") else "user"
                messages.append({"role": role, "content": h.get("content", "")})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
        }

        total_content = ""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                if response.status_code != 200:
                    err_msg = await response.aread()
                    raise LLMError(f"Ollama streaming error {response.status_code}: {err_msg.decode()}")
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        delta = chunk.get("message", {}).get("content", "")
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
