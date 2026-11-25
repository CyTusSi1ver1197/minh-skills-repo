# Fit the request skills to GPT-6 Luna, Astra and GPT-6.1/6.2 Sol (v2.2)
**Goal:** Make `running-when-a-request-is-made` and `information-gathering-for-plan` work well on OpenAI's GPT-6 family in GitHub Copilot, with one shared copy that still works on Claude.
Check the result with a benchmark on GPT-6 Luna and GPT-6.1 Sol.
**Status:** Draft - awaiting review

## Scope
- Area: the benchmark under `bench/skill-token/`.
- The live skill folders (`*-v2.1/`) and `versions/v2.0/` are not changed.
- `bench/skill-token/versions/v2.1/` (create): a complete copy of the current skills, every `.md` and `.py` file, kept as the old version.
- `bench/skill-token/versions/v2.2/` (create): a copy of `versions/v2.1/`. Every change below is made in this copy only.
- `running-when-a-request-is-made/SKILL.md` (modify, in v2.2):
  - The description now says when to use the skill.
  - The class C format question is gone: Claude answers normally and adds a one-line "say 'plan it'" hint.
  - New "Working rules" section:
    - your instructions override the skill;
    - when Claude pauses on a rule, it quotes the rule;
    - it stops only at the named gates;
    - it reports every blocker;
    - it keeps executing through all DCs.
- `running-when-a-request-is-made/references/execution.md` (modify):
  - It runs only the checks the change needs, and adds tests only when asked or required.
  - The references to skills that don't exist are removed.
  - `EXECUTION-SUMMARY.md` gets a `## Blockers` section.
  - The context check is skipped after it returns `unknown`.
- `running-when-a-request-is-made/references/staged-plans.md` (modify): the duplicate context-check rule now points to execution.md.
- `information-gathering-for-plan/SKILL.md` (modify): the description now says when to use the skill.
- `bench/skill-token/report.py` (modify): a `--model` filter, and Copilot runs are compared on total tokens.
- `bench/skill-token/RESULTS-gpt6-luna.md` and `RESULTS-gpt61-sol.md` (create): benchmark results.

## Impact
- **Functional:**
  - Non-plan requests no longer get a format question.
  - The questions that still stop work are: Must questions, every conflict, the execution yes/no check, and irreversible actions.
  - Tests run less often.
  - Blockers always show up in the reply and in the summary.
  - Plan, progress and summary layouts are unchanged, apart from the new Blockers section.
- **Non-functional:**
  - Fewer stalled or over-asking runs on Astra, and fewer extra test runs.
  - Skill size grows by no more than 5 %.
  - Claude behaviour should not change, because the edits are wording only.

## Rules
- Each skill must pass the portability check: name matches folder, description ≤ 1,024 chars, no absolute paths (source: `bench/skill-token/validate_skill.py`).
- Plan and summary layouts stay unchanged, because the benchmark scores them (source: `bench/skill-token/check_outputs.py`).
- Rule 8 of the skill: never drop a DC, a Verify line, a stop condition or an assumption (source: `SKILL.md`).

## Contacts
- Owner: you. There is no CODEOWNERS file and no git history.
- Needs owner review: no. The change is about 60 lines across 9 files, with no API, schema, auth or CI changes.

## Risks, trade-offs & assumptions
- **Claude is not re-benchmarked** because of token limits. Risk: a Claude regression would go unseen until the next Claude bench run.
- **Astra and 6.2 Sol are not benchmarked.** Most of the changes target Astra's documented habits (over-asking, over-testing, stopping early). The gain is inferred from OpenAI's guidance, not measured.
- **The root SKILL.md stays large.** OpenAI suggests a small router, but v2.0's split doubled turns, so the inlined v2.1 layout stays.
- **Copilot CLI has no turn or cost data**, so the comparison uses total tokens with a ±10 % tie band for single runs. This is weak evidence.
- **Copilot CLI has never produced benchmark rows.** A probe run comes first; if it records 0 tokens, work stops there.
- The Luna advice is third-party only, because OpenAI has no Luna prompting guide.
- The GPT model ids in Copilot may differ from the API ids (`gpt-6-luna`, `gpt-6.1-sol`). Confirm them on the logged-in PC.

Done criteria and question map: [PLAN.agent.md](PLAN.agent.md#done-criteria)
