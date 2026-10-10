from fastapi import APIRouter

from shopcart.routes.deps import CurrentUser, ServicesDep
from shopcart.routes.schemas import AddToCartIn, CartLineOut, CartOut, QuantityIn
from shopcart.services.cart import CartView

router = APIRouter(prefix="/cart", tags=["cart"])


def to_cart_out(cart: CartView) -> CartOut:
    return CartOut(
        items=[CartLineOut.model_validate(line) for line in cart.lines],
        subtotal_cents=cart.totals.subtotal_cents,
        shipping_cents=cart.totals.shipping_cents,
        total_cents=cart.totals.total_cents,
    )


@router.get("", response_model=CartOut)
def view_cart(user: CurrentUser, services: ServicesDep):
    return to_cart_out(services.cart.view(user.id))


@router.post("/items", response_model=CartOut, status_code=201)
def add_item(body: AddToCartIn, user: CurrentUser, services: ServicesDep):
    return to_cart_out(services.cart.add_item(user.id, body.product_id, body.quantity))


@router.patch("/items/{item_id}", response_model=CartOut)
def change_quantity(item_id: int, body: QuantityIn, user: CurrentUser, services: ServicesDep):
    return to_cart_out(services.cart.change_quantity(user.id, item_id, body.quantity))


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_item(item_id: int, user: CurrentUser, services: ServicesDep):
    return to_cart_out(services.cart.remove_item(user.id, item_id))
