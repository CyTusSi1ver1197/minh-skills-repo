"""Run the same task set against skill versions v1 and v2 on Claude Code and Copilot CLI.

Usage:
  python run_bench.py --tool claude|copilot|both [--versions v1,v2.1 | v1,v2.0,v2.1] [--repeats 3] [--tasks T1-plan-clear,...]
  python run_bench.py --probe copilot          # one raw T5/v1 run, saved to probe-copilot.jsonl
  python run_bench.py --prepare <task> <version> <tool> <dir>   # set up a run dir only (no CLI call)

Each run: copy fixture/ to a fresh temp dir, git init + commit, install the version's two skills
into the tool's project skill folder, run the CLI headless, parse token usage, score the output
with check_outputs.py, append one JSON line to results/results.jsonl. Versions are interleaved.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = ["running-when-a-request-is-made", "information-gathering-for-plan"]
TOKEN_KEYS = {
    "input_tokens": ["input_tokens", "inputTokens", "prompt_tokens", "promptTokens"],
    "output_tokens": ["output_tokens", "outputTokens", "completion_tokens", "completionTokens"],
    "cache_creation_input_tokens": ["cache_creation_input_tokens", "cacheCreationInputTokens", "cacheWriteTokens",
                                    "cache_write_tokens"],
    "cache_read_input_tokens": ["cache_read_input_tokens", "cacheReadInputTokens", "cacheReadTokens",
                                "cache_read_tokens", "cached_tokens", "cachedTokens"],
}


def load(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def version_dir(version: str) -> Path:
    """v1 and v2.0 are snapshots in versions/; any other name (v2.1, live) = the live skills in SKILLS_ROOT."""
    snap = HERE / "versions" / version
    if snap.is_dir():
        return snap
    return HERE.parent.parent


def prepare(task: dict, version: str, tool: str, cfg: dict, target: Path | None = None) -> Path:
    run = Path(target) if target else Path(tempfile.mkdtemp(prefix=f"bench-{tool}-{version}-{task['id']}-"))
    if run.exists() and any(run.iterdir()):
        shutil.rmtree(run)
    shutil.copytree(HERE / "fixture", run, dirs_exist_ok=True)
    for t in ("claude", "copilot"):  # install for the tool under test only
        if t != tool:
            continue
        dest = run / cfg["skill_dirs"][t]
        dest.mkdir(parents=True, exist_ok=True)
        for s in SKILLS:
            shutil.copytree(version_dir(version) / s, dest / s, dirs_exist_ok=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "bench", "GIT_AUTHOR_EMAIL": "bench@local",
           "GIT_COMMITTER_NAME": "bench", "GIT_COMMITTER_EMAIL": "bench@local"}
    subprocess.run(["git", "init", "-q"], cwd=run, check=True, env=env)
    subprocess.run(["git", "add", "-A"], cwd=run, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=run, check=True, env=env)
    setup = task.get("setup", {})
    if "agent_context" in setup:  # T8: planted low-context reading, read-only
        p = run / ".agent-context.json"
        p.write_text(json.dumps(setup["agent_context"]), encoding="utf-8")
        os.chmod(p, 0o444)
    return run


def find_usage(obj, acc: dict) -> None:
    """Sum every usage-like dict found anywhere in a JSON event."""
    if isinstance(obj, dict):
        hit = False
        for field, names in TOKEN_KEYS.items():
            for n in names:
                v = obj.get(n)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    acc[field] += int(v)
                    hit = True
                    break
        if hit:
            return
        for v in obj.values():
            find_usage(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            find_usage(v, acc)


def parse_claude(stdout: str) -> dict:
    data = json.loads(stdout.strip().splitlines()[-1])
    u = data.get("usage", {})
    return {"input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0),
            "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0),
            "cache_read_input_tokens": u.get("cache_read_input_tokens", 0),
            "cost_usd": data.get("total_cost_usd"), "turns": data.get("num_turns"),
            "duration_ms": data.get("duration_ms"), "reply": data.get("result", ""), "usage_source": "claude-json"}


def parse_copilot(stdout: str) -> dict:
    acc = dict.fromkeys(TOKEN_KEYS, 0)
    reply_parts, events = [], 0
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        events += 1
        # usage events only: avoid double counting cumulative session summaries
        etype = str(ev.get("type", ""))
        if "usage" in etype.lower() or "usage" in ev:
            find_usage(ev, acc)
        for key in ("content", "text", "message"):
            val = ev.get("data", {}).get(key) if isinstance(ev.get("data"), dict) else ev.get(key)
            if isinstance(val, str) and "assistant" in etype.lower():
                reply_parts.append(val)
    return {**acc, "cost_usd": None, "turns": None, "duration_ms": None, "reply": "\n".join(reply_parts),
            "usage_source": "copilot-jsonl" if sum(acc.values()) else "none", "events": events}


def copilot_log_fallback(since: float) -> dict | None:
    """Sum usage from Copilot CLI session files written after `since` (fallback when JSONL lacks counts)."""
    home = Path(os.environ.get("COPILOT_HOME", Path.home())) / ".copilot"
    acc = dict.fromkeys(TOKEN_KEYS, 0)
    found = False
    for p in home.rglob("*"):
        if p.is_file() and p.suffix in {".jsonl", ".json"} and p.stat().st_mtime >= since:
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                before = sum(acc.values())
                if "usage" in json.dumps(ev)[:2000].lower():
                    find_usage(ev, acc)
                found |= sum(acc.values()) > before
    return {**acc, "usage_source": "copilot-session-log"} if found else None


def run_cli(tool: str, task: dict, cfg: dict, run: Path) -> tuple[dict, str]:
    cmd = [c.format(prompt=task["prompt"], model=cfg["models"][tool]) for c in cfg[f"{tool}_cmd"]]
    start = time.time()
    p = subprocess.run(cmd, cwd=run, capture_output=True, text=True, timeout=cfg["timeout_s"], check=False,
                       encoding="utf-8", errors="replace")
    raw = p.stdout + ("\n#STDERR\n" + p.stderr if p.stderr else "")
    if tool == "claude":
        parsed = parse_claude(p.stdout)
    else:
        parsed = parse_copilot(p.stdout)
        if parsed["usage_source"] == "none":
            fb = copilot_log_fallback(start - 1)
            if fb:
                parsed.update(fb)
        parsed["duration_ms"] = int((time.time() - start) * 1000)
    parsed["exit_code"] = p.returncode
    return parsed, raw


def score(run: Path, task: dict, version: str, reply: str) -> dict:
    rf = run.parent / f"{run.name}.reply.txt"
    rf.write_text(reply or "", encoding="utf-8")
    out = subprocess.run([sys.executable, str(HERE / "check_outputs.py"), str(run), task["id"], version,
                          "--reply", str(rf)], capture_output=True, text=True, check=False)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return {"score": 0.0, "failed": [f"checker error: {out.stderr[-300:]}"]}


def existing_counts(cfg: dict) -> dict:
    """Valid rows already in results.jsonl per (tool, version, task, model)."""
    path = HERE / "results" / "results.jsonl"
    counts: dict = {}
    if not path.exists():
        return counts
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        ok = r.get("exit_code") in (0, None) and r.get("total_tokens") and \
            (r.get("tool") != "claude" or isinstance(r.get("turns"), (int, float)))
        if ok:
            k = (r["tool"], r["version"], r["task"], r.get("model"))
            counts[k] = counts.get(k, 0) + 1
    return counts


def cli_version(tool: str) -> str:
    try:
        return subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except OSError:
        return "not found"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", choices=["claude", "copilot", "both"])
    ap.add_argument("--versions", default="v1,v2.1")
    ap.add_argument("--repeats", type=int, help="target number of valid runs per tool/version/task/model; "
                    "existing rows in results.jsonl count toward it (default: config.json repeats)")
    ap.add_argument("--fresh", action="store_true", help="ignore existing rows when counting repeats")
    ap.add_argument("--budget-usd", type=float, default=None,
                    help="stop this invocation once the summed cost_usd estimate reaches this amount")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--probe", choices=["copilot", "claude"])
    ap.add_argument("--prepare", nargs=4, metavar=("TASK", "VERSION", "TOOL", "DIR"))
    ap.add_argument("--keep", action="store_true", help="keep run dirs")
    a = ap.parse_args()
    cfg, tasks = load("config.json"), {t["id"]: t for t in load("tasks.json")}

    if a.prepare:
        tid, ver, tool, d = a.prepare
        print(prepare(tasks[tid], ver, tool, cfg, Path(d)))
        return 0
    if a.probe:
        run = prepare(tasks["T5-other"], "v1", a.probe, cfg)
        _, raw = run_cli(a.probe, tasks["T5-other"], cfg, run)
        out = HERE / f"probe-{a.probe}.jsonl"
        out.write_text(raw, encoding="utf-8")
        print(f"raw output saved to {out}; check it for token-usage events")
        return 0
    if not a.tool:
        ap.error("--tool is required")

    tools = ["claude", "copilot"] if a.tool == "both" else [a.tool]
    versions = a.versions.split(",")
    repeats = a.repeats or cfg["repeats"]
    chosen = [tasks[t] for t in a.tasks.split(",") if t] or list(tasks.values())
    (HERE / "results" / "raw").mkdir(parents=True, exist_ok=True)
    meta = {t: {"cli_version": cli_version(t), "model": cfg["models"][t]} for t in tools}
    (HERE / "results" / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    have = {} if a.fresh else existing_counts(cfg)
    spent, done_runs, skipped = 0.0, 0, []
    for tool in tools:
        for task in chosen:
            for n in range(1, repeats + 1):
                for version in versions:  # interleaved v1, v2, v1, v2 ...
                    allowed = task.get("versions", ["v1", "v2"])
                    if version not in allowed and not (version.startswith("v2") and "v2" in allowed):
                        continue
                    key = (tool, version, task["id"], cfg["models"][tool])
                    if have.get(key, 0) >= repeats:
                        if n == 1:
                            skipped.append(f"{version} {task['id']} ({have[key]} existing)")
                        continue
                    if a.budget_usd is not None and spent >= a.budget_usd:
                        print(f"STOP: budget reached (est. ${spent:.2f} of ${a.budget_usd:.2f}) after {done_runs} runs. "
                              "Re-run the same command later: finished runs are kept and skipped.")
                        return 4
                    have[key] = have.get(key, 0) + 1
                    n_label = have[key]
                    run = prepare(task, version, tool, cfg)
                    try:
                        parsed, raw = run_cli(tool, task, cfg, run)
                    except subprocess.TimeoutExpired:
                        parsed, raw = {"exit_code": "timeout", "reply": "", "usage_source": "none",
                                       **dict.fromkeys(TOKEN_KEYS, 0)}, "TIMEOUT"
                    q = score(run, task, version, parsed.get("reply", ""))
                    total = sum(int(parsed.get(k) or 0) for k in TOKEN_KEYS)
                    row = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "tool": tool,
                           "version": version, "task": task["id"], "feature": bool(task.get("feature")),
                           "repeat": n_label, "model": cfg["models"][tool],
                           **{k: int(parsed.get(k) or 0) for k in TOKEN_KEYS}, "total_tokens": total,
                           "cost_usd": parsed.get("cost_usd"), "turns": parsed.get("turns"),
                           "duration_ms": parsed.get("duration_ms"), "exit_code": parsed.get("exit_code"),
                           "usage_source": parsed.get("usage_source"), "quality": q.get("score", 0.0),
                           "failed_checks": q.get("failed", [])}
                    with (HERE / "results" / "results.jsonl").open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps(row) + "\n")
                    (HERE / "results" / "raw" / f"{tool}-{version}-{task['id']}-{n_label}.json").write_text(raw, encoding="utf-8")
                    spent += float(parsed.get("cost_usd") or 0)
                    done_runs += 1
                    print(f"{tool} {version} {task['id']} #{n_label}: {total:,} tokens, {parsed.get('turns')} turns, "
                          f"est. ${float(parsed.get('cost_usd') or 0):.3f}, quality {row['quality']}  (batch est. ${spent:.2f})")
                    if tool == "copilot" and total == 0:
                        print("STOP: Copilot run produced no token counts (JSONL or session logs). "
                              "Run --probe copilot and check the raw output.")
                        return 3
                    if not a.keep:
                        shutil.rmtree(run, ignore_errors=True)
    if skipped:
        print("Reused existing results for: " + "; ".join(skipped))
    print(f"Done: {done_runs} new runs, batch estimate ${spent:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
