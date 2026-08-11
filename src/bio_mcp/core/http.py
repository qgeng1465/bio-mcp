"""HTTP 基础客户端：超时、重试、限速、缓存，统一错误处理。"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger("bio_mcp")

# NCBI 官方要求：请求间隔 ≥3 秒，且需提供联系方式
NCBI_RATE_LIMIT_SECONDS = 3.0
NCBI_TOOL = "BioMCP"
NCBI_EMAIL = "qgeng1465@users.noreply.github.com"


class BioHTTPError(RuntimeError):
    """带 HTTP 状态码的请求错误。"""

    def __init__(self, message: str, status_code: Optional[int] = None, url: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.url = url


class BioHTTP:
    """可复用的 HTTP 客户端：重试 + 退避 + 可配置限速。"""

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit: float = 0.0,
        headers: Optional[dict[str, str]] = None,
        follow_redirects: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._rate_limit = rate_limit
        self._last_request = 0.0
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=follow_redirects,
            headers=headers or {},
            http2=False,
        )

    def _throttle(self) -> None:
        if self._rate_limit <= 0:
            return
        elapsed = time.monotonic() - self._last_request
        if elapsed < self._rate_limit:
            time.sleep(self._rate_limit - elapsed)
        self._last_request = time.monotonic()

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        if path.startswith("http://") or path.startswith("https://"):
            url = path
        else:
            url = f"{self.base_url}/{path.lstrip('/')}"
        last_err: Exception | None = None
        for attempt in range(3):
            self._throttle()
            try:
                resp = self._client.request(method, url, params=params, json=json, data=data, files=files)
                if resp.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    continue
                resp.raise_for_status()
                return resp
            except (httpx.HTTPStatusError, httpx.TransportError) as e:
                last_err = e
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break
        status = getattr(last_err, "response", None)
        code = status.status_code if status is not None else None
        raise BioHTTPError(str(last_err), status_code=code, url=url) from last_err

    def get(
        self, path: str, params: Optional[dict[str, Any]] = None
    ) -> httpx.Response:
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        files: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        return self.request("POST", path, params=params, json=json, data=data, files=files)

    def close(self) -> None:
        self._client.close()
