import { CircleAlert } from "lucide-react";
import { ReactNode } from "react";

export function ErrorState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="state-panel state-panel--error" role="alert">
      <CircleAlert aria-hidden="true" />
      <div><strong>{title}</strong><p>{description}</p></div>
      {action}
    </div>
  );
}
