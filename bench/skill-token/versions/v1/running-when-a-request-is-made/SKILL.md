---
name: "running-when-a-request-is-made"
description: "Align on a work request before doing it - done criteria (DC), given data (GD), MoSCoW-ranked questions - then write a BuildPlans plan (human + agent versions) or execute an approved plan with DC-by-DC verification."
---

# Running when a request is made

Goal: **consistent inputs → consistent agent → consistent outputs.**
The user and the agent must agree on *what done looks like* and *what data is
available* before any work starts, so the same request always produces the same
kind of result, by any agent.

Vocabulary used throughout:

- **DC** - Done Criteria. Testable conditions that mean the request is finished. IDs: `DC-1`, `DC-2`, ...
- **GD** - Given Data. Everything supplied or discoverable: files, repo, specs, rules, constraints, examples. IDs: `GD-1`, `GD-2`, ...
- **Q** - Clarifying question, always mapped to a DC. IDs: `Q-1`, `Q-2`, ...

---

## Step 0 - Classify the request

| Class | Signal | Go to |
|---|---|---|
| **A. Plan** | User wants something new created or changed (code, report, documentation, ...) and no approved plan exists yet | Step 1 → Step 2 → Step 3 |
| **B. Execute** | User points to an existing plan (`BuildPlans/.../PLAN.agent.md`) or says "execute / run the plan" | Step 4 |
| **C. Other** | Anything else | Ask once (below) |

For class C, ask exactly once per conversation:

> "Do you want this request to follow the structured format (consistent inputs → consistent agent → consistent outputs: done criteria, clarifying questions, then a plan)? Or should I just handle it normally?"

- **Yes** → gather information to fit the format: treat it as class A.
- **No** → handle it as a normal request and ignore the rest of this skill for this request. Keep that answer for the rest of the conversation unless the user changes it.

---

## Step 1 - Inputs: DC and GD

1. **Extract the DC.** Rewrite the request as a numbered list of testable conditions. Each one should be checkable by someone who did not see the conversation (e.g. "`POST /api/orders` returns 201 with the created order", not "orders work").
2. **Extract the GD.** List what you were given and what you can read yourself: repo files, project rules (`CLAUDE.md`, `.github/copilot-instructions.md`, `CONTRIBUTING.md`, `.editorconfig`, linter configs), specs, attachments. Read the code before asking about it.
3. **Challenge a DC** and raise it as a question when it:
   - conflicts with the coding standard or the project rules;
   - creates a bottleneck (performance, scaling, tight coupling, a blocking dependency, a manual step that defeats automation);
   - looks like it was written without the full picture (contradictory, vague, states a solution instead of the problem, ignores obvious edge cases or existing behaviour).
   Once answered, record the result as a revised or new DC. Keep the original wording too: `DC-3 (revised from: ...)`.
4. **Gap check.** For each DC, ask: *is the GD enough to reach this state?* Each "no" becomes a question.
   **If the GD or DC are unclear, vague, missing or conflicting, run the `information-gathering-for-plan` skill here.** It gathers from the knowledge base and retrieval tools, resolves every conflict with the user, and ranks questions in four tiers (Most Relevant → Most Effective → Frequencies of Effective → Relevant Extensions), capped at 10 missing and 6 additional. Its rules replace items 5-6 below for those questions. MoSCoW still decides ask vs assume, and every assumed answer is reported. Its Question Map rows go into this plan's Question Map.
5. **Rank every question with MoSCoW:**

   | Rank | Meaning | Handling |
   |---|---|---|
   | **Must** | A DC cannot be met, or would be built wrong, without this answer | Ask |
   | **Should** | A wrong guess is likely and costly to redo | Ask |
   | **Could** | A detail with a safe, conventional default | Assume, record the assumption |
   | **Would** | Nice-to-have or out of scope for now | Assume, record the assumption |

6. **Ask all Must and Should questions in one batch.** Each one carries its ID, the DC it serves and a suggested default, so the user can answer "defaults are fine". Use a multiple-choice question tool when one is available. If the output format is not specified, add the Step 2 question to this same batch. Don't send it as a separate round trip.
7. **Don't leave Step 1 while any Must is unanswered.** If the user declines a Should, record your best assumption and flag it as a risk.
8. **Every question ends up with an answer**, either from the user (`Source: User`) or assumed (`Source: Assumption`). These answers go into the Question Map (see Templates).

---

## Step 2 - Outputs

- **The user specified the output** (any format: `.md`, `.pdf`, `.xlsx`, `.pptx`, `.docx`, media, ...) → produce exactly that. If it is a plan, still include the DC/Question Map in it.
- **The user did not specify the output** → ask (inside the Step 1 batch):
  > "No output format was given. Should I use the standard set - a build plan as two markdown files (one for you to review, one for an agent to execute) in `BuildPlans/<plan-name>/` - or do you want something else?"
  - Standard set → Step 3 (class A) or Step 4 (class B).
  - Something else → use what they name.

---

## Step 3 - Planning phase (class A, standard outputs)

Planning **does not change the codebase**. It only writes the plan files.

### Folder layout

```
BuildPlans/
└── [optional grouping folders, e.g. sprint-12/ or feature-auth/ ...]
    └── <plan-name>/              # kebab-case, e.g. add-order-endpoint
        ├── PLAN.human.md         # for the user to review and approve
        ├── PLAN.agent.md         # for an agent to execute
        └── assets/               # any other media/output for this plan (optional)
```

Every plan output lives in its own plan folder, and every plan folder sits somewhere under `BuildPlans/`. If the user wants grouping by sprint, feature or anything else, add those folders between `BuildPlans/` and the plan folder, never outside it.

### Required content (both files)

