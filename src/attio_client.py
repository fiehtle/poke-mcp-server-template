from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


@dataclass
class AttioAPIError(RuntimeError):
    status_code: int
    code: str | None
    message: str
    method: str
    url: str
    response_body: Any

    def __str__(self) -> str:
        code_part = f" ({self.code})" if self.code else ""
        return f"Attio API error {self.status_code}{code_part}: {self.message} [{self.method} {self.url}]"

    @classmethod
    def from_response(cls, method: str, url: str, response: requests.Response) -> "AttioAPIError":
        message = response.reason or "Request failed"
        code = None
        response_body: Any

        try:
            response_body = response.json()
            if isinstance(response_body, dict):
                message = str(response_body.get("message") or message)
                code = response_body.get("code")
        except ValueError:
            response_body = response.text[:2000]

        return cls(
            status_code=response.status_code,
            code=code,
            message=message,
            method=method,
            url=url,
            response_body=response_body,
        )


class AttioClient:
    def __init__(
        self,
        *,
        token: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        backoff_seconds: float = 0.7,
    ) -> None:
        resolved_token = token or os.environ.get("ATTIO_ACCESS_TOKEN") or os.environ.get("ATTIO_API_KEY")
        if not resolved_token:
            raise RuntimeError(
                "Missing Attio access token. Set ATTIO_ACCESS_TOKEN (or ATTIO_API_KEY) in your environment."
            )

        self.base_url = (base_url or os.environ.get("ATTIO_BASE_URL") or "https://api.attio.com").rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {resolved_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "attio-complement-mcp/0.1.0",
            }
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_method = method.upper().strip()
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{normalized_path}"

        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        for attempt in range(self.max_retries + 1):
            try:
                response = self._session.request(
                    normalized_method,
                    url,
                    params=clean_params or None,
                    json=json_body,
                    timeout=self.timeout_seconds,
                )
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise RuntimeError(f"Network error while calling Attio API: {exc}") from exc
                time.sleep(self.backoff_seconds * (2 ** attempt))
                continue

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                retry_after = response.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    sleep_seconds = max(float(retry_after), self.backoff_seconds * (2 ** attempt))
                else:
                    sleep_seconds = self.backoff_seconds * (2 ** attempt)
                time.sleep(sleep_seconds)
                continue

            if not response.ok:
                raise AttioAPIError.from_response(normalized_method, url, response)

            if response.status_code == 204:
                return {"data": None}

            try:
                parsed = response.json()
                if isinstance(parsed, dict):
                    return parsed
                return {"data": parsed}
            except ValueError:
                return {"data": response.text}

        raise RuntimeError("Attio request retries exhausted unexpectedly.")

    def get_redirect_location(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{normalized_path}"
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        for attempt in range(self.max_retries + 1):
            try:
                response = self._session.request(
                    "GET",
                    url,
                    params=clean_params or None,
                    timeout=self.timeout_seconds,
                    allow_redirects=False,
                )
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise RuntimeError(f"Network error while calling Attio API: {exc}") from exc
                time.sleep(self.backoff_seconds * (2 ** attempt))
                continue

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                time.sleep(self.backoff_seconds * (2 ** attempt))
                continue

            if 300 <= response.status_code < 400:
                return {
                    "status_code": response.status_code,
                    "location": response.headers.get("Location"),
                }

            if not response.ok:
                raise AttioAPIError.from_response("GET", url, response)

            return {
                "status_code": response.status_code,
                "location": None,
            }

        raise RuntimeError("Attio redirect request retries exhausted unexpectedly.")
