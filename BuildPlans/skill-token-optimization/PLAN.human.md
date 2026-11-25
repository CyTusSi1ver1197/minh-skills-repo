# Skill token optimization + staged plans: running-when-a-request-is-made v2
**Goal:** Cut the tokens the request-workflow skills use in Claude Code and GitHub Copilot by loading only the part of the workflow each request needs. Add **staged plans** so work too large for one session is split into flows of small, self-contained stages that later agents can continue. Prove it by running the same tasks on v1 and v2 in both tools.
**Status:** Executed v2.0 (failed the token bar: turns doubled); v2.1 built, awaiting re-run on Claude Code

## Scope
- Area: the two skills `running-when-a-request-is-made` and `information-gathering-for-plan`, plus a benchmark under `bench/skill-token/`.
- Skill files:
  - `SKILL.md` (modify): becomes a small core (≤ 3,400 chars, from 12,378) with the router and 7 context-budget rules. Rule 7 is "integrity before size".
  - `references/planning.md`, `references/execution.md` (create): read only for plan or execute requests.
  - `references/staged-plans.md` (create): split rules, the `FLOW.md` format, how flows are executed, the low-context stop.
  - `assets/*.template.md` (create, 5 files): plan, progress, summary and **FLOW** templates.
  - `scripts/` (create, 4 files):
    - `contacts.py`: owners and owner-review flags.
    - `flow_status.py`: rebuilds FLOW.md status from each stage's progress file.
    - `statusline_context.py`: a status-line script for both tools that saves the context % to a file.
    - `context_check.py`: reads that file.
  - `information-gathering-for-plan/SKILL.md` (modify): small core plus `references/gather-and-rank.md` and `assets/report.template.md` (create).
- Benchmark (create): v1 snapshot, a Python fixture repo including a small staged plan, 8 tasks, a validator, a runner for both CLIs, a quality checker and a report.

## How a staged plan looks
```
BuildPlans/<plan-name>/
├── FLOW.md              ← master file: flows, stages, progress, next stage, parallel flows, optional flows
├── F1-S01-<name>/       ← stage = sub-plan: PLAN.human.md, PLAN.agent.md, PROGRESS.md
├── F1-S02-<name>/
└── F2-S01-<name>/       ← stage of a parallel flow
```
- **When to split:** a stage has ≤ 4 DCs, ≤ 15 files and ≤ 600 changed lines. The plan is split into flows only when it needs **more than 7 stages**. Otherwise it stays one normal plan.
- **Flow kinds:** **main** (required, in order), **parallel** (required, can run at the same time once its start stage is done), **optional** (improvements).
- **Status tracking:**
  - Agents update only their own stage's `PROGRESS.md` after every DC; a script rebuilds the FLOW.md status block. This avoids edit clashes between parallel agents.
  - A new agent reads FLOW.md, then only the current stage's files, and continues from there.
- **Low-context stop:** at ≤ 5 % context left, the agent asks you whether to stop. If you say yes, or nobody is there to answer, it saves the stage as `PAUSED` with a resume note.
- **Integrity before compression:** every stage plan repeats the context it needs and gets earlier stages' outputs only through named files or contracts. Compression never removes DCs, verify lines, paths, rules, stop conditions or assumptions.

## Impact
- Functional:
  - Same workflow, IDs, questions and BuildPlans layout for normal plans.
  - Human plan ≤ 60 lines, with the Map only in the agent plan (approved earlier).
  - New: staged-plan mode and flow execution with resume.
- Non-functional:
  - Less skill text per request: plan requests ≤ 70 %, execute ≤ 50 %, other ≤ 25 % of v1.
  - Staged plans cost more tokens to write, because each stage repeats its context on purpose. They are needed for large work.
  - Benchmark: 78 headless runs billed to your Claude and Copilot accounts.
  - The 5 % stop needs a one-time status-line setup per tool. VS Code agent mode has no status-line hook, so it relies on saving status after each DC.

## Rules
- Agent Skills spec: `name` = folder name; descriptions unchanged.
- Keep core files well under Claude Code's 5,000-token re-injection cap after compaction.
- Sizing (from you): ≤ 4 DCs / ≤ 15 files / ≤ 600 lines per stage; split only when more than 7 stages are needed.
- No project rules file was given for the skills repo.

## Contacts
- You (skill owner). No CODEOWNERS found.
- Needs owner review: **yes**. More than 10 files change, and the output contract changes.

