from diffgate.prompts import build_review_prompt


def test_prompt_includes_diff_and_sections():
    prompt = build_review_prompt("--- a/f.py\n+++ b/f.py\n+return None")
    assert "## Bugs" in prompt
    assert "## Security" in prompt
    assert "## Suggestions" in prompt
    assert "return None" in prompt


def test_prompt_truncates_huge_diff():
    prompt = build_review_prompt("x" * 50_000)
    assert "truncated" in prompt
    assert len(prompt) < 50_000
