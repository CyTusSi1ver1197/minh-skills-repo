# Provenance

The dated record of how the skills `running-when-a-request-is-made` and `information-gathering-for-plan` were created and changed. Every row lists its source. Commit dates in git are real, not backdated; earlier creation dates are recorded here.

All times are Asia/Bangkok (UTC+7).

## Timeline

| Date / time | Version | What changed | Where | Source / evidence |
|---|---|---|---|---|
| A Sunday evening, about 20:15-22:00 (date to be filled in from the original conversation) | v1 | Both skills first written | Personal device, personal Claude account | Author's statement; timestamps of the original Claude conversation (stored privately, off-repo) |
| 2026-11-24, 10:34-18:25 | v2.0 | Progressive disclosure (references/, assets/, scripts/); benchmark harness built. Failed the token bar (more turns) | Personal Claude account; benchmark run on a personal PC; author off work that day | Author's statement; `BuildPlans/skill-token-optimization/PROGRESS.md` session log; `bench/skill-token/results/results.jsonl` |
| 2026-11-24, 10:34-18:25 | v2.1 | Fewer turns, staged plans, 5 % low-context stop | Same as v2.0 | Same as v2.0; `bench/skill-token/RESULTS.md` |
| 2026-11-25 | v2.2 | GPT-6 / Copilot fit: "Use when" descriptions, class C handled without a format question, working rules, `## Blockers` in the summary, missing-skill references removed. Copilot benchmark (DC-7) still pending | Claude Code (VS Code). Device and work-hours status: to be confirmed by the author | `BuildPlans/gpt6-model-fit/PROGRESS.md` and `EXECUTION-SUMMARY.md` |

## Fingerprints

SHA-256 of each snapshot in `bench/skill-token/versions/<version>/`. The fingerprint is the hash of the sorted per-file `sha256sum` listing. Reproduce it from inside the version folder, in Git Bash:

```bash
find . -type f -not -path '*__pycache__*' | LC_ALL=C sort | xargs sha256sum | sha256sum
```

| Version | Files | Fingerprint |
|---|---|---|
| v1 | 2 | `760d332919f5d16be4940ffd7a8a34bff87753887a48612cc7ca577d0a1cbcde` |
| v2.0 | 16 | `5aeaade920b77b11f16ede362a3e2603033892f791b30743cd9eede160a3b020` |
| v2.1 | 8 | `b50b60404ac58a4917e07c4f0f7cfe5380b08f8105862e42fda7179060fa2647` |
| v2.2 | 8 | `fe194bf8fa1861e21c08d99302fa04a00410db1fdc63f32ce14c89206c9de871` |

## Private evidence

The Claude conversation exports and any contract text are stored privately off-repo, in `%USERPROFILE%\Documents\skills-ip\` on the personal PC. They are not published.

## How to update this file

Add a row to the timeline and the fingerprint table whenever a skill is created or modified. The rule is in [AGENTS.md](AGENTS.md).
