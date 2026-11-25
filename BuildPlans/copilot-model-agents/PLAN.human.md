# Copilot model agents
**Goal:** pick the GPT-6 model by task complexity in GitHub Copilot, using three custom agents that each pin a model, and prove the pinned model really answers.
**Status:** Draft - awaiting review

## Why agents, not a skill
A skill can't choose the model: `SKILL.md` has no `model` field, and the model is already fixed when the skill loads. Custom agents (`.github/agents/*.agent.md`) can pin one.

| Agent | Model | Use for |
|---|---|---|
| `quick` | GPT-6 Luna | Questions, explanations, one-file edits of about 50 lines or fewer, no plan |
| `build` | GPT-6.1 Sol | Plans and executions of up to 10 files |
| `deep` | GPT-6 Astra | Staged plans, more than 10 files or about 400+ lines, public API, DB schema, auth/security, CI/CD, long runs |

You pick the agent. An agent can't switch its own model, so `quick` and `build` stop and name the higher agent when a task is too big for them.

## Scope
- Create: `.github/agents/quick.agent.md`, `.github/agents/build.agent.md`, `.github/agents/deep.agent.md`, `bench/skill-token/check_agent_model.py`.
- Modify: `README.md`, `PROVENANCE.md` (new row), `bench/skill-token/README.md`.

## Impact
- Functional: three new agents in the Copilot agent picker and in `copilot --agent`. Existing skills and benchmark runs are unchanged.
- Non-functional: lower cost on small tasks (Luna is the cheapest GPT-6 model). Only inside this repo, unless you copy the agents to `~/.copilot/agents/`.

## Rules
- No company content in the repo (source: `AGENTS.md`).
- Add a PROVENANCE row; never edit old rows (source: `AGENTS.md`).
- Stdlib-only scripts (source: `bench/skill-token`).

## Contacts
- Owner: you. Needs owner review: no (7 files, no API, schema, auth or CI change).

## Risks & assumptions
- **VS Code may ignore the pin** (reported in microsoft/vscode#338949). Step 7 checks this by hand, with the picker set to another model.
- **Model names are unconfirmed.** They are taken from the Copilot picker at execution. The plan stops if the CLI and VS Code spell them differently.
- **Enterprise policy** must have Luna, 6.1 Sol and Astra enabled.
- **The live checks (Steps 6-7) need the Copilot PC.** Steps 1-5 run anywhere.
- The model check scans Copilot's output and session logs for a model name. If it finds none, the result is UNKNOWN and the plan stops instead of guessing.

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | Three agent files exist with `name`, `description` and a single-string `model` (Luna, 6.1 Sol, Astra) | Original |
| DC-2 | Each description states its tier; `quick` and `build` escalate before editing when a task is above their tier | Original |
| DC-3 | `check_agent_model.py` proves via Copilot CLI that each pinned model answered (selftest + 3× PASS) | Original |
| DC-4 | VS Code hover check: each agent answers on its pin, even with the picker set to another model | Original |
| DC-5 | README tiers + copy note; PROVENANCE row; bench README line | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-2 | Should | How do the descriptions define complexity? | Skill-aligned rubric (table above) | User |
| Q-2 | DC-1, DC-5 | Should | Where do the agents live? | `.github/agents/` + copy note for `~/.copilot/agents/` | User |
| Q-3 | DC-1 | Must | Exact model names? | From the Copilot picker, checked with `copilot --model` at execution | Assumption |
| Q-4 | DC-1 | Could | Single model or fallback list? | Single string (CLI supports only that) | Assumption |
| Q-5 | DC-3 | Could | How to detect the answering model? | Scan JSONL and session logs; UNKNOWN stops | Assumption |
| Q-6 | DC-2 | Could | Should `build` redirect questions to `quick`? | No; only upward escalation | Assumption |
| Q-7 | DC-5 | Could | Record agents in PROVENANCE.md? | Yes | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
| 2026-11-25 | Plan created | - |
