# FLOW: <plan-name>
**Goal:** <two lines>

## Flows
| Flow | Kind | Stages in order | Starts after | Runs in parallel with |
|---|---|---|---|---|
| F1 | main | F1-S01, F1-S02, F1-S03 | - | F2 |
| F2 | parallel | F2-S01 | F1-S01 | F1 |
| F3 | optional | F3-S01 | F1-S03 | - |

## Status
<!-- flow-status:start -->
<!-- flow-status:end -->

## Shared context
- <contract between stages: interface / path / schema> (produced by <stage>, used by <stage>)

## Done Criteria
| ID | Done criterion | Stage(s) | Status |
|---|---|---|---|

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|

## Revision log
| Date | Change | Approved by |
|---|---|---|
