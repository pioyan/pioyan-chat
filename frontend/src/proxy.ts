/** Next.js Proxy: JWT-based route protection. */
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login", "/signup"];
const TOKEN_KEY = "pioyan_chat_token";

export default function proxy(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;

  // 公開パスはそのまま通す
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Cookie でトークン確認 (Next.js proxy は localStorage にアクセスできない)
  const token = request.cookies.get(TOKEN_KEY)?.value;
  if (!token && pathname.startsWith("/chat")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api).*)"],
};
