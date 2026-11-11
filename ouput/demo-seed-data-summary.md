# Ringkasan Data Dummy Seeder (`agroniaga_demo`)

> **Catatan:** Seluruh data berikut merupakan **DATA SINTETIS DEMO** bertanda `DEMO` dari `backend/scripts/seed_demo.py` (`DEMO_SEED=20261111`, `Faker('id_ID')`). Password login lokal tidak disimpan di file ini — lihat `ouput/demo-accounts.local.md` atau `backend/.demo-credentials.local.txt` (keduanya ter-gitignore).

## 1. Jumlah Record Database `agroniaga_demo`

| Entitas / Tabel | Jumlah |
|---|---:|
| `mill_companies` | 5 |
| `mills` | 5 |
| `cooperatives` | 4 |
| `farmers` | 60 |
| `farms` | 75 |
| `vehicles` | 12 |
| `drivers` | 12 |
| `user_accounts` | 12 |
| `mill_price_quotes` | 20 |
| `disbun_reference_prices` | 3 |
| `trade_contracts` | 8 |
| `tbs_receipts` | 83 |
| `delivery_orders` | 18 |
| `mill_weighing_tickets` | 13 |
| `reconciliation_cases` | 10 |
| `farmer_settlement_allocations` | 5 |
| `invoices` | 7 |
| `payment_approvals` | 2 |
| `payment_records` | 1 |
| `audit_events` | 564 |

## 2. Daftar Akun Pengguna Demo (Tanpa Password)

| No | Username | Email | Display Name | Role | Scope | Target Scope | Status |
|---:|---|---|---|---|---|---|---|
| 1 | `demo_director_01` | `demo_director_01@demo.example.invalid` | Direksi Perumda (Approver) | `DIRECTOR` | `PERUMDA_GLOBAL` | `PERUMDA_GLOBAL` | `ACTIVE` |
| 2 | `demo_kop_op_01` | `demo_kop_op_01@demo.example.invalid` | Operator Koperasi #1 (Pelalawan Jaya) | `COOPERATIVE_OPERATOR` | `COOPERATIVE` | `KOP-DEMO-01` | `ACTIVE` |
| 3 | `demo_kop_op_02` | `demo_kop_op_02@demo.example.invalid` | Operator Koperasi #2 (Cross-Scope Ukui) | `COOPERATIVE_OPERATOR` | `COOPERATIVE` | `KOP-DEMO-02` | `ACTIVE` |
| 4 | `demo_mill_op_01` | `demo_mill_op_01@demo.example.invalid` | Petugas PKS #1 (PKS-DEMO-01) | `MILL_OPERATOR` | `MILL` | `PKS-DEMO-01` | `ACTIVE` |
| 5 | `demo_mill_op_02` | `demo_mill_op_02@demo.example.invalid` | Petugas PKS #2 (Cross-Mill PKS-DEMO-02) | `MILL_OPERATOR` | `MILL` | `PKS-DEMO-02` | `ACTIVE` |
| 6 | `demo_perumda_fin_01` | `demo_perumda_fin_01@demo.example.invalid` | Staf Keuangan Perumda #1 (Maker) | `PERUMDA_FINANCE` | `PERUMDA_GLOBAL` | `PERUMDA_GLOBAL` | `ACTIVE` |
| 7 | `demo_perumda_fin_02` | `demo_perumda_fin_02@demo.example.invalid` | Staf Keuangan Perumda #2 (Checker) | `PERUMDA_FINANCE` | `PERUMDA_GLOBAL` | `PERUMDA_GLOBAL` | `ACTIVE` |
| 8 | `demo_perumda_ops_01` | `demo_perumda_ops_01@demo.example.invalid` | Staf Operasional Perumda #1 (Maker) | `PERUMDA_OPERATIONS` | `PERUMDA_GLOBAL` | `PERUMDA_GLOBAL` | `ACTIVE` |
| 9 | `demo_perumda_ops_02` | `demo_perumda_ops_02@demo.example.invalid` | Staf Operasional Perumda #2 (Checker) | `PERUMDA_OPERATIONS` | `PERUMDA_GLOBAL` | `PERUMDA_GLOBAL` | `ACTIVE` |
| 10 | `demo_petani_01` | `demo_petani_01@demo.example.invalid` | Petani Swadaya #1 (Primer) | `FARMER` | `FARMER` | `PET-DEMO-001` | `ACTIVE` |
| 11 | `demo_petani_02` | `demo_petani_02@demo.example.invalid` | Petani Swadaya #2 (Cross-Scope) | `FARMER` | `FARMER` | `PET-DEMO-002` | `ACTIVE` |
| 12 | `demo_sys_admin_01` | `demo_sys_admin_01@demo.example.invalid` | Administrator Sistem (Non-Approver) | `SYSTEM_ADMIN` | `PERUMDA_GLOBAL` | `PERUMDA_GLOBAL` | `ACTIVE` |

