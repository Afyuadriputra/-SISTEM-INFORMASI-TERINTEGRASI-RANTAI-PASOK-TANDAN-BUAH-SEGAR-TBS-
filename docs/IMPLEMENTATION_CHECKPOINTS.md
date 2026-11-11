# IMPLEMENTATION CHECKPOINTS — Rantai Pasok TBS Perumda Tuah Sekata (Unit Agro Niaga)

> **Catatan Tata Kelola Dokumen:** Dokumen ini mencatat progres checkpoint verifikasi desain dan handoff implementasi secara terpisah agar **6 dokumen baseline V1.1** (`PRD.md`, `TRD.md`, `AFD.md`, `DBD.md`, `BSD.md`, dan `IPD.md`) tetap murni sebagai sumber kebutuhan dan *master implementation plan* tanpa perubahan untuk pencatatan progres rutin.
> Seluruh angka dan aturan bisnis yang belum disahkan Perumda tetap ditandai **`Data Simulasi`**, **`Aturan Simulasi`**, atau **`Pending SOP`** (`AFD §41`).

---

## Ringkasan Status Lintas Checkpoint

| Checkpoint | Fase | Status Aktual | Tanggal / Referensi | Ringkasan Hasil |
| :--- | :--- | :--- | :--- | :--- |
| **D4** | Design Verification & Audit | `CONDITIONALLY_READY — DESIGN_FIXES_PENDING` | 2026-11-10 ([design-verification-signoff-report.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/design-verification-signoff-report.md)) | Perbaikan temuan kritis awal (kontras sidebar `#B8C7BE`, privasi pencarian publik, `2105` Detail PKS `/pks/:id`, `2153` Logistik, `2009` 15-State Matrix, `W03.2B`/`W04.2B`, token Tailwind v4); 6 rute mandiri & 2 form master data masih terbuka untuk ditutup di D5. |
| **D5** | Design Gap Closure & Final Sign-Off | **`READY — FIGCRAFT_DESIGN_SIGNOFF`** | 2026-11-10 ([d5-design-gap-closure-signoff.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/d5-design-gap-closure-signoff.md)) | **26/26 (100%)** cakupan rute mandiri `AFD §36`, form penuh `FLOW-05` & `FLOW-06`, refactor `Organism/InternalSidebar #275` pada seluruh 21 layar internal desktop, 14 prototype flow penuh (`215` interaksi, `0` dangling), 7 layar bisnis mobile prioritas, `0/1451` gagal kontras WCAG, `0` missing font, dan `50` board/frame `readyForDev`. |
| **M0** | Requirements & Contract Alignment | **`READY — M0_CONTRACT_ALIGNMENT_VERIFIED`** | 2026-11-10 ([M0_CONTRACT_VALIDATION_REPORT.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/m0/M0_CONTRACT_VALIDATION_REPORT.md)) | `openapi.v1.yaml` (`75` paths, `95` ops, `191` schemas), `error-catalog.yaml` (`69` kode error), `state-catalog.yaml` (`11` mesin state, `41` transisi), `role-permissions.yaml` (`PUBLIC` + `7` peran, `64` permissions, `1:1` OpenAPI), `11` fixture JSON (`22` skenario negatif), `ADR-001..010`, traceability lengkap, dan `10/10` cek validasi `K1–K10` lulus (`0` issue). |
| **M0.1** | Final Handoff Consistency Patch | **`READY — M0_HANDOFF_CONSISTENCY_VERIFIED`** | 2026-11-10 ([M0_CHANGELOG.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/m0/M0_CHANGELOG.md)) | Penyelarasan akhir pra-B0/F0: `TanStack Router`, 48 nama tabel kanonis `DBD §4`, breakdown `95` operasi (`2` health / `7` public / `4` auth / `82` internal = `84` authenticated), `8` operasi wajib `Idempotency-Key`, `M0-CNF-05 = RESOLVED`, arah dependency Clean Architecture 4 layer (`ADR-002`), & struktur `B0` inkremental tanpa folder kosong (`ADR-001`). |
| **B0–B11** | Full Backend Implementation | **`BACKEND_INDEPENDENT_READY`** (`B0–B11 PASS`) | 2026-11-11 (`main @ 0243982`) | Seluruh `B0–B11` PASS (`11` modul domain + `core/` Clean Architecture 4 layer, `11` migrasi Alembic `0001..0011`, `95/95` operasi OpenAPI `1:1`, `69` kode error & `22` skenario negatif, `EXPLAIN ANALYZE` 0.02–0.60 ms, `pg_dump`/`pg_restore` 48 tabel terverifikasi, `import-linter` `16 kept, 0 broken`, `pyright` `0` error, `ruff` bersih, dan `pytest` **`76/76 passed`**). Siap lanjut integrasi Frontend `F0–F11`. |
| **B11.1** | Post-Implementation Verification | **`READY — B11_1_POST_IMPLEMENTATION_VERIFIED`** | 2026-11-11 (`main @ 1b70664` + audit fixes) | Verifikasi independen pasca-B11: `48` tabel PG16 terekonsiliasi (`46` DBD §4 + `contract_approval_events` + `alembic_version`; `2` deferred), **`95/95` operasi OpenAPI teruji live HTTP `2xx` + `0` error JSON Schema Draft 2020-12** (pasca-perbaikan 16 envelope `meta: SimpleSuccessMeta`), perbaikan **N+1** list DO & Rekonsiliasi (`O(1)` query) + deterministic ordering alokasi, benchmark lokal `errors=0`, `import-linter` `16 kept`, `pyright` `0` error, `ruff` bersih, `pytest` **`77/77 passed`**, & kontrak `11/11` PASS. |
| **F0** | Frontend Foundation | **`PASS — F0_FOUNDATION_VERIFIED`** | 2026-11-11 (`frontend/`) | React 19 + Vite 8 + TypeScript 5.9 `strict: true`, Tailwind v4 tokens D5 (`tokens.css`), `openapi-typescript` codegen dari `openapi.v1.yaml` (`generated.d.ts`), `decimal.js`, `69` kode error kanonis, TanStack Router (`26/26` rute `AFD §36`), TanStack Query + CSRF/Idempotency client, dan MSW `v3` berbasis `contracts/fixtures/*.json`. `tsc -b`, `eslint`, `vitest` (`7/7` PASS), & `vite build` lulus. |
| **F1** | Design System & Component Library | **`PASS — F1_DESIGN_SYSTEM_VERIFIED`** | 2026-11-11 (`frontend/`) | Implementasi 5 tingkat Atomic Design (`atoms/`, `molecules/`, `organisms/`, `templates/`) selaras FigCraft D5 (`#14452F`, `#12231B`, `#F8F7F4`, Open Sans & Cascadia Mono subset `latin`), `WeightInputGroup` real-time `Decimal`, `StatusIndicator` seluruh 11 mesin state `SM-01..SM-11`, `ConfirmDialog` dengan Escape & alasan wajib, `DataTable` scroll-safe, `StateFeedbackCard` dengan `request_id`. `tsc -b`, `eslint`, `vitest` (`12/12` PASS), & `vite build` (`985ms`) lulus. |
| **F2** | Portal Publik (7 Rute Publik) | **`PASS — F2_PUBLIC_PORTAL_VERIFIED`** | 2026-11-11 (`frontend/`) | Seluruh 7 rute publik (`/`, `/harga-tbs`, `/pks/:id`, `/lokasi-pks`, `/tentang`, `/kemitraan`, `/kontak`) terhubung ke API kontrak via React Query + MSW, pemisahan Disbun vs PKS (`BR-004`), filter harga & status kedaluwarsa, isolasi PKS privat `404` (`BR-PUB-004`), lazy `maplibre-gl` hanya untuk koordinat terverifikasi tanpa pin palsu, & `0` kebocoran PII petani. `tsc -b`, `eslint`, `vitest` (`16/16` PASS), & `vite build` (`1.71s`) lulus. |
| **F3** | Autentikasi, Sesi & App Shell | **`PASS — F3_AUTH_SHELL_VERIFIED`** | 2026-11-11 (`frontend/`) | Halaman `/login` (React Hook Form + Zod, toggle sandi, CSRF attach/refresh, penolakan generik `401 AUTH_INVALID_CREDENTIALS`, helper simulasi khusus `mock` mode yang nonaktif di `real`), pengalihan anonim `/app/* -> /login?next=...`, penegakan RBAC `403 AUTH_ACCESS_DENIED`, label `Non-Approver (BR-SYS-002)` pada sidebar admin, & pembilasan cache saat logout. `tsc -b`, `eslint`, `vitest` (`19/19` PASS), & `vite build` (`1.69s`) lulus. |
| **F4** | Master Data UI (`FLOW-05`, `FLOW-06`) | **`PASS — F4_MASTER_DATA_VERIFIED`** | 2026-11-11 (`frontend/`) | Form & daftar lengkap `/app/koperasi` (`FLOW-05` petani/kebun cakupan koperasi + armada) dan `/app/perumda` (`FLOW-06` master PKS + persetujuan eksplisit `is_public`), validasi koordinat berpasangan, nonaktif beraudit alasan wajib (`BR-023`), & optimistic locking `version`. `tsc -b`, `eslint`, `vitest` (`21/21` PASS), & `vite build` (`1.45s`) lulus. |
| **F5** | Manajemen Harga Multi-PKS | **`PASS — F5_PRICING_VERIFIED`** | 2026-11-11 (`frontend/`) | Implementasi `/app/perumda/harga` (`FLOW-07..08`): siklus `DRAFT -> PENDING_VERIFICATION -> VERIFIED -> PUBLISHED / REVOKED`, pemisahan tugas `Maker != Checker` (`403 AUTH_CONFLICT_OF_DUTIES`), modal penolakan/pencabutan beralasan audit wajib, dan pemisahan harga acuan Disbun (`BR-004`). `tsc -b`, `eslint`, `vitest` (`22/22` PASS), & `vite build` (`1.39s`) lulus. |
| **F6** | Penerimaan, Timbang & Grading | **`PASS — F6_RECEIVING_GRADING_VERIFIED`** | 2026-11-11 (`frontend/`) | Implementasi `/app/koperasi/penerimaan`: buat draf idempoten (`Idempotency-Key`), `WeightInputGroup` real-time `Decimal` Netto dengan penolakan `Tara > Bruto`, grading terpisah berlabel `Aturan Simulasi` (`BSD §9.3`), validasi, pembatalan beralasan audit, & kunci otomatis penerimaan berstatus `ALLOCATED`/`SHIPPED`. `tsc -b`, `eslint`, `vitest` (`23/23` PASS), & `vite build` (`2.27s`) lulus. |
| **F7** | Kontrak, Kuota & Logistik e-DO | **`PASS — F7_CONTRACTS_LOGISTICS_VERIFIED`** | 2026-11-11 (`frontend/`) | Implementasi `/app/perumda/kontrak`, `/app/koperasi/surat-jalan`, & `/app/perumda/logistik`: pembuatan kontrak + model usaha `Pending SOP`, reservasi kuota idempoten anti-over-quota (`409 CONTRACT_QUOTA_EXCEEDED`), konsolidasi e-DO multi-petani dengan proteksi `LOG_DELIVERY_ALREADY_ASSIGNED`, QR token terkendali, & penegakan RBAC `contracts.read` koperasi. `tsc -b`, `eslint`, `vitest` (`25/25` PASS), & `vite build` (`1.49s`) lulus. |
| **F8** | Timbang PKS & Rekonsiliasi Berat | **`PASS — F8_MILL_RECONCILIATION_VERIFIED`** | 2026-11-11 (`frontend/`) | Implementasi `/app/pks`, `/app/pks/tiket-timbang` (Pendekatan A manual terverifikasi, isolasi `MILL_EDO_MILL_MISMATCH`, anti-duplikat tiket, unggah bukti `/files`), & `/app/perumda/rekonsiliasi` (toleransi simulasi `1,5000%`, penandaan wajib `ANOMALY_NEGATIVE_DIFFERENCE`, dispute review/resolve beraudit, simulasi alokasi `30/20/50%` vs blokir `FINAL` `409 REC_ALLOCATION_POLICY_UNCONFIRMED`). `tsc -b`, `eslint`, `vitest` (`27/27` PASS), & `vite build` (`1.29s`) lulus. |
| **F9** | Keuangan, Faktur, Pembayaran, Direksi & Petani | **`PASS — F9_FINANCE_APPROVAL_VERIFIED`** | 2026-11-11 (`frontend/`) | Implementasi `/app/perumda/pembayaran` (invoice AR, pembayaran ke petani & verifikasi Maker!=Checker idempoten, AP PKS terpisah + status `Pending SOP`, blokir `FIN_PAYMENT_DOUBLE_DISBURSEMENT`), `/app/direksi/persetujuan` (approval Direksi terpisah dari operator & Non-Approver `SYSTEM_ADMIN`), & `/app/petani`, `/app/petani/panen` (`FARMER` read-only terisolasi `own_scope`). `tsc -b`, `eslint`, `vitest` (`29/29` PASS), & `vite build` (`1.70s`) lulus. |
| **F10** | Dashboard Analitik & Portal Admin Sistem | **`PASS — F10_DASHBOARDS_ADMIN_VERIFIED`** | 2026-11-11 (`frontend/`) | Melengkapi 4 rute tersisa sehingga **26/26 rute kanonis AFD §36** hidup penuh tanpa stub: `/app/direksi` (label wajib `Kontribusi Kotor (Simulasi) != Laba Bersih` `BR-MRG-005` & pemisahan kas/AR/AP), `/app/admin` (CCTV Digital `Request ID`, `/health/ready`, Redis hit ratio tanpa nominal keuangan), `/app/admin/pengguna` (`Non-Approver BR-SYS-002`, pencabutan sesi instan, aturan berversi append-only), & `/app/admin/audit` (audit append-only teredaksi). `tsc -b`, `eslint`, `vitest` (`32/32` PASS), & `vite build` (`1.45s`) lulus. |
| **F11** | Hardening, Live FastAPI E2E & Sign-Off | **`READY — FRONTEND_BACKEND_INTEGRATION_VERIFIED`** (`F0–F11 PASS`) | 2026-11-11 (`frontend/` + FastAPI PG 16.15/Redis) | Verifikasi live end-to-end (`VITE_API_MODE=real` tanpa MSW) melalui Vite `:5173` -> FastAPI Uvicorn `:8000` -> PostgreSQL 16.15 (`127.0.0.1:15432`) & Redis 7: Playwright Chromium `2/2` PASS (7 rute publik, auth cookie+CSRF, reload session, `SYSTEM_ADMIN Non-Approver` + rule versioning, Koperasi timbang->validasi->e-DO, & Direksi `BR-MRG-005`), responsif `1440px`/`375px` (`0` overflow), **`axe-core` WCAG 2.2 AA (`0` critical/serious)**, visual QA vs FigCraft D5, `VITE_API_MODE=real` build (`1.54s`, MSW tree-shaken keluar), antislop `0` temuan kode, `vitest` `11/11` (`32/32` PASS), & regresi backend `pytest` **`77/77 passed`**. |
| **F11.1** | Final Frontend UAT & Integration Verification | **`READY — F11_1_FULL_INTEGRATION_AND_UX_VERIFIED`** (`F0–F11.1 PASS`) | 2026-11-11 (`frontend/` + live FastAPI/PG 16.15/Redis `/1`) | Audit UAT final terhadap FastAPI live + `agroniaga_test` PostgreSQL 16.15 (`127.0.0.1:15432`, rev `0011_b10_reporting_indexes`) + Redis `/1` tanpa mengubah `backend/`, kontrak bisnis, dokumen `V1.1`, maupun `agroniaga_dev`. Menutup 9 temuan integrasi/UX/a11y nyata (`PerumdaFinancePage` status `PENDING_VERIFICATION` + indikator/disable upload bukti + guard UUID mock, `MillTicketsPage` status `SUBMITTED` + `is_current`, `PerumdaReconciliationPage` trigger `REC-01` `POST /api/v1/reconciliations`, `KoperasiSuratJalanPage` opsi `__CUSTOM__` multi-kontrak, `logisticsApi` `useDeliveryOrders(filters, enabled)`, `PublicNavbar`/`InternalSidebar`/`ConfirmDialog` keyboard `Escape` + focus restoration + `activeOptions` exact-match `aria-current="page"`, serta `DataTable`/`AdminPenggunaPage` `tabIndex={0}` `role="region"` WCAG 2.2 AA + `min-w-0` grid mobile `390px`). Clean-room `npm.cmd run test:e2e`: **11/11 PASS (`4.2m`)** mencakup matriks 7 peran RBAC, **26 rute x 5 viewport (`1440/1280/768/390/375`, `0` overflow)**, `axe-core` WCAG 2.2 AA (`0` critical/serious), & Workflow A-F lengkap; `tsc -b`, `eslint`, `vitest` (`11/11`, `32/32`), `vite build` mode `real` (`2.00s`, `0` aset MSW), validator `K1-K11` (`13/13` unit test OK), & backend `pytest` **`77/77 passed`**. |
| **LOCAL-DEMO-01** | Real API + Faker Seed + One-Command Launch | **`READY — LOCAL_DEMO_REAL_API_VERIFIED`** (`F0–F11.1 + Demo`) | 2026-11-11 (`scripts/` + `backend/scripts/seed_demo.py`) | Lingkungan demo lokal terisolasi penuh: DB PostgreSQL **`agroniaga_demo`** (port `15432`, rev `0011_b10_reporting_indexes`) + **Redis `/2`**, seeder `Faker(id_ID)` deterministik & idempoten (`DEMO_SEED=20261111`), **12** akun demo 7 peran (kredensial lokal ter-gitignore pada `backend/.demo-credentials.local.txt`), indikator **`MODE DEMO — DATA SINTETIS`** (`VITE_DEMO_BANNER=true`, `VITE_API_MODE=real`, `0` chunk MSW), skrip launcher Windows (`.\scripts\demo-setup.ps1`, `.\scripts\demo-start.ps1`, `.\scripts\demo-stop.ps1`), & uji E2E live **7 peran + UI -> API -> PostgreSQL persistence across reload PASS (`2/2`)** sementara `agroniaga_dev`, `agroniaga_test`, Redis `/0`/`/1`, & proses pengguna lain tetap utuh. |

---

## Checkpoint M0 — Requirements & Contract Alignment

### 1. Status & Ringkasan Penutupan M0
- **Current Milestone:** `M0 — Requirements & Contract Alignment`
- **Status Akhir M0:** **`READY — M0_CONTRACT_ALIGNMENT_VERIFIED`**
- **Baseline Git Commit:** `b081695` (`branch: main`)
- **Tanggal Penutupan M0:** `2026-11-10`
- **Objective:** Menyusun fondasi kontrak tunggal (*Contract-First, One Source of Truth*) bagi backend FastAPI dan frontend React + TypeScript berdasarkan 6 dokumen V1.1 dan hasil D5 FigCraft tanpa menulis kode runtime ataupun mengubah dokumen baseline V1.1.
- **Batasan & Keputusan `PENDING_SOP` Tetap Dipertahankan:**
  - Keputusan `BSD-DEC-001..020` & `AFD §41` (`SOP-01..15`) tetap ditandai `CONFIRMED` / `SIMULATION_ONLY` / `PENDING_SOP` / `FUTURE` (khususnya `business_model_code = UNCONFIRMED` yang memblokir finalisasi keuangan nyata via `409 FIN_POLICY_UNCONFIRMED`, toleransi `1,5%` simulasi, grading `2%` simulasi, dan alokasi multi-petani).
  - Tidak ada berkas pada `backend/`, `frontend/`, `alembic/`, `infra/`, `.figcraft`, `tokens.*`, maupun keenam dokumen baseline V1.1 yang dimodifikasi.

