# Frontend

Next.js App Router 应用。M1 已完成演示角色进入页、全局壳层、角色切换、通知与 Agent 入口，并将驾驶舱的决策队列、货盘健康度、活动准备度和覆盖矩阵接入真实 API。

```bash
npm install
npm run dev
```

浏览器通过 `NEXT_PUBLIC_API_URL` 读取 `/api/v1/dashboard` 与演示角色。界面包含加载、空数据、查询失败、后台刷新和数据更新时间状态。基础组件位于 `components/ui`。

质量门禁：`npm run lint && npm run typecheck && npm test && npm run build`。
