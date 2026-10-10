from dataclasses import dataclass

from shopcart.domain.errors import NotFound
from shopcart.domain.pagination import PageRequest
from shopcart.repositories.orders import Order, OrderRepo
from shopcart.repositories.products import ProductRepo


@dataclass(frozen=True)
class OrderLineView:
    product_id: int
    name: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int
    can_reorder: bool


@dataclass(frozen=True)
class OrderView:
    id: int
    user_id: int
    status: str
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    total_cents: int
    coupon_code: str | None
    created_at: str
    items: list[OrderLineView]


class OrderService:
    def __init__(self, orders: OrderRepo, products: ProductRepo):
        self.orders = orders
        self.products = products

    def list_for_user(self, user_id: int, page: PageRequest) -> tuple[list[OrderView], int]:
        orders, total = self.orders.list_for_user(user_id, page)
        return [self._view(order) for order in orders], total

    def list_all(self, page: PageRequest) -> tuple[list[OrderView], int]:
        orders, total = self.orders.list_all(page)
        return [self._view(order) for order in orders], total

    def get_order(self, order_id: int) -> OrderView:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFound("Order")
        return self._view(order)

    def _view(self, order: Order) -> OrderView:
        lines = []
        for item in self.orders.items(order.id):
            product = self.products.get(item.product_id)
            lines.append(
                OrderLineView(
                    product_id=item.product_id,
                    name=item.product_name,
                    unit_price_cents=item.unit_price_cents,
                    quantity=item.quantity,
                    line_total_cents=item.unit_price_cents * item.quantity,
                    can_reorder=bool(product and product.published and product.stock > 0),
                )
            )
        return OrderView(**vars(order), items=lines)
