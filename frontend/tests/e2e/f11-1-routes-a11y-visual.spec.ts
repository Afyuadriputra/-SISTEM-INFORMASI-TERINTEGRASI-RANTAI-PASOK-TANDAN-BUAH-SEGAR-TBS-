import path from 'node:path';
import { expect, test } from '@playwright/test';
import {
  assertNoHorizontalOverflow,
  loginThroughUi,
  logoutThroughUi,
  runAxeWcagAudit,
  SCREENSHOT_DIR,
  UAT_IDS,
} from './uatHelpers';

const VIEWPORTS = [
  { name: 'desktop-1440', width: 1440, height: 900, isMobileNav: false },
  { name: 'laptop-1280', width: 1280, height: 720, isMobileNav: false },
  { name: 'tablet-768', width: 768, height: 1024, isMobileNav: true },
  { name: 'mobile-390', width: 390, height: 844, isMobileNav: true },
  { name: 'mobile-375', width: 375, height: 812, isMobileNav: true },
] as const;

interface RoleRouteGroup {
  readonly username: string | null;
  readonly routes: readonly string[];
}

const ALL_26_ROUTES_BY_ROLE: readonly RoleRouteGroup[] = [
  {
    username: null,
    routes: [
      '/',
      '/harga-tbs',
      `/pks/${UAT_IDS.millPub1}`,
      '/lokasi-pks',
      '/tentang',
      '/kemitraan',
      '/kontak',
      '/login',
    ],
  },
  {
    username: 'uat_petani_01',
    routes: ['/app/petani', '/app/petani/panen'],
  },
  {
    username: 'uat_kop_op_01',
    routes: ['/app/koperasi', '/app/koperasi/penerimaan', '/app/koperasi/surat-jalan'],
  },
  {
    username: 'uat_perumda_ops_01',
    routes: [
      '/app/perumda',
      '/app/perumda/harga',
      '/app/perumda/kontrak',
      '/app/perumda/logistik',
      '/app/perumda/rekonsiliasi',
      '/app/perumda/pembayaran',
    ],
  },
  {
    username: 'uat_mill_op_01',
    routes: ['/app/pks', '/app/pks/tiket-timbang'],
  },
  {
    username: 'uat_director_01',
    routes: ['/app/direksi', '/app/direksi/persetujuan'],
  },
  {
    username: 'uat_sys_admin_01',
    routes: ['/app/admin', '/app/admin/pengguna', '/app/admin/audit'],
  },
];

async function waitForRouteSettled(page: import('@playwright/test').Page, label = 'route') {
  await page.waitForLoadState('domcontentloaded');
  await expect(
    page.locator('#main-content, main').first(),
    `${label}: main content did not render (url=${page.url()})`,
  ).toBeVisible({ timeout: 15_000 });
  await expect(
    page.getByText(/Memuat halaman\.\.\.|Sedang memuat|Memuat daftar/i),
    `${label}: stuck loading`,
  ).toHaveCount(0, { timeout: 15_000 });
  await page.waitForTimeout(150);
}

