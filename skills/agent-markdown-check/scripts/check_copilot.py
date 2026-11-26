# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Nguyen Phuc Quang Minh
"""Check Markdown files against GitHub Copilot rules (VS Code, Copilot CLI, GitHub.com).

Usage: python check_copilot.py <file|folder>... [--as TYPE] [--selftest]

Types (found by path):
  skill              <name>/SKILL.md, checked with every Markdown file in its folder
  agent              .github/agents/*.md, ~/.copilot/agents/*.md (custom agents); *.chatmode.md (old name)
  prompt             *.prompt.md (prompt files)
  instructions       *.instructions.md (path-specific instructions)
  repo-instructions  .github/copilot-instructions.md
  agents-md          AGENTS.md
Exit 1 if any ERROR.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402

PROVIDER = "GitHub Copilot"
KINDS = ["skill", "agent", "prompt", "instructions", "repo-instructions", "agents-md"]
# ponytail: key lists follow the GitHub/VS Code docs as of 2026-11; unknown keys only WARN, so update when docs add keys
SKILL_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility", "argument-hint",
              "user-invokable", "user-invocable", "disable-model-invocation", "model"}
AGENT_KEYS = {"name", "description", "argument-hint", "tools", "model", "target", "handoffs", "mcp-servers",
              "infer", "metadata", "user-invokable", "disable-model-invocation"}
PROMPT_KEYS = {"name", "description", "argument-hint", "agent", "mode", "model", "tools"}
INSTRUCTION_KEYS = {"name", "description", "applyTo", "excludeAgent"}
REVIEW_CHARS = 4000  # Copilot code review reads only the first 4,000 chars of an instruction file
HOME_DIR = {"agent": "agents", "prompt": "prompts", "instructions": "instructions"}


def classify(p: Path) -> str | None:
    n = p.name.lower()
    parts = [x.lower() for x in p.parts]
    if p.name == "SKILL.md":
        return "skill"
    if n == "copilot-instructions.md":
        return "repo-instructions"
    if n == "agents.md":
        return "agents-md"
    if n.endswith(".instructions.md"):
        return "instructions"
    if n.endswith(".prompt.md"):
        return "prompt"
    # *.agent.md elsewhere (e.g. BuildPlans/PLAN.agent.md) isn't loaded by Copilot; use --as agent for drafts
    if n.endswith(".chatmode.md") or p.parent.name.lower() == "agents" and (".github" in parts or ".copilot" in parts):
        return "agent"
    return None


def check(path: Path, kind: str, rep: c.Report) -> None:
    if kind == "skill":
        folder = path.parent if path.is_file() else path
        fm = c.check_skill(folder, rep, SKILL_KEYS, PROVIDER)
        if fm and "model" in fm:
            rep.warn(folder / "SKILL.md", "Copilot skills can't choose the model, so 'model' is ignored; "
                                          "pin a model in a custom agent (.agent.md) instead")
        return
    text = c.read(path, rep)
    if text is None:
        return
    fm, start = c.frontmatter(text, path, rep)
    sub = HOME_DIR.get(kind)
    if sub and f".github/{sub}" not in path.resolve().as_posix().lower():
        rep.warn(path, f"not under .github/{sub}/; Copilot finds it only there or in a folder set in VS Code settings")
    if kind == "agent":
        if path.name.lower().endswith(".chatmode.md"):
            rep.warn(path, "'.chatmode.md' is the old name; rename the file to '.agent.md'")
        if fm is None or not isinstance(fm.get("description"), str) or not fm["description"].strip():
            rep.err(path, "'description' is required in the frontmatter of a custom agent", 1)
        if fm:
            c.unknown_keys(fm, AGENT_KEYS, path, rep, PROVIDER)
            if isinstance(fm.get("model"), list):
                rep.warn(path, "'model' as a list works in VS Code only; Copilot CLI takes a single string")
    elif kind == "prompt":
        if fm:
            c.unknown_keys(fm, PROMPT_KEYS, path, rep, PROVIDER)
            if "mode" in fm:
                rep.warn(path, "'mode' is the old key; use 'agent'")
    elif kind == "instructions":
        apply_to = (fm or {}).get("applyTo")
        if apply_to is None:
            rep.warn(path, "no 'applyTo' glob, so the file is applied only when attached by hand", 1)
        elif not str(apply_to).strip():
            rep.err(path, "'applyTo' is empty; give a glob such as '**/*.py'")
        if fm:
            c.unknown_keys(fm, INSTRUCTION_KEYS, path, rep, PROVIDER)
    elif kind in ("repo-instructions", "agents-md") and fm is not None:
        rep.warn(path, "this file doesn't use frontmatter; it is read as plain text", 1)
    if kind in ("instructions", "repo-instructions") and len(text) > REVIEW_CHARS:
        rep.warn(path, f"{len(text)} chars; Copilot code review reads only the first {REVIEW_CHARS}")
    c.check_links(path, text, start, rep)


def selftest() -> None:
    c.assert_in_reference(__file__, "github-copilot.md", SKILL_KEYS | AGENT_KEYS | PROMPT_KEYS | INSTRUCTION_KEYS)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        c.write_tree(root, {
            "good-skill/SKILL.md": "---\nname: good-skill\ndescription: Use when testing.\nlicense: MIT\n---\nBody.\n",
            "pinned/SKILL.md": "---\nname: pinned\ndescription: Use when testing.\nmodel: gpt-6-luna\n---\nBody.\n",
            ".github/agents/quick.agent.md": "---\nname: quick\ndescription: Small jobs.\nmodel: GPT-6 Luna\n---\nGo.\n",
            ".github/agents/broken.agent.md": "---\nname: broken\nmodel: [GPT-6 Luna, GPT-6.1 Sol]\n---\nGo.\n",
            "old.chatmode.md": "---\ndescription: Old.\n---\nGo.\n",
            ".github/prompts/fix.prompt.md": "---\nmode: agent\ndescription: Fix it.\n---\nFix.\n",
            ".github/instructions/py.instructions.md": "Use type hints.\n",
            ".github/instructions/empty.instructions.md": "---\napplyTo: ''\n---\nx\n",
            ".github/copilot-instructions.md": "x" * (REVIEW_CHARS + 1),
            "AGENTS.md": "See [plan](missing.md).\n",
            "notes.md": "plain\n",
            "BuildPlans/x/PLAN.agent.md": "# EXECUTION PLAN\n",
        })
        rep = c.Report()
        checked, skipped = c.scan([root], None, classify, check, rep)
        assert (checked, skipped) == (10, 2), (checked, skipped)
        assert not any("good-skill" in w or "quick.agent" in w for _, w, _ in rep.items), rep.items
        for level, where, text in [
            ("WARN", "pinned/SKILL.md", "'model' is ignored"),
            ("ERROR", "broken.agent.md", "'description' is required"),
            ("WARN", "broken.agent.md", "Copilot CLI takes a single string"),
            ("WARN", "old.chatmode.md", "old name"), ("WARN", "old.chatmode.md", "not under .github/agents/"),
            ("WARN", "fix.prompt.md", "'mode' is the old key"),
            ("WARN", "py.instructions.md", "no 'applyTo'"), ("ERROR", "empty.instructions.md", "'applyTo' is empty"),
            ("WARN", "copilot-instructions.md", "reads only the first"),
            ("ERROR", "AGENTS.md", "link target not found: missing.md"),
        ]:
            assert c.has(rep, level, where, text), (level, where, text, rep.items)
        assert rep.count("ERROR") == 3, rep.items


if __name__ == "__main__":
    sys.exit(c.run(sys.argv[1:], PROVIDER, KINDS, classify, check, selftest, __doc__))
