import os

import httpx
from dotenv import load_dotenv

load_dotenv(override=True)


class LLMClient:
    """
    Generic OpenAI-compatible LLM client.

    Uses the same LLM_* environment variables as Cognee:
    - LLM_API_KEY
    - LLM_BASE_URL
    - LLM_MODEL

    For Cognee/LiteLLM, Groq models need the prefix:
    groq/openai/gpt-oss-120b

    For Groq's direct OpenAI-compatible endpoint, we strip the first
    groq/ prefix before sending the request.
    """

    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv(
            "LLM_BASE_URL",
            "https://api.groq.com/openai/v1",
        ).rstrip("/")
        self.model = self._model_for_direct_api(
            os.getenv("LLM_MODEL", "groq/openai/gpt-oss-120b")
        )

    def _model_for_direct_api(self, model: str) -> str:
        """
        Convert LiteLLM-style model names into direct API model names.

        Example:
        Cognee/LiteLLM wants: groq/openai/gpt-oss-120b
        Groq direct API wants: openai/gpt-oss-120b
        """
        if "api.groq.com" in self.base_url and model.startswith("groq/"):
            return model.replace("groq/", "", 1)

        if "api.openai.com" in self.base_url and model.startswith("openai/"):
            return model.replace("openai/", "", 1)

        return model

    async def complete(self, system: str, user: str) -> str:
        """Send one chat completion request and return the text response."""
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY is missing from .env")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": user,
                },
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]