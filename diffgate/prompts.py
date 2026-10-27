"""Review-prompt construction. The quality core of diffgate."""

MAX_DIFF_CHARS = 12000


def build_review_prompt(diff_text: str, language: str | None = None) -> str:
    diff = diff_text.strip()
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n...[diff truncated]"

    lang_line = f"Primary language: {language}.\n" if language else ""

    return f"""You are a strict, senior code reviewer. Review ONLY the diff below.
Find: (1) Bugs, (2) Security issues, (3) Concrete suggestions.

For every changed line, actively check for these high-severity issues first:
- Injection: user/variable data placed into SQL, shell, HTML, or paths via string
  formatting/f-strings/concatenation instead of parameterized/escaped APIs.
- Auth/access: missing authz checks, broken auth, privilege escalation.
- Secrets & data exposure: hardcoded credentials, tokens, or logging of PII/user
  data (emails, passwords) to files, stdout, or third parties.
- Unsafe input: unvalidated/unsanitized input, path traversal, deserialization.
- Correctness: null/None handling, off-by-one, resource leaks (unclosed files),
  wrong error handling, race conditions.

A change that REPLACES a safe pattern with an unsafe one (e.g. a parameterized
query rewritten as an f-string) is a critical finding — never miss it.

Rules:
- Cite file and line for every finding. Order findings most-severe first.
- No praise. No pure style nitpicks unless they cause a bug.
- Omit any category that has no findings.
- If nothing is wrong, reply with exactly: LGTM

{lang_line}Respond in markdown using only these section headers:
## Bugs
## Security
## Suggestions

DIFF:
```diff
{diff}
```
"""
