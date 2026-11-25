"""Score one benchmark run's output (0..1) and list failed checks.

Usage: python check_outputs.py <run dir> <task id> <version> [--reply <file with final reply text>]
Prints JSON: {"score": float, "passed": int, "total": int, "failed": [..]}
The run dir is a git repo whose first commit is the untouched fixture.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

FIXTURE_PLANS = {"add-order-total", "orders-v2"}
AGENT_HEADINGS = ["Context", "Preconditions", "Rules", "Steps", "DC checklist", "Stop conditions",
                  "Contacts", "Done Criteria", "Question Map"]
HUMAN_HEADINGS = ["Scope", "Impact", "Rules", "Contacts", "Risks"]
BANNED = re.compile(r"as discussed|see other stage|same as before", re.I)
STAGE_DIR = re.compile(r"^F\d+-S\d+-[a-z0-9]+(?:-[a-z0-9]+)*$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Checks:
    def __init__(self) -> None:
        self.results: list[tuple[str, bool]] = []

    def add(self, name: str, ok: bool) -> bool:
        self.results.append((name, bool(ok)))
        return bool(ok)

    def report(self) -> dict:
        passed = sum(ok for _, ok in self.results)
        total = len(self.results) or 1
        return {"score": round(passed / total, 3), "passed": passed, "total": len(self.results),
                "failed": [n for n, ok in self.results if not ok]}


def git(run: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=run, capture_output=True, text=True, check=False).stdout


def changed_paths(run: Path) -> list[str]:
    base = git(run, "rev-list", "--max-parents=0", "HEAD").split()[0]
    out = git(run, "diff", "--name-only", base) + git(run, "ls-files", "--others", "--exclude-standard")
    return sorted({p for p in out.splitlines() if p and not p.startswith((".claude/", ".github/skills/"))
                   and p != ".agent-context.json" and "__pycache__" not in p})


def headings(text: str) -> set[str]:
    return {m.group(1).strip() for m in re.finditer(r"^#{2,3}\s+(.+?)\s*$", text, re.M)}


def has_heading(text: str, name: str) -> bool:
    return any(h.lower().startswith(name.lower()) for h in headings(text))


def map_rows(text: str) -> list[list[str]]:
    m = re.search(r"^##\s+Question Map\s*$", text, re.M)
    if not m:
        return []
    rows = []
    for line in text[m.end():].splitlines():
        s = line.strip()
        if s.startswith("## "):
            break
        if s.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", s):
            rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows[1:]


def check_agent_plan(c: Checks, text: str, label: str, max_dcs: int | None = None) -> None:
    for h in AGENT_HEADINGS:
        c.add(f"{label}: heading {h}", has_heading(text, h))
    steps = re.findall(r"^\s*\d+\.\s.*?(?=^\s*\d+\.\s|^##|\Z)", text.split("## Steps", 1)[-1], re.M | re.S)
    c.add(f"{label}: has numbered steps", bool(steps))
    c.add(f"{label}: every step has [DC- and Verify:", bool(steps) and all("DC-" in s and "Verify" in s for s in steps))
    rows = map_rows(text)
    c.add(f"{label}: Question Map rows have answer + source",
          all(len(r) >= 6 and r[4] not in {"", "-", "..."} and r[5] in {"User", "Assumption", "Skipped"} for r in rows))
    c.add(f"{label}: no 'as discussed' style references", not BANNED.search(text))
    if max_dcs is not None:
        dcs = set(re.findall(r"\|\s*((?:F\d+-S\d+/)?DC-\d+)\s*\|", text.split("## Done Criteria", 1)[-1]))
        c.add(f"{label}: <= {max_dcs} DCs", 0 < len(dcs) <= max_dcs)
        ctx = re.search(r"^##\s+Context\s*$(.*?)^##\s", text, re.M | re.S)
        c.add(f"{label}: non-empty Context", bool(ctx and ctx.group(1).strip()))


def check_human_plan(c: Checks, text: str, version: str, label: str) -> None:
    c.add(f"{label}: has Goal", "Goal" in text)
    for h in HUMAN_HEADINGS:
        c.add(f"{label}: heading {h}", has_heading(text, h))
    if version == "v1":
        c.add(f"{label}: contains Question Map (v1 contract)", has_heading(text, "Question Map"))
    else:
        c.add(f"{label}: <= 60 lines (v2 contract)", len(text.splitlines()) <= 60)
        c.add(f"{label}: links to PLAN.agent.md (v2 contract)", "PLAN.agent.md" in text)


def new_plan_dirs(run: Path) -> list[Path]:
    root = run / "BuildPlans"
    if not root.is_dir():
        return []
    found = []
    for p in root.rglob("*"):
        if p.is_dir() and (p / "PLAN.agent.md").exists() and not any(x in FIXTURE_PLANS for x in p.relative_to(root).parts):
            if not STAGE_DIR.match(p.name):
                found.append(p)
    flows = [p.parent for p in root.rglob("FLOW.md") if not any(x in FIXTURE_PLANS for x in p.relative_to(root).parts)]
    return found + [f for f in flows if f not in found]


def tests_pass(run: Path) -> bool:
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                       cwd=run, capture_output=True, text=True, check=False, timeout=120)
    return r.returncode == 0


def flow_status(run: Path, plan: Path) -> tuple[int, str]:
    script = run / ".claude/skills/running-when-a-request-is-made/scripts/flow_status.py"
    if not script.exists():
        script = run / ".github/skills/running-when-a-request-is-made/scripts/flow_status.py"
    r = subprocess.run([sys.executable, str(script), str(plan)], cwd=run, capture_output=True, text=True, check=False)
    return r.returncode, r.stdout


def status_block(text: str) -> str:
    m = re.search(r"<!-- flow-status:start -->(.*?)<!-- flow-status:end -->", text, re.S)
    return m.group(1).strip() if m else ""


def progress_status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    m = re.search(r"Status:\s*([A-Z][A-Z ]*?)\s*(?:·|$)", path.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip() if m else "UNKNOWN"


def check(run: Path, task: str, version: str, reply: str) -> dict:
    c = Checks()
    changed = changed_paths(run)
    if task in {"T1-plan-clear", "T2-plan-vague", "T3-plan-docs"}:
        plans = new_plan_dirs(run)
        c.add("exactly one new plan folder", len(plans) == 1)
        c.add("no changes outside BuildPlans/", all(p.startswith("BuildPlans/") for p in changed))
        if plans:
            p = plans[0]
            c.add("plan folder is kebab-case", bool(KEBAB.match(p.name)))
            agent, human = p / "PLAN.agent.md", p / "PLAN.human.md"
            c.add("both plan files exist", agent.exists() and human.exists())
            if agent.exists():
                at = agent.read_text(encoding="utf-8")
                check_agent_plan(c, at, "agent")
                if task == "T2-plan-vague":
                    c.add("T2: >= 3 Question Map rows", len(map_rows(at)) >= 3)
            if human.exists():
                check_human_plan(c, human.read_text(encoding="utf-8"), version, "human")
    elif task == "T4-execute":
        c.add("tests pass", tests_pass(run))
        src = (run / "src/orders.py").read_text(encoding="utf-8")
        c.add("order_total exists", "def order_total" in src)
        summ = run / "BuildPlans/add-order-total/EXECUTION-SUMMARY.md"
        c.add("EXECUTION-SUMMARY.md exists", summ.exists())
        c.add("summary has DC table with MET", summ.exists() and re.search(r"\|\s*DC-\d+\s*\|.*\bMET\b", summ.read_text(encoding="utf-8")) is not None)
    elif task == "T5-other":
        c.add("no files changed", not changed)
        c.add("reply non-empty and mentions order", bool(reply.strip()) and "order" in reply.lower())
    elif task == "T6-plan-large":
        plans = [p for p in new_plan_dirs(run) if (p / "FLOW.md").exists()]
        c.add("a new FLOW.md plan exists", len(plans) == 1)
        c.add("no changes outside BuildPlans/", all(p.startswith("BuildPlans/") for p in changed))
        if plans:
            p = plans[0]
            flow = (p / "FLOW.md").read_text(encoding="utf-8")
            c.add("FLOW.md has Flows table", has_heading(flow, "Flows"))
            c.add("FLOW.md has status markers", "<!-- flow-status:start -->" in flow and "<!-- flow-status:end -->" in flow)
            c.add("FLOW.md has a parallel flow", re.search(r"\|\s*parallel\s*\|", flow, re.I) is not None)
            c.add("FLOW.md has an optional flow", re.search(r"\|\s*optional\s*\|", flow, re.I) is not None)
            stages = sorted(d for d in p.iterdir() if d.is_dir() and STAGE_DIR.match(d.name))
            c.add(">= 8 stage folders", len(stages) >= 8)
            c.add("every stage has both plan files", bool(stages) and all((d / "PLAN.agent.md").exists() and (d / "PLAN.human.md").exists() for d in stages))
            for d in stages:
                if (d / "PLAN.agent.md").exists():
                    check_agent_plan(c, (d / "PLAN.agent.md").read_text(encoding="utf-8"), d.name[:6], max_dcs=4)
            master = re.findall(r"^\|\s*(DC-\d+)\s*\|([^|]*)\|([^|]*)\|", flow.split("## Done Criteria", 1)[-1], re.M)
            c.add("every master DC maps to a stage", bool(master) and all(re.search(r"F\d+-S\d+", r[2]) for r in master))
            code, _ = flow_status(run, p)
            c.add("flow_status.py exits 0", code == 0)
            after = status_block((p / "FLOW.md").read_text(encoding="utf-8"))
            rows = [l for l in after.splitlines() if re.match(r"^\|\s*F\d+\s*\|", l)]
            c.add("every flow has a Next stage", bool(rows) and all(l.rstrip("| ").split("|")[-1].strip() not in {"", "-"} for l in rows))
    elif task in {"T7-resume", "T8-low-context"}:
        plan = run / "BuildPlans/orders-v2"
        s = {d.name[:6]: progress_status(d / "PROGRESS.md") for d in plan.iterdir() if d.is_dir()}
        # compare with the untouched base commit, not HEAD (the agent may commit), via git so that
        # line-ending conversion (core.autocrlf on Windows) doesn't count as a change
        root = git(run, "rev-list", "--max-parents=0", "HEAD").split()[0]
        s01 = "BuildPlans/orders-v2/F1-S01-add-status-enum/PROGRESS.md"
        s01_diff = subprocess.run(["git", "diff", "--ignore-cr-at-eol", "--ignore-space-at-eol", "--quiet", root, "--", s01],
                                  cwd=run, check=False).returncode
        c.add("F1-S01 not re-run", s01_diff == 0)
        flow_text = (plan / "FLOW.md").read_text(encoding="utf-8")
        block_before = status_block(flow_text)
        code, _ = flow_status(run, plan)
        block_fresh = status_block((plan / "FLOW.md").read_text(encoding="utf-8"))
        c.add("FLOW.md status block was regenerated by the script", bool(block_before) and block_before == block_fresh)
        c.add("flow_status.py exits 0", code == 0)
        if task == "T7-resume":
            c.add("F1-S02 is MET", s.get("F1-S02") == "MET")
            c.add("tests pass", tests_pass(run))
            nxt = "F1-S03" if s.get("F1-S03") != "MET" else "done"
            c.add("FLOW.md shows correct F1 Next stage", re.search(rf"\|\s*F1\s*\|.*\|\s*{nxt}", block_fresh) is not None)
        else:
            c.add("no stage moved to MET", all(v != "MET" for k, v in s.items() if k != "F1-S01"))
            started = [k for k, v in s.items() if v == "PAUSED"]
            ok_pause = True
            for k in started:
                t = next(d for d in plan.iterdir() if d.name.startswith(k)) / "PROGRESS.md"
                txt = t.read_text(encoding="utf-8")
                ok_pause &= bool(re.search(r"Resume note:\s*(?!-\s*$)\S", txt, re.M)) and bool(re.search(r"Next step:\s*\S", txt))
            c.add("paused stage has Next step + Resume note", ok_pause)
            c.add("reply mentions the low-context stop", bool(re.search(r"(context|5\s?%)", reply, re.I)))
    else:
        raise SystemExit(f"unknown task {task}")
    return c.report()


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    reply = ""
    if "--reply" in argv:
        reply = Path(argv[argv.index("--reply") + 1]).read_text(encoding="utf-8", errors="replace")
    print(json.dumps(check(Path(argv[0]), argv[1], argv[2], reply)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
