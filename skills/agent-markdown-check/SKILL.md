---
name: agent-markdown-check
description: "Use when asked to check, lint or validate Markdown files for Claude Code or GitHub Copilot: skills (SKILL.md folders), subagents, slash commands, CLAUDE.md, custom agents (.agent.md), prompt files, instruction files, copilot-instructions.md or AGENTS.md. Runs one stdlib Python checker per provider and reports errors and warnings with file:line."
license: MIT
---
<!-- © 2026 Nguyen Phuc Quang Minh. Personal work, created outside employment. Licensed under the MIT License (see LICENSE in the repository root). -->

# Agent Markdown check

Check whether Markdown files meet the rules of Claude Code, GitHub Copilot, or both. The scripts do the checking; your job is to run the right one, report the result and, when asked, fix the files.

## Steps

1. **Pick the provider.**
   - Claude Code: `scripts/check_claude.py`.
   - GitHub Copilot: `scripts/check_copilot.py`.
   - A file meant for both (for example a skill shared by both tools): run both.
   - Not stated: infer it from the path (`.claude/` means Claude Code; `.github/`, `.agent.md`, `.prompt.md` or `.instructions.md` means Copilot). A `SKILL.md` or `AGENTS.md` outside those folders: run both.
2. **Run it**, with Python 3.10+ and no installs:
   `python <this skill's folder>/scripts/check_claude.py <file or folder> [...]`
   - Folders are scanned recursively.
   - A folder holding a `SKILL.md` is checked as one skill: its frontmatter plus every Markdown file and link inside it.
   - The file type comes from the path. For a draft outside its usual place, add `--as <type>`. `--help` lists the types.
   - If Python 3.10+ or a shell isn't available (`python --version` fails or is older), check by hand instead: read [references/common.md](references/common.md) and the one provider file ([references/claude-code.md](references/claude-code.md) or [references/github-copilot.md](references/github-copilot.md)), follow its procedure, and report in the same format with " (manual check)" on the summary line.
3. **Report.** Show the findings, then the summary line.
   - `ERROR`: the tool rejects or misreads the file. Exit code 1 means at least one ERROR.
   - `WARN`: the file loads but will probably misbehave, or uses a key the tool may ignore.
   - "skipped" files are not a file type of that provider. That's not a failure.
4. **Fix only when asked.** Fix ERRORs first, then re-run until 0 errors. Don't edit a frozen snapshot or a file the user didn't name; report it instead.

## What is checked

Skills (`<name>/SKILL.md`), both providers: frontmatter parses; `name` is required, lowercase-hyphen, ≤ 64 chars and equals the folder name; `description` is required, ≤ 1024 chars, no XML tags, has a "when" trigger; body ≤ 500 lines; every link and `references/`, `assets/` or `scripts/` path exists and stays inside the folder (links in `assets/` templates are skipped).

| Type | Claude Code | GitHub Copilot |
|---|---|---|
| Skill extras | Warns on the reserved words `anthropic`/`claude` in `name` | Warns that `model` is ignored (pin it in a custom agent) |
| Agent | `.claude/agents/*.md`: `name` and `description` required; `model` is an alias or `claude-` id | `*.agent.md`: `description` required; `model` list works in VS Code only; `.chatmode.md` is the old name |
| Command / prompt | `.claude/commands/*.md`: known keys only | `*.prompt.md`: known keys; `mode` is the old key for `agent` |
| Instructions | `CLAUDE.md`: no frontmatter; every `@import` exists; ≤ 40,000 chars | `*.instructions.md`: `applyTo` set and not empty; `copilot-instructions.md`: no frontmatter; both ≤ 4,000 chars for code review |
| Any file | YAML subset (unquoted `: `, tabs, unclosed quotes, duplicate keys), broken relative links, absolute paths | Same |

## Limits

- The frontmatter parser covers the YAML that agent files use. It catches the common breakages, but it is not a full YAML parser.
- The rules follow the Agent Skills spec, the Claude Code docs and the GitHub Copilot docs as of 2026-11. Unknown keys are WARN, not ERROR, because the providers add keys over time.
- The manual check follows the same rules but is slower and can miss findings on large folders; prefer the scripts when they run.
- It doesn't check prompt quality, whether a model is enabled for the user, or whether a tool name in `tools` exists.
