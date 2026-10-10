from typing import Annotated

from fastapi import Depends, Header, Query, Request

from shopcart.domain.errors import Forbidden, Unauthorized
from shopcart.domain.pagination import MAX_PAGE_SIZE, PageRequest
from shopcart.repositories.users import User
from shopcart.services import Services


def get_services(request: Request) -> Services:
    return request.app.state.services


ServicesDep = Annotated[Services, Depends(get_services)]


def current_user(services: ServicesDep, authorization: Annotated[str | None, Header()] = None) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise Unauthorized("Missing bearer token")
    user = services.auth.user_for_token(authorization[7:].strip())
    if user is None:
        raise Unauthorized("Invalid or expired token")
    return user


def require_admin(user: Annotated[User, Depends(current_user)]) -> User:
    if not user.is_admin:
        raise Forbidden("Admins only")
    return user


def page_params(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 10,
) -> PageRequest:
    return PageRequest(page=page, size=size)


CurrentUser = Annotated[User, Depends(current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
PageDep = Annotated[PageRequest, Depends(page_params)]
