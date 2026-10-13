// Per-IP and per-day counters for the site's AI endpoints. Upstash Redis REST
// (UPSTASH_REDIS_REST_URL/_TOKEN or Vercel KV's KV_REST_API_URL/_TOKEN) when set,
// so limits hold across instances; in-memory per instance otherwise.
// Marketplace stores may add a custom prefix (e.g. MYSTORE_KV_REST_API_URL), so match by suffix.
function envBySuffix(...suffixes: string[]): string | undefined {
  for (const suffix of suffixes) {
    const key = Object.keys(process.env).find((k) => k === suffix || k.endsWith(`_${suffix}`));
    if (key && process.env[key]) return process.env[key];
  }
  return undefined;
}
const redisUrl = envBySuffix("UPSTASH_REDIS_REST_URL", "KV_REST_API_URL");
const redisToken = envBySuffix("UPSTASH_REDIS_REST_TOKEN", "KV_REST_API_TOKEN");
const STORE = redisUrl && redisToken ? "redis" : "memory";
const memory = new Map<string, { n: number; reset: number }>();

/** Runs Redis commands through the Upstash REST pipeline; null when no store is configured or it fails. */
export async function redis(commands: (string | number)[][]): Promise<{ result?: unknown; error?: string }[] | null> {
  if (!redisUrl || !redisToken) return null;
  try {
    const res = await fetch(`${redisUrl}/pipeline`, {
      method: "POST",
      headers: { Authorization: `Bearer ${redisToken}`, "Content-Type": "application/json" },
      body: JSON.stringify(commands.map((c) => c.map(String))),
    });
    return res.ok ? ((await res.json()) as { result?: unknown; error?: string }[]) : null;
  } catch {
    return null;
  }
}

export async function hit(key: string, windowS: number): Promise<number> {
  if (redisUrl && redisToken) {
    const res = await fetch(`${redisUrl}/pipeline`, {
      method: "POST",
      headers: { Authorization: `Bearer ${redisToken}`, "Content-Type": "application/json" },
      body: JSON.stringify([
        ["INCR", key],
        ["EXPIRE", key, String(windowS), "NX"],
      ]),
    });
    if (res.ok) {
      const out = (await res.json()) as { result: number }[];
      return Number(out[0]?.result || 0);
    }
  }
  const now = Date.now();
  const cur = memory.get(key);
  if (!cur || cur.reset < now) {
    memory.set(key, { n: 1, reset: now + windowS * 1000 });
    return 1;
  }
  cur.n += 1;
  return cur.n;
}

export function clientIp(request: Request): string {
  return (
    request.headers.get("x-real-ip") ||
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    "unknown"
  );
}

export const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store", "X-Limit-Store": STORE },
  });
