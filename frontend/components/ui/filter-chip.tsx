import { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

type FilterChipProps = ButtonHTMLAttributes<HTMLButtonElement> & { selected?: boolean };

export function FilterChip({ selected, className, ...props }: FilterChipProps) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      className={cn("filter-chip", selected && "filter-chip--selected", className)}
      {...props}
    />
  );
}
