"""Filter-Verify pipeline for AI text inputs (Lab 6: prompt injection protection)."""

from __future__ import annotations

import re
from dataclasses import dataclass

BLOCK_MESSAGE = (
    "Potential prompt injection detected. Input was blocked for security reasons."
)


@dataclass(frozen=True)
class FilterResult:
    passed: bool
    reason: str | None = None


class InputGuardError(Exception):
    """Raised when user-controlled text fails security validation."""


# Stage 1: fast structural regex filter for known injection patterns.
STRUCTURAL_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\[SYSTEM_OVERRIDE_HOOK\]", re.IGNORECASE), "system_override_hook"),
    (re.compile(r"diagnostic_mode", re.IGNORECASE), "diagnostic_mode"),
    (re.compile(r"print_instructions", re.IGNORECASE), "print_instructions"),
    (re.compile(r"Execute\s+SQL", re.IGNORECASE), "execute_sql"),
    (re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE), "ignore_previous_instructions"),
    (re.compile(r"system\s+override", re.IGNORECASE), "system_override"),
    (re.compile(r"developer\s+message", re.IGNORECASE), "developer_message"),
    (re.compile(r"reveal\s+secrets", re.IGNORECASE), "reveal_secrets"),
    (re.compile(r"print\s+all\s+users", re.IGNORECASE), "print_all_users"),
    (re.compile(r"SELECT\s+\*\s+FROM", re.IGNORECASE), "sql_select_all"),
    (
        re.compile(
            r'\{\s*["\']?(role|system|instruction|command|override)["\']?\s*:',
            re.IGNORECASE,
        ),
        "json_instruction_block",
    ),
)

# Stage 2: simulated deeper verification heuristics.
VERIFY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"disregard\s+(all\s+)?(prior|previous)\s+instructions", re.IGNORECASE), "disregard_instructions"),
    (re.compile(r"you\s+are\s+now\s+(a|an|the)\s+", re.IGNORECASE), "role_reassignment"),
    (re.compile(r"new\s+instructions\s*:", re.IGNORECASE), "new_instructions"),
    (re.compile(r"<\s*/?\s*system\s*>", re.IGNORECASE), "system_tag"),
    (re.compile(r"jailbreak", re.IGNORECASE), "jailbreak"),
    (re.compile(r"dump\s+(the\s+)?(database|db|users)", re.IGNORECASE), "dump_database"),
)


def structural_filter(text: str) -> FilterResult:
    """Fast regex scan for structured prompt-injection markers."""
    for pattern, reason in STRUCTURAL_PATTERNS:
        if pattern.search(text):
            return FilterResult(passed=False, reason=reason)
    return FilterResult(passed=True)


def verify_input(text: str) -> FilterResult:
    """Simulated deeper LLM-style verification using secondary heuristics."""
    normalized = " ".join(text.split())
    for pattern, reason in VERIFY_PATTERNS:
        if pattern.search(normalized):
            return FilterResult(passed=False, reason=reason)

    # Block embedded JSON objects that look like instruction payloads.
    if re.search(r'\{\s*"[^"]+"\s*:\s*"[^"]*(instruction|override|system)[^"]*"', normalized, re.IGNORECASE):
        return FilterResult(passed=False, reason="embedded_json_instruction")

    return FilterResult(passed=True)


def validate_ai_input(text: str) -> str:
    """
    Public entry point: run Filter-Verify pipeline and return safe text.

    Raises InputGuardError when malicious patterns are detected.
    """
    if text is None:
        raise InputGuardError(BLOCK_MESSAGE)

    sanitized = text.strip()
    if not sanitized:
        raise InputGuardError(BLOCK_MESSAGE)

    filter_result = structural_filter(sanitized)
    if not filter_result.passed:
        raise InputGuardError(BLOCK_MESSAGE)

    verify_result = verify_input(sanitized)
    if not verify_result.passed:
        raise InputGuardError(BLOCK_MESSAGE)

    return sanitized
