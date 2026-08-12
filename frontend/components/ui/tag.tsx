import { HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

export function Tag({ className, children, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span className={cn("tag", className)} {...props}>
      <span className="tag__dot" aria-hidden="true" />
      {children}
    </span>
  );
}
