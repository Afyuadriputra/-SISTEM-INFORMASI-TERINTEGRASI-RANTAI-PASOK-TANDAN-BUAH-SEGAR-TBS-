# M0 Handoff Brief — Backend Track (`B0–B11`) & Frontend Track (`F0–F11`)

**Milestone Pendahulu:** `M0 & M0.1 — Requirements, Contract Alignment & Consistency Patch` (`PASS`, `K1–K11` 0 issues)  
**Rujukan Kontrak Tunggal:** `contracts/` (`openapi.v1.yaml`, `error-catalog.yaml`, `state-catalog.yaml`, `role-permissions.yaml`, `fixtures/*.json`)  
**Aturan Dasar:** `PRD V1.1`, `TRD V1.1`, `AFD V1.1`, `DBD V1.1`, `BSD V1.1`, `IPD V1.1`, serta desain UI FigCraft D5 (`READY — FIGCRAFT_DESIGN_SIGNOFF`).

---

## 1. Handoff untuk Backend Track (`B0` -> `B11`)

1. **Urutan Implementasi Inkremental (`IPD §9–21`, `TRD §5–6`, `DBD §4.11`):**
   - Mulai dari **`B0` (Project Foundation):** Bangun `backend/app/main.py`, `app/core/` (`config.py`, async `database.py` + Alembic baseline, `redis.py` fail-closed client & pool, `security.py`, `logging.py`, `middleware.py` dengan `X-Request-ID`, `errors.py` global exception handler sesuai `error-catalog.yaml`), Docker Compose PostgreSQL + Redis, endpoint probe `/health/live` dan `/health/ready` (`TRD §25.1`), serta smoke/connectivity/architecture tests. **Dilarang membuat puluhan folder modul/subfolder kosong sekaligus pada `B0` hanya untuk membuktikan existence 11 modul (`TRD §5.1, §6`).**
   - Tambahkan modul domain **secara inkremental bersama migrasi & tes masing-masing** mengikuti urutan IPD: **`B1` (`identity_access`) -> `B2` (`master_data`) -> `B3` (`public_portal` + `pricing`) -> `B4` (`tbs_receiving`) -> `B5` (`contracts`) -> `B6` (`logistics`) -> `B7` (`mill_weighing`) -> `B8` (`reconciliation`) -> `B9` (`finance` subdomain dalam `reconciliation` atau pemisahan bersih) -> `B10` (`reporting` + `audit`) -> `B11` (hardening, performa, & security verification)**.
   - **Clean Architecture Empat Layer (`ADR-002`, `TRD §5`, `IPD §9.1–9.4`):** Setiap modul domain yang benar-benar diimplementasikan wajib memisahkan `domain/`, `application/`, `infrastructure/`, dan `presentation/` dengan arah dependency: **Domain bebas dependency Infrastructure/Presentation/framework; Application bergantung pada Domain & port yang sesuai; Infrastructure mengimplementasikan port tersebut; Presentation memanggil Application use cases; dan wiring konkret adapter dilakukan eksplisit pada composition root (FastAPI `Depends`)**. Redis, PostgreSQL, performance engineering (pooling, indexing, pagination, cache-aside), security (Argon2id, session HttpOnly, CSRF, RBAC/scope, rate limit), serta architecture/import tests di CI tetap wajib.
2. **Invarian Wajib pada Implementasi Schema & Handler:**
   - **DTO & Tipe Presisi:** Seluruh model response Pydantic **wajib** menserialisasikan kuantitas/harga/rupiah/persentase/luas/koordinat sesuai pola string regex `openapi.v1.yaml` (`ADR-009`), timestamp UTC `Z`, dan `UUID` v4 tanpa memakai tipe `float`.
   - **Keamanan & Default-Deny (`95` Total Operasi OpenAPI = `11` Unauthenticated + `84` Authenticated):**
     - `2` Health probes (`getLivenessHealth`, `getReadinessHealth`) + `7` Public Portal + `2` Auth unauthenticated (`getCsrfToken`, `loginUser`) = `11` operasi publik/bootstrap.
     - `2` Auth terautentikasi (`logoutUser`, `getCurrentUser`) + `82` operasi bisnis/admin internal = **`84` endpoint terautentikasi** yang seluruhnya wajib memeriksa session cookie `ts_agroniaga_session`, RBAC permission sesuai `contracts/role-permissions.yaml`, resource scope (`FARMER`/`COOPERATIVE`/`MILL`/`PERUMDA_GLOBAL`), aturan `SOD-01..06`, blokir mutasi bisnis `SYSTEM_ADMIN` (`BR-SYS-002`), dan header `X-CSRF-Token` pada seluruh mutasi terautentikasi.
   - **State, Konkurensi & Idempotency:** Terapkan transisi ketat `contracts/state-catalog.yaml`, optimistic locking `version` (`409 MD_STALE_RECORD_VERSION`), row-level lock `SELECT ... FOR UPDATE` pada kuota/alokasi e-DO/pembayaran, invalidasi cache Redis pasca-commit PostgreSQL, serta **`Idempotency-Key` wajib pada seluruh `8` operasi mutasi kritis** (mewakili `7` kategori proses kritis `BSD §27.2`: `createReceiptDraft`, `reserveContractQuota`, `issueDeliveryOrder`, `createMillTicket`, `createOrTriggerReconciliation`, `calculateReconciliation`, `approveOrRejectInvoicePayment`, `recordPaymentEvidence` — sesuai `ADR-010`).
   - **Proteksi `PENDING_SOP`:** Pertahankan `business_model_code = UNCONFIRMED` default yang mengembalikan `409 FIN_POLICY_UNCONFIRMED` bila mencoba menerbitkan faktur/settlement final di luar mode simulasi tervalidasi, serta tolak pembayaran parsial (`422 PAY_PARTIAL_NOT_SUPPORTED`).
   - **Seed & Regression Tests:** Gunakan `contracts/fixtures/*.json` sebagai data seed deterministik pengujian integrasi dan verifikasi setiap error pada `contracts/fixtures/error-scenarios.json`.

