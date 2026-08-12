# ADR-0001：MVP 技术基线

- 状态：Accepted
- 日期：2026-08-11

## 决策

采用 Next.js + TypeScript + Tailwind CSS 构建 Web，FastAPI + Pydantic + SQLAlchemy 2 + Alembic 构建模块化单体 API，PostgreSQL 保存业务事实，Redis + Celery 执行后台任务，Docker Compose 提供本地环境，GitHub Actions 执行质量门禁。

## 原因

该组合适合高密度数据工作台，也让评分、分析和 Agent 工具共享 Python 生态。MVP 的领域尚在快速演进，模块化单体比微服务具有更低的部署与事务成本；独立 worker 又能防止批处理阻塞 HTTP。

## 后果

- 团队必须维护 Python 与 TypeScript 两套质量工具。
- Redis/Celery 增加一个运行依赖，但换取明确的异步和重试边界。
- 模块共享数据库，因此需要代码审查保证模块写边界。
- 若 Celery 运维成本在真实数据下不成立，可替换为数据库任务表，但任务接口与幂等约定不变。
