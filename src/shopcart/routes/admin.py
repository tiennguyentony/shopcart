from fastapi import APIRouter

from shopcart.routes.deps import AdminUser, PageDep, ServicesDep
from shopcart.routes.schemas import AdminOrderOut, AdminProductOut, Page, ProductIn, ProductPatch

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/products", response_model=AdminProductOut, status_code=201)
def create_product(body: ProductIn, admin: AdminUser, services: ServicesDep):
    return services.catalog.create(**body.model_dump())


@router.patch("/products/{product_id}", response_model=AdminProductOut)
def update_product(product_id: int, body: ProductPatch, admin: AdminUser, services: ServicesDep):
    return services.catalog.update(product_id, body.model_dump(exclude_unset=True))


@router.get("/orders", response_model=Page[AdminOrderOut])
def all_orders(admin: AdminUser, services: ServicesDep, page: PageDep):
    orders, total = services.orders.list_all(page)
    return Page[AdminOrderOut](
        items=[AdminOrderOut.model_validate(o) for o in orders],
        page=page.page,
        size=page.size,
        total=total,
        pages=page.pages_for(total),
    )
