# diffgate

Self-hosted AI code review as a GitHub Action. On every pull request it fetches the diff, has a model **you** run
review it (local Ollama, or your own gateway), and posts one comment with bugs, security issues and concrete
suggestions. Your code never leaves your network.

## Status

Early version. The pipeline, the GitHub Action packaging and the unit tests are done (5 tests, all passing; they
mock the model call). A full live run against a real model on a real PR hasn't been recorded yet, and the review
prompt hasn't been tuned on real diffs. Treat the review quality as unmeasured.

## How it works

```
PR diff (GitHub API) -> prompt (prompts.py) -> model (infer.py: Ollama or gateway) -> markdown (review.py) -> PR comment (github.py)
```

The prompt tells the model to check the high-severity issues first (injection, auth, secrets and PII in logs,
unsafe input, resource leaks), to cite file and line for every finding, and to reply `LGTM` when nothing is wrong.
Diffs over 12,000 characters are truncated.

## Run locally

```bash
pip install -r requirements.txt        # just httpx
ollama pull qwen2.5:3b                 # any Ollama model works, see DIFFGATE_MODEL

python -m diffgate.cli --diff samples/buggy.diff     # a sample diff that turns a parameterised query into an f-string
git diff main | python -m diffgate.cli --diff -      # or pipe any unified diff
```

## Run as a GitHub Action

The runner has to reach your model: a self-hosted runner with Ollama, or a host it can reach.

```yaml
# .github/workflows/diffgate.yml
on: [pull_request]
jobs:
  review:
    runs-on: self-hosted
    permissions:
      pull-requests: write
    steps:
      - uses: sathvik-lokesh/diffgate@main
        with:
          ollama-base-url: http://localhost:11434
          model: qwen2.5:3b
          language: python
```

Inputs: `model`, `language`, `ollama-base-url`, `gateway-url` (instead of Ollama), `github-token` (defaults to the
workflow token).

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `DIFFGATE_MODEL` | `qwen2.5:3b` | model name |
| `DIFFGATE_GATEWAY_URL` | unset | use a `POST /v1/generate` gateway instead of Ollama |
| `DIFFGATE_LANGUAGE` | unset | primary language hint for the prompt |
| `DIFFGATE_TIMEOUT` | `120` | seconds per model call |

## Layout

- `diffgate/prompts.py` review prompt
- `diffgate/infer.py` Ollama by default, gateway via `DIFFGATE_GATEWAY_URL`
- `diffgate/review.py` diff -> review -> markdown comment
- `diffgate/github.py` posts the comment on the PR
- `diffgate/cli.py` local (`--diff`) and CI (`--ci --post-to-pr`) entry points
- `action.yml`, `Dockerfile` GitHub Action packaging

## Tests

```bash
python -m pytest
```

## Licence

MIT
