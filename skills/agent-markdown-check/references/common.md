# Manual check: common rules

## When to use this file
Use this file only when the scripts can't run: `python --version` fails or shows a version older than 3.10, or the environment has no shell tool. Read this file plus **one** provider file: [claude-code.md](claude-code.md) or [github-copilot.md](github-copilot.md). The scripts are the reference: if this file and a script disagree, the script is right.

Each rule below is written as `- [LEVEL] rule → "message"`. Report a finding with exactly that message, filling in the `<...>` parts.

## Procedure
1. **List the files.** For each given path, use the file-list tool. A folder is scanned recursively for `*.md` files. Skip anything under `.git`, `node_modules`, `__pycache__` or `.venv`. A path that doesn't exist: `- [ERROR] → "path not found"`.
2. **Group skills.** Every folder that holds a `SKILL.md` is one skill. All `*.md` files inside it belong to that skill. Don't classify them on their own.
3. **Classify the other files** with the provider file's `## File types` table.
   - No match: the file is *skipped*. Still run the Frontmatter checklist on it if it starts with `---`, and report what you find.
4. **Check.**
   - Each skill: the Frontmatter, Skill and Link checklists below, plus the provider file's skill extras.
   - Each other file: the Frontmatter checklist, its provider type checklist, then the Link checklist.
5. **Report** in the format at the end of this file.

## Frontmatter checklist
Frontmatter is the block between a first line `---` and the next line that is exactly `---`. A file that doesn't start with `---` has no frontmatter.

- [WARN] the file starts with a UTF-8 BOM (U+FEFF; best effort: search for it at the start of line 1, since read tools may hide it) → "starts with a UTF-8 BOM; some loaders then miss the frontmatter"
- [ERROR] no closing `---` line → "frontmatter is not closed with '---'"
- [ERROR] a line is indented with a tab → "tab indentation in frontmatter"
- [ERROR] an indented line that doesn't belong to the key above it → "unexpected indented line"
- [ERROR] a top-level line that isn't `key: value` (or `key:` followed by indented lines) → "not a 'key: value' line: <first 60 chars of the line>"
- [ERROR] the same key twice → "duplicate key '<key>'"
- [ERROR] a value starts with a quote but doesn't end with the same quote → "'<key>': quote is not closed"
- [ERROR] a value starts with `[` but doesn't end with `]` → "'<key>': '[' list is not closed"
- [ERROR] an unquoted value starts with `@`, `` ` ``, `%`, `&`, `*`, `!` or `{` → "'<key>': a plain YAML value can't start with '<char>'; quote the value"
- [ERROR] an unquoted value contains `: ` (colon then space) → "'<key>': unquoted ': ' inside the value breaks YAML; wrap the value in quotes"
- [WARN] an unquoted value contains ` #` (space then hash) → "'<key>': ' #' starts a YAML comment, so the rest is dropped; quote the value"
- [ERROR] the file isn't UTF-8 text → "not UTF-8 text"

Quoted values (`"..."` or `'...'`) and block values (`|`, `>`) may contain `: ` and `#`.

## Skill checklist
For `<folder>/SKILL.md`. The Frontmatter checklist runs on `SKILL.md` only, not on the other files in the skill folder. The rules in this section have no line number, so report them as `<path>` without `:<line>`, apart from the first rule (line 1).
- [ERROR] no frontmatter → "no YAML frontmatter (the file must start with '---')"
- [ERROR] `name` missing or empty → "'name' is required"
- [ERROR] `name` isn't lowercase letters and digits in parts joined by single hyphens (`a-b2-c`), or is over 64 chars → "name '<name>' must be lowercase letters, digits and single hyphens, at most 64 chars"
- [ERROR] `name` differs from the folder name → "name '<name>' must equal the folder name '<folder>'"
- [ERROR] `description` missing or blank → "'description' is required"
- [ERROR] `description` over 1024 chars → "description is <n> chars; the limit is 1024"
- [ERROR] `description` contains a tag such as `<b>` or `</x>` → "description must not contain XML/HTML tags"
- [WARN] `description` doesn't contain the word "when" (any case) → "description has no trigger ('Use when ...'), so the agent may not know when to load it"
- [WARN] more than 500 lines after the closing `---` → "SKILL.md body is over 500 lines; move detail into references/"
- [WARN] a frontmatter key not in the provider file's known keys for skills → "unknown frontmatter key '<key>'; <Provider> may ignore it"

Then run the Link checklist on `SKILL.md` and on every other `*.md` file in the skill folder, except files under `assets/`. Those are templates, and their links only resolve in the files generated from them.

## Link checklist
Check only prose: skip everything inside fenced code blocks (between ```` ``` ```` or `~~~` lines). For Markdown links, also skip inline code spans.

- [ERROR] a Markdown link `[text](target)` whose target (the part before any `#`) doesn't exist, relative to the file's folder → "link target not found: <target>"
  - Skip targets starting with `http:`, `https:`, `mailto:` or `#`, and targets containing `<`, `*`, `{`, `$` or `%`.
- [WARN] inside a skill, a link target that exists but lies outside the skill folder → "link leaves the skill folder, so it isn't shipped with the skill: <target>"
- [ERROR] inside a skill, a bare path such as `references/<file>.md`, `assets/<file>.md` or `scripts/<file>.py` (extensions md, py, json, txt, sh, ps1, js, ts, yaml, yml), including one in inline code, that exists neither from the skill folder nor from the file's folder → "names missing file <path>"
  - Paths with `/` or `.` right before `references`, `assets` or `scripts` are part of a longer path; skip them.
- [WARN] an absolute path in prose (outside inline code), such as a drive letter path or a path under the home, Users or root folder → "absolute path; it breaks on other machines"

Use the file-list or file-read tool to check that a target exists. Don't guess.

## Report format
One line per finding, ERRORs first, then by path:

```
ERROR <path>:<line>  <message>
WARN  <path>:<line>  <message>
```

Leave out `:<line>` when a rule has no line, such as missing keys. Paths are relative to the working folder. End with this summary line:

```
<Provider>: <n> checked, <n> skipped (not a <Provider> file type), <n> error(s), <n> warning(s) (manual check)
```

`<Provider>` is `Claude Code` or `GitHub Copilot`. Count each skill as 1 checked, plus each classified file. Any ERROR means the check failed.
