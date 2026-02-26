/** JWT token management using localStorage + cookie (for middleware). */

const TOKEN_KEY = "pioyan_chat_token";
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7; // 7 days

export function saveToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  // proxy.ts (Next.js middleware) reads from cookies, so keep them in sync.
  document.cookie = `${TOKEN_KEY}=${token}; path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax`;
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  document.cookie = `${TOKEN_KEY}=; path=/; max-age=0`;
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}
