import { ArrowRight, Check, Clock3, Database, ShieldCheck, TriangleAlert } from "lucide-react";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { FilterChip } from "@/components/ui/filter-chip";
import { Tag } from "@/components/ui/tag";
import { getApiHealth } from "@/lib/api";

type Foundation = { layer: string; contract: string; status: string };
const foundations: Foundation[] = [
  { layer: "业务数据", contract: "10 个核心实体与活动级货品状态", status: "已固化" },
  { layer: "评级引擎", contract: "Hotel / Flight 独立硬规则、权重与置信度", status: "已固化" },
  { layer: "Agent 边界", contract: "受控工具与预览—确认—执行协议", status: "已固化" },
  { layer: "运行环境", contract: "Web / API / PostgreSQL / Redis / Worker", status: "可启动" },
];

export default async function Home() {
  const health = await getApiHealth().catch(() => null);
  const ready = health?.status === "ok";
  return (
    <AppShell apiReady={ready}>
      <main>
        <section className="page-head">
          <div><span className="eyebrow">M0 · Engineering foundation</span><h1>供应链决策工作台</h1><p>设计契约和工程边界已就位，下一阶段将由统一演示数据驱动业务壳层。</p></div>
          <div className="filters"><FilterChip selected>全部市场</FilterChip><FilterChip>Hotel</FilterChip><FilterChip>Flight</FilterChip></div>
        </section>

        <section className="readiness-strip" aria-label="工程就绪状态">
          <div><span>当前阶段</span><strong>M0 · 工程骨架</strong></div>
          <div><span>API</span><strong className={ready ? "healthy" : "waiting"}>{ready ? "已连接" : "等待连接"}</strong></div>
          <div><span>数据库</span><strong>{health?.checks.database === "ok" ? "PostgreSQL 正常" : "待启动"}</strong></div>
          <Button variant="secondary">查看架构约定<ArrowRight /></Button>
        </section>

        <div className="workspace-grid">
          <section className="decision-panel">
            <div className="section-head"><div><span className="section-index">01</span><h2>工程就绪清单</h2></div><Tag>{ready ? "环境可用" : "等待 Docker"}</Tag></div>
            <DataTable caption="M0 工程就绪清单" rows={foundations} rowKey={(row) => row.layer} columns={[
              { key: "layer", header: "层级", render: (row) => <strong>{row.layer}</strong> },
              { key: "contract", header: "固化内容", render: (row) => row.contract },
              { key: "status", header: "状态", render: (row) => <span className="table-status"><Check />{row.status}</span> },
            ]} />
          </section>
          <aside className="principles-panel">
            <div className="section-head"><div><span className="section-index">02</span><h2>系统护栏</h2></div><ShieldCheck /></div>
            <ul><li><Database /><span><strong>业务事实只进 PostgreSQL</strong><small>队列不承担持久化事实</small></span></li><li><Clock3 /><span><strong>批处理脱离 HTTP 请求</strong><small>导入、评级与规则执行进入 worker</small></span></li><li><TriangleAlert /><span><strong>Agent 写入必须确认</strong><small>版本、权限和过期时间二次校验</small></span></li></ul>
          </aside>
        </div>
        <section className="next-slice"><span className="section-index">03</span><div><h2>下一纵向切片</h2><p>载入“东南亚暑期旅行节”固定演示数据，让风险队列、货盘健康和市场覆盖矩阵从真实 API 读取。</p></div><Button>进入 M1<ArrowRight /></Button></section>
      </main>
    </AppShell>
  );
}
