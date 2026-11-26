# EXECUTION PLAN: agent-markdown-check-references

## Context
`skills/agent-markdown-check/` is an Agent Skill that checks Markdown files against Claude Code and GitHub Copilot rules. Today it has:
- `SKILL.md`: which checker to run, how to report, fix only when asked;
- `scripts/_common.py`: shared frontmatter parser, link checks, skill rules;
- `scripts/check_claude.py`: Claude Code rules, plus `--selftest`;
- `scripts/check_copilot.py`: GitHub Copilot rules, plus `--selftest`.

The scripts need Python 3.10+ and a shell. Some environments have neither: Copilot chat without a terminal, claude.ai, a locked-down work laptop. This plan adds a `references/` folder with Markdown checklists. An agent can then run the same checks by hand, using only file read and file list tools, and report in the same format.

The scripts stay the primary path. The references are the fallback, and the agent loads only the file for the provider it checks.

Report format (same as the scripts): one line per finding, `ERROR <path>:<line>  <message>` or `WARN  <path>:<line>  <message>`, then a summary line `<Provider>: <n> checked, <n> skipped (not a <Provider> file type), <n> error(s), <n> warning(s)`. The manual path appends ` (manual check)` to the summary line.

Rules to carry over, from the scripts as they are now:
- **Frontmatter (common):** the file starts with `---` and has a closing `---`. Each line is `key: value`. ERROR on tab indentation, a stray indented line, a duplicate key, an unclosed quote or `[` list, an unquoted value starting with `@ \` % & * ! {`, or an unquoted `: ` inside a value. WARN on ` #` inside an unquoted value (the rest becomes a comment) and on a UTF-8 BOM.
- **Skill (common):**
  - `name` is required, matches `[a-z0-9]+(-[a-z0-9]+)*`, is ≤ 64 chars and equals the folder name.
  - `description` is required, 1-1024 chars, has no XML/HTML tags, and WARN when it has no "when" trigger.
  - WARN when the body is over 500 lines.
  - Every relative link and every bare `references/`, `assets/` or `scripts/` path exists. WARN when a link leaves the skill folder.
  - Links in `assets/` templates are skipped.
  - WARN on absolute paths outside code.
  - Fenced code blocks and inline code are never checked.
- **Claude Code:**
  - Type comes from the path: `SKILL.md` = skill, `CLAUDE.md` or `CLAUDE.local.md` = memory, `.claude/agents/*.md` = agent, `.claude/commands/*.md` = command.
  - Skill: WARN when `name` contains `anthropic` or `claude`.
  - Agent: frontmatter required; `name` required and lowercase-hyphen; `description` required; WARN on an empty body.
  - `model` (agent, command, skill): WARN unless it is `sonnet`, `opus`, `haiku`, `fable`, `inherit` or starts with `claude-`.
  - Memory: WARN on frontmatter or > 40,000 chars. ERROR when an `@path` import (one containing `/` or `.`, trailing `.,;:` stripped, `~/` = home, otherwise relative to the file) doesn't exist.
  - Known keys are the `SKILL_KEYS`, `AGENT_KEYS` and `COMMAND_KEYS` sets in `check_claude.py`. Other keys WARN.
- **GitHub Copilot:**
  - Type comes from the path: `SKILL.md` = skill, `copilot-instructions.md` = repo-instructions, `AGENTS.md` = agents-md, `*.instructions.md` = instructions, `*.prompt.md` = prompt, `*.chatmode.md` or `.github/agents/*.md` / `~/.copilot/agents/*.md` = agent.
  - Other `*.agent.md` files, such as `BuildPlans/.../PLAN.agent.md`, are skipped.
  - Skill: WARN when `model` is present (Copilot ignores it).
  - Agent: ERROR without `description`. WARN on `model` as a list (VS Code only) and on `.chatmode.md` (old name).
  - Prompt: WARN on `mode` (old key for `agent`).
  - Instructions: WARN without `applyTo`, ERROR on an empty `applyTo`.
  - repo-instructions and agents-md: WARN on frontmatter.
  - instructions and repo-instructions: WARN over 4,000 chars (code review reads only the first 4,000).
  - Agent, prompt and instructions files: WARN when not under `.github/agents/`, `.github/prompts/` or `.github/instructions/`.
  - Known keys are the `SKILL_KEYS`, `AGENT_KEYS`, `PROMPT_KEYS` and `INSTRUCTION_KEYS` sets in `check_copilot.py`.

