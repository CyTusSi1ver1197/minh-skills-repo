---
name: "running-when-a-request-is-made"
description: "Align on a work request before doing it - done criteria (DC), given data (GD), MoSCoW-ranked questions - then write a BuildPlans plan (human + agent versions) or execute an approved plan with DC-by-DC verification."
---

# Running when a request is made

Goal: **consistent inputs → consistent agent → consistent outputs.** Agree on *what done looks like* and *what data is available* before any work starts.

Vocabulary: **DC-n** Done Criteria (testable "finished" conditions) · **GD-n** Given Data (supplied or discoverable inputs) · **Q-n** clarifying question, always mapped to a DC · **Stage** one sub-plan folder of a staged plan · **Flow** an ordered list of stages (main / parallel / optional).

## Context budget (always on)

Every step (tool call) re-sends the whole conversation, so **fewer steps** saves the most.
1. **Batch:** put independent reads, searches and commands in one step (parallel tool calls, or one shell command).
2. Read files under 300 lines whole, together in one step. Search first only in large files or large folders; read large files in sections. Don't re-read a file already in context unless it changed.
3. Delegate discovery to a sub-agent (Claude Code: Explore/Task; Copilot: its sub-agent / `runSubagent` tool) only when it would take many reads; ask for a ≤ 30-line summary with `file:line` evidence.
4. Keep tool output small: filter command output (failures only, `tail`, `--quiet`, counts).
5. Write each file complete in one call. Edit afterwards only to fix a real error.
6. State lives in files, not in chat: the plan in `BuildPlans/<plan-name>/`, execution progress in its `PROGRESS.md`. After compaction or resume, re-read only those.
7. Replies summarize and link. Don't repeat file contents in chat.
8. Integrity before size: never compress away a DC, a Verify line, an exact path or signature, a rule and its source, a stop condition, an assumption, or the context a plan or stage needs to run alone.

## Step 0 - Classify the request

| Class | Signal | Go to |
|---|---|---|
| **A. Plan** | Something new created or changed, no approved plan yet | Steps 1-3 below |
| **B. Execute** | Points to `BuildPlans/.../PLAN.agent.md` or `BuildPlans/<plan>/FLOW.md`, or says "execute / run / continue the plan" | Read `references/execution.md`; for a FLOW.md also `references/staged-plans.md` (one step) |
| **C. Other** | Anything else | Ask once (below) |

`references/` and `scripts/` are in this skill's folder (`<skill>`). Read a reference only when its class applies, once per conversation.

For class C, ask exactly once per conversation:

> "Do you want this request to follow the structured format (consistent inputs → consistent agent → consistent outputs: done criteria, clarifying questions, then a plan)? Or should I just handle it normally?"

- **Yes** → treat it as class A.
- **No** → handle it normally and ignore the rest of this skill for this request. Keep that answer for the conversation unless the user changes it.

## Step 1 - Inputs: DC and GD

1. **Extract the DC:** numbered, testable conditions a stranger to the conversation can check ("`POST /api/orders` returns 201", not "orders work").
2. **Extract the GD:** what you were given plus what you can read: repo files, project rules (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `CONTRIBUTING.md`, `.editorconfig`, linter configs, `CODEOWNERS`), specs, attachments. Read the code before asking about it: list the repo once, then read the relevant files in one batched step. One line per item: `GD-n | source | what it gives`.
3. **Challenge a DC** (as a question) when it conflicts with the coding standard or project rules; creates a bottleneck (performance, scaling, coupling, blocking dependency, a manual step that defeats automation); or looks written without the full picture (contradictory, vague, a solution instead of the problem, ignores edge cases or existing behaviour). Record the result as a revised or new DC: `DC-3 (revised from: ...)`.
4. **Gap check:** for each DC, is the GD enough to reach it? Each "no" is a question. **If the GD or DC are unclear, vague, missing or conflicting, run the `information-gathering-for-plan` skill here** (four tiers, capped at 10 missing and 6 additional; its rules replace items 5-6 for those questions). MoSCoW still decides ask vs assume, every assumed answer is reported, and its Map rows join this plan's Map.
5. **Rank every question with MoSCoW:**

   | Rank | Meaning | Handling |
   |---|---|---|
   | **Must** | A DC cannot be met, or would be built wrong, without this answer | Ask |
   | **Should** | A wrong guess is likely and costly to redo | Ask |
   | **Could** | A detail with a safe, conventional default | Assume, record the assumption |
   | **Would** | Nice-to-have or out of scope for now | Assume, record the assumption |

