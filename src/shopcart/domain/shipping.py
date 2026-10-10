from dataclasses import dataclass


@dataclass(frozen=True)
class ShippingRule:
    """Flat-rate shipping, free for larger orders.

    Orders of $50.00 or more (after discounts) ship free; anything smaller
    pays the flat fee. Values come from Settings.
    """

    flat_fee_cents: int
    free_threshold_cents: int

    def fee_for(self, amount_cents: int) -> int:
        if amount_cents >= self.free_threshold_cents:
            return 0
        return self.flat_fee_cents
