"""Static load measurement: how much skill text each version loads per request class.

Usage: python static_measure.py <version folder> [--as v1|v2.0|v2.1] [--append STATIC.md]
v2.1 = the live skills: python static_measure.py ../.. --as v2.1
Tokens are estimated as chars / 4. If ANTHROPIC_API_KEY is set, exact counts are
fetched from the Messages count_tokens endpoint as well.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

RUN = "running-when-a-request-is-made"
IG = "information-gathering-for-plan"

SCENARIOS = {
    "v1": {
        "A": [f"{RUN}/SKILL.md"],
        "A+IG": [f"{RUN}/SKILL.md", f"{IG}/SKILL.md"],
        "B": [f"{RUN}/SKILL.md"],
        "B-staged": [f"{RUN}/SKILL.md"],
        "C": [f"{RUN}/SKILL.md"],
    },
    "v2.1": {
        "A": [f"{RUN}/SKILL.md"],
        "A+IG": [f"{RUN}/SKILL.md", f"{IG}/SKILL.md"],
        "B": [f"{RUN}/SKILL.md", f"{RUN}/references/execution.md"],
        "B-staged": [f"{RUN}/SKILL.md", f"{RUN}/references/execution.md", f"{RUN}/references/staged-plans.md"],
        "C": [f"{RUN}/SKILL.md"],
    },
    "v2.0": {
        "A": [f"{RUN}/SKILL.md", f"{RUN}/references/planning.md",
              f"{RUN}/assets/PLAN.agent.template.md", f"{RUN}/assets/PLAN.human.template.md"],
        "A+IG": [f"{RUN}/SKILL.md", f"{RUN}/references/planning.md",
                 f"{RUN}/assets/PLAN.agent.template.md", f"{RUN}/assets/PLAN.human.template.md",
                 f"{IG}/SKILL.md", f"{IG}/references/gather-and-rank.md", f"{IG}/assets/report.template.md"],
        "B": [f"{RUN}/SKILL.md", f"{RUN}/references/execution.md",
              f"{RUN}/assets/PROGRESS.template.md", f"{RUN}/assets/EXECUTION-SUMMARY.template.md"],
        "B-staged": [f"{RUN}/SKILL.md", f"{RUN}/references/execution.md", f"{RUN}/references/staged-plans.md",
                     f"{RUN}/assets/PROGRESS.template.md", f"{RUN}/assets/EXECUTION-SUMMARY.template.md"],
        "C": [f"{RUN}/SKILL.md"],
    },
}


def exact_tokens(text: str) -> int | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    body = json.dumps({"model": os.environ.get("COUNT_MODEL", "claude-sonnet-4-5"),
                       "messages": [{"role": "user", "content": text}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages/count_tokens", data=body, headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["input_tokens"]
    except Exception:  # noqa: BLE001 - optional enrichment only
        return None


def measure(version_dir: Path, version: str | None = None) -> list[dict]:
    version = version or version_dir.name
    if version not in SCENARIOS:
        raise SystemExit(f"unknown version folder name {version!r}; expected v1 or v2")
    rows = []
    for scenario, files in SCENARIOS[version].items():
        text = ""
        for f in files:
            p = version_dir / f
            if not p.exists():
                raise SystemExit(f"missing file for {version}/{scenario}: {p}")
            text += p.read_text(encoding="utf-8")
        rows.append({"version": version, "scenario": scenario, "files": len(files), "reads": len([f for f in files if not f.endswith(("/SKILL.md",))]),
                     "chars": len(text), "est_tokens": round(len(text) / 4),
                     "exact_tokens": exact_tokens(text)})
    return rows


def to_markdown(rows: list[dict]) -> str:
    out = ["| Version | Class | Files | Extra reads | Chars | Est. tokens | Exact tokens |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['version']} | {r['scenario']} | {r['files']} | {r['reads']} | {r['chars']:,} | "
                   f"{r['est_tokens']:,} | {r['exact_tokens'] if r['exact_tokens'] is not None else '-'} |")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    as_version = argv[argv.index("--as") + 1] if "--as" in argv else None
    rows = measure(Path(argv[0]), as_version)
    md = to_markdown(rows)
    print(md)
    if "--append" in argv:
        target = Path(argv[argv.index("--append") + 1])
        with target.open("a", encoding="utf-8") as fh:
            fh.write(md + "\n")
    if "--json" in argv:
        print(json.dumps(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