## 3. Master Data PKS (`mills`), Koperasi (`cooperatives`), & Sampel Petani

### PKS Mitra (5 PKS)

| Kode PKS | Nama PKS | Kabupaten | Publik? | Koordinat | Status Kemitraan |
|---|---|---|---|---|---|
| `PKS-DEMO-01` | PKS Demo Pangkalan Kerinci Sejahtera | Pelalawan | `True` | `0.415200, 101.868400` | `ACTIVE` |
| `PKS-DEMO-02` | PKS Demo Langgam Jaya Lestari | Pelalawan | `True` | `0.289100, 101.732400` | `ACTIVE` |
| `PKS-DEMO-03` | PKS Demo Sorek Satu Utama | Pelalawan | `True` | `0.154800, 102.042100` | `ACTIVE` |
| `PKS-DEMO-04` | PKS Demo Ukui Mitra Mandiri | Pelalawan | `True` | `Belum terverifikasi / null` | `ACTIVE` |
| `PKS-DEMO-05` | PKS Demo Rahasia Internal | Pelalawan | `False` | `Belum terverifikasi / null` | `ACTIVE` |

### Koperasi Pemasok (4 Koperasi)

| Kode Koperasi | Nama Koperasi | Status |
|---|---|---|
| `KOP-DEMO-01` | KUD Demo Pelalawan Sawit Jaya | `ACTIVE` |
| `KOP-DEMO-02` | KUD Demo Ukui Tani Makmur | `ACTIVE` |
| `KOP-DEMO-03` | KUD Demo Sorek Harapan Bersama | `ACTIVE` |
| `KOP-DEMO-04` | KUD Demo Bunut Subur Mandiri | `ACTIVE` |

### Sampel Petani (60 total; 10 pertama)

| Kode Petani | Nama Petani (Sintetis) | Telepon Sintetis |
|---|---|---|
| `PET-DEMO-001` | Hasna Situmorang (Demo) | `0813-6501-8281` |
| `PET-DEMO-002` | Jagapati Sihotang (Demo) | `0813-6502-5105` |
| `PET-DEMO-003` | Ir. Teguh Padmasari, S.IP (Demo) | `0813-6503-1848` |
| `PET-DEMO-004` | Parman Hidayanto (Demo) | `0813-6504-5107` |
| `PET-DEMO-005` | Jasmani Kuswandari (Demo) | `0813-6505-3726` |
| `PET-DEMO-006` | Dinda Suwarno (Demo) | `0813-6506-1569` |
| `PET-DEMO-007` | Calista Zulaika (Demo) | `0813-6507-6455` |
| `PET-DEMO-008` | Tgk. Puti Napitupulu (Demo) | `0813-6508-1269` |
| `PET-DEMO-009` | Mahesa Napitupulu (Demo) | `0813-6509-7647` |
| `PET-DEMO-010` | Cindy Habibi, M.Kom. (Demo) | `0813-6510-1955` |

