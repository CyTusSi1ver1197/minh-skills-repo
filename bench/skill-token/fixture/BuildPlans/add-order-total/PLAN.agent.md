# EXECUTION PLAN: add-order-total
## Context
`src/orders.py` is an in-memory order store. `Order.items` is a list of `(sku, quantity, unit_price)` tuples. Orders are looked up with `get_order(order_id)`, which raises `KeyError` for unknown IDs. Project rules are in `CLAUDE.md` (PEP 8, type hints, stdlib `unittest`, no new dependencies, tests must pass).

## Preconditions
- Python 3.10+; run commands from the repo root.

## Rules
- PEP 8 and type hints on public functions (source: CLAUDE.md)
- Tests with stdlib `unittest` in `tests/` (source: CLAUDE.md)
- No new dependencies (source: CLAUDE.md)

## Steps
1. [DC-1] Modify `src/orders.py`: add `def order_total(order_id: int) -> float` returning the sum of `quantity * unit_price` over the order's items, rounded to 2 decimals. Unknown IDs raise `KeyError` (reuse `get_order`).
   Verify: `python -c "from src.orders import create_order, order_total; o=create_order([('A',2,1.25),('B',1,3.0)]); assert order_total(o.id)==5.5"`
2. [DC-2] Modify `tests/test_orders.py`: add `test_order_total` (two items → 5.5) and `test_order_total_unknown` (`KeyError`).
   Verify: `python -m unittest discover -s tests -t .`

## DC checklist
- [ ] DC-1 - verify by: Step 1 command
- [ ] DC-2 - verify by: Step 2 command passes with 5 tests

## Stop conditions
- Stop and ask if: `get_order` no longer exists, or an existing test fails before your change.

## Contacts
- `src/orders.py`, `tests/test_orders.py` → @fixture-owner (CODEOWNERS) · Needs owner review: no

## Done Criteria
| ID | Done criterion | Status |
|---|---|---|
| DC-1 | `order_total(order_id)` returns the rounded sum of quantity × unit price and raises KeyError for unknown IDs | Original |
| DC-2 | Unit tests cover the normal and unknown-ID cases and the suite passes | Original |

## Question Map
| Q | DC | MoSCoW | Question | Answer | Source |
|---|---|---|---|---|---|
| Q-1 | DC-1 | Could | Rounding? | 2 decimals | Assumption |
| Q-2 | DC-1 | Should | Error for unknown IDs? | KeyError, same as get_order | User |

## Revision log
| Date | Change | Approved by |
|---|---|---|
