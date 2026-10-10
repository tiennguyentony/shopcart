class DomainError(Exception):
    """Base class for errors the API turns into a 4xx response."""

    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFound(DomainError):
    status_code = 404
    code = "NOT_FOUND"

    def __init__(self, what: str):
        super().__init__(f"{what} not found")


class Unauthorized(DomainError):
    status_code = 401
    code = "UNAUTHORIZED"


class Forbidden(DomainError):
    status_code = 403
    code = "FORBIDDEN"


class OutOfStock(DomainError):
    status_code = 409
    code = "OUT_OF_STOCK"

    def __init__(self, product_name: str, available: int):
        super().__init__(f"Only {available} of '{product_name}' left in stock")


class InvalidCoupon(DomainError):
    status_code = 422
    code = "INVALID_COUPON"


class EmptyCart(DomainError):
    code = "EMPTY_CART"

    def __init__(self) -> None:
        super().__init__("Your cart is empty")