## 4. Harga Acuan Disbun & Kontrak Niaga (`trade_contracts`)

### Harga Acuan Dinas Perkebunan

| Kode Kategori | Kategori | Harga Acuan (Rp/kg) | Status |
|---|---|---:|---|
| `DISBUN_10_20` | Referensi Disbun Umur 10-20 Tahun | `2965.00` | `PUBLISHED` |
| `DISBUN_10_20` | Referensi Disbun Umur 10-20 Tahun | `2940.00` | `PUBLISHED` |
| `DISBUN_10_20` | Referensi Disbun Umur 10-20 Tahun | `2910.00` | `PUBLISHED` |

### Kontrak Niaga & Kuota (8 Kontrak)

| Nomor Kontrak | PKS | Model Usaha | Harga (Rp/kg) | Batas Kuota (kg) | Tercadang (kg) | Terealisasi (kg) | Status |
|---|---|---|---:|---:|---:|---:|---|
| `KTR-DEMO-DRF-08` | `PKS-DEMO-02` | `PRINCIPAL` | `2880.00` | `35000.000` | `0` | `0` | `DRAFT` |
| `KTR-DEMO-NEAR-02` | `PKS-DEMO-02` | `PRINCIPAL` | `2885.00` | `24000.000` | `10400.000` | `10400.000` | `ACTIVE` |
| `KTR-DEMO-PEND-07` | `PKS-DEMO-01` | `PRINCIPAL` | `2915.00` | `45000.000` | `0` | `0` | `PENDING_APPROVAL` |
| `KTR-DEMO-PRI-01` | `PKS-DEMO-01` | `PRINCIPAL` | `2910.00` | `120000.000` | `30450.000` | `33750.000` | `ACTIVE` |
| `KTR-DEMO-PRI-03` | `PKS-DEMO-03` | `PRINCIPAL` | `2870.00` | `80000.000` | `15100.000` | `17700.000` | `ACTIVE` |
| `KTR-DEMO-PRI-04` | `PKS-DEMO-04` | `PRINCIPAL` | `2850.00` | `60000.000` | `0` | `9250.000` | `ACTIVE` |
| `KTR-DEMO-PRIV-05` | `PKS-DEMO-05` | `PRINCIPAL` | `2990.00` | `40000.000` | `6000.000` | `0` | `ACTIVE` |
| `KTR-DEMO-UNC-06` | `PKS-DEMO-01` | `UNCONFIRMED` | `2890.00` | `50000.000` | `0` | `7200.000` | `ACTIVE` |

## 5. Delivery Orders (`delivery_orders`), Tiket Timbang PKS, & Rekonsiliasi

### Delivery Orders / e-DO (18 Transaksi)

