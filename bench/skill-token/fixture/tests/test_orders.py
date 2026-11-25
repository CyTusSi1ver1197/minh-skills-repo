import unittest

from src import orders


class OrderTests(unittest.TestCase):
    def setUp(self) -> None:
        orders.reset()

    def test_create_assigns_ids(self) -> None:
        a = orders.create_order([("A", 1, 2.0)])
        b = orders.create_order([("B", 2, 3.0)])
        self.assertEqual((a.id, b.id), (1, 2))
        self.assertEqual(a.status, orders.OrderStatus.NEW)

    def test_create_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            orders.create_order([])

    def test_get_and_list(self) -> None:
        a = orders.create_order([("A", 1, 2.0)])
        self.assertIs(orders.get_order(a.id), a)
        self.assertEqual(orders.list_orders(), [a])
        with self.assertRaises(KeyError):
            orders.get_order(99)


if __name__ == "__main__":
    unittest.main()