1. **Scope** - which part of the codebase changes (module/layer/project), and the list of files that will be **created, modified or deleted**. List only files that change.
2. **Impact**
   - *Functional:* behaviour that changes for users, APIs, data, other modules and callers.
   - *Non-functional:* performance, security, reliability, maintainability, compatibility/breaking changes, deployment/config, cost.
3. **Rules** - the project rules this change must follow, with their source file. If no rules were given or found, write "No project rules given".
4. **Contacts** - who to involve if the change is too large to handle alone. Find owners from `CODEOWNERS` first. Otherwise use the top committers of each changed file:
   `git log --format='%an <%ae>' -- <file> | sort | uniq -c | sort -rn | head -3`
   Mark the change **"needs owner review"** when it touches more than 10 files, roughly 400+ changed lines, a public API contract, the DB schema/migrations, auth/security, or CI/CD.
5. **DC & Question Map** - at the **end** of the plan: every DC, and every question mapped to its DC with its MoSCoW rank and answer. No blank answers.

### PLAN.human.md - written for review

Short and readable: the goal in two lines, then Scope, Impact, Rules, Contacts, the main risks and trade-offs, the assumptions you made, and the Map. It must answer *"is this the right plan?"* without reading any code.

### PLAN.agent.md - written for execution

Must be executable by any capable coding agent (any vendor, medium reasoning effort) **without the conversation**:

- Self-contained: repeat the needed context; never write "as discussed".
- Exact paths, the exact action per file (create / modify / delete), and the intended change described concretely (signatures, names, behaviour).
- Numbered, ordered steps. Each step lists the DC(s) it serves and a **verify** line (a command to run or an observable check).
- Preconditions (branch, tools, env), the Rules, and **stop conditions**: when to halt and ask instead of improvising.
- A DC checklist that says how to verify each DC.

End your reply with:
> "Review `BuildPlans/.../PLAN.human.md`. When it meets the requirements, ask me (or any agent) to execute `BuildPlans/.../PLAN.agent.md`."

---

## Step 4 - Execution phase (class B)

1. **Load the plan.** Read `PLAN.agent.md`. Confirm it contains both GD and DC. If either is missing, stop and go back to Step 1 for the missing part.
2. **Consequence check (once).** Send one message listing the files that will change, the functional and non-functional impact, and any rule the change will conflict with. Ask:
   > "Do you understand these consequences and want me to run the execution? (yes/no)"
   Only an explicit **yes** continues. Anything else → stop.
3. **GD sufficiency.** If the GD is not enough to build every DC, ask the missing Must/Should questions (Step 1 rules) before touching code.
4. **Checklist.** Make a checklist with one item per DC (use the task-list tool if one exists).
5. **Build and verify DC by DC.**
   - Implement the plan steps for the current DC.
   - Then start a **verifier sub-agent asynchronously** (in the background where supported). Give it only the DC text, the relevant plan steps and the diff, and ask: *"Is this DC met? Answer MET / NOT MET with evidence."* Move on to the next DC while it runs.
   - If no sub-agent tool exists (some Copilot or chat environments), verify each DC yourself in a separate pass after building: re-read the diff fresh and run the plan's verify commands.
6. **All checks must pass.** If one or a few DCs cannot be met as written, don't force them and don't quietly change them. Stop on those DCs, explain why, propose a revised DC, and ask the user. Record the approved changes in the plan's Map under a `Revision log`.
7. **Rules check after changes.** Run whatever the project has: format/lint, build, unit tests, integration/connectivity tests, plus checks for the plan's Rules. Fix failures that are within scope. Report the ones that are not. For tests, use the testing skills: if the project rules require tests to verify changes, build and run **unit tests only** with the unit-tests skill. Build integration or performance tests (integration-tests, performance-tests skills) only when the user explicitly asked for them, and ask before running them.
8. **Summary before closing.** Print it in the reply **and** save it as `EXECUTION-SUMMARY.md` in the plan folder:
   - files created / modified / deleted, with the idea of each change (one line each);
   - DC status table (MET / NOT MET / REVISED);
   - rule and test results;
   - assumptions used and deviations from the plan.
   Ask the user to verify.

---

## Templates

### DC & Question Map (end of every plan)

```markdown
## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | ... | Original |
| DC-2 | ... (revised from: "...") | Revised via Q-3 |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-1 | Must | ... | ... | User |
| Q-2 | DC-2 | Could | ... | ... | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
```

### PLAN.human.md

```markdown
# <Plan title>
**Goal:** <two lines>
**Status:** Draft - awaiting review

## Scope
- Area: ...
- Files: `path/a.cs` (modify), `path/b.tsx` (create)

## Impact
- Functional: ...
- Non-functional: ...

## Rules
- ... (source: CONTRIBUTING.md)

## Contacts
- `path/a.cs` → Name <email> (CODEOWNERS)
- Needs owner review: yes/no - why

## Risks & assumptions
- ...

<DC & Question Map>
```

### PLAN.agent.md

```markdown
# EXECUTION PLAN: <plan-name>
## Context
<everything an agent needs to know, self-contained>

## Preconditions
- Branch / tools / env vars

## Rules
- ...

## Steps
1. [DC-1] Modify `path/a.cs`: <exact change>.
   Verify: `dotnet test --filter OrderTests`
2. [DC-2] Create `path/b.tsx`: <exact component, props, behaviour>.
   Verify: `npm run test -- b`

## DC checklist
- [ ] DC-1 - verify by: ...
- [ ] DC-2 - verify by: ...

## Stop conditions
- Stop and ask if: <file differs from what the plan expects, a test outside scope fails, a rule conflict appears, ...>

## Contacts
- ...

<DC & Question Map>
```