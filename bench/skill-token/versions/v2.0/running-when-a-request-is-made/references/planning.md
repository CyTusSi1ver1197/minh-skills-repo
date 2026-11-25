# Planning (class A): Steps 1-3

## Step 1 - Inputs: DC and GD

1. **Extract the DC:** numbered, testable conditions a stranger to the conversation can check ("`POST /api/orders` returns 201", not "orders work").
2. **Extract the GD:** what you were given plus what you can read: repo files, project rules (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `CONTRIBUTING.md`, `.editorconfig`, linter configs), specs, attachments. Read the code before asking about it, under the Context budget rules in `SKILL.md`. One line per item: `GD-n | source | what it gives`.
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
4. **Contacts:** run `python <skill>/scripts/contacts.py <changed files...>` from the repo root. If Python is unavailable, use CODEOWNERS, else `git log --format='%an <%ae>' -- <file> | sort | uniq -c | sort -rn | head -3`. Mark **"needs owner review"** when the change touches more than 10 files, roughly 400+ changed lines, a public API contract, the DB schema/migrations, auth/security, or CI/CD.
5. **DC & Question Map** at the end of `PLAN.agent.md`: every DC, and every question with its DC, MoSCoW rank and answer. No blank answers.

Start from `assets/PLAN.agent.template.md` and `assets/PLAN.human.template.md`.
- `PLAN.human.md`: at most 60 lines. Goal (2 lines), Scope, Impact, Rules, Contacts, Risks, trade-offs & assumptions, then a link to `PLAN.agent.md#done-criteria` instead of repeating the Map. It must answer *"is this the right plan?"* without reading code.
- `PLAN.agent.md`: executable by any capable agent at medium effort **without the conversation**: self-contained (never "as discussed"), exact paths and action per file, concrete changes (signatures, names, behaviour), numbered steps each with DC(s) and a **Verify** line, preconditions, Rules, **stop conditions**, DC checklist.

After drafting, compress only by removing repetition and boilerplate. Integrity before size (rule 7).

End your reply with:
> "Review `BuildPlans/.../PLAN.human.md`. When it meets the requirements, ask me (or any agent) to execute `BuildPlans/.../PLAN.agent.md`."
