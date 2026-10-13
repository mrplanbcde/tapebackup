// Keeps the last questions asked to the site's AI tools in Upstash Redis, newest
// first, so the owner can read them at /api/history. Visitors are stored as a
// short salted hash of their IP plus Vercel's country/city, never the raw IP.
import { createHash } from "node:crypto";
import { clientIp, redis } from "./limit.js";

export const HISTORY_KEEP = 5000;
export type HistoryKind = "chat" | "topology" | "backup" | "info2soft";

export async function record(kind: HistoryKind, request: Request, data: Record<string, unknown>) {
  const salt = process.env.HISTORY_SALT || "mrplanb-history";
  const city = request.headers.get("x-vercel-ip-city");
  const entry = {
    t: new Date().toISOString(),
    visitor: createHash("sha256").update(`${salt}:${clientIp(request)}`).digest("hex").slice(0, 10),
    country: request.headers.get("x-vercel-ip-country") || "",
    city: city ? decodeURIComponent(city) : "",
    page: request.headers.get("referer") || "",
    ...data,
  };
  await redis([
    ["LPUSH", `history:${kind}`, JSON.stringify(entry)],
    ["LTRIM", `history:${kind}`, 0, HISTORY_KEEP - 1],
  ]);
}