6. **Ask all Must and Should questions in one batch**, each with ID, DC and a suggested default ("defaults are fine" works). Use a multiple-choice tool if one exists. Include the Step 2 question.
7. Don't leave Step 1 while any Must is unanswered. If the user declines a Should, record your best assumption and flag it as a risk.
8. Every question gets an answer (`Source: User` or `Source: Assumption`) in the Question Map.

## Step 2 - Outputs

- **Output specified** (any format) → produce exactly that; a plan still includes the DC/Question Map.
- **Not specified** → ask (in the Step 1 batch):
  > "No output format was given. Should I use the standard set - a build plan as two markdown files (one for you to review, one for an agent to execute) in `BuildPlans/<plan-name>/` - or do you want something else?"
  Standard set → Step 3 (or Step 4 to execute). Something else → use what they name.

## Step 3 - Planning phase (standard outputs)

Planning **does not change the codebase**. It only writes `BuildPlans/[optional grouping/]<plan-name>/{PLAN.human.md, PLAN.agent.md, assets/}` (kebab-case name; grouping folders only inside `BuildPlans/`).

**Size check first:** group the DCs into stages of ≤ 4 DCs, ≤ 15 files changed and ≤ 600 changed lines. If the plan needs more than 7 stages, read `references/staged-plans.md` and write a staged plan. Otherwise write one normal plan.

Every plan contains:
1. **Scope:** the area that changes, and only the files created / modified / deleted.
2. **Impact:** functional (users, APIs, data, callers); non-functional (performance, security, reliability, maintainability, compatibility, deployment, cost).
3. **Rules** with their source file, or "No project rules given".
4. **Contacts:** if `CODEOWNERS` (root, `.github/`, `docs/`) covers the files, use it. Otherwise, in the same step as other lookups, run `python <skill>/scripts/contacts.py <changed files...>` (no Python: `git log --format='%an <%ae>' -- <file> | sort | uniq -c | sort -rn | head -3`). Mark **"needs owner review"** when the change touches more than 10 files, roughly 400+ changed lines, a public API contract, the DB schema/migrations, auth/security, or CI/CD.
5. **DC & Question Map** at the end of `PLAN.agent.md`: every DC, and every question with its DC, MoSCoW rank and answer. No blank answers.

Write both files in one step, each complete in one call:

- **`PLAN.agent.md`**, executable by any capable agent at medium effort **without the conversation**: self-contained (never "as discussed"), exact paths and action per file, concrete changes (signatures, names, behaviour). Sections in this order:
  `# EXECUTION PLAN: <plan-name>` · `## Context` · `## Preconditions` (branch / tools / env) · `## Rules` (`- <rule> (source: <file>)`) · `## Steps` (`1. [DC-1] <Create|Modify|Delete> \`path\`: <exact change>.` then `   Verify: \`<command or check>\``) · `## DC checklist` (`- [ ] DC-1 - verify by: ...`) · `## Stop conditions` (`- Stop and ask if: ...`) · `## Contacts` (owner + needs owner review: yes/no - why) · `## Done Criteria` (`| ID | Done criterion | Status |`, status Original / Revised via Q-n) · `## Question Map` (`| Q | DC | MoSCoW | Question | Answer | Source |`) · `## Revision log` (`| Date | Change | Approved by |`).
- **`PLAN.human.md`**, at most 60 lines, answers *"is this the right plan?"* without reading code: `# <title>` · `**Goal:**` (2 lines) · `**Status:** Draft - awaiting review` · `## Scope` (area + files with action) · `## Impact` (functional / non-functional) · `## Rules` · `## Contacts` · `## Risks, trade-offs & assumptions` · last line `Done criteria and question map: [PLAN.agent.md](PLAN.agent.md#done-criteria)` (don't repeat the Map).

Compress only by removing repetition and boilerplate (rule 8).

End your reply with:
> "Review `BuildPlans/.../PLAN.human.md`. When it meets the requirements, ask me (or any agent) to execute `BuildPlans/.../PLAN.agent.md`."
