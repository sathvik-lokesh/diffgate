"""diffgate review pipeline: diff -> prompt -> inference -> markdown review."""

from __future__ import annotations

from dataclasses import dataclass

from diffgate import infer, prompts


@dataclass
class ReviewResult:
    body: str
    model: str
    provider: str
    latency_ms: int
    prompt_tokens: int | None
    completion_tokens: int | None


def review_diff(diff_text: str, language: str | None = None, model: str | None = None) -> ReviewResult:
    prompt = prompts.build_review_prompt(diff_text, language=language)
    text, meta = infer.generate(prompt, model=model)
    body = text.strip() or "_diffgate produced an empty review._"
    return ReviewResult(
        body=body,
        model=meta.get("model", "?"),
        provider=meta.get("provider", "?"),
        latency_ms=meta.get("latency_ms", 0),
        prompt_tokens=meta.get("prompt_tokens"),
        completion_tokens=meta.get("completion_tokens"),
    )


def render_comment(result: ReviewResult) -> str:
    footer = (
        "\n\n---\n"
        f"_diffgate self-hosted review · {result.provider}/{result.model} · "
        f"{result.latency_ms}ms · your code never left your network._"
    )
    return f"## diffgate review\n\n{result.body}{footer}"
