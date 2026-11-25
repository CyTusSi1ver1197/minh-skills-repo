"""In-memory order store."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class OrderStatus(str, Enum):
    NEW = "new"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class Order:
    id: int
    items: list[tuple[str, int, float]] = field(default_factory=list)  # (sku, quantity, unit price)
    status: OrderStatus = OrderStatus.NEW


_ORDERS: dict[int, Order] = {}
_NEXT_ID = 1


def create_order(items: list[tuple[str, int, float]]) -> Order:
    """Create an order from (sku, quantity, unit price) tuples."""
    global _NEXT_ID
    if not items:
        raise ValueError("an order needs at least one item")
    order = Order(id=_NEXT_ID, items=list(items))
    _ORDERS[order.id] = order
    _NEXT_ID += 1
    return order


def get_order(order_id: int) -> Order:
    """Return the order or raise KeyError."""
    return _ORDERS[order_id]


def list_orders() -> list[Order]:
    """Return all orders, oldest first."""
    return [ _ORDERS[k] for k in sorted(_ORDERS) ]


def reset() -> None:
    """Clear the store (tests only)."""
    global _NEXT_ID
    _ORDERS.clear()
    _NEXT_ID = 1
