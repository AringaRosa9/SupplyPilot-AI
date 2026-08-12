# 数据字典与业务状态

> 状态：Approved for M0（2026-08-11）
> 约定：字段使用 `snake_case`；主键为 UUID；时间为带时区 UTC；金额使用 `numeric(18,2)` + ISO 4217 币种。

## 1. 实体关系

```text
Campaign 1──* SourcingTask
Campaign 1──* SupplyTarget
Campaign 1──* ProductPoolEntry *──1 Product *──1 Supplier
ProductPoolEntry 1──* GradingResult
Campaign 1──* Alert
AgentRecommendation ──optional──► Campaign / Task / PoolEntry
AuditLog ──polymorphic──► every audited aggregate
```

同一 Product 可以进入多个 Campaign；活动级状态与评级快照只存在于 ProductPoolEntry/GradingResult，不写回 Product 主数据。

## 2. 核心实体

所有实体默认包含 `id`、`created_at`、`updated_at`，AuditLog 只追加不更新。

| 实体 | 关键字段 | 约束与说明 |
|---|---|---|
| Campaign | `name`, `description`, `status`, `target_markets[]`, `product_lines[]`, `starts_at`, `ends_at`, `sourcing_deadline`, `owner_id`, `requirements` | `draft/planned/active/completed/archived`；结束不早于开始 |
| SourcingTask | `campaign_id`, `product_line`, `scope`, `assignee_id`, `priority`, `status`, `due_at`, `progress` | status: `todo/in_progress/blocked/completed/cancelled`；progress 0–100 |
| Product | `external_code`, `product_line`, `supplier_id`, `name`, `market`, `attributes`, `data_version` | `(supplier_id, external_code)` 唯一；关键字段变化递增 data_version |
| ProductPoolEntry | `campaign_id`, `product_id`, `status`, `exception_status`, `current_grading_result_id`, `status_reason`, `version` | `(campaign_id, product_id)` 唯一；乐观锁 version |
| GradingResult | `pool_entry_id`, `product_line`, `model_version`, `input_version`, `input_snapshot`, `dimension_scores`, `score`, `grade`, `confidence`, `missing_fields`, `is_current`, `computed_at` | 历史不可变；同一 entry 仅一个 current 结果 |
| Supplier | `code`, `name`, `status`, `markets[]`, `quality_score`, `performance` | code 唯一；status: `active/watchlist/suspended/inactive` |
| SupplyTarget | `campaign_id`, `product_line`, `market`, `dimension`, `target_product_count`, `target_inventory` | 目标数非负；dimension 存城市/航线/客群等受控 JSON |
| Alert | `campaign_id`, `type`, `severity`, `status`, `entity_type`, `entity_id`, `facts`, `owner_id` | status: `open/acknowledged/resolved/ignored`；severity: `p0..p3` |
| AuditLog | `actor_type`, `actor_id`, `action`, `entity_type`, `entity_id`, `before`, `after`, `reason`, `request_id`, `occurred_at` | 只追加；敏感字段在写入前脱敏 |
| AgentRecommendation | `tool_name`, `status`, `scope`, `evidence`, `proposed_action`, `base_versions`, `expires_at`, `confirmed_by`, `confirmed_at`, `execution_result` | `preview/confirmed/executed/rejected/expired/failed` |

辅助实体 `ScoringModel`、`ProductSnapshot`、`AutomationRule`、`TaskRun` 和 `SupplierPerformance` 在对应功能进入开发时创建，但其版本引用已在上述字段中预留。

## 3. 货品池状态机

### 主状态

```text
sourcing → submitted → validating → ready_for_grading → grading
                                      ▲                 │
                                      └─────────────────┤ retry
                                                        ▼
                               pending_review → ready_to_list → listed
```

`exception_status` 与主状态正交，可为空或为：`needs_information`、`grading_failed`、`rejected`、`expired`、`delisted`。异常解除后回到同一主状态或通过显式迁移推进，禁止通过直接改字段“跳状态”。

| 从 | 到 | 触发者 | 前置条件 | 审计内容 |
|---|---|---|---|---|
| sourcing | submitted | user/import | Product 已创建且关联活动 | 导入批次、操作者、来源 |
| submitted | validating | system | 校验任务已入队 | task id、input version |
| validating | ready_for_grading | system | 阻塞校验为 0 | 规则版本、结果摘要 |
| ready_for_grading | grading | system | 有效评分模型存在 | model version、task id |
| grading | pending_review | system | 评分成功且为 current | result id、score、confidence |
| pending_review | ready_to_list | authorized user | 审核通过；低置信度已显式确认 | 审核意见、actor |
| ready_to_list | listed | authorized user/system | 活动有效且商品未过期 | 渠道、发布时间 |
| grading | ready_for_grading | worker | 失败可重试 | error code、retry count |

任何关键 Product 字段变化：旧结果 `is_current=false`，关联的非终态 entry 迁移到 `ready_for_grading` 并写审计；`listed` 商品先标记 `needs_information`，由授权用户确认是否重评/下架。

### 异常规则

- `needs_information`：缺少非硬阻塞字段；补齐并复验后清除。
- `grading_failed`：计算或依赖失败；保留主状态和可重试任务。
- `rejected`：仅人工审核产生；必须填写原因，可重新提交到 `submitted`。
- `expired`：活动日期、价格或库存时效失效；重新提供有效数据后复验。
- `delisted`：已上架商品被撤下；记录渠道和原因。

## 4. 指标口径

所有指标必须返回 `scope`、`as_of`、分子、分母和数据完整度。

- 覆盖率 = `min(current / target, 1)`；商品覆盖与库存覆盖分别计算，目标为 0 时返回 `null`，不返回 100%。
- 库存缺口 = `max(target_inventory - eligible_inventory, 0)`；eligible 仅含校验通过、未过期、非拒绝/下架商品。
- 高评级占比 = 当前有效评级为 S/A 的 eligible 商品数 ÷ 当前有效评级商品数；分母为 0 返回 `null`。
- HHI = `Σ supplier_share² × 10,000`，share 基于范围内 eligible 库存；`<1500` 低、`1500–2499` 中、`≥2500` 高集中。无库存返回 `null`。
- 货盘健康度 = `25% 供给目标完成度 + 20% 高评级占比 + 15% 库存稳定性 + 15% 价格竞争力 + 15% 供应商多样性 + 10% 商品新鲜度`；每维 0–100，缺失维度不默认为 0，而按可用权重归一并降低完整度。

`supplier_diversity_score = clamp(100 × (1 - HHI / 10000), 0, 100)`。指标实现若修改阈值或资格范围，必须升级口径版本。
