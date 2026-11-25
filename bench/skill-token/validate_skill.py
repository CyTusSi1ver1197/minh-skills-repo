"""Validate an Agent Skill folder for Claude Code + GitHub Copilot portability.

Usage: python validate_skill.py <skill folder> [<skill folder> ...]
Checks: frontmatter parses; name == folder name and matches ^[a-z0-9-]{1,64}$; description
<= 1024 chars; every relative references/ assets/ scripts/ path named in any .md exists;
core SKILL.md within its size budget; no absolute paths. Exit 0 = all pass.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# core budgets from the plan (chars, frontmatter included)
CORE_BUDGET = {"running-when-a-request-is-made": 9000, "information-gathering-for-plan": 8000}  # v2.1: one read per class
REF = re.compile(r"(?<![\w/.-])((?:references|assets|scripts)/[\w./-]+?\.(?:md|py|json|txt|sh|ps1))")
ABS = re.compile(r"(?<![\w`<])(?:[A-Za-z]:\\\\?[\w]|/(?:home|Users|root|etc/claude|tmp)/)")


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        raise ValueError("no YAML frontmatter")
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("frontmatter not closed")
    data = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def validate(folder: Path) -> list[str]:
    errors: list[str] = []
    skill = folder / "SKILL.md"
    if not skill.is_file():
        return [f"{folder}: SKILL.md missing"]
    text = skill.read_text(encoding="utf-8")
    try:
        fm = frontmatter(text)
    except ValueError as exc:
        return [f"{skill}: {exc}"]
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != folder.name:
        errors.append(f"name '{name}' != folder '{folder.name}'")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        errors.append(f"name '{name}' is not lowercase-hyphen <= 64 chars")
    if not desc or len(desc) > 1024:
        errors.append(f"description length {len(desc)} not in 1..1024")
    budget = CORE_BUDGET.get(folder.name)
    if budget and len(text) > budget:
        errors.append(f"SKILL.md is {len(text)} chars > budget {budget}")
    for md in folder.rglob("*.md"):
        body = md.read_text(encoding="utf-8")
        for ref in set(REF.findall(body)):
            if "<" in ref or "*" in ref:
                continue
            if not (folder / ref).exists():
                errors.append(f"{md.relative_to(folder)} names missing file {ref}")
        for line_no, line in enumerate(body.splitlines(), 1):
            if ABS.search(line):
                errors.append(f"{md.relative_to(folder)}:{line_no} has an absolute path")
    return errors


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    failed = False
    for arg in argv:
        errs = validate(Path(arg))
        if errs:
            failed = True
            print(f"FAIL {arg}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"PASS {arg}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
