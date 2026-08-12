import { PackageOpen } from "lucide-react";
import { ReactNode } from "react";

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="state-panel">
      <PackageOpen aria-hidden="true" />
      <div><strong>{title}</strong><p>{description}</p></div>
      {action}
    </div>
  );
}
