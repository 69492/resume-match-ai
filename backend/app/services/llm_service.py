import json
import math
import os
from collections.abc import Callable
from typing import Any

import httpx

from app.schemas.llm_analysis import AnalysisRequest, LLMAnalysis
from app.services.prompts.resume_analysis import SYSTEM_PROMPT, build_analysis_prompt


class LLMConfigurationError(ValueError):
    pass


class LLMProviderError(RuntimeError):
    pass


def _settings() -> tuple[str, str, float, str]:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    try:
        timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    except ValueError as exc:
        raise LLMConfigurationError("LLM_TIMEOUT_SECONDS must be a number.") from exc
    if not api_key:
        raise LLMConfigurationError("LLM_API_KEY is required for analysis.")
    if not model:
        raise LLMConfigurationError("LLM_MODEL must not be empty.")
    if not math.isfinite(timeout) or timeout <= 0:
        raise LLMConfigurationError("LLM_TIMEOUT_SECONDS must be greater than zero.")
    return api_key, model, timeout, base_url


class LLMService:
    """OpenAI-compatible provider adapter with typed output validation."""

    def __init__(self, provider: Callable[[str, str, float, str], Any] | None = None):
        self._provider = provider

    def analyze_match(self, request: AnalysisRequest) -> LLMAnalysis:
        api_key, model, timeout, base_url = _settings()
        prompt = build_analysis_prompt(request)
        raw = self._provider(api_key, model, timeout, prompt) if self._provider else self._request_provider(api_key, model, timeout, base_url, prompt)
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise LLMProviderError("The LLM returned malformed structured output.") from exc
        try:
            return LLMAnalysis.model_validate(raw)
        except Exception as exc:
            raise LLMProviderError("The LLM response failed structured validation.") from exc

    @staticmethod
    def _request_provider(api_key: str, model: str, timeout: float, base_url: str, prompt: str) -> Any:
        payload = {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        try:
            response = httpx.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return content
        except httpx.TimeoutException as exc:
            raise LLMProviderError("The LLM request timed out.") from exc
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise LLMProviderError("The LLM provider request failed.") from exc
