# Frontend

Next.js App Router 应用。M0 将确认版 HTML 原型拆成导航、顶部上下文栏、页面容器和基于 Radix Dialog 的 Intelligence Rail，并建立语义 token 与基础组件。

```bash
npm install
npm run dev
```

服务端通过 `API_INTERNAL_URL` 读取 `/api/v1/health`。基础组件位于 `components/ui`：Button、Tag、FilterChip、DataTable、EmptyState、ErrorState、Drawer、Toast。

质量门禁：`npm run lint && npm run typecheck && npm test && npm run build`。
