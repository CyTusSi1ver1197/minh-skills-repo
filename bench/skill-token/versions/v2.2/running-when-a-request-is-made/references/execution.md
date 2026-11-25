# Execution (class B): Step 4

For `BuildPlans/<plan>/FLOW.md` (a staged plan), also follow `references/staged-plans.md`. Follow the Context budget rules in `SKILL.md`: batch independent reads and commands, write files whole.

1. **Load the plan.** Read `PLAN.agent.md` (plus `PROGRESS.md` if it exists, same step). Confirm it contains both GD and DC. If either is missing, stop and go back to Step 1 in `SKILL.md` for the missing part.
2. **Consequence check (once).** One message listing the files that will change, the functional and non-functional impact, and any rule the change will conflict with. Ask:
   > "Do you understand these consequences and want me to run the execution? (yes/no)"
   Only an explicit **yes** continues. Anything else → stop.
3. **GD sufficiency.** If the GD is not enough to build every DC, ask the missing Must/Should questions (Step 1 rules) before touching code.
4. **Checklist.** One item per DC in `PROGRESS.md` in the plan folder, and in the task-list tool if one exists. Update `PROGRESS.md` after each DC (status + last finished step). On resume or after compaction, read `PROGRESS.md` and only the plan steps for the next unfinished DC. `PROGRESS.md` layout:
   ```
   # Progress: <plan or stage id>
   Stage: <id or -> · Flow: <id or -> · Status: TODO|IN PROGRESS|PAUSED|MET|NOT MET · Updated: <ISO time>
   Needs: <stage ids from other flows, or ->
   Next step: <step number>
   Resume note: <what is half done, files touched, what to verify first>

   | DC | Status (TODO/IN PROGRESS/MET/NOT MET/REVISED) | Last step | Note |
   |---|---|---|---|

   ## Session log
   | Date | Tool | DCs done | Stopped because |
   |---|---|---|---|
   ```
5. **Build and verify DC by DC.** **Before each DC**, run `python <skill>/scripts/context_check.py`. If it prints `remaining=` 5 or less, stop and follow "Low-context stop" in `references/staged-plans.md` (ask, or pause and save status when unattended). If it prints `remaining=unknown`, don't run it again this session; per-DC `PROGRESS.md` updates are the safety net. This check overrides any instruction to finish a number of stages or DCs. Then implement the steps for the current DC. Then start a **verifier sub-agent asynchronously** (in the background where supported), giving it only the DC text, the relevant steps and the diff: *"Is this DC met? Answer MET / NOT MET with at most 10 lines of evidence."* Move on while it runs. Without a sub-agent tool, verify each DC yourself in a separate pass after building: re-read the diff fresh and run the plan's verify commands (batched in one step).
6. **All checks must pass.** If a DC cannot be met as written, don't force it and don't quietly change it. Stop on it, explain why, propose a revised DC, and ask the user. Record approved changes in the Map's `Revision log`.
7. **Rules check after changes.** Run the plan's Verify commands, plus the format/lint, build and test commands the project rules name, for the files you changed only. Chain them in one command and filter output to failures and the summary line. Run the full test suite only when the project rules require it or the change touches code shared by other modules. Add new tests only when the user asked, the project rules require them, or a specific regression needs one. Never build or run integration or performance tests unless the user asked, and ask before running them. Fix in-scope failures; report the rest as blockers.
8. **Summary before closing.** Write `EXECUTION-SUMMARY.md` in the plan folder with sections `## Files changed` (`- \`path\` (create|modify|delete) - <idea>`), `## DC status` (`| DC | Status (MET / NOT MET / REVISED) | Evidence |`), `## Rule & test results`, `## Assumptions & deviations`, `## Blockers` (`- <blocker> - <effect on which DC> - <what is needed>`, or `- none`). The reply shows only the DC status table, any blockers, and a link to the file. Ask the user to verify.
