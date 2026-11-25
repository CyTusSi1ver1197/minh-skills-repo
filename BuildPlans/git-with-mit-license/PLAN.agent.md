# EXECUTION PLAN: personal-skills-repo

## Context
The user owns two Agent Skills, `running-when-a-request-is-made` and `information-gathering-for-plan`. They work in Claude Code, Claude and GitHub Copilot. The user's employment contract says work done **outside work hours and not on company property** (company laptop, company Microsoft accounts and ecosystem, which includes company GitHub) is not company IP.

Timeline the user has stated (Source: User):
- **v1** was written on a Sunday evening, about 20:15-22:00 Asia/Bangkok, in a personal Claude account on a personal device.
- **v2.0** and **v2.1** were built on **Tuesday 2026-11-24, 10:34-18:25 Asia/Bangkok**, in a personal Claude account. The user was **off work** that day, and the benchmark ran on a **personal PC**.

**Goal:** a **public** repo on the user's **personal** GitHub account, created and pushed **only from the personal PC**. It is a dated, signed record of the skills and how they were built. It also:
- licenses the skills under **MIT**, so the employer uses them like any open-source tool;
- lets the work laptop install them read-only with `gh skill install`, with no personal credentials on company property.

This is a record-keeping and licensing plan, not legal advice. Before relying on it, the user checks the exact contract wording.

**Inputs on the personal PC** (all delivered earlier in this chat):
- `skill-token-optimization-v2.zip`: v2.0 skills, the `bench/` harness, and `BuildPlans/skill-token-optimization/`.
- `skill-v2.1.zip` (latest): v2.1 skills, `bench/` including `versions/v1` and `versions/v2.0` snapshots, and `BuildPlans/skill-token-optimization/`.
- `running-when-a-request-is-made-v2.1.zip`, `information-gathering-for-plan-v2.1.zip`: the release zips.
- `results/results.jsonl` and `RESULTS.md` from the user's benchmark runs.

## Preconditions
- **Personal PC only.** No step runs on the company laptop or under a company account.
- Personal GitHub account. It is **not** a company-managed (Enterprise Managed User) account, and it is not the account used at work.
- Git ≥ 2.34 (SSH commit signing) and GitHub CLI ≥ 2.90 (`gh skill`), which is preview.
- Python 3.10+ for the validator.
- Placeholders to replace before Step 4:
  - `<Your Full Name>`: legal name;
  - `<github-user>`: personal GitHub username;
  - `<personal-email>`: an email on the personal GitHub account. Use the GitHub no-reply address if the email should stay private.
- Repo name: `agent-skills`. A working folder, e.g. `C:\dev\agent-skills` (not inside OneDrive or any company-synced folder).

