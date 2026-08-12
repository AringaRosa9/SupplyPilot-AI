# Backend

FastAPI 模块化单体与 Celery worker。当前 M0 提供核心 SQLAlchemy 实体、Alembic 初始迁移、统一配置/日志/错误边界以及健康检查。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

- 存活检查：`GET /health`
- 就绪检查：`GET /api/v1/health`
- OpenAPI：`GET /api/docs`
- worker：`celery -A app.tasks.celery_app:celery_app worker --loglevel=INFO`
- 迁移：`alembic upgrade head`
- 质量门禁：`ruff check . && ruff format --check . && mypy app && pytest`
