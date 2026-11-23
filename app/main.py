"""FastAPI ilovasi: http://localhost:8000/docs — Swagger UI."""

from fastapi import FastAPI

from .database import init_db
from .routers import auth

init_db()

app = FastAPI(
    title="Avtorizatsiya API",
    description=(
        "SQLite asosidagi avtorizatsiya API. Ro'yxatdan o'tish, login, "
        "access/refresh tokenlar va himoyalangan endpoint.\n\n"
        "Swagger orqali sinash: **Authorize** tugmasiga username va parolni kiriting."
    ),
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(auth.router)


@app.get("/", tags=["Tizim"], summary="Ma'lumot")
def root():
    return {
        "message": "Avtorizatsiya API ishlamoqda",
        "docs": "/docs",
        "endpoints": ["/register", "/login", "/login/json", "/refresh", "/me"],
    }


@app.get("/health", tags=["Tizim"], summary="Sog'liqni tekshirish")
def health():
    return {"status": "ok"}
