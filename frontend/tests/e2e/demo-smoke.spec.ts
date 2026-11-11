import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from '@playwright/test';
import { browserApiCall, loginThroughUi, logoutThroughUi } from './uatHelpers';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const CREDENTIALS_FILE = path.resolve(
  __dirname,
  '../../../backend/.demo-credentials.local.txt',
);

function loadDemoPassword(): string {
  if (!fs.existsSync(CREDENTIALS_FILE)) {
    throw new Error(
      `File kredensial demo tidak ditemukan di ${CREDENTIALS_FILE}. Jalankan .\\scripts\\demo-setup.ps1 terlebih dahulu.`,
    );
  }
  const text = fs.readFileSync(CREDENTIALS_FILE, 'utf-8');
  const match = text.match(/Password Bersama Semua Akun Demo \(Argon2id\):\s*(\S+)/);
  if (!match?.[1]) {
    throw new Error(`Password demo tidak ditemukan di ${CREDENTIALS_FILE}.`);
  }
  return match[1];
}

test.describe.serial('LOCAL-DEMO-01 Real API + Faker Seed Browser Smoke', () => {
  const demoPassword = loadDemoPassword();

  test('Public portal renders published demo data with MODE DEMO banner and zero MSW', async ({
    page,
  }) => {
    test.setTimeout(60_000);
    const mswRequests: string[] = [];
    const apiRequests: string[] = [];
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];

    page.on('pageerror', (err) => pageErrors.push(err.message));
    page.on('request', (req) => {
      if (req.url().includes('mockServiceWorker')) {
        mswRequests.push(req.url());
      }
      if (req.url().includes('/api/v1/')) {
        apiRequests.push(req.url());
      }
    });
    page.on('response', (res) => {
      if (res.status() >= 500) {
        serverErrors.push(`${res.status()} ${res.url()}`);
      }
    });

    await page.goto('/');
    await expect(page.getByText(/MODE DEMO — DATA SINTETIS/i).first()).toBeVisible();
    await expect(
      page.getByRole('heading', { name: /Transparansi Harga TBS Multi-PKS/i }),
    ).toBeVisible();

    await page.goto('/harga-tbs');
    await expect(page.getByText('PKS-DEMO-01').first()).toBeVisible();
    await expect(page.getByText('PKS-DEMO-02').first()).toBeVisible();
    await expect(page.getByText('PKS-DEMO-05')).toHaveCount(0);
    await expect(page.getByText('PET-DEMO-001')).toHaveCount(0);

    await page.goto('/lokasi-pks');
    await expect(
      page.getByRole('heading', { name: /Lokasi Kantor Perumda & PKS Mitra/i }),
    ).toBeVisible();
    await expect(page.getByText('PKS-DEMO-01').first()).toBeVisible();
    await expect(page.getByText('PKS-DEMO-05')).toHaveCount(0);

    await page.goto('/login');
    await expect(page.getByText(/MODE DEMO — DATA SINTETIS/i).first()).toBeVisible();

    expect(mswRequests).toEqual([]);
    expect(apiRequests.length).toBeGreaterThan(0);
    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });

  test('Seven demo roles log in with real cookies, scoped visibility, DB dashboard aggregates, and UI -> PostgreSQL persistence', async ({
    page,
  }) => {
    test.setTimeout(180_000);
    const mswRequests: string[] = [];
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];

    page.on('pageerror', (err) => pageErrors.push(err.message));
    page.on('request', (req) => {
      if (req.url().includes('mockServiceWorker')) {
        mswRequests.push(req.url());
      }
    });
    page.on('response', (res) => {
      if (res.status() >= 500) {
        serverErrors.push(`${res.status()} ${res.url()}`);
      }
    });

    // 1. FARMER (demo_petani_01): personal read-only data + Jalur C payout, no cross-farmer data
    await loginThroughUi(page, 'demo_petani_01', demoPassword);
    await expect(page).toHaveURL(/\/app\/petani/);
    await expect(page.getByText(/MODE DEMO — DATA SINTETIS/i).first()).toBeVisible();
    await expect(page.getByText('PET-DEMO-001').first()).toBeVisible();
    await expect(page.getByText('SIM-DEMO-TRF-0002').first()).toBeVisible();
    await page.goto('/app/petani/panen');
    await expect(page.getByText('Kebun Demo Blok A #01').first()).toBeVisible();
    await expect(page.getByText(/PAY-/i).first()).toBeVisible();
    await expect(page.getByText('PET-DEMO-002')).toHaveCount(0);
    await logoutThroughUi(page);

    // 2. COOPERATIVE_OPERATOR (demo_kop_op_01): scoped farmers + UI -> PostgreSQL persistence across reload
    await loginThroughUi(page, 'demo_kop_op_01', demoPassword);
    await expect(page).toHaveURL(/\/app\/koperasi$/);

    await page.goto('/app/koperasi/penerimaan');
    const uniqueNote = `DEMO-UI-SMOKE-${Date.now()}`;
    const farmerOpt = page.locator('#rcp-farmer option', { hasText: 'PET-DEMO-001' }).first();
    await expect(farmerOpt).toBeAttached();
    const farmerIdVal = await farmerOpt.getAttribute('value');
    expect(farmerIdVal).toBeTruthy();
    await page.locator('#rcp-farmer').selectOption(farmerIdVal!);
    await page.locator('#rcp-notes').fill(uniqueNote);
    await page.getByRole('button', { name: /Buat Draf Penerimaan/i }).click();

    const draftAlert = page.getByText(/Penerimaan RCV-[A-Z0-9-]+ dibuat/i).first();
    await expect(draftAlert).toBeVisible({ timeout: 15_000 });
    const draftMsg = (await draftAlert.textContent()) ?? '';
    const rcvMatch = draftMsg.match(/RCV-[A-Z0-9-]+/);
    expect(rcvMatch?.[0]).toBeTruthy();
    const createdReceiptNumber = rcvMatch![0];

    await page.getByLabel(/Berat Bruto/i).fill('4250.000');
    await page.getByLabel(/Berat Tara/i).fill('1000.000');
    await expect(page.getByText(/3\.250,000 kg/i).first()).toBeVisible();
    await page.getByRole('button', { name: /Simpan Penimbangan/i }).click();
    await expect(page.getByText(/Timbangan .* tercatat/i).first()).toBeVisible();

    // Reload browser -> verify session persisted via cookie+Redis/PG AND new receipt persisted in PostgreSQL
    await page.reload({ waitUntil: 'domcontentloaded' });
    await expect(page).toHaveURL(/\/app\/koperasi\/penerimaan/);
    await expect(page.getByText(createdReceiptNumber).first()).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/3\.250,000 kg/i).first()).toBeVisible();

    const apiReceipts = await browserApiCall(page, { path: '/api/v1/receipts?page_size=50' });
    expect(apiReceipts.status).toBe(200);
    const receiptRows = (apiReceipts.json.data as Array<{
      receipt_number?: string;
      current_weighing?: {
        gross_weight_kg?: string;
        tare_weight_kg?: string;
        net_weight_kg?: string;
      } | null;
    }>) ?? [];
    const saved = receiptRows.find((r) => r.receipt_number === createdReceiptNumber);
    expect(saved).toBeDefined();
    expect(saved?.current_weighing?.gross_weight_kg).toBe('4250.000');
    expect(saved?.current_weighing?.tare_weight_kg).toBe('1000.000');
    expect(saved?.current_weighing?.net_weight_kg).toBe('3250.000');

    await page.goto('/app/koperasi/surat-jalan');
    await expect(page.getByText(/EDO-/i).first()).toBeVisible();
    await logoutThroughUi(page);

    // Cross-coop check (demo_kop_op_02 does not receive PET-DEMO-001 from KOP-DEMO-01)
    await loginThroughUi(page, 'demo_kop_op_02', demoPassword);
    const kop2Farmers = await browserApiCall(page, { path: '/api/v1/farmers?page_size=50' });
    expect(kop2Farmers.status).toBe(200);
    const kop2Codes = ((kop2Farmers.json.data as Array<{ farmer_code?: string }>) ?? []).map(
      (f) => f.farmer_code,
    );
    expect(kop2Codes.length).toBeGreaterThan(0);
    expect(kop2Codes).not.toContain('PET-DEMO-001');
    await logoutThroughUi(page);

    // 3. PERUMDA_OPERATIONS (demo_perumda_ops_01): real DB dashboard + contracts + reconciliation
    await loginThroughUi(page, 'demo_perumda_ops_01', demoPassword);
    await expect(page).toHaveURL(/\/app\/perumda$/);
    await page.goto('/app/perumda/kontrak');
    await expect(page.locator('table tbody tr', { hasText: 'KTR-DEMO-NEAR-02' }).first()).toBeVisible();
    await expect(page.locator('table tbody tr', { hasText: 'KTR-DEMO-UNC-06' }).first()).toBeVisible();
    await page.goto('/app/perumda/rekonsiliasi');
    await expect(
      page.locator('table tbody tr', { hasText: /Ditahan Sengketa|DISPUTE_HOLD/i }).first(),
    ).toBeVisible();
    await logoutThroughUi(page);

    // 4. PERUMDA_FINANCE (demo_perumda_fin_01): AR/AP invoices & Pending SOP protection
    await loginThroughUi(page, 'demo_perumda_fin_01', demoPassword);
    await expect(page).toHaveURL(/\/app\/perumda\/pembayaran/);
    await expect(page.locator('table tbody tr', { hasText: 'INV-AR-' }).first()).toBeVisible();
    await expect(page.locator('table tbody tr', { hasText: 'INV-AP-' }).first()).toBeVisible();
    await logoutThroughUi(page);

    // 5. MILL_OPERATOR (demo_mill_op_01): scoped e-DOs & weigh tickets for PKS-DEMO-01
    await loginThroughUi(page, 'demo_mill_op_01', demoPassword);
    await expect(page).toHaveURL(/\/app\/pks$/);
    await expect(page.locator('table tbody tr', { hasText: 'EDO-' }).first()).toBeVisible();
    await page.goto('/app/pks/tiket-timbang');
    await expect(page.locator('table tbody tr', { hasText: /WB-DEMO-/i }).first()).toBeVisible();
    await logoutThroughUi(page);

    // 6. DIRECTOR (demo_director_01): executive reporting aggregates & approval queue
    await loginThroughUi(page, 'demo_director_01', demoPassword);
    await expect(page).toHaveURL(/\/app\/direksi$/);
    const execOverview = await browserApiCall(page, { path: '/api/v1/reports/overview' });
    expect(execOverview.status).toBe(200);
    const execData = execOverview.json.data as {
      total_receipts_count?: number;
      total_received_weight_kg?: string;
      matched_reconciliations_count?: number;
      dispute_reconciliations_count?: number;
    };
    expect(execData.total_receipts_count ?? 0).toBeGreaterThanOrEqual(80);
    expect(Number(execData.total_received_weight_kg ?? '0')).toBeGreaterThan(0);
    expect(execData.matched_reconciliations_count ?? 0).toBeGreaterThanOrEqual(1);
    expect(execData.dispute_reconciliations_count ?? 0).toBeGreaterThanOrEqual(1);

    const execFinance = await browserApiCall(page, { path: '/api/v1/reports/finance' });
    expect(execFinance.status).toBe(200);
    const finData = execFinance.json.data as {
      ar_billed_total?: string;
      ap_approved_unpaid_total?: string;
      ap_verified_paid_total?: string;
      is_net_profit?: boolean;
    };
    expect(Number(finData.ar_billed_total ?? '0')).toBeGreaterThan(0);
    expect(Number(finData.ap_approved_unpaid_total ?? '0')).toBeGreaterThan(0);
    expect(Number(finData.ap_verified_paid_total ?? '0')).toBeGreaterThan(0);
    expect(finData.is_net_profit).toBe(false);

    await page.goto('/app/direksi/persetujuan');
    await expect(page.getByText('KTR-DEMO-PEND-07').first()).toBeVisible();
    await logoutThroughUi(page);

    // 7. SYSTEM_ADMIN (demo_sys_admin_01): non-approver governance + user list + audit events
    await loginThroughUi(page, 'demo_sys_admin_01', demoPassword);
    await expect(page).toHaveURL(/\/app\/admin$/);
    await page.goto('/app/admin/pengguna');
    await expect(
      page.locator('table tbody tr', { hasText: 'demo_director_01' }).first(),
    ).toBeVisible();
    await page.goto('/app/admin/audit');
    await expect(page.locator('table tbody tr').first()).toBeVisible();
    await logoutThroughUi(page);

    // After logout, direct navigation to internal route redirects to /login
    await page.goto('/app/koperasi');
    await expect(page).toHaveURL(/\/login/);

    expect(mswRequests).toEqual([]);
    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });
});