### 2. Status Unit Kerja M0
| Unit Kerja | Ruang Lingkup | Status |
| :--- | :--- | :--- |
| `M0-A Documentation` | Discovery, pembacaan penuh 6 dokumen V1.1, D4/D5 FigCraft, & `M0_DOCUMENT_AUDIT.md` | `PASS` |
| `M0-B Domain Alignment` | Inventaris 11 modul, konflik `CNF-01..10`, `M0_DECISION_REGISTER.md`, & `ADR-001..010` | `PASS` |
| `M0-C OpenAPI` | `contracts/openapi.v1.yaml` (OpenAPI `3.1.0`, `75` paths, `95` operations, `191` schemas) | `PASS` |
| `M0-D State Catalog` | `contracts/state-catalog.yaml` (`11` mesin state persisten vs turunan/UI, `41` transisi) | `PASS` |
| `M0-E Error Catalog` | `contracts/error-catalog.yaml` (`69` kode `MODULE_CATEGORY_DESCRIPTION`, HTTP map, `retryable`) | `PASS` |
| `M0-F Role/Permission` | `contracts/role-permissions.yaml` (`PUBLIC` + `7` peran, `4` scopes, `SOD-01..06`, `BR-SYS-002`) | `PASS` |
| `M0-G Fixtures` | `contracts/fixtures/*.json` (`11` dataset deterministik, `22` skenario negatif) + `README.md` | `PASS` |
| `M0-H Validation` | `contracts/scripts/validate_contracts.py` + `contracts/tests/test_contracts.py` (`K1–K10`: `0` issues) & `M0_CONTRACT_VALIDATION_REPORT.md` | `PASS` |
| `M0-I Final Handoff` | `M0_REQUIREMENT_TRACEABILITY.md`, `M0_CHANGELOG.md`, `M0_HANDOFF.md`, & checkpoint sign-off | `PASS` |

### 3. Pengujian & Verifikasi yang Dijalankan
- `python contracts/scripts/validate_contracts.py` -> `PASS` (`K1`–`K11` lulus seluruhnya, `TOTAL ISSUES: 0`).
- `python -m unittest discover -s contracts/tests -v` -> `PASS` (`11` test cases `test_k1`..`test_k11` OK).
- `npx --yes openapi-typescript contracts/openapi.v1.yaml -o <tmpdir>/openapi-types.d.ts` -> `exit code 0` (bagian terverifikasi dari `K8`).

### 4. Artefak M0 & Langkah Berikutnya
- **Artefak Kontrak (`contracts/`):** `openapi.v1.yaml`, `error-catalog.yaml`, `state-catalog.yaml`, `role-permissions.yaml`, `fixtures/README.md`, `fixtures/*.json` (`11` berkas), `scripts/validate_contracts.py`, `tests/test_contracts.py`.
- **Artefak Dokumentasi M0 (`docs/m0/` & `docs/adr/`):** `M0_DOCUMENT_AUDIT.md`, `M0_DECISION_REGISTER.md`, `M0_REQUIREMENT_TRACEABILITY.md`, `M0_CONTRACT_VALIDATION_REPORT.md`, `M0_CHANGELOG.md`, `M0_HANDOFF.md`, serta `ADR-001`..`ADR-010` + `docs/adr/README.md`.
- **Langkah Berikutnya (Sesuai IPD V1.1, Belum Dieksekusi pada M0/M0.1):**
  1. Memulai paralelisme terkendali pada **Backend Track `B0 — Project Foundation`** (`main.py` + `core/` untuk DB/Alembic & Redis fail-closed, Request ID, global error handler, `/health/live` & `/health/ready`, architecture/infra tests — **tanpa scaffolding puluhan folder kosong modul**; modul ditambah inkremental mulai `B1` dengan 4 layer wajib `ADR-002`) dan **Frontend Track `F0 — Project Foundation`** (React + Vite + TypeScript strict + Tailwind v4 token D5 + **`TanStack Router`** 26 rute `AFD §36` + TanStack Query + `openapi-typescript` codegen).
  2. Seluruh pengembang/agent track wajib merujuk `docs/m0/M0_HANDOFF.md` serta menjaga suite `K1–K11` tetap hijau sebelum pengajuan perubahan kontrak.

---

## Checkpoint M0.1 — Final Handoff Consistency Patch

- **Status Akhir M0.1:** **`READY — M0_HANDOFF_CONSISTENCY_VERIFIED`** (`2026-11-10`)
- **Ringkasan Koreksi yang Diverifikasi & Ditutup:**
  1. **Router Frontend:** Ditegaskan **`TanStack Router`** di [`M0_HANDOFF.md`](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/m0/M0_HANDOFF.md) & checkpoint ini (selaras `TRD §3, §17` & `ADR-006`).
  2. **Nama Entitas DBD (`48/48`):** Dikoreksi pada [`M0_REQUIREMENT_TRACEABILITY.md`](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/m0/M0_REQUIREMENT_TRACEABILITY.md) (`user_accounts`, `user_role_grants`, `receipt_weighing_revisions`, `delivery_order_lines`, `delivery_status_events`) serta seluruh 48 tabel `DBD §4` terindeks lengkap sesuai `DBD §4.11`.
  3. **Hitungan Operasi OpenAPI (`95` ops):** Dikoreksi pada handoff & laporan (`2` health + `7` public + `2` auth bootstrap + `2` auth session + `82` internal bisnis/admin = `11` bebas login & `84` terautentikasi).
  4. **Idempotency Operations (`8` ops):** Diselaraskan pada [`ADR-010`](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-010-idempotency-concurrency-pending-sop.md), `M0_DECISION_REGISTER.md` (`M0-TECH-07`), traceability, & handoff untuk 8 operasi wajib `Idempotency-Key` (mewakili 7 kategori proses kritis `BSD §27.2`).
  5. **Konsistensi Register (`M0-CNF-05`):** Diseragamkan **`RESOLVED`** di [`M0_DOCUMENT_AUDIT.md`](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/m0/M0_DOCUMENT_AUDIT.md), `M0_DECISION_REGISTER.md`, dan `M0_CHANGELOG.md`.
  6. **Clean Architecture & Struktur Solo Dev:** Penegasan [`ADR-001`](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-001-modular-monolith.md) & [`ADR-002`](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-002-four-layer-clean-architecture.md) (4 layer per modul inkremental, dependency ke dalam via port & composition root wiring, bebas subfolder kosong di `B0`).
  7. **Regresi Otomatis M0.1:** Suite `K1–K11` (`python contracts/scripts/validate_contracts.py` & `python -m unittest discover -s contracts/tests -v`) berjalan penuh dan lulus (`0` issue).

---

## Checkpoint D4 — Design Verification

### 1. Status & Cakupan Awal
- **Status Akhir D4:** `CONDITIONALLY_READY — DESIGN_FIXES_PENDING`
- **File Desain:** `D:\figcraft\test-output\agroniaga-tbs-perumda-tuah-sekata.figcraft`
- **Token Ekspor:** `D:\figcraft\test-output\tokens.tailwind.css` & `D:\figcraft\test-output\tokens.json`

### 2. Perbaikan yang Diselesaikan pada D4
- **Privasi Data Publik (`BR-PUB-001..005`):** Membersihkan kebocoran pencarian PKS/koperasi pada komponen pencarian publik (`#209`, `#490`, `#626`) agar portal publik hanya mengekspos data publik terkurasi.
- **Kontras Sidebar Internal:** Memperbarui warna teks/ikon menu pada 15 layar internal gelap menjadi `#B8C7BE` (rasio `9.32:1`, WCAG AAA terhadap latar gelap).
- **Rute & Modul Tambahan:** Menambahkan frame `/pks/:id` (`id: 2105` di Page 4), `/app/perumda/logistik` (`id: 2153` di Page 8), shell Tablet (`768px`, `id: 830`) & Mobile (`375px`/`390px`, `id: 837`), matriks `15` variasi state (`id: 2009`), serta dialog konfirmasi `W03.2B` / `W04.2B`.
- **Token Semantic Refactors:** Memperbarui 6 penamaan semantic token agar kompatibel dengan Tailwind v4 `@theme static`.

### 3. Gap Terbuka Hasil D4 (Menjadi Target Wajib D5)
1. **6 Rute Mandiri `AFD §36` masih terkompresi dalam frame komposit / belum memiliki layar desktop `1440px` mandiri:** `/tentang`, `/kemitraan`, `/kontak` (`P06–P08` di frame komposit `645`), `/app/perumda`, `/app/direksi/persetujuan`, dan `/app/admin`. (Serta resolusi tabrakan koordinat antara `645` dan `2105` di Page 4).
2. **Form `FLOW-05` & `FLOW-06` Belum Lengkap:** Belum memiliki alur penuh validasi `422`, error konflik `409`, konfirmasi `Organism/ConfirmDialog`, dan feedback sukses untuk Master Data Petani/Kebun (`FLOW-05`) serta Master Data PKS & publikasi `is_public` (`FLOW-06`).
3. **Adopsi Komponen Atomic Design Lokal:** `Organism/InternalSidebar #275` belum menggantikan sidebar lokal pada 16 layar internal sebelumnya, dan `Molecule/WeightInputGroup #227` belum terpasang langsung pada layar penimbangan mobile prioritas.
4. **Prototype Antar-Portal Terpotong & Penempatan Page 1:** Sebagian flow belum menghubungkan rute baru dan beberapa flow masih menempel di Page 1 alih-alih halaman portalnya masing-masing.
5. **Layar Bisnis Mobile Prioritas (`390px`/`375px`):** Layar operasional inti masih terlalu bergantung pada shell mobile generik (`837`).

---

## Checkpoint D5 — Design Gap Closure & Final Sign-Off

### 1. Status Aktual
- **Status Akhir D5:** **`READY — FIGCRAFT_DESIGN_SIGNOFF`**
- **Cakupan Rute Mandiri terhadap `AFD §36`:** **`26 / 26` rute (`100%`)** tersedia sebagai frame desktop `1440px` mandiri beserta label rute/role eksplisit dan tanpa ketergantungan pada frame komposit lama (`id: 645` dipindahkan ke arsip `(0, 2250)` dengan `devStatus: "none"`).

### 2. Screen & Form yang Diselesaikan pada D5

#### A. Enam Rute Desktop `1440px` Mandiri Baru
| Rute `AFD §36` | Node ID | Page | Koordinat & Ukuran | Ringkasan Isi & Kepatuhan V1.1 |
| :--- | :--- | :--- | :--- | :--- |
| `/tentang` | `2281` | Page 4 | `(8000, 0)`, `1440x880` | `PUB / P06 Tentang Perumda & Unit Agro Niaga (/tentang) / Desktop` — hero proporsional Golden Ratio, eksklusi eksplisit Unit Listrik & Gas, 3 pilar layanan Agro Niaga, navbar `Tentang` aktif. |
| `/kemitraan` | `2327` | Page 4 | `(9600, 0)`, `1440x900` | `PUB / P07 Informasi Kemitraan (/kemitraan) / Desktop` — 3 kartu mitra inti, alur 4 tahap kemitraan, penjaga privasi komersial `BR-PUB-003`. |
| `/kontak` | `2372` | Page 4 | `(11200, 0)`, `1440x820` | `PUB / P08 Kontak Resmi & Lokasi Kantor (/kontak) / Desktop` — data `perumda_offices`, `LocationLink #240`, guard privasi kontak `BSD §5.4`, pratinjau peta kantor MapLibre. |
| `/app/perumda` | `2444` | Page 8 | `(8000, 0)`, `1440x900` | `OPS / Dashboard Operasional Perumda (/app/perumda) / Desktop` — 4 kartu KPI operasional lintas alur, antrean prioritas, akses cepat SOP (`Pending SOP`) & Master PKS. |
| `/app/direksi/persetujuan` | `2514` | Page 10 | `(3200, 0)`, `1440x900` | `DIR / Daftar & Detail Persetujuan Kewenangan (/app/direksi/persetujuan) / Desktop` — pencarian & filter tanggal, antrean 3 item otorisasi, panel validasi `Maker != Checker`. |
| `/app/admin` | `2576` | Page 11 | `(3200, 0)`, `1440x900` | `ADM / Dashboard Administrator Sistem (/app/admin) / Desktop` — KPI kesehatan teknis non-transaksional (`/healthz`, Redis, error 5xx `req_8f2a1c90`), lencana `BR-SYS-002 Dilarang Approver`, feed audit keamanan. |

#### B. Form Bisnis Lengkap (`FLOW-05` & `FLOW-06`)
| Alur Bisnis | Node ID | Page | Koordinat & Ukuran | State & Validasi Terverifikasi |
| :--- | :--- | :--- | :--- | :--- |
| **`FLOW-05`** Master Data Petani & Kebun | `2641` | Page 7 | `(4800, 0)`, `1440x960` | Field `DBD farmers/farms` (`farmer_code`, `full_name`, `contact_phone`, kunci scope `KOP-01`, `farm_code`, `area_hectares`, `planting_year`), `Molecule/FormField #210` (error validasi berpasangan `422` koordinat + guard privasi `BR-MD-008`), `Atom/Input` (`Default`/`Focus`/`Disabled`), `Organism/ConfirmDialog #288` (`BR-MD-003/010` nonaktif tanpa hapus histori), kartu sukses `201 Created`, & `Organism/StateFeedbackCard #296` (guard konflik `409`/jaringan). |
| **`FLOW-06`** Master Data PKS & Publikasi Profil (`/app/perumda/pks`) | `2741` | Page 8 | `(9600, 0)`, `1440x960` | Field `DBD mill_companies/mills`, `Molecule/FormField #210` (error validasi `422` Lat `[-90..90]`/Lng berpasangan sesuai `DBD §7.7`), `Checkbox` pemisah status kemitraan internal vs publikasi portal `is_public` (`AFD §9.4`, menyembunyikan kontrak/kuota `BR-PUB-003`), `Organism/ConfirmDialog #288`, banner sukses `200 OK` cache invalidation, & `LocationLink #240`. |

#### C. Layar Bisnis Mobile Prioritas (`390px` / `375px`)
| Domain / Layar | Node ID | Page | Catatan Implementasi D5 |
| :--- | :--- | :--- | :--- |
| `PUB / P05 Detail PKS Mitra (/pks/:id) / Mobile (390px)` | `2414` | Page 4 | Menghindari clip kanan pada `LocationLink`, layout bertumpuk ramah sentuh (`>=44px`). |
| `AUTH / P09 Login Portal Internal / Mobile (390px)` | `2841` | Page 5 | Input kredensial, tombol aksi penuh, informasi error RBAC/lockout. |
| `PET / Ringkasan Pembayaran & Riwayat Panen / Mobile (390px)` | `2864` | Page 6 | Pemecahan bertahap ringkasan pembayaran (`BR-PAY-010`) + pengetatan `980` (`sizingV: "hug"`). |
| `KOP / Form Input Penerimaan TBS Lapangan / Mobile (390px)` | `1232` | Page 7 | Di-upgrade memakai instance live `Molecule/WeightInputGroup #227` (fit `17.340,000` kg bersih di `390px`/`375px`). |
| `KOP / Detail e-DO Konsolidasi & QR / Mobile (390px)` | `2887` | Page 7 | Verifikasi QR konsolidasi e-DO, identitas armada, dan status penimbangan. |
| `OPS / Detail Rekonsiliasi Timbang / Mobile (390px)` | `2908` | Page 8 | Ringkasan selisih Ramp vs PKS, pemicu eskalasi rekonsiliasi, & label `Aturan Simulasi`. |
| `PKS / Input Tiket Timbang PKS / Mobile (390px)` | `2931` | Page 9 | Memakai instance live `Molecule/WeightInputGroup #227` + aksi kirim tiket PKS. |

#### D. Konsolidasi Atomic Design & Prototype Interactive
- **Refactor `Organism/InternalSidebar #275`:** Ditingkatkan dengan Brand Header + `7` slot menu `44px` (`Nav/Slot-1..7`) + tombol bawah `Nav/Logout` (`Keluar Akun -> /login`, `#B8C7BE`, rasio `9.32:1` AAA), serta pembersihan wrapper fill `#FFFFFF` (`fills: []`). Seluruh **16** sidebar lokal pada frame internal lama (`844, 917, 1017, 1101, 1163, 1261, 1324, 1384, 1447, 2153, 1509, 1560, 1611, 1677, 1719, 1779`) berhasil diganti non-destruktif menjadi instance live `#275` -> total **`21` instance aktif** pada 21 layar internal desktop.
- **Katalog Komponen (`component.list`):** **`48` entri (`3 COMPONENT_SET` + `45 COMPONENT`)**, **`39 / 45` (`86.7%`) komponen aktif terpakai (`>0` instance)**, total **`393` instance** di seluruh dokumen. Hanya `6` varian mikro showcase (`Icon/PriceTag`, `Icon/Scale`, `Icon/Truck`, `Icon/Lock`, `Button Hover`, `Checkbox-Unchecked`) yang dipertahankan di showcase Page 3 sebagai referensi implementasi CSS/React.
- **Prototype Flows (`14` Flow, `215` Interaksi, `0` Target Rusak/Dangling):**
  - Page 4: `Portal Publik Penuh (P01->P08 Desktop) -> 329` (`60` interactions)
  - Page 5: `Auth & App Shell (/login) -> 755` (`5` interactions)
  - Page 6: `Portal Petani Penuh -> 844` (`11` interactions)
  - Page 7: `Koperasi End-to-End Penuh (Ramp -> Timbang -> e-DO) -> 1017` (`25` interactions)
  - Page 8: `Perumda Operations & Finance Penuh -> 2444` (`56` interactions)
  - Page 9: `PKS Penerimaan & Timbang Penuh -> 1509` (`7` interactions)
  - Page 10: `Direksi Eksekutif & Persetujuan Penuh -> 1611` (`15` interactions)
  - Page 11: `Administrator RBAC & CCTV Digital Penuh -> 2576` (`15` interactions)
  - Page 12: `W01–W06` (`6` storyboards, `21` interactions tetap utuh)
- **Batasan Prototype vs React/Backend:** Interaksi FigCraft hanya memodelkan navigasi antar-layar, pemilihan tab, modal konfirmasi, dan showcase state statis. Autentikasi (`JWT`/`Cookie`, lockout), query filter/paginasi server, perhitungan netto/potongan/harga TBS, penguncian transaksi (`Maker != Checker`), enkripsi QR, serta invalidasi cache `is_public` **harus diimplementasikan di React + FastAPI + PostgreSQL**.

