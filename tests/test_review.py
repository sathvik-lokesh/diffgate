import diffgate.review as review_mod
from diffgate.review import ReviewResult, render_comment, review_diff


def test_review_diff_uses_inference(monkeypatch):
    def fake_generate(prompt, model=None):
        return "LGTM", {
            "model": "qwen2.5:3b",
            "provider": "local",
            "latency_ms": 5,
            "prompt_tokens": 10,
            "completion_tokens": 1,
        }

    monkeypatch.setattr(review_mod.infer, "generate", fake_generate)
    result = review_diff("+x = 1")

    assert result.body == "LGTM"
    assert result.model == "qwen2.5:3b"
    assert result.provider == "local"
    assert result.latency_ms == 5


def test_review_diff_empty_output_falls_back(monkeypatch):
    monkeypatch.setattr(
        review_mod.infer,
        "generate",
        lambda prompt, model=None: ("   ", {"model": "m", "provider": "local", "latency_ms": 1}),
    )
    result = review_diff("+x")
    assert "empty review" in result.body


def test_render_comment_has_header_body_and_footer():
    result = ReviewResult(
        body="## Bugs\nnone here",
        model="m",
        provider="local",
        latency_ms=12,
        prompt_tokens=1,
        completion_tokens=2,
    )
    out = render_comment(result)
    assert "## diffgate review" in out
    assert "none here" in out
    assert "never left your network" in out
