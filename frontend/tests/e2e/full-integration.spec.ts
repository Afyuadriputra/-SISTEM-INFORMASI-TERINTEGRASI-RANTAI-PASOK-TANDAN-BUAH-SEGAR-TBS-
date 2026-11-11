import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, type Page, test } from '@playwright/test';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const AXE_PATH = path.resolve(__dirname, '../../node_modules/axe-core/axe.min.js');
const SCREENSHOT_DIR =
  process.env.PLAYWRIGHT_SCREENSHOT_DIR ||
  path.resolve(__dirname, '../../playwright-screenshots');

const LIVE_CONTRACT_ID = process.env.E2E_CONTRACT_ID ?? '71000000-0000-4000-8000-000000000001';
const LIVE_CONTRACT_MILL_ID = process.env.E2E_CONTRACT_MILL_ID ?? '41000000-0000-4000-8000-000000000001';
const PRIVATE_MILL_ID = process.env.E2E_PRIVATE_MILL_ID ?? '41000000-0000-4000-8000-000000000003';
const LIVE_PASSWORD = process.env.E2E_PASSWORD ?? 'UatSimulasi!2026';
const ACTOR_PREFIX = process.env.E2E_ACTOR_PREFIX ?? 'uat';
const ADMIN_USER = `${ACTOR_PREFIX}_sys_admin_01`;
const KOP_USER = `${ACTOR_PREFIX}_kop_op_01`;
const DIR_USER = `${ACTOR_PREFIX}_director_01`;

async function resolvePublicMillId(page: Page): Promise<string> {
  if (process.env.E2E_PUBLIC_MILL_ID) {
    return process.env.E2E_PUBLIC_MILL_ID;
  }
  const res = await page.request.get('/api/v1/public/mills');
  if (res.ok()) {
    const body = (await res.json()) as { data?: Array<{ id?: string }> };
    const firstId = body.data?.[0]?.id;
    if (firstId) {
      return firstId;
    }
  }
  return '41000000-0000-4000-8000-000000000001';
}

fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

async function assertNoHorizontalOverflow(page: Page, contextLabel: string) {
  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(
    overflow.scrollWidth,
    `${contextLabel}: scrollWidth (${overflow.scrollWidth}) > clientWidth (${overflow.clientWidth})`,
  ).toBeLessThanOrEqual(overflow.clientWidth + 1);
}

