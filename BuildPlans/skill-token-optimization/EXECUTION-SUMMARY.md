# Execution summary: skill-token-optimization

Executed 2026-11-24 in a cloud workspace (no Claude Code / Copilot CLI logins, skills repo not connected). Built from the synced copy of both skills; the result is delivered as a zip to unpack into `SKILLS_ROOT`. Live parts are left for the user's PC (see "Next run").

## Files changed

**running-when-a-request-is-made/**
- `SKILL.md` (modify): 12,314 → 3,075 chars. Goal, vocabulary (+ Stage, Flow), Step 0 router to the references, the verbatim class C question, the loading rule, and context-budget rules 1-7 (rule 7 = integrity before size).
- `references/planning.md` (create): Steps 1-3, plus the size check (> 7 stages → staged plan), the slim PLAN.human contract and the compression rule.
- `references/execution.md` (create): Step 4, plus PROGRESS.md checkpoints, resume after compaction, ≤ 10-line verifier evidence, filtered test output, and a short reply + summary file.
- `references/staged-plans.md` (create): split rules, folder layout, flows (main / parallel / optional), FLOW.md content, self-contained stages, flow execution, the low-context stop, resume, setup.
- `assets/PLAN.agent.template.md`, `assets/PLAN.human.template.md`, `assets/PROGRESS.template.md`, `assets/EXECUTION-SUMMARY.template.md`, `assets/FLOW.template.md` (create): the output templates.
- `scripts/contacts.py` (create): CODEOWNERS / top committers and the owner-review flags.
- `scripts/flow_status.py` (create): rebuilds only the FLOW.md Status block. It is idempotent, makes no write when nothing changed, makes no write and exits 1 on a table/folder mismatch, and writes atomically.
- `scripts/statusline_context.py` (create): a status-line command for Claude Code + Copilot CLI that writes `.agent-context.json`.
- `scripts/context_check.py` (create): prints `remaining=<n>` or `remaining=unknown`.

**information-gathering-for-plan/**
- `SKILL.md` (modify): 8,440 → 2,090 chars. Purpose, modes, vocabulary, the Step 1 "is this needed?" check, and a pointer to the reference.
- `references/gather-and-rank.md` (create): Steps 2-6 with tiers, caps, conflict rules and section D.
- `assets/report.template.md` (create): the v1 report template.

**bench/skill-token/** (all created)
- `versions/v1/**`: untouched v1 snapshot.
- `fixture/**`: Python stdlib repo with tests, rules, CODEOWNERS, the T4 plan and the staged `orders-v2` example.
- `tasks.json` (8 tasks), `config.json`.
- `static_measure.py`, `validate_skill.py`, `run_bench.py`, `check_outputs.py`, `report.py`.
- `STATIC.md`, `RULE-COVERAGE.md`, `README.md`, `SMOKE.md`, `PARKED.md`, `.gitignore`.

**BuildPlans/skill-token-optimization/**
- `PROGRESS.md`, `EXECUTION-SUMMARY.md` (create).

## DC status
| DC | Status | Evidence |
|---|---|---|
| DC-1 | MET | `git diff --no-index` of v1 vs snapshot is empty. Static v1 = 12,314 chars (12,378 bytes, within ±2 %), A+IG = 20,748. |
| DC-2 | NOT MET (static sub-targets) → revision proposed | All files built and the validator passes. All 61 v1 rule lines are mapped, with 0 missing (RULE-COVERAGE.md). An independent verifier checked the rules and said MET after 2 restored items. Static load: class A 75.5 % (target 70 %), class B 51.7 % (50 %), class C 25.0 % (25 %, met). The rest is required rule text (rule 7). |
| DC-3 | NOT MET (static sub-target) → revision proposed | Split done; core 2,090 ≤ 2,500. The verifier said MET on content. Static A+IG load is 81.5 % of v1 (target 65 %), because once gathering is needed, Steps 2-6 are needed in full. |
| DC-4 | IN PROGRESS | `validate_skill.py` PASS for both skills. The 3 manual smoke tests (Claude Code, Copilot CLI, VS Code) are pending in SMOKE.md. |
| DC-5 | IN PROGRESS | Fixture tests pass, `tasks.json` has 8 tasks. The runner, checker and report work end to end with fake CLIs: each recorded total_tokens > 0, and the checker caught negative cases. The real single-run verify needs your CLIs. |
| DC-6 | TODO | Needs the 78 live runs. |
| DC-7 | IN PROGRESS | Reference and template built; the verifier said MET on content. T6 live check pending. |
| DC-8 | IN PROGRESS | Scripts tested offline: Claude Code / Copilot / empty / stale payloads, idempotency, mismatch exit 1, PAUSED rendering. The verifier said MET. T7/T8 live checks and a real context reading are pending. |

## Rule & test results
- `validate_skill.py`: PASS (both skills).
- Fixture: `python -m unittest discover -s tests -t .` OK.
- Checker self-tests: simulated good runs score 1.0 (T1 v2, T4, T5, T7, T8). The negative cases each fail the right check: hand-edited FLOW status, a changed file in T5, the missing v1 Map under the v1 contract.
- Independent verifier (separate agent): DC-2, DC-3, DC-7, DC-8 MET on content. It found 5 issues and all 5 are fixed:
  - contacts.py dot-folder CODEOWNERS matching;
  - Step 2 "something else" routing restored;
  - "trade-offs" restored;
  - flow_status no-op and mismatch writes;
  - coverage row 34.

## Assumptions & deviations
- **Workspace:** built in a cloud copy, not in your repo. The baseline is the synced copy of your skills (sizes matched the plan within 2 %).
- **Budgets raised under rule 7:**
  - `planning.md` is 5,045 chars (plan: 4,400). The rest is verbatim-required text plus the 2 restored rules.
  - `gather-and-rank.md` is 4,546 chars (plan: 4,500).
  - Both are recorded in RULE-COVERAGE.md.
- **Static targets not met:** classes A, A+IG and B miss the plan's static targets. I didn't force them (Step 4 item 6). The proposed revision of DC-2/DC-3: drop the per-class static percentages as pass conditions and report them for information only. The binding bar stays DC-6's live ≥ 25 % token reduction, which also counts the output savings (slim human plan, short replies, fewer re-reads) that the static count can't see.
- **Test command:** the fixture tests run as `python -m unittest discover -s tests -t .` from the fixture root (the plan's `-s bench/.../tests` can't import `src`).
- **Script paths:** commands in the skill are written `python <skill>/scripts/...` (scripts live in the skill folder, not the repo root). The core says that `references/`, `assets/` and `scripts/` are in the skill's folder.
- **Copilot JSONL event names are not confirmed.** The runner sums any usage-like fields and falls back to `~/.copilot` session logs. Run `--probe copilot` first.

## Next run (your PC)
1. Unzip into `SKILLS_ROOT` (keep your current skills under git so you can diff).
2. Run the 3 smoke tests and the context check in `bench/skill-token/SMOKE.md` (DC-4, DC-8).
3. Follow `bench/skill-token/README.md`: probe, single runs, then `run_bench.py --tool both --versions v1,v2 --repeats 3` and `report.py` (DC-5 to DC-8).
4. Ask an agent to continue this plan: it reads `PROGRESS.md` here.
