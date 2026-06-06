#!/usr/bin/env python3
"""AI Security Reviewer for Smart Resume Builder pull requests (Lab 7)."""

from __future__ import annotations

import os
import re
import sys

PROJECT_CONTEXT = """
Project: Smart Resume Builder (academic mini project)

Stack:
- Backend: FastAPI
- Database: MongoDB (Motor)
- Authentication: JWT (python-jose) + bcrypt password hashing
- AI provider: Groq (resume generation and job matching)
- Frontend: static SPA served from /ui/
- API docs: /docs

Lab 6 security (already implemented):
- Filter-Verify pipeline in app/security/input_guard.py
- validate_ai_input() must run before any Groq call in app/services/ai_service.py
- Security tests in test_security_injection.py (11 tests, Groq is mocked)

Expected and NOT vulnerabilities:
- unittest.mock / patch used in tests to mock Groq or MongoDB
- verify_input() is a simulated deeper check (not a live LLM call)
- Academic/demo scope; missing production hardening alone is NOT a finding
- Placeholder values in .env.example (change_me, your_groq_api_key_here)
- Environment variables loaded via pydantic-settings (.env), not hardcoded in app code
- CI workflow env vars like ci-test-groq-key in GitHub Actions (not real secrets)
"""

REVIEW_PROMPT = """
You are a senior application security reviewer for the Smart Resume Builder mini project.

{context}

Review ONLY the git diff below for CRITICAL code-level security issues.

Flag ONLY if the diff introduces:
1. Hardcoded API keys, database passwords, JWT secrets, or Groq/Gemini keys in source code
2. Removal or bypass of validate_ai_input / input_guard before Groq calls
3. Sending raw user input directly to Groq without Filter-Verify protection
4. Weakening JWT authentication or bcrypt password hashing
5. Disabling, deleting, or skipping security tests (test_security_injection.py)
6. Unsafe database access patterns (e.g., unsanitized query injection)
7. Exposing secrets in logs, print statements, or API responses

Do NOT flag:
- Academic mini-project limitations
- Mocked Groq/client in tests
- Simulated verify_input implementation
- Documentation or README-only changes unless they embed real secrets
- GitHub Actions secret references like ${{ secrets.GEMINI_API_KEY }}

RESPONSE FORMAT (strict):
- If the diff is safe or has no critical issues, start your response with exactly:
  SAFE_CODE
- If you find a critical vulnerability in the diff, start with exactly:
  VULNERABILITY_FOUND
- After the first line, provide a concise explanation (2-6 sentences).

Git diff to review:
---
{diff}
---
"""


def _safe_skip(message: str) -> None:
    print(f"SAFE_CODE\n{message}")


def _safe_exception_message(exc: Exception, api_key: str | None = None) -> str:
    """Return exception text with secrets redacted."""
    message = str(exc).strip() or repr(exc)
    if api_key:
        message = message.replace(api_key, "[REDACTED]")
    message = re.sub(r"AIza[\w-]+", "[REDACTED]", message)
    message = re.sub(r"gsk_[\w-]+", "[REDACTED]", message)
    message = re.sub(r"sk-[\w-]+", "[REDACTED]", message)
    message = re.sub(
        r'(?i)(api[_-]?key\s*[:=]\s*)[^\s"\']+',
        r"\1[REDACTED]",
        message,
    )
    return message[:500]


def _safe_unavailable(exc: Exception, api_key: str | None = None) -> None:
    print(
        "SAFE_CODE\n"
        "AI reviewer unavailable.\n"
        f"Error type: {exc.__class__.__name__}\n"
        f"Error message: {_safe_exception_message(exc, api_key)}"
    )


def main() -> int:
    diff = sys.stdin.read()
    if not diff.strip():
        _safe_skip("No code changes in diff to review.")
        return 0

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        _safe_skip("GEMINI_API_KEY not configured; AI review skipped.")
        return 0

    try:
        from google import genai
    except ImportError:
        _safe_skip("google-genai package not installed; AI review skipped.")
        return 0

    client = genai.Client(api_key=api_key)
    prompt = REVIEW_PROMPT.format(context=PROJECT_CONTEXT, diff=diff[:120000])

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        review_text = (response.text or "").strip()
    except Exception as exc:
        _safe_unavailable(exc, api_key)
        return 0

    if not review_text:
        _safe_skip("AI reviewer returned an empty response.")
        return 0

    print(review_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
