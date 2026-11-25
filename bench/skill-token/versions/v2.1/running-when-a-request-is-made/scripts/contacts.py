"""Find contacts for changed files and flag when owner review is needed.

Usage (from the repo root): python scripts/contacts.py <changed file> [<changed file> ...]
Owner source: CODEOWNERS (CODEOWNERS, .github/CODEOWNERS, docs/CODEOWNERS; last matching
pattern wins), else the top 3 committers from git log. Always exits 0.
"""
from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

CODEOWNERS_PATHS = ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]
RISKY = re.compile(r"(migrations?|schema|auth|security|\.github/workflows|(^|/)ci(/|\.|$)|pipeline|(^|/)api(/|$))",
                   re.IGNORECASE)


def load_codeowners(root: Path) -> list[tuple[str, list[str]]]:
    for rel in CODEOWNERS_PATHS:
        p = root / rel
        if p.is_file():
            rules = []
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    rules.append((parts[0], parts[1:]))
            return rules
    return []


def pattern_matches(pattern: str, path: str) -> bool:
    path = path.replace("\\", "/").removeprefix("./")
    anchored = pattern.startswith("/")
    pat = pattern.lstrip("/")
    if pat.endswith("/"):
        pat += "**"
    if pat == "*":
        return True
    candidates = [pat] if anchored or "/" in pat.rstrip("*") else [pat, f"**/{pat}"]
    for c in candidates:
        if fnmatch.fnmatch(path, c) or fnmatch.fnmatch(path, c.replace("**/", "")):
            return True
        if c.endswith("/**") and path.startswith(c[:-3]):
            return True
    return False


def owners_for(path: str, rules: list[tuple[str, list[str]]]) -> list[str]:
    owners: list[str] = []
    for pattern, who in rules:  # last match wins
        if pattern_matches(pattern, path):
            owners = who
    return owners


def top_committers(path: str) -> list[str]:
    try:
        out = subprocess.run(["git", "log", "--format=%an <%ae>", "--", path],
                             capture_output=True, text=True, timeout=30, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    counts = Counter(l for l in out.splitlines() if l.strip())
    return [f"{name} ({n} commits)" for name, n in counts.most_common(3)]


def main(files: list[str]) -> int:
    if not files:
        print(__doc__)
        return 0
    rules = load_codeowners(Path.cwd())
    reasons: list[str] = []
    for f in files:
        owners = owners_for(f, rules) if rules else []
        if owners:
            print(f"`{f}` → {' '.join(owners)} (CODEOWNERS)")
        else:
            committers = top_committers(f)
            who = ", ".join(committers) if committers else "no owner found (new file or no git history)"
            print(f"`{f}` → {who} (git log)")
        m = RISKY.search(f.replace("\\", "/"))
        if m:
            reasons.append(f"{f} touches '{m.group(1).strip('/')}'")
    if len(files) > 10:
        reasons.insert(0, f"{len(files)} files changed (> 10)")
    if reasons:
        print("needs owner review: yes (" + "; ".join(reasons) + ")")
    else:
        print("needs owner review: no (also check: ~400+ changed lines or a public API contract)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as exc:  # noqa: BLE001 - must never fail the planning flow
        print(f"contacts.py could not finish: {exc}")
        sys.exit(0)
