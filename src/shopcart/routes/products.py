from fastapi import APIRouter

from shopcart.routes.deps import PageDep, ServicesDep
from shopcart.routes.schemas import Page, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=Page[ProductOut])
def list_products(
    services: ServicesDep,
    page: PageDep,
    search: str | None = None,
    category: str | None = None,
):
    products, total = services.catalog.list_published(page, search=search, category=category)
    return Page[ProductOut](
        items=[ProductOut.model_validate(p) for p in products],
        page=page.page,
        size=page.size,
        total=total,
        pages=page.pages_for(total),
    )


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, services: ServicesDep):
    return services.catalog.get_published(product_id)
