# EXECUTION PLAN: skill-token-optimization

## Context

Two Agent Skills are maintained as plain folders, used by both **Claude Code** and **GitHub Copilot** (Copilot CLI, Copilot cloud agent, VS Code agent mode):

- `running-when-a-request-is-made/SKILL.md` (v1: 224 lines, 12,378 chars, single file). Workflow: Step 0 classify request (A plan / B execute / C other) → Step 1 DC & GD + MoSCoW questions → Step 2 outputs → Step 3 write `BuildPlans/<plan-name>/PLAN.human.md` + `PLAN.agent.md` → Step 4 execute an approved plan DC by DC → Templates.
- `information-gathering-for-plan/SKILL.md` (v1: 161 lines, 8,440 chars, single file). Called from Step 1 of the first skill when GD/DC are unclear. Steps 1-6 + report template.

Both tools use **progressive disclosure** for skills: at startup only `name` + `description` are in context; the full `SKILL.md` body is injected when the skill is chosen; other files in the skill folder are read only when `SKILL.md` tells the agent to read them, and scripts can be executed without being loaded into context.

**Problem:** v1 loads the whole 12.4K-char workflow on every use, even when only one class applies (class B never needs Steps 1-3; class C needs only Step 0). The body then stays in context for every later turn. It also writes duplicated output (the DC & Question Map in both plan files, the execution summary both in the reply and in a file) and gives no rules limiting how much the agent reads while discovering GD.

**Goal:** a v2 of both skills that keeps every v1 behaviour and ID (`DC-n`, `GD-n`, `Q-n`, MoSCoW, BuildPlans layout) but uses fewer tokens, plus a benchmark that runs the **same task set** against v1 and v2 on **both** tools and proves the saving.

**Second goal: staged plans.** When a plan is too large for one agent session, the planner splits it into **stages**. Each stage is one sub-plan folder with its own `PLAN.human.md` + `PLAN.agent.md`. Stages are grouped into **flows**:
- the **main** flow is required, run in order;
- **parallel** flows are required and can run at the same time as other flows;
- **optional** flows are improvements.

One master file `FLOW.md` shows which flow contains which stages, each flow's progress and next stage, and which flows run in parallel. Executing agents record status per stage, and a script rebuilds `FLOW.md` from that, so a later agent can continue where the previous one stopped. When the context window has ≤ 5 % left, the agent asks whether to stop, then saves resume status. **Context integrity comes before compression:** every stage plan stays self-contained.

**Approved decisions (from the user):**
- Pass bar: in each tool, total tokens drop **≥ 25 %** (v2 vs v1, aggregate of per-task medians) and the output-quality score does **not drop** on any task.
- Output contract may change: `PLAN.human.md` becomes a short summary (≤ 60 lines) that links to the DC & Question Map, which lives **only** in `PLAN.agent.md`. `PLAN.agent.md` stays fully self-contained.
- Benchmark runs headless on the user's Windows PC: `claude -p ... --output-format json` and `copilot -p ... --output-format json`, 3 repeats per task per version per tool, plus a deterministic static size count.

**Known limits that shape the design:**
- Claude Code, after compaction, re-injects invoked skill bodies capped at 5,000 tokens per skill, keeping the start of the file. Core `SKILL.md` files must stay far below that, with the most important rules at the top.
- Headless runs cannot answer questions, so every benchmark prompt carries pre-set answers (see Step 9).
- VS Code agent mode has no headless runner. It gets a manual smoke test only (Step 8); the token benchmark covers Copilot CLI, which uses the same skill format.

## Preconditions

- Environment variable `SKILLS_ROOT` = the folder that contains both skill folders (e.g. `C:\dev\agent-skills`). All paths below are relative to it. It should be a git repo; create branch `feat/skill-token-optimization`.
- Tools on PATH: `git`, `python` ≥ 3.10 (stdlib only, no installs), `claude` (Claude Code CLI, signed in), `copilot` (GitHub Copilot CLI, signed in, Copilot Memory may stay on).
- During benchmark runs, no other copy of either skill may be discoverable at user level. Before Step 10, move any copies out of `~/.claude/skills/`, `~/.copilot/skills/` and `~/.config/github-copilot/skills/` into `%USERPROFILE%\skills-parked\`, and restore them after Step 11. Record what was moved in `bench/skill-token/PARKED.md`.
- Pick one model per tool and keep it fixed for all runs (e.g. Claude Code `--model sonnet`, Copilot `--model <model shown by copilot -p "hi">`). Record both in `bench/skill-token/config.json`.

## Rules

- Agent Skills spec: frontmatter `name` equals the folder name, lowercase-hyphen; `description` ≤ 1,024 chars. Keep both v1 descriptions unchanged (they drive discovery).
- Keep the vocabulary, IDs, MoSCoW table, class names, BuildPlans folder layout and all user-facing question wordings from v1. v2 changes **where** text lives and **how much** is loaded, not what the workflow does (apart from the approved output-contract change).
- All links inside a skill are relative paths within that skill's folder. No absolute paths, no tool-specific syntax without a fallback sentence for the other tool.
- Core `SKILL.md` ≤ 3,400 chars (running) and ≤ 2,500 chars (information-gathering).
- **Integrity before size (applies to every compression in this plan and to the v2 skill itself).** A char budget never justifies removing any of these: a DC text, a Verify line, an exact path or signature, a rule and its source, a stop condition, an assumption, or the context a stage plan needs to run alone. If a budget can't be met without removing one of them, raise the budget and record why in `RULE-COVERAGE.md`. Don't cut the item.
- Staged-plan sizing (user-set): a stage has ≤ 4 DCs, ≤ 15 files changed, ≤ 600 changed lines. Use staged mode only when the plan needs **more than 7 stages**; otherwise write one normal plan. Reference files ≤ the budgets given in each step.
- Scripts: Python 3 stdlib only, runnable on Windows and Linux, no network.
- No project rules file was given for the skills repo. If `SKILLS_ROOT` contains `CLAUDE.md`, `AGENTS.md` or `.github/copilot-instructions.md`, follow it and note it in the summary.

## Target layout (v2)

```
running-when-a-request-is-made/
├── SKILL.md                          # core: goal, vocabulary, Step 0 router, context-budget rules
├── references/
│   ├── planning.md                   # Steps 1-3 (class A)
│   ├── execution.md                  # Step 4 (class B)
│   └── staged-plans.md               # split rules, FLOW.md, flow execution, low-context stop
├── assets/
│   ├── PLAN.agent.template.md        # includes DC & Question Map + Revision log
│   ├── PLAN.human.template.md        # ≤ 60-line summary, links to the agent plan's Map
│   ├── PROGRESS.template.md          # execution checkpoint (also per stage)
│   ├── FLOW.template.md              # master flow file for staged plans
│   └── EXECUTION-SUMMARY.template.md
└── scripts/
    ├── contacts.py                   # CODEOWNERS / top committers + owner-review flags
    ├── flow_status.py                # rebuilds FLOW.md status block from each stage's PROGRESS.md
    ├── context_check.py              # prints remaining context % (or "unknown")
    └── statusline_context.py         # status-line command for Claude Code + Copilot CLI; writes the context file
