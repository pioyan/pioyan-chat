/**
 * DM（ダイレクトメッセージ）機能の E2E 検証
 *
 * 検証項目:
 * 1. AppNavBar が画面左端に表示される
 * 2. DM アイコンをクリックするとサイドバーが DM セクションに切り替わる
 * 3. チャンネルアイコンをクリックするとサイドバーがチャンネルセクションに戻る
 * 4. DM を開いてメッセージを送信できる
 */

import { test, expect, type Page } from "@playwright/test";

const API_BASE = "http://localhost:8000";
const TOKEN_KEY = "pioyan_chat_token";

// ── ヘルパー ──────────────────────────────────────────────────

function uniqueUser(suffix: string) {
  const ts = Date.now();
  return {
    username: `e2e_${suffix}_${ts}`,
    email: `e2e${suffix}${ts}@example.com`,
    password: "e2eTest123!",
  };
}

async function apiPost<T>(
  path: string,
  body: unknown,
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`POST ${path} failed ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

async function apiGet<T>(path: string, token: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`GET ${path} failed ${res.status}`);
  return res.json() as Promise<T>;
}

async function signupAndGetToken(user: {
  username: string;
  email: string;
  password: string;
}): Promise<string> {
  const data = await apiPost<{ access_token: string }>(
    "/api/auth/signup",
    user,
  );
  return data.access_token;
}

async function getMe(token: string): Promise<{ id: string; username: string }> {
  return apiGet<{ id: string; username: string }>("/api/auth/me", token);
}

/** DM チャンネルを作成し、チャンネル名を返す */
async function createDm(
  token: string,
  targetUserId: string,
): Promise<{ id: string; name: string }> {
  return apiPost<{ id: string; name: string }>(
    "/api/dm",
    { user_id: targetUserId },
    token,
  );
}

/** cookie + localStorage に JWT をセットして /chat に遷移 */
async function loginToPage(page: Page, token: string) {
  await page.context().addCookies([
    {
      name: TOKEN_KEY,
      value: token,
      domain: "localhost",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
      sameSite: "Lax",
    },
  ]);
  await page.goto("/chat");
  await page.evaluate(
    ([key, t]) => localStorage.setItem(key, t),
    [TOKEN_KEY, token],
  );
  // API レスポンスを待つ（チャンネル一覧が揃うまで）
  await page.waitForTimeout(2500);
}

/** AppNavBar のボタンをクリック（nav 内を正確にスコープ） */
function clickNavButton(page: Page, label: string) {
  return page.locator("nav").first().getByRole("button", { name: label, exact: true }).click();
}

/** サイドバーの h2 見出し locator */
function sidebarHeading(page: Page) {
  return page.locator("aside").first().locator("h2").first();
}

// ── テスト ────────────────────────────────────────────────────

test.describe("AppNavBar", () => {
  test("画面左端に AppNavBar が表示される", async ({ page }) => {
    const user = uniqueUser("nav");
    const token = await signupAndGetToken(user);
    await loginToPage(page, token);

    await expect(page).toHaveURL(/\/chat/);
    // 最左の nav 要素が存在する
    await expect(page.locator("nav").first()).toBeVisible({ timeout: 8000 });
  });

  test("チャンネル・DM・検索・設定ボタンが表示される", async ({ page }) => {
    const user = uniqueUser("navicons");
    const token = await signupAndGetToken(user);
    await loginToPage(page, token);
    await expect(page).toHaveURL(/\/chat/);

    // AppNavBar 内のボタンを正確に特定
    const nav = page.locator("nav").first();
    await expect(
      nav.getByRole("button", { name: "チャンネル", exact: true }),
    ).toBeVisible({ timeout: 8000 });
    await expect(
      nav.getByRole("button", { name: "ダイレクトメッセージ", exact: true }),
    ).toBeVisible();
    await expect(
      nav.getByRole("button", { name: "検索", exact: true }),
    ).toBeVisible();
    await expect(
      nav.getByRole("button", { name: "設定・プロフィール", exact: true }),
    ).toBeVisible();
  });
});

test.describe("DM セクション切り替え", () => {
  test("DM アイコンクリックでサイドバーが DM セクションに切り替わる", async ({
    page,
  }) => {
    const user = uniqueUser("dmsec");
    const token = await signupAndGetToken(user);
    await loginToPage(page, token);
    await expect(page).toHaveURL(/\/chat/);

    // 初期状態: サイドバー見出しが「チャンネル」
    await expect(sidebarHeading(page)).toHaveText("チャンネル", {
      timeout: 8000,
    });

    // DM ボタンをクリック
    await clickNavButton(page, "ダイレクトメッセージ");

    // サイドバー見出しが「ダイレクトメッセージ」に切り替わる
    await expect(sidebarHeading(page)).toHaveText("ダイレクトメッセージ", {
      timeout: 5000,
    });
  });

  test("チャンネルアイコンクリックでチャンネルセクションに戻る", async ({
    page,
  }) => {
    const user = uniqueUser("chback");
    const token = await signupAndGetToken(user);
    await loginToPage(page, token);
    await expect(page).toHaveURL(/\/chat/);

    // DM に切り替えてから戻す
    await clickNavButton(page, "ダイレクトメッセージ");
    await expect(sidebarHeading(page)).toHaveText("ダイレクトメッセージ", {
      timeout: 5000,
    });

    await clickNavButton(page, "チャンネル");
    await expect(sidebarHeading(page)).toHaveText("チャンネル", {
      timeout: 5000,
    });
  });
});

test.describe("DM 会話", () => {
  test("DM リストに作成した DM が表示される", async ({ page }) => {
    const user1 = uniqueUser("u1");
    const user2 = uniqueUser("u2");

    const token1 = await signupAndGetToken(user1);
    const token2 = await signupAndGetToken(user2);
    const me2 = await getMe(token2);

    // DM 作成
    const dm = await createDm(token1, me2.id);

    await loginToPage(page, token1);
    await expect(page).toHaveURL(/\/chat/);

    // DM セクションに切り替え
    await clickNavButton(page, "ダイレクトメッセージ");
    await expect(sidebarHeading(page)).toHaveText("ダイレクトメッセージ", {
      timeout: 5000,
    });

    // 作成した DM のチャンネル名がリストに表示される
    const dmItem = page.locator("aside").first().getByText(dm.name, { exact: true });
    await expect(dmItem).toBeVisible({ timeout: 8000 });
  });

  test("DM を開いてメッセージを送信できる", async ({ page }) => {
    const user1 = uniqueUser("sender");
    const user2 = uniqueUser("recvr");
    const testMessage = `E2E テスト @ ${Date.now()}`;

    const token1 = await signupAndGetToken(user1);
    const token2 = await signupAndGetToken(user2);
    const me2 = await getMe(token2);

    const dm = await createDm(token1, me2.id);

    await loginToPage(page, token1);
    await expect(page).toHaveURL(/\/chat/);

    // DM セクションに切り替えて DM をクリック
    await clickNavButton(page, "ダイレクトメッセージ");
    await expect(sidebarHeading(page)).toHaveText("ダイレクトメッセージ", {
      timeout: 5000,
    });

    // DM アイテムをクリック
    const dmItem = page.locator("aside").first().getByText(dm.name, { exact: true });
    await expect(dmItem).toBeVisible({ timeout: 8000 });
    await dmItem.click();

    // メッセージ入力欄を取得して送信
    const input = page.locator("textarea").last();
    await expect(input).toBeVisible({ timeout: 5000 });
    await input.fill(testMessage);
    await input.press("Enter");

    // 送信したメッセージが表示される
    await expect(page.getByText(testMessage)).toBeVisible({ timeout: 8000 });
  });
});
