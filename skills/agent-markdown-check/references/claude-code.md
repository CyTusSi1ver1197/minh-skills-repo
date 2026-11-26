# Manual check: Claude Code

Read [common.md](common.md) first. It has the procedure, the common checklists and the report format. `<Provider>` is `Claude Code`. This file matches `scripts/check_claude.py`.

## File types
| Path | Type |
|---|---|
| `<folder>/SKILL.md` | skill |
| `CLAUDE.md`, `CLAUDE.local.md` | memory |
| `.claude/agents/*.md` (the folder right after the last `.claude` is `agents`) | agent |
| `.claude/commands/*.md` | command |
| Anything else | skipped |

## Skill extras
After the common Skill checklist:
- [WARN] `name` contains `anthropic` or `claude` → "name contains a reserved word ('anthropic' or 'claude'); claude.ai and the API reject it"
- The Model check below, when `model` is set.

## Agent checklist (subagents)
- [ERROR] no frontmatter → "a subagent needs YAML frontmatter with 'name' and 'description'" (line 1; stop checking this file)
- [ERROR] `name` missing or empty → "'name' is required"
- [ERROR] `name` isn't lowercase letters, digits and hyphens → "name '<name>' must be lowercase letters, digits and hyphens"
- [ERROR] `description` missing or blank → "'description' is required; Claude uses it to decide when to delegate"
- [WARN] nothing but blank lines after the closing `---` → "no system prompt below the frontmatter"
- [WARN] a key not in the agent keys below → "unknown frontmatter key '<key>'; Claude Code may ignore it"
- The Model check below.
- Then the common Link checklist.

## Command checklist (slash commands)
Frontmatter is optional. When it is present:
- [WARN] a key not in the command keys below → "unknown frontmatter key '<key>'; Claude Code may ignore it"
- The Model check below.

Then the common Link checklist.

## Memory checklist (CLAUDE.md)
- [WARN] the file has frontmatter → "CLAUDE.md doesn't use frontmatter; it is read as plain text" (line 1)
- [WARN] the file is over 40,000 chars → "<n> chars; over 40000 chars slows every session"
- [ERROR] an import that doesn't exist → "@import not found: <path>"
  - An import is `@` followed by a path, in prose only (not in code blocks or inline code), not directly after a letter, digit, `_` or `@`. So `me@example.com` is not an import.
  - Strip trailing `.`, `,`, `;` or `:` from the path. Only paths that contain `/` or `.` count. `@someone` is a mention, not an import.
  - `~/path` is under the home folder. Anything else is relative to the CLAUDE.md file's folder.
- Then the common Link checklist.

## Model check
When `model` is a non-empty single value:
- [WARN] it isn't one of the values below and doesn't start with `claude-` → "model '<model>' is not an alias (fable, haiku, inherit, opus, sonnet) or a 'claude-' model id"

## Model values
`sonnet`, `opus`, `haiku`, `fable`, `inherit`, or any id starting with `claude-`.

## Known frontmatter keys
- Skill: `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`, `model`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `context`, `agent`, `hooks`
- Agent: `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `skills`, `hooks`, `color`, `memory`, `mcpServers`
- Command: `description`, `allowed-tools`, `argument-hint`, `model`, `disable-model-invocation`
