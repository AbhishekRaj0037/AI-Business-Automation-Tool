// middleware.js
import { NextResponse } from "next/server";

const PUBLIC_ROUTES = ["/login", "/signup"];
const TOKEN_COOKIE = "jwt_token";

export function middleware(request) {
  const { pathname } = request.nextUrl;
  const isPublicRoute = PUBLIC_ROUTES.includes(pathname);
  const token = request.cookies.get(TOKEN_COOKIE)?.value;
  console.log("We are in middleware", token);
  // Has cookie + trying to access login/signup → redirect to home
  if (token && isPublicRoute) {
    return NextResponse.redirect(new URL("/home", request.url));
  }

  // No cookie + trying to access protected route → redirect to login
  if (!token && !isPublicRoute) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
