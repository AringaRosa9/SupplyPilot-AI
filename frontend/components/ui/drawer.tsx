"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { ReactNode } from "react";

export function Drawer({ trigger, title, children }: { trigger: ReactNode; title: string; children: ReactNode }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="drawer-overlay" />
        <Dialog.Content className="drawer-content">
          <div className="drawer-head">
            <div><span className="eyebrow">Intelligence</span><Dialog.Title>{title}</Dialog.Title></div>
            <Dialog.Close className="icon-button" aria-label="关闭"><X /></Dialog.Close>
          </div>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