information-gathering-for-plan/
├── SKILL.md                          # core: purpose, modes, vocabulary, Step 1 "is this needed?"
├── references/
│   └── gather-and-rank.md            # Steps 2-6
└── assets/
    └── report.template.md            # its output template
bench/skill-token/                    # benchmark harness (Steps 9-11)
```

## Steps

1. **[DC-1] Snapshot v1.** Copy both skill folders unchanged to `bench/skill-token/versions/v1/running-when-a-request-is-made/` and `bench/skill-token/versions/v1/information-gathering-for-plan/`. Commit.
   Verify: `git diff --no-index running-when-a-request-is-made bench/skill-token/versions/v1/running-when-a-request-is-made` prints nothing (same for the other skill).

2. **[DC-1] Create `bench/skill-token/static_measure.py`.** Input: a version folder (`versions/v1` or `versions/v2`). For each class scenario it sums the characters of the files that version loads, and prints chars and estimated tokens (chars ÷ 4; if env var `ANTHROPIC_API_KEY` is set, also call the Messages count-tokens endpoint and print exact tokens). Scenarios:
   - v1: `A` = running/SKILL.md; `A+IG` = running/SKILL.md + IG/SKILL.md; `B` = running/SKILL.md; `C` = running/SKILL.md.
   - v2: `A` = SKILL.md + references/planning.md + assets/PLAN.agent.template.md + assets/PLAN.human.template.md; `A+IG` = A + IG/SKILL.md + IG/references/gather-and-rank.md + IG/assets/report.template.md; `B` = SKILL.md + references/execution.md + assets/PROGRESS.template.md + assets/EXECUTION-SUMMARY.template.md; `C` = SKILL.md.
   Output: a markdown table, appended to `bench/skill-token/STATIC.md`.
   Verify: `python bench/skill-token/static_measure.py bench/skill-token/versions/v1` prints A = 12,378 chars and A+IG = 20,818 chars (±2 % for line endings).

3. **[DC-2] Write the v2 core `running-when-a-request-is-made/SKILL.md`** (replace v1 content; keep frontmatter unchanged). It holds only: title; the goal line; the vocabulary line (add: **Stage** = one sub-plan folder of a staged plan; **Flow** = an ordered list of stages, kind main / parallel / optional); **Step 0** with the class table, where the "Go to" column becomes "Read next":
- A → `references/planning.md`;
- B → `references/execution.md`. Add to B's signal: "or points to `BuildPlans/<plan>/FLOW.md` / says 'continue the plan'"; for FLOW.md also read `references/staged-plans.md`;
- C → "ask once".
Then the v1 class C question **verbatim** with its Yes/No handling, a loading rule, and the **Context budget** section. Use this text for the new parts (the 7th rule is the integrity rule):

   > Read a reference file only when its class applies, once per conversation. Re-read it only if it changed or was lost to compaction. Read a template from `assets/` only when you are about to write that file.
   >
   > **Context budget (always on)**
   > 1. Search before you read: list or grep first, then read only the relevant files or line ranges. Read files over 300 lines in sections. Don't re-read a file already in context unless it changed.
   > 2. Delegate broad discovery when a sub-agent tool exists (Claude Code: the Explore or Task agent; Copilot: its sub-agent or `runSubagent` tool). Ask for a summary of at most 30 lines with `file:line` evidence. Without one, follow rule 1 inline.
   > 3. Keep tool output small: filter command output (failures only, `tail`, `--quiet`, counts) instead of pasting whole logs.
   > 4. Write each output file once, starting from its template. Fix it with targeted edits, not full rewrites.
   > 5. State lives in files, not in chat: the plan in `BuildPlans/<plan-name>/`, execution progress in its `PROGRESS.md`. After compaction or resume, re-read only those files.
   > 6. Replies summarize and link. Don't repeat file contents in chat.
   > 7. Integrity before size: never compress away a DC, a Verify line, an exact path or signature, a rule and its source, a stop condition, an assumption, or the context a plan or stage needs to run alone.

   Budget: ≤ 3,400 chars total including frontmatter.
   Verify: `python -c "import pathlib;print(len(pathlib.Path('running-when-a-request-is-made/SKILL.md').read_text(encoding='utf-8')))"` ≤ 3400, and `grep -c "references/planning.md\|references/execution.md\|references/staged-plans.md" running-when-a-request-is-made/SKILL.md` ≥ 3.

4. **[DC-2] Create `running-when-a-request-is-made/references/planning.md`** from v1 Steps 1, 2 and 3. Budget ≤ 4,400 chars. Condense by doing exactly this:
   - Keep verbatim: the MoSCoW table, the Step 2 output-format question, the Step 1 rule to run `information-gathering-for-plan` (with its caps 10 missing / 6 additional), the "needs owner review" thresholds, the final reply line ("Review `BuildPlans/.../PLAN.human.md`. When it meets the requirements, ask me (or any agent) to execute `BuildPlans/.../PLAN.agent.md`.").
   - Replace the folder-layout code block with one sentence plus the path pattern `BuildPlans/[optional grouping/]<plan-name>/{PLAN.human.md, PLAN.agent.md, assets/}`.
   - Replace the "Required content" and the two "written for review / execution" sections with: a 5-item list (Scope, Impact, Rules, Contacts, DC & Question Map), followed by "Start from `assets/PLAN.agent.template.md` and `assets/PLAN.human.template.md`."
   - Contacts: "Run `python scripts/contacts.py <changed files...>` from the repo root. If Python is unavailable, use CODEOWNERS, else `git log --format='%an <%ae>' -- <file> | sort | uniq -c | sort -rn | head -3`."
   - **New output contract:** `PLAN.human.md` ≤ 60 lines: Goal (2 lines), Scope, Impact, Rules, Contacts, Risks & assumptions, and a final line linking to `PLAN.agent.md#done-criteria` instead of repeating the Map. `PLAN.agent.md` keeps the full DC & Question Map and stays self-contained.
   - Add the GD discovery rule: "Discover GD under the Context budget rules in `SKILL.md`. Record each GD item as one line: `GD-n | source (path or link) | what it gives`."
   - Add the sizing check, placed before writing files: "Estimate the stages: group the DCs into stages of ≤ 4 DCs, ≤ 15 files changed and ≤ 600 changed lines. If the plan needs more than 7 stages, read `references/staged-plans.md` and write a staged plan. Otherwise write one normal plan."
   - Add the compression rule: "After drafting, compress only by removing repetition and boilerplate. Integrity before size (rule 7)."
   Verify: file ≤ 4,400 chars, and each of these strings occurs in it: `Must`, `Should`, `Could`, `Would`, `information-gathering-for-plan`, `needs owner review`, `PLAN.agent.template.md`, `60 lines`, `staged-plans.md`, `more than 7 stages`.

