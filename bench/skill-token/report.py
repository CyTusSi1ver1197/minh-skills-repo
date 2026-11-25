"""Build RESULTS.md from results/results.jsonl (+ STATIC.md, results/meta.json).

Usage: python report.py [--results results/results.jsonl] [--out RESULTS.md] [--baseline v1] [--candidate v2.1]

Pass bar (config.json pass_bar, revised 2026-11-24, Claude Code only):
  for every token task (T1-T5): candidate median turns <= baseline median turns,
  candidate median cost_usd <= baseline median cost_usd, candidate median quality >= baseline.
  Feature tasks (T6-T8, v2.x only): all checks pass in >= feature_min_passes runs.
Total tokens (cache reads counted at full weight) are reported for information only.
cost_usd is Claude Code's client-side API-price estimate, not a subscription charge: use it to
compare versions; check /usage before/after each batch for your plan's real consumption.
Rows with missing values (timeouts, failed runs) are listed and left out of the medians.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent


def med(rows: list[dict], key: str):
    vals = [r[key] for r in rows if isinstance(r.get(key), (int, float)) and not isinstance(r.get(key), bool)]
    return median(vals) if vals else None


def f_int(v) -> str:
    return f"{int(round(v)):,}" if v is not None else "-"


def f_num(v, nd=1) -> str:
    return f"{v:.{nd}f}" if v is not None else "-"


def pct(new, old) -> str:
    return f"{(new - old) / old * 100:+.1f} %" if new is not None and old else "-"


def spread(rows: list[dict], key: str):
    vals = [r[key] for r in rows if isinstance(r.get(key), (int, float)) and not isinstance(r.get(key), bool)]
    return (min(vals), max(vals)) if vals else (None, None)


def signal(rb: list[dict], rc: list[dict]) -> str:
    """Is one more candidate run worth it? Compare the candidate median with the baseline's own range."""
    if len(rb) < 3:
        return f"baseline has {len(rb)} run(s): need 3 to judge"
    verdicts = []
    for key in ("turns", "cost_usd"):
        lo, hi = spread(rb, key)
        c = med(rc, key)
        if lo is None or c is None:
            continue
        verdicts.append("win" if c < lo else "loss" if c > hi else "close")
    if not verdicts:
        return "-"
    if all(v == "win" for v in verdicts):
        return "clear win: done"
    if any(v == "loss" for v in verdicts):
        return "clear loss: stop, fix"
    return "close: add 1 run" if len(rc) < 3 else "close: within noise"


