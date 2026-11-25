# Smoke tests (manual, fill in on your PC)

Setup: copy `fixture/` to a scratch folder, `git init`, put both v2 skill folders in `.claude/skills/` and `.github/skills/`.
Prompt: `Use the running-when-a-request-is-made skill. Classify this request: 'what does src/orders.py do?'`
Pass = the agent loads the skill and asks the class C question.

| Surface | Version | Result (PASS/FAIL) | Notes | Date |
|---|---|---|---|---|
| Claude Code | | | | |
| Copilot CLI | | | | |
| VS Code agent mode | | | | |

## Context signal (DC-8)
Install `running-when-a-request-is-made/scripts/statusline_context.py` as the status line (see `references/staged-plans.md` → Setup), work a few turns, then run `python <skill>/scripts/context_check.py` in the repo.
Pass = it prints `remaining=<number>`, not `unknown`.

| Tool | Result | Printed value | Date |
|---|---|---|---|
| Claude Code | | | |
| Copilot CLI | | | |