5. **[DC-2] Create `running-when-a-request-is-made/references/execution.md`** from v1 Step 4. Budget ≤ 2,600 chars. Keep items 1-8 and the consequence-check question verbatim. Change:
   - Item 4: the checklist goes into `BuildPlans/<plan>/PROGRESS.md` (from `assets/PROGRESS.template.md`) **and** the task-list tool if one exists. Update `PROGRESS.md` after each DC (status + last finished step).
   - Add: "On resume or after compaction, read `PROGRESS.md` and only the plan steps for the next unfinished DC."
   - Item 5: the verifier's answer must be "MET / NOT MET + at most 10 lines of evidence".
   - Item 7: run tests and linters with output filtered to failures and the summary line.
   - Item 8: write `EXECUTION-SUMMARY.md` from `assets/EXECUTION-SUMMARY.template.md`. The reply shows only the DC status table and a link to the file.
   Verify: file ≤ 2,600 chars; contains `PROGRESS.md`, `Do you understand these consequences`, `MET / NOT MET`, `EXECUTION-SUMMARY.md`, `unit-tests`.

6. **[DC-2] Create the assets and script.**
   - `assets/PLAN.agent.template.md`: the v1 PLAN.agent.md template plus the full v1 DC & Question Map + Revision log template at the end, with heading `## Done Criteria` (anchor `done-criteria`).
   - `assets/PLAN.human.template.md`: Goal, Status, Scope, Impact, Rules, Contacts, Risks & assumptions, then the line `Done criteria and question map: [PLAN.agent.md](PLAN.agent.md#done-criteria)`. Add the one-line HTML comment `<!-- max 60 lines -->`.
   - `assets/PROGRESS.template.md`: a table `| DC | Status (TODO/IN PROGRESS/MET/NOT MET/REVISED) | Last step | Note |` and a line `Next: <step number>`.
   - `assets/EXECUTION-SUMMARY.template.md`: sections Files changed (one line each), DC status table, Rule & test results, Assumptions & deviations.
   - `scripts/contacts.py`: args = file paths. For each file: CODEOWNERS owner (checks `CODEOWNERS`, `.github/CODEOWNERS`, `docs/CODEOWNERS`; last matching pattern wins), else top 3 committers via `git log`. Then print the flags: file count > 10, and any path matching `migrations|schema|auth|security|\.github/workflows|ci|pipeline|api` → "needs owner review: yes (<reason>)". Exit 0 always. Use stdlib only.
   Verify: total size of the four templates ≤ 2,500 chars (checked before Step 7B adds stage fields); `python running-when-a-request-is-made/scripts/contacts.py running-when-a-request-is-made/SKILL.md` prints at least one contact line and a `needs owner review:` line.

7. **[DC-3] Split `information-gathering-for-plan`.**
   - Core `SKILL.md` (≤ 2,500 chars, frontmatter unchanged): purpose, the two modes, the vocabulary, and v1 Step 1 (the problem table and "If nothing is flagged ... stop"). End it with: "If anything is flagged, read `references/gather-and-rank.md` and follow Steps 2-6."
   - `references/gather-and-rank.md` (≤ 4,500 chars): v1 Steps 2-6. Keep verbatim the four ranking tiers, the caps (10 missing, 6 additional), and every conflict rule. Add: "Gather under the Context budget rules of the calling skill, or, standalone: search before you read, read only relevant ranges, delegate broad search to a sub-agent when one exists."
   - `assets/report.template.md`: the v1 report template.
   Verify: core ≤ 2,500 chars and contains `gather-and-rank.md`; reference contains `10`, `6`, `Most Relevant`, `Most Effective`.

