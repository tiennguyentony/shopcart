from dataclasses import dataclass
from datetime import datetime

from shopcart.domain.errors import InvalidCoupon


@dataclass(frozen=True)
class Coupon:
    id: int
    code: str
    percent_off: int
    max_uses: int | None
    times_used: int
    min_order_cents: int
    expires_at: datetime | None


def check_coupon(coupon: Coupon, subtotal_cents: int, now: datetime) -> None:
    """Raises InvalidCoupon if the coupon can't be used on this order."""
    if coupon.expires_at is not None and now >= coupon.expires_at:
        raise InvalidCoupon(f"Coupon {coupon.code} has expired")
    if coupon.max_uses is not None and coupon.times_used > coupon.max_uses:
        raise InvalidCoupon(f"Coupon {coupon.code} has been fully redeemed")
    if subtotal_cents < coupon.min_order_cents:
        minimum = coupon.min_order_cents / 100
        raise InvalidCoupon(f"Coupon {coupon.code} needs an order of at least ${minimum:.2f}")
