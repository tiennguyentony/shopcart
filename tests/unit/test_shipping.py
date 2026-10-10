from shopcart.config import Settings
from shopcart.domain.shipping import ShippingRule


def rule_from_settings() -> ShippingRule:
    settings = Settings()
    return ShippingRule(settings.shipping_fee_cents, settings.free_shipping_threshold_cents)


def test_free_shipping_threshold_is_75_dollars():
    assert Settings().free_shipping_threshold_cents == 7500


def test_flat_fee_below_threshold():
    assert rule_from_settings().fee_for(7499) == 599


def test_free_at_threshold():
    assert rule_from_settings().fee_for(7500) == 0


def test_free_above_threshold():
    assert rule_from_settings().fee_for(12000) == 0
