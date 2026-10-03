import json
import logging
import math
import os
import time
from collections.abc import Callable
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Any

import httpx

from app.schemas.llm_analysis import AnalysisRequest, LLMAnalysis
from app.services.prompts.resume_analysis import SYSTEM_PROMPT, build_analysis_prompt, build_repair_prompt


class LLMConfigurationError(ValueError):
    pass


class LLMProviderError(RuntimeError):
    pass


class LLMRateLimitError(LLMProviderError):
    """The provider rejected the request because its rate limit was exceeded."""

    def __init__(self, message: str = "The LLM provider rate limit was exceeded.", retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class _LLMStructuredShapeError(ValueError):
    """The decoded response cannot safely be sent to typed validation."""


logger = logging.getLogger(__name__)
_RESPONSE_FORMAT = {"type": "json_object"}
_DIAGNOSTIC_LIMIT = 1200
_MAX_RETRIES = 1
_MAX_BACKOFF_SECONDS = 2.0
_DEFAULT_BACKOFF_SECONDS = 0.5


def _redact_diagnostic(value: Any, secret: str = "") -> str:
    """Return bounded provider diagnostics without credentials or auth headers."""
    secret_names = {"api_key", "apikey", "authorization", "token", "access_token", "secret"}

    def clean(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: "[REDACTED]" if key.lower() in secret_names else clean(val) for key, val in item.items()}
        if isinstance(item, list):
            return [clean(val) for val in item]
        if isinstance(item, str):
            return item.replace("Bearer ", "Bearer [REDACTED]")
        return item

    try:
        rendered = json.dumps(clean(value), ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        rendered = str(value)
    if secret:
        rendered = rendered.replace(secret, "[REDACTED]")
    return rendered[:_DIAGNOSTIC_LIMIT]


def _response_diagnostic(response: httpx.Response, secret: str = "") -> str:
    try:
        return _redact_diagnostic(response.json(), secret)
    except ValueError:
        return _redact_diagnostic(response.text, secret)


def _retry_after_seconds(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


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
        raw = self._complete(api_key, model, timeout, base_url, prompt)
        decoded = self._decode_json(raw)
        try:
            self._validate_shape(decoded)
            return LLMAnalysis.model_validate(decoded)
        except Exception as exc:
            logger.warning("LLM response requires one bounded schema repair: %s", str(exc)[:500])
            repaired = self._complete(api_key, model, timeout, base_url, build_repair_prompt(request, decoded))
            repaired_decoded = self._decode_json(repaired)
            try:
                self._validate_shape(repaired_decoded)
                return LLMAnalysis.model_validate(repaired_decoded)
            except Exception as repair_exc:
                logger.error("LLM response parsing failed after repair: structured validation error=%s", str(repair_exc)[:500])
                raise LLMProviderError("The LLM response failed structured validation.") from repair_exc

    def _complete(self, api_key: str, model: str, timeout: float, base_url: str, prompt: str) -> Any:
        # A repair uses the same provider, JSON mode, and rate-limit handling.
        return self._provider(api_key, model, timeout, prompt) if self._provider else self._request_provider(api_key, model, timeout, base_url, prompt)

    @staticmethod
    def _decode_json(raw: Any) -> Any:
        if not isinstance(raw, str):
            return raw
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("LLM response parsing failed: malformed JSON error=%s", str(exc)[:500])
            raise LLMProviderError("The LLM returned malformed structured output.") from exc

    @staticmethod
    def _validate_shape(value: Any) -> None:
        if not isinstance(value, dict):
            raise _LLMStructuredShapeError("top-level response must be a JSON object")
        for field in ("strong_matches", "partial_matches"):
            entries = value.get(field, [])
            if not isinstance(entries, list):
                raise _LLMStructuredShapeError(f"{field} must be an array")
            if any(not isinstance(entry, dict) for entry in entries):
                raise _LLMStructuredShapeError(f"{field} must contain objects only")

    @staticmethod
    def _request_provider(api_key: str, model: str, timeout: float, base_url: str, prompt: str) -> Any:
        payload = {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": _RESPONSE_FORMAT,
        }
        logger.info("Sending LLM request model=%s response_format_sent=%s", model, "response_format" in payload)
        for attempt in range(_MAX_RETRIES + 1):
            try:
                response = httpx.post(
                    f"{base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                    timeout=timeout,
                )
                if response.status_code >= 400:
                    logger.error(
                        "LLM provider HTTP error status=%s model=%s response_format_sent=%s attempt=%s body=%s",
                        response.status_code,
                        model,
                        "response_format" in payload,
                        attempt + 1,
                        _response_diagnostic(response, api_key),
                    )
                response.raise_for_status()
                try:
                    response_body = response.json()
                    content = response_body["choices"][0]["message"]["content"]
                    if not isinstance(content, str) or not content.strip():
                        raise TypeError("message.content was empty or not a string")
                except (ValueError, KeyError, IndexError, TypeError) as exc:
                    logger.error(
                        "LLM response parsing failed status=%s model=%s response_format_sent=%s error=%s body=%s",
                        response.status_code,
                        model,
                        "response_format" in payload,
                        str(exc)[:500],
                        _response_diagnostic(response, api_key),
                    )
                    raise LLMProviderError("The LLM provider returned an invalid response.") from exc
                return content
            except httpx.TimeoutException as exc:
                logger.error("LLM provider timeout model=%s response_format_sent=%s", model, "response_format" in payload)
                raise LLMProviderError("The LLM request timed out.") from exc
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 429:
                    raise LLMProviderError(f"The LLM provider rejected the request (HTTP {exc.response.status_code}).") from exc
                retry_after = _retry_after_seconds(exc.response)
                if attempt < _MAX_RETRIES:
                    delay = min(retry_after if retry_after is not None else _DEFAULT_BACKOFF_SECONDS, _MAX_BACKOFF_SECONDS)
                    logger.warning("LLM provider rate limited; retrying once after %.3f seconds", delay)
                    time.sleep(delay)
                    continue
                raise LLMRateLimitError(retry_after=retry_after) from exc
            except httpx.HTTPError as exc:
                logger.error("LLM provider transport error model=%s error=%s", model, str(exc)[:500])
                raise LLMProviderError("The LLM provider request failed.") from exc
