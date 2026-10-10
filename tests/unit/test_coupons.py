from datetime import datetime, timedelta, timezone

import pytest

from shopcart.domain.coupons import Coupon, check_coupon
from shopcart.domain.errors import InvalidCoupon

NOW = datetime(2031, 3, 3, 9, 0, tzinfo=timezone.utc)


def make_coupon(**overrides) -> Coupon:
    fields = dict(
        id=1, code="TEST10", percent_off=10, max_uses=None, times_used=0, min_order_cents=0, expires_at=None
    )
    return Coupon(**{**fields, **overrides})


def test_valid_coupon_passes():
    check_coupon(make_coupon(), subtotal_cents=1000, now=NOW)


def test_expired_coupon_is_rejected():
    with pytest.raises(InvalidCoupon):
        check_coupon(make_coupon(expires_at=NOW - timedelta(days=1)), subtotal_cents=1000, now=NOW)


def test_minimum_order_is_enforced():
    with pytest.raises(InvalidCoupon):
        check_coupon(make_coupon(min_order_cents=5000), subtotal_cents=4999, now=NOW)
