# SupplyPilot AI

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

面向全球旅游电商的供应链招商自动化、产品评级与货盘决策平台。

SupplyPilot AI 覆盖从营销活动发起、招商任务拆解、商品提交、自动校验、产品评级、货品池管理，到供给缺口识别、供应商风险预警和产线复盘的完整链路。项目希望展示如何将 AI Agent、可解释评分模型和事件驱动自动化真正嵌入供应链工作流，而不只是为数据增加一个聊天入口。

> 当前阶段：M1 演示数据与产品壳层已完成，下一阶段为 M2 招商业务闭环。

## 核心场景

以“东南亚暑期旅行节”为例，系统可以：

1. 将自然语言活动需求转换为结构化招商要求。
2. 识别目标市场、酒店类型和航线的供给缺口。
3. 自动生成并分发 Hotel、Flight 产线招商任务。
4. 校验供应商提交的价格、库存和活动适配性。
5. 使用产线独立模型完成商品评级，并给出置信度与解释。
6. 监测货盘健康度和供应商集中度，触发补充招商预警。
7. 为商品上架和前台排序提供建议。
8. 活动结束后生成产线及供应商复盘报告。

## 产品能力

- 招商活动与任务协同
- AI 招商需求结构化
- 商品批量提交与自动校验
- 全生命周期货品池管理
- Hotel / Flight 可解释评级模型
- Product Line Intelligence Agent
- 供给缺口、集中度与货盘健康度分析
- 事件驱动的自动化规则与预警
- 跨活动产线及供应商复盘

## MVP 范围

第一阶段聚焦 Hotel 和 Flight 两条产线，完成一条可演示的端到端业务链路：

```text
创建活动 → 拆解招商任务 → 导入商品 → 自动校验 → 产品评级
        → 人工审核 → 建议上架 → 供给洞察 → 活动复盘
```

MVP 将包含活动管理、CSV 导入、规则校验、两套评分模型、货品池看板、供给分析、Agent 数据问答、自动预警以及可复现的模拟数据。

## 技术架构

| 层级 | 候选技术 |
|---|---|
| Web | Next.js、TypeScript、Tailwind CSS；图表阶段引入 ECharts |
| API | FastAPI、Pydantic、SQLAlchemy 2、Alembic |
| 数据库 | PostgreSQL 16 |
| 异步任务 | Redis、Celery |
| 数据分析 | SQL、Polars（按需） |
| AI | LLM Tool Calling、受控分析工具、可选 RAG |
| 交付 | Docker Compose、自动化测试、GitHub Actions |

架构原则：评分结果可解释、模型与规则可版本化、Agent 操作受控、关键变更需要确认、所有自动状态变更可审计。完整决策见 [系统架构设计](docs/architecture.md)。

## 仓库结构

```text
supplypilot-ai/
├── README.md
├── README.en.md
├── README.ja.md
├── CONTRIBUTING.md
├── .gitignore
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   ├── scoring-model.md
│   ├── agent-design.md
│   ├── data-dictionary.md
│   └── demo-script.md
├── frontend/             # Next.js Web 与基础组件
├── backend/              # FastAPI、Celery、SQLAlchemy 与迁移
├── docker-compose.yml
├── Makefile
├── data/
│   └── README.md
└── notebooks/
    └── README.md
```

## 文档导航

- [产品需求文档](docs/PRD.md)
- [前端页面与布局方案](docs/frontend-design.md)
- [MVP 开发计划](docs/development-plan.md)
- [系统架构设计](docs/architecture.md)
- [产品评分模型](docs/scoring-model.md)
- [Agent 设计](docs/agent-design.md)
- [数据字典](docs/data-dictionary.md)
- [演示脚本](docs/demo-script.md)
- [贡献指南](CONTRIBUTING.md)

M1 已在工程骨架上补齐固定演示数据、轻量角色上下文和真实 API 驱动的供应链驾驶舱；后续里程碑将在这条可复现演示基线上迭代。

## 本地启动

复制环境变量并启动全部组件：

```bash
cp .env.example .env
docker compose up --build
```

首次启动后可随时将数据库恢复到固定演示状态：

```bash
make demo-reset
```

- Web：<http://localhost:3000>
- API 健康检查：<http://localhost:8000/api/v1/health>
- 驾驶舱 API：<http://localhost:8000/api/v1/dashboard?role=marketing_ops>
- OpenAPI：<http://localhost:8000/api/docs>

执行本地质量门禁：`make check`。首次运行需要先按 `backend/README.md` 和 `frontend/README.md` 安装开发依赖。

## 里程碑

- [x] 确定项目定位与名称
- [x] 完成初版 PRD
- [x] 建立文档和工程目录骨架
- [x] 完成信息架构、数据模型和系统架构设计
- [x] 准备可复现的模拟数据集与驾驶舱产品壳层
- [ ] 实现活动、招商任务与货品池基础链路
- [ ] 实现 Hotel / Flight 评级引擎
- [ ] 实现供给洞察、自动化规则与 Agent
- [ ] 完成测试、Docker 化、演示视频和项目复盘

## 项目状态

SupplyPilot AI 已完成 M1。固定演示数据、轻量角色上下文和真实 API 驱动的供应链驾驶舱已可用于后续纵向切片。产品范围以 [PRD](docs/PRD.md) 为基线，技术与业务契约的变更应通过 ADR、迁移和对应测试同步记录。
