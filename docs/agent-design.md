# Product Line Intelligence Agent 设计

> 状态：Approved for M0（2026-08-11）

## 1. 能力边界

Agent 是受控分析层，不是数据库管理员。它可以查询供给缺口、评级依据、供应商集中度、货盘健康变化、活动目标情景并生成招商任务草案；不能执行任意 SQL、读取密钥、修改评分配置或绕过用户确认改变核心数据。

## 2. 工具协议

所有工具输入由 Pydantic/JSON Schema 校验，只接受白名单筛选项，默认继承当前用户权限与页面范围。

| 工具 | 模式 | 关键输入 | 输出 |
|---|---|---|---|
| `get_supply_gaps` | read | campaign, product_line, market, dimension, as_of | targets/current/gaps、scope、freshness |
| `explain_grading` | read | pool_entry_id, result_id? | score、contributions、evidence、missing |
| `analyze_supplier_concentration` | read | campaign, market, product_line | shares、HHI、threshold、entities |
| `explain_health_change` | read | scope, from, to | dimension deltas、drivers、limitations |
| `simulate_target_change` | read | campaign, target_delta, dimension | deterministic scenario、assumptions |
| `draft_sourcing_tasks` | preview | gap ids, assignment policy | proposed tasks、validation warnings |

工具结果统一包含 `tool_call_id`、`schema_version`、`scope`、`as_of`、`data_version`、`facts`、`limitations` 和 `duration_ms`。模型不得在工具结果之外编造关键数字。

## 3. 回答协议

每次回答固定包含：

1. `conclusion`：直接回答问题。
2. `evidence`：数字、来源实体和可跳转筛选范围。
3. `methodology`：统计口径、范围、更新时间。
4. `risks_and_limits`：缺失、时效、样本与权限限制。
5. `recommended_actions`：只读建议或待确认行动。
6. `confidence`：0–1，并给出降低原因。

工具不可用时不补造答案，降级到已缓存的确定性报表并明确时间；没有可靠数据则要求用户缩小范围或补充数据。

## 4. 写操作确认协议

```text
Agent/tool 生成草案
  → 保存 AgentRecommendation(preview + base_versions + expires_at)
  → UI 展示实体级差异、影响范围、权限与不可逆影响
  → 用户明确确认
  → API 重新校验权限、过期时间和 base_versions
  → 事务执行 + AuditLog + execution_result
```

确认令牌与登录会话绑定且一次性使用。任何版本冲突、过期或权限变化都返回新预览要求，不静默套用旧建议。拒绝、修改后确认和执行失败均保留差异与原因。

## 5. 安全与审计

- 检索内容和商品文本均视为不可信数据，不能覆盖系统指令或工具策略。
- 工具层执行授权与参数校验，不能只依赖 Prompt。
- 记录工具名、参数摘要、结果摘要、耗时、错误码、用户和 request id；敏感内容脱敏。
- 评估集覆盖正确性、数字溯源、数据缺失、越权、过期确认、Prompt Injection 和依赖失败。

MVP 进入演示主线前，关键数字可溯源率必须 100%，未确认写入为 0，越权与注入测试不得出现成功写入。
