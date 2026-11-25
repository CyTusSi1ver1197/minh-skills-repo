"""Tiny CLI: python -m src.app create SKU:QTY:PRICE ... | list"""
from __future__ import annotations

import sys

from src.orders import create_order, list_orders


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "create":
        items = [(s, int(q), float(p)) for s, q, p in (a.split(":") for a in argv[1:])]
        print(create_order(items))
    elif argv[0] == "list":
        for order in list_orders():
            print(order)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
