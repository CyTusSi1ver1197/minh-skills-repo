"""Rebuild the Status block of a staged plan's FLOW.md from each stage's PROGRESS.md.

Usage: python scripts/flow_status.py BuildPlans/<plan-name>
Only the text between <!-- flow-status:start --> and <!-- flow-status:end --> is replaced.
Idempotent: the block contains no run timestamp, only data from the stage files.
Exit 0 = updated; 1 = Flows table and stage folders don't match; 2 = usage/format error.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

START, END = "<!-- flow-status:start -->", "<!-- flow-status:end -->"
STAGE_DIR = re.compile(r"^(F\d+-S\d+)(?:-.*)?$")
DONE = {"MET"}


def table_after(text: str, heading: str) -> list[list[str]]:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.M)
    if not m:
        return []
    rows = []
    for line in text[m.end():].splitlines():
        s = line.strip()
        if s.startswith("## "):
            break
        if s.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", s):
            rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows[1:] if rows else []  # drop header


def ids(cell: str) -> list[str]:
    return re.findall(r"F\d+-S\d+", cell)


def field(text: str, name: str) -> str:
    m = re.search(rf"{name}:\s*([^·\n]+)", text)
    return m.group(1).strip() if m else ""


def read_stage(folder: Path) -> dict:
    prog = folder / "PROGRESS.md"
    t = prog.read_text(encoding="utf-8") if prog.exists() else ""
    status = " ".join((field(t, "Status") or "TODO").upper().split())
    if "|" in status or status not in {"TODO", "IN PROGRESS", "PAUSED", "MET", "NOT MET"}:
        status = "TODO"
    dc_rows = [l for l in t.splitlines() if re.match(r"^\|\s*(?:F\d+-S\d+/)?DC-\d+", l.strip())]
    met = sum(1 for l in dc_rows if re.search(r"\|\s*MET\s*\|", l))
    log = [l.strip() for l in t.split("## Session log", 1)[1].splitlines()
           if re.match(r"^\|\s*\d{4}-\d{2}-\d{2}", l.strip())] if "## Session log" in t else []
    return {"status": status, "met": met, "total": len(dc_rows), "updated": field(t, "Updated") or "-",
            "next": field(t, "Next step") or "-", "needs": ids(field(t, "Needs")),
            "resume": field(t, "Resume note"), "log": log}


def build(plan: Path) -> tuple[str, list[str]]:
    flow_md = (plan / "FLOW.md").read_text(encoding="utf-8")
    flows = []
    for r in table_after(flow_md, "Flows"):
        if len(r) < 4:
            continue
        flows.append({"id": r[0], "kind": r[1].lower(), "stages": ids(r[2]), "after": ids(r[3])})
    folders = {}
    for d in sorted(p for p in plan.iterdir() if p.is_dir()):
        m = STAGE_DIR.match(d.name)
        if m:
            folders[m.group(1)] = d
    listed = [s for f in flows for s in f["stages"]]
    errors = [f"stage {s} is in the Flows table but has no folder" for s in listed if s not in folders]
    errors += [f"folder {folders[s].name} is not in the Flows table" for s in folders if s not in listed]
    stages = {s: read_stage(folders[s]) for s in listed if s in folders}

    def met(s: str) -> bool:
        return stages.get(s, {}).get("status") in DONE

    lines = ["| Flow | Kind | Done | Current stage | Next stage |", "|---|---|---|---|---|"]
    ready = []
    for f in flows:
        st = f["stages"]
        done = sum(met(s) for s in st)
        current = next((s for s in st if stages.get(s, {}).get("status") in {"IN PROGRESS", "PAUSED"}), "-")
        nxt = next((s for s in st if not met(s)), None)
        if nxt is None:
            nxt_txt = "done"
        else:
            deps = (f["after"] if nxt == st[0] else []) + stages.get(nxt, {}).get("needs", [])
            blockers = [b for b in deps if not met(b)]
            nxt_txt = f"{nxt} (waits for {', '.join(blockers)})" if blockers else nxt
            if not blockers:
                ready.append(f"{nxt} ({f['id']}, {f['kind']})")
        lines.append(f"| {f['id']} | {f['kind']} | {done}/{len(st)} | {current} | {nxt_txt} |")
    lines += ["", "| Stage | Status | DCs MET | Updated | Next step | Resume note |", "|---|---|---|---|---|---|"]
    for s in listed:
        if s in stages:
            x = stages[s]
            note = x["resume"] if x["status"] == "PAUSED" else ""
            lines.append(f"| {s} | {x['status']} | {x['met']}/{x['total']} | {x['updated']} | {x['next']} | {note} |")
    lines += ["", "Ready now: " + (", ".join(ready) if ready else "none")]
    logs = sorted({l for x in stages.values() for l in x["log"]})[-10:]
    if logs:
        lines += ["", "Session log (last 10):", "| Date | Tool | DCs done | Stopped because |", "|---|---|---|---|", *logs]
    block = "\n".join(lines)
    if START not in flow_md or END not in flow_md:
        raise ValueError("FLOW.md has no status markers")
    head, rest = flow_md.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{block}\n{END}{tail}", errors


def write_atomic(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".flow-", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main(argv: list[str]) -> int:
    if len(argv) != 1 or not (Path(argv[0]) / "FLOW.md").is_file():
        print(__doc__)
        return 2
    plan = Path(argv[0])
    for attempt in range(2):
        before = (plan / "FLOW.md").stat().st_mtime_ns
        try:
            new, errors = build(plan)
        except ValueError as exc:
            print(f"error: {exc}")
            return 2
        if errors:
            break  # never write on a Flows-table / folder mismatch
        if (plan / "FLOW.md").stat().st_mtime_ns == before or attempt == 1:
            if new != (plan / "FLOW.md").read_text(encoding="utf-8"):
                write_atomic(plan / "FLOW.md", new)
            break
    for e in errors:
        print(f"error: {e}")
    print("FLOW.md not changed: fix the errors above" if errors else "FLOW.md status up to date")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
