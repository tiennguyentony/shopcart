from shopcart.domain.pricing import Line, calculate_totals, subtotal_cents
from shopcart.domain.shipping import ShippingRule

SHIPPING = ShippingRule(flat_fee_cents=599, free_threshold_cents=7500)


def test_subtotal_adds_up_lines():
    lines = [Line(1999, 2), Line(500, 1)]
    assert subtotal_cents(lines) == 4498


def test_small_order_pays_shipping():
    totals = calculate_totals([Line(1000, 2)], SHIPPING)
    assert totals.subtotal_cents == 2000
    assert totals.discount_cents == 0
    assert totals.shipping_cents == 599
    assert totals.total_cents == 2599


def test_empty_cart_costs_nothing():
    totals = calculate_totals([], SHIPPING)
    assert totals.total_cents == 0
    assert totals.shipping_cents == 0


def test_percent_off_is_applied_before_shipping():
    totals = calculate_totals([Line(2500, 1)], SHIPPING, percent_off=20)
    assert totals.discount_cents == 500
    assert totals.total_cents == 2000 + 599


def test_discount_can_drop_order_below_free_shipping():
    totals = calculate_totals([Line(4000, 2)], SHIPPING, percent_off=10)
    assert totals.discount_cents == 800
    assert totals.shipping_cents == 599
    assert totals.total_cents == 7200 + 599


def test_large_order_with_coupon():
    totals = calculate_totals([Line(5000, 2)], SHIPPING, percent_off=10)
    assert totals.discount_cents == 1000
    assert totals.shipping_cents == 0
    assert totals.total_cents == 9000
