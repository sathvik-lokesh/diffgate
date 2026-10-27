"""Inference adapter: local Ollama by default, optional FastAPI /v1/generate gateway."""

from __future__ import annotations

import os
import time

import httpx


def generate(prompt: str, model: str | None = None) -> tuple[str, dict]:
    """Return (text, meta). Calls Ollama directly, or the gateway if DIFFGATE_GATEWAY_URL is set.

    The gateway is any service exposing POST /v1/generate {"prompt"} -> {"text", "model", ...}.
    """
    base = (os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
    model = model or os.getenv("DIFFGATE_MODEL") or "qwen2.5:3b"
    timeout = float(os.getenv("DIFFGATE_TIMEOUT") or "120")
    gateway = os.getenv("DIFFGATE_GATEWAY_URL", "").strip() or None

    start = time.perf_counter()
    with httpx.Client(timeout=timeout) as client:
        if gateway:
            resp = client.post(f"{gateway.rstrip('/')}/v1/generate", json={"prompt": prompt})
            resp.raise_for_status()
            data = resp.json()
            text = data.get("text", "")
            meta = {
                "model": data.get("model", model),
                "provider": data.get("provider", "gateway"),
                "prompt_tokens": data.get("prompt_tokens"),
                "completion_tokens": data.get("completion_tokens"),
            }
        else:
            resp = client.post(
                f"{base}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "")
            meta = {
                "model": model,
                "provider": "local",
                "prompt_tokens": data.get("prompt_eval_count"),
                "completion_tokens": data.get("eval_count"),
            }

    meta["latency_ms"] = int((time.perf_counter() - start) * 1000)
    return text, meta
