from fastapi import APIRouter

from shopcart.routes.deps import CurrentUser, ServicesDep
from shopcart.routes.schemas import LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, services: ServicesDep):
    return TokenOut(token=services.auth.login(body.email, body.password))


@router.get("/me")
def me(user: CurrentUser):
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}
