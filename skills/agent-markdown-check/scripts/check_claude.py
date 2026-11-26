# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Nguyen Phuc Quang Minh
"""Check Markdown files against Claude Code rules.

Usage: python check_claude.py <file|folder>... [--as skill|agent|command|memory] [--selftest]

Types (found by path):
  skill    <name>/SKILL.md, checked with every Markdown file in its folder
  agent    .claude/agents/*.md (subagents)
  command  .claude/commands/*.md (slash commands)
  memory   CLAUDE.md, CLAUDE.local.md
Exit 1 if any ERROR.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402

PROVIDER = "Claude Code"
KINDS = ["skill", "agent", "command", "memory"]
# ponytail: key lists follow the Claude Code docs as of 2026-11; unknown keys only WARN, so update when docs add keys
SKILL_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility", "model",
              "argument-hint", "disable-model-invocation", "user-invocable", "context", "agent", "hooks"}
AGENT_KEYS = {"name", "description", "tools", "disallowedTools", "model", "permissionMode", "skills",
              "hooks", "color", "memory", "mcpServers"}
COMMAND_KEYS = {"description", "allowed-tools", "argument-hint", "model", "disable-model-invocation"}
MODEL_ALIASES = {"sonnet", "opus", "haiku", "fable", "inherit"}
IMPORT_RE = re.compile(r"(?<![\w@])@((?:~/|\.{1,2}/)?[\w.-]+(?:/[\w.-]+)*)")
MEMORY_WARN_CHARS = 40_000


def classify(p: Path) -> str | None:
    if p.name == "SKILL.md":
        return "skill"
    if p.name in ("CLAUDE.md", "CLAUDE.local.md"):
        return "memory"
    parts = [x.lower() for x in p.parts]
    if ".claude" in parts:
        i = len(parts) - 1 - parts[::-1].index(".claude")
        sub = parts[i + 1] if i + 1 < len(parts) else ""
        return {"agents": "agent", "commands": "command"}.get(sub)
    return None


def check_model(fm: dict, path: Path, rep: c.Report) -> None:
    model = fm.get("model")
    if isinstance(model, str) and model and model not in MODEL_ALIASES and not model.startswith("claude-"):
        rep.warn(path, f"model '{model}' is not an alias ({', '.join(sorted(MODEL_ALIASES))}) or a 'claude-' model id")


def check(path: Path, kind: str, rep: c.Report) -> None:
    if kind == "skill":
        folder = path.parent if path.is_file() else path
        fm = c.check_skill(folder, rep, SKILL_KEYS, PROVIDER)
        if fm and isinstance(fm.get("name"), str) and re.search("anthropic|claude", fm["name"]):
            rep.warn(folder / "SKILL.md", "name contains a reserved word ('anthropic' or 'claude'); "
                                          "claude.ai and the API reject it")
        if fm:
            check_model(fm, folder / "SKILL.md", rep)
        return
    text = c.read(path, rep)
    if text is None:
        return
    fm, start = c.frontmatter(text, path, rep)
    if kind == "agent":
        if fm is None:
            rep.err(path, "a subagent needs YAML frontmatter with 'name' and 'description'", 1)
            return
        name = fm.get("name")
        if not isinstance(name, str) or not name:
            rep.err(path, "'name' is required")
        elif not c.NAME_RE.fullmatch(name):
            rep.err(path, f"name '{name}' must be lowercase letters, digits and hyphens")
        if not isinstance(fm.get("description"), str) or not fm["description"].strip():
            rep.err(path, "'description' is required; Claude uses it to decide when to delegate")
        if not text.split("\n")[start - 1:] or not "".join(text.split("\n")[start - 1:]).strip():
            rep.warn(path, "no system prompt below the frontmatter")
        c.unknown_keys(fm, AGENT_KEYS, path, rep, PROVIDER)
        check_model(fm, path, rep)
    elif kind == "command":
        if fm:
            c.unknown_keys(fm, COMMAND_KEYS, path, rep, PROVIDER)
            check_model(fm, path, rep)
    elif kind == "memory":
        if fm is not None:
            rep.warn(path, "CLAUDE.md doesn't use frontmatter; it is read as plain text", 1)
        if len(text) > MEMORY_WARN_CHARS:
            rep.warn(path, f"{len(text)} chars; over {MEMORY_WARN_CHARS} chars slows every session")
        for n, _, prose in c.body_lines(text, start):
            for ref in IMPORT_RE.findall(prose):
                ref = ref.rstrip(".,;:")
                if "/" not in ref and "." not in ref:
                    continue  # a mention like @user, not a file import
                dest = Path.home() / ref[2:] if ref.startswith("~/") else path.parent / ref
                if not dest.exists():
                    rep.err(path, f"@import not found: {ref}", n)
    c.check_links(path, text, start, rep)


def selftest() -> None:
    c.assert_in_reference(__file__, "claude-code.md", SKILL_KEYS | AGENT_KEYS | COMMAND_KEYS | MODEL_ALIASES)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        c.write_tree(root, {
            "good-skill/SKILL.md": "---\nname: good-skill\ndescription: \"Use when testing: a quoted colon is fine.\"\n"
                                   "---\nSee [a](references/a.md) and `references/a.md`.\n",
            "good-skill/references/a.md": "# A\n",
            "bad/SKILL.md": "---\nname: Bad_Name\ndescription: Use when: testing\nlicense: MIT\nlicense: X\n---\n"
                            "Read references/missing.md and [x](./nope.md).\n```\n[ignored](in-code.md)\n```\n",
            ".claude/agents/rev.md": "---\nname: rev\nmodel: gpt-6\n---\nReview code.\n",
            ".claude/commands/go.md": "Run it.\n",
            "CLAUDE.md": "@AGENTS.md\n@docs/ok.md\nMail me@example.com. Ask @someone.\n`@not/checked.md`\n",
            "docs/ok.md": "ok\n",
            "notes.md": "plain notes\n",
        })
        rep = c.Report()
        checked, skipped = c.scan([root], None, classify, check, rep)
        assert (checked, skipped) == (5, 2), (checked, skipped)  # docs/ok.md and notes.md skipped
        assert not any("good-skill" in w for _, w, _ in rep.items), rep.items
        for level, where, text in [
            ("ERROR", "bad/SKILL.md", "must be lowercase"), ("ERROR", "bad/SKILL.md", "folder name"),
            ("ERROR", "bad/SKILL.md", "unquoted ': '"), ("ERROR", "bad/SKILL.md", "duplicate key"),
            ("ERROR", "bad/SKILL.md", "missing file references/missing.md"),
            ("ERROR", "bad/SKILL.md", "link target not found: ./nope.md"),
            ("ERROR", "rev.md", "'description' is required"), ("WARN", "rev.md", "model 'gpt-6'"),
            ("ERROR", "CLAUDE.md", "@import not found: AGENTS.md"),
        ]:
            assert c.has(rep, level, where, text), (level, where, text, rep.items)
        assert not c.has(rep, "ERROR", "", "in-code.md") and not c.has(rep, "ERROR", "", "example.com")
        assert not c.has(rep, "ERROR", "", "docs/ok.md") and not c.has(rep, "ERROR", "", "not/checked")
        assert rep.count("ERROR") == 8, rep.items


if __name__ == "__main__":
    sys.exit(c.run(sys.argv[1:], PROVIDER, KINDS, classify, check, selftest, __doc__))