---

## 2. Handoff untuk Frontend Track (`F0` -> `F11`)

1. **Urutan Implementasi (`IPD §26–37`):**
   - Mulai dari **`F0` (Project Foundation):** Setup Vite + React + TypeScript strict + Tailwind v4 memakai design tokens resmi D5 (`D:\figcraft\test-output\tokens.tailwind.css` & `tokens.json` tanpa memodifikasi berkas sumber asli di `D:\figcraft`), **TanStack Router** (sesuai `TRD §3, §17` dan `ADR-006`) untuk 26 rute `AFD §36`, **TanStack Query**, **React Hook Form + Zod**, dan generasi otomatis tipe TypeScript langsung dari `contracts/openapi.v1.yaml` menggunakan `openapi-typescript`.
   - Bangun **`F1` (Atomic Design System)** selaras 5 level komponen D5 (`Organism/InternalSidebar`, `Molecule/WeightInputGroup`, `Molecule/FormField`, dialog konfirmasi) lalu kembangkan fitur bertahap **`F2` (Portal Publik) -> `F3` (Auth & App Shell) -> `F4` (`FLOW-05` & `FLOW-06`) -> `F5..F10` -> `F11`**.
2. **Aturan API Client, MSW & Keadaan UI:**
   - **Zero-Drift Mock (MSW):** Selama backend belum aktif (`I0–I4`), handler Mock Service Worker (MSW) di frontend **wajib** mengembalikan payload identik dengan `contracts/fixtures/*.json` (termasuk status `EXPIRED` sebagai `display_status` dan 22 skenario error `ErrorResponse`).
   - **Auth & CSRF:** Login internal mengandalkan `GET /api/v1/auth/csrf` + `POST /api/v1/auth/login` dengan `credentials: 'include'`. Frontend dilarang membaca atau menyimpan token sesi ke `localStorage`/`sessionStorage` (`ADR-005`), dan penyembunyian menu UI mengikuti daftar `permissions` dari `getCurrentUser` tanpa menjadi satu-satunya pengaman.
   - **Transparansi Nilai & Label Simulasi:** Seluruh angka bobot, tarif, dan total rupiah diformat di sisi presentation UI dari string desimal API (mis. pemisah ribuan Indonesia + satuan `kg` / `Rp`) tanpa kalkulasi presisi `Number`/`float` untuk data mutasi kritis. Pertahankan lencana eksplisit `Data Simulasi` / `Pending SOP` sesuai D5 pada aturan toleransi `1,5%`, grading `2%`, dan alokasi proporsional `30/20/50%`, serta pastikan tombol persetujuan faktur/pembayaran tidak pernah menampilkan label `Lunas / PAID` sebelum `settlement_status == 'PAID'`.
   - **Kelengkapan State Halaman (`AFD §38`):** Setiap rute `AFD §36` wajib menangani state Loading, Empty (seperti `empty_public_prices_envelope`), Validation Error `422` (`error.details`), Business/Conflict Error `409`, Unauthorized/Forbidden `401/403`, dan Offline/Network retry secara ramah memakai `request_id` dari respons.

---

## 3. Penjaga Paralelisme Sebelum Masuk Track `B0` / `F0`

- **Kontrak Beku:** Jangan menyunting `contracts/openapi.v1.yaml` atau katalog lain saat mulai menulis kode tanpa mengikuti *Contract Change Management* (`docs/m0/M0_CHANGELOG.md §3`).
- **Gerbang Regresi Cepat:** Jalankan selalu `python contracts/scripts/validate_contracts.py` dan `python -m unittest discover -s contracts/tests -v` setiap kali menyentuh berkas di `contracts/`.
