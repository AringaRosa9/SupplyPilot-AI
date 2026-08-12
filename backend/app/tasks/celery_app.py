from celery import Celery  # type: ignore[import-untyped]

from app.core.config import settings

celery_app = Celery("supplypilot", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    timezone="UTC",
)


@celery_app.task(name="system.ping")  # type: ignore[untyped-decorator]
def ping() -> dict[str, str]:
    return {"status": "ok", "worker": "supplypilot"}
