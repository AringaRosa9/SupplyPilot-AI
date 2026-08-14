"use client";

import { Activity, Bell, Bot, Boxes, ChevronDown, Gauge, Search, SlidersHorizontal, Sparkles, Workflow } from "lucide-react";
import { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { Drawer } from "@/components/ui/drawer";
import { Tag } from "@/components/ui/tag";
import type { DemoRole, DemoRoleId } from "@/lib/api";

const navigation = [
  ["驾驶舱", Gauge], ["招商活动", Activity], ["货品池", Boxes], ["供给洞察", SlidersHorizontal], ["自动化", Workflow],
] as const;

export function AppShell({
  children, apiReady, campaignName, role, roles, onRoleChange,
}: {
  children: ReactNode;
  apiReady: boolean;
  campaignName: string;
  role: DemoRole;
  roles: DemoRole[];
  onRoleChange: (role: DemoRoleId) => void;
}) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark"><Sparkles /></span><span>SupplyPilot<small>AI OPERATIONS</small></span></div>
        <p className="nav-label">工作空间</p>
        <nav aria-label="主导航">{navigation.map(([label, Icon], index) => <a className={index === 0 ? "nav-item nav-item--active" : "nav-item"} href="#" key={label}><Icon />{label}</a>)}</nav>
        <div className="sidebar-status"><span className={apiReady ? "status-dot" : "status-dot status-dot--down"} />{apiReady ? "演示数据已同步" : "API 等待连接"}<small>产品壳层 · M1</small></div>
      </aside>
      <section className="main-shell">
        <header className="topbar">
          <label className="search"><Search /><span className="sr-only">全局搜索</span><input placeholder="搜索活动、商品或供应商" /><kbd>⌘ K</kbd></label>
          <button className="context-button"><span className="status-dot" />{campaignName}<ChevronDown /></button>
          <div className="top-actions">
            <Drawer title="Product Line Intelligence" trigger={<Button><Bot />询问 Agent</Button>}>
              <div className="agent-context"><span>当前分析范围</span><Tag>东南亚暑期旅行节</Tag><Tag>Hotel + Flight</Tag></div>
              <div className="agent-empty"><Bot /><strong>从业务上下文开始</strong><p>Agent 默认只读。涉及创建任务或状态变更时，会先展示可审计的行动预览。</p><button>哪些市场存在供给缺口？</button><button>解释本周货盘健康度变化</button></div>
            </Drawer>
            <button className="icon-button" aria-label="通知，4 条未读"><Bell /><i /></button>
            <label className="role-switcher">
              <span className="avatar" aria-hidden="true">{role.initials}</span>
              <span className="role-switcher__copy"><small>{role.title}</small><strong>{role.name}</strong></span>
              <select aria-label="切换演示角色" value={role.id} onChange={(event) => onRoleChange(event.target.value as DemoRoleId)}>
                {roles.map((option) => <option key={option.id} value={option.id}>{option.title} · {option.name}</option>)}
              </select>
              <ChevronDown />
            </label>
          </div>
        </header>
        {children}
      </section>
    </div>
  );
}
