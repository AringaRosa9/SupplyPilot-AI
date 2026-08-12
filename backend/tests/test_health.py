from fastapi.testclient import TestClient

from app.api.v1 import health as health_module
from app.main import app


def test_liveness() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-request-id"]


def test_readiness_reports_database(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def database_is_ready() -> bool:
        return True

    monkeypatch.setattr(health_module, "check_database", database_is_ready)
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["checks"] == {"database": "ok"}
