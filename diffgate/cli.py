"""diffgate CLI. Local: review a diff file/stdin. CI: review the PR that triggered the run."""

from __future__ import annotations

import argparse
import json
import os
import sys

import httpx

from diffgate import github, review


def _read_diff(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _ci_diff(repo: str, pr_number: int, token: str) -> str:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    with httpx.Client(timeout=30) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
    return resp.text


def _pr_number_from_event() -> int | None:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return None
    with open(event_path, "r", encoding="utf-8") as fh:
        event = json.load(fh)
    num = (event.get("pull_request") or {}).get("number")
    return int(num) if num else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="diffgate", description="Self-hosted AI code review.")
    parser.add_argument("--diff", help="Path to a unified diff file, or '-' for stdin.")
    parser.add_argument("--language", help="Primary language hint (e.g. python, typescript).")
    parser.add_argument("--model", help="Override the inference model.")
    parser.add_argument("--ci", action="store_true", help="Read the PR diff from the GitHub event.")
    parser.add_argument("--post-to-pr", action="store_true", help="Post the review as a PR comment (CI).")
    args = parser.parse_args(argv)

    repo = os.getenv("GITHUB_REPOSITORY", "")
    token = os.getenv("GITHUB_TOKEN", "")
    pr_number = _pr_number_from_event()

    if args.ci:
        if not (repo and token and pr_number):
            print(
                "diffgate: --ci requires GITHUB_REPOSITORY, GITHUB_TOKEN and a pull_request event.",
                file=sys.stderr,
            )
            return 2
        diff_text = _ci_diff(repo, pr_number, token)
    elif args.diff:
        diff_text = _read_diff(args.diff)
    else:
        parser.error("provide --diff <path|-> or --ci")

    language = args.language or os.getenv("DIFFGATE_LANGUAGE") or None
    result = review.review_diff(diff_text, language=language, model=args.model)
    comment = review.render_comment(result)
    print(comment)
    print(
        f"[model={result.model} provider={result.provider} latency={result.latency_ms}ms "
        f"tokens={result.prompt_tokens}/{result.completion_tokens}]",
        file=sys.stderr,
    )

    if args.post_to_pr:
        if not (repo and token and pr_number):
            print(
                "diffgate: --post-to-pr requires GITHUB_REPOSITORY, GITHUB_TOKEN and a pull_request event.",
                file=sys.stderr,
            )
            return 2
        cid = github.post_pr_comment(repo, pr_number, comment, token=token)
        print(f"diffgate: posted comment id={cid} to {repo}#{pr_number}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