def valid(r: dict) -> bool:
    if r.get("exit_code") not in (0, None) or not r.get("total_tokens"):
        return False
    return r.get("tool") != "claude" or isinstance(r.get("turns"), (int, float))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(HERE / "results" / "results.jsonl"))
    ap.add_argument("--out", default=str(HERE / "RESULTS.md"))
    ap.add_argument("--baseline", default="v1")
    ap.add_argument("--candidate", default=None, help="default: every non-baseline version found")
    ap.add_argument("--model", default=None, help="only rows run with this model id")
    a = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    bar = cfg["pass_bar"]
    rows = [json.loads(l) for l in Path(a.results).read_text(encoding="utf-8").splitlines() if l.strip()]
    if a.model:
        rows = [r for r in rows if r.get("model") == a.model]
    bad = [r for r in rows if not valid(r)]
    good = [r for r in rows if valid(r)]
    by = defaultdict(list)
    for r in good:
        by[(r["tool"], r["task"], r["version"])].append(r)
    tools = sorted({r["tool"] for r in good})
    versions = sorted({r["version"] for r in good})
    cands = [a.candidate] if a.candidate else [v for v in versions if v != a.baseline]
    token_tasks = sorted({r["task"] for r in good if not r.get("feature")})
    feature_tasks = sorted({r["task"] for r in good if r.get("feature")})

    out = ["# Benchmark results: running-when-a-request-is-made", "",
           f"Runs: {len(rows)} recorded, {len(good)} used, {len(bad)} left out (timeout / missing values).",
           "Pass bar: on every task, candidate median **turns** and **cost** ≤ baseline, and quality not lower.",
           "Cost = Claude Code's API-price estimate (`total_cost_usd`), not a subscription charge. "
           "Total tokens count cache reads at full weight: information only.", ""]
    meta = HERE / "results" / "meta.json"
    if meta.exists():
        for tool, m in json.loads(meta.read_text(encoding="utf-8")).items():
            out.append(f"- {tool}: model `{m['model']}`, CLI `{m['cli_version']}`")
        out.append("")
    verdicts = {}
    for tool in tools:
        for cand in cands:
            out += [f"## {tool}: {a.baseline} vs {cand}", "",
                    "| Task | Turns (base → cand) | Cost $ (base → cand) | Cost change | Total tokens (base → cand) | "
                    "Output tokens (base → cand) | Quality (base → cand) | Task OK | Next |",
                    "|---|---|---|---|---|---|---|---|---|"]
            all_ok, sum_b, sum_c, complete = True, 0.0, 0.0, True
            for task in token_tasks:
                rb, rc = by.get((tool, task, a.baseline), []), by.get((tool, task, cand), [])
                if not rb or not rc:
                    complete = False
                    out.append(f"| {task} | {len(rb)} / {len(rc)} runs | | incomplete | | | | ✗ | run it |")
                    continue
                tb, tc = med(rb, "turns"), med(rc, "turns")
                cb, cc = med(rb, "cost_usd"), med(rc, "cost_usd")
                qb, qc = med(rb, "quality"), med(rc, "quality")
                ok = (tb is None or tc is None or tc <= tb) and (cb is None or cc is None or cc <= cb) \
                    and (qb is None or qc is None or qc >= qb)
                if tool == "copilot":
                    # ponytail: total_tokens is the only Copilot metric; switch to turns once parse_copilot records them
                    ok &= med(rc, "total_tokens") <= med(rb, "total_tokens") * 1.10
                all_ok &= ok
                sum_b += cb or 0
                sum_c += cc or 0
                out.append(f"| {task} | {f_num(tb)} → {f_num(tc)} | {f_num(cb, 3)} → {f_num(cc, 3)} | {pct(cc, cb)} | "
                           f"{f_int(med(rb, 'total_tokens'))} → {f_int(med(rc, 'total_tokens'))} | "
                           f"{f_int(med(rb, 'output_tokens'))} → {f_int(med(rc, 'output_tokens'))} | "
                           f"{f_num(qb, 2)} → {f_num(qc, 2)} | {'✓' if ok else '✗'} | {signal(rb, rc)} |")
            out += ["", f"Total median cost: {f_num(sum_b, 3)} → {f_num(sum_c, 3)} ({pct(sum_c, sum_b)})", ""]
            feat_ok = True
            feats = [t for t in feature_tasks if by.get((tool, t, cand))]
            if feats:
                out += ["Feature checks:", "", "| Task | Runs | All checks passed | Median turns | Median cost $ | Common failed checks |",
                        "|---|---|---|---|---|---|"]
                for task in feats:
                    rs = by[(tool, task, cand)]
                    full = sum(1 for r in rs if r.get("quality", 0) >= 1.0)
                    fails = defaultdict(int)
                    for r in rs:
                        for f in r.get("failed_checks", []):
                            fails[f] += 1
                    common = "; ".join(f"{k} ({v})" for k, v in sorted(fails.items(), key=lambda x: -x[1])[:3]) or "-"
                    ok = full >= bar["feature_min_passes"]
                    feat_ok &= ok
                    out.append(f"| {task} | {len(rs)} | {full} {'✓' if ok else '✗'} | {f_num(med(rs, 'turns'))} | "
                               f"{f_num(med(rs, 'cost_usd'), 3)} | {common} |")
                out.append("")
            verdicts[(tool, cand)] = complete and all_ok and feat_ok
            out += [f"**{tool} {cand}: {'PASS' if verdicts[(tool, cand)] else 'FAIL'}**", ""]
    if bad:
        out += ["## Left out", "", "| Tool | Version | Task | Repeat | Exit | Why |", "|---|---|---|---|---|---|"]
        for r in bad:
            why = "missing turns" if not isinstance(r.get("turns"), (int, float)) else "error exit"
            out.append(f"| {r.get('tool')} | {r.get('version')} | {r.get('task')} | {r.get('repeat')} | {r.get('exit_code')} | {why} |")
        out.append("")
    out += ["## Verdict", ""] + [f"- {t} {c}: {'PASS' if v else 'FAIL'}" for (t, c), v in verdicts.items()]
    static = HERE / "STATIC.md"
    if static.exists():
        out += ["", "## Static load per request class", "", static.read_text(encoding="utf-8").strip()]
    Path(a.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(l for l in out if l.startswith(("**", "- ", "Total median"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