7A. **[DC-7] Create `running-when-a-request-is-made/references/staged-plans.md`** (≤ 4,500 chars). It defines:
   - **Trigger and sizing:** the rule from Step 4 (stage ≤ 4 DCs / ≤ 15 files / ≤ 600 changed lines; staged mode only when more than 7 stages are needed). A stage this size is meant to let an agent finish at least 7 stages of a flow in one 5-hour session. If a single DC alone breaks the caps, split the DC and record it as `DC-n (revised from: ...)` in the master Map.
   - **Folder layout:**
     ```
     BuildPlans/[optional grouping/]<plan-name>/
     ├── FLOW.md                       # the one master flow file
     ├── F1-S01-<kebab>/               # stage = sub-plan: Flow 1, Stage 01
     │   ├── PLAN.human.md  PLAN.agent.md  PROGRESS.md  [EXECUTION-SUMMARY.md]
     ├── F1-S02-<kebab>/ ...
     ├── F2-S01-<kebab>/ ...           # another flow
     └── assets/                       # optional, shared media
     ```
     Folder names start with the flow and stage number, so a sort by name gives the flow order.
   - **Flows:** each stage belongs to exactly one flow.
     - **main** (F1): required; its stages run in order.
     - **parallel**: required; runs at the same time as other flows once its `Starts after` stage is MET.
     - **optional**: an improvement, not needed for the plan to be done.
     Within a flow, stages always run in order. A stage may also list `Needs: <stage ids>` from other flows.
   - **FLOW.md content** (from `assets/FLOW.template.md`): Goal; a **Flows** table (`Flow | Kind | Stages in order | Starts after | Runs in parallel with`); a generated **Status** block between `<!-- flow-status:start -->` and `<!-- flow-status:end -->`, with:
     - per flow: done/total stages, current stage, **Next stage**;
     - per stage: status, DCs MET/total, last update, paused-at note;
     - a list of stages that are ready now;
     - a short session log.
     Then a **Shared context** section, which lists only the contracts between stages: interfaces, file paths, schemas a later stage consumes. The FLOW.md file closes with the master **Done Criteria** (each master DC → the stage(s) that meet it), the **Question Map** and the **Revision log**.
   - **Stage plans:** normal plans from the normal templates. Their DC IDs are stage-local and prefixed (`F1-S02/DC-1`), each mapped to a master DC. **Integrity rule:** each stage `PLAN.agent.md` is self-contained. It repeats the context, rules, paths and signatures it needs, and gets inputs from earlier stages only through a section `Inputs from earlier stages: <stage id> → <file/contract>`. Never write "see other stage", "as discussed" or "same as before".
   - **Execution of a staged plan:**
     1. Read `FLOW.md` (Status block + Flows + Shared context only). Pick a stage: the one the user named, otherwise the main flow's next stage; if the user said "parallel", the ready stage of the named flow.
     2. Run the consequence check once per session, listing the stages planned for this session.
     3. Execute each stage as a normal plan (`references/execution.md`). After every DC, update that stage's `PROGRESS.md` and then run `python scripts/flow_status.py BuildPlans/<plan>`. Agents never edit the Status block by hand, and never edit another stage's `PROGRESS.md`. This keeps parallel agents from writing the same lines.
     4. When a stage is MET, continue with the next stage of the same flow, as long as its `Starts after` / `Needs` stages are MET.
   - **Low-context stop:** after every DC (and before starting a new stage), run `python scripts/context_check.py`.
     - If it prints `remaining=<n>` with n ≤ 5, or the tool shows any context-low or usage-limit warning, stop working and ask the user: "Context is at ≤ 5 % remaining. Stop here and save status for the next run? (yes/no)".
     - If the user says yes, or nobody can answer (headless/unattended), write the stage's `PROGRESS.md` with status `PAUSED`, the last finished step, the next step, and a 3-line resume note (what is half done, which files are touched, what to verify first). Then run `flow_status.py` and end the turn.
     - If the user says no, continue, and ask again only after the next DC.
     - If the script prints `remaining=unknown` (e.g. VS Code), the per-DC `PROGRESS.md` updates are the safety net. Before starting each new stage, also write a resume note.
   - **Resume:** read `FLOW.md`, then the `PROGRESS.md` of the stage(s) shown as current. A `PAUSED` stage resumes at its "next step" after its resume note has been checked.
   Verify: file ≤ 4,500 chars; contains `more than 7 stages`, `600`, `15 files`, `main`, `parallel`, `optional`, `Next stage`, `flow_status.py`, `context_check.py`, `PAUSED`, `5 %`, `self-contained`.

7B. **[DC-7] Create `assets/FLOW.template.md`** with the sections above and an example of 3 flows (F1 main: 3 stages; F2 parallel, starts after F1-S01; F3 optional). The Status block is empty between its markers. Also add the stage-related fields to `assets/PROGRESS.template.md`: `Stage: <id>`, `Flow: <id>`, `Status: TODO|IN PROGRESS|PAUSED|MET|NOT MET`, `Next step`, `Resume note`, `Updated: <ISO time>`, and a `Session log` table (`Date | Tool | DCs done | Stopped because`).
   Verify: FLOW template contains both status markers and the words `main`, `parallel`, `optional`, `Starts after`. The four normal templates plus FLOW stay ≤ 3,800 chars together.

7C. **[DC-8] Create `scripts/flow_status.py <plan folder>`** (stdlib only). It:
   - reads `FLOW.md`'s Flows table and every `F*-S*/PROGRESS.md`;
   - computes per flow: done/total, current stage, next stage (the first stage not MET whose `Starts after` / `Needs` are MET), and the list of stages ready now;
   - collects the last 10 session-log rows across stages, sorted by date;
   - replaces **only** the text between the status markers. It writes to a temp file and then renames it, so it never leaves a half-written file, and it retries once if the file changed during the run.
   - exits 1 if the Flows table and the stage folders don't match, naming the missing stage.
   Verify (run after Step 9 has created the fixture): on the T7 fixture, `python running-when-a-request-is-made/scripts/flow_status.py bench/skill-token/fixture/BuildPlans/orders-v2` rewrites the block to show F1 1/3 done and Next stage = F1-S02. A second run gives a byte-identical file (idempotent).

