import sqlite3
from dataclasses import dataclass, field

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shopcart.clock import Clock, SystemClock
from shopcart.config import Settings, load_settings
from shopcart.db import open_database
from shopcart.domain.errors import DomainError
from shopcart.routes import admin, auth, cart, orders, products
from shopcart.seed import seed_if_empty
from shopcart.services import build_services


@dataclass
class AppDeps:
    conn: sqlite3.Connection
    clock: Clock = field(default_factory=SystemClock)
    settings: Settings = field(default_factory=Settings)


def default_deps() -> AppDeps:
    settings = load_settings()
    conn = open_database(settings.db_path)
    clock = SystemClock()
    if settings.seed_demo_data:
        seed_if_empty(conn, clock)
    return AppDeps(conn=conn, clock=clock, settings=settings)


# Composition root: everything the app depends on comes in through AppDeps,
# so tests can pass an in-memory database and a fake clock.
def create_app(deps: AppDeps | None = None) -> FastAPI:
    deps = deps or default_deps()
    app = FastAPI(title="Shopcart", version="0.4.0")
    app.state.services = build_services(deps.conn, deps.clock, deps.settings)

    @app.exception_handler(DomainError)
    def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.get("/health", tags=["meta"])
    def health():
        return {"ok": True}

    for module in (auth, products, cart, orders, admin):
        app.include_router(module.router)
    return app
