"use client";

import {
  ArrowRight, BellRing, Bot, Check, ChevronRight, CircleAlert, Clock3,
  DatabaseZap, Hotel, Plane, RotateCcw, ShieldCheck, Sparkles, TriangleAlert,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { FilterChip } from "@/components/ui/filter-chip";
import { Tag } from "@/components/ui/tag";
import {
  DashboardData, DemoRole, DemoRoleId, getDashboard, getDemoRoles,
} from "@/lib/api";

const roleOrder: DemoRoleId[] = ["marketing_ops", "sourcing_manager", "product_ops", "executive"];

function formatUpdatedAt(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit", hour12: false,
  }).format(new Date(value));
}

function LoginScreen({ roles, onEnter }: { roles: DemoRole[]; onEnter: (role: DemoRoleId) => void }) {
  const [selected, setSelected] = useState<DemoRoleId>("marketing_ops");
  const current = roles.find((role) => role.id === selected) ?? roles[0];
  return (
    <main className="login-screen">
      <section className="login-story">
        <div className="brand brand--login"><span className="brand-mark"><Sparkles /></span><span>SupplyPilot<small>AI OPERATIONS</small></span></div>
        <div className="login-story__body">
          <span className="eyebrow eyebrow--light">M1 · Live demonstration</span>
          <h1>让每一次招商决策，<br />都有清晰的数据来路。</h1>
          <p>进入“东南亚暑期旅行节”统一演示环境。不同角色拥有不同的决策队列与操作权限。</p>
        </div>
        <div className="login-signal"><span><DatabaseZap />固定种子数据</span><span><ShieldCheck />操作权限隔离</span><span><Clock3 />最后快照 08/14 09:30</span></div>
      </section>
      <section className="login-panel">
        <div><span className="section-index">DEMO ACCESS</span><h2>选择你的工作视角</h2><p>无需账号。角色可在进入后随时切换。</p></div>
        <div className="role-options">
          {roleOrder.map((id) => {
            const role = roles.find((item) => item.id === id);
            if (!role) return null;
            return <button key={id} className={selected === id ? "role-option role-option--active" : "role-option"} onClick={() => setSelected(id)}><span>{role.initials}</span><div><strong>{role.title}</strong><small>{role.description}</small></div>{selected === id && <Check />}</button>;
          })}
        </div>
        {current && <div className="role-capabilities"><span>此视角可用</span>{current.capabilities.map((item) => <Tag key={item}>{item}</Tag>)}</div>}
        <Button onClick={() => onEnter(selected)}>进入演示环境<ArrowRight /></Button>
        <small className="login-note">演示环境不连接企业身份系统，所有写入能力均为受控预览。</small>
      </section>
    </main>
  );
}

function DashboardSkeleton() {
  return <main className="dashboard-loading" aria-label="正在加载驾驶舱" aria-busy="true"><span /><span /><div><span /><span /></div><div><span /><span /><span /></div></main>;
}

