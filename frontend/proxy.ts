import { NextRequest, NextResponse } from "next/server";
import { getSessionCookie } from "better-auth/cookies";

export function proxy(request: NextRequest) {
  const isLoginPage = request.nextUrl.pathname === "/login";
  const isAuthRoute = request.nextUrl.pathname.startsWith("/api/auth");
  const isProxyRoute = request.nextUrl.pathname.startsWith("/api/proxy");

  // Allow auth API and proxy routes through
  if (isAuthRoute || isProxyRoute) return NextResponse.next();

  const sessionCookie = getSessionCookie(request);

  // Not logged in → redirect to login
  if (!sessionCookie && !isLoginPage) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Already logged in → redirect away from login
  if (sessionCookie && isLoginPage) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
