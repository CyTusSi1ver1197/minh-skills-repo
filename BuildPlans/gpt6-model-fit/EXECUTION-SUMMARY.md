# Execution summary: gpt6-model-fit

## Files changed
- `bench/skill-token/versions/v2.1/` (create): a complete copy of the live v2.1 skills: 2× SKILL.md, 2 references, 4 scripts. Identical to the live files (`diff -r` empty).
- `bench/skill-token/versions/v2.2/` (create): a copy of v2.1. Only these 4 files were edited:
  - `running-when-a-request-is-made/SKILL.md` (modify):
    - "Use when" description.
    - Class C now answers normally and adds a "plan it" hint.
    - New "Working rules" section: user precedence and quoting the rule, stop only at the named gates, report blockers, continue through all DCs.
    - Trims to stay within the 9,000-char budget: Goal second sentence dropped, Stage/Flow definitions now point to `references/staged-plans.md`, sub-agent tool names dropped from rule 3.
  - `running-when-a-request-is-made/references/execution.md` (modify):
    - Proportionate checks in step 7, and the references to missing skills removed.
    - `## Blockers` added to the summary in step 8.
    - The context check is skipped after `remaining=unknown` in step 5.
  - `running-when-a-request-is-made/references/staged-plans.md` (modify): the context-check rule points to execution.md step 5, and the duplicate `unknown` rule is gone.
  - `information-gathering-for-plan/SKILL.md` (modify): "Use when" description.
- `bench/skill-token/report.py` (modify): a `--model` filter, plus a Copilot pass rule (median total_tokens ≤ 110 % of baseline).
- Not touched: the live `*-v2.1/` folders, `versions/v1/`, `versions/v2.0/`, `RESULTS.md`.

## DC status
| DC | Status (MET / NOT MET / REVISED) | Evidence |
|---|---|---|
| DC-1 | MET | `grep -c '^description: "Use when'` = 1 per file; lengths 219 and 208; `validate_skill.py` 2× PASS |
| DC-2 | MET (text); run check pending | "ask exactly once" is gone and the "plan it" line is present. T5 reply check waits on Step 10 |
| DC-3 | MET (text); run check pending | `grep` for unit-tests, integration-tests and performance-tests finds nothing. T4 `tests pass` waits on Step 10 |
| DC-4 | MET | The old "After every DC…" line is gone; `remaining=unknown` skip appears in execution.md |
| DC-5 | MET (text); run check pending | `## Working rules` is at SKILL.md line 24 and `## Blockers` is in execution.md step 8. T4 summary check waits on Step 10 |
| DC-6 | MET | Static chars, v2.1 → v2.2: A 8,830 → 8,996 (+1.9 %); A+IG 16,423 → 16,519 (+0.6 %); B 12,409 → 12,916 (+4.1 %); B-staged 17,473 → 17,992 (+3.0 %) |
| DC-7 | NOT MET | The 16 Copilot runs (Steps 10-11) have not been done |
| DC-8 | MET | `diff -r` live vs `versions/v2.1` is empty; `diff -rq v2.1 v2.2` lists only the 4 planned files |

## Rule & test results
- `validate_skill.py`:
  - v2.1: 2× PASS.
  - v2.2: 2× PASS after trimming. The first pass failed with `SKILL.md is 9358 chars > budget 9000`.
- `report.py`:
  - Claude output is byte-identical to the current `RESULTS.md`, with and without `--model sonnet`.
  - Synthetic Copilot rows: +8 % tokens gives PASS, +20 % gives FAIL.
- No project test suite applies. These are skill text and benchmark tooling changes.

## Assumptions & deviations
- To meet the 9,000-char budget, `SKILL.md` was trimmed beyond the plan's Step 4 trim. Only repeated wording was removed (rule 8):
  - The Goal's second sentence restated the description.
  - The Stage/Flow definitions now live only in `staged-plans.md`.
- The plan's Step 9 check `diff vs RESULTS.md` needed `PYTHONIOENCODING=utf-8` (see Blockers).

## Blockers
- Steps 10-11 (DC-7) need a PC with Copilot CLI logged in.
- Model ids: the ids are not confirmed yet. The OpenAI API ids are `gpt-6-luna` and `gpt-6.1-sol`. Copilot usually uses the same style, but its ids may differ.
  - Before running, check each id: `copilot -p hi --model gpt-6-luna` must answer. If it fails, use the id that `/model` in an interactive `copilot` session lists.
  - Example `config.json` entry for the Luna run: `"copilot": "gpt-6-luna"`. For the Sol run: `"copilot": "gpt-6.1-sol"`.
  - In the `report.py` commands below, `<luna id>` becomes `gpt-6-luna` and `<sol id>` becomes `gpt-6.1-sol`. Use whatever ids `copilot` actually accepted.
- Run there, from `bench/skill-token`, in PowerShell:
  ```powershell
  $env:PYTHONIOENCODING = "utf-8"
  # 1. config.json: set "models.copilot" to the Copilot id for GPT-6 Luna
  python run_bench.py --probe copilot          # stop if 0 tokens
  python run_bench.py --tool copilot --versions v2.1,v2.2 --tasks T1-plan-clear,T2-plan-vague,T4-execute,T5-other
  # 2. set "models.copilot" to the GPT-6.1 Sol id, repeat the two commands
  python report.py --baseline v2.1 --candidate v2.2 --model <luna id> --out RESULTS-gpt6-luna.md
  python report.py --baseline v2.1 --candidate v2.2 --model <sol id> --out RESULTS-gpt61-sol.md
  ```
- `report.py` crashes on its final `print` when stdout is not UTF-8 (`UnicodeEncodeError: 'charmap' codec can't encode character '→'`). This existed before this plan. The report file is still written first. Workaround: `PYTHONIOENCODING=utf-8`.
- Not installed: v2.2 exists only in `bench/skill-token/versions/v2.2/`. Copy it to `~/.copilot/skills/` or `.github/skills/` once DC-7 passes.
