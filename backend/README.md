# Backend

FastAPI 模块化单体与 Celery worker。M1 提供核心 SQLAlchemy 实体、固定演示数据、角色上下文、驾驶舱聚合 API、统一配置/日志/错误边界以及健康检查。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

- 存活检查：`GET /health`
- 就绪检查：`GET /api/v1/health`
- 驾驶舱：`GET /api/v1/dashboard?role=marketing_ops`
- 演示角色：`GET /api/v1/demo/roles`
- 重置演示数据：`python -m app.cli.seed_demo --reset`（固定种子，可重复执行）
- OpenAPI：`GET /api/docs`
- worker：`celery -A app.tasks.celery_app:celery_app worker --loglevel=INFO`
- 迁移：`alembic upgrade head`
- 质量门禁：`ruff check . && ruff format --check . && mypy app && pytest`
