# EXECUTION PLAN: orders-v2 / F1-S03 Add cancel_order
## Context
`src/orders.py` is an in-memory order store: `Order(id, items, status)` where `items` is a list of `(sku, quantity, unit_price)` tuples and `status` is an `OrderStatus` enum (`new`, `paid`, `cancelled`). `get_order(order_id)` raises `KeyError` for unknown IDs; `reset()` clears the store in tests. Project rules (CLAUDE.md): PEP 8, type hints on public functions, stdlib `unittest` in `tests/`, no new dependencies, `python -m unittest discover -s tests -t .` must pass.
This is stage F1-S03 of the staged plan `BuildPlans/orders-v2` (see its FLOW.md for flow order).

## Inputs from earlier stages
- F1-S01 → `OrderStatus.CANCELLED` in `src/orders.py`

## Preconditions
- Python 3.10+; run commands from the repo root.

## Rules
- PEP 8, type hints on public functions (source: CLAUDE.md)
- stdlib `unittest` tests in `tests/` (source: CLAUDE.md)
- No new dependencies (source: CLAUDE.md)

## Steps
1. [F1-S03/DC-1] Modify `src/orders.py`: add `def cancel_order(order_id: int) -> Order` that sets `status` to `OrderStatus.CANCELLED` and returns the order; unknown IDs raise `KeyError`; an already cancelled order raises `ValueError`.
   Verify: `python -c "from src.orders import create_order, cancel_order, OrderStatus; o=create_order([('A',1,1.0)]); assert cancel_order(o.id).status is OrderStatus.CANCELLED"`
2. [F1-S03/DC-2] Modify `tests/test_orders.py`: add tests for cancel, unknown ID (KeyError) and double cancel (ValueError).
   Verify: `python -m unittest discover -s tests -t .`

## DC checklist
- [ ] F1-S03/DC-1 - verify by: step 1
- [ ] F1-S03/DC-2 - verify by: step 2

## Stop conditions
- Stop and ask if: a function this stage expects is missing, or an existing test fails before your change.

## Contacts
- `src/orders.py`, `tests/test_orders.py`, `docs/` → @fixture-owner (CODEOWNERS) · Needs owner review: no

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| F1-S03/DC-1 | `cancel_order` sets CANCELLED, KeyError for unknown, ValueError for double cancel (master DC-3) | Original |
| F1-S03/DC-2 | Tests cover the three cases and the suite passes (master DC-3) | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | F1-S03/DC-1 | Could | Extra behaviour beyond the steps? | No | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
