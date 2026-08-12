from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text

from app.db.session import engine

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: str
    version: str
    checks: dict[str, str]


async def check_database() -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse | JSONResponse:
    database_ok = await check_database()
    payload = HealthResponse(
        status="ok" if database_ok else "degraded",
        service="api",
        version="0.1.0",
        checks={"database": "ok" if database_ok else "unavailable"},
    )
    if not database_ok:
        return JSONResponse(status_code=503, content=payload.model_dump())
    return payload
