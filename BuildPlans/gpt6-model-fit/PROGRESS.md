# Progress: gpt6-model-fit
Stage: - · Flow: - · Status: PAUSED · Updated: 2026-11-25
Needs: -
Next step: 10
Resume note:
- Steps 1-9 are done. The v2.1 baseline and the v2.2 copy are in `bench/skill-token/versions/`. `report.py` has `--model` and the Copilot token rule.
- Steps 10-11 need the PC where Copilot CLI is logged in. First confirm the Copilot model ids for GPT-6 Luna and GPT-6.1 Sol.
- On that PC, check first that `python run_bench.py --probe copilot` records more than 0 tokens.

| DC | Status (TODO/IN PROGRESS/MET/NOT MET/REVISED) | Last step | Note |
|---|---|---|---|
| DC-1 | MET | 2 | Descriptions are 219 and 208 chars and start with "Use when"; validate PASS |
| DC-2 | IN PROGRESS | 3 | Text change verified; the T5 reply check is waiting on the Step 10 runs |
| DC-3 | IN PROGRESS | 5 | No references to missing skills remain; T4 `tests pass` is waiting on the Step 10 runs |
| DC-4 | MET | 7 | The context check is defined once; it is skipped after `unknown` |
| DC-5 | IN PROGRESS | 4, 6 | Rules and `## Blockers` are in place; the T4 summary check is waiting on the Step 10 runs |
| DC-6 | MET | 8 | v2.2 is at most 104.1 % of v2.1 (class B) |
| DC-7 | NOT MET | 9 | Steps 10-11 have not run (needs the Copilot PC) |
| DC-8 | MET | 1, 1b, 8 | Live = v2.1 snapshot (`diff -r` empty); only the 4 planned files differ in v2.2 |

## Session log
| Date | Tool | DCs done | Stopped because |
|---|---|---|---|
| 2026-11-25 | Claude Code (VS Code) | DC-1, DC-4, DC-6, DC-8 | Steps 10-11 need the logged-in Copilot CLI PC |
