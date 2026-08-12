# 系统架构设计

> 状态：Approved for M0（2026-08-11）
> 决策记录：[ADR-0001](adr/0001-technology-baseline.md)

## 1. 目标与约束

SupplyPilot AI 以一个可部署的模块化单体承载 MVP。目标是先跑通活动、货品、评级、洞察与受控 Agent 的完整链路，同时保留清晰的异步任务边界，避免把批量导入、评级和规则执行耦合在 HTTP 请求中。

- 业务数据以 PostgreSQL 为唯一事实来源。
- API 使用 `/api/v1` 版本前缀；错误、日志和审计格式统一。
- Celery worker 只执行可重试的后台任务；Redis 仅作 broker/result backend，不存业务真相。
- Agent 只调用白名单工具。写操作先生成建议，再由用户确认执行。
- MVP 采用模块化单体，不提前拆微服务；模块之间通过应用服务和领域事件协作。

## 2. 技术选型

| 层级 | 选择 | M0 决策 |
|---|---|---|
| Web | Next.js、TypeScript、Tailwind CSS | App Router；服务端读取 API 健康状态 |
| UI | 自定义组件，后续按需引入 Radix primitives | token 先行，不绑定组件模板 |
| API | FastAPI、Pydantic | OpenAPI 契约、统一错误响应 |
| ORM | SQLAlchemy 2、Alembic | 显式事务和迁移 |
| Database | PostgreSQL 16 | UUID 主键、JSONB 配置、UTC 时间 |
| Async | Redis 7、Celery | 独立 worker；任务幂等键由业务模块提供 |
| Analytics | SQL、Polars（按需） | 指标先以可追溯 SQL 实现 |
| Delivery | Docker Compose、GitHub Actions | 本地与 CI 使用相同检查命令 |

## 3. 系统上下文与容器

```text
浏览器
  │ HTTP
  ▼
Next.js Web ───────► FastAPI /api/v1 ───────► PostgreSQL
                          │                       ▲
                          │ enqueue               │ read/write
                          ▼                       │
                       Redis ───────────────► Celery Worker
                          │
                          └── broker/result metadata only
```

### 后端模块边界

- `campaigns`：Campaign、SourcingTask、SupplyTarget。
- `products`：Product、ProductPoolEntry、状态迁移与校验。
- `grading`：硬规则、评分配置、GradingResult。
- `suppliers`：Supplier 与长期履约事实。
- `intelligence`：覆盖率、HHI、健康度等确定性查询。
- `alerts`：Alert 生命周期与通知入口。
- `agent`：只读工具、AgentRecommendation 和确认执行。
- `audit`：不可变审计记录。

模块可以共享数据库，但不得跨模块直接修改对方聚合；写入通过应用服务完成。

## 4. 同步、异步与事务

同步 API 负责参数校验、授权、短事务写入和查询。以下操作必须异步：批量导入校验、批量评级/重评、自动化规则执行、复盘生成。API 在同一事务中写入业务记录与任务记录，worker 使用 `idempotency_key` 防止重复执行。失败记录保留错误码、可安全展示的摘要、重试次数和下次重试时间。

建议领域事件名采用过去式：`product.submitted`、`product.validated`、`product.changed`、`grading.completed`、`supply.coverage_changed`。事件至少包含 `event_id`、`event_type`、`occurred_at`、`actor`、`aggregate_type`、`aggregate_id`、`payload_version` 和 `correlation_id`。

## 5. API、错误和日志规范

成功响应直接返回资源或分页对象。错误响应固定为：

```json
{
  "error": {
    "code": "POOL_INVALID_TRANSITION",
    "message": "商品不能从 submitted 直接进入 grading",
    "details": {"from": "submitted", "to": "grading"},
    "request_id": "01J..."
  }
}
```

日志输出单行 JSON，字段至少包含 `timestamp`、`level`、`service`、`environment`、`message`、`request_id`、`correlation_id`；不得记录密钥、完整 Prompt、导入文件内容或个人敏感信息。

## 6. 健康检查

- `GET /health`：进程存活，不访问依赖，供容器探针使用。
- `GET /api/v1/health`：返回 API 和数据库状态；数据库不可用时返回 `503`。
- Web 首页服务端请求 `API_INTERNAL_URL/api/v1/health`，展示真实连接状态。
- worker 通过 Celery ping 和容器进程状态检查；Redis/PostgreSQL 使用 Compose healthcheck。

## 7. 权限、确认与审计

M0 只定义边界，M1 实现演示角色。所有核心写操作携带 actor；状态迁移、评分失效、规则执行和 Agent 确认写入 AuditLog。AgentRecommendation 保存预览、创建时的数据版本、过期时间和确认结果；确认时必须重新检查权限、版本和过期时间。

## 8. 部署与扩展

本地由 Docker Compose 启动 `web`、`api`、`worker`、`postgres` 和 `redis`。生产环境可独立扩容 Web/API/worker；只有当团队、发布节奏或性能数据证明需要时，才从模块化单体拆分服务。
