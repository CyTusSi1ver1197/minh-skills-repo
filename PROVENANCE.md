# Provenance

The dated record of how the skills `running-when-a-request-is-made`, `information-gathering-for-plan` and `explain-skills-in-details` were created and changed. Every row lists its source. Commit dates in git are real, not backdated; earlier creation dates are recorded here.

All times are Asia/Bangkok (UTC+7).

## Timeline

| Date / time | Version | What changed | Where | Source / evidence |
|---|---|---|---|---|
| A Sunday evening, about 20:15-22:00 (date to be filled in from the original conversation) | v1 | Both skills first written | Personal device, personal Claude account | Author's statement; timestamps of the original Claude conversation (stored privately, off-repo) |
| 2026-11-24, 10:34-18:25 | v2.0 | Progressive disclosure (references/, assets/, scripts/); benchmark harness built. Failed the token bar (more turns) | Personal Claude account; benchmark run on a personal PC; author off work that day | Author's statement; `BuildPlans/skill-token-optimization/PROGRESS.md` session log; `bench/skill-token/results/results.jsonl` |
| 2026-11-24, 10:34-18:25 | v2.1 | Fewer turns, staged plans, 5 % low-context stop | Same as v2.0 | Same as v2.0; `bench/skill-token/RESULTS.md` |
| 2026-11-25 | v2.2 | GPT-6 / Copilot fit: "Use when" descriptions, class C handled without a format question, working rules, `## Blockers` in the summary, missing-skill references removed. Copilot benchmark (DC-7) still pending | Claude Code (VS Code). Device and work-hours status: to be confirmed by the author | `BuildPlans/gpt6-model-fit/PROGRESS.md` and `EXECUTION-SUMMARY.md` |
| 2026-11-26, 14:00 | v2.2 (hot-fix, no new version) | `running-when-a-request-is-made/references/execution.md` step 5: one rule to pick the cheapest sub-agent model that fits the job (GitHub Copilot: GPT-6 Luna for verifiers, lookups and low-complexity stages; GPT-6.1 Sol or GPT-6 Astra only for complex stages) | Claude Code (VS Code). Device and work-hours status: to be confirmed by the author | Author's request in the Claude Code session; git history |
| 2026-11-26, 21:16 | Correction | The row above has the wrong time: 14:00 was UTC. The hot-fix was made at 21:00 Asia/Bangkok | - | Modification time of `bench/skill-token/versions/v2.2/running-when-a-request-is-made/references/execution.md` (2026-11-26 21:00:54 +0700) |
| 2026-11-25, 23:02-23:03 (file times) | `explain-skills-in-details` 2.0.0 (its own `metadata.version`) | Separate skill: explains a topic in depth in three stages (ground, build, use), with a checkpoint file in `.explain/`. 8 files | Device and work-hours status: to be confirmed by the author | File modification times of its files; `metadata.version` in its `SKILL.md`. Earlier history of the skill: to be confirmed by the author |
| 2026-11-26, 20:22 | `explain-skills-in-details` 2.0.0 | Added to this repo, by mistake inside the frozen v1 snapshot as `bench/skill-token/versions/v1/explain-skills-in-details/explain-skills-in-details/` | This PC | Folder creation time |
| 2026-11-26, 21:16 | `explain-skills-in-details` 2.0.0 | Moved unchanged to `skills/explain-skills-in-details/`. The v1 snapshot is back to its recorded fingerprint. `validate_skill.py`: PASS | Claude Code (VS Code), this PC | Git history; fingerprints below |
| About 22:30, 2026-11-25 | `explain-skills-in-details` 1.x → 2.0.0 | Author's details for the rows above. The earlier version was one full Markdown file. It was then shrunk and split into this 2.0.0 layout (router `SKILL.md` + `references/` + `assets/`). The 23:02-23:03 file times match this | This laptop (the PC holding this repo), the author's Claude Pro account. Work-hours status: to be confirmed by the author | Author's statement, 2026-11-26 |
| 2026-11-26 | v2.2 (device) | Device for the 2026-11-25 v2.2 row: the PC that runs this Claude Code session and holds this repo. Work-hours status: to be confirmed by the author | - | Author's statement, 2026-11-26 |
| 2026-11-26 | Correction | In the `explain-skills-in-details` 1.x → 2.0.0 row, "(the PC holding this repo)" was an inference, not the author's words. The author said "this laptop", a different device from the Claude Code PC | - | Author's statement, 2026-11-26 |
| 2026-11-26 | Correction | The correction row above is wrong. "This laptop" and the PC that runs this Claude Code session are the same machine. So `explain-skills-in-details` 1.x → 2.0.0 and v2.2 were both made on this machine, which holds this repo | - | Author's statement, 2026-11-26 |

## Fingerprints

SHA-256 of each snapshot in `bench/skill-token/versions/<version>/` and each skill in `skills/<name>/`. The fingerprint is the hash of the sorted per-file `sha256sum` listing. Reproduce it from inside that folder, in Git Bash:

```bash
find . -type f -not -path '*__pycache__*' | LC_ALL=C sort | xargs sha256sum | sha256sum
```

| Version | Files | Fingerprint |
|---|---|---|
| v1 | 2 | `760d332919f5d16be4940ffd7a8a34bff87753887a48612cc7ca577d0a1cbcde` |
| v2.0 | 16 | `5aeaade920b77b11f16ede362a3e2603033892f791b30743cd9eede160a3b020` |
| v2.1 | 8 | `b50b60404ac58a4917e07c4f0f7cfe5380b08f8105862e42fda7179060fa2647` |
| `skills/explain-skills-in-details` (2.0.0) | 8 | `4c019dc7af0e032098f9938a8b58588195f968a2a17c975eb12fa4c2d8461d5e` |
| v2.2 (2026-11-25) | 8 | `fe194bf8fa1861e21c08d99302fa04a00410db1fdc63f32ce14c89206c9de871` |
| v2.2 (after 2026-11-26 hot-fix) | 8 | `a8e1b539ab13ee5d5facaf741bbe5492b5d0614158c9f2752b37a594e2b006b9` |

## Private evidence

The Claude conversation exports and any contract text are stored privately off-repo, in `%USERPROFILE%\Documents\skills-ip\` on the personal PC. They are not published.

## How to update this file

Add a row to the timeline and the fingerprint table whenever a skill is created or modified. The rule is in [AGENTS.md](AGENTS.md).