## Risks & assumptions
- **Fixture bias:** the token saving measured on a tiny repo will be higher than on big repos. RESULTS.md shows static and live numbers separately.
- **"≥ 7 stages per 5-hour session" can't be measured directly:** agents can't see your 5-hour usage window. The stage caps are the stand-in, and the report shows tokens per stage so you can tune them.
- **Context % may be missing:** the status-line fields may be empty early in a session, and the hook doesn't run in headless mode. Then the agent sees `unknown` and falls back to saving status after each DC. T8 tests the stop by planting a 4 % reading.
- **Copilot token data:** if neither JSON output nor session logs have counts, execution stops and asks.
- **Assumptions:**
  - The staged features (T6-T8) are quality checks only and are not part of the 25 % bar.
  - The consequence check is asked once per session.
  - Unattended runs stop by themselves at ≤ 5 %.
  - The master Map lives in FLOW.md.

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | v1 preserved; static load per class measured | Original |
| DC-2 | running skill v2: core + references + templates + scripts, all v1 rules kept, human plan ≤ 60 lines | Revised via Q-3 |
| DC-3 | information-gathering v2 loads only its "needed?" check unless gathering is required | Original |
| DC-4 | Both v2 skills valid and routing correctly in Claude Code, Copilot CLI, VS Code agent mode | Original |
| DC-5 | Reproducible benchmark (fixture, tasks, runners, checker, report) | Original |
| DC-6 | v2.1 turns and cost ≤ v1 and quality not lower on every task T1-T5, Claude Code only | Revised via Q-23, Q-24 |
| DC-7 | Staged plans: more than 7 stages → FLOW.md + stage sub-plans in main / parallel / optional flows, self-contained stages | Added via Q-14, Q-15 |
| DC-8 | Per-stage status sync to FLOW.md, resume by later agents, ask-to-stop at ≤ 5 % context with PAUSED status | Added via Q-16, Q-17 |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | all | Must | Output format? | Standard BuildPlans set | User |
| Q-2 | DC-6 | Should | Pass bar? | ≥ 25 % less, same quality | User |
| Q-3 | DC-2 | Should | Change output contract? | Yes, slim human plan | User |
| Q-4 | DC-5 | Should | Benchmark runner? | Headless CLIs on your PC, 3 repeats + static | User |
| Q-5 | DC-2 | Could | Separate memory skill? | No | Assumption |
| Q-6 | DC-3 | Could | Include information-gathering skill? | Yes | Assumption |
| Q-7 | all | Could | Where do the skills live? | `SKILLS_ROOT` | Assumption |
| Q-8 | DC-5 | Could | Fixture stack? | Python stdlib + unittest | Assumption |
| Q-9 | DC-5, DC-6 | Could | Repeats / model / order? | 3, fixed model per tool, interleaved | Assumption |
| Q-10 | DC-4 | Could | VS Code agent mode coverage? | Manual smoke test | Assumption |
| Q-11 | DC-2 | Could | Shorter execution-summary reply? | Yes | Assumption |
| Q-12 | DC-1 | Would | Static token count method? | chars ÷ 4, exact API count if key set | Assumption |
| Q-13 | DC-5 | Could | Headless question handling? | Fixed non-interactive suffix | Assumption |
| Q-14 | DC-7 | Must | Stage vs sub-plan? | 1 stage = 1 sub-plan folder | User |
| Q-15 | DC-7 | Must | Sizing rule? | ≤ 4 DCs, ≤ 15 files, ≤ 600 lines; split when more than 7 stages | User |
| Q-16 | DC-8 | Must | Low-token signal? | Context window ≤ 5 % remaining | User |
| Q-17 | DC-8 | Should | Parallel write safety? | Per-stage PROGRESS.md + rebuild script | User |
| Q-18 | DC-7, DC-8 | Could | Staged features in the 25 % bar? | No, quality checks only | Assumption |
| Q-19 | DC-8 | Could | Consequence check in flow runs? | Once per session | Assumption |
| Q-20 | DC-8 | Could | ≤ 5 % with nobody to answer? | Stop and save PAUSED | Assumption |
| Q-21 | DC-7 | Could | Master Map location? | FLOW.md | Assumption |
| Q-22 | DC-8 | Could | Tool without status-line hook? | `unknown` → per-DC checkpoints | Assumption |
| Q-23 | DC-6 | Must | Pass bar measure? | Turns + cost per task ≤ v1, quality not lower; /usage per batch | User |
| Q-24 | DC-6 | Must | Tools benchmarked? | Claude Code only | User |
| Q-25 | DC-2, DC-3 | Should | Static size targets? | Information only | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
| 2026-11-24 | Plan created | - |
| 2026-11-24 | v2.0 failed (turns doubled on plan requests); v2.1 built for fewer turns; bar → turns + cost, Claude Code only | User |
| 2026-11-24 | Added staged plans, status sync, low-context stop, integrity rule (DC-7, DC-8) | User |
