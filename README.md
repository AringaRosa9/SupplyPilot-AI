# SupplyPilot AI

面向全球旅游电商的供应链招商自动化、产品评级与货盘决策平台。

SupplyPilot AI 覆盖从营销活动发起、招商任务拆解、商品提交、自动校验、产品评级、货品池管理，到供给缺口识别、供应商风险预警和产线复盘的完整链路。项目希望展示如何将 AI Agent、可解释评分模型和事件驱动自动化真正嵌入供应链工作流，而不只是为数据增加一个聊天入口。

> 当前阶段：产品设计与工程框架搭建。仓库暂不包含业务代码。

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

## 计划技术架构

| 层级 | 候选技术 |
|---|---|
| Web | Next.js、TypeScript、Tailwind CSS、ECharts |
| API | FastAPI 或 NestJS，待架构阶段确认 |
| 数据库 | PostgreSQL |
| 异步任务 | Celery 或 BullMQ |
| 数据分析 | SQL、Polars / Pandas |
| AI | LLM Tool Calling、受控分析工具、可选 RAG |
| 交付 | Docker Compose、自动化测试、GitHub Actions |

架构原则：评分结果可解释、模型与规则可版本化、Agent 操作受控、关键变更需要确认、所有自动状态变更可审计。

## 仓库结构

```text
supplypilot-ai/
├── README.md
├── CONTRIBUTING.md
├── .gitignore
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   ├── scoring-model.md
│   ├── agent-design.md
│   ├── data-dictionary.md
│   └── demo-script.md
├── frontend/
│   └── README.md
├── backend/
│   └── README.md
├── data/
│   └── README.md
└── notebooks/
    └── README.md
```

## 文档导航

- [产品需求文档](docs/PRD.md)
- [系统架构设计](docs/architecture.md)
- [产品评分模型](docs/scoring-model.md)
- [Agent 设计](docs/agent-design.md)
- [数据字典](docs/data-dictionary.md)
- [演示脚本](docs/demo-script.md)
- [贡献指南](CONTRIBUTING.md)

除 PRD 外，其余设计文档目前为待完善的框架，后续会伴随技术选型和 MVP 开发逐步补齐。

## 里程碑

- [x] 确定项目定位与名称
- [x] 完成初版 PRD
- [x] 建立文档和工程目录骨架
- [ ] 完成信息架构、数据模型和系统架构设计
- [ ] 准备可复现的模拟数据集
- [ ] 实现活动、招商任务与货品池基础链路
- [ ] 实现 Hotel / Flight 评级引擎
- [ ] 实现供给洞察、自动化规则与 Agent
- [ ] 完成测试、Docker 化、演示视频和项目复盘

## 项目状态

SupplyPilot AI 目前处于设计阶段，接口、数据结构和技术选型都可能继续调整。现阶段以 [PRD](docs/PRD.md) 作为产品范围基线。

