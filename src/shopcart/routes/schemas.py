from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    token: str


class ProductOut(Out):
    id: int
    name: str
    description: str
    category: str
    price_cents: int
    stock: int


class AdminProductOut(ProductOut):
    published: bool


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""
    category: str = Field(min_length=1, max_length=50)
    price_cents: int = Field(ge=0)
    stock: int = Field(ge=0)
    published: bool = False


class ProductPatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = Field(None, min_length=1, max_length=50)
    price_cents: int | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)
    published: bool | None = None


class AddToCartIn(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1, le=99)


class QuantityIn(BaseModel):
    quantity: int = Field(ge=1, le=99)


class CartLineOut(Out):
    id: int
    product_id: int
    name: str
    unit_price_cents: int
    quantity: int
    total_cents: int


class CartOut(BaseModel):
    items: list[CartLineOut]
    subtotal_cents: int
    shipping_cents: int
    total_cents: int


class CheckoutIn(BaseModel):
    coupon_code: str | None = None


class OrderLineOut(Out):
    product_id: int
    name: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int
    can_reorder: bool


class OrderOut(Out):
    id: int
    status: str
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    total_cents: int
    coupon_code: str | None
    created_at: str
    items: list[OrderLineOut]


class AdminOrderOut(OrderOut):
    user_id: int


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    size: int
    total: int
    pages: int
