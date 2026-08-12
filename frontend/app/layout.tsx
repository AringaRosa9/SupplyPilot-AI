import type { Metadata } from "next";
import { ReactNode } from "react";

import { ToastProvider } from "@/components/ui/toast";
import "./globals.css";

export const metadata: Metadata = { title: "SupplyPilot AI", description: "供应链招商与货盘决策平台" };

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="zh-CN"><body><ToastProvider>{children}</ToastProvider></body></html>;
}
