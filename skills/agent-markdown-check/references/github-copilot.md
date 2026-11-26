# Manual check: GitHub Copilot

Read [common.md](common.md) first. It has the procedure, the common checklists and the report format. `<Provider>` is `GitHub Copilot`. This file matches `scripts/check_copilot.py`.

## File types
Check the rows in order; the first match wins. File names compare case-insensitively.

| Path | Type |
|---|---|
| `<folder>/SKILL.md` | skill |
| `copilot-instructions.md` | repo-instructions |
| `AGENTS.md` | agents-md |
| `*.instructions.md` | instructions |
| `*.prompt.md` | prompt |
| `*.chatmode.md`, or any `.md` whose folder is `agents` inside `.github` or `.copilot` | agent |
| Anything else, including `*.agent.md` in other folders (such as `BuildPlans/.../PLAN.agent.md`) | skipped |

## Skill extras
After the common Skill checklist:
- [WARN] `model` is present → "Copilot skills can't choose the model, so 'model' is ignored; pin a model in a custom agent (.agent.md) instead"

## Location check
For agent, prompt and instructions files:
- [WARN] the path doesn't contain `.github/agents`, `.github/prompts` or `.github/instructions` (matching the type) → "not under .github/<agents|prompts|instructions>/; Copilot finds it only there or in a folder set in VS Code settings"

## Agent checklist (custom agents)
- [WARN] the file name ends with `.chatmode.md` → "'.chatmode.md' is the old name; rename the file to '.agent.md'"
- [ERROR] no frontmatter, or `description` missing or blank → "'description' is required in the frontmatter of a custom agent" (line 1)
- [WARN] a key not in the agent keys below → "unknown frontmatter key '<key>'; GitHub Copilot may ignore it"
- [WARN] `model` is a list (`[a, b]` or `- a` lines) → "'model' as a list works in VS Code only; Copilot CLI takes a single string"

## Prompt checklist (prompt files)
Frontmatter is optional. When it is present:
- [WARN] a key not in the prompt keys below → "unknown frontmatter key '<key>'; GitHub Copilot may ignore it"
- [WARN] `mode` is present → "'mode' is the old key; use 'agent'"

## Instructions checklist (*.instructions.md)
- [WARN] no frontmatter or no `applyTo` key → "no 'applyTo' glob, so the file is applied only when attached by hand" (line 1)
- [ERROR] `applyTo` is empty or only spaces → "'applyTo' is empty; give a glob such as '**/*.py'"
- [WARN] a key not in the instructions keys below → "unknown frontmatter key '<key>'; GitHub Copilot may ignore it"
- [WARN] the file is over 4,000 chars → "<n> chars; Copilot code review reads only the first 4000"

## repo-instructions and agents-md checklist
- [WARN] the file has frontmatter → "this file doesn't use frontmatter; it is read as plain text" (line 1)
- repo-instructions only: [WARN] the file is over 4,000 chars → "<n> chars; Copilot code review reads only the first 4000"

Each non-skill type then runs the common Link checklist. Skills already run it as part of the common Skill checklist.

## Known frontmatter keys
- Skill: `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`, `argument-hint`, `user-invokable`, `user-invocable`, `disable-model-invocation`, `model`
- Agent: `name`, `description`, `argument-hint`, `tools`, `model`, `target`, `handoffs`, `mcp-servers`, `infer`, `metadata`, `user-invokable`, `disable-model-invocation`
- Prompt: `name`, `description`, `argument-hint`, `agent`, `mode`, `model`, `tools`
- Instructions: `name`, `description`, `applyTo`, `excludeAgent`
