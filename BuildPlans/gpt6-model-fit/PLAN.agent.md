# EXECUTION PLAN: gpt6-model-fit

## Context
The two request-workflow skills (`running-when-a-request-is-made` v2.1 and `information-gathering-for-plan` v2.1) were tuned on Claude. They must also work well on OpenAI GPT-6 Luna, GPT-6 Astra, GPT-6.1 Sol and GPT-6.2 Sol, run through GitHub Copilot (VS Code agent mode, Copilot CLI). One shared copy serves every model, Claude included. The result is version **v2.2**.

Guidance these changes follow (checked 2026-11-25):
- OpenAI "Using GPT-6.2" guide, https://developers.openai.com/api/docs/guides/latest-model. It says to stop to clarify only when scope changes significantly, when concretely blocked, when a user-level decision is needed, or before an irreversible action. Otherwise make reasonable assumptions and continue. Add new tests only when asked, when the repo requires them, or for a specific regression.
- OpenAI dev blog "Rethinking skills and prompts for GPT-6 Astra", https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra. Key points:
  - The skill description should be short and say when to use the skill.
  - Astra over-tests, and strong ask-first wording can stop it.
  - Astra may return after a first implementation while work remains.
  - Guidance written for weaker models can overconstrain Astra.
- OpenAI GPT-6.2 announcement, https://openai.com/index/introducing-gpt-6-2-astra-sol/. It says 6.2 Astra and 6.2 Sol tend to leave out blockers, such as a missing file or an unavailable tool.
- There is no official GPT-6 Luna prompting guide. For Luna, keep rules explicit, which the skill already does.

Paths are relative to the repo root `skill-v2.1.1/`:
- `BENCH` = `bench/skill-token`
- `LIVE_RUN` = `running-when-a-request-is-made-v2.1/running-when-a-request-is-made` (current v2.1; never edited by this plan)
- `LIVE_IG` = `information-gathering-for-plan-v2.1/information-gathering-for-plan` (current v2.1; never edited by this plan)
- `RUN` = `BENCH/versions/v2.2/running-when-a-request-is-made` (the copy that receives every edit)
- `IG` = `BENCH/versions/v2.2/information-gathering-for-plan` (the copy that receives every edit)

Version folders after this plan:
- `BENCH/versions/v1/`: unchanged.
- `BENCH/versions/v2.0/`: unchanged. It holds the real v2.0 rewrite (assets/, planning.md).
- `BENCH/versions/v2.1/`: a frozen, complete copy of the current skills (every .md and .py file).
- `BENCH/versions/v2.2/`: a copy of v2.1 with this plan's changes.

Not in scope:
- Splitting `SKILL.md` back into small reference files. v2.0 did that and doubled turns, so v2.1 inlined it on purpose (Q-5).
- Benchmarking Astra and 6.2 Sol (Q-3).

## Preconditions
- Python 3 on PATH.
- The benchmark runs (Steps 9-11) need a PC where Copilot CLI is logged in with a Copilot Enterprise seat, plus a copy of this repo.
- On that PC, `copilot -p hi --model <id>` must answer for both GPT-6 Luna and GPT-6.1 Sol. Note the exact model ids the CLI accepts. The OpenAI API ids are `gpt-6-luna` and `gpt-6.1-sol`, but Copilot ids may differ.
- Park any user-level copies of both skills before the runs, as described in `BENCH/PARKED.md`.

## Rules
- Each `SKILL.md` keeps `name` equal to its folder name and the description under 1,024 chars. No absolute paths, and every referenced file must exist (source: `BENCH/validate_skill.py`).
- The planning, execution and staged-plan file layouts stay unchanged, because `BENCH/check_outputs.py` scores them (source: `BENCH/check_outputs.py`).
- Compress only by removing repetition. Never remove a DC, a Verify line, a stop condition or an assumption (source: `RUN/SKILL.md` rule 8).
- Write in plain prose without ALL-CAPS emphasis (source: OpenAI GPT-6.2 guide style).

