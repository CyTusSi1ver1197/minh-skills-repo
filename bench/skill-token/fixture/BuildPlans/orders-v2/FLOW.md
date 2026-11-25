# FLOW: orders-v2
**Goal:** Add order status handling, totals and cancellation to the order store, with docs in parallel.

## Flows
| Flow | Kind | Stages in order | Starts after | Runs in parallel with |
|---|---|---|---|---|
| F1 | main | F1-S01, F1-S02, F1-S03 | - | F2 |
| F2 | parallel | F2-S01 | F1-S01 | F1 |

## Status
<!-- flow-status:start -->
| Flow | Kind | Done | Current stage | Next stage |
|---|---|---|---|---|
| F1 | main | 1/3 | - | F1-S02 |
| F2 | parallel | 0/1 | - | F2-S01 |

| Stage | Status | DCs MET | Updated | Next step | Resume note |
|---|---|---|---|---|---|
| F1-S01 | MET | 1/1 | 2026-11-20T10:00:00Z | - |  |
| F1-S02 | TODO | 0/2 | - | 1 |  |
| F1-S03 | TODO | 0/2 | - | 1 |  |
| F2-S01 | TODO | 0/1 | - | 1 |  |

Ready now: F1-S02 (F1, main), F2-S01 (F2, parallel)

Session log (last 10):
| Date | Tool | DCs done | Stopped because |
|---|---|---|---|
| 2026-11-20 | claude-code | F1-S01/DC-1 | stage done |
<!-- flow-status:end -->

## Shared context
- `OrderStatus` enum in `src/orders.py` (values new / paid / cancelled), produced by F1-S01, used by F1-S03 and F2-S01.
- `order_total(order_id) -> float` in `src/orders.py`, produced by F1-S02, documented by F2-S01.

## Done Criteria
| ID | Done criterion | Stage(s) | Status |
|---|---|---|---|
| DC-1 | Orders carry an `OrderStatus` | F1-S01 | MET |
| DC-2 | `order_total` works and is tested | F1-S02 | Open |
| DC-3 | `cancel_order` works and is tested | F1-S03 | Open |
| DC-4 | `docs/orders.md` documents the public API | F2-S01 | Open |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-2 | Could | Rounding of totals? | 2 decimals | Assumption |
| Q-2 | DC-3 | Should | Cancel an already cancelled order? | Raise ValueError | User |

## Revision log
| Date | Change | Approved by |
|---|---|---|
