from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database import DEFAULT_DATABASE_PATH, initialize_database
from backend.routes.audit import router as audit_router
from backend.routes.targets import router as targets_router


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_app(database_path: Path = DEFAULT_DATABASE_PATH) -> FastAPI:
    resolved_database_path = Path(database_path).resolve()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        initialize_database(resolved_database_path)
        yield

    application = FastAPI(
        title="SentinelScan API",
        description=(
            "API local para registrar ativos, escopo autorizado e auditoria. "
            "Esta etapa não executa varreduras."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    application.state.database_path = resolved_database_path
    application.include_router(targets_router)
    application.include_router(audit_router)

    @application.get("/api/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "inventory-only"}

    @application.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "index.html")

    application.mount(
        "/css",
        StaticFiles(directory=PROJECT_ROOT / "css", check_dir=False),
        name="css",
    )
    application.mount(
        "/js",
        StaticFiles(directory=PROJECT_ROOT / "js", check_dir=False),
        name="js",
    )
    return application


app = create_app()
