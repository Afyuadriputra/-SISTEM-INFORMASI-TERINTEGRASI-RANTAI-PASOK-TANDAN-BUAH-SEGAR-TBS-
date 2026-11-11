import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, type Page } from '@playwright/test';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const AXE_PATH = path.resolve(__dirname, '../../node_modules/axe-core/axe.min.js');
export const SCREENSHOT_DIR =
  process.env.PLAYWRIGHT_SCREENSHOT_DIR ||
  path.resolve(__dirname, '../../playwright-screenshots');

fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

export const UAT_PASSWORD = process.env.E2E_PASSWORD ?? 'UatSimulasi!2026';

export const UAT_IDS = {
  farmer1: '61100000-0000-4000-8000-000000000001',
  farmer2: '61100000-0000-4000-8000-000000000002',
  coop1: '61000000-0000-4000-8000-000000000001',
  millPub1: '41000000-0000-4000-8000-000000000001',
  millPub2: '41000000-0000-4000-8000-000000000002',
  millPriv: '41000000-0000-4000-8000-000000000003',
  contractPri: '71000000-0000-4000-8000-000000000001',
  contractUnconf: '71000000-0000-4000-8000-000000000002',
  receiptDispute: '81000000-0000-4000-8000-000000000002',
  receiptUnconf: '81000000-0000-4000-8000-000000000003',
} as const;

export const TINY_PNG_BUFFER = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=',
  'base64',
);

export async function loginThroughUi(
  page: Page,
  username: string,
  password = UAT_PASSWORD,
  expectSuccessRedirect = true,
) {
  const alreadyAtLogin =
    page.url().includes('/login') &&
    (await page.getByLabel(/Username/i).isVisible().catch(() => false));
  if (!alreadyAtLogin) {
    await page.goto('/login');
  }
  await expect(page.getByLabel(/Username/i)).toBeVisible({ timeout: 10_000 });
  await page.getByLabel(/Username/i).fill(username);
  await page.getByLabel(/^Kata Sandi/i).fill(password);
  await page.getByRole('button', { name: /Masuk ke Portal Internal/i }).click();
  if (expectSuccessRedirect) {
    await expect(page).toHaveURL(/\/app\//, { timeout: 15_000 });
  }
}

export async function logoutThroughUi(page: Page) {
  const logoutBtn = page.getByRole('button', { name: /Keluar Sesi/i }).first();
  if (!(await logoutBtn.isVisible().catch(() => false))) {
    const homeBack = page.getByRole('link', { name: /Kembali ke Beranda Peran/i });
    if (await homeBack.isVisible().catch(() => false)) {
      await homeBack.click();
    } else {
      const menuBtn = page.getByRole('button', { name: /Buka menu/i });
      if (await menuBtn.isVisible().catch(() => false)) {
        await menuBtn.click();
      }
    }
  }
  await expect(logoutBtn).toBeVisible({ timeout: 8000 });
  await logoutBtn.click();
  await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  await expect(page.getByLabel(/Username/i)).toBeVisible({ timeout: 10_000 });
}

export async function assertNoHorizontalOverflow(page: Page, label: string) {
  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(
    overflow.scrollWidth,
    `${label}: scrollWidth (${overflow.scrollWidth}) > clientWidth (${overflow.clientWidth})`,
  ).toBeLessThanOrEqual(overflow.clientWidth + 1);
}

export async function runAxeWcagAudit(page: Page, label: string) {
  await page.addScriptTag({ path: AXE_PATH });
  const results = await page.evaluate(async () => {
    const axe = (
      window as unknown as {
        axe: {
          run: (opts?: unknown) => Promise<{
            violations: Array<{
              id: string;
              impact?: string | null;
              description: string;
              nodes: Array<{ target: string[] }>;
            }>;
          }>;
        };
      }
    ).axe;
    return await axe.run({
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'],
      },
    });
  });

  const blocking = results.violations.filter(
    (v) => v.impact === 'critical' || v.impact === 'serious',
  );
  expect(
    blocking,
    `${label} WCAG 2.2 AA violations: ${JSON.stringify(
      blocking.map((b) => ({
        id: b.id,
        impact: b.impact,
        targets: b.nodes.map((n) => n.target),
      })),
    )}`,
  ).toEqual([]);
}

/**
 * Call real FastAPI endpoint from inside the browser context using its active HttpOnly session & CSRF token.
 */
export async function browserApiCall(
  page: Page,
  options: {
    path: string;
    method?: 'GET' | 'POST' | 'PATCH';
    body?: unknown;
    idempotencyKey?: string;
  },
): Promise<{ status: number; json: Record<string, unknown> }> {
  return page.evaluate(async (opts) => {
    const method = opts.method ?? 'GET';
    const headers: Record<string, string> = {};
    if (opts.body !== undefined) {
      headers['Content-Type'] = 'application/json';
    }
    if (opts.idempotencyKey) {
      headers['Idempotency-Key'] = opts.idempotencyKey;
    }
    if (method !== 'GET') {
      const csrfRes = await fetch('/api/v1/auth/csrf', { credentials: 'include' });
      const csrfJson = (await csrfRes.json()) as { data?: { csrf_token?: string } };
      if (csrfJson.data?.csrf_token) {
        headers['X-CSRF-Token'] = csrfJson.data.csrf_token;
      }
    }
    const res = await fetch(opts.path, {
      method,
      credentials: 'include',
      headers,
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    });
    const json = (await res.json().catch(() => ({}))) as Record<string, unknown>;
    return { status: res.status, json };
  }, options);
}
