import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.domains import router as domains_router
from app.db.session import init_db

load_dotenv(override=True)


def get_cors_origins() -> list[str]:
    """Read allowed frontend URLs from .env."""
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown logic for the API."""
    await init_db()
    yield


app = FastAPI(
    title="AgentOS API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(domains_router)


@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    """Small route used to confirm the backend is alive."""
    return {"status": "ok"}