## Preconditions
- Repo `skill-factory`, branch `main`, clean apart from this plan.
- Python 3.10+ to run the verify commands. The new references must not need it.

## Rules
- Skill size: keep `SKILL.md` short and put detail in `references/`; the body stays ≤ 500 lines (source: Agent Skills spec; the skill's own check).
- Stdlib only (source: `bench/skill-token` and this skill).
- `PROVENANCE.md`: add a timeline row and update the skill's fingerprint; never edit old rows (source: `AGENTS.md`).
- No company names, internal URLs or private evidence in the repo (source: `AGENTS.md`).
- The references and the scripts must state the same rules. Where they differ, the script is right; fix the reference.

## Steps
1. [DC-1, DC-3] Create `skills/agent-markdown-check/references/common.md`, at most about 120 lines:
   - `## When to use this file`: Python 3.10+ or a shell isn't available. Read this file plus one provider file.
   - `## Procedure`:
     1. list the given files, recursively for folders, skipping `.git`, `node_modules`, `__pycache__` and `.venv`;
     2. group each `SKILL.md` folder as one skill;
     3. classify the other files with the provider file's type table;
     4. run the checklists;
     5. report.
   - `## Frontmatter checklist` and `## Skill checklist`: the common rules from Context, each one a line `- [ERROR|WARN] <rule> → message: "<script message>"`, using the script's message text.
   - `## Link checklist`: what to check, what to skip (code, `http(s):`, `mailto:`, `#` anchors, targets with `< * { $ %`, `assets/` templates). Check that a target exists with the file-list tool.
   - `## Report format`: from Context, including ` (manual check)`.
   Verify: `python skills/agent-markdown-check/scripts/check_claude.py skills/agent-markdown-check` shows 0 errors (the new links resolve).
2. [DC-1, DC-3] Create `skills/agent-markdown-check/references/claude-code.md`, at most about 80 lines:
   - `## File types` (table: path pattern → type);
   - one checklist section per type, with the Claude Code rules from Context in the Step 1 line format;
   - `## Known frontmatter keys`, listing each key of `SKILL_KEYS`, `AGENT_KEYS` and `COMMAND_KEYS` in backticks, grouped by type;
   - `## Model values`.
   Verify: same command as Step 1.
3. [DC-1, DC-3] Create `skills/agent-markdown-check/references/github-copilot.md`, the same shape as Step 2, with the Copilot rules and `SKILL_KEYS`, `AGENT_KEYS`, `PROMPT_KEYS` and `INSTRUCTION_KEYS`.
   Verify: `python skills/agent-markdown-check/scripts/check_copilot.py skills/agent-markdown-check` shows 0 errors.
4. [DC-2] Modify `skills/agent-markdown-check/SKILL.md`:
   - In Step 2, add: `If Python 3.10+ or a shell isn't available (\`python --version\` fails or is older), check by hand instead: read references/common.md and the one provider file (references/claude-code.md or references/github-copilot.md), follow its procedure, and report in the same format with " (manual check)" on the summary line.`
   - In `## Limits`, add: `The manual check follows the same rules but is slower and can miss findings on large folders; prefer the scripts when they run.`
   Verify: `python bench/skill-token/validate_skill.py skills/agent-markdown-check` prints PASS; `grep -c "manual check" skills/agent-markdown-check/SKILL.md` ≥ 2.
5. [DC-4] Add a drift check to each script's `selftest()`:
   - `check_claude.py`: read `../references/claude-code.md` relative to the script. Assert that every key in `SKILL_KEYS | AGENT_KEYS | COMMAND_KEYS` and every value in `MODEL_ALIASES` appears in backticks.
   - `check_copilot.py`: the same against `../references/github-copilot.md`, with its four key sets.
   - Fail with a message naming the missing keys.
   Verify: both `--selftest` runs print `selftest OK`. Then temporarily delete one key from a reference file, check that the selftest fails and names it, and restore the file.
6. [DC-5] Update `PROVENANCE.md`:
   - add a timeline row (date and time from `date "+%Y-%m-%d %H:%M"` in Git Bash; that is already local +0700, so don't set `TZ`);
   - add a new fingerprint row for `skills/agent-markdown-check`, keeping the old one;
   - device: this machine; work-hours status: "to be confirmed by the author".
   Verify: `grep -c "agent-markdown-check" PROVENANCE.md` went up by at least 2; the fingerprint recomputed with the command in `PROVENANCE.md` matches the new row.

## DC checklist
- [ ] DC-1 - verify by: the 3 reference files exist; each provider file covers every type its script classifies; both checkers give 0 errors on the skill.
- [ ] DC-2 - verify by: the Step 4 checks.
- [ ] DC-3 - verify by: a manual check of `skills/explain-skills-in-details` and `bench/skill-token/versions/v2.1`, using only the references, gives the same findings as the scripts (the scripts give 0 errors and 1 WARN on v2.1, the missing "when" trigger).
- [ ] DC-4 - verify by: the Step 5 selftests, including the deliberate failure.
- [ ] DC-5 - verify by: the Step 6 checks.

## Stop conditions
- Stop and ask if:
  - a rule in the scripts differs from this plan's Context (the scripts changed since the plan was written);
  - `SKILL.md` would go over 500 lines or need a rule removed;
  - the DC-3 manual run gives different findings from the scripts and the difference can't be fixed in the references.
- Don't change the scripts' rules or messages; this plan only adds references, one SKILL.md fallback, and the selftest drift check.

## Contacts
- Owner: the user (sole author). No CODEOWNERS.
- Needs owner review: no (6 files, no API, schema, auth or CI change).

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | `skills/agent-markdown-check/references/` holds `common.md`, `claude-code.md` and `github-copilot.md`, which together state every rule the two scripts check, with the same ERROR/WARN level and message text | Original |
| DC-2 | `SKILL.md` tells the agent to use the references when Python 3.10+ or a shell isn't available, to load only the needed provider file, and to mark the report "(manual check)" | Original |
| DC-3 | A manual check with only the references gives the same findings as the scripts on `skills/explain-skills-in-details` and `bench/skill-token/versions/v2.1` | Original |
| DC-4 | Each script's `--selftest` fails when a known frontmatter key or model alias is missing from its reference file | Original |
| DC-5 | `PROVENANCE.md` has a new timeline row and a new fingerprint row for the changed skill | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-1 | Could | How many reference files? | Three: `common.md` plus one per provider, so the agent loads only what it needs | Assumption |
| Q-2 | DC-1 | Could | Which source wins when references and scripts differ? | The scripts; the references are fixed to match | Assumption |
| Q-3 | DC-2 | Could | When is Python "not usable"? | `python --version` fails or is below 3.10, or the environment has no shell tool | Assumption |
| Q-4 | DC-4 | Could | How to keep the references in sync? | A selftest check on the key and model lists (the parts most likely to change) | Assumption |
| Q-5 | DC-3 | Could | Which folders to compare manual and script results on? | `skills/explain-skills-in-details` (8 files, links) and `bench/skill-token/versions/v2.1` (2 skills, scripts folder, one WARN) | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
| 2026-11-26 | Plan created | - |