test.describe('F11.1 All 26 Routes x 5 Viewports, Keyboard/Focus/Escape, Axe WCAG 2.2 AA & Visual Capture', () => {
  test('26 canonical routes across 5 viewports have zero horizontal overflow and proper responsive navigation highlight', async ({
    page,
  }) => {
    test.setTimeout(240_000);
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    for (const group of ALL_26_ROUTES_BY_ROLE) {
      if (group.username) {
        await page.setViewportSize({ width: 1440, height: 900 });
        await loginThroughUi(page, group.username);
      }

      for (const route of group.routes) {
        await page.setViewportSize({ width: VIEWPORTS[0].width, height: VIEWPORTS[0].height });
        await page.goto(route);
        await waitForRouteSettled(page, route);

        for (const vp of VIEWPORTS) {
          await page.setViewportSize({ width: vp.width, height: vp.height });
          await page.waitForTimeout(80);
          await assertNoHorizontalOverflow(page, `${route} @ ${vp.name}`);

          if (route.startsWith('/app/')) {
            if (vp.isMobileNav) {
              await expect(page.locator('#mobile-portal-menu-trigger')).toBeVisible();
            } else {
              const sidebar = page.getByRole('complementary', { name: /Navigasi Portal Internal/i });
              await expect(sidebar.locator('a[aria-current="page"]')).toHaveCount(1);
            }
          }
        }
      }

      if (group.username) {
        await page.setViewportSize({ width: 1440, height: 900 });
        await logoutThroughUi(page);
      }
    }

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });

  test('Keyboard navigation, Escape drawer/dialog focus restoration, Reduced Motion & Axe WCAG 2.2 AA priority audit + Screenshots', async ({
    page,
  }) => {
    test.setTimeout(240_000);
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    // 1. Reduced motion CSS honored
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto('/');
    await waitForRouteSettled(page);
    const transitionDuration = await page
      .getByRole('link', { name: /Masuk Portal Internal/i })
      .first()
      .evaluate((el) => getComputedStyle(el).transitionDuration);
    expect(['0s', '0.00001s', '1e-05s', '0.01ms']).toContain(transitionDuration);
    await page.emulateMedia({ reducedMotion: 'no-preference' });

    // 2. Public priority pages Axe + Mobile Escape focus restoration
    for (const pubRoute of ['/', '/harga-tbs', `/pks/${UAT_IDS.millPub1}`, '/login']) {
      await page.setViewportSize({ width: 1440, height: 900 });
      await page.goto(pubRoute);
      await waitForRouteSettled(page);
      await runAxeWcagAudit(page, `Public ${pubRoute} 1440px`);
    }

    // Mobile Public Navbar Escape focus restore + Login Mobile capture
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/');
    await waitForRouteSettled(page);
    const pubMenuBtn = page.getByRole('button', { name: /Buka menu navigasi/i });
    await pubMenuBtn.focus();
    await pubMenuBtn.click();
    await expect(page.locator('#public-mobile-drawer')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.locator('#public-mobile-drawer')).toBeHidden();
    await expect(pubMenuBtn).toBeFocused();

    await page.goto('/login');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, 'Login 375px');
    // Keyboard tab order through Login inputs, password toggle, & submit button
    await page.getByLabel(/Username/i).focus();
    await page.keyboard.press('Tab');
    await expect(page.getByLabel(/^Kata Sandi/i)).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: /Tampilkan kata sandi/i })).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: /Masuk ke Portal Internal/i })).toBeFocused();
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-mobile-login.png'),
      fullPage: true,
    });

    // 3. Farmer routes Axe + Mobile & Desktop screenshots
    await page.setViewportSize({ width: 1440, height: 900 });
    await loginThroughUi(page, 'uat_petani_01');
    for (const r of ['/app/petani', '/app/petani/panen']) {
      await page.goto(r);
      await waitForRouteSettled(page);
      await runAxeWcagAudit(page, `${r} 1440px`);
    }
    await page.goto('/app/petani');
    await waitForRouteSettled(page);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-desktop-petani.png'),
      fullPage: true,
    });

    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/app/petani');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/petani 375px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-mobile-petani.png'),
      fullPage: true,
    });

    // Test Internal Mobile Drawer Escape focus restore
    const internalMenuTrigger = page.locator('#mobile-portal-menu-trigger');
    await internalMenuTrigger.focus();
    await internalMenuTrigger.click();
    await expect(page.getByRole('dialog', { name: /Menu Portal Internal/i })).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog', { name: /Menu Portal Internal/i })).toBeHidden();
    await expect(internalMenuTrigger).toBeFocused();

    await page.goto('/app/petani/panen');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/petani/panen 375px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-mobile-petani-panen.png'),
      fullPage: true,
    });
    await page.setViewportSize({ width: 1440, height: 900 });
    await logoutThroughUi(page);

    // 4. Cooperative routes Axe + Mobile receiving capture
    await loginThroughUi(page, 'uat_kop_op_01');
    await page.goto('/app/koperasi');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/koperasi 1440px');
    await page.goto('/app/koperasi/penerimaan');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/koperasi/penerimaan 1440px');
    await page.setViewportSize({ width: 375, height: 812 });
    await waitForRouteSettled(page);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-mobile-koperasi-timbang.png'),
      fullPage: true,
    });
    await page.setViewportSize({ width: 1440, height: 900 });
    await logoutThroughUi(page);

    // 5. Mill operator weighing ticket Axe + Mobile capture
    await loginThroughUi(page, 'uat_mill_op_01');
    await page.goto('/app/pks/tiket-timbang');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/pks/tiket-timbang 1440px');
    await page.setViewportSize({ width: 375, height: 812 });
    await waitForRouteSettled(page);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-mobile-pks-tiket.png'),
      fullPage: true,
    });
    await page.setViewportSize({ width: 1440, height: 900 });
    await logoutThroughUi(page);

    // 6. Perumda OPS / Finance Axe + Desktop + Mobile captures
    await loginThroughUi(page, 'uat_perumda_ops_01');
    await page.goto('/app/perumda');
    await waitForRouteSettled(page);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-desktop-perumda.png'),
      fullPage: true,
    });
    await page.goto('/app/perumda/harga');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/perumda/harga 1440px');
    await page.goto('/app/perumda/rekonsiliasi');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/perumda/rekonsiliasi 1440px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-desktop-perumda-rekonsiliasi.png'),
      fullPage: true,
    });
    await page.setViewportSize({ width: 375, height: 812 });
    await waitForRouteSettled(page);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-mobile-ops-rekonsiliasi.png'),
      fullPage: true,
    });

    await page.setViewportSize({ width: 1440, height: 900 });
    await logoutThroughUi(page);

    // 6b. Perumda FINANCE full forms Axe + Desktop + Mobile captures
    await loginThroughUi(page, 'uat_perumda_fin_01');
    await page.goto('/app/perumda/pembayaran');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/perumda/pembayaran 1440px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-desktop-perumda-pembayaran.png'),
      fullPage: true,
    });
    await page.setViewportSize({ width: 375, height: 812 });
    await waitForRouteSettled(page);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-mobile-perumda-pembayaran.png'),
      fullPage: true,
    });
    await page.setViewportSize({ width: 1440, height: 900 });
    await logoutThroughUi(page);

    // 7. Director routes Axe + Desktop approvals capture
    await loginThroughUi(page, 'uat_director_01');
    await page.goto('/app/direksi');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/direksi 1440px');
    await page.goto('/app/direksi/persetujuan');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/direksi/persetujuan 1440px');
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'f11-1-desktop-direksi-persetujuan.png'),
      fullPage: true,
    });
    await logoutThroughUi(page);

    // 8. Admin /app/admin/pengguna Axe + ConfirmDialog Escape focus restore
    await loginThroughUi(page, 'uat_sys_admin_01');
    await page.goto('/app/admin/pengguna');
    await waitForRouteSettled(page);
    await runAxeWcagAudit(page, '/app/admin/pengguna 1440px');
    const disableBtn = page.locator('button:not([disabled])', { hasText: /^Nonaktifkan$/i }).first();
    await disableBtn.focus();
    await disableBtn.click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.locator('#confirm-dialog-reason')).toBeFocused();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).toBeHidden();
    await expect(disableBtn).toBeFocused();
    await logoutThroughUi(page);

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });
});
