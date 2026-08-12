"use client";

import * as ToastPrimitive from "@radix-ui/react-toast";
import { ReactNode } from "react";

export function ToastProvider({ children }: { children: ReactNode }) {
  return <ToastPrimitive.Provider swipeDirection="right">{children}<ToastPrimitive.Viewport className="toast-viewport" /></ToastPrimitive.Provider>;
}

export function Toast({ open, onOpenChange, title, description }: { open: boolean; onOpenChange: (open: boolean) => void; title: string; description?: string }) {
  return <ToastPrimitive.Root open={open} onOpenChange={onOpenChange} className="toast"><ToastPrimitive.Title>{title}</ToastPrimitive.Title>{description && <ToastPrimitive.Description>{description}</ToastPrimitive.Description>}</ToastPrimitive.Root>;
}