async function runAxeWcagAudit(page: Page, routeLabel: string) {
  await page.addScriptTag({ path: AXE_PATH });
  const results = await page.evaluate(async () => {
    const axe = (
      window as unknown as {
        axe: {
          run: (options?: unknown) => Promise<{
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
    `${routeLabel} WCAG 2.2 AA violations: ${JSON.stringify(
      blocking.map((b) => ({
        id: b.id,
        impact: b.impact,
        targets: b.nodes.map((n) => n.target),
      })),
    )}`,
  ).toEqual([]);
}

async function loginThroughUi(page: Page, username: string, password = LIVE_PASSWORD) {
  await page.goto('/login');
  await expect(page.getByLabel(/Username/i)).toBeVisible();
  await page.getByLabel(/Username/i).fill(username);
  await page.getByLabel(/^Kata Sandi/i).fill(password);
  await page.getByRole('button', { name: /Masuk ke Portal Internal/i }).click();
}

async function logoutThroughUi(page: Page) {
  const logoutBtn = page.getByRole('button', { name: /Keluar Sesi/i }).first();
  if (await logoutBtn.isVisible().catch(() => false)) {
    await logoutBtn.click();
  } else {
    // Open mobile nav drawer if viewport is narrow
    const menuBtn = page.getByRole('button', { name: /Buka menu/i });
    if (await menuBtn.isVisible().catch(() => false)) {
      await menuBtn.click();
    }
    await page.getByRole('button', { name: /Keluar Sesi/i }).first().click();
  }
  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByLabel(/Username/i)).toBeVisible({ timeout: 10_000 });
}

test.describe('F11 End-to-End Integration, Responsive & WCAG 2.2 AA Audit', () => {
  test('Public portal 7 routes render live API data cleanly across desktop & mobile with zero a11y/overflow defects', async ({
    page,
  }) => {
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    const mswRequests: string[] = [];

    page.on('pageerror', (err) => pageErrors.push(err.message));
    page.on('request', (req) => {
      if (req.url().includes('mockServiceWorker.js')) {
        mswRequests.push(req.url());
      }
    });
    page.on('response', (res) => {
      if (res.status() >= 500) {
        serverErrors.push(`${res.status()} ${res.url()}`);
      }
    });

    const publicMillId = await resolvePublicMillId(page);
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto('/');
    await expect(
      page.getByRole('heading', { name: /Transparansi Harga TBS Multi-PKS/i }),
    ).toBeVisible();
    await expect(page.getByText(/Rp 2\.950,00\/kg/i).first()).toBeVisible();
    await expect(page.getByText(/Rp 2\.890,00\/kg/i).first()).toBeVisible();
    await assertNoHorizontalOverflow(page, 'Home 1440px');
    await runAxeWcagAudit(page, 'Public Home 1440px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-public-home-desktop.png'),
      fullPage: true,
    });

    for (const route of [
      '/harga-tbs',
      `/pks/${publicMillId}`,
      '/lokasi-pks',
      '/tentang',
      '/kemitraan',
      '/kontak',
    ]) {
      await page.goto(route);
      await page.waitForLoadState('domcontentloaded');
      await expect(page.locator('#main-content, main').first()).toBeVisible({ timeout: 10_000 });
      await expect(page.getByText(/Memuat halaman\.\.\.|Sedang memuat|Memuat daftar/i)).toHaveCount(0, { timeout: 10_000 });
      await assertNoHorizontalOverflow(page, `${route} 1440px`);
    }

    // Tentang & Kontak clarify Listrik/Gas exclusion
    await page.goto('/tentang');
    await expect(page.getByText(/Listrik/i).first()).toBeVisible();

    // Unpublished private PKS returns safe 404 / error without leaking internal mill name
    await page.goto(`/pks/${PRIVATE_MILL_ID}`);
    await expect(page.getByText(/PKS Rahasia Internal UAT|PKS Mitra Internal Rahasia/i)).toHaveCount(0);

    // Mobile 375px responsive + axe audit
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await assertNoHorizontalOverflow(page, 'Home 375px');
    await runAxeWcagAudit(page, 'Public Home 375px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-public-home-mobile.png'),
      fullPage: true,
    });

    await page.goto('/harga-tbs');
    await assertNoHorizontalOverflow(page, '/harga-tbs 375px');
    await runAxeWcagAudit(page, 'Harga TBS 375px');

    expect(mswRequests).toEqual([]);
    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });

  test('Live FastAPI authentication, RBAC Non-Approver admin, rule versioning, receiving -> e-DO, and DIRECTOR dashboard', async ({
    page,
  }) => {
    test.setTimeout(90_000);
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];

    page.on('pageerror', (err) => pageErrors.push(err.message));
    page.on('response', (res) => {
      if (res.status() >= 500) {
        serverErrors.push(`${res.status()} ${res.url()}`);
      }
    });

    await page.setViewportSize({ width: 1440, height: 900 });

    // Anonymous guard redirect
    await page.goto('/app/admin');
    await expect(page).toHaveURL(/\/login\?next=%2Fapp%2Fadmin/);
    await runAxeWcagAudit(page, 'Login 1440px');

    // In real mode, simulation quick-login buttons must NOT render
    await expect(page.getByText(/Akses Cepat Simulasi/i)).toHaveCount(0);

    // Generic invalid password error
    await loginThroughUi(page, ADMIN_USER, 'WrongPass999!');
    await expect(page.getByRole('alert')).toContainText(/Username atau kata sandi tidak sesuai/i);

    // Real FastAPI login as SYSTEM_ADMIN
    await loginThroughUi(page, ADMIN_USER);
    await expect(page).toHaveURL(/\/app\/admin$/);
    await expect(
      page.getByRole('heading', { name: /Dashboard Administrasi Teknis & Kesehatan Sistem/i }),
    ).toBeVisible();
    await expect(page.getByText(/SEHAT \(UP\)/i)).toBeVisible();

    // Reload persists session cleanly via HttpOnly cookie + /api/v1/auth/me
    await page.reload();
    await expect(
      page.getByRole('heading', { name: /Dashboard Administrasi Teknis & Kesehatan Sistem/i }),
    ).toBeVisible();
    await assertNoHorizontalOverflow(page, 'Admin Dashboard 1440px');
    await runAxeWcagAudit(page, 'Admin Dashboard 1440px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-admin-dashboard-desktop.png'),
      fullPage: true,
    });

    // Admin Users & Rule Versioning
    await page.goto('/app/admin/pengguna');
    await expect(
      page.getByRole('heading', { name: /Manajemen Akun, Cakupan RBAC & Aturan Berversi/i }),
    ).toBeVisible();
    await expect(
      page.locator('#main-content').getByText(ADMIN_USER, { exact: true }),
    ).toBeVisible();

    // SYSTEM_ADMIN cannot issue CONFIRMED production policy (BR-SYS-002 -> 403/400 block)
    await page.getByLabel(/Klasifikasi Kebijakan/i).selectOption('CONFIRMED');
    await page.getByRole('button', { name: /Buat Versi Aturan Baru/i }).click();
    await expect(page.getByRole('alert').first()).toBeVisible();

    // SYSTEM_ADMIN creates append-only SIMULATION_ONLY rule version
    await page.getByLabel(/Klasifikasi Kebijakan/i).selectOption('SIMULATION_ONLY');
    await page.getByLabel(/Nilai Persentase/i).fill('1.6500');
    await page.getByRole('button', { name: /Buat Versi Aturan Baru/i }).click();
    await expect(page.getByText(/RECONCILIATION_WEIGHT_TOLERANCE v\d+ tercatat/i)).toBeVisible();

    // Cross-role route RBAC check
    await page.goto('/app/direksi');
    await expect(page.getByText(/AUTH_ACCESS_DENIED/i)).toBeVisible();
    await page.getByRole('link', { name: /Kembali ke Beranda Peran/i }).click();
    await expect(page).toHaveURL(/\/app\/admin$/);

    await logoutThroughUi(page);

    // Cooperative operator flow: Mobile receiving screen QA + create draft -> weigh -> validate -> e-DO
    await loginThroughUi(page, KOP_USER);
    await expect(page).toHaveURL(/\/app\/koperasi$/);

    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/app/koperasi/penerimaan');
    await expect(
      page.getByRole('heading', { name: /Pencatatan Penerimaan & Penimbangan TBS/i }),
    ).toBeVisible();
    await assertNoHorizontalOverflow(page, 'Koperasi Penerimaan 375px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-koperasi-receiving-mobile.png'),
      fullPage: true,
    });

    await page.setViewportSize({ width: 1440, height: 900 });
    await page.getByRole('button', { name: /Buat Draf Penerimaan/i }).click();
    await expect(page.getByText(/Penerimaan .* dibuat/i).first()).toBeVisible();

    // Select valid weights (Bruto 5000, Tara 800 -> Netto 4.200,000 kg)
    const grossInput = page.getByLabel(/Berat Bruto/i);
    const tareInput = page.getByLabel(/Berat Tara/i);
    await grossInput.fill('5000.000');
    await tareInput.fill('800.000');
    await expect(page.getByText(/4\.200,000 kg/i).first()).toBeVisible();
    await page.getByRole('button', { name: /Simpan Penimbangan/i }).click();
    await page.getByRole('button', { name: /Catat Grading Simulasi/i }).click();
    await page.getByRole('button', { name: /Validasi Penerimaan/i }).click();
    await expect(page.getByText(/VALIDATED|Tervalidasi/i).first()).toBeVisible();

    // Create e-DO from validated receipt against seeded active contract UUID
    await page.goto('/app/koperasi/surat-jalan');
    await expect(
      page.getByRole('heading', { name: /Penyusunan & Penerbitan e-DO Konsolidasi/i }),
    ).toBeVisible();
    const trmCheckbox = page
      .locator('label')
      .filter({ hasText: /Tervalidasi/i })
      .first()
      .locator('input[type="checkbox"]');
    await trmCheckbox.check();

    const millField = page.locator('#edo-mill');
    if ((await millField.locator(`option[value="${LIVE_CONTRACT_MILL_ID}"]`).count()) > 0) {
      await millField.selectOption(LIVE_CONTRACT_MILL_ID);
    }

    const contractField = page.getByLabel(/Referensi Kontrak Tujuan/i);
    const tagName = await contractField.evaluate((el) => el.tagName.toLowerCase());
    if (tagName === 'input') {
      await contractField.fill(LIVE_CONTRACT_ID);
    } else if ((await contractField.locator(`option[value="${LIVE_CONTRACT_ID}"]`).count()) > 0) {
      await contractField.selectOption(LIVE_CONTRACT_ID);
    }
    await page.getByRole('button', { name: /Susun Draf e-DO/i }).click();
    await expect(page.getByText(/Draf e-DO .* dibuat/i).first()).toBeVisible();
    await page.getByRole('button', { name: /Terbitkan e-DO/i }).first().click();
    await expect(page.getByText(/e-DO .* diterbitkan/i).first()).toBeVisible();

    await logoutThroughUi(page);

    // Director executive dashboard audit
    await loginThroughUi(page, DIR_USER);
    await expect(page).toHaveURL(/\/app\/direksi$/);
    await expect(
      page.getByRole('heading', { name: /Dashboard Eksekutif Direksi/i }),
    ).toBeVisible();
    await expect(
      page.getByText(/Kontribusi Kotor Niaga \(Data Simulasi - Bukan Laba Bersih\)/i),
    ).toBeVisible();
    await assertNoHorizontalOverflow(page, 'Director Dashboard 1440px');
    await runAxeWcagAudit(page, 'Director Dashboard 1440px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-director-dashboard-desktop.png'),
      fullPage: true,
    });

    await logoutThroughUi(page);

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });
});
