# agent-markdown-check: manual-check references
**Goal:** let an agent run the same Claude Code and Copilot Markdown checks by hand when Python or a shell isn't available, with the same findings and report format as the scripts.
**Status:** Draft - awaiting review

## Scope
- Area: `skills/agent-markdown-check/`.
- Create:
  - `references/common.md`: procedure, frontmatter, skill and link checklists, report format;
  - `references/claude-code.md`: Claude Code file types, checklists, known keys, model values;
  - `references/github-copilot.md`: the same for Copilot.
- Modify:
  - `SKILL.md`: one fallback line in Step 2, one line in Limits;
  - `scripts/check_claude.py`, `scripts/check_copilot.py`: a drift check in `--selftest`;
  - `PROVENANCE.md`: new rows.

## Impact
- Functional: in environments without Python, the skill still works through a manual checklist. Its reports end with "(manual check)". The scripts' behaviour doesn't change.
- Non-functional: the agent loads 2 small files (common + one provider), and only when Python fails. The risk is the references drifting from the scripts; the selftest drift check covers the key and model lists.

## Rules
- Keep `SKILL.md` short; detail goes in `references/` (Agent Skills spec).
- Stdlib only.
- PROVENANCE row and fingerprint; never edit old rows (`AGENTS.md`).

## Contacts
- Owner: you. Needs owner review: no.

## Risks & assumptions
- **Manual checks are slower and can miss findings** on large folders. The SKILL.md says to prefer the scripts.
- **Drift:** the selftest catches missing keys and model values only. A changed rule or message still needs a manual update of the reference. The plan states that the scripts win when they differ.
- **DC-3 compares by hand**: an agent runs the manual check on two folders and must match the scripts' findings.

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | 3 reference files state every script rule, with the same level and message | Original |
| DC-2 | `SKILL.md` falls back to the references without Python and marks the report "(manual check)" | Original |
| DC-3 | The manual check matches the scripts on `skills/explain-skills-in-details` and `versions/v2.1` | Original |
| DC-4 | The selftests fail when a key or model alias is missing from a reference | Original |
| DC-5 | PROVENANCE timeline row + new fingerprint | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-1 | Could | How many reference files? | Three: common + one per provider | Assumption |
| Q-2 | DC-1 | Could | Which wins if references and scripts differ? | The scripts | Assumption |
| Q-3 | DC-2 | Could | When is Python "not usable"? | `python --version` fails or is below 3.10, or no shell tool | Assumption |
| Q-4 | DC-4 | Could | How to keep them in sync? | Selftest check on key and model lists | Assumption |
| Q-5 | DC-3 | Could | Where to compare manual and script results? | `skills/explain-skills-in-details`, `versions/v2.1` | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
| 2026-11-26 | Plan created | - |
