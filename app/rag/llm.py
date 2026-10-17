"""Hosted LLM client with retry, timeout handling, and test mock support."""

from typing import List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import LLMServiceError
from app.rag.prompt import SYSTEM_PROMPT


class LLMClient:
    """Client for generating answers using hosted OpenAI-compatible LLMs."""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_REQUEST_TIMEOUT_SECONDS
        self.max_retries = settings.LLM_MAX_RETRIES
        self.use_mock = settings.USE_MOCK_LLM or (not self.api_key) or self.api_key.startswith("mock-")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    def _call_openai_compatible_api(self, prompt: str) -> str:
        """Execute request to OpenAI-compatible chat completion endpoint."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    def generate_answer(self, prompt: str, retrieved_context_summary: Optional[str] = None) -> str:
        """Generate answer from prompt. Uses deterministic synthesis in mock mode."""
        if self.use_mock:
            logger.info("Generating response using LLM client mock mode.")
            # Deterministic, grounded mock answer based on retrieved evidence
            if retrieved_context_summary:
                return (
                    f"Based on the authorized campus documentation ({retrieved_context_summary}), "
                    f"here is the verified information: The requested campus procedures and regulations "
                    f"are governed by the official guidelines documented in the campus repository."
                )
            return "Based on the provided documents, the official campus policy specifies this regulation."

        try:
            return self._call_openai_compatible_api(prompt)
        except Exception as exc:
            logger.error("LLM service call failed: %s", exc)
            raise LLMServiceError(f"LLM generation failed: {str(exc)}")


llm_client = LLMClient()
