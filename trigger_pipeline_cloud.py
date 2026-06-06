#!/usr/bin/env python3
"""Lab 8: Send a Smart Resume Builder business event to a Make.com webhook."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_ENV_VAR = "MAKE_WEBHOOK_URL"
MISSING_WEBHOOK_MESSAGE = (
    "MAKE_WEBHOOK_URL is not configured. Add it to .env or your environment."
)


def build_payload() -> dict[str, object]:
    """Build a demo business event for resume generation and job match review."""
    return {
        "event_time": datetime.now(timezone.utc).isoformat(),
        "event_type": "resume_job_match_review",
        "user_email": "demo.user@example.com",
        "candidate_name": "Demo Candidate",
        "resume_summary": (
            "Software engineer with 4 years of Python, FastAPI, MongoDB, and REST API "
            "experience building resume and job-matching tools."
        ),
        "job_description": (
            "Backend Python developer with FastAPI, MongoDB, JWT authentication, and "
            "AI integration experience."
        ),
        "similarity_score": 87.5,
        "system_status": "completed",
        "source": "smart_resume_builder_local_trigger",
    }


def main() -> int:
    webhook_url = os.environ.get(WEBHOOK_ENV_VAR, "").strip()
    if not webhook_url:
        print(MISSING_WEBHOOK_MESSAGE)
        return 1

    payload = build_payload()
    print("Transmitting Smart Resume Builder event to Make.com webhook...")
    print(f"Event type: {payload['event_type']}")

    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
    except requests.RequestException as exc:
        print(f"Request failed: {exc.__class__.__name__}: {exc}")
        return 1

    print(f"Response status code: {response.status_code}")

    if response.status_code in (200, 202):
        print("Success: Make.com webhook accepted the event.")
        return 0

    print("Failure: Make.com webhook did not accept the event.")
    if response.text:
        print(f"Response body: {response.text[:300]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
