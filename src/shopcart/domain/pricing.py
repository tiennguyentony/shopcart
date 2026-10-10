"""Cart and order totals.

All amounts are integer cents (see docs/adr/001-money-as-integer-cents.md).
"""

from collections.abc import Iterable
from dataclasses import dataclass

from shopcart.domain.shipping import ShippingRule


@dataclass(frozen=True)
class Line:
    unit_price_cents: int
    quantity: int

    @property
    def total_cents(self) -> int:
        return self.unit_price_cents * self.quantity


@dataclass(frozen=True)
class Totals:
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    total_cents: int


def subtotal_cents(lines: Iterable[Line]) -> int:
    return sum(line.total_cents for line in lines)


def apply_percent_off(amount_cents: int, percent_off: int) -> tuple[int, int]:
    """Returns (discount, amount after discount), rounded to the nearest cent."""
    amount = amount_cents / 100
    discount = round(amount * percent_off / 100, 2)
    discounted = round(amount - discount, 2)
    return int(discount * 100), int(discounted * 100)


def calculate_totals(lines: Iterable[Line], shipping: ShippingRule, percent_off: int = 0) -> Totals:
    subtotal = subtotal_cents(lines)
    if percent_off:
        discount, discounted = apply_percent_off(subtotal, percent_off)
    else:
        discount, discounted = 0, subtotal
    shipping_cents = shipping.fee_for(discounted) if subtotal else 0
    return Totals(
        subtotal_cents=subtotal,
        discount_cents=discount,
        shipping_cents=shipping_cents,
        total_cents=discounted + shipping_cents,
    )