| Nomor e-DO | PKS | Berat Asal (kg) | Status | QR Token Verifikasi |
|---|---|---:|---|---|
| `EDO-2026-1111-0001` | `PKS-DEMO-01` | `10350.000` | `RECEIVED` | `EDO-2026-1111-0001-96AA5625` |
| `EDO-2026-1111-0002` | `PKS-DEMO-01` | `6000.000` | `RECEIVED` | `EDO-2026-1111-0002-DD79B2A1` |
| `EDO-2026-1111-0003` | `PKS-DEMO-02` | `5200.000` | `RECEIVED` | `EDO-2026-1111-0003-C898A051` |
| `EDO-2026-1111-0004` | `PKS-DEMO-02` | `5200.000` | `RECEIVED` | `EDO-2026-1111-0004-9072C59F` |
| `EDO-2026-1111-0005` | `PKS-DEMO-01` | `7200.000` | `RECEIVED` | `EDO-2026-1111-0005-DC9FC265` |
| `EDO-2026-1111-0006` | `PKS-DEMO-03` | `8800.000` | `RECEIVED` | `EDO-2026-1111-0006-603C9D37` |
| `EDO-2026-1111-0007` | `PKS-DEMO-01` | `9400.000` | `RECEIVED` | `EDO-2026-1111-0007-698D5F3A` |
| `EDO-2026-1111-0008` | `PKS-DEMO-03` | `8900.000` | `RECEIVED` | `EDO-2026-1111-0008-8F270313` |
| `EDO-2026-1111-0009` | `PKS-DEMO-01` | `8000.000` | `RECEIVED` | `EDO-2026-1111-0009-4F1E8537` |
| `EDO-2026-1111-0010` | `PKS-DEMO-04` | `9250.000` | `RECEIVED` | `EDO-2026-1111-0010-1EF90E9C` |
| `EDO-2026-1111-0011` | `PKS-DEMO-02` | `5200.000` | `ARRIVED` | `EDO-2026-1111-0011-0B8F4E07` |
| `EDO-2026-1111-0012` | `PKS-DEMO-05` | `6000.000` | `ARRIVED` | `EDO-2026-1111-0012-0219F16C` |
| `EDO-2026-1111-0013` | `PKS-DEMO-01` | `9800.000` | `ARRIVED` | `EDO-2026-1111-0013-64CAD21B` |
| `EDO-2026-1111-0014` | `PKS-DEMO-02` | `5200.000` | `ARRIVED` | `EDO-2026-1111-0014-8373031E` |
| `EDO-2026-1111-0015` | `PKS-DEMO-01` | `10050.000` | `IN_TRANSIT` | `EDO-2026-1111-0015-7E2EE064` |
| `EDO-2026-1111-0016` | `PKS-DEMO-03` | `15100.000` | `IN_TRANSIT` | `EDO-2026-1111-0016-895714D2` |
| `EDO-2026-1111-0017` | `PKS-DEMO-01` | `10600.000` | `READY` | `EDO-2026-1111-0017-872FE7FC` |
| `EDO-2026-1111-0018-DRAFT` | `PKS-DEMO-01` | `9300.000` | `DRAFT` | `-` |

### Tiket Timbang PKS (13 Record termasuk Revisi)

| No. Tiket | Rev | Current? | Nomor e-DO | Bruto / Tara / Netto (kg) | Status |
|---|---:|---|---|---|---|
| `WB-DEMO-001` | 1 | `False` | `EDO-2026-1111-0001` | `18767.200` / `8500.000` / `10267.200` | `SUBMITTED` |
| `WB-DEMO-001` | 2 | `True` | `EDO-2026-1111-0001` | `18782.200` / `8500.000` / `10282.200` | `VERIFIED` |
| `WB-DEMO-002` | 1 | `True` | `EDO-2026-1111-0002` | `14452.000` / `8500.000` / `5952.000` | `VERIFIED` |
| `WB-DEMO-003` | 1 | `True` | `EDO-2026-1111-0003` | `13658.400` / `8500.000` / `5158.400` | `VERIFIED` |
| `WB-DEMO-004` | 1 | `True` | `EDO-2026-1111-0004` | `13658.400` / `8500.000` / `5158.400` | `VERIFIED` |
| `WB-DEMO-005` | 1 | `True` | `EDO-2026-1111-0005` | `15642.400` / `8500.000` / `7142.400` | `VERIFIED` |
| `WB-DEMO-006` | 1 | `True` | `EDO-2026-1111-0006` | `17229.600` / `8500.000` / `8729.600` | `VERIFIED` |
| `WB-DEMO-007` | 1 | `True` | `EDO-2026-1111-0007` | `18220.000` / `8500.000` / `9720.000` | `VERIFIED` |
| `WB-DEMO-008` | 1 | `True` | `EDO-2026-1111-0008` | `16972.800` / `8500.000` / `8472.800` | `VERIFIED` |
| `WB-DEMO-009` | 1 | `True` | `EDO-2026-1111-0009` | `16220.000` / `8500.000` / `7720.000` | `VERIFIED` |
| `WB-DEMO-010` | 1 | `True` | `EDO-2026-1111-0010` | `17454.000` / `8500.000` / `8954.000` | `VERIFIED` |
| `WB-DEMO-011` | 1 | `True` | `EDO-2026-1111-0011` | `13658.400` / `8500.000` / `5158.400` | `SUBMITTED` |
| `WB-DEMO-012` | 1 | `True` | `EDO-2026-1111-0012` | `14452.000` / `8500.000` / `5952.000` | `SUBMITTED` |

