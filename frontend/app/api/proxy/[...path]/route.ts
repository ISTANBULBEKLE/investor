import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

async function proxyRequest(req: NextRequest) {
  const path = req.nextUrl.pathname.replace("/api/proxy", "");
  const url = `${BACKEND_URL}${path}${req.nextUrl.search}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  const init: RequestInit = {
    method: req.method,
    headers,
  };

  if (req.method !== "GET" && req.method !== "HEAD") {
    init.body = await req.text();
  }

  try {
    const resp = await fetch(url, init);
    const data = await resp.text();

    return new Response(data, {
      status: resp.status,
      headers: {
        "Content-Type": resp.headers.get("Content-Type") || "application/json",
      },
    });
  } catch (error) {
    console.error(`Proxy error for ${path}:`, (error as Error).message);
    return new Response(
      JSON.stringify({ detail: "Backend unavailable", path }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    );
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const DELETE = proxyRequest;
export const PATCH = proxyRequest;
