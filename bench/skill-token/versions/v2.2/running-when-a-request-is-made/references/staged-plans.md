# Staged plans: flows of stage sub-plans

## When and how to split

Group DCs into **stages**: ≤ 4 DCs, ≤ 15 files changed, ≤ 600 changed lines each, so an agent can finish at least 7 stages of a flow in one 5-hour session. Use a staged plan only when **more than 7 stages** are needed; otherwise write one normal plan. If one DC alone breaks the caps, split it and record `DC-n (revised from: ...)` in the master Map.

```
BuildPlans/[optional grouping/]<plan-name>/
├── FLOW.md            # the one master flow file (layout below)
├── F1-S01-<kebab>/    # stage = sub-plan: PLAN.human.md, PLAN.agent.md, PROGRESS.md
├── F1-S02-<kebab>/
├── F2-S01-<kebab>/    # stage of another flow
└── assets/            # optional shared media
```

Stage folders start with flow and stage number, so name order is flow order.

**Flows:** each stage belongs to exactly one flow. **main** (F1): required, stages in order. **parallel**: required, runs at the same time as other flows once its `Starts after` stage is MET. **optional**: improvements, not needed for done. A stage may also list `Needs: <stage ids>` from other flows.

**FLOW.md:** Goal; **Flows** table (`Flow | Kind | Stages in order | Starts after | Runs in parallel with`); the generated **Status** block between `<!-- flow-status:start -->` and `<!-- flow-status:end -->` (per flow: done/total, current stage, **Next stage**; per stage: status, DCs MET/total, last update, paused note; ready stages; session log); **Shared context** (only the contracts between stages: interfaces, paths, schemas a later stage consumes); master **Done Criteria** (each master DC → its stage(s)), **Question Map**, **Revision log**.

FLOW.md layout (write it whole in one call):
```
# FLOW: <plan-name>
**Goal:** <two lines>

## Flows
| Flow | Kind | Stages in order | Starts after | Runs in parallel with |
|---|---|---|---|---|
| F1 | main | F1-S01, F1-S02 | - | F2 |
| F2 | parallel | F2-S01 | F1-S01 | F1 |

## Status
<!-- flow-status:start -->
<!-- flow-status:end -->

## Shared context
- <contract> (produced by <stage>, used by <stage>)

## Done Criteria
| ID | Done criterion | Stage(s) | Status |
|---|---|---|---|

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|

## Revision log
| Date | Change | Approved by |
|---|---|---|
```
Then run `python <skill>/scripts/flow_status.py BuildPlans/<plan>` once to fill the Status block.

**Stage plans** use the normal plan layouts from `SKILL.md` Step 3 and the `PROGRESS.md` layout from `references/execution.md`. Write all stage files of the plan in as few steps as possible. DC IDs are stage-local and prefixed (`F1-S02/DC-1`), each mapped to a master DC. **Integrity rule:** every stage `PLAN.agent.md` is self-contained. It repeats the context, rules, paths and signatures it needs and takes earlier results only through `Inputs from earlier stages: <stage id> → <file/contract>`. Never write "see other stage", "as discussed" or "same as before".

## Executing a staged plan

1. Read `FLOW.md` (Status block, Flows, Shared context only). Pick the stage the user named; else the main flow's Next stage; for "parallel", the named flow's ready stage.
2. Consequence check once per session, listing every stage planned for this session.
3. Run each stage as a normal plan (`references/execution.md`). After every DC, update **that stage's** `PROGRESS.md`, then run `python <skill>/scripts/flow_status.py BuildPlans/<plan>`. Never hand-edit the Status block or another stage's `PROGRESS.md`. This keeps parallel agents off the same lines.
4. When a stage is MET, continue with the next stage of the same flow if its `Starts after` / `Needs` stages are MET.

## Low-context stop

Run the context check before each DC and before each new stage (same rule as `references/execution.md` step 5): `python <skill>/scripts/context_check.py`.
- `remaining=<n>` with n ≤ 5 %, or any context-low / usage-limit warning from the tool → stop and ask: "Context is at ≤ 5 % remaining. Stop here and save status for the next run? (yes/no)".
- **yes**, or nobody can answer (headless/unattended) → set the stage's `PROGRESS.md` to `PAUSED` with last finished step, Next step and a 3-line Resume note (what is half done, files touched, what to verify first). Run `flow_status.py`, end the turn.
- **no** → continue; ask again after the next DC.
- `remaining=unknown` (no status-line hook, e.g. VS Code) → write a Resume note before each new stage.

**Resume:** read `FLOW.md`, then the `PROGRESS.md` of the current stage(s). A `PAUSED` stage restarts at its Next step after checking its Resume note.

## Setup (once per machine)

Add `.agent-context.json` to `.gitignore`. Set `scripts/statusline_context.py` as the status-line command:
- Claude Code `~/.claude/settings.json`: `"statusLine": {"type": "command", "command": "python <skill>/scripts/statusline_context.py"}`
- Copilot CLI `~/.copilot/settings.json`: the same `statusLine` block (enable via `/statusline` if needed).
VS Code agent mode has no status-line hook, so it runs with `remaining=unknown`.
