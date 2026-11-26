# Execution summary: agent-markdown-check-references

## Files changed
- `skills/agent-markdown-check/references/common.md` (create): when to use the manual check, the 5-step procedure, the Frontmatter, Skill and Link checklists with the scripts' exact messages, and the report format with " (manual check)".
- `skills/agent-markdown-check/references/claude-code.md` (create): Claude Code file types, skill extras, agent, command and memory checklists, model values, known keys.
- `skills/agent-markdown-check/references/github-copilot.md` (create): Copilot file types, skill extras, location check, agent, prompt, instructions and repo-instructions/agents-md checklists, known keys.
- `skills/agent-markdown-check/SKILL.md` (modify): Step 2 fallback to the references when Python 3.10+ or a shell isn't available; one line in Limits.
- `skills/agent-markdown-check/scripts/_common.py` (modify): `assert_in_reference()`, the drift-check helper.
- `skills/agent-markdown-check/scripts/check_claude.py`, `scripts/check_copilot.py` (modify): `selftest()` calls the drift check first. No rule or message changed.
- `PROVENANCE.md` (modify): a new timeline row and a new fingerprint row (`86020782…`, 7 files); the older rows are kept.

## DC status
| DC | Status (MET / NOT MET / REVISED) | Evidence |
|---|---|---|
| DC-1 | MET | The 3 files cover every `rep.err`/`rep.warn` message in the scripts (checked against a grep of all 48 calls) and every type each script classifies. Both checkers give 0 errors on the skill |
| DC-2 | MET | `grep -c "manual check" SKILL.md` = 2; `validate_skill.py` PASS |
| DC-3 | MET | A fresh sub-agent with no Python and no access to `scripts/` gave, for both providers, the same finding as the scripts (1 WARN, `description has no trigger`, on `versions/v2.1/running-when-a-request-is-made/SKILL.md`) and the same counts (3 checked, 0 skipped, 0 errors, 1 warning). The only difference was a line number (`:3`), now fixed in the references |
| DC-4 | MET | Both `--selftest` runs print `selftest OK`. Removing `permissionMode` from `claude-code.md` makes the selftest fail with `references/claude-code.md is missing: permissionMode`; the file was then restored |
| DC-5 | MET | New timeline row (2026-11-26, 21:44) and fingerprint row in `PROVENANCE.md` |

## Rule & test results
- `check_claude.py --selftest`, `check_copilot.py --selftest`: OK.
- `check_claude.py` and `check_copilot.py` on `skills/agent-markdown-check`: 0 errors, 0 warnings.
- `validate_skill.py skills/agent-markdown-check`: PASS.
- `SKILL.md` has 48 lines; the references have 77 + 55 + 53 lines.

## Assumptions & deviations
- The DC-3 sub-agent raised 4 unclear points. I fixed them in the references only:
  - skill rules have no line number;
  - the Frontmatter checklist applies to `SKILL.md` only;
  - Copilot skills do run the Link checklist (the wording was misleading);
  - the BOM check is best effort without raw bytes.
- `_common.py` also changed (the drift helper). The plan named only the two scripts. The change is small and holds no rule logic.
- No `PROGRESS.md`: the plan has one stage, finished in one session.

## Blockers
- none