### Kasus Rekonsiliasi (10 Kasus)

| Nomor e-DO | Berat Asal (kg) | Berat PKS (kg) | Selisih (%) | Selisih Negatif? | Status |
|---|---:|---:|---:|---|---|
| `EDO-2026-1111-0001` | `10350.000` | `10282.200` | `0.6551%` | `False` | `MATCHED` |
| `EDO-2026-1111-0002` | `6000.000` | `5952.000` | `0.8000%` | `False` | `MATCHED` |
| `EDO-2026-1111-0003` | `5200.000` | `5158.400` | `0.8000%` | `False` | `MATCHED` |
| `EDO-2026-1111-0004` | `5200.000` | `5158.400` | `0.8000%` | `False` | `MATCHED` |
| `EDO-2026-1111-0005` | `7200.000` | `7142.400` | `0.8000%` | `False` | `MATCHED` |
| `EDO-2026-1111-0006` | `8800.000` | `8729.600` | `0.8000%` | `False` | `MATCHED` |
| `EDO-2026-1111-0007` | `9400.000` | `9720.000` | `-3.4043%` | `True` | `DISPUTE_HOLD` |
| `EDO-2026-1111-0008` | `8900.000` | `8472.800` | `4.8000%` | `False` | `DISPUTE_HOLD` |
| `EDO-2026-1111-0009` | `8000.000` | `7720.000` | `3.5000%` | `False` | `UNDER_REVIEW` |
| `EDO-2026-1111-0010` | `9250.000` | `8954.000` | `3.2000%` | `False` | `RESOLVED` |

## 6. Faktur AR/AP & Pembayaran Simulasi

### Faktur Keuangan (7 Record)

| Nomor Faktur | Jenis | Model Usaha | Kebijakan | Total (Rp) | Status |
|---|---|---|---|---:|---|
| `INV-AP-202611-00002` | `ACCOUNTS_PAYABLE` | `PRINCIPAL` | `PENDING_SOP` | `29921202.00` | `ISSUED` |
| `INV-AP-202611-00004` | `ACCOUNTS_PAYABLE` | `PRINCIPAL` | `PENDING_SOP` | `17320320.00` | `ISSUED` |
| `INV-AP-202611-00005` | `ACCOUNTS_PAYABLE` | `PRINCIPAL` | `PENDING_SOP` | `14881984.00` | `ISSUED` |
| `INV-AR-202611-00001` | `ACCOUNTS_RECEIVABLE` | `PRINCIPAL` | `PENDING_SOP` | `29921202.00` | `ISSUED` |
| `INV-AR-202611-00003` | `ACCOUNTS_RECEIVABLE` | `PRINCIPAL` | `PENDING_SOP` | `17320320.00` | `ISSUED` |
| `INV-AR-202611-00006` | `ACCOUNTS_RECEIVABLE` | `PRINCIPAL` | `PENDING_SOP` | `25940700.00` | `PENDING_VERIFICATION` |
| `INV-AR-202611-00007` | `ACCOUNTS_RECEIVABLE` | `UNCONFIRMED` | `PENDING_SOP` | `20641536.00` | `PENDING_VERIFICATION` |

### Catatan Pembayaran Simulasi

| Nomor Bayar | Arah | Nominal (Rp) | Referensi Simulasi | Status |
|---|---|---:|---|---|
| `PAY-OUT-202611-00001` | `OUTBOUND` | `17320320.00` | `SIM-DEMO-TRF-0002` | `VERIFIED` |