## Rules
- Nothing company-specific goes in the repo: no employer name, internal URLs, company rules, company code or company BuildPlans. (Source: user's contract boundary; the IP advice)
- Don't backdate commits (`GIT_AUTHOR_DATE` / `GIT_COMMITTER_DATE`). The record must show the real push date. Earlier creation dates are documented in `PROVENANCE.md` with their sources. (Source: integrity of evidence)
- v1 and v2.0 snapshots stay **byte-for-byte unchanged**. Copyright headers go only on the live v2.1 files. (Source: evidence integrity)
- Agent Skills spec: frontmatter `name` = folder name. The copyright comment goes **below** the frontmatter, so the files stay portable. (Source: Agent Skills spec; IP advice)
- Private material stays out of the repo: the chat export, the employer email draft, and any contract text. They go in `%USERPROFILE%\Documents\skills-ip\` on the personal PC. (Source: public repo)

## Steps
1. [DC-1] Check the accounts, in one PowerShell step: `gh auth status; gh api user --jq ".login,.type"; gh api user/orgs --jq ".[].login"; git --version; gh --version`.
   Verify: the login is the personal account (`<github-user>`), `type` is `User`, and the orgs list shows no employer org. Otherwise stop.
2. [DC-5] Set up SSH signing for this repo only:
   - `ssh-keygen -t ed25519 -C "<personal-email> signing" -f $HOME\.ssh\id_ed25519_signing` (skip if a personal key already exists);
   - `gh ssh-key add $HOME\.ssh\id_ed25519_signing.pub --type signing --title "personal signing"`.
   Verify: `gh api user/ssh_signing_keys --jq ".[].title"` lists "personal signing".
3. [DC-2] Build the folder layout in `C:\dev\agent-skills`:
   ```
   agent-skills/
   ├── skills/
   │   ├── running-when-a-request-is-made/   # v2.1, from skill-v2.1.zip
   │   └── information-gathering-for-plan/   # v2.1
   ├── history/
   │   ├── v1/<both skills>                  # = bench/skill-token/versions/v1, unchanged
   │   └── v2.0/<both skills>                # = bench/skill-token/versions/v2.0, unchanged
   ├── bench/skill-token/                    # harness, fixture, tasks, STATIC.md, RULE-COVERAGE.md, RESULTS.md, results/results.jsonl (no results/raw)
   ├── BuildPlans/
   │   ├── skill-token-optimization/         # PLAN.human.md, PLAN.agent.md, PROGRESS.md, EXECUTION-SUMMARY.md
   │   └── personal-skills-repo/             # this plan
   ├── evidence/                             # the 4 delivered zips + SHA256SUMS.txt
   ├── LICENSE  README.md  PROVENANCE.md  CHANGELOG.md  .gitignore
   ```
   In `bench/skill-token/run_bench.py` and `static_measure.py`, set the live-skills path to `skills/`, so `version_dir()` and `--as v2.1` point at `../../skills`.
   Verify: `Get-ChildItem -Recurse skills,history -Filter SKILL.md` lists 6 files.
4. [DC-3] Add the copyright headers (live v2.1 files only):
   - Insert as the first line after the closing `---` of each `skills/*/SKILL.md`: `<!-- © 2026 <Your Full Name>. Personal work, created outside employment. Licensed under the MIT License (see LICENSE in the repository root). -->`
   - At the top of each `skills/running-when-a-request-is-made/scripts/*.py`, add `# SPDX-License-Identifier: MIT` and `# Copyright (c) 2026 <Your Full Name>`. Put them under the shebang if a file has one.
   - Create `LICENSE`: the standard MIT text with `Copyright (c) 2026 <Your Full Name>`.
   Verify: `Select-String -Path skills\*\SKILL.md -Pattern "© 2026"` gives 2 hits; `Select-String -Path skills\*\scripts\*.py -Pattern "SPDX-License-Identifier: MIT"` gives 4 hits; `python bench\skill-token\validate_skill.py skills\running-when-a-request-is-made skills\information-gathering-for-plan` prints PASS twice.
5. [DC-4] Write `PROVENANCE.md`. Facts only, each with its source:
   - a timeline table: date/time (Asia/Bangkok), version, what changed, where (personal device, personal Claude account), and evidence;
   - for v1: the user's statement and the timestamps of the original Claude conversation;
   - for v2.0/v2.1: this conversation, Tue 2026-11-24 10:34-18:25, the user off work on a personal PC, and the benchmark run on the personal PC;
   - a SHA-256 table of the 4 zips in `evidence/`, from `Get-FileHash evidence\*.zip -Algorithm SHA256 | Format-Table -HideTableHeaders Hash, Path > evidence\SHA256SUMS.txt`;
   - one line saying the chat export is stored privately off-repo.

   Then, separately: export the Claude account data (Claude Settings → Privacy → Export data, if offered) and save it, with today's date, to `%USERPROFILE%\Documents\skills-ip\`.
   Verify: `PROVENANCE.md` has rows for v1, v2.0 and v2.1, and `SHA256SUMS.txt` has 4 lines whose hashes match `Get-FileHash`.
6. [DC-6] Write `README.md`:
   - what the skills do;
   - **Install**:
     - `gh skill install <github-user>/agent-skills running-when-a-request-is-made --agent claude-code --scope user --pin v2.1.0`, and the same for `information-gathering-for-plan`;
     - Copilot: the same command without `--agent`;
     - a manual-copy fallback.
   - **License**: MIT, © <Your Full Name>;
   - **Provenance**: a link to PROVENANCE.md;
   - **Benchmark**: a link to `bench/skill-token/RESULTS.md`.

   Also write `CHANGELOG.md` with v1.0.0, v2.0.0 (progressive disclosure, failed the token bar) and v2.1.0 (fewer turns, staged plans, 5 % stop), and a `.gitignore` covering `__pycache__/`, `bench/skill-token/results/raw/`, `probe-*.jsonl` and `.agent-context.json`.
   Verify: no placeholders left outside the plan files (`Select-String -Path README.md,LICENSE,PROVENANCE.md,skills\*\SKILL.md -Pattern "<Your Full Name>|<github-user>"` gives 0 hits).
7. [DC-1, DC-5] Create the repo and make signed, ordered commits:
   - `git init -b main`
   - `git config user.name "<Your Full Name>"; git config user.email "<personal-email>"`
   - `git config gpg.format ssh; git config user.signingkey $HOME\.ssh\id_ed25519_signing.pub; git config commit.gpgsign true; git config tag.gpgsign true`

   Then three commits, each followed by a signed tag:
   1. `history/v1` + `LICENSE` + `.gitignore`, message "v1: original skills (Sunday, personal)", tag `git tag -s v1.0.0 -m "v1"`;
   2. `history/v2.0` + `bench/` + `BuildPlans/skill-token-optimization/`, message "v2.0: progressive disclosure + benchmark", tag `v2.0.0`;
   3. everything else, message "v2.1: fewer turns, staged plans, provenance", tag `v2.1.0`.

   Finally `gh repo create <github-user>/agent-skills --public --source . --push` and `git push --tags`.
   Verify: `git log --show-signature --oneline` shows "Good signature" on all 3 commits; `gh api repos/<github-user>/agent-skills/commits/main --jq .commit.verification.verified` returns `true`; `git tag -v v2.1.0` verifies.
8. [DC-7] Test the install, on the personal PC, into a scratch folder:
   - `gh skill publish --dry-run` from the repo root (spec check; preview command);
   - `gh skill install <github-user>/agent-skills running-when-a-request-is-made --agent claude-code --scope project --pin v2.1.0` inside an empty test repo, then compare the installed SKILL.md with `skills/...` (`fc.exe`).

   Verify: the dry run reports no spec errors (record any security-setting warnings in PROVENANCE.md, they don't block), and `fc.exe` reports no differences.
9. [DC-8] Draft the employer notice and keep it private: write `%USERPROFILE%\Documents\skills-ip\employer-notice.md` from the template below. Sending it is the user's decision. Don't send it from this plan.
   ```
   Subject: Notice: use of my personal, pre-existing AI agent skills at work
   Hi <manager>,
   I've created a set of AI agent skills (instruction files for Claude Code / GitHub Copilot) as personal work, outside working hours and on my own devices and accounts. They're published under the MIT License at https://github.com/<github-user>/agent-skills.
   I'd like to use them read-only when working on company projects, installed from that public repo. I'll make any changes to the skills outside work on my own equipment; the code and documents produced for company projects remain company work.
   Could you reply to confirm this is fine, or let me know if HR or legal should review it?
   Thanks, <Your Full Name>
   ```
   Verify: the file exists outside the repo, and `git ls-files | Select-String employer` gives 0 hits.

## DC checklist
- [ ] DC-1 - verify by: Step 1 output; the repo is public under `<github-user>`.
- [ ] DC-2 - verify by: the Step 3 listing; `git diff --no-index history\v1 <v1 snapshot from zip>` is empty (same for v2.0).
- [ ] DC-3 - verify by: the Step 4 checks.
- [ ] DC-4 - verify by: the Step 5 checks; the chat export exists in `Documents\skills-ip\`.
- [ ] DC-5 - verify by: the Step 7 checks (3 verified commits, 3 verified tags).
- [ ] DC-6 - verify by: README has Install, License, Provenance and Benchmark sections; 0 placeholders left.
- [ ] DC-7 - verify by: the Step 8 checks.
- [ ] DC-8 - verify by: the Step 9 checks.

## Stop conditions
- Stop and ask if:
  - the GitHub account is company-managed, belongs to an employer org with SSO, or is the one used at work;
  - the working folder sits in OneDrive or any company-synced location;
  - any file contains employer names, internal URLs or company code;
  - an unchanged-snapshot check fails;
  - commit signing can't be verified on GitHub;
  - `gh` is older than 2.90, or `gh skill` is missing. In that case, install via manual copy and note it in README; don't upgrade tooling on a company machine.
- Never run any step on the company laptop. Never push with a company account.

## Contacts
- Owner: the user (sole author). No CODEOWNERS.
- Needs owner review: **yes**, because of legal sensitivity and > 10 files. Optional: an employment lawyer reviews PROVENANCE.md and the notice against the contract.

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | A public repo `<github-user>/agent-skills` exists on the user's personal (non-company-managed) GitHub account, created and pushed only from the personal PC | Original |
| DC-2 | `skills/` holds both v2.1 skills in an Agent Skills layout that `gh skill` can discover; `history/v1` and `history/v2.0` hold unchanged snapshots | Original |
| DC-3 | Each live `SKILL.md` has the copyright comment below its frontmatter, each script has SPDX + copyright lines, and `LICENSE` is MIT with the user's name and 2026 | Revised via Q-3 (from: "MIT or a short custom license") |
| DC-4 | `PROVENANCE.md` records the dated timeline (v1 Sunday evening; v2.0/v2.1 Tue 2026-11-24 10:34-18:25, off work, personal PC) with sources, plus SHA-256 hashes of the delivered zips; the chat export is saved privately off-repo | Revised via Q-1 (from: "skills written Sunday evening") |
| DC-5 | Commits v1 → v2.0 → v2.1 and their tags are signed and show as Verified on GitHub, with no backdated dates | Original |
| DC-6 | README documents install (`gh skill install … --pin v2.1.0`, manual fallback), the MIT license, provenance and benchmark results, with no company-specific content | Original |
| DC-7 | `gh skill publish --dry-run` reports no spec errors and a pinned `gh skill install` reproduces the v2.1 files exactly | Original |
| DC-8 | An employer notice draft exists outside the repo, ready for the user to send | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-4 | Must | Were the Tue 2026-11-24 10:34-18:25 sessions (v2.0/v2.1, benchmark) off work and on a personal PC? | Yes: off work and a personal PC; v1, v2.0 and v2.1 are all recorded as personal work | User |
| Q-2 | DC-2 | Must | Which skills go in the repo? | `running-when-a-request-is-made` and `information-gathering-for-plan` | User |
| Q-3 | DC-3, DC-6 | Should | Visibility and license? | Public + MIT (no personal credentials needed on the work laptop) | User |
| Q-4 | DC-3 | Must | Name in the copyright lines? | Placeholder `<Your Full Name>`, replaced at Step 4 | User |
| Q-5 | all | Could | Output format of this plan? | Standard BuildPlans set (v2.1 format) | Assumption |
| Q-6 | DC-1 | Could | Repo name? | `agent-skills` | Assumption |
| Q-7 | DC-5 | Could | Signing method? | SSH signing (works with existing Windows OpenSSH; simpler than GPG) | Assumption |
| Q-8 | DC-4, DC-5 | Should | Backdate commits to the creation days? | No: real commit dates; creation dates documented with sources in PROVENANCE.md | Assumption |
| Q-9 | DC-2 | Could | Include the benchmark harness and results? | Yes: evidence of how v2.x was built and tested (no company data in it) | Assumption |
| Q-10 | DC-8 | Could | Should the plan send the email? | No: draft only, kept off-repo; sending is the user's call | Assumption |
| Q-11 | DC-2 | Could | Repo layout for `gh skill`? | `skills/<name>/SKILL.md` at the repo root | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
| 2026-11-24 | Plan created | - |
