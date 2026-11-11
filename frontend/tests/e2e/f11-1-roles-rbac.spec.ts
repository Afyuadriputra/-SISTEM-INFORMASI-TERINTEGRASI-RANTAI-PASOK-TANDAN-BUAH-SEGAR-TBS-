import { expect, test } from '@playwright/test';
import {
  browserApiCall,
  loginThroughUi,
  logoutThroughUi,
  UAT_IDS,
} from './uatHelpers';

interface RoleUatSpec {
  username: string;
  homePath: string;
  homeHeading: RegExp;
  expectedNavLinks: string[];
  forbiddenRoute: string;
  forbiddenApiChecks: Array<{
    label: string;
    path: string;
    method?: 'GET' | 'POST' | 'PATCH';
    body?: unknown;
    idempotencyKey?: string;
    expectedStatuses: number[];
  }>;
}

const SEVEN_ROLE_SPECS: RoleUatSpec[] = [
  {
    username: 'uat_petani_01',
    homePath: '/app/petani',
    homeHeading: /Portal Transparansi Petani/i,
    expectedNavLinks: ['Ringkasan Petani', 'Riwayat Panen & Bayar'],
    forbiddenRoute: '/app/perumda',
    forbiddenApiChecks: [
      { label: 'FARMER contracts.read denied', path: '/api/v1/contracts', expectedStatuses: [403] },
      { label: 'FARMER invoices.read denied', path: '/api/v1/invoices', expectedStatuses: [403] },
      {
        label: 'FARMER cross-farmer scope denied',
        path: `/api/v1/farmers/${UAT_IDS.farmer2}`,
        expectedStatuses: [403, 404],
      },
      {
        label: 'FARMER create farmer mutation denied',
        path: '/api/v1/farmers',
        method: 'POST',
        body: { farmer_code: 'UNAUTHORIZED-01', full_name: 'Bad Actor' },
        expectedStatuses: [403],
      },
    ],
  },
  {
    username: 'uat_kop_op_01',
    homePath: '/app/koperasi',
    homeHeading: /Dashboard & Master Data Koperasi/i,
    expectedNavLinks: ['Beranda & Master Data', 'Penerimaan & Timbang TBS', 'Surat Jalan e-DO'],
    forbiddenRoute: '/app/perumda/kontrak',
    forbiddenApiChecks: [
      { label: 'COOP contracts.read denied', path: '/api/v1/contracts', expectedStatuses: [403] },
      { label: 'COOP finance report denied', path: '/api/v1/reports/finance', expectedStatuses: [403] },
      {
        label: 'COOP pricing create denied',
        path: '/api/v1/prices',
        method: 'POST',
        body: {},
        expectedStatuses: [403],
      },
    ],
  },
  {
    username: 'uat_perumda_ops_01',
    homePath: '/app/perumda',
    homeHeading: /Dashboard Operasional & Master Data PKS/i,
    expectedNavLinks: [
      'Dashboard & Master PKS',
      'Manajemen Harga PKS',
      'Kontrak & Kuota PKS',
      'Monitoring Logistik e-DO',
      'Rekonsiliasi & Sengketa',
      'Faktur & Pembayaran',
    ],
    forbiddenRoute: '/app/admin',
    forbiddenApiChecks: [
      { label: 'OPS reports.finance denied', path: '/api/v1/reports/finance', expectedStatuses: [403] },
      { label: 'OPS admin.users denied', path: '/api/v1/admin/users', expectedStatuses: [403] },
      {
        label: 'OPS invoice create denied',
        path: '/api/v1/invoices',
        method: 'POST',
        body: {},
        expectedStatuses: [403],
      },
      {
        label: 'OPS contract approve denied',
        path: `/api/v1/contracts/${UAT_IDS.contractPri}/approve`,
        method: 'POST',
        expectedStatuses: [403],
      },
    ],
  },
  {
    username: 'uat_perumda_fin_01',
    homePath: '/app/perumda/pembayaran',
    homeHeading: /Manajemen Faktur & Pencatatan Pembayaran Manual Terverifikasi/i,
    expectedNavLinks: ['Faktur & Pembayaran', 'Rekonsiliasi Terkait', 'Kontrak & Kuota', 'Ringkasan Operasional'],
    forbiddenRoute: '/app/direksi',
    forbiddenApiChecks: [
      { label: 'FIN admin.users denied', path: '/api/v1/admin/users', expectedStatuses: [403] },
      {
        label: 'FIN price create denied',
        path: '/api/v1/prices',
        method: 'POST',
        body: {},
        expectedStatuses: [403],
      },
      {
        label: 'FIN director payment approve denied',
        path: `/api/v1/payments/${UAT_IDS.contractPri}/approve`,
        method: 'POST',
        body: { decision: 'APPROVED', reason: 'Unauthorized' },
        idempotencyKey: 'fin-unauth-approve-001',
        expectedStatuses: [403],
      },
    ],
  },
  {
    username: 'uat_mill_op_01',
    homePath: '/app/pks',
    homeHeading: /Dashboard & Verifikasi Kedatangan TBS PKS/i,
    expectedNavLinks: ['Verifikasi Kedatangan e-DO', 'Tiket Timbang & Grading'],
    forbiddenRoute: '/app/perumda/harga',
    forbiddenApiChecks: [
      { label: 'MILL contracts denied', path: '/api/v1/contracts', expectedStatuses: [403] },
      { label: 'MILL invoices denied', path: '/api/v1/invoices', expectedStatuses: [403] },
      {
        label: 'MILL receipt draft denied',
        path: '/api/v1/receipts',
        method: 'POST',
        body: {},
        idempotencyKey: 'mill-unauth-rcp-001',
        expectedStatuses: [403],
      },
    ],
  },
  {
    username: 'uat_director_01',
    homePath: '/app/direksi',
    homeHeading: /Dashboard Eksekutif Direksi/i,
    expectedNavLinks: ['Dashboard Eksekutif', 'Pusat Persetujuan', 'Audit Trail'],
    forbiddenRoute: '/app/admin/pengguna',
    forbiddenApiChecks: [
      { label: 'DIR admin.users denied', path: '/api/v1/admin/users', expectedStatuses: [403] },
      { label: 'DIR system-health denied', path: '/api/v1/admin/system-health', expectedStatuses: [403] },
      {
        label: 'DIR invoice create denied (Maker!=Approver)',
        path: '/api/v1/invoices',
        method: 'POST',
        body: {},
        expectedStatuses: [403],
      },
    ],
  },
  {
    username: 'uat_sys_admin_01',
    homePath: '/app/admin',
    homeHeading: /Dashboard Administrasi Teknis & Kesehatan Sistem/i,
    expectedNavLinks: ['Kesehatan Sistem', 'Pengguna & Aturan Versi', 'Audit & CCTV Digital'],
    forbiddenRoute: '/app/direksi/persetujuan',
    forbiddenApiChecks: [
      { label: 'ADMIN contracts denied (BR-SYS-002)', path: '/api/v1/contracts', expectedStatuses: [403] },
      { label: 'ADMIN invoices denied (BR-SYS-002)', path: '/api/v1/invoices', expectedStatuses: [403] },
      { label: 'ADMIN finance report denied', path: '/api/v1/reports/finance', expectedStatuses: [403] },
      {
        label: 'ADMIN CONFIRMED rule denied (BR-SYS-002)',
        path: '/api/v1/admin/rule-versions',
        method: 'POST',
        body: {
          rule_code: 'RECONCILIATION_WEIGHT_TOLERANCE',
          effective_from: new Date().toISOString(),
          rule_config: { tolerance_percent: '1.0000' },
          policy_classification: 'CONFIRMED',
        },
        expectedStatuses: [403],
      },
    ],
  },
];

