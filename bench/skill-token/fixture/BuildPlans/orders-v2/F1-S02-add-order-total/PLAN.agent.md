# EXECUTION PLAN: orders-v2 / F1-S02 Add order_total
## Context
`src/orders.py` is an in-memory order store: `Order(id, items, status)` where `items` is a list of `(sku, quantity, unit_price)` tuples and `status` is an `OrderStatus` enum (`new`, `paid`, `cancelled`). `get_order(order_id)` raises `KeyError` for unknown IDs; `reset()` clears the store in tests. Project rules (CLAUDE.md): PEP 8, type hints on public functions, stdlib `unittest` in `tests/`, no new dependencies, `python -m unittest discover -s tests -t .` must pass.
This is stage F1-S02 of the staged plan `BuildPlans/orders-v2` (see its FLOW.md for flow order).

## Inputs from earlier stages
- F1-S01 → `OrderStatus` in `src/orders.py` (not used here)

## Preconditions
- Python 3.10+; run commands from the repo root.

## Rules
- PEP 8, type hints on public functions (source: CLAUDE.md)
- stdlib `unittest` tests in `tests/` (source: CLAUDE.md)
- No new dependencies (source: CLAUDE.md)

## Steps
1. [F1-S02/DC-1] Modify `src/orders.py`: add `def order_total(order_id: int) -> float` = sum of `quantity * unit_price` over the order's items, rounded to 2 decimals; unknown IDs raise `KeyError` (reuse `get_order`).
   Verify: `python -c "from src.orders import create_order, order_total; o=create_order([('A',2,1.25),('B',1,3.0)]); assert order_total(o.id)==5.5"`
2. [F1-S02/DC-2] Modify `tests/test_orders.py`: add `test_order_total` (two items → 5.5) and `test_order_total_unknown` (KeyError).
   Verify: `python -m unittest discover -s tests -t .`

## DC checklist
- [ ] F1-S02/DC-1 - verify by: step 1
- [ ] F1-S02/DC-2 - verify by: step 2

## Stop conditions
- Stop and ask if: a function this stage expects is missing, or an existing test fails before your change.

## Contacts
- `src/orders.py`, `tests/test_orders.py`, `docs/` → @fixture-owner (CODEOWNERS) · Needs owner review: no

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| F1-S02/DC-1 | `order_total` returns the rounded sum and raises KeyError for unknown IDs (master DC-2) | Original |
| F1-S02/DC-2 | Tests cover both cases and the suite passes (master DC-2) | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | F1-S02/DC-1 | Could | Extra behaviour beyond the steps? | No | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
