"""Hosted LLM client with Anthropic Claude Messages API, OpenAI fallback, retry, timeout, and mock support."""

from typing import List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import LLMServiceError
from app.rag.prompt import SYSTEM_PROMPT

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class LLMClient:
    """Client for generating grounded answers using hosted LLMs (Anthropic Claude or OpenAI)."""

    def __init__(self):
        self.provider = (settings.LLM_PROVIDER or "anthropic").lower()
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_REQUEST_TIMEOUT_SECONDS
        self.max_retries = settings.LLM_MAX_RETRIES

        # Anthropic configuration
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.anthropic_model = settings.ANTHROPIC_MODEL or "claude-3-5-sonnet-20241022"

        # OpenAI configuration
        self.openai_api_key = settings.LLM_API_KEY
        self.openai_base_url = settings.LLM_BASE_URL.rstrip("/")
        self.openai_model = settings.LLM_MODEL

        # Determine mock status
        if settings.USE_MOCK_LLM:
            self.use_mock = True
        elif self.provider == "anthropic":
            self.use_mock = (not self.anthropic_api_key) or self.anthropic_api_key.startswith("mock-")
        else:
            self.use_mock = (not self.openai_api_key) or self.openai_api_key.startswith("mock-")

        # Initialize Anthropic client instance if credentials exist
        self._anthropic_client = None
        if not self.use_mock and self.provider == "anthropic" and HAS_ANTHROPIC and self.anthropic_api_key:
            try:
                self._anthropic_client = anthropic.Anthropic(
                    api_key=self.anthropic_api_key,
                    timeout=self.timeout,
                    max_retries=self.max_retries,
                )
            except Exception as e:
                logger.warning("Failed to initialize Anthropic client: %s", e)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    def _call_anthropic_messages_api(self, prompt: str) -> str:
        """Call Anthropic Messages API using official Python SDK."""
        if not HAS_ANTHROPIC or not self._anthropic_client:
            raise LLMServiceError("Anthropic SDK is not initialized or API key is missing")

        try:
            response = self._anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            if not response.content:
                raise LLMServiceError("Empty response returned by Anthropic API")
            
            # Extract text blocks
            texts = [block.text for block in response.content if hasattr(block, "text")]
            return "\n".join(texts).strip()
        except anthropic.APIError as exc:
            logger.error("Anthropic API Error: status_code=%s, message=%s", getattr(exc, "status_code", "unknown"), exc)
            raise LLMServiceError(f"Anthropic API call failed: {str(exc)}") from exc

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True,
    )
    def _call_openai_compatible_api(self, prompt: str) -> str:
        """Execute request to OpenAI-compatible chat completion endpoint."""
        url = f"{self.openai_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.openai_model,
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
            logger.info("Generating response using LLM client mock mode [Provider=%s].", self.provider)
            # Deterministic, grounded mock answer based on retrieved evidence
            if retrieved_context_summary:
                return (
                    f"Based on the authorized campus documentation ({retrieved_context_summary}), "
                    f"here is the verified information: The requested campus procedures and regulations "
                    f"are governed by the official guidelines documented in the campus repository."
                )
            return "Based on the provided documents, the official campus policy specifies this regulation."

        try:
            if self.provider == "anthropic":
                return self._call_anthropic_messages_api(prompt)
            return self._call_openai_compatible_api(prompt)
        except Exception as exc:
            logger.error("LLM service call failed: %s", exc)
            raise LLMServiceError(f"LLM generation failed: {str(exc)}")


llm_client = LLMClient()
