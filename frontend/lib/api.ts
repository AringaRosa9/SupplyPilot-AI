export type ApiHealth = {
  status: "ok" | "degraded";
  service: string;
  version: string;
  checks: Record<string, string>;
};

export type DemoRoleId = "marketing_ops" | "sourcing_manager" | "product_ops" | "executive";

export type DemoRole = {
  id: DemoRoleId;
  name: string;
  title: string;
  description: string;
  initials: string;
  capabilities: string[];
};

export type DashboardData = {
  campaign: {
    id: string;
    name: string;
    status: string;
    target_markets: string[];
    product_lines: string[];
    sourcing_deadline: string;
  };
  role: DemoRole;
  decision_queue: Array<{
    id: string;
    severity: "P0" | "P1" | "P2";
    type: string;
    title: string;
    facts: Record<string, string | number>;
    action: string | null;
  }>;
  health: {
    score: number;
    weekly_change: number;
    dimensions: Array<{ name: string; score: number; change: number }>;
    methodology: string;
  };
  readiness: Record<"target" | "submitted" | "validated" | "high_grade" | "listed" | "pending_review", number>;
  coverage: Array<{
    market: string;
    product_line: "hotel" | "flight";
    scope: string;
    audience: string | null;
    current_products: number;
    target_products: number;
    current_inventory: number;
    target_inventory: number;
    coverage_rate: number;
  }>;
  updated_at: string;
  permissions: Record<"create_campaign" | "create_task" | "review_product" | "read_only", boolean>;
};

const publicBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiRequest<T>(path: string): Promise<T> {
  const response = await fetch(`${publicBaseUrl}/api/v1${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`API request failed: ${response.status}`);
  return (await response.json()) as T;
}

export function getDemoRoles(): Promise<DemoRole[]> {
  return apiRequest<DemoRole[]>("/demo/roles");
}

export function getDashboard(role: DemoRoleId): Promise<DashboardData> {
  return apiRequest<DashboardData>(`/dashboard?role=${encodeURIComponent(role)}`);
}

export async function getApiHealth(): Promise<ApiHealth> {
  const baseUrl = process.env.API_INTERNAL_URL ?? "http://localhost:8000";
  const response = await fetch(`${baseUrl}/api/v1/health`, {
    cache: "no-store",
    signal: AbortSignal.timeout(2500),
  });
  const payload = (await response.json()) as ApiHealth;
  if (!response.ok) throw new Error(payload.status);
  return payload;
}