7D. **[DC-8] Create `scripts/statusline_context.py` and `scripts/context_check.py`** (stdlib only).
   - `statusline_context.py` is set as the status-line command in Claude Code (`statusLine` in `~/.claude/settings.json`) and in Copilot CLI (`statusLine` in `~/.copilot/settings.json`; enable it with `/statusline` if needed). It reads the JSON on stdin and computes remaining %:
     - Claude Code: `context_window.remaining_percentage`, else `100 - context_window.used_percentage`;
     - Copilot CLI: `100 - context_window.used_percentage`, else from `current_context_tokens / displayed_context_limit`.
     Missing or null fields count as unknown. It writes `{"remaining": <n|null>, "tool": ..., "updated": <ISO time>}` to `<cwd>/.agent-context.json` and prints a short status line (e.g. `ctx 37% left`).
   - `context_check.py` reads `.agent-context.json` from the repo root and prints `remaining=<n>` or `remaining=unknown`. Unknown covers a missing file or one older than 10 minutes.
   - Add `.agent-context.json` to the repo's `.gitignore` instructions in `staged-plans.md`.
   - Add a 6-line "Setup" note to `staged-plans.md` with the two settings snippets. Say that VS Code agent mode has no status-line hook, so it runs with `remaining=unknown`.
   Verify: `echo {"context_window":{"remaining_percentage":4}} | python scripts/statusline_context.py` writes remaining 4, and `context_check.py` then prints `remaining=4`. The same works with the Copilot shape `{"context_window":{"used_percentage":96}}`. Feeding `{}` gives `remaining=unknown`.

8. **[DC-4] Portability checks.** Create `bench/skill-token/validate_skill.py <skill folder>`. It checks: frontmatter parses, `name` equals the folder name and matches `^[a-z0-9-]{1,64}$`, `description` ≤ 1,024 chars, every relative path mentioned in any `.md` file (`references/…`, `assets/…`, `scripts/…`) exists, the core-size budgets hold, and no absolute paths appear. Run it on both v2 skills. Then do one manual smoke test per surface, in a scratch copy of `bench/skill-token/fixture` with the v2 skills in `.claude/skills/` and `.github/skills/`. The prompt is: "Use the running-when-a-request-is-made skill. Classify this request: 'what does src/orders.py do?'". The check: the agent loads the skill and asks the class C question. Do it in (a) Claude Code, (b) Copilot CLI, (c) VS Code agent mode. Record pass/fail in `bench/skill-token/SMOKE.md`.
   Verify: the validator exits 0 for both skills; `SMOKE.md` shows 3 passes.

9. **[DC-5] Build the benchmark fixture and tasks.**
   - `bench/skill-token/fixture/` (copied to a temp dir and `git init`-ed by the runner on every run):
     - `src/orders.py`: an in-memory `Order` dataclass with `id`, `items: list[tuple[str, int, float]]`, `status`; functions `create_order`, `get_order`, `list_orders`.
     - `src/app.py`: a tiny CLI that calls them.
     - `tests/test_orders.py`: `unittest` tests for the three functions.
     - `CLAUDE.md` and `.github/copilot-instructions.md` with the same 5 rules (PEP 8, type hints, unittest, no new dependencies, tests must pass before done).
     - `CODEOWNERS`: `* @fixture-owner`.
     - `BuildPlans/add-order-total/PLAN.agent.md`: a small approved plan in the v1 agent format. It adds `order_total(order_id) -> float` with 2 DCs and unit tests, and its Map has all answers filled in.
     - `README.md`: 3 lines.
     - `BuildPlans/orders-v2/`: a small **staged** plan in the v2 format (FLOW.md + `F1-S01-add-status-enum/`, `F1-S02-add-order-total/`, `F1-S03-add-cancel-order/`, `F2-S01-docs/` (parallel, starts after F1-S01)). Each stage has 1-2 DCs, both plan files and a PROGRESS.md. F1-S01 is `MET` (and its code change is already applied in `src/orders.py`); the others are `TODO`. Used by T7 and T8.
   - `bench/skill-token/tasks.json`: five tasks. Each one has `id`, `class`, `prompt`, `checks`. Every prompt starts with `Use the running-when-a-request-is-made skill.` and ends with the fixed **non-interactive suffix**: "This is a non-interactive benchmark run. Nobody will answer questions. For every question you would ask, use your suggested default and record it as Source: Assumption. Output format: the standard set."
     - `T1-plan-clear` (A): "Plan adding `cancel_order(order_id)` to src/orders.py: sets status to 'cancelled', raises ValueError for unknown IDs, with unit tests."
     - `T2-plan-vague` (A + IG): "Make order handling better and faster."
     - `T3-plan-docs` (A): "Plan documenting the public API of src/orders.py in docs/orders.md."
     - `T4-execute` (B): "Execute BuildPlans/add-order-total/PLAN.agent.md. The answer to the consequence check is yes."
     - `T5-other` (C): "What does src/orders.py do? Answer to the structured-format question: No."
     - **v2-only feature tasks** (field `"versions": ["v2"]`; quality-checked, tokens reported for information, not part of the 25 % bar):
       - `T6-plan-large` (A, staged): "Plan an orders subsystem for this repo:
         - SQLite persistence with migrations,
         - an HTTP JSON API (stdlib `http.server`) for create/get/list/cancel/total,
         - token auth,
         - a CLI,
         - CSV export,
         - a daily sales report,
         - input validation,
         - structured logging,
         - unit tests for every part,
         - a GitHub Actions CI workflow,
         - API docs,
         - optional: a caching layer and performance tests."

         (This must need more than 7 stages.)
       - `T7-resume` (B, staged): "Continue the plan BuildPlans/orders-v2. The answer to the consequence check is yes. Run at most 2 stages."
       - `T8-low-context` (B, staged): same prompt as T7. The runner writes `.agent-context.json` with `{"remaining": 4}` into the temp repo before the run and makes it read-only, so the agent must hit the low-context stop on its first check.
   Verify: `python -m unittest discover -s bench/skill-token/fixture/tests` passes; `python -c "import json;t=json.load(open('bench/skill-token/tasks.json'));assert len(t)==8"` succeeds; `flow_status.py` on `fixture/BuildPlans/orders-v2` exits 0.

