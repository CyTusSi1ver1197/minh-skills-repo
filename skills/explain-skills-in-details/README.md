# explain-skills-in-details (Agent Skill)

Personal skill for GitHub Copilot agent mode in VS Code and Visual Studio
(also works in Claude Code). Model-agnostic.

## Install (Windows, personal scope)

Copy the whole folder (not just SKILL.md) to:

```
%USERPROFILE%\.copilot\skills\explain-skills-in-details\
```

The folder name must equal the `name` in SKILL.md.

## Structure

```
explain-skills-in-details/
├── SKILL.md                      # router: loaded when the skill triggers
├── references/                   # loaded one stage at a time
│   ├── stage-a-ground.md         # Steps 1–4
│   ├── stage-b-build.md          # Steps 5–7
│   ├── stage-c-use.md            # Steps 8–10
│   └── style-and-depth.md
└── assets/
    ├── checkpoint-template.md    # state file written to .explain/
    └── output-template.md
```

## Use

- Automatic: ask "explain X" in agent mode.
- Manual: `/explain-skills-in-details dependency injection, I know OOP, working`.
- Say `continue` to get the next stage.

## Notes

- The skill writes `.explain/<topic>.md` in the open workspace as a
  checkpoint. Add `.explain/` to `.gitignore` (or `.git/info/exclude`
  for a company repo you don't want to change).
- Requirements: VS Code with agent skills enabled; Visual Studio 2026 18.5+.
