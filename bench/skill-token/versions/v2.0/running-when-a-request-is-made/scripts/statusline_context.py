"""Status-line command for Claude Code and GitHub Copilot CLI.

Reads the session JSON the tool pipes on stdin, works out the remaining context %,
writes it to <workspace>/.agent-context.json for scripts/context_check.py, and prints
a short status line. Unknown or null fields give "remaining": null.

Claude Code:  context_window.remaining_percentage, else 100 - context_window.used_percentage
Copilot CLI:  100 - context_window.used_percentage, else from
              context_window.current_context_tokens / context_window.displayed_context_limit
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def remaining_from(payload: dict) -> tuple[float | None, str]:
    cw = payload.get("context_window") or {}
    if not isinstance(cw, dict):
        return None, "unknown"
    if num(cw.get("remaining_percentage")) is not None:
        return float(cw["remaining_percentage"]), "claude-code"
    if num(cw.get("used_percentage")) is not None:
        tool = "copilot-cli" if "displayed_context_limit" in cw or "current_context_tokens" in cw else "claude-code"
        return 100.0 - float(cw["used_percentage"]), tool
    cur, lim = num(cw.get("current_context_tokens")), num(cw.get("displayed_context_limit"))
    if cur is not None and lim:
        return 100.0 * (1 - cur / lim), "copilot-cli"
    return None, "unknown"


def workspace_dir(payload: dict) -> Path:
    ws = payload.get("workspace") if isinstance(payload.get("workspace"), dict) else {}
    for key in ("project_dir", "current_dir", "cwd"):
        val = ws.get(key) or payload.get(key)
        if isinstance(val, str) and val and Path(val).is_dir():
            return Path(val)
    return Path(os.getcwd())


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    remaining, tool = remaining_from(payload)
    if remaining is not None:
        remaining = max(0.0, min(100.0, round(remaining, 1)))
    record = {"remaining": remaining, "tool": tool,
              "updated": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    try:
        (workspace_dir(payload) / ".agent-context.json").write_text(json.dumps(record), encoding="utf-8")
    except OSError:
        pass  # never break the status line
    print(f"ctx {remaining:g}% left" if remaining is not None else "ctx ?")
    return 0


if __name__ == "__main__":
    sys.exit(main())
