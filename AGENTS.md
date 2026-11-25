# Agent rules

## Provenance (always)

Whenever you create or modify a skill, update `PROVENANCE.md` in the same change. A skill is any `SKILL.md`, or any file in its `references/`, `assets/` or `scripts/` folders, including the snapshots in `bench/skill-token/versions/`.

1. Add a timeline row: date and time (Asia/Bangkok), version, what changed, where (tool, device), and the source (plan file, benchmark results).
2. Write only facts you can source. If the device or work-hours status is unknown, write "to be confirmed by the author". Never guess it.
3. For a new or changed snapshot in `bench/skill-token/versions/<version>/`, recompute its fingerprint with the command in `PROVENANCE.md` and update the fingerprint table.
4. Never edit an existing timeline row's facts or a frozen snapshot's files. Correct mistakes with a new row.
5. Keep company names, internal URLs and private evidence out of the repo.
