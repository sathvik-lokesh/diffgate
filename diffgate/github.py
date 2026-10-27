"""Post a review as a GitHub PR comment. Optional — the core works without GitHub."""

from __future__ import annotations

import os

import httpx


def post_pr_comment(repo: str, pr_number: int, body: str, token: str | None = None) -> int:
    """Post `body` as a comment on repo#pr_number. Returns the new comment id."""
    token = token or os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, headers=headers, json={"body": body})
        resp.raise_for_status()
    return resp.json().get("id", 0)
