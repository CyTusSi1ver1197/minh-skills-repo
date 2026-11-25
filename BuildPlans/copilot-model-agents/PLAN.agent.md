# EXECUTION PLAN: copilot-model-agents

## Context
A skill can't choose the model in GitHub Copilot. `SKILL.md` frontmatter has no `model` field (official fields: `name`, `description`, `license`, `allowed-tools`), and the model is already fixed when the skill loads. Copilot **custom agents** can pin one: a `model:` field in `.github/agents/<name>.agent.md` frontmatter.

This plan adds three custom agents to the `skill-factory` repo. Each one pins a model to a task-complexity tier:

| Agent | Model | Tier |
|---|---|---|
| `quick` | GPT-6 Luna | Questions, explanations, one-file edits of about 50 changed lines or fewer, no plan |
| `build` | GPT-6.1 Sol | Normal plans and executions (`running-when-a-request-is-made` class A/B) touching up to 10 files, with none of the deep triggers |
| `deep` | GPT-6 Astra | Staged plans, more than 10 files or about 400+ changed lines, a public API contract, DB schema/migrations, auth/security, CI/CD, or long autonomous runs |

The deep triggers are the skill's own "needs owner review" triggers.

The user picks the agent per task: VS Code agent picker, or `copilot --agent <name>` in the CLI. An agent can't switch its own model. When a task is above its tier, it stops before editing and names the higher agent.