export function DashboardClient() {
  const [roles, setRoles] = useState<DemoRole[]>([]);
  const [roleId, setRoleId] = useState<DemoRoleId | null>(null);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [lineFilter, setLineFilter] = useState<"all" | "hotel" | "flight">("all");

  const loadRoles = useCallback(async () => {
    setLoading(true); setError(false);
    try { setRoles(await getDemoRoles()); } catch { setError(true); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { void loadRoles(); }, [loadRoles]);

  const enter = useCallback(async (nextRole: DemoRoleId) => {
    setRoleId(nextRole); setLoading(true); setError(false);
    try { setData(await getDashboard(nextRole)); } catch { setError(true); }
    finally { setLoading(false); }
  }, []);

  const filteredCoverage = useMemo(() => data?.coverage.filter((row) => lineFilter === "all" || row.product_line === lineFilter) ?? [], [data, lineFilter]);

  if (loading && !data) return <DashboardSkeleton />;
  if (error && !data) return <main className="standalone-state"><ErrorState title="暂时无法载入演示环境" description="请确认 API 与 PostgreSQL 已启动，然后重试。" action={<Button onClick={() => void loadRoles()}><RotateCcw />重新连接</Button>} /></main>;
  if (!roleId) {
    if (!roles.length) return <main className="standalone-state"><EmptyState title="暂无演示角色" description="角色配置为空，请重置演示数据后重试。" /></main>;
    return <LoginScreen roles={roles} onEnter={(role) => void enter(role)} />;
  }
  if (!data) return <DashboardSkeleton />;

  return (
    <AppShell apiReady={!error} campaignName={data.campaign.name} role={data.role} roles={roles} onRoleChange={(role) => void enter(role)}>
      <main className={loading ? "dashboard dashboard--refreshing" : "dashboard"} aria-busy={loading}>
        <section className="page-head dashboard-head">
          <div><span className="eyebrow">Supply chain cockpit</span><h1>今天有 {data.decision_queue.length} 项需要决策</h1><p>{data.role.title}视角 · 其中 2 项会影响东南亚暑期旅行节的活动准备度</p></div>
          <div className="head-actions"><span className="updated-at"><span className="status-dot" />数据更新于 {formatUpdatedAt(data.updated_at)}</span>{data.permissions.create_campaign && <Button>创建招商活动</Button>}</div>
        </section>

        <section className="decision-health-grid">
          <div className="decision-queue">
            <div className="section-head"><div><span className="section-index">01</span><h2>决策队列</h2></div><Tag>{data.decision_queue.length} 项未处理</Tag></div>
            <div className="decision-list">
              {data.decision_queue.map((item, index) => <article className="decision-item" key={item.id}><span className={`priority priority--${item.severity.toLowerCase()}`}>{item.severity}</span><div><strong>{item.title}</strong><small>{item.type === "supplier_concentration" ? "HHI 0.61 · 头部供应商占比 75% · 阈值 45%" : item.type === "inventory_gap" ? "距目标仍缺 456 库存 · 招商截止还有 6 天" : item.type === "audience_gap" ? "当前仅覆盖 3 / 8 个目标商品" : "Hotel 8 个 · Flight 4 个"}</small></div>{item.action ? <button className="text-action">{item.action}<ChevronRight /></button> : <span className="readonly-label">只读</span>}{index === 0 && <span className="decision-pulse" />}</article>)}
            </div>
          </div>
          <aside className="health-panel">
            <div className="section-head"><div><span className="section-index">02</span><h2>货盘健康度</h2></div><span className="negative-change">较上周 {data.health.weekly_change}</span></div>
            <div className="health-score"><strong>{data.health.score}</strong><span>/ 100<small>需要关注</small></span></div>
            <div className="health-bars">{data.health.dimensions.map((dimension) => <div key={dimension.name}><span>{dimension.name}<small>{dimension.change > 0 ? `+${dimension.change}` : dimension.change}</small></span><i><b style={{ width: `${dimension.score}%` }} /></i><strong>{dimension.score}</strong></div>)}</div>
            <button className="methodology"><CircleAlert />查看计算口径<span>{data.health.methodology}</span></button>
          </aside>
        </section>

        <section className="readiness-panel">
          <div className="section-head"><div><span className="section-index">03</span><h2>活动准备度</h2></div><span className="deadline"><Clock3 />招商截止 8 月 20 日 · 剩余 6 天</span></div>
          <div className="readiness-flow">
            {([ ["招商目标", "target"], ["已提交", "submitted"], ["已校验", "validated"], ["高评级", "high_grade"], ["已上架", "listed"] ] as const).map(([label, key], index) => <div key={key} className={index === 4 ? "readiness-step readiness-step--last" : "readiness-step"}><span>{String(index + 1).padStart(2, "0")}</span><strong>{data.readiness[key]}</strong><small>{label}</small>{index < 4 && <i><b style={{ width: `${Math.min(100, (data.readiness[key] / data.readiness.target) * 100)}%` }} /></i>}</div>)}
          </div>
        </section>

        <section className="coverage-agent-grid">
          <div className="coverage-panel">
            <div className="section-head"><div><span className="section-index">04</span><h2>市场 × 产线供给覆盖</h2></div><div className="mini-filters"><FilterChip selected={lineFilter === "all"} onClick={() => setLineFilter("all")}>全部</FilterChip><FilterChip selected={lineFilter === "hotel"} onClick={() => setLineFilter("hotel")}>Hotel</FilterChip><FilterChip selected={lineFilter === "flight"} onClick={() => setLineFilter("flight")}>Flight</FilterChip></div></div>
            {filteredCoverage.length ? <div className="coverage-table"><div className="coverage-row coverage-row--head"><span>客源市场 / 范围</span><span>产线</span><span>商品</span><span>库存</span><span>覆盖率</span></div>{filteredCoverage.map((row) => <div className="coverage-row" key={`${row.market}-${row.product_line}-${row.scope}`}><span><strong>{row.market}</strong><small>{row.scope}{row.audience ? ` · ${row.audience}` : ""}</small></span><span className="line-label">{row.product_line === "hotel" ? <Hotel /> : <Plane />}{row.product_line === "hotel" ? "Hotel" : "Flight"}</span><span>{row.current_products}<small>/ {row.target_products}</small></span><span>{row.current_inventory}<small>/ {row.target_inventory}</small></span><span><i className={`coverage-meter ${row.coverage_rate < .5 ? "coverage-meter--risk" : row.coverage_rate < .75 ? "coverage-meter--warn" : ""}`}><b style={{ width: `${row.coverage_rate * 100}%` }} /></i><strong>{Math.round(row.coverage_rate * 100)}%</strong></span></div>)}</div> : <EmptyState title="当前筛选下没有覆盖目标" description="切换产线筛选，或为该市场配置供给目标。" />}
          </div>
          <aside className="agent-brief">
            <div className="agent-brief__head"><span><Bot /></span><div><small>INTELLIGENCE BRIEF</small><h2>今日建议</h2></div></div>
            <p className="agent-conclusion"><TriangleAlert />优先补充上海—普吉航线库存，同时降低曼谷酒店对单一供应商的依赖。</p>
            <dl><div><dt>数据依据</dt><dd>航线库存缺口 38%；曼谷 HHI 0.61，超过 0.45 阈值。</dd></div><div><dt>行动建议</dt><dd>向 2 家备选供应商发起定向招商，目标补充 456 库存。</dd></div></dl>
            <Button disabled={!data.permissions.create_task} variant="secondary">{data.permissions.create_task ? "预览招商任务" : "当前角色仅可查看"}<ArrowRight /></Button>
            <small className="agent-guard"><ShieldCheck />Agent 默认只读，行动将在确认后执行</small>
          </aside>
        </section>
        {error && <div className="refresh-warning"><BellRing />角色数据刷新失败，当前仍显示上一次成功结果。</div>}
      </main>
    </AppShell>
  );
}
