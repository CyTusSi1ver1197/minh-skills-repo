# Skill token benchmark (v1 vs v2)

Proves that `running-when-a-request-is-made` v2 (with `information-gathering-for-plan` v2) uses fewer tokens than v1 on the same tasks, in Claude Code and GitHub Copilot CLI, without losing output quality. It also checks the new staged-plan features.

## Layout
| Path | What |
|---|---|
| `versions/v1/` | Untouched v1 of both skills (baseline). v2 = the live skill folders in the repo root. |
| `fixture/` | Tiny Python repo copied fresh for every run (includes `BuildPlans/add-order-total/` for T4 and the staged `BuildPlans/orders-v2/` for T7/T8). |
| `tasks.json` | 8 tasks: T1-T5 (token bar, v1 + v2), T6-T8 (staged features, v2 only). |
| `config.json` | Models, CLI commands, pass bar. **Set `models.copilot` before running.** |
| `static_measure.py` | Characters/tokens each version loads per request class → `STATIC.md`. |
| `validate_skill.py` | Agent Skills spec + budgets + relative-path check. |
| `run_bench.py` | Runs tasks headless, records tokens + quality → `results/results.jsonl`. |
| `check_outputs.py` | Quality score (0-1) per run. |
| `report.py` | `RESULTS.md` with PASS/FAIL per tool. |
| `RULE-COVERAGE.md` | Every v1 rule → its v2 location. |
| `SMOKE.md`, `PARKED.md` | Manual records (fill in). |

## Versions
- `v1`: original skills (`versions/v1/`).
- `v2.0`: first rewrite, many small files (`versions/v2.0/`). It doubled turns on plan requests.
- `v2.1`: the live skills in the repo root. Planning and output layouts are back in `SKILL.md`, the context rules count steps, and information-gathering is one file again.

## Run on your PC (Windows PowerShell, Claude Code only): low-usage procedure
The runner **reuses results already in `results/results.jsonl`**: `--repeats N` means "N valid runs in total per version and task", so v1's 3 runs from the first benchmark are not repeated. Each new run prints its turns and estimated cost. `--budget-usd` stops the batch once the summed estimate reaches the limit; re-run the same command later to continue.

```powershell
cd $env:SKILLS_ROOT\bench\skill-token
# 0. Park user-level copies of the skills (PARKED.md). Note /usage (session %, weekly %).
# 1. Screen the two tasks v2.0 failed: 2 runs (v1 reused)
python run_bench.py --tool claude --versions v1,v2.1 --tasks T1-plan-clear,T2-plan-vague --budget-usd 1
python report.py --candidate v2.1      # read the "Next" column
#    "clear loss" on either -> stop; send me RESULTS.md. Otherwise continue.
# 2. The other token tasks: 3 runs
python run_bench.py --tool claude --versions v1,v2.1 --tasks T3-plan-docs,T4-execute,T5-other --budget-usd 1
# 3. Only for tasks marked "close: add 1 run": raise the target to 2 (or 3) for that task
python run_bench.py --tool claude --versions v1,v2.1 --repeats 2 --tasks <task id>
# 4. Feature checks, once each (T6 is the most expensive; run it last)
python run_bench.py --tool claude --versions v2.1 --tasks T7-resume,T8-low-context,T6-plan-large --budget-usd 2
python report.py --candidate v2.1
# 5. Note /usage again. Restore the parked skills.
```
Typical total: 8-10 new runs instead of 78. If your Claude Code CLI version changed since the v1 runs, re-run v1 for T1-T2 too (`--fresh` ignores old rows) so both sides use the same CLI.

**Calibrating the budget:** after step 1, compare the `/usage` session % change with the printed batch estimate (e.g. "$0.40 ≈ 8 %"). Use that ratio to pick a `--budget-usd` that leaves room in your 5-hour window. The ratio is your own measurement; Anthropic doesn't publish one.

## Pass bar (revised 2026-11-24)
- On **every** task T1-T5: v2.1 median **turns** ≤ v1, median **cost** ≤ v1, median quality ≥ v1.
- With 1 run per task, a task counts as decided when v2.1 is below v1's lowest run (clear win) or above v1's highest run (clear loss) on turns or cost. Inside v1's range = add a run (max 3).
- T6, T7, T8: all checks pass in ≥ 2 of 3 runs.
- `cost_usd` is Claude Code's API-price estimate, not your subscription charge. Use it to compare versions. Your plan's real consumption is the `/usage` change you note before and after each batch (that check is coarse, because your other Claude use also counts).
- Total tokens count cache reads at full weight. They're shown for information only.
