"""Reusable API security hooks."""
from __future__ import annotations
import hmac
from fastapi import Header, HTTPException


def api_key_dependency(expected_key: str | None):
    """Return a FastAPI dependency that is open when no key is configured.

    Deployments can configure a secret key without changing route code. The
    comparison is constant-time and the key is never returned by the API.
    """
    def verify(x_truepass_api_key: str | None = Header(default=None)) -> None:
        if expected_key is None:
            return
        if x_truepass_api_key is None or not hmac.compare_digest(x_truepass_api_key, expected_key):
            raise HTTPException(status_code=401, detail="invalid or missing API key")
    return verify
