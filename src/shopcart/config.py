import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str = "shopcart.db"
    free_shipping_threshold_cents: int = 7500
    shipping_fee_cents: int = 599
    session_ttl_hours: int = 24 * 7
    seed_demo_data: bool = True


def load_settings() -> Settings:
    return Settings(
        db_path=os.environ.get("SHOPCART_DB", "shopcart.db"),
        seed_demo_data=os.environ.get("SHOPCART_SEED", "1") != "0",
    )