10. **[DC-5] Create the runner, checker and report scripts** (stdlib only):
    - `bench/skill-token/run_bench.py --tool claude|copilot|both --versions v1,v2 --repeats 3`. For each tool × version × task × repeat: copy the fixture to a fresh temp dir, `git init && git add -A && git commit -m base`. Copy the version's two skill folders into `<tmp>/.claude/skills/` (Claude Code) or `<tmp>/.github/skills/` (Copilot). Run the CLI with `cwd=<tmp>` and a 15-minute timeout:
      - Claude Code: `claude -p "<prompt>" --output-format json --model <cfg> --permission-mode bypassPermissions` (runs only inside the throwaway temp dir). Parse the final JSON: `usage.input_tokens`, `usage.output_tokens`, `usage.cache_creation_input_tokens`, `usage.cache_read_input_tokens`, `total_cost_usd`, `num_turns`, `duration_ms`.
      - Copilot CLI: `copilot -p "<prompt>" --output-format json --model <cfg> --allow-all-tools`. Output is JSONL. Sum every event that carries token usage (input / output / cache fields, whatever names the events use). **First, run a probe**: one run of T5 with v1, saved raw to `bench/skill-token/probe-copilot.jsonl`. If no event carries token counts, use the fallback: read the newest session log under `~/.copilot/` (session-state or logs) for that run. If neither gives counts, **stop** (see Stop conditions).
      - `total_tokens` = input + output + cache_creation + cache_read (all input counted, cached or not).
      - Run the checker on `<tmp>`, then append one JSON line per run to `bench/skill-token/results/results.jsonl`: tool, version, task, repeat, model, token fields, total_tokens, cost, turns, duration, quality score, failed checks. Keep the raw CLI output in `results/raw/<tool>-<version>-<task>-<n>.json`.
      - Run the versions **interleaved** (v1, v2, v1, v2, …) to spread time-of-day and service variance evenly.
    - `bench/skill-token/check_outputs.py <tmp> <task id> <version>`. It returns a score from 0-1 (passed checks ÷ total) and the list of failed checks:
      - A tasks: exactly one new folder under `BuildPlans/` (kebab-case) with both plan files. `PLAN.agent.md` has the headings Context, Preconditions, Rules, Steps, DC checklist, Stop conditions, Contacts, Done Criteria, Question Map. Every numbered step has `[DC-` and `Verify:`. Every Question Map row has a non-empty Answer and a Source of `User` or `Assumption`. `git status` shows no changes outside `BuildPlans/`. `PLAN.human.md` has Goal, Scope, Impact, Rules, Contacts, Risks. For **v1** it must also contain a Question Map; for **v2** it must be ≤ 60 lines and link to `PLAN.agent.md`. T2 also needs ≥ 3 Question Map rows.
      - B task: `python -m unittest discover -s tests` passes. `order_total` exists in `src/orders.py`. `BuildPlans/add-order-total/EXECUTION-SUMMARY.md` exists with a DC table containing `MET`.
      - C task: no files changed. The final reply (from the raw output) is non-empty and mentions `order`.
      - T6: a new `BuildPlans/<name>/FLOW.md` exists with the Flows table and status markers, and ≥ 8 stage folders named `F<n>-S<nn>-<kebab>`. There is at least one `parallel` flow and at least one `optional` flow. Every stage folder has both plan files, and every stage `PLAN.agent.md` has ≤ 4 DCs, a non-empty Context, and no `as discussed` / `see other stage` / `same as before`. Every master DC maps to ≥ 1 stage. `flow_status.py` exits 0 on the folder, and its Status block names a Next stage for every flow. No changes outside `BuildPlans/`.
      - T7: F1-S02 (and F1-S03 or F2-S01, if a second stage was run) have PROGRESS `MET`, F1-S01 was not re-run (its PROGRESS is unchanged), tests pass, and FLOW.md's Status block shows the updated counts and the correct Next stage. The Status block equals the output of a fresh `flow_status.py` run, which proves it wasn't hand-edited.
      - T8: no stage moved to `MET`. The stage that was started is `PAUSED` with Next step and Resume note filled, or `TODO` if the stop came before any change. FLOW.md was regenerated, and the reply contains the low-context question or says it stopped because of low context.
    - `bench/skill-token/report.py`: reads `results.jsonl` and writes `bench/skill-token/RESULTS.md`:
      - per tool, per task: min / median / max of total_tokens and output_tokens, for v1 and v2, the change in %, and the median quality score;
      - per tool, the aggregate reduction = 1 − Σ(task medians v2) ÷ Σ(task medians v1);
      - PASS/FAIL against DC-6;
      - the STATIC.md table from Step 2 and the model and CLI versions used.
    Verify: `python bench/skill-token/run_bench.py --tool claude --versions v1 --repeats 1 --tasks T5-other` writes one valid line to results.jsonl with total_tokens > 0, then delete that line. Do the same with `--tool copilot` after the probe.

11. **[DC-6, DC-7, DC-8] Run the full benchmark and report.** Park the user-level skills (see Preconditions). Run `python bench/skill-token/run_bench.py --tool both --versions v1,v2 --repeats 3`: 60 runs for T1-T5 plus 18 v2-only runs for T6-T8. The runner skips v1 for tasks marked v2-only. `report.py` lists T6-T8 in a separate "Feature checks" table, which needs all checks to pass in ≥ 2 of 3 runs per tool. Then run `python bench/skill-token/static_measure.py` on both versions and `python bench/skill-token/report.py`. Restore the parked skills.
    Verify: `RESULTS.md` exists with 78 runs counted. For each tool, the aggregate reduction on T1-T5 is ≥ 25 % and, for each of T1-T5, the v2 median quality ≥ the v1 median quality. The Feature checks table shows T6, T7 and T8 passing in ≥ 2 of 3 runs per tool. The report states PASS for both tools.