## Steps
1. [DC-7, DC-8] Create `BENCH/versions/v2.1/`: copy the whole of `LIVE_RUN` (SKILL.md, references/*.md, scripts/*.py) to `BENCH/versions/v2.1/running-when-a-request-is-made/`, and the whole of `LIVE_IG` to `BENCH/versions/v2.1/information-gathering-for-plan/`. This is the frozen baseline. Don't touch `BENCH/versions/v2.0/`. If `BENCH/versions/v2.1/` already exists, stop and ask.
   Verify:
   - `diff -r LIVE_RUN BENCH/versions/v2.1/running-when-a-request-is-made` and `diff -r LIVE_IG BENCH/versions/v2.1/information-gathering-for-plan` print nothing.
   - `python BENCH/validate_skill.py BENCH/versions/v2.1/running-when-a-request-is-made BENCH/versions/v2.1/information-gathering-for-plan` prints 2× PASS.
1b. [DC-8] Create `BENCH/versions/v2.2/` as a complete copy of `BENCH/versions/v2.1/` (both skill folders, all .md and .py files). Steps 2-7 edit only these copied files (`RUN`, `IG`).
   Verify: `diff -r BENCH/versions/v2.1 BENCH/versions/v2.2` prints nothing before Step 2.
2. [DC-1] Modify `RUN/SKILL.md` line 3, the description, to:
   `"Use when a request asks to plan, build or change something, or to execute or continue a BuildPlans plan. Agrees done criteria, given data and ranked questions first, then writes a two-file plan or executes one DC by DC."`
   Modify `IG/SKILL.md` line 3 to:
   `"Use when a request or plan has unclear, missing or conflicting done criteria or given data. Gathers evidence from the repo and retrieval tools, resolves conflicts, then asks a capped, ranked set of questions."`
   Verify: `grep -c '^description: "Use when' RUN/SKILL.md IG/SKILL.md` shows 1 for each. Each description is ≤ 300 chars: `python -c "import re,sys;[print(f,len(re.search(r'description: \"(.*)\"',open(f,encoding='utf-8').read()).group(1))) for f in sys.argv[1:]]" RUN/SKILL.md IG/SKILL.md`.
3. [DC-2] Modify `RUN/SKILL.md` Step 0:
   - Replace lines 34-39 (the class C opt-in question) with: `For class C, handle the request normally and do not ask about format. If it could be planning work, end the reply with one line: "Say 'plan it' to use the structured plan workflow." If the user says so, treat the request as class A.`
   - In the table row for C, change `Ask once (below)` to `Handle normally (below)`.
   Verify: `grep -n "ask exactly once" RUN/SKILL.md` prints nothing, and `grep -n "plan it" RUN/SKILL.md` prints 1 line.
4. [DC-5] Modify `RUN/SKILL.md`: insert a section `## Working rules (always on)` directly after the Context budget section, with exactly these four items:
   1. `The user's explicit instructions override this skill. When a rule of this skill makes you pause or ask, name the file, quote the rule, and say whether it is explicit or your interpretation.`
   2. `Stop for the user only at the gates this skill names (unanswered Must questions, conflicts, the execution yes/no check, a DC that can't be met as written) or before an irreversible or destructive action. Everywhere else, make a reasonable, reversible assumption, state it, and continue.`
   3. `Report every blocker: a missing file, an unavailable tool or skill, a command that fails, or a check you could not run. Never skip a step silently.`
   4. `When executing, keep going through every DC until all are MET or a stop condition applies. Don't return for review between DCs.`
   To keep the size net-neutral, shorten Context budget rule 3 to `Delegate discovery to a sub-agent only when it would take many reads; ask for a ≤ 30-line summary with file:line evidence.`
   Verify: `grep -n "## Working rules" RUN/SKILL.md` prints 1 line. `python BENCH/validate_skill.py RUN IG` prints 2× PASS.
5. [DC-3] Modify `RUN/references/execution.md` step 7. Replace it with: `**Rules check after changes.** Run the plan's Verify commands, plus the format/lint, build and test commands the project rules name, for the files you changed only. Chain them in one command and filter output to failures and the summary line. Run the full test suite only when the project rules require it or the change touches code shared by other modules. Add new tests only when the user asked, the project rules require them, or a specific regression needs one. Never build or run integration or performance tests unless the user asked, and ask before running them. Fix in-scope failures; report the rest as blockers.`
   This removes the references to the unit-tests, integration-tests and performance-tests skills, which don't exist.
   Verify: `grep -rn "unit-tests skill\|integration-tests\|performance-tests" RUN` prints nothing.
6. [DC-5] Modify `RUN/references/execution.md` step 8. In the `EXECUTION-SUMMARY.md` section list, add `## Blockers` (`- <blocker> - <effect on which DC> - <what is needed>`, or `- none`) after `## Assumptions & deviations`. Add to the reply sentence: `and any blockers`.
   Verify: `grep -n "## Blockers" RUN/references/execution.md` prints 1 line.
7. [DC-4] Modify `RUN/references/execution.md` step 5:
   - Keep the context check before each DC.
   - Add: `If it prints remaining=unknown, don't run it again this session. Per-DC PROGRESS.md updates are the safety net.`
   Modify `RUN/references/staged-plans.md`:
   - Change the first line of "Low-context stop" (line 65) to `Run the context check before each DC and before each new stage (same rule as references/execution.md step 5).`
   - Line 69 already says the same thing as the new step 5 text, so replace it with `- remaining=unknown: write a Resume note before each new stage.`
   Verify: `grep -n "After every DC and before each new stage" RUN/references/staged-plans.md` prints nothing. `grep -n "remaining=unknown" RUN/references/execution.md` prints 1 line.
8. [DC-6, DC-7, DC-8] Check the v2.2 copy and measure both versions. Benchmarking v2.1 and v2.2 from `BENCH/versions/` is also required: `run_bench.py` `version_dir()` falls back to the repo root, where the skills are not present (they sit in `*-v2.1/` folders).
   Verify:
   - `diff -r LIVE_RUN BENCH/versions/v2.1/running-when-a-request-is-made` still prints nothing (live and baseline are untouched). `diff -rq BENCH/versions/v2.1 BENCH/versions/v2.2` lists only `SKILL.md` (both skills), `references/execution.md` and `references/staged-plans.md`.
   - `python BENCH/validate_skill.py BENCH/versions/v2.2/running-when-a-request-is-made BENCH/versions/v2.2/information-gathering-for-plan` prints 2× PASS.
   - `python BENCH/static_measure.py BENCH/versions/v2.1 --as v2.1` and `python BENCH/static_measure.py BENCH/versions/v2.2 --as v2.1` (same layout, so `--as v2.1`): the v2.2 chars per request class are ≤ 105 % of v2.1.
9. [DC-7] Modify `BENCH/report.py`:
   - Add `ap.add_argument("--model", default=None)` and filter `good` to rows whose `model` equals it when it is set.
   - For tool `copilot` (turns and cost_usd are `None`), compare median `total_tokens` instead of turns and cost.
   - Keep the Claude logic unchanged.
   Add `# ponytail: total_tokens is the only Copilot metric; switch to turns once parse_copilot records them`.
   Verify: `python BENCH/report.py --candidate v2.1 --out %TEMP%/r.md` still runs on the existing Claude rows. Diff `%TEMP%/r.md` against `BENCH/RESULTS.md`: only lines that come from `meta.json` may change.
10. [DC-7] On the Copilot PC, from `BENCH`:
    1. Set `config.json` `models.copilot` to the Luna id.
    2. Run `python run_bench.py --probe copilot`. Stop if it shows 0 tokens.
    3. Run `python run_bench.py --tool copilot --versions v2.1,v2.2 --tasks T1-plan-clear,T2-plan-vague,T4-execute,T5-other`.
    4. Set `models.copilot` to the 6.1 Sol id and repeat sub-steps 2 and 3.
    That is 16 runs in total.
    Verify: `results/results.jsonl` has 16 new rows with `tool` copilot, `exit_code` 0 and `total_tokens` > 0.
11. [DC-7] Run `python report.py --baseline v2.1 --candidate v2.2 --model <luna id> --out RESULTS-gpt6-luna.md`, then the same command for the 6.1 Sol id (`--out RESULTS-gpt61-sol.md`).
    Verify: for each model and task, v2.2 median quality ≥ v2.1, and v2.2 median total_tokens ≤ 110 % of v2.1. 1 run each means noise: inside ±10 % counts as a tie and passes. For T2, also check by hand that the reply states assumptions instead of stopping on Should-level questions.

## DC checklist
- [ ] DC-1 - verify by: Step 2 commands
- [ ] DC-2 - verify by: Step 3 commands; T5 rows show no format question in the reply
- [ ] DC-3 - verify by: Step 5 grep; T4 rows pass `tests pass`
- [ ] DC-4 - verify by: Step 7 greps
- [ ] DC-5 - verify by: Step 4 and 6 greps; T4 `EXECUTION-SUMMARY.md` contains `## Blockers`
- [ ] DC-6 - verify by: Step 8 static measure ≤ 105 %
- [ ] DC-7 - verify by: Steps 1, 8, 10, 11 pass
- [ ] DC-8 - verify by: Step 1, 1b and 8 diff commands

## Stop conditions
- Stop and ask if the Copilot CLI doesn't list GPT-6 Luna or GPT-6.1 Sol, or if `--probe copilot` records 0 tokens.
- Stop and ask if `check_outputs.py` fails a check on v2.2 that v2.1 passes on the same model (quality regression).
- Stop and ask if any change needs a different plan, progress or summary file layout than the one in `RUN/SKILL.md` Step 3 and `RUN/references/execution.md`.
- Stop and ask if v2.2 static size exceeds 105 % of v2.1 and can't be trimmed without dropping a rule-8 item.

## Contacts
- Owner: the repo owner (no `CODEOWNERS` file and no git history in this repo).
- Needs owner review: no. The change touches 9 files plus 2 snapshot folders, about 60 changed lines, and no public API, schema, auth or CI.

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | Both `SKILL.md` descriptions start with "Use when", are ≤ 300 chars, and `validate_skill.py` passes | Original |
| DC-2 | Class C requests are handled without a format question. The hard gates are exactly: unanswered Must questions, every conflict, the execution yes/no check, an unmeetable DC, and irreversible actions | Revised via Q-2 |
| DC-3 | Execution runs only the checks the change needs, adds tests only when asked, required or for a regression, and names no skill that doesn't exist | Original |
| DC-4 | The context check is defined once (before each DC) and skipped after its first `remaining=unknown` | Original |
| DC-5 | The skill states that user instructions take precedence, says to quote the rule when pausing, says to report every blocker (including a `## Blockers` summary section), and says to keep executing through all DCs | Original |
| DC-6 | v2.2 static load per request class is ≤ 105 % of v2.1 | Original |
| DC-7 | On Copilot CLI with GPT-6 Luna and GPT-6.1 Sol, v2.2 vs v2.1 on T1, T2, T4 and T5: quality not lower, total tokens ≤ 110 % | Revised via Q-3 |
| DC-8 | `BENCH/versions/v2.1/` is a complete, unchanged copy of the current skills (all .md and .py files). `BENCH/versions/v2.2/` is that copy plus this plan's edits. The live `*-v2.1/` folders and `BENCH/versions/v2.0/` are unchanged | Added via Q-10 |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-1-DC-5 | Must | One shared skill for all models, or per-model variants? | One shared skill, Claude included | User |
| Q-2 | DC-2 | Must | Which user-question gates stay hard stops? | The execution yes/no check, Must questions, and every conflict asked. The class C opt-in question becomes "handle normally plus a one-line hint" | User |
| Q-3 | DC-7 | Should | How should the changes be verified? | Static checks, plus a bench on GPT-6 Luna and GPT-6.1 Sol only (token limits) | User |
| Q-4 | all | Must | Output format? | The standard BuildPlans set in `BuildPlans/gpt6-model-fit/` | User |
| Q-5 | DC-6 | Could | Split `SKILL.md` back into a small router plus references, as the OpenAI skills blog suggests? | No. v2.0 tried this and doubled turns, so the v2.1 inlining stays | Assumption |
| Q-6 | DC-7 | Should | Re-run the Claude bench to prove no regression on Claude? | No, because of token limits. The changes are wording-only and Claude-neutral. Flagged as a risk | Assumption |
| Q-7 | DC-7 | Could | Which tasks to run? | T1, T2, T4 and T5, 1 run each. T3 overlaps T1, and T6-T8 are expensive and cover staged features that are unchanged | Assumption |
| Q-8 | DC-7 | Could | What to name the new version? | v2.2, in `BENCH/versions/v2.2/` | User |
| Q-9 | DC-7 | Could | Which Copilot metric, given that turns and cost are not recorded? | total_tokens, with a ±10 % tie band for single runs | Assumption |
| Q-10 | DC-8 | Must | Where does the old version go, and where are the edits made? | Keep the current skills complete in `BENCH/versions/v2.1/` (the real v2.0 stays in `versions/v2.0/`). Copy it to `versions/v2.2/` and edit only that copy | User |

## Revision log
| Date | Change | Approved by |
|---|---|---|
| 2026-11-25 | Plan created | - |
| 2026-11-25 | The old version is kept complete in `versions/v2.1/`. Edits move to a `versions/v2.2/` copy, and the live folders are no longer edited (Steps 1, 1b, 8; DC-8; Q-10) | User |
