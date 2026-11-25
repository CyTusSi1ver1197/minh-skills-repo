# EXECUTION PLAN: orders-v2 / F2-S01 Document the orders API
## Context
`src/orders.py` is an in-memory order store: `Order(id, items, status)` where `items` is a list of `(sku, quantity, unit_price)` tuples and `status` is an `OrderStatus` enum (`new`, `paid`, `cancelled`). `get_order(order_id)` raises `KeyError` for unknown IDs; `reset()` clears the store in tests. Project rules (CLAUDE.md): PEP 8, type hints on public functions, stdlib `unittest` in `tests/`, no new dependencies, `python -m unittest discover -s tests -t .` must pass.
This is stage F2-S01 of the staged plan `BuildPlans/orders-v2` (see its FLOW.md for flow order).

## Inputs from earlier stages
- F1-S01 → `OrderStatus`; F1-S02 → `order_total` (document it if present, else mark 'planned')

## Preconditions
- Python 3.10+; run commands from the repo root.

## Rules
- PEP 8, type hints on public functions (source: CLAUDE.md)
- stdlib `unittest` tests in `tests/` (source: CLAUDE.md)
- No new dependencies (source: CLAUDE.md)

## Steps
1. [F2-S01/DC-1] Create `docs/orders.md`: one section per public function in `src/orders.py` (signature, behaviour, errors) and the `OrderStatus` values.
   Verify: `python -c "t=open('docs/orders.md').read(); assert 'create_order' in t and 'OrderStatus' in t"`

## DC checklist
- [ ] F2-S01/DC-1 - verify by: step 1

## Stop conditions
- Stop and ask if: a function this stage expects is missing, or an existing test fails before your change.

## Contacts
- `src/orders.py`, `tests/test_orders.py`, `docs/` → @fixture-owner (CODEOWNERS) · Needs owner review: no

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| F2-S01/DC-1 | `docs/orders.md` documents every public function and `OrderStatus` (master DC-4) | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | F2-S01/DC-1 | Could | Extra behaviour beyond the steps? | No | Assumption |

## Revision log
| Date | Change | Approved by |
|---|---|---|
