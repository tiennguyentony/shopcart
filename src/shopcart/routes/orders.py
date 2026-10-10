from fastapi import APIRouter

from shopcart.routes.deps import CurrentUser, PageDep, ServicesDep
from shopcart.routes.schemas import CheckoutIn, OrderOut, Page

router = APIRouter(tags=["orders"])


@router.post("/checkout", response_model=OrderOut, status_code=201)
def checkout(user: CurrentUser, services: ServicesDep, body: CheckoutIn | None = None):
    coupon_code = body.coupon_code if body else None
    order_id = services.checkout.checkout(user.id, coupon_code)
    return services.orders.get_order(order_id)


@router.get("/orders", response_model=Page[OrderOut])
def my_orders(user: CurrentUser, services: ServicesDep, page: PageDep):
    orders, total = services.orders.list_for_user(user.id, page)
    return Page[OrderOut](
        items=[OrderOut.model_validate(o) for o in orders],
        page=page.page,
        size=page.size,
        total=total,
        pages=page.pages_for(total),
    )


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, user: CurrentUser, services: ServicesDep):
    return services.orders.get_order(order_id)
