import { expect, test } from '@playwright/test';
import {
  browserApiCall,
  loginThroughUi,
  logoutThroughUi,
  TINY_PNG_BUFFER,
  UAT_IDS,
  UAT_PASSWORD,
} from './uatHelpers';

test.describe.serial('F11.1 Workflows A-F Full Business Logic UAT (Real FastAPI + PostgreSQL 16.15 + Redis)', () => {
  let edoMainNumber = '';
  let edoMainQrToken = '';
  let edoDisputeNumber = '';
  let edoDisputeQrToken = '';
  let edoUnconfNumber = '';
  let edoUnconfQrToken = '';

  test('Workflow A: Public Transparency & Private Data Isolation', async ({ page }) => {
    test.setTimeout(60_000);
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto('/');
    await expect(page.getByRole('heading', { name: /Transparansi Harga TBS Multi-PKS/i })).toBeVisible();
    await expect(page.getByText(/Rp 2\.950,00\/kg/i).first()).toBeVisible();
    await expect(page.getByText(/Rp 2\.890,00\/kg/i).first()).toBeVisible();

    await page.goto('/harga-tbs');
    await expect(page.getByText('PKS-UAT-01').first()).toBeVisible();
    await expect(page.getByText(/Petani UAT Satu/i)).toHaveCount(0);

    // Verified coordinates mill vs unverified coordinates mill vs private unpublished mill
    await page.goto(`/pks/${UAT_IDS.millPub1}`);
    await expect(page.getByRole('heading', { name: /PKS Pangkalan Kerinci UAT/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Buka Navigasi Peta/i })).toBeVisible();

    await page.goto(`/pks/${UAT_IDS.millPub2}`);
    await expect(page.getByRole('heading', { name: /PKS Sorek Makmur UAT/i })).toBeVisible();
    await expect(page.getByText(/Koordinat peta belum terverifikasi/i)).toBeVisible();

    await page.goto(`/pks/${UAT_IDS.millPriv}`);
    await expect(page.getByText(/PKS Rahasia Internal UAT/i)).toHaveCount(0);

    await page.goto('/tentang');
    await expect(page.getByText(/Listrik/i).first()).toBeVisible();
    await page.goto('/kemitraan');
    await expect(page.getByRole('heading', { name: /Kemitraan/i }).first()).toBeVisible();
    await page.goto('/kontak');
    await expect(page.getByText(/\(0761\) 493120/i).first()).toBeVisible();

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });

  test('Workflow B: FLOW-05, FLOW-06, Pricing Governance & Maker != Checker (SoD)', async ({ page }) => {
    test.setTimeout(120_000);
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    await page.setViewportSize({ width: 1440, height: 900 });

    // FLOW-05: Koperasi operator creates farmer, checks paired-coord validation on farm, creates farm, deactivates temp farmer
    await loginThroughUi(page, 'uat_kop_op_01');
    await expect(page).toHaveURL(/\/app\/koperasi$/);

    await page.locator('#farmer-code').fill('PTN-UAT-09');
    await page.locator('#farmer-coop').selectOption(UAT_IDS.coop1);
    await page.locator('#farmer-name').fill('Petani Uji Deaktivasi');
    await page.locator('#farmer-phone').fill('081233445566');
    await page.getByRole('button', { name: /Simpan Data Petani/i }).click();
    await expect(page.getByText('PTN-UAT-09').first()).toBeVisible();

    // Paired coordinate validation on Farm (only latitude -> inline error)
    await page.locator('#farm-farmer').selectOption(UAT_IDS.farmer1);
    await page.locator('#farm-code').fill('KBN-UAT-09');
    await page.locator('#farm-name').fill('Kebun UAT Sembilan');
    await page.locator('#farm-area').fill('3.2500');
    await page.locator('#farm-village').fill('Makmur');
    await page.locator('#farm-district').fill('Pelalawan');
    await page.locator('#farm-lat').fill('0.411100');
    await page.getByRole('button', { name: /Simpan Data Kebun/i }).click();
    await expect(page.getByText(/Koordinat wajib diisi berpasangan/i)).toBeVisible();

    await page.locator('#farm-lon').fill('101.855500');
    await page.getByRole('button', { name: /Simpan Data Kebun/i }).click();
    await expect(page.getByText('KBN-UAT-09').first()).toBeVisible();

    // Safe deactivation of PTN-UAT-09 via ConfirmDialog (reason required >= 5 chars)
    const farmerRow = page.locator('tr', { hasText: 'PTN-UAT-09' });
    await farmerRow.getByRole('button', { name: /Nonaktifkan/i }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.locator('#confirm-dialog-reason').fill('Uji nonaktif petani selesai');
    await page.getByRole('button', { name: /Simpan Perubahan Status/i }).click();
    await expect(
      page.locator('tr', { hasText: 'PTN-UAT-09' }).getByText(/^(INACTIVE|Nonaktif)$/i),
    ).toBeVisible();

    await logoutThroughUi(page);

    // FLOW-06: Perumda OPS creates a verified public mill + Pricing Draft -> Submit -> SoD block
    await loginThroughUi(page, 'uat_perumda_ops_01');
    await expect(page).toHaveURL(/\/app\/perumda$/);

    await page.locator('#mill-company').selectOption({ index: 1 });
    await page.locator('#mill-code').fill('PKS-UAT-03');
    await page.locator('#mill-name').fill('PKS Pelalawan Baru UAT');
    await page.locator('#mill-address').fill('Jl. Poros Sawit KM 15');
    await page.locator('#mill-district').fill('Bunut');
    await page.locator('#mill-regency').fill('Pelalawan');
    await page.locator('#mill-phone').fill('0761-776655');
    await page.locator('#mill-lat').fill('0.422200');
    // Negative paired coord check first
    await page.getByRole('button', { name: /Simpan Data PKS/i }).click();
    await expect(page.getByText(/Latitude \(-90 s\.d\. 90\) dan Longitude/i)).toBeVisible();

    await page.locator('#mill-lon').fill('101.877700');
    await page.locator('#mill-is-public').check();
    await page.getByRole('button', { name: /Simpan Data PKS/i }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.getByRole('button', { name: /Ya, Publikasikan Profil PKS/i }).click();
    await expect(page.getByText('PKS-UAT-03').first()).toBeVisible();

    // Pricing Draft -> Submit -> SoD self-verify block
    await page.goto('/app/perumda/harga');
    await expect(page.getByRole('heading', { name: /Manajemen Harga Multi-PKS/i })).toBeVisible();
    await page.locator('#prc-mill').selectOption(UAT_IDS.millPub1);
    await page.locator('#prc-amount').fill('2915.00');
    await page.getByRole('button', { name: /Simpan Draf Harga/i }).click();
    await expect(page.getByText(/2\.915,00/i).first()).toBeVisible();

    const quoteRowOps1 = page.locator('tr', { hasText: '2.915,00' }).first();
    await quoteRowOps1.getByRole('button', { name: /Ajukan Verifikasi/i }).click();
    await expect(quoteRowOps1.getByRole('button', { name: /Uji Blokir Self-Verify/i })).toBeVisible();
    await quoteRowOps1.getByRole('button', { name: /Uji Blokir Self-Verify/i }).click();
    await expect(page.getByRole('alert')).toContainText(/AUTH_CONFLICT_OF_DUTIES/i);

    await logoutThroughUi(page);

    // Ops #2 checker verifies & publishes quote -> live on /harga-tbs
    await loginThroughUi(page, 'uat_perumda_ops_02');
    await page.goto('/app/perumda/harga');
    const quoteRowOps2 = page.locator('tr', { hasText: '2.915,00' }).first();
    await quoteRowOps2.getByRole('button', { name: /Setujui Verifikasi/i }).click();
    await expect(quoteRowOps2.getByRole('button', { name: /Publikasikan/i })).toBeVisible();
    await quoteRowOps2.getByRole('button', { name: /Publikasikan/i }).click();
    await expect(quoteRowOps2.getByText(/PUBLISHED|Dipublikasikan/i).first()).toBeVisible();

    await page.goto('/harga-tbs');
    await expect(page.getByText(/Rp 2\.915,00\/kg/i).first()).toBeVisible();

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });

  test('Workflow C: Contract Draft -> Director Approval -> Active Contract State', async ({ page }) => {
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    await page.setViewportSize({ width: 1440, height: 900 });
    await loginThroughUi(page, 'uat_perumda_ops_01');
    await page.goto('/app/perumda/kontrak');
    await expect(page.getByRole('heading', { name: /Manajemen Kontrak Niaga & Kuota Pasokan PKS/i })).toBeVisible();

    await page.locator('#ktr-num').fill('KTR-UAT-NEW-003');
    await page.locator('#ktr-mill').selectOption(UAT_IDS.millPub1);
    await page.locator('#ktr-quota').fill('60000.000');
    await page.locator('#ktr-price').fill('2915.00');
    await page.locator('#ktr-model').selectOption('PRINCIPAL');
    await page.getByRole('button', { name: /Simpan Draf Kontrak/i }).click();

    const ktrRow = page.locator('tr', { hasText: 'KTR-UAT-NEW-003' });
    await expect(ktrRow).toBeVisible();
    await expect(ktrRow.getByText(/PENDING_APPROVAL|Menunggu Persetujuan/i)).toBeVisible();

    await logoutThroughUi(page);

    await loginThroughUi(page, 'uat_director_01');
    await page.goto('/app/direksi/persetujuan');
    const pendingCard = page.locator('div', { hasText: 'KTR-UAT-NEW-003' }).filter({
      has: page.getByRole('button', { name: /Aktifkan Kontrak/i }),
    }).first();
    await expect(pendingCard).toBeVisible();
    await pendingCard.getByRole('button', { name: /Aktifkan Kontrak/i }).click();
    await expect(page.getByText(/KTR-UAT-NEW-003 disetujui menjadi ACTIVE/i)).toBeVisible();

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });

  test('Workflow D: Receiving -> Grading (Simulation) -> Validation -> e-DO -> Over-Quota Block -> Cross-Mill Isolation -> Mill Weighing -> Reconciliation & Dispute Hold', async ({
    page,
  }) => {
    test.setTimeout(150_000);
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    await page.setViewportSize({ width: 1440, height: 900 });
    await loginThroughUi(page, 'uat_kop_op_01');

    // Step D1: Create draft receipt, check Tara > Bruto guard, weigh 5000/800 = 4200 kg, grade 2%, validate
    await page.goto('/app/koperasi/penerimaan');
    await page.locator('#rcp-farmer').selectOption(UAT_IDS.farmer1);
    await page.getByRole('button', { name: /Buat Draf Penerimaan/i }).click();
    await expect(page.getByText(/Penerimaan RCV-.* dibuat/i).first()).toBeVisible();

    await page.getByLabel(/Berat Bruto/i).fill('1000.000');
    await page.getByLabel(/Berat Tara/i).fill('1500.000');
    await page.getByRole('button', { name: /Simpan Penimbangan/i }).click();
    await expect(page.getByRole('alert')).toBeVisible();

    await page.getByLabel(/Berat Bruto/i).fill('5000.000');
    await page.getByLabel(/Berat Tara/i).fill('800.000');
    await expect(page.getByText(/4\.200,000 kg/i).first()).toBeVisible();
    await page.getByRole('button', { name: /Simpan Penimbangan/i }).click();
    await expect(page.getByText(/Timbangan .* tercatat/i).first()).toBeVisible();

    await page.getByRole('button', { name: /Catat Grading Simulasi/i }).click();
    await expect(page.getByText(/Grading .* dicatat/i).first()).toBeVisible();

    await page.getByRole('button', { name: /Validasi Penerimaan/i }).click();
    await expect(page.getByText(/VALIDATED|Tervalidasi/i).first()).toBeVisible();

    // Step D2: Create e-DO #1 (Main 4200 kg), Issue, Depart; also e-DO #2 (Dispute 4000 kg), e-DO #3 (Unconfirmed 3000 kg)
    await page.goto('/app/koperasi/surat-jalan');

    // Find checkbox for newly created 4200 kg receipt
    const createEdoForReceipt = async (receiptSelectorText: RegExp, targetContractId: string) => {
      const label = page.locator('label', { hasText: receiptSelectorText }).first();
      await label.locator('input[type="checkbox"]').check();
      await page.locator('#edo-mill').selectOption(UAT_IDS.millPub1);
      const contractInput = page.locator('#edo-contract');
      const tag = await contractInput.evaluate((el) => el.tagName.toLowerCase());
      if (tag === 'input') {
        await contractInput.fill(targetContractId);
      } else {
        const hasOpt = await contractInput.locator(`option[value="${targetContractId}"]`).count();
        if (hasOpt > 0) {
          await contractInput.selectOption(targetContractId);
        } else {
          await contractInput.selectOption('__CUSTOM__');
          await page.locator('#edo-contract-custom').fill(targetContractId);
        }
      }
      await page.getByRole('button', { name: /Susun Draf e-DO/i }).click();
      await expect(page.getByText(/Draf e-DO .* dibuat/i).first()).toBeVisible();
    };

    const readSelectedQrToken = async (doNum: string) => {
      const qrSection = page.locator('section', { hasText: `Detail e-DO: ${doNum}` }).first();
      await expect(qrSection).toBeVisible();
      const tokenText = await qrSection
        .locator('div', { hasText: 'Token Verifikasi Terkendali PKS' })
        .locator('p.font-mono')
        .first()
        .textContent();
      const cleaned = tokenText?.trim() ?? '';
      expect(cleaned.length).toBeGreaterThan(4);
      return cleaned;
    };

    // 1. Main e-DO (4.200,000 kg)
    await createEdoForReceipt(/4\.200,000 kg/i, UAT_IDS.contractPri);
    let row = page.locator('tr', { hasText: '4.200,000 kg' }).first();
    await row.getByRole('button', { name: /Terbitkan e-DO/i }).click();
    await expect(row.getByRole('button', { name: /Berangkat/i })).toBeVisible();
    edoMainNumber = (await row.locator('p.font-mono').first().textContent())?.trim() ?? '';
    await row.getByRole('button', { name: /Berangkat/i }).click();
    await expect(row.getByText(/Dalam Perjalanan|IN_TRANSIT/i).first()).toBeVisible();
    await row.locator('button', { hasText: edoMainNumber }).click();
    edoMainQrToken = await readSelectedQrToken(edoMainNumber);

    // 2. Dispute e-DO (seeded TRM-UAT-DSP-001, 4.000,000 kg)
    await createEdoForReceipt(/TRM-UAT-DSP-001/i, UAT_IDS.contractPri);
    row = page.locator('tr', { hasText: '4.000,000 kg' }).first();
    await row.getByRole('button', { name: /Terbitkan e-DO/i }).click();
    await expect(row.getByRole('button', { name: /Berangkat/i })).toBeVisible();
    edoDisputeNumber = (await row.locator('p.font-mono').first().textContent())?.trim() ?? '';
    await row.getByRole('button', { name: /Berangkat/i }).click();
    await expect(row.getByText(/Dalam Perjalanan|IN_TRANSIT/i).first()).toBeVisible();
    await row.locator('button', { hasText: edoDisputeNumber }).click();
    edoDisputeQrToken = await readSelectedQrToken(edoDisputeNumber);

    // 3. UNCONFIRMED Pending-SOP e-DO (seeded TRM-UAT-UNC-002, 3.000,000 kg)
    await createEdoForReceipt(/TRM-UAT-UNC-002/i, UAT_IDS.contractUnconf);
    row = page.locator('tr', { hasText: '3.000,000 kg' }).first();
    await row.getByRole('button', { name: /Terbitkan e-DO/i }).click();
    await expect(row.getByRole('button', { name: /Berangkat/i })).toBeVisible();
    edoUnconfNumber = (await row.locator('p.font-mono').first().textContent())?.trim() ?? '';
    await row.getByRole('button', { name: /Berangkat/i }).click();
    await expect(row.getByText(/Dalam Perjalanan|IN_TRANSIT/i).first()).toBeVisible();
    await row.locator('button', { hasText: edoUnconfNumber }).click();
    edoUnconfQrToken = await readSelectedQrToken(edoUnconfNumber);

    expect(edoMainNumber).toMatch(/^EDO-/);
    expect(edoDisputeNumber).toMatch(/^EDO-/);
    expect(edoUnconfNumber).toMatch(/^EDO-/);

    await logoutThroughUi(page);

    // Step D3: Test over-quota atomic block on /app/perumda/kontrak (CONTRACT_QUOTA_EXCEEDED)
    await loginThroughUi(page, 'uat_perumda_ops_01');
    await page.goto('/app/perumda/kontrak');
    await page.locator('#res-ktr').selectOption(UAT_IDS.contractPri);
    await page.locator('#res-kg').fill('55000.000');
    await page.getByRole('button', { name: /Cadangkan Kuota PKS/i }).click();
    await expect(page.getByRole('alert')).toContainText(/CONTRACT_QUOTA_EXCEEDED/i);
    await logoutThroughUi(page);

    // Step D4: Cross-mill mismatch check (MILL_PRIV operator cannot verify MILL_PUB e-DO)
    await loginThroughUi(page, 'uat_mill_op_02');
    await page.goto('/app/pks');
    await page.locator('#pks-qr-input').fill(edoMainQrToken);
    await page.locator('#pks-plate-input').fill('BM 9102 UAT');
    await page.getByRole('button', { name: /Verifikasi Tiba/i }).click();
    await expect(page.getByRole('alert')).toContainText(/MILL_EDO_MILL_MISMATCH/i);
    await logoutThroughUi(page);

    // Step D5: Authorized Mill arrival verification & weigh tickets for all 3 e-DOs
    await loginThroughUi(page, 'uat_mill_op_01');
    await page.goto('/app/pks');
    for (const [edoNum, token] of [
      [edoMainNumber, edoMainQrToken],
      [edoDisputeNumber, edoDisputeQrToken],
      [edoUnconfNumber, edoUnconfQrToken],
    ] as const) {
      await page.locator('#pks-qr-input').fill(token);
      await page.locator('#pks-plate-input').fill('BM 9102 UAT');
      await page.getByRole('button', { name: /Verifikasi Tiba/i }).click();
      await expect(
        page.getByText(new RegExp(`Kedatangan ${edoNum} terverifikasi`, 'i')).first(),
      ).toBeVisible();
    }

    await page.goto('/app/pks/tiket-timbang');
    const createAndVerifyTicket = async (
      edoNumber: string,
      ticketNo: string,
      gross: string,
      tare: string,
    ) => {
      const optLocator = page.locator('#wb-edo option', { hasText: edoNumber }).first();
      await expect(optLocator).toBeAttached();
      const optValue = await optLocator.getAttribute('value');
      expect(optValue).toBeTruthy();
      await page.locator('#wb-edo').selectOption(optValue!);
      await page.locator('#wb-num').fill(ticketNo);
      await page.getByLabel(/Berat Bruto/i).fill(gross);
      await page.getByLabel(/Berat Tara/i).fill(tare);
      await page.locator('#wb-proof').setInputFiles({
        name: 'slip-timbang.png',
        mimeType: 'image/png',
        buffer: TINY_PNG_BUFFER,
      });
      await expect(page.getByText(/ID Bukti Tersimpan/i)).toBeVisible();
      await page.getByRole('button', { name: /Simpan Tiket Timbang PKS/i }).click();
      const tRow = page.locator('tr', { hasText: ticketNo }).first();
      await expect(tRow).toBeVisible();
      await tRow.getByRole('button', { name: /Verifikasi Final/i }).click();
      await expect(tRow.getByText(/VERIFIED|Terverifikasi/i).first()).toBeVisible();
    };

    // Normal tolerance: origin 4200 vs mill 4150 (1.19% <= 1.50%) -> MATCHED
    await createAndVerifyTicket(edoMainNumber, 'WB-UAT-001', '14150.000', '10000.000');
    // Negative difference anomaly: origin 4000 vs mill 4350 -> ANOMALY_NEGATIVE_DIFFERENCE -> DISPUTE_HOLD
    await createAndVerifyTicket(edoDisputeNumber, 'WB-UAT-002', '14350.000', '10000.000');
    // Unconfirmed contract normal tolerance: origin 3000 vs mill 2980 -> MATCHED
    await createAndVerifyTicket(edoUnconfNumber, 'WB-UAT-003', '12980.000', '10000.000');

    await logoutThroughUi(page);

    // Step D6: Perumda OPS triggers & calculates reconciliation + Dispute review/SOD-03 + 30/20/50 Simulation + FINAL block
    await loginThroughUi(page, 'uat_perumda_ops_01');
    await page.goto('/app/perumda/rekonsiliasi');
    for (const edoNum of [edoMainNumber, edoDisputeNumber, edoUnconfNumber]) {
      const recOpt = page.locator('#rec-trigger-do option', { hasText: edoNum }).first();
      await expect(recOpt).toBeAttached();
      const recDoId = await recOpt.getAttribute('value');
      await page.locator('#rec-trigger-do').selectOption(recDoId!);
      await page.getByRole('button', { name: /Buat & Hitung Rekonsiliasi/i }).click();
      await expect(
        page.getByText(new RegExp(`Rekonsiliasi ${edoNum} dihitung`, 'i')).first(),
      ).toBeVisible();
    }

    // Check negative anomaly banner on Dispute case -> review into UNDER_REVIEW -> verify SOD-03 blocks same reviewer from resolving
    await page.locator('tr', { hasText: edoDisputeNumber }).first().getByRole('button', { name: edoDisputeNumber }).click();
    await expect(page.getByText(/Anomali Selisih Negatif terdeteksi/i)).toBeVisible();
    await page.getByRole('button', { name: /Catat Klarifikasi Sengketa/i }).click();
    await page.locator('#confirm-dialog-reason').fill('Klarifikasi awal selisih negatif oleh operasional');
    await page.getByRole('button', { name: /Simpan Pemeriksaan/i }).click();
    await expect(page.getByText(/Hasil pemeriksaan sengketa dicatat/i).first()).toBeVisible();

    await page.getByRole('button', { name: /Putuskan Sengketa \(Resolve\)/i }).click();
    await page.locator('#confirm-dialog-reason').fill('Uji pelanggaran pemisahan tugas reviewer resolve');
    await page.getByRole('button', { name: /Sahkan Penyelesaian/i }).click();
    await expect(
      page.getByRole('alert').filter({ hasText: /AUTH_CONFLICT_OF_DUTIES/i }).first(),
    ).toBeVisible();

    // Run 30/20/50 simulation on Main case & verify FINAL block (Pending SOP)
    await page.locator('tr', { hasText: edoMainNumber }).first().getByRole('button', { name: edoMainNumber }).click();
    await page.getByRole('button', { name: /Jalankan Simulasi Alokasi/i }).click();
    await expect(page.getByText(/Petani UAT Satu/i).first()).toBeVisible();
    await page.getByRole('button', { name: /Uji Finalisasi Alokasi Resmi/i }).click();
    await expect(
      page.getByRole('alert').filter({ hasText: /REC_ALLOCATION_POLICY_UNCONFIRMED/i }).first(),
    ).toBeVisible();

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });

  test('Workflow E: Finance AR/AP Separation, DISPUTE_HOLD & Pending-SOP Blocks, Maker != Checker SoD, Executive Approval != PAID, Full Manual Settlement -> Farmer Visibility', async ({
    page,
  }) => {
    test.setTimeout(150_000);
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    await page.setViewportSize({ width: 1440, height: 900 });

    // E1: FIN #1 verifies DISPUTE_HOLD & UNCONFIRMED blocks + drafts AR & AP for Main e-DO
    await loginThroughUi(page, 'uat_perumda_fin_01');
    await expect(page).toHaveURL(/\/app\/perumda\/pembayaran$/);

    // Block 1: DISPUTE_HOLD invoice drafting denied
    const disputeOptLoc = page.locator('#inv-rec option', { hasText: edoDisputeNumber }).first();
    await expect(disputeOptLoc).toBeAttached();
    const disputeOpt = await disputeOptLoc.getAttribute('value');
    await page.locator('#inv-rec').selectOption(disputeOpt!);
    await page.locator('#inv-type').selectOption('ACCOUNTS_RECEIVABLE');
    await page.getByRole('button', { name: /Buat Draf Faktur/i }).click();
    await expect(page.getByRole('alert')).toContainText(/FIN_DISPUTE_HOLD_BLOCKED/i);

    // Draft UNCONFIRMED invoice (allowed in draft, blocked on issue -> FIN_POLICY_UNCONFIRMED)
    const unconfOptLoc = page.locator('#inv-rec option', { hasText: edoUnconfNumber }).first();
    await expect(unconfOptLoc).toBeAttached();
    const unconfOpt = await unconfOptLoc.getAttribute('value');
    await page.locator('#inv-rec').selectOption(unconfOpt!);
    await page.locator('#inv-type').selectOption('ACCOUNTS_RECEIVABLE');
    await page.getByRole('button', { name: /Buat Draf Faktur/i }).click();
    await expect(page.getByText(/PENDING_SOP/i).first()).toBeVisible();

    // Draft AR and AP for Main e-DO
    const mainOptLoc = page.locator('#inv-rec option', { hasText: edoMainNumber }).first();
    await expect(mainOptLoc).toBeAttached();
    const mainOpt = await mainOptLoc.getAttribute('value');
    await page.locator('#inv-rec').selectOption(mainOpt!);
    await page.locator('#inv-type').selectOption('ACCOUNTS_RECEIVABLE');
    await page.getByRole('button', { name: /Buat Draf Faktur/i }).click();
    await expect(page.getByText(/Draf faktur INV-AR-/i).first()).toBeVisible();

    await page.locator('#inv-rec').selectOption(mainOpt!);
    await page.locator('#inv-type').selectOption('ACCOUNTS_PAYABLE');
    await page.getByRole('button', { name: /Buat Draf Faktur/i }).click();
    await expect(page.getByText(/Draf faktur INV-AP-/i).first()).toBeVisible();

    // Verify Maker!=Checker block on Invoice verify (SOD-04)
    const arDraftRow = page.locator('tr', { hasText: 'INV-AR-' }).first();
    await arDraftRow.getByRole('button', { name: /^Verifikasi$/i }).click();
    await expect(page.getByRole('alert')).toContainText(/AUTH_CONFLICT_OF_DUTIES/i);

    await logoutThroughUi(page);

    // E2: FIN #2 checker verifies all 3 invoices & triggers FIN_POLICY_UNCONFIRMED on PENDING_SOP invoice, issues Main AR & AP
    await loginThroughUi(page, 'uat_perumda_fin_02');
    const verifyButtonsLocator = page.locator('tr', {
      has: page.getByRole('button', { name: /^Verifikasi$/i }),
    });
    await expect(verifyButtonsLocator.first()).toBeVisible();
    const countPending = await verifyButtonsLocator.count();
    expect(countPending).toBe(3);
    for (let i = 0; i < countPending; i++) {
      await verifyButtonsLocator.first().getByRole('button', { name: /^Verifikasi$/i }).click();
      await expect(verifyButtonsLocator).toHaveCount(countPending - i - 1);
    }

    // Try issuing PENDING_SOP invoice -> FIN_POLICY_UNCONFIRMED
    const pendingSopRow = page.locator('tr', { hasText: 'PENDING_SOP' }).first();
    await pendingSopRow.getByRole('button', { name: /Terbitkan Faktur/i }).click();
    await expect(page.getByRole('alert')).toContainText(/FIN_POLICY_UNCONFIRMED/i);

    // Issue Main AR and Main AP invoices
    const arMainRow = page.locator('tr', { hasText: 'INV-AR-' }).filter({ hasText: 'SIMULATION_ONLY' }).first();
    await arMainRow.getByRole('button', { name: /Terbitkan Faktur/i }).click();
    await expect(arMainRow.getByText(/Diterbitkan|ISSUED/i).first()).toBeVisible();

    const apMainRow = page.locator('tr', { hasText: 'INV-AP-' }).filter({ hasText: 'SIMULATION_ONLY' }).first();
    await apMainRow.getByRole('button', { name: /Terbitkan Faktur/i }).click();
    await expect(apMainRow.getByText(/Diterbitkan|ISSUED/i).first()).toBeVisible();

    await logoutThroughUi(page);

    // E3: Verify PAY_APPROVAL_REQUIRED before Director approval on AP
    await loginThroughUi(page, 'uat_perumda_fin_01');
    const apPayOptLoc = page.locator('#pay-inv option', { hasText: 'INV-AP-' }).first();
    await expect(apPayOptLoc).toBeAttached();
    const apInvOption = await apPayOptLoc.getAttribute('value');
    const apInvNum = (await apMainRowText(page)) ?? 'INV-AP-';
    expect(apInvOption).toBeTruthy();
    await page.locator('#pay-inv').selectOption(apInvOption!);
    await Promise.all([
      page.waitForResponse((res) => res.url().includes('/api/v1/files') && res.request().method() === 'POST' && res.status() === 201),
      page.locator('#pay-proof').setInputFiles({
        name: 'bukti-ap.png',
        mimeType: 'image/png',
        buffer: TINY_PNG_BUFFER,
      }),
    ]);
    await expect(page.getByText(/Bukti: bukti-ap\.png/i)).toBeVisible();
    await page.locator('#pay-ref').fill('REF-PRE-APPR-001');
    await page.getByRole('button', { name: /Catat Bukti Pembayaran/i }).click();
    await expect(
      page.getByRole('alert').filter({ hasText: /PAY_APPROVAL_REQUIRED/i }).first(),
    ).toBeVisible();
    await logoutThroughUi(page);

    // E4: Director approves AP payment (APPROVED -> AWAITING_PAYMENT, NOT PAID!) & resolves Dispute
    await loginThroughUi(page, 'uat_director_01');
    await page.goto('/app/direksi/persetujuan');
    const apApprovalCard = page.locator('div', { hasText: 'INV-AP-' }).filter({
      has: page.getByRole('button', { name: /Setujui Pencairan/i }),
    }).first();
    await apApprovalCard.getByRole('button', { name: /Setujui Pencairan/i }).click();
    await page.locator('#confirm-dialog-reason').fill('Otorisasi pencairan dana AP UAT disetujui');
    await page.getByRole('button', { name: /Sahkan Keputusan/i }).click();
    await expect(page.getByText(/Otorisasi pembayaran INV-AP-.*: APPROVED/i).first()).toBeVisible();

    // Resolve Dispute case
    const disputeCard = page.locator('div', { hasText: edoDisputeNumber }).filter({
      has: page.getByRole('button', { name: /Putuskan Sengketa/i }),
    }).first();
    await disputeCard.getByRole('button', { name: /Putuskan Sengketa/i }).click();
    await page.locator('#confirm-dialog-reason').fill('Klarifikasi berat jembatan timbang diterima oleh Direksi');
    await page.getByRole('button', { name: /Sahkan Keputusan/i }).click();
    await expect(page.getByText(/diselesaikan \(RESOLVED\)/i).first()).toBeVisible();

    await logoutThroughUi(page);

    // Confirm Farmer Portal sees grading & NOT Lunas Terverifikasi (PAID) yet before verified transfer!
    await loginThroughUi(page, 'uat_petani_01');
    await page.goto('/app/petani/panen');
    await expect(page.getByText(/Potongan Grading Terpisah/i).first()).toBeVisible();
    await expect(page.getByText(/2,0000%/i).first()).toBeVisible();
    await expect(page.getByText(/Lunas Terverifikasi/i)).toHaveCount(0);
    await logoutThroughUi(page);

    // E5: FIN #1 rejects partial payment (PAY_PARTIAL_NOT_SUPPORTED), records full payment, blocked from self-verify (SoD)
    await loginThroughUi(page, 'uat_perumda_fin_01');
    const apRowFin = page.locator('tr', { hasText: 'INV-AP-' }).first();
    await expect(apRowFin.getByText(/Menunggu Pembayaran|AWAITING_PAYMENT/i).first()).toBeVisible();
    const apOptFin = await page.locator('#pay-inv option:has-text("INV-AP-")').first().getAttribute('value');
    await page.locator('#pay-inv').selectOption(apOptFin!);

    // Negative partial payment check
    await page.locator('#pay-amt').fill('1000.00');
    await page.locator('#pay-ref').fill('REF-PARTIAL-001');
    await Promise.all([
      page.waitForResponse((res) => res.url().includes('/api/v1/files') && res.request().method() === 'POST' && res.status() === 201),
      page.locator('#pay-proof').setInputFiles({
        name: 'bukti-ap.png',
        mimeType: 'image/png',
        buffer: TINY_PNG_BUFFER,
      }),
    ]);
    await expect(page.getByText(/Bukti: bukti-ap\.png/i)).toBeVisible();
    await page.getByRole('button', { name: /Catat Bukti Pembayaran/i }).click();
    await expect(
      page.getByRole('alert').filter({ hasText: /PAY_PARTIAL_NOT_SUPPORTED/i }).first(),
    ).toBeVisible();

    // Full exact payment
    await page.locator('#pay-amt').fill('');
    await page.locator('#pay-ref').fill(`REF-AP-FULL-${apInvNum}`);
    await page.getByRole('button', { name: /Catat Bukti Pembayaran/i }).click();
    await expect(page.getByText(/menunggu verifikasi checker/i).first()).toBeVisible();

    // Maker != Checker self-verify block on payment (SOD-05)
    await apRowFin.getByRole('button', { name: /Verifikasi Bayar/i }).click();
    await expect(
      page.getByRole('alert').filter({ hasText: /AUTH_CONFLICT_OF_DUTIES/i }).first(),
    ).toBeVisible();
    await logoutThroughUi(page);

    // E6: FIN #2 verifies payment -> PAID, then duplicate payment blocked (PAY_DUPLICATE_PAYMENT)
    await loginThroughUi(page, 'uat_perumda_fin_02');
    const apRowChecker = page.locator('tr', { hasText: 'INV-AP-' }).first();
    await apRowChecker.getByRole('button', { name: /Verifikasi Bayar/i }).click();
    await expect(apRowChecker.getByText(/Lunas Terverifikasi|PAID/i).first()).toBeVisible();

    // Duplicate payment attempt blocked cleanly
    const apOptDup = await page.locator('#pay-inv option:has-text("INV-AP-")').first().getAttribute('value');
    await page.locator('#pay-inv').selectOption(apOptDup!);
    await Promise.all([
      page.waitForResponse((res) => res.url().includes('/api/v1/files') && res.request().method() === 'POST' && res.status() === 201),
      page.locator('#pay-proof').setInputFiles({
        name: 'bukti-dup.png',
        mimeType: 'image/png',
        buffer: TINY_PNG_BUFFER,
      }),
    ]);
    await expect(page.getByText(/Bukti: bukti-dup\.png/i)).toBeVisible();
    await page.locator('#pay-ref').fill('REF-DUP-001');
    await page.getByRole('button', { name: /Catat Bukti Pembayaran/i }).click();
    await expect(
      page.getByRole('alert').filter({ hasText: /PAY_DUPLICATE_PAYMENT/i }).first(),
    ).toBeVisible();

    await logoutThroughUi(page);

    // E7: Cooperative sees VERIFIED OUTBOUND payment on /api/v1/payments, and Farmer portal sees grading simulation without cross-farmer leakage
    await loginThroughUi(page, 'uat_kop_op_01');
    const coopPays = await browserApiCall(page, { path: '/api/v1/payments' });
    expect(coopPays.status).toBe(200);
    const coopPayRows = (coopPays.json.data as Array<{ payment_direction?: string; status?: string }> | undefined) ?? [];
    expect(coopPayRows.some((p) => p.payment_direction === 'OUTBOUND' && p.status === 'VERIFIED')).toBe(true);
    await logoutThroughUi(page);

    await loginThroughUi(page, 'uat_petani_01');
    await page.goto('/app/petani/panen');
    await expect(page.getByText(/Potongan Grading Terpisah/i).first()).toBeVisible();
    await expect(page.getByText(/2,0000%/i).first()).toBeVisible();
    await expect(page.getByText(/Petani UAT Dua/i)).toHaveCount(0);
    await logoutThroughUi(page);

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });

  test('Workflow F: System Admin Rule Versioning (CONFIRMED blocked), Temp User Create & Instant Session Revocation + Audit Trail', async ({
    page,
    browser,
  }) => {
    test.setTimeout(120_000);
    const pageErrors: string[] = [];
    const serverErrors: string[] = [];
    page.on('pageerror', (e) => pageErrors.push(e.message));
    page.on('response', (res) => {
      if (res.status() >= 500) serverErrors.push(`${res.status()} ${res.url()}`);
    });

    await page.setViewportSize({ width: 1440, height: 900 });
    await loginThroughUi(page, 'uat_sys_admin_01');
    await page.goto('/app/admin/pengguna');

    // BR-SYS-002 block CONFIRMED rule version
    await page.locator('#rule-policy').selectOption('CONFIRMED');
    await page.getByRole('button', { name: /Buat Versi Aturan Baru/i }).click();
    await expect(page.getByRole('alert')).toBeVisible();

    // Append-only SIMULATION_ONLY rule version
    await page.locator('#rule-policy').selectOption('SIMULATION_ONLY');
    await page.locator('#rule-value').fill('1.7500');
    await page.locator('#rule-reason').fill('Uji aturan simulasi F11.1');
    await page.getByRole('button', { name: /Buat Versi Aturan Baru/i }).click();
    await expect(page.getByText(/RECONCILIATION_WEIGHT_TOLERANCE v\d+ tercatat/i)).toBeVisible();

    // Create temporary user, log that user in on a separate browser context, deactivate user -> session immediately revoked!
    await page.getByRole('button', { name: /\+ Tambah Akun Pengguna/i }).click();
    await page.locator('#new-username').fill('uat_temp_revoke_01');
    await page.locator('#new-email').fill('uat_temp_revoke_01@uat.invalid');
    await page.locator('#new-password').fill(UAT_PASSWORD);
    await page.locator('#new-role').selectOption('COOPERATIVE_OPERATOR');
    await page.locator('#new-scope').selectOption('COOPERATIVE');
    await page.locator('#new-target-id').fill(UAT_IDS.coop1);
    await page.getByRole('button', { name: /Simpan Akun Baru/i }).click();
    await expect(page.locator('tr', { hasText: 'uat_temp_revoke_01' })).toBeVisible();

    const tempContext = await browser.newContext();
    const tempPage = await tempContext.newPage();
    await loginThroughUi(tempPage, 'uat_temp_revoke_01');
    await expect(tempPage).toHaveURL(/\/app\/koperasi$/);

    // Admin deactivates uat_temp_revoke_01
    const tempRow = page.locator('tr', { hasText: 'uat_temp_revoke_01' }).first();
    await tempRow.getByRole('button', { name: /Nonaktifkan/i }).click();
    await page.locator('#confirm-dialog-reason').fill('Cabut akses akun uji UAT F11.1');
    await page.getByRole('button', { name: /Nonaktifkan Akun/i }).click();
    await expect(
      page.getByText(/Status akun uat_temp_revoke_01 diubah menjadi INACTIVE/i),
    ).toBeVisible();
    await expect(
      page.locator('tr', { hasText: 'uat_temp_revoke_01' }).getByText(/^(INACTIVE|Nonaktif)$/i),
    ).toBeVisible();

    // Existing session of revoked user immediately invalidated on API & reload -> redirect to /login
    const meAfterRevoke = await browserApiCall(tempPage, { path: '/api/v1/auth/me' });
    expect([401, 403]).toContain(meAfterRevoke.status);
    await tempPage.reload();
    await expect(tempPage).toHaveURL(/\/login/);
    await tempContext.close();

    // Audit trail displays real audit events from workflow actions
    await page.goto('/app/admin/audit');
    await expect(page.getByRole('heading', { name: /Audit/i }).first()).toBeVisible();
    await expect(page.locator('table tbody tr').first()).toBeVisible();

    expect(pageErrors).toEqual([]);
    expect(serverErrors).toEqual([]);
  });
});

async function apMainRowText(page: import('@playwright/test').Page): Promise<string | null> {
  return page.locator('tr', { hasText: 'INV-AP-' }).first().locator('p.font-mono').first().textContent();
}
