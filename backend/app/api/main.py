from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import health
from app.api.v1 import assets, vulnerabilities, security_scans, dashboard, policies, compliance, ai_chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["assets"])
app.include_router(vulnerabilities.router, prefix="/api/v1/vulnerabilities", tags=["vulnerabilities"])
app.include_router(security_scans.router, prefix="/api/v1/scans", tags=["security-scans"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["policies"])
app.include_router(compliance.router, prefix="/api/v1", tags=["compliance"])
app.include_router(ai_chat.router, prefix="/api/v1/ai", tags=["ai"])
