# Personal skills repo: dated, signed, MIT-licensed
**Goal:** Publish `running-when-a-request-is-made` and `information-gathering-for-plan` in a public repo on your personal GitHub, pushed only from your personal PC. It's a dated, signed record that the skills are your work, licensed MIT so your employer can use them read-only.
**Status:** Draft - awaiting review

## Scope
- New repo `<github-user>/agent-skills` (public), built in `C:\dev\agent-skills` on the personal PC.
- `skills/` (v2.1, live) · `history/v1`, `history/v2.0` (unchanged snapshots) · `bench/skill-token/` · `BuildPlans/` · `evidence/` (4 zips + SHA256SUMS).
- New files: `LICENSE` (MIT), `README.md`, `PROVENANCE.md`, `CHANGELOG.md`, `.gitignore`. Copyright comment in both live `SKILL.md`; SPDX lines in the 4 scripts.
- Off-repo, private: the Claude data export and the employer-notice draft, in `Documents\skills-ip\`.

## Impact
- Functional: the work laptop installs read-only with `gh skill install <github-user>/agent-skills <skill> --pin v2.1.0`. No personal credentials go on company property.
- Non-functional:
  - Public: anyone can read and use the skills under MIT.
  - Signed commits and tags plus file hashes give a tamper-evident date.
  - `gh skill` is preview, so there's a manual-copy fallback.

## Rules
- Nothing company-specific in the repo (contract boundary).
- No backdated commits. Earlier dates go in PROVENANCE.md with their sources.
- v1 and v2.0 snapshots stay byte-identical. Headers go only on the live v2.1 files.
- Every step runs on the personal PC with the personal account.

## Contacts
- You (sole author). Optional: an employment lawyer checks PROVENANCE.md and the notice against your contract.
- Needs owner review: yes (legal sensitivity, > 10 files).

## Risks, trade-offs & assumptions
- **Not legal advice.** Whether this protects you depends on your contract's exact wording. The employer's written reply (Step 9) is the strongest evidence.
- **Public vs private:** public means anyone can see and use the skills, including competitors. In exchange, there are no credentials on the work laptop and the dated record is stronger.
- **Today's timestamps:** v2.0/v2.1 were built Tue 24 Nov, 10:34-18:25. You confirmed you were off work and on a personal PC. PROVENANCE.md states this, so be ready to back it up (leave record, device).
- **v1's date** rests on your statement plus the original chat's timestamps. Export that chat before anything else.
- **Assumptions:** repo name `agent-skills`; SSH signing; the benchmark is included; email drafted but not sent.

Done criteria and question map: [PLAN.agent.md](PLAN.agent.md#done-criteria)
