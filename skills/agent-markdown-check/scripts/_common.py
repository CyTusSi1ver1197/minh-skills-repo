# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Nguyen Phuc Quang Minh
"""Shared parsing and reporting for check_claude.py and check_copilot.py (stdlib only)."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
LINK_RE = re.compile(r"\]\((?!https?:|mailto:|#)([^)\s]+)\)")
BARE_REF = re.compile(r"(?<![\w/.-])((?:references|assets|scripts)/[\w./-]+?\.(?:md|py|json|txt|sh|ps1|js|ts|ya?ml))")
ABS_RE = re.compile(r"(?<![\w<])(?:[A-Za-z]:[\\/]\w|/(?:home|Users|root)/)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}


class Report:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str]] = []

    def _add(self, level: str, path: Path, msg: str, line: int | None) -> None:
        try:
            shown = path.resolve().relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            shown = path.as_posix()
        self.items.append((level, f"{shown}:{line}" if line else shown, msg))

    def err(self, path: Path, msg: str, line: int | None = None) -> None:
        self._add("ERROR", path, msg, line)

    def warn(self, path: Path, msg: str, line: int | None = None) -> None:
        self._add("WARN", path, msg, line)

    def count(self, level: str) -> int:
        return sum(1 for lv, _, _ in self.items if lv == level)

    def finish(self, provider: str, checked: int, skipped: int) -> int:
        for level, where, msg in sorted(self.items, key=lambda x: (x[0] != "ERROR", x[1])):
            print(f"{level:5} {where}  {msg}")
        print(f"{provider}: {checked} checked, {skipped} skipped (not a {provider} file type), "
              f"{self.count('ERROR')} error(s), {self.count('WARN')} warning(s)")
        return 1 if self.count("ERROR") else 0


def read(path: Path, rep: Report) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        rep.err(path, "not UTF-8 text")
        return None
    if text.startswith("﻿"):
        rep.warn(path, "starts with a UTF-8 BOM; some loaders then miss the frontmatter", 1)
        text = text[1:]
    return text.replace("\r\n", "\n")


def _value(key: str, val: str, block: list[str], path: Path, rep: Report, ln: int):
    items = [b.strip() for b in block if b.strip() and not b.strip().startswith("#")]
    if not val:
        if items and all(x == "-" or x.startswith("- ") for x in items):
            return [x[1:].strip().strip("\"'") for x in items]
        return {"_nested": items} if items else ""
    if val[0] in "|>":
        return " ".join(items)
    if val[0] in "\"'":
        joined = " ".join([val] + items)
        if len(joined) < 2 or not joined.endswith(val[0]):
            rep.err(path, f"'{key}': quote is not closed", ln)
        return joined[1:-1]
    if val.startswith("["):
        if not val.endswith("]"):
            rep.err(path, f"'{key}': '[' list is not closed", ln)
        return [x.strip().strip("\"'") for x in val.strip("[]").split(",") if x.strip()]
    if val[0] in "@`%&*!{":
        rep.err(path, f"'{key}': a plain YAML value can't start with '{val[0]}'; quote the value", ln)
    if ": " in val:
        rep.err(path, f"'{key}': unquoted ': ' inside the value breaks YAML; wrap the value in quotes", ln)
    if " #" in val:
        rep.warn(path, f"'{key}': ' #' starts a YAML comment, so the rest is dropped; quote the value", ln)
        val = val.split(" #")[0]
    return " ".join([val] + items)


def frontmatter(text: str, path: Path, rep: Report) -> tuple[dict | None, int]:
    """Parse the YAML subset used in agent Markdown. Returns (data or None, first body line)."""
    if not text.startswith("---\n"):
        return None, 1
    lines = text.split("\n")
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        rep.err(path, "frontmatter is not closed with '---'", 1)
        return {}, 1
    data: dict = {}
    i = 1
    while i < end:
        raw, ln = lines[i], i + 1
        i += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] in " \t":
            rep.err(path, "tab indentation in frontmatter" if raw[0] == "\t" else "unexpected indented line", ln)
            continue
        m = re.match(r"([\w-]+):(\s.*)?$", raw)
        if not m:
            rep.err(path, f"not a 'key: value' line: {raw.strip()[:60]}", ln)
            continue
        key = m.group(1)
        if key in data:
            rep.err(path, f"duplicate key '{key}'", ln)
        block = []
        while i < end and (not lines[i].strip() or lines[i][0] in " \t"):
            if lines[i].startswith("\t"):
                rep.err(path, "tab indentation in frontmatter", i + 1)
            block.append(lines[i])
            i += 1
        data[key] = _value(key, (m.group(2) or "").strip(), block, path, rep, ln)
    return data, end + 2


def body_lines(text: str, start: int):
    """Yield (line number, raw line, line without inline code) outside fenced code blocks."""
    fence = None
    for n, line in enumerate(text.split("\n")[start - 1:], start):
        m = FENCE_RE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)
            elif line.strip().startswith(fence):
                fence = None
            continue
        if fence is None:
            yield n, line, re.sub(r"`[^`]*`", "", line)


def check_links(md: Path, text: str, start: int, rep: Report, root: Path | None = None) -> None:
    for n, raw, prose in body_lines(text, start):
        for target in LINK_RE.findall(prose):
            target = target.split("#")[0]
            if not target or any(ch in target for ch in "<*{$%"):
                continue
            dest = (md.parent / target).resolve()
            if not dest.exists():
                rep.err(md, f"link target not found: {target}", n)
            elif root and root.resolve() not in dest.parents and dest != root.resolve():
                rep.warn(md, f"link leaves the skill folder, so it isn't shipped with the skill: {target}", n)
        if root:
            for ref in BARE_REF.findall(raw):
                if not ((root / ref).exists() or (md.parent / ref).exists()):
                    rep.err(md, f"names missing file {ref}", n)
        if ABS_RE.search(prose):
            rep.warn(md, "absolute path; it breaks on other machines", n)


def unknown_keys(fm: dict, known: set[str], path: Path, rep: Report, provider: str) -> None:
    for key in fm:
        if key not in known:
            rep.warn(path, f"unknown frontmatter key '{key}'; {provider} may ignore it")


def check_skill(folder: Path, rep: Report, known: set[str], provider: str) -> dict | None:
    """Agent Skills rules shared by both providers. Returns the frontmatter."""
    skill = folder / "SKILL.md"
    text = read(skill, rep)
    if text is None:
        return None
    fm, start = frontmatter(text, skill, rep)
    if fm is None:
        rep.err(skill, "no YAML frontmatter (the file must start with '---')", 1)
        return None
    name, desc = fm.get("name"), fm.get("description")
    if not isinstance(name, str) or not name:
        rep.err(skill, "'name' is required")
    else:
        if not NAME_RE.fullmatch(name) or len(name) > 64:
            rep.err(skill, f"name '{name}' must be lowercase letters, digits and single hyphens, at most 64 chars")
        if name != folder.name:
            rep.err(skill, f"name '{name}' must equal the folder name '{folder.name}'")
    if not isinstance(desc, str) or not desc.strip():
        rep.err(skill, "'description' is required")
    else:
        if len(desc) > 1024:
            rep.err(skill, f"description is {len(desc)} chars; the limit is 1024")
        if re.search(r"<[A-Za-z/][^>]*>", desc):
            rep.err(skill, "description must not contain XML/HTML tags")
        if not re.search(r"\bwhen\b", desc, re.I):
            rep.warn(skill, "description has no trigger ('Use when ...'), so the agent may not know when to load it")
    unknown_keys(fm, known, skill, rep, provider)
    if len(text.split("\n")) - start + 1 > 500:
        rep.warn(skill, "SKILL.md body is over 500 lines; move detail into references/")
    for md in sorted(folder.rglob("*.md")):
        if md == skill:
            check_links(md, text, start, rep, folder)
        elif "assets" in md.relative_to(folder).parts:
            continue  # templates: their links resolve only in the files generated from them
        elif (t := read(md, rep)) is not None:
            check_links(md, t, 1, rep, folder)
    return fm


def collect(paths: list[Path], rep: Report) -> list[Path]:
    files: set[Path] = set()
    for p in paths:
        if not p.exists():
            rep.err(p, "path not found")
        elif p.is_file():
            files.add(p)
        else:
            files.update(f for f in p.rglob("*.md") if not SKIP_DIRS & set(f.parts))
    return sorted(files)


def scan(paths: list[Path], kind: str | None, classify, check, rep: Report) -> tuple[int, int]:
    files = collect(paths, rep)
    skills = sorted({f.parent for f in files if f.name == "SKILL.md" and kind in (None, "skill")})
    if kind == "skill":
        skills = sorted(set(skills) | {f.parent for f in files})
    checked, skipped = len(skills), 0
    for folder in skills:
        check(folder, "skill", rep)
    for f in files:
        if any(s == f.parent or s in f.parents for s in skills):
            continue
        k = kind or classify(f)
        if k is None:
            skipped += 1
            if (t := read(f, rep)) is not None:
                frontmatter(t, f, rep)  # syntax only
            continue
        check(f, k, rep)
        checked += 1
    return checked, skipped


def run(argv: list[str], provider: str, kinds: list[str], classify, check, selftest, doc: str) -> int:
    ap = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="Markdown files or folders (scanned recursively)")
    ap.add_argument("--as", dest="kind", choices=kinds, help="treat every given file as this type")
    ap.add_argument("--selftest", action="store_true", help="run the built-in checks and exit")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        print("selftest OK")
        return 0
    if not a.paths:
        ap.error("give at least one file or folder")
    rep = Report()
    checked, skipped = scan(a.paths, a.kind, classify, check, rep)
    return rep.finish(provider, checked, skipped)


def write_tree(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def assert_in_reference(script: str, ref_name: str, words: set[str]) -> None:
    """Drift check: every key or value the script knows must appear in backticks in its manual-check reference."""
    ref = Path(script).resolve().parent.parent / "references" / ref_name
    text = ref.read_text(encoding="utf-8")
    missing = sorted(w for w in words if f"`{w}`" not in text)
    assert not missing, f"references/{ref_name} is missing: {', '.join(missing)}"


def has(rep: Report, level: str, where: str, text: str) -> bool:
    return any(lv == level and where in w and text in m for lv, w, m in rep.items)
