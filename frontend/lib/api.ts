export type ApiHealth = {
  status: "ok" | "degraded";
  service: string;
  version: string;
  checks: Record<string, string>;
};

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
