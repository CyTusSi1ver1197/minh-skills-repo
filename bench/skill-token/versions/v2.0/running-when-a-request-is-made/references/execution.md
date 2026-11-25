# Execution (class B): Step 4

For `BuildPlans/<plan>/FLOW.md` (a staged plan), also follow `references/staged-plans.md`.

1. **Load the plan.** Read `PLAN.agent.md`. Confirm it contains both GD and DC. If either is missing, stop and go back to Step 1 (`references/planning.md`) for the missing part.
2. **Consequence check (once).** One message listing the files that will change, the functional and non-functional impact, and any rule the change will conflict with. Ask:
   > "Do you understand these consequences and want me to run the execution? (yes/no)"
   Only an explicit **yes** continues. Anything else → stop.
3. **GD sufficiency.** If the GD is not enough to build every DC, ask the missing Must/Should questions (Step 1 rules) before touching code.
4. **Checklist.** One item per DC in `PROGRESS.md` in the plan folder (from `assets/PROGRESS.template.md`), and in the task-list tool if one exists. Update `PROGRESS.md` after each DC (status + last finished step). On resume or after compaction, read `PROGRESS.md` and only the plan steps for the next unfinished DC.
5. **Build and verify DC by DC.** Implement the steps for the current DC. Then start a **verifier sub-agent asynchronously** (in the background where supported), giving it only the DC text, the relevant steps and the diff: *"Is this DC met? Answer MET / NOT MET with at most 10 lines of evidence."* Move on while it runs. Without a sub-agent tool, verify each DC yourself in a separate pass after building: re-read the diff fresh and run the plan's verify commands.
6. **All checks must pass.** If a DC cannot be met as written, don't force it and don't quietly change it. Stop on it, explain why, propose a revised DC, and ask the user. Record approved changes in the Map's `Revision log`.
7. **Rules check after changes.** Run format/lint, build, unit tests, integration/connectivity tests and the plan's Rules checks, with output filtered to failures and the summary line. Fix in-scope failures; report the rest. If the project rules require tests, build and run **unit tests only** with the unit-tests skill. Build integration or performance tests (integration-tests, performance-tests skills) only when the user asked, and ask before running them.
8. **Summary before closing.** Write `EXECUTION-SUMMARY.md` in the plan folder from `assets/EXECUTION-SUMMARY.template.md`: files created / modified / deleted with one line each, DC status (MET / NOT MET / REVISED), rule and test results, assumptions and deviations. The reply shows only the DC status table and a link to the file. Ask the user to verify.