Known risks (sources: GitHub changelog/docs, microsoft/vscode#338949, github/copilot-cli#2564 and #2758):
- VS Code has been reported to ignore an agent's `model:` pin and use the chat picker's model.
- VS Code accepts `model:` as a fallback list. The CLI documents a single string, so this plan uses a single string.
- Enterprise model policy limits which models exist. A pin to a disabled model can't work.

So the plan also adds a check that proves which model actually answered.

Repo layout today: `bench/skill-token/` (benchmark harness; `run_bench.py` already runs Copilot CLI and reads its JSONL output and `~/.copilot` session logs), `BuildPlans/`, `README.md`, `PROVENANCE.md`, `AGENTS.md`, `LICENSE` (MIT, Nguyen Phuc Quang Minh). The repo has no `.github/` folder yet.

## Preconditions
- Steps 1-5 run on any PC.
- Steps 6-7 need the PC where Copilot CLI is logged in with a seat that has GPT-6 Luna, GPT-6.1 Sol and GPT-6 Astra enabled by policy.
- Python 3.10+ (stdlib only).
- Before Step 1, on the Copilot PC (or from the VS Code model picker), note the exact model names Copilot accepts. Check each one with `copilot -p hi --model "<name>"`. Also check that `copilot --help` lists `--agent`.

## Rules
- Agent Skills spec and the repo's [AGENTS.md](../../AGENTS.md): keep company names, internal URLs and private evidence out of the repo.
- `PROVENANCE.md`: add a timeline row for new authored work. Never edit existing rows (source: `AGENTS.md`).
- Stdlib only for scripts. No new dependency (source: `bench/skill-token` uses stdlib only).
- Don't change existing skills or the snapshots in `bench/skill-token/versions/`.

## Steps
1. [DC-1, DC-2] Create `.github/agents/quick.agent.md`:
   ```markdown
   ---
   name: quick
   description: "Use for low-complexity work: questions, explanations, code lookup, and one-file edits of about 50 changed lines or fewer that need no plan. Runs on GPT-6 Luna (cheapest). For plans or multi-file changes use the build agent."
   model: <Luna name from Preconditions>
   ---
   You handle low-complexity tasks only.

   Before editing anything, check the task against your tier: one file, about 50 changed lines or fewer, no plan needed. If the task is larger, needs a plan, or touches a public API, DB schema, auth/security or CI/CD, don't edit. Reply with one line naming the agent to use instead (`build` or `deep`) and why.
   ```
   Verify: `python -c "import re,pathlib;t=pathlib.Path('.github/agents/quick.agent.md').read_text();assert re.search(r'^model:\s*\S',t,re.M)"`.
2. [DC-1, DC-2] Create `.github/agents/build.agent.md`, same shape:
   - `name: build`.
   - `description: "Use for medium-complexity work: planning or executing a change of up to 10 files with the running-when-a-request-is-made skill. Runs on GPT-6.1 Sol. For staged plans, more than 10 files, about 400+ changed lines, public API, DB schema, auth/security or CI/CD use the deep agent."`.
   - `model: <6.1 Sol name>`.
   - Body: use the `running-when-a-request-is-made` skill for plans and executions. Escalate to `deep` before editing if any deep trigger applies. If the task is a plain question, answer it; don't redirect to `quick`.
   Verify: same check as Step 1 for `build.agent.md`.
3. [DC-1, DC-2] Create `.github/agents/deep.agent.md`, same shape:
   - `name: deep`.
   - `description: "Use for high-complexity work: staged plans, changes of more than 10 files or about 400+ lines, public API contracts, DB schema or migrations, auth/security, CI/CD, and long autonomous runs. Runs on GPT-6 Astra."`.
   - `model: <Astra name>`.
   - Body: use the `running-when-a-request-is-made` skill (staged plans when the skill calls for them). Keep going through every DC until done or a stop condition applies. No escalation line, since this is the top tier.
   Verify: same check as Step 1 for `deep.agent.md`.
4. [DC-3] Create `bench/skill-token/check_agent_model.py` (stdlib only, about 80 lines):
   - `pinned(path) -> str`: read `model:` from an agent file's frontmatter with a regex.
   - `norm(s) -> str`: lowercase and drop non-alphanumerics, so `GPT-6 Luna` and `gpt-6-luna` compare equal.
   - `seen_models(stdout, since) -> set[str]`: every string value under a key containing `model` in the JSONL lines of `stdout`, plus the same scan over `~/.copilot` session files modified after `since` (same location as `run_bench.copilot_log_fallback`; respect `COPILOT_HOME`).
   - `main`: for each `.github/agents/*.agent.md`, run `copilot -p "Reply with the single word OK." --agent <name> --output-format json --allow-all-tools` from the repo root, **with no `--model` flag**. Print one line per agent: `<name>  pinned=<pin>  seen=<models>  PASS|FAIL|UNKNOWN`. PASS means `norm(pin)` equals the norm of a seen model and no other GPT model was seen. UNKNOWN means no model string was found. Exit 0 only if all three PASS.
   - `--selftest`: assert-based check on synthetic JSONL (one matching, one mismatching, one with no model key). It runs without Copilot.
   - Add `# ponytail: string scan of JSONL/session logs; switch to a structured field once Copilot documents one`.
   Verify: `python bench/skill-token/check_agent_model.py --selftest` prints `selftest OK`.
5. [DC-5] Docs:
   - `README.md`: add a `## Copilot agents` section with the tier table from Context, how to pick an agent (VS Code agent picker; `copilot --agent quick`), and: "To use them in every repo, copy `.github/agents/*.agent.md` to `~/.copilot/agents/`."
   - `PROVENANCE.md`: add a timeline row for the three agents and the check script (date, what, where, source = this plan). Device and work-hours status: "to be confirmed by the author" unless the user states them.
   - `bench/skill-token/README.md`: one line on `check_agent_model.py`.
   Verify: `grep -c "Copilot agents" README.md` = 1; `grep -c "copilot-model-agents" PROVENANCE.md` ≥ 1.
6. [DC-3] On the Copilot PC, from the repo root: `python bench/skill-token/check_agent_model.py`.
   Verify: 3 lines with PASS, exit code 0. Save the output in `EXECUTION-SUMMARY.md`.
7. [DC-4] On the Copilot PC, in VS Code (Copilot Chat, agent mode):
   - Set the chat model picker to a model that is **not** any pin, for example Auto.
   - For each agent, select it, send `Reply with the single word OK.`, and hover the response to read the model.
   Verify: the hover model equals the pin for all 3 agents. Record each result in `EXECUTION-SUMMARY.md`. A mismatch is the known VS Code bug: record the VS Code version and mark DC-4 NOT MET.

## DC checklist
- [ ] DC-1 - verify by: Steps 1-3 checks; `copilot` lists `quick`, `build` and `deep` (`/agent` in an interactive session).
- [ ] DC-2 - verify by: each description names its tier and the next agent up; each of `quick` and `build` has the escalation rule in its body.
- [ ] DC-3 - verify by: Step 4 selftest, then Step 6 3× PASS.
- [ ] DC-4 - verify by: Step 7 hover results recorded.
- [ ] DC-5 - verify by: Step 5 greps.

## Stop conditions
- Stop and ask if:
  - `copilot --help` has no `--agent` flag, or `/agent` doesn't list the repo agents;
  - any of the three models is missing from `copilot` or the VS Code picker (a policy may disable it);
  - the CLI and VS Code need different spellings of the same model name in `model:`;
  - Step 6 prints UNKNOWN for any agent. Don't guess the model. Record what the terminal shows and ask;
  - Step 6 or 7 shows a model other than the pin. Record it; don't work around it with `--model`.
- Don't edit existing skills, `bench/skill-token/versions/`, or existing PROVENANCE rows.

## Contacts
- Owner: the user (sole author). No CODEOWNERS.
- Needs owner review: no (7 files, no API, schema, auth or CI change).

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | `.github/agents/quick.agent.md`, `build.agent.md` and `deep.agent.md` exist, each with `name`, `description` and a single-string `model`: quick = GPT-6 Luna, build = GPT-6.1 Sol, deep = GPT-6 Astra, spelled as Copilot accepts them | Original |
| DC-2 | Each description states its complexity tier (skill-aligned rubric). `quick` and `build` stop before editing when a task is above their tier and name the higher agent | Original |
| DC-3 | `bench/skill-token/check_agent_model.py` runs each agent via Copilot CLI without `--model` and reports PASS only when the answering model equals the pin; its `--selftest` passes without Copilot; the live run gives 3× PASS | Original |
| DC-4 | In VS Code, with the picker set to another model, each agent answers on its pinned model (hover check), and the result is recorded | Original |
| DC-5 | `README.md` documents the tiers and the copy to `~/.copilot/agents/`; `PROVENANCE.md` has a row for this work; `bench/skill-token/README.md` mentions the check | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-2 | Should | How do the descriptions define complexity? | Skill-aligned: quick = questions and one-file edits of about 50 lines or fewer; build = plans of up to 10 files; deep = the skill's owner-review triggers and staged plans | User |
| Q-2 | DC-1, DC-5 | Should | Where do the agents live? | `.github/agents/` in this repo, plus a README note to copy them to `~/.copilot/agents/` | User |
| Q-3 | DC-1 | Must | Exact model names for `model:`? | Taken from the Copilot picker and checked with `copilot --model` at execution. Stop if the CLI and VS Code spellings differ | Assumption |
| Q-4 | DC-1 | Could | Single model or fallback list in `model:`? | Single string, because the CLI documents only that | Assumption |
| Q-5 | DC-3 | Could | How to detect the answering model? | Scan JSONL output and new `~/.copilot` session files for `model` keys; UNKNOWN is a stop | Assumption |
| Q-6 | DC-2 | Could | Should `build` redirect plain questions to `quick`? | No, it answers them. Only upward escalation, to avoid ping-pong | Assumption |
| Q-7 | DC-5 | Could | Record agents in PROVENANCE.md, though they aren't skills? | Yes: new authored work, same record | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
| 2026-11-25 | Plan created | - |
