#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


API_URL = os.environ.get("KIMI_API_BASE_URL", "https://api.moonshot.ai/v1").rstrip("/") + "/chat/completions"
MODEL = os.environ.get("KIMI_MODEL", "kimi-k2.5")
TIMEOUT_SECONDS = float(os.environ.get("KIMI_TIMEOUT_SECONDS", "90"))
TEMPERATURE = float(os.environ.get("KIMI_TEMPERATURE", "1"))


def _extract_reasoning(message: dict) -> str:
    reasoning = message.get("reasoning_content", "")
    return reasoning if isinstance(reasoning, str) else ""


def _extract_content(message: dict) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
        return "".join(chunks)
    return ""


def main() -> int:
    api_key = os.environ.get("KIMI_API_KEY", "").strip()
    if not api_key:
        print("KIMI_API_KEY is not set.", file=sys.stderr)
        return 1
    prompt = sys.stdin.read()
    if not prompt.strip():
        print("Prompt was empty.", file=sys.stderr)
        return 1

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a cautious research-manager assistant. "
                    "Return only valid JSON and keep every claim grounded in the provided evidence."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": TEMPERATURE,
        "stream": False,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(detail or str(exc), file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        envelope = json.loads(raw)
        message = envelope["choices"][0]["message"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        print(raw, file=sys.stderr)
        return 1

    content = _extract_content(message)
    reasoning = _extract_reasoning(message)
    if not content.strip():
        print(raw, file=sys.stderr)
        return 1

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        print(content)
        return 0

    if isinstance(parsed, dict) and reasoning and not parsed.get("manager_reasoning"):
        parsed["manager_reasoning"] = reasoning
    print(json.dumps(parsed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