12. **[all] Write `BuildPlans/skill-token-optimization/EXECUTION-SUMMARY.md`** (per the v1 Step 4 rules, which still govern this execution) and commit on the branch.
    Verify: `git status` is clean, and the summary lists every file in the Scope below.

## Scope (files)

Modify: `running-when-a-request-is-made/SKILL.md`, `information-gathering-for-plan/SKILL.md`.
Create: `running-when-a-request-is-made/references/planning.md`, `.../references/execution.md`, `.../assets/PLAN.agent.template.md`, `.../assets/PLAN.human.template.md`, `.../assets/PROGRESS.template.md`, `.../assets/EXECUTION-SUMMARY.template.md`, `.../references/staged-plans.md`, `.../assets/FLOW.template.md`, `.../scripts/contacts.py`, `.../scripts/flow_status.py`, `.../scripts/context_check.py`, `.../scripts/statusline_context.py`, `information-gathering-for-plan/references/gather-and-rank.md`, `information-gathering-for-plan/assets/report.template.md`, `bench/skill-token/{static_measure.py, validate_skill.py, run_bench.py, check_outputs.py, report.py, tasks.json, config.json, STATIC.md, SMOKE.md, RESULTS.md, PARKED.md}`, `bench/skill-token/versions/v1/**` (copy), `bench/skill-token/fixture/**` (≈ 20 files, including the staged `BuildPlans/orders-v2/` example), `bench/skill-token/results/**` (generated).
Delete: none.

## DC checklist