test.describe('F11.1 Seven-Role Auth, RBAC, Session Persistence & Expiry Matrix (Real FastAPI)', () => {
  test('All 7 roles enforce login, cookie reload persistence, permission-aware sidebar, forbidden routes, live 403 API checks, and session purge on logout/expiry', async ({
    page,
    context,
  }) => {
    test.setTimeout(180_000);

    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    const mswRequests: string[] = [];

    page.on('pageerror', (err) => pageErrors.push(err.message));
    page.on('request', (req) => {
      if (req.url().includes('mockServiceWorker.js')) mswRequests.push(req.url());
    });
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    await page.setViewportSize({ width: 1440, height: 900 });

    for (const spec of SEVEN_ROLE_SPECS) {
      await loginThroughUi(page, spec.username);
      await expect(page).toHaveURL(new RegExp(`${spec.homePath}$`), { timeout: 10_000 });
      await expect(page.getByRole('heading', { name: spec.homeHeading })).toBeVisible();
      await expect(page.getByText(/LIVE FASTAPI/i)).toBeVisible();

      // Reload persists HttpOnly session cleanly
      await page.reload();
      await expect(page.getByRole('heading', { name: spec.homeHeading })).toBeVisible();

      // Permission-aware sidebar links match role specification
      const sidebar = page.getByRole('complementary', { name: /Navigasi Portal Internal/i });
      for (const linkText of spec.expectedNavLinks) {
        await expect(sidebar.getByRole('link', { name: linkText })).toBeVisible();
      }
      if (spec.username === 'uat_sys_admin_01') {
        await expect(sidebar.getByText(/Non-Approver \(BR-SYS-002\)/i)).toBeVisible();
      }

      // Direct backend 403 / cross-scope / unauthorized mutation verification
      for (const check of spec.forbiddenApiChecks) {
        const res = await browserApiCall(page, check);
        expect(
          check.expectedStatuses,
          `${spec.username} -> ${check.label}: got HTTP ${res.status}`,
        ).toContain(res.status);
      }

      // Forbidden frontend route renders 403 view & cleanly returns home
      await page.goto(spec.forbiddenRoute);
      await expect(page.getByText(/AUTH_ACCESS_DENIED/i)).toBeVisible();
      await page.getByRole('link', { name: /Kembali ke Beranda Peran/i }).click();
      await expect(page).toHaveURL(new RegExp(`${spec.homePath}$`));

      // Logout clears HttpOnly cookie & query cache
      await logoutThroughUi(page);
      const afterLogoutMe = await browserApiCall(page, { path: '/api/v1/auth/me' });
      expect(afterLogoutMe.status).toBe(401);
    }

    // Session expiry behavior: clear cookie mid-session & trigger navigation -> clean redirect + expiry handling
    await loginThroughUi(page, 'uat_perumda_ops_01');
    await expect(page).toHaveURL(/\/app\/perumda$/);
    await context.clearCookies();
    await page.reload();
    await expect(page).toHaveURL(/\/login\?next=%2Fapp%2Fperumda/);

    expect(mswRequests).toEqual([]);
    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });
});
