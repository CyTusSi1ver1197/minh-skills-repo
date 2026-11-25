# Benchmark results: running-when-a-request-is-made

Runs: 3 recorded, 3 used, 0 left out (timeout / missing values).
Pass bar: on every task, candidate median **turns** and **cost** ≤ baseline, and quality not lower.
Cost = Claude Code's API-price estimate (`total_cost_usd`), not a subscription charge. Total tokens count cache reads at full weight: information only.

- claude: model `sonnet`, CLI `2.1.300 (Claude Code)`

## claude: v1 vs v2.1

| Task | Turns (base → cand) | Cost $ (base → cand) | Cost change | Total tokens (base → cand) | Output tokens (base → cand) | Quality (base → cand) | Task OK | Next |
|---|---|---|---|---|---|---|---|---|

Total median cost: 0.000 → 0.000 (-)

Feature checks:

| Task | Runs | All checks passed | Median turns | Median cost $ | Common failed checks |
|---|---|---|---|---|---|
| T6-plan-large | 1 | 0 ✗ | 10.0 | 0.956 | F1-S04: <= 4 DCs (1); F1-S06: <= 4 DCs (1); F1-S08: <= 4 DCs (1) |
| T7-resume | 1 | 1 ✗ | 9.0 | 0.206 | - |
| T8-low-context | 1 | 1 ✗ | 8.0 | 0.186 | - |

**claude v2.1: FAIL**

## Verdict

- claude v2.1: FAIL

## Static load per request class

| Version | Class | Files | Extra reads | Chars | Est. tokens | Exact tokens |
|---|---|---|---|---|---|---|
| v1 | A | 1 | 0 | 12,314 | 3,078 | - |
| v1 | A+IG | 2 | 0 | 20,748 | 5,187 | - |
| v1 | B | 1 | 0 | 12,314 | 3,078 | - |
| v1 | B-staged | 1 | 0 | 12,314 | 3,078 | - |
| v1 | C | 1 | 0 | 12,314 | 3,078 | - |

| Version | Class | Files | Extra reads | Chars | Est. tokens | Exact tokens |
|---|---|---|---|---|---|---|
| v2.0 | A | 4 | 3 | 9,303 | 2,326 | - |
| v2.0 | A+IG | 7 | 5 | 16,914 | 4,228 | - |
| v2.0 | B | 4 | 3 | 6,364 | 1,591 | - |
| v2.0 | B-staged | 5 | 4 | 10,546 | 2,636 | - |
| v2.0 | C | 1 | 0 | 3,075 | 769 | - |

| Version | Class | Files | Extra reads | Chars | Est. tokens | Exact tokens |
|---|---|---|---|---|---|---|
| v2.1 | A | 1 | 0 | 8,830 | 2,208 | - |
| v2.1 | A+IG | 2 | 0 | 16,423 | 4,106 | - |
| v2.1 | B | 2 | 1 | 12,110 | 3,028 | - |
| v2.1 | B-staged | 3 | 2 | 17,174 | 4,294 | - |
| v2.1 | C | 1 | 0 | 8,830 | 2,208 | - |


## Comparison (chars; extra reads = files read besides SKILL.md bodies)
| Class | v1 chars | v2.0 chars (extra reads) | v2.1 chars (extra reads) | v2.1 / v1 |
|---|---|---|---|---|
| A | 12,314 | 9,303 (3) | 8,830 (0) | 72 % |
| A+IG | 20,748 | 16,914 (5) | 16,423 (0) | 79 % |
| B | 12,314 | 6,364 (3) | 12,110 (1) | 98 % |
| B-staged | 12,314 | 10,546 (4) | 17,174 (2) | 139 % |
| C | 12,314 | 3,075 (0) | 8,830 (0) | 72 % |
