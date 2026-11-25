"""Print the remaining context-window % for the low-context stop rule.

Usage: python scripts/context_check.py [repo root]
Reads <repo root>/.agent-context.json (written by scripts/statusline_context.py).
Prints `remaining=<n>` or `remaining=unknown` (no file, unreadable, null, or older than 10 minutes).
Always exits 0.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_AGE = timedelta(minutes=10)


def find_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".agent-context.json").exists() or (p / ".git").exists():
            return p
    return start


def main(argv: list[str]) -> int:
    root = Path(argv[0]) if argv else find_root(Path.cwd())
    try:
        data = json.loads((root / ".agent-context.json").read_text(encoding="utf-8"))
        rem = data.get("remaining")
        updated = data.get("updated")
        if updated:
            ts = datetime.fromisoformat(str(updated).replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - ts > MAX_AGE:
                rem = None
        if isinstance(rem, (int, float)) and not isinstance(rem, bool):
            print(f"remaining={rem:g}")
            return 0
    except (OSError, ValueError, AttributeError):
        pass
    print("remaining=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