### 3. Pengujian yang Dilakukan & Bukti Terverifikasi
1. **Audit Kontras WCAG (Python JSON Scan kedalaman 12 penuh tanpa truncasi pada `inspect_document`):** Memeriksa **`1.451` node `TEXT` tampak** -> **`0` kegagalan kontras (`< 4.5:1`)** *(catatan: FigCraft MCP tidak memiliki command `design.lint` bawaan, sehingga lint kontras, dangling interaction, dan bounding dijalankan langsung atas output JSON `inspect_document`)*.
2. **Audit Font (`file.fontReport` & `text.missingFonts`):** **`2` font** (`Open Sans`, `Cascadia Mono`), `available: true`, **`missing: 0`**, `families: []`.
3. **Audit Komponen (`component.list`):** **`39/45` (`86.7%`) komponen aktif**, **`393` total instance**, Page 14 `HANDOFF` (`2091`) diperbarui.
4. **Penandaan Dev Handoff (`inspect.readyForDev`):** **`50` board/frame terverifikasi** di Page 4–14 ditandai `readyForDev` (frame arsip komposit `id: 645` sengaja dipertahankan `devStatus: "none"`).
5. **Verifikasi Codegen Tailwind (`inspect.code {id: 2105, mobile: 2414, language: "tailwind"}`):** Mengonfirmasi keluaran JSX mobile-first yang merujuk variabel token `--color-primary-default`, `--color-ink-primary`, dll. sesuai `tokens.tailwind.css`.
6. **Ekspor Token & Penyimpanan File (`save_file` & `variable.export`):**
   - [agroniaga-tbs-perumda-tuah-sekata.figcraft](file:///D:/figcraft/test-output/agroniaga-tbs-perumda-tuah-sekata.figcraft) (`399.987 bytes`, `dirty: false`)
   - [tokens.tailwind.css](file:///D:/figcraft/test-output/tokens.tailwind.css) (`1.471 bytes`, `53` baris, `2` blok `@theme static`)
   - [tokens.json](file:///D:/figcraft/test-output/tokens.json) (`29.391 bytes`, `45` variabel)
7. **Bukti Screenshot:** **29 berkas PNG terverifikasi** (`12` dipertahankan dari D4 + `17` capture baru D5) tersimpan di [screenshots/](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/).

### 4. Temuan Tersisa (Non-Blocking — Diteruskan ke Implementasi React / Keputusan SOP)
1. **15 Keputusan SOP Terbuka (`AFD §41` / `BSD`):** Nilai ambang batas rekonsiliasi timbangan, batas keterlambatan unggah tiket PKS, SLA approval Direksi, retensi log, dan rule harga yang masih berstatus `Pending SOP` tetap diberi penanda **`Data Simulasi`** / **`Aturan Simulasi`** di desain dan UI React hingga Perumda menetapkan SK resmi.
2. **Pengujian Runtime Browser & Aksesibilitas Nyata (Fase `F8` IPD):** Verifikasi DOM `:focus-visible`, `prefers-reduced-motion`, navigasi keyboard Tab-order, ARIA landmark/live-region, serta respons tabel sekunder pada layar Admin Log (`390px`/`768px`) harus diuji langsung di Vite/React + Chrome DevTools.
3. **Varian Interaktif CSS/React (6 item Showcase Page 3):** State hover tombol & unchecked checkbox showcase (`0` instance di kanvas statis) dipetakan ke utility class Tailwind (`hover:`, `:checked`) dan micro-interactions Framer/CSS saat implementasi komponen React.
4. **Arsip Frame Komposit Lama (`id: 645`):** Frame `[ARSIP KOMPOSIT] PUB / P05-P08 Gabungan Lama / Desktop` tetap berada di koordinat `(0, 2250)` Page 4 dengan `devStatus: "none"` sebagai referensi historis D1–D4 dan **bukan acuan implementasi**.

### 5. Referensi Artefak
- Laporan Audit D4: [design-verification-signoff-report.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/design-verification-signoff-report.md)
- Laporan Penutupan Gap & Sign-Off D5: [d5-design-gap-closure-signoff.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/d5-design-gap-closure-signoff.md)
- Direktori Screenshot Bukti: [screenshots/](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/)
- Berkas FigCraft Sumber: [agroniaga-tbs-perumda-tuah-sekata.figcraft](file:///D:/figcraft/test-output/agroniaga-tbs-perumda-tuah-sekata.figcraft)
- Ekspor Token CSS & JSON: [tokens.tailwind.css](file:///D:/figcraft/test-output/tokens.tailwind.css) | [tokens.json](file:///D:/figcraft/test-output/tokens.json)

---

## Langkah Berikutnya (Handoff ke Track Implementasi Frontend — `IPD.md`)

Implementasi frontend mengacu pada **Master Implementation Plan** di [IPD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/IPD.md) (Milestone Track Frontend `F1–F8`):
1. **`F1` Design System & Token Setup:** Impor `tokens.tailwind.css` (`@theme static`) ke entry Tailwind CSS v4 React + TypeScript, pasang font `Open Sans` & `Cascadia Mono`, serta bangun primitives Atomic Design (`InternalSidebar`, `PublicNavbar`, `Atom/Input`, `FormField`, `WeightInputGroup`, `ConfirmDialog`, `StateFeedbackCard`, `LocationLink`).
2. **`F2–F3` Public Portal & Auth/AppShell Gate:** Implementasi `P01–P08` sesuai frame `1440px`/`390px` + guard `BR-PUB-003` (`is_public` & sanitasi data privat), serta autentikasi `/login` dengan RBAC route guard dan kebijakan `BR-SYS-002` pada role Administrator.
3. **`F4–F7` Portal Petani, Koperasi (`FLOW-05`), Perumda (`FLOW-06`, Rekonsiliasi), PKS, Direksi, & Admin:** Sambungkan formulir, validasi `422`/`409`, label `Data Simulasi`/`Pending SOP`, `Maker != Checker`, dan responsivitas `1440px / 1280px / 768px / 390px / 375px` dengan endpoint backend FastAPI sesuai kontrak `TRD.md` & `AFD.md`.
4. **`F8` Verification, A11y & Performance Gate:** Jalankan pengujian fokus keyboard, `prefers-reduced-motion`, kontrak API end-to-end, dan uji responsif lintas breakpoint sebelum UAT.

---

# BACKEND DEVELOPMENT TRACK

## Current Status

- **Current Milestone:** `B11.1 — Post-Implementation Verification` *(pasca `B11_PASS — BACKEND_INDEPENDENT_READY`; siap lanjut `F0–F11`)*
- **Last Milestone Passed:** `B11.1 — Post-Implementation Verification` (`READY — B11_1_POST_IMPLEMENTATION_VERIFIED`)
- **Last Verified Commit:** `1b70664` (`branch: main`, ditambah perbaikan kerja lokal `B11.1` siap commit oleh developer)
- **Backend Readiness:** `BACKEND_INDEPENDENT_READY` *(B0–B11 dan audit independen B11.1 lulus terverifikasi)*
- **Environment:** Python `3.12.0` di `backend/.venv` (`uv 0.13.7`, `114` paket terinstal & kompatibel); PostgreSQL 16 terisolasi di WSL2 Ubuntu (`127.0.0.1:15432`, DB `agroniaga_dev` & `agroniaga_test`, role least-privilege `agroniaga_dev`, tanpa menyentuh PostgreSQL 17 Windows di port `5432`); Redis 7 di WSL2 Ubuntu (`127.0.0.1:6379`, dev DB `/0`, test DB `/1`).
- **Pending SOP:** Keputusan `BSD-DEC-001..020` & `AFD §41 #1..15` (`SOP-01..15`) tetap berstatus `SIMULATION_ONLY` / `PENDING_SOP` / `FUTURE`.
- **Open Blockers:** Tidak ada.

---

## B0 — Project Foundation

- **Milestone ID:** `B0`
- **Nama Milestone:** `Project Foundation`
- **Status:** **`B0_PASS — FOUNDATION_VERIFIED`**
- **Tanggal:** `2026-11-10`
- **Baseline Commit:** `0243982`
- **Tujuan:** Membangun pondasi aplikasi FastAPI modular (`main.py` + `app/core/`), Pydantic Settings, async PostgreSQL engine + Alembic baseline, async Redis pool client & fail-closed guards, structured JSON logging + redaksi secrets, Request ID middleware + bounded timeout `504`, global exception handlers OpenAPI (`69` error codes), probe `/health/live` & `/health/ready`, Docker Compose PostgreSQL + Redis, serta tes unit, arsitektur, & integrasi tanpa membuat folder kosong modul domain.
- **Completed:**
  - [x] Verifikasi `.venv` Python `3.12.0` + instalasi `uv 0.13.7` ke dalam `.venv` (zero global installs) & generasi `uv.lock` (`113` resolved / `111` synced).
  - [x] Konfigurasi `backend/pyproject.toml` (Ruff, Pyright, Pytest, Import Linter), `.env.example`, `.env` (gitignored, dev+test terisolasi), `README.md`, dan `infra/docker-compose.yml` (+ `01-create-test-db.sh`).
  - [x] Implementasi `app/core/`: `config.py`, `logging.py`, `schemas.py`, `exceptions.py` (`69` `ErrorCode` selaras 1:1 `error-catalog.yaml`), `errors.py`, `database.py` (PostgreSQL async Psycopg 3 pool + Selector loop Windows guard), `redis.py` (pool, telemetry counters, fail-closed `SYS_DEPENDENCY_UNAVAILABLE`), `security.py`, `middleware.py`, `health.py`, dan composition root `app/main.py`.
  - [x] Setup & verifikasi Alembic async baseline (`alembic.ini`, `alembic/env.py`, `alembic/versions/0001_b0_baseline.py`) terhadap PostgreSQL 16 nyata (`agroniaga_dev`: `upgrade head` -> `downgrade base` -> `upgrade head`; `agroniaga_test`: `upgrade head`).
  - [x] Verifikasi koneksi PostgreSQL live, koneksi Redis live + fail-closed probe (`redis://127.0.0.1:6399/0`), dan `/health/ready -> 200 OK`.
- **Files Created:**
  - `backend/pyproject.toml`, `backend/uv.lock`, `backend/.env.example`, `backend/.env` *(gitignored, local runtime only)*, `backend/README.md`, `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/script.py.mako`, `backend/alembic/versions/0001_b0_baseline.py`
  - `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/core/__init__.py`, `backend/app/core/config.py`, `backend/app/core/logging.py`, `backend/app/core/schemas.py`, `backend/app/core/exceptions.py`, `backend/app/core/errors.py`, `backend/app/core/database.py`, `backend/app/core/redis.py`, `backend/app/core/security.py`, `backend/app/core/middleware.py`, `backend/app/core/health.py`
  - `backend/tests/__init__.py`, `backend/tests/conftest.py`, `backend/tests/architecture/test_import_boundaries.py`, `backend/tests/unit/test_foundation_unit.py`, `backend/tests/integration/test_foundation_infra.py`
  - `infra/docker-compose.yml`, `infra/postgres-init/01-create-test-db.sh`
- **Files Modified:** `docs/IMPLEMENTATION_CHECKPOINTS.md`, `contracts/scripts/validate_contracts.py` (membuat `K10` sadar fase agar `backend/` dan `infra/` sah saat Backend Track berjalan sambil tetap melarang `frontend/` & root `alembic/`).
- **Database Changes:** Belum ada tabel bisnis (`0001_b0_baseline` adalah anchor rantai revisi Alembic sebelum `B1`, terverifikasi `upgrade head` -> `downgrade base` -> `upgrade head` pada PostgreSQL 16 `127.0.0.1:15432`).
- **Dependencies:** `fastapi==0.162.3`, `uvicorn==0.54.0`, `pydantic==2.14.3`, `pydantic-settings==2.16.2`, `sqlalchemy==2.0.57`, `psycopg[binary]==3.3.8`, `alembic==1.20.1`, `redis==5.3.1`, `argon2-cffi==25.1.0`; dev/QA: `pytest==8.4.2`, `pytest-asyncio==0.26.0`, `httpx==0.28.1`, `ruff==0.17.4`, `pyright==1.1.414`, `import-linter==2.16`, `hypothesis==6.170.15`, `schemathesis==3.39.16`, `locust==2.47.0`, `pyyaml==6.0.3`, `uv==0.13.7` (seluruhnya terpasang hanya dalam `backend/.venv`).
- **Features Implemented:** Liveness `/health/live`, Readiness `/health/ready` (`200 ok` saat PostgreSQL & Redis aktif; `503 SYS_DEPENDENCY_UNAVAILABLE` fail-safe saat dependency mati), Request ID `req_<hex>` & `X-Request-ID`, timeout protection `504 SYS_REQUEST_TIMEOUT`, global JSON error mapping 69 error catalog, redaksi log secrets/DSN, layer isolation guards.
- **Bugs Found & Fixed:**
  1. `TBS_STALE_RECORD_VERSION` mengandung salah ketik `"Catatatan"` -> ditangkap `test_error_code_enum_matches_canonical_catalog` & diperbaiki menjadi `"Catatan"`.
  2. `app.core.errors` sempat mencampurkan FastAPI HTTP handler dengan `AppError` sehingga `import-linter` mendeteksi kebocoran `fastapi`/`starlette` ke adapter `redis` -> dipisahkan bersih menjadi framework-free `app/core/exceptions.py` dan HTTP-only `app/core/errors.py`.
  3. `WindowsProactorEventLoopPolicy` default Python Windows bentrok dengan `psycopg` 3 async -> ditangani dengan `WindowsSelectorEventLoopPolicy()` pada entrypoint, Alembic env, & pytest `conftest.py`.
  4. `backend/alembic.ini` kekurangan `qualname` pada section `[logger_sqlalchemy]` & `[logger_alembic]` (`KeyError: 'qualname'` saat menjalankan `alembic upgrade head`) -> ditambahkan `qualname = sqlalchemy.engine` dan `qualname = alembic`.
  5. `tests/conftest.py` hanya membaca `os.environ` sehingga `TEST_DATABASE_URL` dari `backend/.env` tidak terbaca saat `pytest` dijalankan langsung -> diperbaiki via `_load_backend_env_settings()` tanpa pernah fallback ke `DATABASE_URL` dev.
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` / `downgrade base` / `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`0001_b0_baseline`, exit `0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` -> **PASS** (`21 files already formatted`, exit `0`)
  - `.venv\Scripts\python.exe -m ruff check .` -> **PASS** (`All checks passed!`, exit `0`)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`, exit `0`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 2 kept, 0 broken`, exit `0`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`11 passed in 7.75s`: `3` architecture, `3` PostgreSQL/Redis integration, `5` unit; `0` failed, `0` skipped)
- **Counts:** `11` PASS (`5` unit, `3` architecture, `3` live DB/Redis integration), `0` FAIL, `0` SKIPPED; `11/11` `K1–K11` contract validation OK.
- **Quality Gate:** **PASS (`B0_PASS — FOUNDATION_VERIFIED`)**.
- **Known Limitations:** `K10` pada `validate_contracts.py` disesuaikan agar mengenali `# BACKEND DEVELOPMENT TRACK`; `backend/.venv` berisi `uv.exe` sendiri karena `uv` global tidak tersedia; host runtime dev/test memakai PostgreSQL 16 (`127.0.0.1:15432`) & Redis 7 (`127.0.0.1:6379`) pada WSL2 Ubuntu karena Docker belum terpasang di Windows.
- **Next Action:** Lanjut ke **`B1 — Identity, Auth, Session, RBAC`** (modul `app/modules/identity_access/` dengan 4 layer Clean Architecture, tabel `user_accounts`, `roles`, `permissions`, `role_permissions`, `user_role_grants`, `user_access_scopes`, `auth_sessions`, `audit_events`, `/api/v1/auth/*`, `/api/v1/admin/users*`, Argon2id, HttpOnly session + Redis, CSRF `X-CSRF-Token`, anti brute-force rate limit, serta guard `BR-SYS-002`).

---

## B1 — Identity & Access

- **Milestone ID:** `B1`
- **Nama Milestone:** `Identity & Access`
- **Status:** **`B1_PASS — IDENTITY_ACCESS_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Membangun modul `identity_access` dengan arsitektur Clean Architecture 4 layer (`domain/`, `application/`, `infrastructure/`, `presentation/`), skema RBAC & session PostgreSQL (`roles`, `permissions`, `role_permissions`, `user_accounts`, `user_role_grants`, `user_access_scopes`, `auth_sessions`), tabel audit append-only `audit_events` (`app/core/audit.py`), autentikasi `/api/v1/auth/*`, administrasi akses `/api/v1/admin/users*`, Argon2id off-event-loop, Redis fail-closed session + rate limiting, HMAC CSRF terikat sesi + pengecekan `Origin`, rotasi session ID (anti session-fixation), serta penegakan `BR-SYS-002`.
- **Completed:**
  - [x] Skema ORM & migrasi Alembic `0002_b1_identity_access` (`roles`, `permissions`, `role_permissions`, `user_accounts`, `user_role_grants`, `user_access_scopes` dengan check konsistensi target scope, `auth_sessions`, & `audit_events` lengkap trigger append-only PostgreSQL + seed deterministik `7` role & `64` permission sesuai `contracts/role-permissions.yaml`).
  - [x] Domain invariants & RBAC matrix (`domain/entities.py`, `domain/rules.py`): validasi role-scope, komputasi permission efektif, pelarangan approver bagi `SYSTEM_ADMIN` (`BR-SYS-002`), & helper ownership scope (`assert_farmer_scope`, `assert_cooperative_scope`, `assert_mill_scope`) untuk dipakai modul `B2–B10`.
  - [x] Use cases (`application/use_cases.py` + `application/ports.py`): login dengan anti-enumerasi timing dummy Argon2id + rotasi sesi baru, resolusi sesi Redis+PostgreSQL fail-closed, logout, penerbitan/verifikasi CSRF terikat sesi, & manajemen akses pengguna dengan pencabutan sesi aktif instan.
  - [x] Security adapters & presentation (`infrastructure/security_adapters.py`, `repository.py`, `presentation/dependencies.py`, `schemas.py`, `router.py`): `GET /api/v1/auth/csrf`, `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`, `GET /api/v1/admin/users`, `POST /api/v1/admin/users`, `PATCH /api/v1/admin/users/{user_id}`.
- **Files Created:**
  - `backend/app/core/audit.py`, `backend/alembic/versions/0002_b1_identity_access.py`
  - `backend/app/modules/__init__.py`, `backend/app/modules/identity_access/__init__.py`
  - `backend/app/modules/identity_access/domain/__init__.py`, `entities.py`, `rules.py`
  - `backend/app/modules/identity_access/application/__init__.py`, `ports.py`, `use_cases.py`
  - `backend/app/modules/identity_access/infrastructure/__init__.py`, `models.py`, `repository.py`, `security_adapters.py`
  - `backend/app/modules/identity_access/presentation/__init__.py`, `schemas.py`, `dependencies.py`, `router.py`
  - `backend/tests/unit/test_identity_access_unit.py`, `backend/tests/integration/test_identity_access_integration.py`
- **Files Modified:** `backend/app/core/config.py`, `backend/app/core/logging.py`, `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0002_b1_identity_access` menambahkan `roles` (`7`), `permissions` (`64`), `role_permissions`, `user_accounts`, `user_role_grants`, `user_access_scopes`, `auth_sessions`, & `audit_events` + trigger PostgreSQL `trg_audit_events_append_only`. Target FK opsional ke `parties`/`farmers`/`cooperatives`/`mills` disiapkan terindeks untuk ditautkan pada migrasi `B2` saat tabel master data dibuat.
- **Dependencies:** Memakai `argon2-cffi`, `redis`, `sqlalchemy` yang sudah ada pada `.venv` (zero paket baru ditambahkan).
- **Features Implemented:** HttpOnly + SameSite cookie sessions, SHA-256 hashed session persistence, Argon2id via `asyncio.to_thread`, Redis rate limiter (`429 AUTH_TOO_MANY_REQUESTS` + `Retry-After`), fail-closed `503 SYS_DEPENDENCY_UNAVAILABLE` saat Redis down, HMAC-SHA256 CSRF token (`s1.` vs `p1.`) + validasi `Origin`, pencabutan sesi instan saat admin mengubah role/scope/status, append-only redacted audit trail.
- **Bugs Found & Fixed:**
  1. Passing `cookies=...` per request ke `httpx.AsyncClient` memicu `DeprecationWarning` di pytest strict mode -> diganti client terpisah ber-cookie pada test integrasi.
  2. Test route lokal yang didefinisikan di dalam body fungsi dengan `from __future__ import annotations` dan import lokal gagal resolusi FastAPI (`422`) -> import `Annotated`/`UUID` dipindah ke top-level module test.
  3. Test fail-closed meneruskan `SecretStr` mentah via `str(...)` (`"SecretStr('***')"`) -> diganti memakai string DSN fixture `test_db_url`.
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` -> `downgrade 0001_b0_baseline` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` -> **PASS** (`41 files already formatted`, exit `0`)
  - `.venv\Scripts\python.exe -m ruff check .` -> **PASS** (`All checks passed!`, exit `0`)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`, exit `0`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 4 kept, 0 broken`, `57 files`, `175 dependencies`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`21 passed in 19.25s`: `10` unit, `3` architecture, `8` PostgreSQL/Redis integration; `0` failed, `0` skipped)
- **Counts:** `21` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B1_PASS — IDENTITY_ACCESS_VERIFIED`)**.
- **Known Limitations:** Relasi `FOREIGN KEY` kolom `linked_party_id`, `farmer_id`, `cooperative_id`, & `mill_id` pada `B1` ditambatkan di migrasi `B2` tepat ketika tabel `parties`, `farmers`, `cooperatives`, dan `mills` dibuat agar tidak memelihara tabel kosong prematur.
- **Next Action:** Lanjut ke **`B2 — Master Data`** (`app/modules/master_data/` + migrasi `0003_b2_master_data` untuk `parties`, `farmers`, `farms`, `cooperatives`, `cooperative_memberships`, `mill_companies`, `mills`, `perumda_offices`, `vehicles`, `drivers` + tautan FK ke tabel `B1`).

---

## B2 — Master Data

- **Milestone ID:** `B2`
- **Nama Milestone:** `Master Data`
- **Status:** **`B2_PASS — MASTER_DATA_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan modul `master_data` (`parties`, `cooperatives`, `farmers`, `cooperative_memberships`, `farms`, `mill_companies`, `mills`, `perumda_offices`, `vehicles`, `drivers`), penambatan FK tertunda dari `B1`, validasi koordinat berpasangan & presisi `Decimal` (`NUMERIC(12,4)`, `NUMERIC(9,6)`, `NUMERIC(14,3)`), isolasi scope koperasi & PKS, optimistic version locking, soft deactivation tanpa menghapus riwayat, serta invalidasi cache direktori PKS publik pasca-commit.
- **Completed:**
  - [x] Domain entities & rules (`master_data/domain/`): validasi koordinat WGS84 berpasangan `VAL_INVALID_COORDINATES`, `parse_area_hectares` / `parse_nominal_capacity_kg` `VAL_INVALID_DECIMAL_PRECISION`, normalisasi plat nomor.
  - [x] Application ports & use cases (`master_data/application/`): 18 endpoint use cases dengan isolasi scope `FARMER` / `COOPERATIVE` / `MILL` / `PERUMDA_GLOBAL`, optimistic locking `version`, serta invalidasi Redis `public:mills:v1:*` setelah commit DB.
  - [x] SQLAlchemy ORM models, repository anti-N+1 (`selectinload`/`joinedload`), migrasi Alembic `0003_b2_master_data` (10 tabel + 4 FK tertunda ke `user_accounts` & `user_access_scopes` + partial unique membership aktif), & router OpenAPI `/api/v1/{farmers,farms,cooperatives,mill-companies,mills,vehicles,drivers}`.
  - [x] Konsolidasi helper bersama `build_pagination_meta` & `format_decimal` pada `app/core/schemas.py` tanpa duplikasi antar modul.
- **Files Created:**
  - `backend/alembic/versions/0003_b2_master_data.py`
  - `backend/app/modules/master_data/__init__.py`
  - `backend/app/modules/master_data/domain/__init__.py`, `entities.py`, `rules.py`
  - `backend/app/modules/master_data/application/__init__.py`, `ports.py`, `use_cases.py`
  - `backend/app/modules/master_data/infrastructure/__init__.py`, `models.py`, `repository.py`, `cache_adapter.py`
  - `backend/app/modules/master_data/presentation/__init__.py`, `schemas.py`, `router.py`
  - `backend/tests/unit/test_master_data_unit.py`, `backend/tests/integration/test_master_data_integration.py`
- **Files Modified:** `backend/app/core/schemas.py`, `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `backend/app/modules/identity_access/presentation/schemas.py`, `backend/app/modules/identity_access/infrastructure/repository.py`, `backend/tests/integration/test_identity_access_integration.py`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0003_b2_master_data` menambah 10 tabel (`parties`, `cooperatives`, `farmers`, `cooperative_memberships`, `farms`, `mill_companies`, `mills`, `perumda_offices`, `vehicles`, `drivers`), unique partial index 1 koperasi aktif per petani, CHECK constraint koordinat berpasangan & angka positif, serta menambatkan 4 FK tabel `B1`.
- **Dependencies:** Zero paket baru ditambahkan.
- **Features Implemented:** CRUD terotorisasi penuh 18 operasi Master Data OpenAPI, optimistic lock conflict `409 MD_STALE_RECORD_VERSION` dengan detail `{expected_version, current_version}`, terjemahan unik/FK error aman `409 MD_DUPLICATE_CODE` & `422 VAL_INVALID_FORMAT`, soft deactivation `INACTIVE` menjaga histori, dan post-commit cache invalidation.
- **Bugs Found & Fixed:**
  1. SQLAlchemy Unit-of-Work menyisipkan `farmers`/`mill_companies` sebelum `parties` ketika ORM tidak memiliki `relationship()` eksplisit sehingga memicu PostgreSQL `ForeignKeyViolation` -> diperbaiki dengan explicit `await session.flush()` setelah `PartyModel` dan `MillCompanyModel`.
  2. `SqlAlchemyIdentityRepository` sebelumnya memetakan semua `IntegrityError` ke `MD_DUPLICATE_CODE` -> diperbaiki membedakan PG SQLSTATE `23503` (missing FK target scope -> `422 VAL_INVALID_FORMAT`) vs `23505` (duplicate key -> `409 MD_DUPLICATE_CODE`).
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` -> `downgrade 0002_b1_identity_access` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` & `ruff check .` -> **PASS** (`58 files already formatted`, `0` issues)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 5 kept, 0 broken`, `72 files`, `244 dependencies`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`26 passed in 24.45s`: `13` unit, `3` architecture, `10` PostgreSQL/Redis integration; `0` failed, `0` skipped)
- **Counts:** `26` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B2_PASS — MASTER_DATA_VERIFIED`)**.
- **Known Limitations:** `perumda_offices` baru dibuat di migrasi B2 dan segera diekspos ke Portal Publik pada `B3`.
- **Next Action:** Lanjut ke **`B3 — Public Portal & Pricing API`** (`app/modules/pricing/` + `app/modules/public_portal/` atau modul kohesif dengan migrasi `0004_b3_pricing_public` untuk `price_sources`, `price_categories`, `mill_price_quotes`, `price_verification_events`, `disbun_reference_prices`, `public_pages`, `public_notices`, workflow `SM-01` + `SOD-01`, Redis cache-aside & graceful fallback PostgreSQL).

---

## B3 — Public Portal & Pricing API

- **Milestone ID:** `B3`
- **Nama Milestone:** `Public Portal & Pricing API`
- **Status:** **`B3_PASS — PUBLIC_PORTAL_PRICING_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan `pricing` (`10` endpoint manajemen harga internal multi-PKS, `SM-01`, `SOD-01`, riwayat verifikasi append-only, referensi Disbun terpisah) dan `public_portal` (`7` endpoint Portal Publik bebas login, sanitasi XSS, privasi `is_public`, pemisahan harga Disbun vs PKS, Redis cache-aside pasca-commit invalidation, & graceful fallback PostgreSQL).
- **Completed:**
  - [x] Skema PostgreSQL & migrasi `0004_b3_pricing_public` (`price_sources`, `price_categories`, `mill_price_quotes`, `price_verification_events`, `disbun_reference_prices`, `public_pages`, `public_notices` + deterministic seed 4 source & 3 non-comparable categories).
  - [x] Domain & Use Cases `pricing`: validasi `price_per_kg > 0` (`PRICE_INVALID_AMOUNT`), periode (`PRICE_INVALID_PERIOD`), state machine `SM-01`, `SOD-01` Maker != Checker (`AUTH_CONFLICT_OF_DUTIES`), `BR-SYS-002`, pencegahan publikasi tumpang tindih dengan row-level lock `mills` + `PUBLISHED` quotes (`PRICE_OVERLAPPING_PERIOD`), isolasi DRAFT/REJECTED dari peran Petani/Koperasi.
  - [x] Domain & Read Model `public_portal`: eksposur terkurasi `PUBLISHED` + `is_public=true` saja, derived status `EXPIRED` & parameter `include_expired`, koordinat tersembunyi bila belum terverifikasi (`DBD §7.7`), batch loading anti-N+1, sanitasi HTML/XSS, Redis cache-aside + fallback mulus ke PostgreSQL saat Redis mati.
- **Files Created:**
  - `backend/alembic/versions/0004_b3_pricing_public.py`
  - `backend/app/modules/pricing/__init__.py`, `domain/` (`entities.py`, `rules.py`), `application/` (`ports.py`, `use_cases.py`), `infrastructure/` (`models.py`, `repository.py`, `cache_adapter.py`), `presentation/` (`schemas.py`, `router.py`)
  - `backend/app/modules/public_portal/__init__.py`, `domain/` (`entities.py`), `application/` (`ports.py`, `use_cases.py`), `infrastructure/` (`models.py`, `repository.py`, `cache_adapter.py`), `presentation/` (`schemas.py`, `router.py`)
  - `backend/tests/unit/test_pricing_public_unit.py`, `backend/tests/integration/test_pricing_public_integration.py`
- **Files Modified:** `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0004_b3_pricing_public` menambahkan 7 tabel (`price_sources`, `price_categories`, `mill_price_quotes`, `price_verification_events`, `disbun_reference_prices`, `public_pages`, `public_notices`) dan seed katalog sumber/kategori.
- **Dependencies:** Zero paket baru ditambahkan.
- **Features Implemented:** Workflow lengkap `DRAFT -> PENDING_VERIFICATION -> VERIFIED/REJECTED -> PUBLISHED -> REVOKED`, `EXPIRED` terhitung dinamis, pemisahan kategori harga `SWADAYA_STD` vs `PLASMA_KONTRAK`, pemisahan harga Disbun `BR-CMP-001`, portal publik anti-bocor `404`, Redis cache telemetry & post-commit invalidation, fallback Redis outage `200 OK`, anti-race concurrent publication `409`.
- **Bugs Found & Fixed:**
  1. `validate_price_period` di application layer tidak cukup bila `PATCH /prices/{id}` hanya mengirim salah satu ujung periode (`effective_from` atau `effective_until`) -> ditegakkan pula pada baris terkunci di repository sesudah penggabungan nilai eksisting + input baru.
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` -> `downgrade 0003_b2_master_data` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` & `ruff check .` -> **PASS** (`88 files already formatted`, `0` issues)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 7 kept, 0 broken`, `100 files`, `382 dependencies`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`31 passed in 35.18s`: `16` unit, `3` architecture, `12` PostgreSQL/Redis integration; `0` failed, `0` skipped)
- **Counts:** `31` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B3_PASS — PUBLIC_PORTAL_PRICING_VERIFIED`)**.
- **Known Limitations:** `source_document_id` pada `mill_price_quotes` & `disbun_reference_prices` menunggu modul `file_assets` sebelum ditautkan sebagai FK eksplisit.
- **Next Action:** Lanjut ke **`B4 — TBS Receiving & Grading`** (`app/core/idempotency.py`, `app/modules/tbs_receiving/` + migrasi `0005_b4_tbs_receiving` untuk `idempotency_records`, `tbs_receipts`, `receipt_weighing_revisions`, `receipt_grading_items`, `SM-02`, timbangan bruto/tara -> netto server-side, pemisahan komponen grading anti-potongan ganda, & `Idempotency-Key`).

---

## B4 — TBS Receiving & Grading

- **Milestone ID:** `B4`
- **Nama Milestone:** `TBS Receiving & Grading`
- **Status:** **`B4_PASS — TBS_RECEIVING_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan mesin idempotensi durable PostgreSQL (`idempotency_records`, `app/core/idempotency.py`, & `app/core/idempotency_primitives.py`) serta modul `tbs_receiving` (`tbs_receipts`, `receipt_weighing_revisions`, `receipt_grading_items`) dengan alur `SM-02`, perhitungan `net = gross - tare` berbasis `Decimal` di server, riwayat revisi tanpa hapus baris lama (`is_current`), wajib alasan koreksi (`BR-WGT-001`), pemisahan komponen potongan grading (`SIMULATION_ONLY` `BSD-DEC-006`) agar tidak terjadi potongan ganda, isolasi kepemilikan petani/koperasi (`BR-MD-004`), optimistic locking, serta penguncian setelah `ALLOCATED`/`SHIPPED`/`CLOSED` (`TBS_RECEIPT_LOCKED`).
- **Completed:**
  - [x] Durable Idempotency Engine (`core/idempotency_primitives.py`, `core/idempotency.py`, tabel `idempotency_records`): klaim atomik slot `IN_PROGRESS` (`ON CONFLICT DO NOTHING` + `SELECT FOR UPDATE`), deteksi payload mismatch (`409 IDM_KEY_CONFLICT_PAYLOAD_MISMATCH`), in-flight guard (`409 IDM_REQUEST_IN_PROGRESS`), replay aman pasca-commit (`meta.idempotency_replayed=True`), & pelepasan slot saat error `4xx/422` sebelum commit.
  - [x] Domain & Use Cases `tbs_receiving`: validasi presisi `NUMERIC(14,3)` (`VAL_INVALID_DECIMAL_PRECISION`), guard `tare <= gross` (`TBS_INVALID_WEIGHT`), anti-duplikasi kategori & dasar `NET_WEIGHT_BEFORE_GRADING` (`TBS_INVALID_GRADING_DEDUCTION`), penguncian mutasi `ALLOCATED/SHIPPED/CLOSED` (`TBS_RECEIPT_LOCKED`), serta scope ketat `FARMER` vs `COOPERATIVE` vs `PERUMDA_GLOBAL`.
  - [x] Skema PostgreSQL & migrasi Alembic `0005_b4_tbs_receiving`: sequence `tbs_receipt_seq`, `tbs_receipts`, `receipt_weighing_revisions` (CHECK constraint DB `tare_weight_kg <= gross_weight_kg` dan `net_weight_kg = gross_weight_kg - tare_weight_kg`, partial unique `is_current IS TRUE`), `receipt_grading_items` (unique `(weighing_revision_id, grading_category)`), serta 7 endpoint OpenAPI `/api/v1/receipts*`.
- **Files Created:**
  - `backend/alembic/versions/0005_b4_tbs_receiving.py`
  - `backend/app/core/idempotency_primitives.py`, `backend/app/core/idempotency.py`
  - `backend/app/modules/tbs_receiving/__init__.py`
  - `backend/app/modules/tbs_receiving/domain/__init__.py`, `entities.py`, `rules.py`
  - `backend/app/modules/tbs_receiving/application/__init__.py`, `ports.py`, `use_cases.py`
  - `backend/app/modules/tbs_receiving/infrastructure/__init__.py`, `models.py`, `repository.py`
  - `backend/app/modules/tbs_receiving/presentation/__init__.py`, `schemas.py`, `router.py`
  - `backend/tests/unit/test_tbs_receiving_unit.py`, `backend/tests/integration/test_tbs_receiving_integration.py`
- **Files Modified:** `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0005_b4_tbs_receiving` menambahkan `idempotency_records`, sequence `tbs_receipt_seq`, `tbs_receipts`, `receipt_weighing_revisions`, dan `receipt_grading_items` lengkap dengan DB CHECK & partial unique constraints.
- **Dependencies:** Zero paket baru ditambahkan.
- **Features Implemented:** Pembuatan draf penerimaan idempoten (`201 Created`, `Idempotency-Key` wajib), penimbangan terversi dengan komputasi `net_weight_kg` server-side & kewajiban `correction_reason` pada revisi, pencatatan grading terpisah bertanda `is_simulation=true` & `simulation_notice`, validasi `DRAFT -> VALIDATED` berbasis timbang valid, pembatalan ber-alasan dengan riwayat `CANCELLED`, dan proteksi lintas petani/koperasi.
- **Bugs Found & Fixed:**
  1. Pemisahan `idempotency_primitives.py` (bebas SQLAlchemy/FastAPI) dari `core/idempotency.py` mencegah pelanggaran `import-linter` ketika service layer menginjeksikan idempotensi melalui port `IdempotencySlotPort`.
  2. Penghapusan `await` keliru pada fungsi sinkron `append_audit_event(..., resource_id=str(...))` yang terdeteksi `pyright` sebelum eksekusi migrasi.
  3. Penyesuaian fixture test integrasi `UserRoleGrantModel` & `UserAccessScopeModel` mengikuti kolom `revoked_at=None` skema B1.
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` -> `downgrade 0004_b3_pricing_public` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` & `ruff check .` -> **PASS** (`106 files already formatted`, `0` issues)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 8 kept, 0 broken`, `115 files`, `471 dependencies`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`44 passed in 43.84s`: `27` unit, `3` architecture, `14` PostgreSQL/Redis integration including concurrent `Idempotency-Key` race test; `0` failed, `0` skipped)
- **Counts:** `44` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B4_PASS — TBS_RECEIVING_VERIFIED`)**.
- **Known Limitations:** Nilai `delivery_order_id` dalam detail error `TBS_RECEIPT_LOCKED` diisi setelah tabel `delivery_order_lines` dibangun pada `B6`.
- **Next Action:** Lanjut ke **`B5 — Contracts & Quota`** (`app/modules/contracts/` + migrasi `0006_b5_contracts_quota` untuk `system_rule_versions` seed awal, `trade_contracts`, `contract_quota_periods`, `quota_reservations`, `contract_approval_events`, workflow `SM-03` & `SM-04`, `SOD-02`, isolasi `UNCONFIRMED`, dan row-level locking reservasi kuota anti over-quota).

---

## B5 — Contracts & Quota

- **Milestone ID:** `B5`
- **Nama Milestone:** `Contracts & Quota`
- **Status:** **`B5_PASS — CONTRACTS_QUOTA_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan katalis kebijakan berversi `system_rule_versions` (`app/core/system_rules.py`) dan modul kontrak niaga PKS serta kuota (`contracts`: `trade_contracts`, `contract_quota_periods`, `quota_reservations`, `contract_approval_events`) lengkap dengan state machine `SM-03` & `SM-04`, pemisahan `PRINCIPAL` vs `AGENT` vs `UNCONFIRMED` (`PENDING_SOP`), `SOD-02` Maker != Checker, pelarangan pembukaan rahasia kontrak ke koperasi/petani/PKS, & PostgreSQL `SELECT FOR UPDATE` reservasi kuota anti over-quota dan anti double-consumption.
- **Completed:**
  - [x] Tabel `system_rule_versions` (`core/system_rules.py`) & seed awal 3 versi aturan dasar (`RECONCILIATION_TOLERANCE` 1,5% `SIMULATION_ONLY`, `BUSINESS_MODEL_POLICY` `UNCONFIRMED` `PENDING_SOP`, `FARMER_ALLOCATION_POLICY` `PENDING_SOP`).
  - [x] Domain & Use Cases `contracts`: validasi struktur pihak `PRINCIPAL` vs `AGENT` vs `UNCONFIRMED` (`422 CONTRACT_BUSINESS_MODEL_UNCONFIRMED`), validasi harga `FIXED`, pelarangan pembatalan `SOD-02` self-approval (`AUTH_CONFLICT_OF_DUTIES`), guard `BR-SYS-002` (`AUTH_OPERATION_FORBIDDEN`), guard status aktif (`CONTRACT_NOT_ACTIVE`), kedaluwarsa (`CONTRACT_EXPIRED`), dan idempotensi `reserveContractQuota`.
  - [x] Operasional SQL row-lock bersama (`contracts/infrastructure/quota_ops.py`): `reserve_quota_in_tx`, `consume_quota_reservation_in_tx`, & `release_quota_reservation_in_tx` di PostgreSQL + partial unique index `uq_quota_reservations_active_do` mencegah double reservation/consumption, serta `6` endpoint `/api/v1/contracts*`.
- **Files Created:**
  - `backend/alembic/versions/0006_b5_contracts_quota.py`
  - `backend/app/core/system_rules.py`
  - `backend/app/modules/contracts/__init__.py`
  - `backend/app/modules/contracts/domain/__init__.py`, `entities.py`, `rules.py`
  - `backend/app/modules/contracts/application/__init__.py`, `ports.py`, `use_cases.py`
  - `backend/app/modules/contracts/infrastructure/__init__.py`, `models.py`, `quota_ops.py`, `repository.py`
  - `backend/app/modules/contracts/presentation/__init__.py`, `schemas.py`, `router.py`
  - `backend/tests/unit/test_contracts_unit.py`, `backend/tests/integration/test_contracts_integration.py`
- **Files Modified:** `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0006_b5_contracts_quota` menambah `system_rule_versions` (+3 baseline seed), `trade_contracts`, `contract_quota_periods`, `quota_reservations`, dan `contract_approval_events` beserta CHECK constraints model usaha/pihak dan partial unique `uq_quota_reservations_active_do`.
- **Dependencies:** Zero paket baru ditambahkan.
- **Features Implemented:** Pembuatan draf kontrak rahasia komersial (`PENDING_APPROVAL`), isolasi model `UNCONFIRMED` (`PENDING_SOP`) vs `SIMULATION_ONLY`, aktivasi Direktur (`SOD-02`), kueri sisa kuota langsung dari PostgreSQL (tanpa Redis cache `ADR-004`), reservasi kuota idempoten anti-race, konversi `RESERVED -> CONSUMED`, dan pelepasan `RESERVED -> RELEASED`.
- **Bugs Found & Fixed:** Perbaikan nama kolom `MillCompanyModel` (`company_code`, `contact_phone`, `address`) di fixture integrasi `test_contracts_integration.py`.
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` -> `downgrade 0005_b4_tbs_receiving` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` & `ruff check .` -> **PASS** (`124 files already formatted`, `0` issues)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 9 kept, 0 broken`, `130 files`, `560 dependencies`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`49 passed in 47.90s`: `30` unit, `3` architecture, `16` PostgreSQL/Redis integration termasuk uji balap kuota `asyncio.gather` `25t vs 2x20t`; `0` failed, `0` skipped)
- **Counts:** `49` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B5_PASS — CONTRACTS_QUOTA_VERIFIED`)**.
- **Known Limitations:** Relasi FK `quota_reservations.delivery_order_id -> delivery_orders.id` ditambatkan di migrasi `B6` saat tabel `delivery_orders` dibuat.
- **Next Action:** Lanjut ke **`B6 — Logistics & e-DO`** (`app/modules/logistics/` + migrasi `0007_b6_logistics_edo` untuk `delivery_orders`, `delivery_order_lines`, partial unique `ux_active_receipt_allocation`, `delivery_status_events`, QR hash, `SM-05`, integrasi kuota `B5`, & penguncian penerimaan `B4`).

---

## B6 — Logistics & e-DO

- **Milestone ID:** `B6`
- **Nama Milestone:** `Logistics & e-DO`
- **Status:** **`B6_PASS — LOGISTICS_EDO_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan modul pengiriman konsolidasi multi-petani dan e-DO (`logistics`: `delivery_orders`, `delivery_order_lines`, `delivery_status_events`), penambatan FK tertunda `quota_reservations.delivery_order_id -> delivery_orders.id`, transaksi atomik penerbitan e-DO (`Idempotency-Key` wajib, kunci alokasi `ux_active_receipt_allocation`, kunci `tbs_receipts -> ALLOCATED`, reservasi kuota `RESERVED`, generasi token & hash SHA-256 QR), transisi state machine `SM-05` (`DRAFT -> READY -> IN_TRANSIT -> ARRIVED -> RECEIVED -> COMPLETED`), verifikasi QR terautentikasi PKS (`MILL_EDO_MILL_MISMATCH`), pembatalan pra-keberangkatan yang melepaskan muatan dan kuota secara konsisten, serta isolasi privasi lini petani lain.
- **Completed:**
  - [x] Domain & Rules (`logistics/domain/`): state machine `SM-05`, pembatasan perpindahan `IN_TRANSIT` vs `COMPLETED`, guard pembatalan (`LOG_CANCELLATION_FORBIDDEN` pasca-tiba), & generasi token/SHA-256 QR non-tebakan.
  - [x] Use Cases & Repository (`logistics/application/`, `infrastructure/`): 7 operasi OpenAPI `/api/v1/delivery-orders*`, konsolidasi multi-petani berdasar netto otoritatif (tanpa potongan simulasi ganda), transaksi atomik `issueDeliveryOrder` dengan `SELECT FOR UPDATE` berurutan atas `delivery_orders`, `tbs_receipts`, & `contract_quota_periods`, pelepasan lengkap saat pembatalan (`ALLOCATED -> VALIDATED`, `allocation_status = RELEASED`, `quota -> RELEASED`), dan filter lini privat `FARMER`.
  - [x] Migrasi `0007_b6_logistics_edo`: sequence `delivery_order_seq`, `delivery_orders`, `delivery_order_lines` (partial unique `ux_active_receipt_allocation`), `delivery_status_events`, serta penambatan FK `fk_quota_reservations_delivery_order_id`.
- **Files Created:**
  - `backend/alembic/versions/0007_b6_logistics_edo.py`
  - `backend/app/modules/logistics/__init__.py`
  - `backend/app/modules/logistics/domain/__init__.py`, `entities.py`, `rules.py`
  - `backend/app/modules/logistics/application/__init__.py`, `ports.py`, `use_cases.py`
  - `backend/app/modules/logistics/infrastructure/__init__.py`, `models.py`, `repository.py`
  - `backend/app/modules/logistics/presentation/__init__.py`, `schemas.py`, `router.py`
  - `backend/tests/unit/test_logistics_unit.py`, `backend/tests/integration/test_logistics_integration.py`
- **Files Modified:** `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `backend/app/modules/contracts/infrastructure/quota_ops.py`, `backend/tests/integration/test_contracts_integration.py`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0007_b6_logistics_edo` menambah `delivery_order_seq`, `delivery_orders`, `delivery_order_lines`, `delivery_status_events`, partial unique index anti double-allocation `ux_active_receipt_allocation`, serta FK `quota_reservations.delivery_order_id -> delivery_orders.id`.
- **Dependencies:** Zero paket baru ditambahkan.
- **Features Implemented:** Pembuatan draft konsolidasi multi-petani, deteksi konflik alokasi ganda (`409 LOG_DELIVERY_ALREADY_ASSIGNED`), penerbitan idempoten anti-race, rollback penuh bila kuota tidak cukup, pelacakan histori status `delivery_status_events`, pembatalan ber-alasan dengan pelepasan kuota & penerimaan, verifikasi QR PKS terautentikasi (`403 MILL_EDO_MILL_MISMATCH`), dan pemisahan privasi muatan bagi akun petani (`gps_tracking_supported=false`).
- **Bugs Found & Fixed:**
  1. Pembacaan `contracts/role-permissions.yaml` mengungkap `COOPERATIVE_OPERATOR` memegang `delivery_orders.issue` & `delivery_orders.cancel` tanpa memegang permission `quotas.reserve`/`quotas.release` secara langsung -> dependency endpoint diset ke `delivery_orders.issue`/`cancel` sementara reservasi/pelepasan kuota dieksekusi oleh domain server dalam transaksi atomik.
  2. Penyelarasan nama kolom `VehicleModel` (`updated_at`) & `DriverModel` (`contact_phone`, `driver_reference`, `updated_at`) pada fixture seed test integrasi `B5` & `B6` saat FK `delivery_order_id` ditambatkan.
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` -> `downgrade 0006_b5_contracts_quota` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` & `ruff check .` -> **PASS** (`140 files already formatted`, `0` issues)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 10 kept, 0 broken`, `143 files`, `629 dependencies`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`54 passed in 58.42s`: `33` unit, `3` architecture, `18` PostgreSQL/Redis integration termasuk balap `issueDeliveryOrder` & cross-mill QR guard; `0` failed, `0` skipped)
- **Counts:** `54` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B6_PASS — LOGISTICS_EDO_VERIFIED`)**.
- **Known Limitations:** Status `ARRIVED -> RECEIVED` pada `delivery_orders` otomatis terpicu saat verifikasi tiket timbang PKS di `B7`.
- **Next Action:** Lanjut ke **`B7 — Mill Weighing & Evidence Files`** (`app/modules/files/` & `app/modules/mill_weighing/` + migrasi `0008_b7_mill_weighing_files` untuk `file_assets`, `mill_weighing_tickets`, `mill_grading_items`, `/api/v1/files*`, `/api/v1/mill-tickets*`, alur `SM-06`, revisi tiket berversi, integrasi konversi kuota `CONSUMED` & transisi `ARRIVED -> RECEIVED`).

---

## B7 — Mill Weighing & Evidence Files

- **Milestone ID:** `B7`
- **Nama Milestone:** `Mill Weighing & Evidence Files`
- **Status:** **`B7_PASS — MILL_WEIGHING_FILES_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan penyimpanan metadata dan berkas bukti terotorisasi non-publik (`files`: `file_assets`, `/api/v1/files*`, penambatan FK bukti harga `B3`) serta modul penimbangan & grading pabrik PKS (`mill_weighing`: `mill_weighing_tickets`, `mill_grading_items`, `/api/v1/mill-tickets*`) dengan alur `SM-06`, keunikan tiket current per PKS & e-DO, revisi berversi tanpa hapus histori, isolasi ketat antar PKS (`MILL_EDO_MILL_MISMATCH`), validasi status kedatangan `ARRIVED`, konversi kuota `RESERVED -> CONSUMED`, & transisi e-DO `ARRIVED -> RECEIVED`.
- **Completed:**
  - [x] Shared Decimal weight validator `app/core/weight_primitives.py` dipakai bersama oleh `tbs_receiving` dan `mill_weighing` tanpa duplikasi logika.
  - [x] Modul `files` (4 layer): verifikasi tanda tangan biner (magic bytes PDF/JPEG/PNG), batas ukuran 10 MiB, sanitasi path-traversal nama berkas, checksum SHA-256, `storage_key` buram non-publik di disk terisolasi, & isolasi akses lintas-PKS.
  - [x] Modul `mill_weighing` (4 layer): pembuatan tiket idempoten (`ARRIVED` wajib), partial unique indexes `ux_current_mill_ticket_per_do` & `uq_mill_tickets_mill_number_current` (`MILL_DUPLICATE_TICKET`), revisi berversi berantai `previous_ticket_id` menjaga `revision_number` lama, pemblokiran `COMPLETED` finality (`MILL_TICKET_ALREADY_FINAL`), serta verifikasi `SUBMITTED -> VERIFIED` yang otomatis memajukan e-DO ke `RECEIVED` & mengonsumsi reservasi kuota `B5`.
- **Files Created:**
  - `backend/alembic/versions/0008_b7_mill_weighing_files.py`
  - `backend/app/core/weight_primitives.py`
  - `backend/app/modules/files/__init__.py`, `domain/` (`entities.py`, `rules.py`), `application/` (`ports.py`, `use_cases.py`), `infrastructure/` (`models.py`, `storage.py`, `repository.py`), `presentation/` (`schemas.py`, `router.py`)
  - `backend/app/modules/mill_weighing/__init__.py`, `domain/` (`entities.py`, `rules.py`), `application/` (`ports.py`, `use_cases.py`), `infrastructure/` (`models.py`, `repository.py`), `presentation/` (`schemas.py`, `router.py`)
  - `backend/tests/unit/test_mill_weighing_unit.py`, `backend/tests/integration/test_mill_weighing_integration.py`
- **Files Modified:** `backend/app/core/config.py`, `backend/app/modules/tbs_receiving/domain/rules.py`, `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `backend/uv.lock`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0008_b7_mill_weighing_files` menambah `file_assets`, menambatkan 2 FK `source_document_id` pada tabel pricing `B3`, dan menambah `mill_weighing_tickets` + `mill_grading_items` dengan partial unique & CHECK constraints bruto-tara-netto.
- **Dependencies:** Ditambahkan `python-multipart>=0.0.12,<1.0.0` (terpasang `0.0.33` di `.venv`) agar FastAPI memproses endpoint upload multipart `/api/v1/files`.
- **Features Implemented:** Unggah/unduh bukti aman terotorisasi, pencatatan tiket PKS idempoten, deteksi nomor tiket ganda per PKS & blokir e-DO non-`ARRIVED`, revisi tiket menjaga histori, blokir pasca-selesai, & konsumsi kuota saat tiket terverifikasi.
- **Bugs Found & Fixed:** FastAPI mewajibkan paket `python-multipart` saat mendaftarkan route multipart `Form`/`UploadFile` pada `/api/v1/files` -> dideklarasikan di `pyproject.toml` dan di-sync bersih ke `backend/.venv` via `uv sync`.
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` -> `downgrade 0007_b6_logistics_edo` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` & `ruff check .` -> **PASS** (`171 files already formatted`, `0` issues)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 12 kept, 0 broken`, `174 files`, `768 dependencies`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`58 passed in 62.59s`: `36` unit, `3` architecture, `19` PostgreSQL/Redis integration; `0` failed, `0` skipped)
- **Counts:** `58` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B7_PASS — MILL_WEIGHING_FILES_VERIFIED`)**.
- **Known Limitations:** Guard `MILL_TICKET_ALREADY_FINAL` juga disambungkan ke status faktur terbit (`ISSUED`/`PAID`) saat modul keuangan dibangun pada `B9`.
- **Next Action:** Lanjut ke **`B8 — Reconciliation, Dispute & Farmer Allocation`** (`app/modules/reconciliation/` + migrasi `0009_b8_reconciliation` untuk `reconciliation_cases`, `dispute_reviews`, `farmer_settlement_allocations`, toleransi 1,5% `SIMULATION_ONLY`, deteksi selisih negatif `BR-REC-009`, dual-review `SOD-03`, & simulasi alokasi proporsional anti `REC_ALLOCATION_IMBALANCE`).

---

## B8 — Reconciliation, Dispute & Farmer Allocation

- **Milestone ID:** `B8`
- **Nama Milestone:** `Reconciliation, Dispute & Farmer Allocation`
- **Status:** **`B8_PASS — RECONCILIATION_DISPUTE_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan modul rekonsiliasi berat asal vs tiket PKS (`reconciliation`: `reconciliation_cases`, `dispute_reviews`, `farmer_settlement_allocations`), rumus selisih kanonis `BSD §17.4` (`origin - mill`), deteksi otomatis anomali selisih negatif (`BR-REC-009`), penangkapan snapshot `system_rule_versions` (`1,5000% SIMULATION_ONLY`), penegakan kesetaraan dasar berat (`REC_INVALID_WEIGHT_BASIS`), riwayat revisi tanpa hapus versi lama, peninjauan sengketa dual-role `SOD-03`, serta komputasi alokasi proporsional multi-petani dengan koreksi pembulatan deterministik (`REC_ALLOCATION_POLICY_UNCONFIRMED` memblokir mode `FINAL`).
- **Completed:**
  - [x] Domain Rules (`reconciliation/domain/`): komputasi `Decimal` selisih & persentase, guard dasar berat setara `NET_WEIGHT_BEFORE_GRADING`, deteksi `is_negative_difference` (`BR-REC-009`), otorisasi `SOD-03` & `BR-SYS-002` pada `resolveReconciliationDispute`, dan algoritma alokasi proporsional anti-selisih pembulatan (`REC_ALLOCATION_IMBALANCE`).
  - [x] Repository & Use Cases (`reconciliation/application/`, `infrastructure/`): 7 operasi `/api/v1/reconciliations*`, lock `SELECT FOR UPDATE` pada `delivery_orders` + partial unique index `ux_current_reconciliation_per_do`, snapshot aturan toleransi per transaksi, eskalasi `DISPUTE_HOLD -> UNDER_REVIEW -> RESOLVED/CANCELLED`, blokir sengketa dari alokasi (`REC_WEIGHT_DISPUTE`), & pemblokiran mode alokasi nyata (`REC_ALLOCATION_POLICY_UNCONFIRMED` `BSD-DEC-013`).
  - [x] Migrasi `0009_b8_reconciliation`: tabel `reconciliation_cases`, `dispute_reviews`, `farmer_settlement_allocations` lengkap dengan CHECK & FK constraints.
- **Files Created:**
  - `backend/alembic/versions/0009_b8_reconciliation.py`
  - `backend/app/modules/reconciliation/__init__.py`
  - `backend/app/modules/reconciliation/domain/__init__.py`, `entities.py`, `rules.py`
  - `backend/app/modules/reconciliation/application/__init__.py`, `ports.py`, `use_cases.py`
  - `backend/app/modules/reconciliation/infrastructure/__init__.py`, `models.py`, `repository.py`
  - `backend/app/modules/reconciliation/presentation/__init__.py`, `schemas.py`, `router.py`
  - `backend/tests/unit/test_reconciliation_unit.py`, `backend/tests/integration/test_reconciliation_integration.py`
- **Files Modified:** `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0009_b8_reconciliation` menambahkan 3 tabel (`reconciliation_cases`, `dispute_reviews`, `farmer_settlement_allocations`) beserta partial unique `ux_current_reconciliation_per_do` menjaga 1 kasus aktif current per e-DO.
- **Dependencies:** Zero paket baru ditambahkan.
- **Features Implemented:** Rekonsiliasi idempoten terunci, deteksi selisih negatif `BR-REC-009`, isolasi snapshot aturan toleransi masa lalu terhadap revisi aturan masa depan, histori revisi rekonsiliasi pasca-koreksi tiket, review & resolusi `SOD-03`, simulasi alokasi proporsional berlabel `SIMULATION_ONLY`, dan penolakan eksplisit `mode="FINAL"` sebelum SOP disahkan.
- **Bugs Found & Fixed:** Zero bug terdeteksi pada logic inti; 2 baris komentar/string >100 karakter dirapikan sesuai standar `ruff E501`.
- **Tests Executed:**
  - `.venv\Scripts\python.exe -m alembic upgrade head` -> `downgrade 0008_b7_mill_weighing_files` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\python.exe -m ruff format --check .` & `ruff check .` -> **PASS** (`187 files already formatted`, `0` issues)
  - `.venv\Scripts\python.exe -m pyright` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 13 kept, 0 broken`, `187 files`, `844 dependencies`)
  - `.venv\Scripts\python.exe -m pytest -v` -> **PASS** (`63 passed in 69.58s`: `39` unit, `3` architecture, `21` PostgreSQL/Redis integration; `0` failed, `0` skipped)
- **Counts:** `63` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B8_PASS — RECONCILIATION_DISPUTE_VERIFIED`)**.
- **Known Limitations:** Pembayaran nyata dan penerbitan faktur masih ditahan sampai integrasi faktur & pembayaran pada `B9` selesai.
- **Next Action:** Lanjut ke **`B9 — Finance, Invoices & Payments`** (`app/modules/finance/` + migrasi `0010_b9_finance` untuk `invoices`, `invoice_lines`, `payment_approvals`, `payment_records`, `payment_allocations`, pemisahan AR vs AP & INBOUND vs OUTBOUND, `FIN_DISPUTE_HOLD_BLOCKED`, `FIN_POLICY_UNCONFIRMED`, `SOD-04..06`, `PAY_PARTIAL_NOT_SUPPORTED`, `APPROVED != PAID`, serta penyambungan finality guard ke `B7`).

---

## B9 — Finance, Invoices & Payments

- **Milestone ID:** `B9`
- **Nama Milestone:** `Finance, Invoices & Payments`
- **Status:** **`B9_PASS — FINANCE_INVOICES_PAYMENTS_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan modul keuangan AR/AP terpisah (`finance`: `invoices`, `invoice_lines`, `payment_approvals`, `payment_records`), pemisahan arus piutang `ACCOUNTS_RECEIVABLE` (`PKS -> Perumda`, `INBOUND`) vs utang `ACCOUNTS_PAYABLE` (`Perumda -> Koperasi/Petani`, `OUTBOUND`), pemblokiran faktur saat sengketa (`FIN_DISPUTE_HOLD_BLOCKED`) dan penerbitan saat model usaha `UNCONFIRMED` (`FIN_POLICY_UNCONFIRMED`), penguncian harga historis transaksi, dual-control `SOD-04..06` + `BR-SYS-002`, idempotency `approveOrRejectInvoicePayment` & `recordPaymentEvidence`, penolakan pembayaran parsial (`PAY_PARTIAL_NOT_SUPPORTED`), prinsip `APPROVED != PAID` (`BR-PAY-010`), mekanisme pembalikan `REVERSED`, privasi Jalur C, serta finality guard `MILL_TICKET_ALREADY_FINAL` pada `B7`.
- **Completed:**
  - [x] Domain & Rules (`finance/domain/`): kalkulasi `Decimal` nominal IDR (`NUMERIC(20,2)`), validasi arah dana & pasangan pihak, `derive_settlement_status` (`PAID` hanya tercapai dari `VERIFIED` penuh non-reversed), serta guard `SOD-04` (`verifyInvoice`), `SOD-05` (`approveOrRejectInvoicePayment`), `SOD-06` (`verifyPaymentRecord`), & `BR-SYS-002`.
  - [x] Repository & Use Cases (`finance/application/`, `infrastructure/`): 9 endpoint OpenAPI `/api/v1/invoices*` & `/api/v1/payments*`, row lock + partial unique index `ux_invoices_active_case_type` & `ux_payment_records_active_ref`, snapshot harga kontrak `FIXED` maupun `MillPriceQuoteModel` `PUBLISHED` saat waktu e-DO, idempotency `approveOrRejectInvoicePayment` + `recordPaymentEvidence`, & isolasi baca `FARMER` / `COOPERATIVE_OPERATOR` khusus `OUTBOUND` Jalur C.
  - [x] Integrasi `B7`: `revise_ticket` dan `verify_ticket` di `mill_weighing` memblokir perubahan tiket dengan `409 MILL_TICKET_ALREADY_FINAL` bila sudah ada faktur `ISSUED`.
  - [x] Migrasi `0010_b9_finance`: `invoice_seq`, `payment_seq`, 4 tabel DBD §14 lengkap dengan CHECK (`invoice_parties_distinct`, `payment_approval_sod_05`, `payment_record_sod_06`) & partial unique indexes.
- **Files Created:**
  - `backend/alembic/versions/0010_b9_finance.py`
  - `backend/app/modules/finance/__init__.py`
  - `backend/app/modules/finance/domain/__init__.py`, `entities.py`, `rules.py`
  - `backend/app/modules/finance/application/__init__.py`, `ports.py`, `use_cases.py`
  - `backend/app/modules/finance/infrastructure/__init__.py`, `models.py`, `repository.py`
  - `backend/app/modules/finance/presentation/__init__.py`, `schemas.py`, `router.py`
  - `backend/tests/unit/test_finance_unit.py`, `backend/tests/integration/test_finance_integration.py`
- **Files Modified:** `backend/app/modules/mill_weighing/infrastructure/repository.py`, `backend/app/main.py`, `backend/alembic/env.py`, `backend/pyproject.toml`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0010_b9_finance` menambahkan sequence `invoice_seq` & `payment_seq`, 4 tabel (`invoices`, `invoice_lines`, `payment_approvals`, `payment_records`), partial unique index faktur aktif per rekonsiliasi+jenis & referensi bayar aktif, serta constraint DB `SOD-05`/`SOD-06`.
- **Dependencies:** Zero paket baru ditambahkan.
- **Features Implemented:** Siklus lengkap AR/AP `PENDING_VERIFICATION -> VERIFIED -> ISSUED`, persetujuan kewajiban Direksi `APPROVED != PAID`, pencatatan & verifikasi bukti transfer manual idempoten, penolakan parsial/lebih bayar/pasangan salah/tanpa approval/ganda, pembalikan `REVERSED`, privasi Jalur C Petani/Koperasi, & penguncian revisi tiket pasca-faktur terbit.
- **Bugs Found & Fixed:**
  1. Envelope idempotency metadata pada `SimpleSuccessMeta` bernama `idempotency_replayed` (sempat ditulis `idempotent_replay`) -> diselaraskan dan tervalidasi oleh `pyright` strict + test integrasi.
  2. Test finality tiket memanggil `PUT /api/v1/mill-tickets/{id}` sementara rute revisi OpenAPI memakai `PATCH /api/v1/mill-tickets/{id}` -> disesuaikan dan terverifikasi `409 MILL_TICKET_ALREADY_FINAL`.
- **Tests Executed:**
  - `.venv\Scripts\alembic.exe upgrade head` -> `downgrade -1` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\ruff.exe format --check .` & `ruff check .` -> **PASS** (`203 files already formatted`, `All checks passed!`)
  - `.venv\Scripts\pyright.exe` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 14 kept, 0 broken`, `200 files`, `928 dependencies`)
  - `.venv\Scripts\pytest.exe -v` -> **PASS** (`68 passed in 80.77s`: `43` unit, `3` architecture, `22` PostgreSQL/Redis integration; `0` failed, `0` skipped)
- **Counts:** `68` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B9_PASS — FINANCE_INVOICES_PAYMENTS_VERIFIED`)**.
- **Known Limitations:** Laporan agregat `FinanceReport` (`BR-MRG-005`), audit viewer, rule management, serta observability metrics dibangun pada `B10`.
- **Next Action:** Lanjut ke **`B10 — Reporting & Admin Audit/Rule/Health`** (`reporting` & `admin` modules + 8 operasi `/api/v1/reports/*` & `/api/v1/admin/{rule-versions,audit-events,system-health}`, Redis cache KPI scoped + fallback PG, `BR-SYS-002`, & redaksi log audit).

---

## B10 — Reporting & Admin Audit/Rule/Health

- **Milestone ID:** `B10`
- **Nama Milestone:** `Reporting & Admin Audit/Rule/Health`
- **Status:** **`B10_PASS — REPORTING_ADMIN_OBSERVABILITY_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Mengimplementasikan modul pelaporan dashboard agregat scoped (`reporting`: `/api/v1/reports/{overview,supply,reconciliation,finance}`), caching Redis per peran/scope dengan fallback mulus PostgreSQL saat Redis down, penandaan `BR-MRG-005` `Kontribusi Kotor Niaga (Data Simulasi - Bukan Laba Bersih)` & `is_net_profit: false`, serta modul administrasi tata kelola & observability (`admin`: `/api/v1/admin/{rule-versions,audit-events,system-health}`, `BR-SYS-002`, redaksi log audit, dan metrik CCTV Digital 24h non-transaksional).
- **Completed:**
  - [x] Core Observability Tracker (`app/core/observability.py`, `middleware.py`, `errors.py`): pelacakan rolling 24 jam jumlah HTTP request, insiden `5xx`, & korelasi `request_id`/`trace_id`/`error_code`/`module` tanpa menyimpan data rupiah atau PII.
  - [x] Modul `reporting` (4 layer): 4 endpoint OpenAPI dengan agregasi SQL mengecualikan baris `CANCELLED`, pemisahan scope `FARMER` / `COOPERATIVE` / `MILL` / `PERUMDA_GLOBAL`, pemblokiran laporan keuangan bagi peran non-Finance/non-Direksi, cache-aside Redis keyed per-scope + fallback PostgreSQL.
  - [x] Modul `admin` (4 layer): `GET/POST /api/v1/admin/rule-versions` yang menegakkan `BR-SYS-002` (`SYSTEM_ADMIN` & `PERUMDA_OPERATIONS` dilarang menerbitkan aturan `CONFIRMED`; transaksi historis mempertahankan snapshot `rule_version_id`), `GET /api/v1/admin/audit-events` berpaginasi & teredaksi dari password/rekening/token, serta `GET /api/v1/admin/system-health` eksklusif `SYSTEM_ADMIN`.
  - [x] Migrasi `0011_b10_reporting_indexes`: 5 composite index DBD §20.2 pada `delivery_orders`, `reconciliation_cases`, `audit_events`, `invoices`, & `payment_records`.
- **Files Created:**
  - `backend/alembic/versions/0011_b10_reporting_indexes.py`
  - `backend/app/core/observability.py`
  - `backend/app/modules/reporting/__init__.py`, `domain/` (`entities.py`, `rules.py`), `application/` (`ports.py`, `use_cases.py`), `infrastructure/` (`models.py`, `cache_adapter.py`, `repository.py`), `presentation/` (`schemas.py`, `router.py`)
  - `backend/app/modules/admin/__init__.py`, `domain/` (`entities.py`, `rules.py`), `application/` (`ports.py`, `use_cases.py`), `infrastructure/` (`models.py`, `observability_adapter.py`, `repository.py`), `presentation/` (`schemas.py`, `router.py`)
  - `backend/tests/unit/test_reporting_admin_unit.py`, `backend/tests/integration/test_reporting_admin_integration.py`
- **Files Modified:** `backend/app/core/middleware.py`, `backend/app/core/errors.py`, `backend/app/main.py`, `backend/pyproject.toml`, `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Migrasi `0011_b10_reporting_indexes` menambahkan index prioritas laporan & audit (`ix_delivery_orders_status_created`, `ix_reconciliation_cases_status_calculated`, `ix_audit_events_occurred_at`, `ix_invoices_date_type_status`, `ix_payment_records_date_dir_status`).
- **Dependencies:** Zero paket baru ditambahkan.
- **Features Implemented:** Overview dashboard terisolasi, laporan supply & rekonsiliasi mengecualikan `CANCELLED`, laporan keuangan terpisah (`AR vs Kas`, `AP approved-unpaid vs verified-paid`, `gross_contribution_simulation`), rule versioning tidak memutasi riwayat, redaksi audit log, & CCTV Digital observability.
- **Bugs Found & Fixed:** Signature `AuthenticatedPrincipal` dalam fixture test awal perlu diselaraskan ke `AccessScopeEntity` + field wajib `non_approver_admin` -> terdeteksi cepat oleh `pyright` sebelum pytest dijalankan.
- **Tests Executed:**
  - `.venv\Scripts\alembic.exe upgrade head` -> `downgrade -1` -> `upgrade head` (`agroniaga_dev` & `agroniaga_test`) -> **PASS** (`exit 0`)
  - `.venv\Scripts\ruff.exe format --check .` & `ruff check .` -> **PASS** (`235 files already formatted`, `All checks passed!`)
  - `.venv\Scripts\pyright.exe` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 16 kept, 0 broken`, `230 files`, `1082 dependencies`)
  - `.venv\Scripts\pytest.exe -v` -> **PASS** (`73 passed in 92.33s`: `46` unit, `3` architecture, `24` PostgreSQL/Redis integration; `0` failed, `0` skipped)
- **Counts:** `73` PASS, `0` FAIL, `0` SKIPPED.
- **Quality Gate:** **PASS (`B10_PASS — REPORTING_ADMIN_OBSERVABILITY_VERIFIED`)**.
- **Known Limitations:** Pengujian menyeluruh E2E conformance seluruh 95 operasi OpenAPI, pemutaran skenario error catalog, benchmark performa query (`EXPLAIN ANALYZE` + beban), serta simulasi backup/restore PostgreSQL dikerjakan sebagai gerbang final pada `B11`.
- **Next Action:** Lanjut ke **`B11 — Hardening, Security, DB Performance & Final Sign-Off`** untuk verifikasi `K1–K11`, 95 operasi OpenAPI, `contracts/fixtures/error-scenarios.json`, `EXPLAIN ANALYZE`, verifikasi `pg_dump` + restore DB terpisah, serta penandaan `BACKEND_INDEPENDENT_READY`.

---

## B11 — Hardening, Security, DB Performance & Final Sign-Off

- **Milestone ID:** `B11`
- **Nama Milestone:** `Hardening, Security, DB Performance & Final Sign-Off`
- **Status:** **`B11_PASS — BACKEND_INDEPENDENT_READY`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `0243982`
- **Tujuan:** Melaksanakan verifikasi pengerasan keamanan, kepatuhan penuh kontrak `openapi.v1.yaml` (`95` operasi), replay katalog error `contracts/fixtures/error-scenarios.json` (`22` skenario), audit dependensi, uji beban konkuren + PostgreSQL `EXPLAIN ANALYZE`, uji penuh E2E tanpa frontend lintas seluruh modul, serta uji backup & restore `pg_dump`/`pg_restore` guna menetapkan status **`BACKEND_INDEPENDENT_READY`** (`IPD §21`).
- **Completed:**
  - [x] Contract conformance 95 operasi OpenAPI + header `Idempotency-Key` pada seluruh 8 operasi idempoten + keselarasan 69 kode error & 22 skenario negatif `error-scenarios.json`.
  - [x] Uji penuh E2E tanpa frontend (`test_b11_full_e2e_supply_chain_and_security_headers`): Portal Publik -> Auth/CSRF & security headers -> Master Data -> Pricing `SM-01` -> TBS Receiving `SM-02` -> Kontrak & Kuota -> e-DO `SM-05` + QR -> Unggah Bukti + Tiket PKS `SM-06` -> Rekonsiliasi `SM-07` & Simulasi Alokasi -> Faktur AR + Pembayaran Masuk `SOD-06` + `BR-SYS-002` -> Reporting Keuangan `BR-MRG-005` -> Audit Log -> System Health Observability.
  - [x] Performance & concurrency benchmark: `60` request konkuren (`status=[200]`, `p50=533.83 ms`, `p95=696.78 ms`, `max=711.75 ms`) + `EXPLAIN (ANALYZE, FORMAT JSON)` query prioritas PostgreSQL 16 (`0.023 ms`–`0.596 ms` execution time).
  - [x] Backup & restore verification (`pg_dump` + `pg_restore` pada database sementara `agroniaga_restore_verify`, tervalidasi `48` tabel & `alembic_version=0011_b10_reporting_indexes`, kemudian database sementara dihapus bersih).
  - [x] Audit kompatibilitas paket (`uv pip check`: `114 packages`, seluruh dependensi kompatibel) + validasi kontrak M0.1 (`K1–K11`).
- **Files Created:**
  - `backend/tests/integration/test_b11_contract_conformance.py`
- **Files Modified:** `docs/IMPLEMENTATION_CHECKPOINTS.md`
- **Database Changes:** Tidak ada perubahan skema baru (`HEAD` tetap `0011_b10_reporting_indexes`); terverifikasi backup/restore penuh `343,788` bytes -> `48` tabel publik.
- **Dependencies:** Zero paket baru ditambahkan (`uv pip check` = `114 packages compatible`).
- **Features Implemented:** Rangkaian uji conformance & regresi final independen seluruh 11 modul domain + keamanan + performa + recovery.
- **Bugs Found & Fixed:** Uji awal E2E menyesuaikan payload kanonis (`partnership_status` pada PKS, `version` pada penimbangan, `/api/v1/receipts` + `Idempotency-Key`, `initial_quota_kg` pada kontrak, `IN_TRANSIT` lalu `/verify-qr` untuk `ARRIVED`, & `AllocationMode.SIMULATION`).
- **Tests Executed:**
  - `.venv\Scripts\ruff.exe format --check .` & `ruff check .` -> **PASS** (`236 files already formatted`, `All checks passed!`)
  - `.venv\Scripts\pyright.exe` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 16 kept, 0 broken`, `230 files`, `1082 dependencies`)
  - `.venv\Scripts\pytest.exe -v` -> **PASS** (`76 passed in 101.82s`: `46` unit, `3` architecture, `27` PostgreSQL/Redis integration; `0` failed, `0` skipped)
  - `python contracts\scripts\validate_contracts.py` & `python -m unittest discover -s contracts\tests -v` -> **PASS** (`K1–K11` = `0` issues, `11/11` tests `OK`)
  - PostgreSQL `EXPLAIN ANALYZE`: `tbs_receipts_coop` `0.569 ms`, `delivery_orders_status` `0.115 ms`, `reconciliation_status` `0.023 ms`, `invoices_agg` `0.596 ms`, `audit_events_recent` `0.093 ms`
  - Backup/Restore `pg_dump` -> `agroniaga_restore_verify` (`48` tables, `0011_b10_reporting_indexes`) -> **PASS**
- **Counts:** Backend `76` PASS / `0` FAIL / `0` SKIPPED; Contract validator `11` PASS / `0` FAIL.
- **Quality Gate:** **PASS (`B11_PASS — BACKEND_INDEPENDENT_READY`)**.
- **Known Limitations:** Seluruh aturan bisnis berstatus `PENDING_SOP` / `SIMULATION_ONLY` (model usaha `UNCONFIRMED`, toleransi susut `1,5000%`, grading `2%`, pembagian hasil multi-petani final, penolakan bayar parsial) tetap terisolasi secara eksplisit sesuai kontrak M0.1 dan **tidak** mensimulasikan transfer bank otomatis maupun kelayakan produksi keuangan nyata sebelum SOP Perumda disahkan.
- **Next Action:** Siap melanjutkan tahap **Frontend `F0–F11`** memakai API backend terverifikasi dan artefak kontrak `contracts/`.

---

## B11.1 — Post-Implementation Verification

- **Milestone ID:** `B11.1`
- **Nama Milestone:** `Post-Implementation Independent Audit & Verification`
- **Status:** **`READY — B11_1_POST_IMPLEMENTATION_VERIFIED`**
- **Tanggal:** `2026-11-11`
- **Baseline Commit:** `1b70664` (`branch: main`, ditambah patch perbaikan kerja lokal `B11.1` sebelum commit manual)
- **Tujuan:** Audit independen atas kesesuaian implementasi `B0–B11` terhadap kode sumber aktual, skema PostgreSQL 16 live, kontrak `openapi.v1.yaml` (`95` operasi), invarian keamanan & pemisahan kewenangan, kinerja/konkurensi/N+1, kebersihan repositori/environment, serta re-verifikasi penuh seluruh regresi.
- **Database Schema & Migrations Reconciliation (`agroniaga_dev` & `agroniaga_test`):**
  - Kedua database berada pada revisi Alembic `0011_b10_reporting_indexes (head)`.
  - Inspeksi katalog live PostgreSQL 16 mencatat tepat `48` tabel publik (`104` FK, `118` CHECK, `29` UNIQUE, `134` indeks dengan `10` indeks parsial): `46` tabel `DBD §4` (`CORE` + `SUPPORTING`) + `1` tabel audit transisi tambahan terverifikasi (`contract_approval_events` dari migrasi `0006`) + `1` tabel infrastruktur (`alembic_version`). Tepat `2` tabel `DBD §4` tetap berstatus `DEFERRED` sesuai `DBD §4.11` (`outbox_events`, `user_notifications`); `0` tabel tak terduga.
- **Clean Architecture & Dependency Direction:**
  - Audit AST atas seluruh `197` berkas Python di `backend/app/`: `0` siklus impor; `domain/` & `application/` bersih dari impor `infrastructure/` / `presentation/` / FastAPI / ORM / Redis.
  - `.venv\Scripts\lint-imports.exe` -> `Contracts: 16 kept, 0 broken` (`230 files, 1084 dependencies`).
- **Contract Parity & Runtime Live Schema Conformance (`95/95`):**
  - Perbaikan kontrak runtime **16 envelope `meta: null` -> `SimpleSuccessMeta`** (`master_data` `MillEnvelope`, `pricing` `InternalPriceEnvelope`, `tbs_receiving` `ReceiptEnvelope`, `contracts` `ContractEnvelope` / `QuotaPeriodListEnvelope` / `QuotaReservationEnvelope`, `logistics` `DeliveryOrderEnvelope`, `mill_weighing` `MillTicketEnvelope`, & `reconciliation` `ReconciliationEnvelope` / `AllocationListEnvelope`) sehingga cocok 100% dengan `$ref: #/components/schemas/SimpleSuccessMeta` non-nullable di `contracts/openapi.v1.yaml`.
  - Penambahan `test_b11_remaining_ops_schema_conformance_and_n1_budget` pada `backend/tests/integration/test_b11_contract_conformance.py` menutup cakupan live `2xx` untuk seluruh `23` operasi yang sebelumnya hanya tersentuh non-2xx / statis (`GET /health/live`, `listCooperatives`, `getFarmer`, `listFarms`, `listMillCompanies`, `updateMill`, `listVehicles`, `getPricingMetadata`, `listInternalPrices`, `getInternalPrice`, `updatePriceDraft`, `getPublicMillDetail`, `getPublicPriceDetail`, `listReceipts`, `cancelReceipt`, `listContracts`, `getContractDetail`, `listDeliveryOrders`, `listMillTickets`, `listReconciliations`, `calculateReconciliation`, `listUsers`, `listSystemRuleVersions`).
  - Hasil probe live FastAPI + `jsonschema.Draft202012Validator` (`audit_runtime_probe.py`): **`95/95` operasi OpenAPI tereksekusi dengan status `2xx`**, `0` operasi tersisa (`unhit_ops: []`, `non_2xx_only: {}`), & **`0` error JSON Schema** (`schema_errors_unique: []`).
- **Security, Integrity & Business-Rule Invariants:**
  - Scan AST hardcoded credentials di `backend/app/` & `backend/alembic/` bersih (literal hanya ada sebagai default lokal / validator guard staging-prod pada `backend/app/core/config.py`).
  - Terverifikasi lewat suite integrasi & unit: cookie `HttpOnly` + `SameSite=lax`, rotasi sesi saat re-login, pembatalan sesi instan saat akun `INACTIVE`/logout, penolakan `AUTH_CSRF_INVALID` (`403`) termasuk header `Origin` silang, rate limit login Redis (`429 AUTH_TOO_MANY_REQUESTS` + `Retry-After`), fail-closed Redis (`503 SYS_DEPENDENCY_UNAVAILABLE`), pembatasan lintas peran/cakupan (`AUTH_ACCESS_DENIED`, `AUTH_SCOPE_FORBIDDEN`), proteksi `BR-SYS-002` pada `SYSTEM_ADMIN`, maker != checker (`SOD-01..06`), proteksi file bukti + MIME magic bytes, append-only `audit_events` trigger PG, serta blokir `REC_WEIGHT_DISPUTE` / `REC_ALLOCATION_POLICY_UNCONFIRMED` / `APPROVED != PAID`. *(Catatan faktual: rate limiting terimplementasi pada endpoint login via `RedisLoginRateLimiter`; belum ada rate limiter generik terpisah pada endpoint tulis terautentikasi).*
- **N+1 Fixes, Deterministic Ordering & Benchmark Lokal (`agroniaga_test`):**
  - Perbaikan query **N+1** pada `SqlAlchemyLogisticsRepository.list_delivery_orders` dan `SqlAlchemyReconciliationRepository.list_cases` menjadi batch hydration (`_case_detail_stmt` / `_hydrate_case_rows` & `_do_detail_stmt` / `_hydrate_do_rows`) serta penyempurnaan urutan deterministik alokasi petani (`DeliveryOrderLineModel.created_at, TbsReceiptModel.receipt_number, DeliveryOrderLineModel.id` + offset mikrodetik pada `FarmerSettlementAllocationModel.created_at`). Terverifikasi otomatis `O(1)` query count (`p1 == p3`) dan `<= 5` query domain SQL per halaman.
  - Benchmark lokal terhadap `agroniaga_test` (`25` baris rantai pasok sintetis, `5` PKS/kuota publik, ASGI transport pada loopback Windows):
    - Public prices warm cache (`100` request, `10x10` konkuren): `0` error, `p50=25.175 ms`, `p95=38.990 ms` (`<= 1500 ms` TRD).
    - Public prices cache miss (`20` sekuensial): `0` error, `p50=6.504 ms`, `p95=18.110 ms`.
    - Public prices fallback saat Redis mati (`20` sekuensial): `0` error (`200 OK`), `p50=4039.275 ms`, `p95=4072.195 ms` *(disebabkan timeout koneksi Redis `REDIS_CONNECT_TIMEOUT_SECONDS=2.0` pada `get_cached_json` + `set_cached_json`; fallback fungsional namun latensi saat gangguan Redis mengikuti 2x timeout koneksi)*.
    - Daftar terautentikasi (`25` baris/halaman, `30` sekuensial): `delivery-orders` `p95=165.944 ms`, `reconciliations` `p95=56.774 ms`, `receipts` `p95=46.926 ms`; dashboard `overview` `p95=50.435 ms` & `finance` `p95=50.062 ms` (`<= 3000 ms` TRD pada dataset uji lokal).
    - Concurrency race reservasi kuota (`20` worker bersamaan ke sisa kuota `5000.000 kg`): `0` error tak terduga, tepat `5` `201 Created` & `15` `409 CON_INSUFFICIENT_QUOTA`, `p95=1077.563 ms`.
    - Idempotent receipt replay (`20` sekuensial): `0` error, ID identik + `idempotency_replayed=true`, `p95=63.481 ms`.
    - Kalkulasi rekonsiliasi (`15` kasus `READY`): `0` error, `p95=79.020 ms`.
    - *(Keterbatasan benchmark: dijalankan pada satu node lokal Windows + loopback + dataset sintetis kecil `25` baris; bukan pengganti uji beban multi-host berskala produksi).*
- **Files Modified in B11.1 (17 files):**
  - `backend/app/modules/{logistics,master_data,mill_weighing,pricing,tbs_receiving}/presentation/{router,schemas}.py`, `backend/app/modules/contracts/presentation/schemas.py`, & `backend/app/modules/reconciliation/presentation/schemas.py` (`meta: SimpleSuccessMeta` non-nullable conformance)
  - `backend/app/modules/reconciliation/infrastructure/repository.py` (batch list hydration + deterministic order)
  - `backend/app/modules/logistics/infrastructure/repository.py` (batch list hydration)
  - `backend/tests/integration/test_b11_contract_conformance.py` (live `95/95` conformance + Draft202012 validation + `O(1)` query budget)
  - `backend/README.md` (menambahkan `.venv\Scripts\lint-imports.exe`)
  - `docs/IMPLEMENTATION_CHECKPOINTS.md` (pembaruan status stale + checkpoint `B11.1`)
- **Tests Executed (Post-Edit Final Verification):**
  - `.venv\Scripts\ruff.exe format --check .` & `.venv\Scripts\ruff.exe check .` -> **PASS** (`236 files already formatted`, `All checks passed!`)
  - `.venv\Scripts\pyright.exe` -> **PASS** (`0 errors, 0 warnings, 0 informations`)
  - `.venv\Scripts\lint-imports.exe` -> **PASS** (`Contracts: 16 kept, 0 broken`, `230 files`, `1084 dependencies`)
  - `.venv\Scripts\pytest.exe -v` -> **PASS** (`77/77 passed`: `46` unit, `3` architecture, `28` integration; `0` failed, `0` skipped)
  - Runtime OpenAPI probe (`audit_runtime_probe.py`) -> **PASS** (`95/95` `2xx`, `0` unhit, `0` JSON Schema errors)
  - `python contracts\scripts\validate_contracts.py` & `python -m unittest discover -s contracts\tests -v` -> **PASS** (`11/11` OK)
- **Final Verdict:** **`READY — B11_1_POST_IMPLEMENTATION_VERIFIED`**
- **Next Action:** Siap melanjutkan tahap **Frontend `F0–F11`** (atau melakukan `git commit` terkelola atas perbaikan `B11.1` sesuai kebutuhan workflow developer).

---

## FRONTEND DEVELOPMENT TRACK (`F0–F11`)

### Checkpoint F0 — Project Foundation (`PASS — F0_FOUNDATION_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/`):**
  - Konfigurasi strict TypeScript (`strict: true`, `erasableSyntaxOnly: true`, `verbatimModuleSyntax: true`), Vite 8 proxy `/api` & `/health` -> `127.0.0.1:8000`, Vitest + Testing Library + Playwright config, ESLint (`eslint-config-prettier`), dan Tailwind CSS v4 dengan seluruh semantic token FigCraft D5 pada `src/styles/tokens.css`.
  - Codegen tipe OpenAPI `src/lib/api/generated.d.ts` langsung dari `contracts/openapi.v1.yaml` via `npm run codegen:api`.
  - Infrastruktur inti: `src/lib/config/env.ts` (pemisahan tegas `VITE_API_MODE=mock|real` tanpa silent mock fallback), `src/lib/decimal/precision.ts` (`decimal.js` + zona waktu WIB `Asia/Jakarta`), `src/lib/errors/errorCatalog.ts` (`69/69` kode error), `src/lib/auth/permissions.ts` (`PUBLIC` + `7` peran, `26` rute `AFD §36`, `BR-SYS-002`), `src/lib/api/client.ts` (cookie credentials, auto-CSRF + 1x retry `403 AUTH_CSRF_INVALID`, `401` cache purge, dan `Idempotency-Key` persisten per-aksi), `src/app/router/router.tsx` (`26` rute lazy-loaded dengan guard autentikasi & peran), serta `src/mocks/` (`MSW v3` + `mockDb` dari `contracts/fixtures/*.json`).
- **Hasil Verifikasi F0 (Post-Edit):**
  - `npm.cmd run typecheck` (`tsc -b`) -> **PASS** (`0` error)
  - `npm.cmd run lint` (`eslint .`) -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` (`vitest run`) -> **PASS** (`7/7` tests passed in `src/test/f0-foundation.test.ts`)
  - `npm.cmd run build` (`tsc -b && vite build`) -> **PASS**
  - Catatan regresi kontrak (`python contracts/scripts/validate_contracts.py`): `K1–K9` & `K11` **PASS**; `K10_scope_and_hygiene` menandai keberadaan `frontend/` yang memang diharapkan saat track frontend dimulai.

### Checkpoint F1 — Design System & Atomic Components (`PASS — F1_DESIGN_SYSTEM_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/components/`):**
  - **Atoms (`atoms/`):** `Button` (min-height `44px`, spinner loading), `Input`, `Select`, `Textarea`, `Label`, `Badge`, `Checkbox`, `Spinner`, `SkeletonRow`.
  - **Molecules (`molecules/`):** `FormField`, `SearchField`, `PriceDisplay` (format `Rp/kg` presisi & tanggal WIB), `StatusIndicator` (`statusMeta.ts` mencakup `SM-01..SM-11` + `Data Simulasi`/`Pending SOP`), `WeightInputGroup` (pratinjau Netto berbasis `Decimal` + batas `Tara <= Bruto` sesuai `BR-TBS-004`), `DateRangeFilter`, `PaginationControl`, `LocationLink` (koordinat terverifikasi vs penegasan tanpa pin perkiraan `BR-PUB-004`), `PolicyNoticeBanner`.
  - **Organisms (`organisms/`):** `PublicNavbar`, `PublicFooter`, `InternalSidebar` (panel gelap `#12231B`, teks `#B8C7BE`, banner non-approver `BR-SYS-002`, laci mobile Escape-accessible), `PageHeader`, `KPIGrid`, `FilterPanel`, `FormSection`, `DataTable` (`overflow-x-auto`), `ConfirmDialog` (Escape + alasan audit wajib), `StatusTimeline`, `StateFeedbackCard` (menampilkan pesan aman + `request_id`).
  - **Templates (`templates/`):** `PublicTemplate`, `AuthTemplate`, `InternalAppShell` (dengan lencana mode `MODE SIMULASI (MSW)` vs `LIVE FASTAPI`), `DashboardTemplate`, `TransactionTemplate`, `DataManagementTemplate`, `ExecutiveTemplate`.
- **Hasil Verifikasi F1 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`12/12` passed across `f0-foundation.test.ts` & `f1-design-system.test.tsx`)
  - `npm.cmd run build` -> **PASS** (`35.00 kB` CSS / `7.23 kB` gzip; `index` `11.20 kB` gzip; `vendor-react` `64.49 kB` gzip).

### Checkpoint F2 — Portal Publik 7 Rute Tanpa Login (`PASS — F2_PUBLIC_PORTAL_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/public/`):**
  - `api/publicApi.ts`: React Query hooks untuk 7 endpoint publik OpenAPI (`prices`, `disbun-prices`, `mills`, `mill detail`, `profile`, `notices`).
  - `pages/HomePage.tsx` (`/`), `HargaTbsPage.tsx` (`/harga-tbs`), `PksDetailPage.tsx` (`/pks/$id`), `LokasiPksPage.tsx` (`/lokasi-pks`), `TentangPage.tsx` (`/tentang`), `KemitraanPage.tsx` (`/kemitraan`), `KontakPage.tsx` (`/kontak`).
  - `components/PksLocationMap.tsx`: lazy-loaded `maplibre-gl` (`vendor-maplibre` terisolasi hanya pada `/lokasi-pks`), fallback aman saat WebGL tidak tersedia, & kepatuhan `BR-PUB-004` / `DEC-014` (tanpa pin perkiraan untuk koordinat yang belum diverifikasi).
- **Hasil Verifikasi F2 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`16/16` passed across `f0-foundation.test.ts`, `f1-design-system.test.tsx`, & `f2-public-portal.test.tsx`, memverifikasi `404` PKS `is_public=false`, pemisahan harga Disbun vs PKS, filter kedaluwarsa, & 7 rute publik)
  - `npm.cmd run build` -> **PASS** (`vite build` `1.71s`; lazy chunk per halaman publik `0.92–2.67 kB` gzip).

### Checkpoint F3 — Autentikasi & App Shell (`PASS — F3_AUTH_SHELL_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/auth/` & `frontend/src/app/router/`):**
  - `pages/LoginPage.tsx`: validasi React Hook Form + Zod, pengamanan redirect `?next=` khusus rute `/app/*` yang sesuai izin peran (`canAccessRoutePath`), penanganan generik `401` tanpa enumerasi username, serta quick-actor simulasi MSW yang otomatis tersembunyi pada `VITE_API_MODE=real`.
  - Guard terproteksi pada seluruh `18` rute internal `AFD §36` via `resolveSessionUser` + `ForbiddenRoleView` (`403`).
- **Hasil Verifikasi F3 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`19/19` passed across `f0`, `f1`, `f2`, & `f3-auth-shell.test.tsx`)
  - `npm.cmd run build` -> **PASS** (`vite build` `1.69s`; `LoginPage` `2.59 kB` gzip).

### Checkpoint F4 — Master Data UI (`PASS — F4_MASTER_DATA_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/master-data/`, `cooperative/`, `perumda/`):**
  - `FarmerFarmSection.tsx` (`FLOW-05`), `MillMasterSection.tsx` (`FLOW-06`), `FleetMasterSection.tsx`, `KoperasiHomePage.tsx` (`/app/koperasi`), `PerumdaDashboardPage.tsx` (`/app/perumda`), serta stateful MSW `masterDataHandlers.ts` dengan proteksi cakupan koperasi/PKS dan validasi `version` + koordinat berpasangan.
- **Hasil Verifikasi F4 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`21/21` passed termasuk uji `f4-master-data.test.tsx` untuk `FLOW-05` & `FLOW-06`)
  - `npm.cmd run build` -> **PASS** (`vite build` `1.45s`).

### Checkpoint F5 — Manajemen Harga Multi-PKS (`PASS — F5_PRICING_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/pricing/`):**
  - `api/pricingApi.ts`, `pages/PerumdaPricingPage.tsx` (`/app/perumda/harga`), & `src/mocks/handlers/pricingHandlers.ts` dengan seluruh transisi status harga `SM-01_PRICE_QUOTE`, blokir self-verify `AUTH_CONFLICT_OF_DUTIES`, serta formulir acuan Disbun terpisah.
- **Hasil Verifikasi F5 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`22/22` passed termasuk uji E2E internal `f5-pricing.test.tsx`)
  - `npm.cmd run build` -> **PASS** (`vite build` `1.39s`; `PerumdaPricingPage` `4.09 kB` gzip).

### Checkpoint F6 — Penerimaan, Penimbangan & Grading TBS (`PASS — F6_RECEIVING_GRADING_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/receiving/`):**
  - `api/receivingApi.ts`, `pages/KoperasiReceivingPage.tsx` (`/app/koperasi/penerimaan`), & `src/mocks/handlers/receivingHandlers.ts` (idempotency pada `createReceiptDraft`, presisi `Decimal` 3 desimal untuk kg & 4 desimal untuk `%` grading, penegakan `TBS_INVALID_WEIGHT` dan `TBS_RECEIPT_LOCKED`).
- **Hasil Verifikasi F6 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`23/23` passed termasuk `f6-receiving.test.tsx`)
  - `npm.cmd run build` -> **PASS** (`vite build` `2.27s`; `KoperasiReceivingPage` `4.02 kB` gzip).

### Checkpoint F7 — Kontrak, Kuota & Logistik e-DO (`PASS — F7_CONTRACTS_LOGISTICS_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/logistics/`):**
  - `api/logisticsApi.ts`, `PerumdaContractsPage.tsx` (`/app/perumda/kontrak`), `KoperasiSuratJalanPage.tsx` (`/app/koperasi/surat-jalan`), `PerumdaLogistikPage.tsx` (`/app/perumda/logistik`), & `src/mocks/handlers/logisticsHandlers.ts`.
  - Memisahkan akses koperasi agar tidak memuat endpoint komersial `GET /api/v1/contracts` yang khusus `PERUMDA_*` / `DIRECTOR`, sambil mencegah double allocation & kuota berlebih secara idempoten.
- **Hasil Verifikasi F7 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`25/25` passed termasuk `f7-contracts-logistics.test.tsx`)
  - `npm.cmd run build` -> **PASS** (`vite build` `1.49s`).

### Checkpoint F8 — Timbang PKS & Rekonsiliasi Berat (`PASS — F8_MILL_RECONCILIATION_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/mill/` & `frontend/src/features/reconciliation/`):**
  - `MillOperatorPortalPage.tsx` (`/app/pks`), `MillTicketsPage.tsx` (`/app/pks/tiket-timbang`), `PerumdaReconciliationPage.tsx` (`/app/perumda/rekonsiliasi`), `reconciliationApi.ts`, & `src/mocks/handlers/reconciliationHandlers.ts`.
  - Mendukung unggah bukti `FormData` `/api/v1/files`, toleransi simulasi `1,5000%`, deteksi anomali selisih negatif (`mill > origin`), penyelesaian sengketa beraudit alasan wajib, & blokir finalisasi alokasi multi-petani (`REC_ALLOCATION_POLICY_UNCONFIRMED`).
- **Hasil Verifikasi F8 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`27/27` passed termasuk `f8-mill-reconciliation.test.tsx`)
  - `npm.cmd run build` -> **PASS** (`vite build` `1.29s`).

### Checkpoint F9 — Keuangan, Faktur, Pembayaran, Persetujuan Direksi & Petani (`PASS — F9_FINANCE_APPROVAL_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/finance/`, `director/`, `farmer/`):**
  - `financeApi.ts`, `PerumdaFinancePage.tsx` (`/app/perumda/pembayaran`), `DireksiPersetujuanPage.tsx` (`/app/direksi/persetujuan`), `PetaniDashboardPage.tsx` (`/app/petani`), `PetaniPanenPage.tsx` (`/app/petani/panen`), & `src/mocks/handlers/financeHandlers.ts`.
  - Menegakkan pemisahan faktur piutang (`AR`), hutang (`AP`) yang eksplisit bertanda `Pending SOP`, pembayaran ke petani idempoten anti-double disbursement (`409 FIN_PAYMENT_DOUBLE_DISBURSEMENT`), verifikasi Maker != Checker (`403 AUTH_CONFLICT_OF_DUTIES`), persetujuan khusus `DIRECTOR`, & portal `FARMER` read-only `own_scope`.
- **Hasil Verifikasi F9 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`29/29` passed termasuk `f9-finance-approvals.test.tsx`)
  - `npm.cmd run build` -> **PASS** (`vite build` `1.70s`).

### Checkpoint F10 — Dashboard Analitik, Observabilitas & Portal Admin Sistem (`PASS — F10_DASHBOARDS_ADMIN_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Artefak Inti (`frontend/src/features/reports/`, `director/`, `admin/`, & `mocks/handlers/adminReportsHandlers.ts`):**
  - `reportsApi.ts`, `adminApi.ts`, `DireksiDashboardPage.tsx` (`/app/direksi`), `AdminDashboardPage.tsx` (`/app/admin`), `AdminPenggunaPage.tsx` (`/app/admin/pengguna`), `AdminAuditPage.tsx` (`/app/admin/audit`), pengayaan KPI `/app/perumda`, & registrasi penuh `routePageRegistry.tsx` (**26/26 rute kanonis AFD §36 tanpa stub**).
  - Menegakkan `BR-MRG-005` (`is_net_profit: false` & label `Kontribusi Kotor Niaga (Data Simulasi - Bukan Laba Bersih)`), isolasi `SYSTEM_ADMIN` non-transaksional (`BR-SYS-002` blokir `CONFIRMED` -> `403 AUTH_OPERATION_FORBIDDEN`), pencabutan sesi beraudit wajib alasan, versi aturan append-only (`system_rule_versions`), & audit log append-only teredaksi.
- **Hasil Verifikasi F10 (Post-Edit):**
  - `npm.cmd run typecheck` -> **PASS** (`0` error)
  - `npm.cmd run lint` -> **PASS** (`0` error, `0` warning)
  - `npm.cmd test` -> **PASS** (`11/11` file, `32/32` passed termasuk `f10-dashboards-admin.test.tsx`)
  - `npm.cmd run build` -> **PASS** (`vite build` `1.45s`).

### Checkpoint F11 — UI/UX Hardening, Live FastAPI Integration, Playwright E2E, Visual QA & Final Sign-Off (`READY — FRONTEND_BACKEND_INTEGRATION_VERIFIED`)
- **Tanggal:** `2026-11-11`
- **Hardening & Perbaikan Integrasi Nyata (`frontend/`):**
  - Menyelaraskan parameter query API ke kontrak M0.1 / FastAPI: `/api/v1/public/prices` & `/api/v1/public/mills` & `/api/v1/farmers` & `/api/v1/mills` menggunakan `q`, `sort_by` (`price_per_kg`/`mill_name`/`updated_at`), & `sort_dir` (`asc`/`desc`) sehingga integrasi langsung `HomePage` terhadap FastAPI bebas error validasi `VAL_INVALID_FORMAT`.
  - Menambahkan `optimizeDeps: { exclude: ['maplibre-gl'] }` pada `frontend/vite.config.ts` untuk meniadakan error dev worker `504` pada `/lokasi-pks`.
  - Menambahkan dukungan input UUID kontrak penugasan pada `KoperasiSuratJalanPage.tsx` saat koperasi belum memiliki e-DO teralokasi (menjaga isolasi `contracts.read` koperasi) dan guard `farmers.read` pada `PerumdaDashboardPage.tsx` bagi `PERUMDA_FINANCE`.
  - Menambahkan `shrink-0 whitespace-nowrap` badge `FormSection` serta dead-code guard `import.meta.env.VITE_API_MODE !== 'real'` pada `src/main.tsx` sehingga build `VITE_API_MODE=real` menyingkirkan modul MSW sepenuhnya dari bundle produksi.
- **Hasil Verifikasi Akhir F11 & Lintas Stack:**
  - `VITE_API_MODE=real npm.cmd run build` -> **PASS** (`1.54s`, `0` chunk MSW/browser).
  - `npm.cmd run typecheck` (`tsc -b`) -> **PASS** (`0` error).
  - `npm.cmd run lint` (`eslint .`) -> **PASS** (`0` error, `0` warning).
  - `npm.cmd test` (`vitest run`) -> **PASS** (`11/11` file, `32/32` passed).
  - `npm.cmd run build` -> **PASS** (`1.47s`).
  - `npm.cmd run test:e2e` (`playwright test` live against FastAPI Uvicorn + PostgreSQL 16.15 + Redis 7, `VITE_API_MODE=real`) -> **PASS** (`2/2` suite lulus: portal publik 7 rute, login/cookie/CSRF/reload persistensi, `SYSTEM_ADMIN` Non-Approver + rule versioning, Koperasi penerimaan->timbang->validasi->e-DO, & Dashboard Direksi `BR-MRG-005`; `0` `mockServiceWorker.js`, `0` `pageerror`, `0` HTTP `>=500`, `0` overflow `1440px`/`375px`).
  - Audit aksesibilitas `axe-core` WCAG 2.2 AA via Playwright (`Home 1440px`, `Home 375px`, `Harga TBS 375px`, `Login 1440px`, `Admin Dashboard 1440px`, `Director Dashboard 1440px`) -> **PASS** (`0` pelanggaran `critical` atau `serious`).
  - Inspeksi visual screenshot nyata (`f11-public-home-desktop.png`, `f11-koperasi-receiving-mobile.png`, `f11-admin-dashboard-desktop.png`, `f11-director-dashboard-desktop.png`) selaras palet/hirarki FigCraft D5; **0** temuan antislop (`—` em-dash / stub tersisa).
  - Regresi backend (`backend\.venv\Scripts\python.exe -m pytest -q`) -> **PASS** (`77/77 passed`), tanpa perubahan sumber `backend/`, `contracts/`, atau 6 dokumen `V1.1`.
- **Status Akhir Track Frontend (`F0–F11`):** **`READY — FRONTEND_BACKEND_INTEGRATION_VERIFIED`** *(seluruh indikator simulasi & elemen `Pending SOP` dipertahankan eksplisit menunggu pengesahan operasional Perumda sebelum rilis produksi).*

---

### Checkpoint F11.1 — Final Frontend UAT & Integration Verification (`READY — F11_1_FULL_INTEGRATION_AND_UX_VERIFIED`)

- **Tanggal:** 2026-11-11
- **Lingkup Verifikasi & Isolasi Lingkungan:** Audit end-to-end terintegrasi terhadap backend FastAPI (`127.0.0.1:8000`) terhubung ke database uji terisolasi **`agroniaga_test`** pada PostgreSQL **16.15** (Ubuntu/WSL2 `127.0.0.1:15432`, revisi `0011_b10_reporting_indexes`) dan **Redis `/1`**, serta frontend React (`VITE_API_MODE=real` tanpa MSW di `:5173`). `agroniaga_dev`, kode `backend/`, dokumen kanonis `V1.1`, dan spesifikasi bisnis kontrak tidak disentuh. Penyesuaian tooling `K10` pada `contracts/scripts/validate_contracts.py` & `contracts/tests/test_contracts.py` hanya menyelaraskan validasi artefak F0–F11.1.
- **Temuan Nyata & Perbaikan Frontend yang Dieksekusi:**
  1. `frontend/src/features/finance/pages/PerumdaFinancePage.tsx`: Menambahkan dukungan status backend nyata `PENDING_VERIFICATION` pada tombol `Verifikasi` faktur (sebelumnya hanya tampil untuk `DRAFT` di MSW sehingga alur verifikasi checker AR/AP terblokir di mode live), menyamakan pencarian pihak `UNCONFIRMED`/`SELLER`/`BUYER` ke `contractWithParties`, membatasi fallback UUID mock hanya saat `isMockApiMode()`, serta menambahkan status unggahan bukti bayar (`uploadedProofName`) dan kunci tombol submit saat `uploadFile.isPending`.
  2. `frontend/src/features/mill/pages/MillTicketsPage.tsx`: Menambahkan dukungan status tiket timbang backend nyata `SUBMITTED` + `t.is_current` pada tombol `Verifikasi Final` (sebelumnya hanya tampil pada `DRAFT`).
  3. `frontend/src/features/reconciliation/pages/PerumdaReconciliationPage.tsx`: Menghubungkan aksi `REC-01` (`useDeliveryOrders` + `useTriggerReconciliation()` ke `POST /api/v1/reconciliations`) agar operator Perumda dapat memicu kalkulasi rekonsiliasi secara penuh melalui UI.
  4. `frontend/src/features/logistics/pages/KoperasiSuratJalanPage.tsx` & `frontend/src/features/logistics/api/logisticsApi.ts`: Menambahkan opsi `__CUSTOM__` (`#edo-contract-custom`) saat `!canReadContracts && assignedContractIds.length > 0` untuk pemasukan UUID kontrak kedua, serta parameter opsional `enabled = true` pada `useDeliveryOrders`.
  5. `frontend/src/features/logistics/pages/PerumdaContractsPage.tsx`: Menjaga agar nilai fallback UUID mock hanya dipakai ketika `isMockApiMode()` aktif.
  6. `frontend/src/components/organisms/PublicNavbar.tsx`, `frontend/src/components/organisms/InternalSidebar.tsx`, & `frontend/src/components/templates/InternalAppShell.tsx`: Menambahkan `activeOptions={{ exact: ... }}` pada `<Link>` portal publik dan rute dasar portal internal agar atribut `aria-current="page"` tetap unik (`1` tautan aktif), serta id `#mobile-portal-menu-trigger` (`aria-expanded`), penutupan drawer `Escape`, dan pemulihan fokus ke tombol pemicu.
  7. `frontend/src/components/organisms/ConfirmDialog.tsx`: Menambahkan fokus awal otomatis pada field alasan/`Batal`, penutupan `Escape`, dan pemulihan fokus (`previousActive`) saat dialog ditutup.
  8. `frontend/src/components/organisms/DataTable.tsx` & `frontend/src/features/admin/pages/AdminPenggunaPage.tsx`: Menambahkan `tabIndex={0}`, `role="region"`, `aria-label={caption}`, `min-w-0`, dan fokus ring pada kontainer tabel agar lolos aturan WCAG `scrollable-region-focusable`, serta `min-w-0` dan `break-all` pada layout grid `/app/admin/pengguna` untuk meniadakan overflow horizontal (`scrollWidth 740 -> <=390`) di viewport mobile.
  9. `frontend/src/features/perumda/pages/PerumdaDashboardPage.tsx` & `frontend/src/features/master-data/api/masterDataApi.ts`: Menjaga tab `Armada & Supir` di `/app/perumda` agar hanya tampil ketika `vehicles.read` tersedia (`canReadVehicles`) dan menambah parameter `enabled = true` pada `useMillCompanies`.
- **Catatan Model Pembayaran Baseline (Observed Behavior):** Sesuai desain backend B9 (`backend/app/modules/finance/infrastructure/repository.py`), pembayaran faktur AP Koperasi (`Perumda -> Koperasi`, `creditor_party_id = cooperative.party_id`) terlihat oleh akun Koperasi pada `GET /api/v1/payments`, sedangkan portal Petani (`/app/petani/panen`) hanya menampilkan `PaymentRecord` `OUTBOUND` dengan `payee_party_id` milik petani langsung apabila faktur Jalur C petani diterbitkan.
- **Verifikasi Clean-Room Setelah Edit Terakhir:**
  - `npm.cmd run test:e2e` (live FastAPI + PostgreSQL 16.15 `agroniaga_test` + Redis `/1`, DB di-reseed bersih): **PASS — `11 passed (4.2m)`, `0` skipped, `0` failed** (`f11-1-roles-rbac.spec.ts` matriks auth/RBAC 7 peran + 403 API + cookie reload + logout/expiry, `f11-1-routes-a11y-visual.spec.ts` **26 rute x 5 viewport `1440/1280/768/390/375` (`0` overflow)** + `axe-core` WCAG 2.2 AA (`0` critical/serious) + keyboard/Escape focus restore + `prefers-reduced-motion` + 12 screenshot UI, `f11-1-workflows.spec.ts` Workflow A-F lengkap termasuk SoD `AUTH_CONFLICT_OF_DUTIES`, `PAY_APPROVAL_REQUIRED`, `PAY_PARTIAL_NOT_SUPPORTED`, `PAY_DUPLICATE_PAYMENT`, `CONTRACT_QUOTA_EXCEEDED`, `MILL_EDO_MILL_MISMATCH`, `DISPUTE_HOLD`, `FIN_POLICY_UNCONFIRMED`, `SYS_POLICY_APPROVAL_FORBIDDEN`, dan pencabutan sesi instan `INACTIVE`, serta `full-integration.spec.ts` regresi F11).
  - Seluruh proses server UAT sementara (`task-4535` Uvicorn & `task-5327` Vite) dihentikan bersih; port `:8000` dan `:5173` terverifikasi bebas tanpa listener tersisa.
  - `npm.cmd run typecheck` (`tsc -b`) -> **PASS** (`0` error); `npm.cmd run lint` (`eslint .`) -> **PASS** (`0` error).
  - `npm.cmd test` (`vitest run`) -> **PASS** (`11` test file, `32/32` test passed dalam `78.37s`).
  - `$env:VITE_API_MODE='real'; npm.cmd run build` -> **PASS** (`built in 2.00s`); inspeksi `dist/assets` memastikan **0** berkas/chunk `msw` atau mock ter-bundle.
  - `python contracts\scripts\validate_contracts.py` -> **PASS** (`K1–K11 PASS`, `TOTAL ISSUES: 0`); `python -m unittest discover -s contracts\tests -v` -> **PASS** (`13/13 OK` dalam `12.309s`).
  - `backend\.venv\Scripts\python.exe -m pytest -q` -> **PASS** (`77 passed in 124.54s`, `0` skipped, `0` failed).
- **Status Akhir Track Frontend (`F0–F11.1`):** **`READY — F11_1_FULL_INTEGRATION_AND_UX_VERIFIED`** *(seluruh indikator simulasi & elemen `Pending SOP` tetap dipertahankan eksplisit menunggu pengesahan operasional Perumda).*

---

### LOCAL-DEMO-01 — Real API + Faker Seed + One-Command Launch (`READY — LOCAL_DEMO_REAL_API_VERIFIED`)

- **Tanggal:** 2026-11-11
- **Tujuan & Batasan Isolasi:** Menyediakan lingkungan demo lokal Windows 11 satu perintah (*Real API, Real PostgreSQL, Real Redis, Tanpa MSW/Mock*) agar pengguna nonteknis dapat menjalankan seluruh alur 7 peran secara aman tanpa menyentuh `agroniaga_dev`, `agroniaga_test`, Redis `/0`, Redis `/1`, 6 dokumen baseline `V1.1`, kontrak bisnis M0/M0.1, ataupun desain FigCraft D5.
- **Arsitektur & Pemisahan Lingkungan (`env.demo`):**
  - **PostgreSQL 16.15 (`127.0.0.1:15432`):** Database **`agroniaga_demo`** (owner/role terbatas `agroniaga_demo` dengan `NOSUPERUSER NOCREATEDB NOCREATEROLE`, hak akses dicabut pada `agroniaga_dev`/`agroniaga_test`), bermigrasi hingga `HEAD` **`0011_b10_reporting_indexes`**.
  - **Redis (`127.0.0.1:6379/2`):** Database **`/2`** terisolasi untuk sesi autentikasi demo, CSRF/rate limiter, dan cache portal publik/reporting (`ts_agroniaga_demo_session`, `LOGIN_IP_RATE_LIMIT_MAX_ATTEMPTS=120` khusus profil demo lokal).
  - **Konfigurasi Gitignored:** `backend/.env.demo` (dibangkitkan dari template tracked `backend/.env.demo.example` dengan password acak CSPRNG dan `SESSION_SECRET`), `backend/.demo-credentials.local.txt`, `backend/var/demo_evidence_files/`, dan `.demo-state/` diabaikan via `.gitignore` + `backend/.gitignore`.
  - **Penanda Visual Demo Terpisah dari API Mode:** Menambahkan `isDemoBannerEnabled()` (`frontend/src/lib/config/env.ts`, membaca `VITE_DEMO_BANNER === 'true'`) dan `<DemoModeBanner variant="bar" | "badge" />` pada `PublicTemplate`, `AuthTemplate`, serta `InternalAppShell` tanpa mengubah perilaku atau bundel `VITE_API_MODE=real`.
- **Faker Seeder Idempotent (`backend/scripts/seed_demo.py`, `faker==39.1.0` `id_ID`, `DEMO_SEED=20261111`):**
  - Guard target ketat: menolak berjalan apabila `DATABASE_URL` tidak berakhir pada `/agroniaga_demo` atau `REDIS_URL` bukan `/2`, serta mengosongkan `TEST_DATABASE_URL`/`TEST_REDIS_URL` agar tidak fallback ke `agroniaga_test`.
  - Idempotent penuh: saat data demo terdeteksi (`mill_companies > 0`), eksekusi default melewati penulisan ulang dan memvalidasi integritas; opsi reset (`--reset-demo --confirm-reset agroniaga_demo`) hanya mengosongkan tabel non-alembic di `agroniaga_demo` + Redis `/2`.
  - **Ringkasan Record Seed Baseline (`agroniaga_demo`) & Skenario Terhubung (Skenario A–G):**
    - `mill_companies`: **5** | `mills`: **5** (`PKS-DEMO-01..04` publik termasuk `1` koordinat belum terverifikasi + `PKS-DEMO-05` privat) | `perumda_offices`: **2**
    - `cooperatives`: **4** | `farmers`: **60** | `cooperative_memberships`: **60** | `farms`: **75** | `vehicles`: **12** | `drivers`: **12** | `user_accounts`: **12** (mencakup 7 peran resmi, maker/checker, serta akun lintas koperasi & lintas PKS dengan hash **Argon2id** dan email `@demo.example.invalid`)
    - `mill_price_quotes`: **20** (`DRAFT`, `PENDING_VERIFICATION`, `VERIFIED`, `PUBLISHED`, `REVOKED`, `EXPIRED`) | `disbun_reference_prices`: **3** (terpisah dari kutipan PKS `BR-004`)
    - `trade_contracts`: **8** (`ACTIVE PRINCIPAL`, termasuk kontrak hampir penuh `KTR-DEMO-NEAR-02` ~85%, `ACTIVE UNCONFIRMED` `KTR-DEMO-UNC-06`, `PENDING_APPROVAL` `KTR-DEMO-PEND-07`, & `DRAFT` `KTR-DEMO-DRF-08`)
    - `tbs_receipts`: **80** baseline (**83** setelah uji UI live; kombinasi `ALLOCATED`, `VALIDATED`, & `DRAFT`, revisi timbang & grading simulasi bertanda `NET_WEIGHT_BEFORE_GRADING`, 0 `tare > bruto`) | `delivery_orders`: **18** (`DRAFT`, `READY`, `IN_TRANSIT`, `ARRIVED`, `RECEIVED`; **0** alokasi receipt ganda)
    - `mill_weighing_tickets`: **13** (termasuk 1 revisi berantai `WB-DEMO-001`) | `reconciliation_cases`: **10** (`MATCHED`, `DISPUTE_HOLD`, `UNDER_REVIEW`, `RESOLVED`) | `farmer_settlement_allocations`: **5** simulasi
    - `invoices`: **7** (AR & AP terpisah; `APPROVED != PAID`; draft `UNCONFIRMED` tertahan sebagai `PENDING_SOP`) | `payment_approvals`: **2** | `payment_records`: **1** (`SIM-DEMO-TRF-0002` simulasi Jalur C untuk `demo_petani_01` tanpa transfer perbankan nyata) | `audit_events`: **528** baseline (**563** pasca-verifikasi UAT)
- **Launcher Windows 11 (`scripts/_demo-common.ps1`, `demo-setup.ps1`, `demo-start.ps1`, `demo-stop.ps1` + `README.md`):**
  - Kompatibel Windows PowerShell 5.1 & PowerShell 7: memeriksa Python `.venv`, Node/npm, PostgreSQL `15432`, dan Redis `/2`; memicu Uvicorn dengan `--loop asyncio:SelectorEventLoop` (mencegah `ProactorEventLoop` + `psycopg` `InterfaceError` di Windows), menjalankan Vite `VITE_API_MODE=real` + `VITE_DEMO_BANNER=true`, mendukung pemilihan port alternatif aman bila `:8000`/`:5173` dipakai proses pengguna lain (`5173 -> 5174` tanpa menyentuh `node PID 8968` di port `:5173`), dan menyimpan pelacakan `pid + startTimeUtc` di `.demo-state/pids.json` agar `demo-stop.ps1` hanya menghentikan proses demo miliknya.
  - Perbaikan dukungan lingkungan dev pada `frontend/vite.config.ts`: membaca `VITE_DEV_PROXY_TARGET` (default tetap `http://127.0.0.1:8000`).
- **Hasil Verifikasi Menyeluruh Pasca-Edit Akhir:**
  - **Idempotensi & Isolasi Database/Redis:** `.\scripts\demo-setup.ps1` run ke-2 mencetak `DEMO_SEED_SKIPPED_ALREADY_POPULATED` dengan jumlah stabil; `seed_demo.py --verify-only` melaporkan **`DEMO_INTEGRITY_VERIFIED`** (`bad_weights=0`, `double_allocs=0`, `unconf_issued=0`, `bad_rules=0`, `dispute_invoices=0`). `agroniaga_dev` tetap **9** `user_accounts`, Redis `/0` (**0** keys) dan Redis `/1` (**3** keys) tetap utuh, sedangkan Redis `/2` aktif melayani sesi demo.
  - **Uji Browser Playwright Live (`frontend/tests/e2e/demo-smoke.spec.ts` terhadap `demo-start.ps1` + `agroniaga_demo` + Redis `/2`):** **`2/2 PASS (34.5s)`** (`Public portal renders published demo data with MODE DEMO banner and zero MSW` & `Seven demo roles log in with real cookies, scoped visibility, DB dashboard aggregates, and UI -> PostgreSQL persistence`), membuktikan **0** request `mockServiceWorker.js`, login **7 peran**, agregasi SQL `/api/v1/reports/overview` & `/api/v1/reports/finance`, isolasi scope lintas petani/koperasi, penciptaan receipt baru (`4250.000` / `1000.000` -> `3250.000 kg`) via UI tersimpan ke PostgreSQL dan tetap tampil setelah `page.reload()`, serta penghentian bersih `.\scripts\demo-stop.ps1` tanpa menyentuh proses lain.
  - **Backend Static, Architecture & Tests:** `ruff check .` (`0` error), `pyright` (`0` errors/warnings), `lint-imports` (**`16 kept, 0 broken`**), `pytest -q` (**`81 passed`** mencakup `tests/unit/test_demo_seed_guards.py` `4/4`).
  - **Frontend Static, Tests & Build Mode `real`:** `npm.cmd run typecheck` (`0` error), `npm.cmd run lint` (`0` error), `npm.cmd test` (**`11` file, `32/32 passed`** termasuk pengujian `isDemoBannerEnabled`), `VITE_API_MODE=real VITE_DEMO_BANNER=true npm.cmd run build` (**PASS `1.83s`**, inspeksi `dist/assets` menunjukkan **0** aset MSW).
  - **Contracts Validator:** `python -B contracts\scripts\validate_contracts.py` (**`K1–K11 PASS`, `TOTAL ISSUES: 0`**) & `python -B -m unittest discover -s contracts\tests -v` (**`13/13 OK` dalam `11.807s`**).
- **Status Akhir Track Demo Lokal (`LOCAL-DEMO-01`):** **`READY — LOCAL_DEMO_REAL_API_VERIFIED`** *(kredensial demo acak tersimpan lokal pada `backend/.demo-credentials.local.txt`, tanpa hardcode rahasia pada source code, Git, atau dokumentasi).*