- [ ] DC-1: run the Step 1 and Step 2 verify lines; `STATIC.md` has the v1 rows.
- [ ] DC-2: the Steps 3-6 verify lines pass; static class-A load in v2 is ≤ 70 % of v1, class B ≤ 50 %, class C ≤ 25 % (from `STATIC.md`); the v1 → v2 rule-coverage check below passes.
- [ ] DC-3: the Step 7 verify lines pass; static `A+IG` in v2 is ≤ 65 % of v1.
- [ ] DC-4: `validate_skill.py` exits 0 for both skills; `SMOKE.md` shows Claude Code, Copilot CLI and VS Code agent mode passing.
- [ ] DC-5: fixture tests pass; `tasks.json` has 5 tasks; the single-run verify in Step 10 works for both tools.
- [ ] DC-6: `RESULTS.md` says PASS for Claude Code **and** Copilot CLI (≥ 25 % aggregate reduction on T1-T5, no task's median quality lower in v2).
- [ ] DC-7: the Steps 7A and 7B verify lines pass; T6 passes its feature checks in ≥ 2 of 3 runs per tool.
- [ ] DC-8: the Steps 7C and 7D verify lines pass; T7 and T8 pass their feature checks in ≥ 2 of 3 runs per tool; a manual interactive test in Claude Code and in Copilot CLI with the status line installed shows `context_check.py` printing a real number (not `unknown`), recorded in `SMOKE.md`.

**Rule-coverage check (part of DC-2/DC-3):** create `bench/skill-token/RULE-COVERAGE.md`. List every v1 sentence containing `must`, `never`, `always`, `only`, `don't`, `do not`, `stop`, `ask` or `exactly` (case-insensitive) with its v2 file location, or mark it "changed by approved contract (Q-3)". Verify: the row count ≥ the count from `grep -ciE "must|never|always|only|don't|do not|stop|ask|exactly"` over the v1 files, and no row says "missing".

## Stop conditions

- Stop and ask if:
  - a v1 file differs from the sizes in Context by more than 5 % (the skill changed since this plan was written);
  - Copilot CLI exposes no token counts in JSONL **or** in local session logs;
  - the status-line JSON in either tool has none of the context fields named in Step 7D (print one raw payload to check; propose the field the tool actually sends);
  - a stage in T6 can't be kept within 4 DCs / 15 files / 600 lines without breaking a DC apart in a way that loses its meaning;
  - a CLI flag in Step 10 is rejected (check `claude --help` / `copilot --help`; propose the equivalent flag; don't guess);
  - a reference file can't meet its char budget without dropping a v1 rule;
  - DC-6 fails. Don't tune prompts or tasks to pass. Report the numbers and propose which lever to change.
- Never run `bypassPermissions` / `--allow-all-tools` outside the temp fixture copy.
- Don't change the benchmark tasks, the non-interactive suffix or the models between v1 and v2 runs.

## Contacts

- No `CODEOWNERS` was found for the skills repo. The owner and reviewer is the user (skill author).
- Needs owner review: **yes**. The change touches more than 10 files and changes the skill's output contract (a "public" contract for any agent that consumes these plans).

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | v1 of both skills is preserved unchanged under `bench/skill-token/versions/v1/`, and its static load per class (A, A+IG, B, C) is measured in `STATIC.md` | Original |
| DC-2 | `running-when-a-request-is-made` v2.1: planning steps and output layouts in `SKILL.md` (0 extra reads for plan requests), execution and staged plans one reference each, turn-aware context rules, every v1 rule kept or mapped to an approved contract change, `PLAN.human.md` ≤ 60 lines with the Map only in `PLAN.agent.md`; static size is reported for information (revised from: v2.0 progressive-disclosure layout with per-class static targets) | Revised via Q-3, Q-25 |
| DC-3 | `information-gathering-for-plan` v2.1 is one file again (no extra reads when gathering is needed); static size reported for information (revised from: split core + reference) | Revised via Q-25 |
| DC-4 | Both v2 skills are valid Agent Skills that load and route correctly in Claude Code, Copilot CLI and VS Code agent mode | Original |
| DC-5 | A reproducible benchmark exists: fixed fixture repo, 5 tasks covering classes A, A+IG, B, C, a runner for both CLIs, a quality checker and a report | Original |
| DC-7 | The planner writes a **staged plan** when more than 7 stages are needed: stage = one sub-plan folder (≤ 4 DCs, ≤ 15 files, ≤ 600 changed lines; sized so ≥ 7 stages fit one 5-hour session), grouped into main / parallel / optional flows, with one master `FLOW.md` showing each flow's stages, progress, next stage and which flows run in parallel; every stage plan is self-contained (integrity before compression) | Added via Q-14, Q-15 |
| DC-8 | Executing agents record status per stage in `PROGRESS.md` after every DC; `flow_status.py` rebuilds FLOW.md so a later agent continues correctly; when context remaining is ≤ 5 % the agent asks whether to stop (stops by itself when unattended) and saves PAUSED status with a resume note | Added via Q-16, Q-17 |
| DC-6 | On the same tasks T1-T5 × 3 repeats in **Claude Code**, v2.1 has median turns ≤ v1, median `cost_usd` ≤ v1 and median quality ≥ v1 on **every** task; `/usage` is noted before/after each batch; total tokens reported for information (revised from: "≥ 25 % fewer total tokens in both Claude Code and Copilot CLI") | Revised via Q-23, Q-24 |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | all | Must | What output format should this plan use? | Standard BuildPlans set (PLAN.human.md + PLAN.agent.md) | User |
| Q-2 | DC-6 | Should | What counts as proven improvement? | ≥ 25 % fewer median total tokens per tool, no quality drop | User |
| Q-3 | DC-2 | Should | May the skill's output contract change? | Yes: human plan ≤ 60 lines and links to the Map, which lives only in PLAN.agent.md | User |
| Q-4 | DC-5 | Should | How are the benchmark runs executed? | Headless `claude -p` and `copilot -p` on the user's PC, 3 repeats, plus a static count | User |
| Q-5 | DC-2 | Could | Build a separate standalone memory skill? | No: context-budget rules live in the core SKILL.md of the existing skill; nothing new to install | Assumption |
| Q-6 | DC-3 | Could | Include `information-gathering-for-plan` in scope? | Yes: it is loaded inside Step 1, so it counts toward class A cost | Assumption |
| Q-7 | all | Could | Where do the skills live? | In `SKILLS_ROOT`; the plan and bench live under it | Assumption |
| Q-8 | DC-5 | Could | Fixture tech stack? | Python stdlib + unittest (zero installs, same on Windows/Linux) | Assumption |
| Q-9 | DC-5, DC-6 | Could | Repeats, model choice, run order? | 3 repeats, one fixed model per tool, v1/v2 interleaved | Assumption |
| Q-10 | DC-4 | Could | How is VS Code agent mode covered? | Manual smoke test only (no headless runner); Copilot CLI carries the token benchmark | Assumption |
| Q-11 | DC-2 | Could | Shorten the execution-summary reply? | Yes: reply shows the DC table + link; the full summary is in the file | Assumption |
| Q-12 | DC-1 | Would | How to count static tokens? | chars ÷ 4, plus exact count-tokens API when `ANTHROPIC_API_KEY` is set | Assumption |
| Q-13 | DC-5 | Could | How do headless runs handle questions? | A fixed non-interactive suffix makes every question use its default (Source: Assumption), identical for v1 and v2 | Assumption |
| Q-14 | DC-7 | Must | How do stage and sub-plan folder relate? | 1 stage = 1 sub-plan folder; flows are ordered stage lists; ≥ 7 stages should fit one 5-hour session | User |
| Q-15 | DC-7 | Must | What sizing rule splits a plan? | Stage ≤ 4 DCs, ≤ 15 files changed, ≤ 600 changed lines; split into flows when more than 7 stages are needed, to keep context integrity | User |
| Q-16 | DC-8 | Must | Which signal triggers the 5 % stop? | Context window ≤ 5 % remaining (via the status-line context file), plus any context-low / usage-limit warning; per-DC checkpoint as fallback | User |
| Q-17 | DC-8 | Should | How are parallel FLOW.md writes kept safe? | Each stage writes only its own PROGRESS.md; `flow_status.py` rebuilds the FLOW.md status block | User |
| Q-18 | DC-7, DC-8 | Could | Do the staged-plan features join the 25 % token bar? | No: T6-T8 are v2-only quality checks (v1 has no such feature); their tokens are reported for information | Assumption |
| Q-19 | DC-8 | Could | How often is the consequence check asked in flow runs? | Once per session, listing every stage planned for that session | Assumption |
| Q-20 | DC-8 | Could | What happens at ≤ 5 % with nobody to answer? | Stop, save PAUSED + resume note, regenerate FLOW.md | Assumption |
| Q-21 | DC-7 | Could | Where does the staged plan's master DC & Question Map live? | In FLOW.md; stage plans hold stage-local DCs mapped to master DCs | Assumption |
| Q-22 | DC-8 | Could | What if the tool has no status-line hook (VS Code agent mode)? | `remaining=unknown`; rely on per-DC PROGRESS updates plus a resume note before each new stage | Assumption |
| Q-23 | DC-6 | Must | What should the pass bar measure, given a monthly subscription? | Turns and `cost_usd` (price-weighted estimate) per task ≤ v1, quality not lower; `/usage` before/after each batch as the real-plan check; total tokens for information | User |
| Q-24 | DC-6 | Must | Which tools are benchmarked? | Claude Code only (no paid Copilot account); the skill stays Copilot-compatible | User |
| Q-25 | DC-2, DC-3 | Should | Keep the per-class static size targets? | No: v2.0 met size goals but doubled turns; static size is reported for information only | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
| 2026-11-24 | Plan created | - |
| 2026-11-24 | v2.0 benchmark on Claude Code: −13.4 % "reduction" (more tokens), turns doubled on plan requests (T1 7.3 → 14.3, T2 6.0 → 14.7), cost +17 % / +8 %. Built v2.1: planning + layouts back in SKILL.md, turn-aware context rules, IG one file, v2.0 snapshot kept; pass bar → turns + cost, Claude Code only | User (Q-23, Q-24) |
| 2026-11-24 | Added staged plans (FLOW.md, flows, stage sub-plans), per-stage status sync, low-context stop, integrity-before-compression rule; DC-7, DC-8, Steps 7A-7D, tasks T6-T8 | User (Q-14 … Q-17) |
