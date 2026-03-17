from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from app.api.endpoints import admin, auth, mock_biz, users
from app.core.config import settings

_log_handlers: list = [logging.StreamHandler()]
if not settings.DEBUG:
    _log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app.log")
    try:
        _log_handlers.append(logging.FileHandler(_log_file))
    except OSError:
        pass  # не критично — логи идут в stdout

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=_log_handlers,
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Система аутентификации и разграничения прав доступа",
    version="1.0.0",
    debug=settings.DEBUG,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(mock_biz.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
async def root() -> dict:
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "api_version": settings.API_V1_PREFIX,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
