
# MASTER PROMPT CODEX — M0 CONTRACT ALIGNMENT & SHARED FOUNDATION

**Project:** Sistem Informasi Terintegrasi Rantai Pasok Tandan Buah Segar (TBS)
**Organization:** Perumda Tuah Sekata — Unit Agro Niaga
**Milestone:** M0 — Requirements & Contract Alignment
**Development Model:** Solo Developer + Optional Parallel Coding Agents
**Execution Status:** NOT_STARTED
**Scope:** Shared Contract & Documentation Only

---

# 1. ROLE & RESPONSIBILITY

Bertindak sebagai:

- Principal Software Architect
- API Contract Architect
- Domain-Driven Design Architect
- Senior Backend Engineer
- Senior Frontend Architect
- Database Architect
- Security Architect
- QA Automation Engineer
- Technical Documentation Engineer

Tugas kamu adalah **mengeksekusi Milestone M0 secara menyeluruh**, berdasarkan enam dokumen spesifikasi V1.1, hasil sign-off UI/UX FigCraft D5, serta checkpoint pengembangan.

Milestone M0 adalah pekerjaan membuat fondasi kontrak, bukan implementasi aplikasi.

Hasil M0 harus memungkinkan:

1. Backend FastAPI dikembangkan tanpa menunggu frontend.
2. Frontend React dikembangkan menggunakan OpenAPI dan MSW tanpa backend.
3. Kedua jalur memakai skema request/response yang identik.
4. Business rules dan state transitions konsisten.
5. Hak akses dan data scope terdefinisi.
6. Error handling terstandarisasi.
7. Test fixtures digunakan bersama.
8. Pengembangan paralel oleh coding agent tidak menghasilkan kontrak berbeda.
9. Hasil implementasi dapat diverifikasi terhadap requirement yang sama.
10. Progress dapat dilanjutkan melalui checkpoint pada sesi berikutnya.

**Prinsip: Contract First, One Source of Truth, No Hidden Assumptions, Evidence-Based Verification.**

---

# 2. INSTRUKSI WAJIB: JANGAN LANGSUNG MEMBUAT OPENAPI

Sebelum membuat atau mengubah file apa pun, wajib lakukan tahap berikut:

**DISCOVER → READ → UNDERSTAND → AUDIT → DESIGN → IMPLEMENT CONTRACTS → TEST → VERIFY → CHECKPOINT → REPORT**

Jangan langsung menghasilkan file `openapi.v1.yaml` hanya berdasarkan ingatan atau ringkasan tugas.

Kamu harus membaca dokumen sebenarnya.

Tidak diperbolehkan:

- Mengarang endpoint tanpa dukungan kebutuhan.
- Mengarang business rules yang belum disahkan.
- Menganggap semua keputusan SOP sudah final.
- Menyalin contoh API dari proyek lain.
- Menetapkan role tanpa memeriksa dokumen.
- Membuat payload yang berbeda dengan model data.
- Mengubah state bisnis secara sepihak.
- Menggunakan mock data sebagai fakta operasional.
- Mengklaim kontrak valid tanpa menjalankan pemeriksaan.

Apabila terdapat perbedaan antardokumen, catat dalam Decision Register dan selesaikan berdasarkan kepemilikan keputusan masing-masing dokumen.

Jika perbedaan membutuhkan keputusan bisnis resmi, jangan mengarang solusinya.

---

# 3. DOCUMENT DISCOVERY

## 3.1 Workspace

Gunakan workspace proyek yang aktif.

Lokasi sebelumnya:

`D:\Kuliah\joki\radit\projek thesis bg givo`

Verifikasi lokasi aktual sebelum bekerja.

Jangan membuat repository baru apabila repository proyek sudah tersedia.

## 3.2 Enam dokumen utama

Baca sepenuhnya:

- `docs/PRD.md`
- `docs/TRD.md`
- `docs/AFD.md`
- `docs/DBD.md`
- `docs/BSD.md`
- `docs/IPD.md`

Pastikan keenam dokumen menggunakan baseline V1.1 terkonsolidasi.

Jika ada versi lebih baru, jangan otomatis mengganti sumber. Laporkan perbedaannya dan tetapkan baseline yang berlaku berdasarkan bukti.

## 3.3 Dokumen checkpoint

Wajib baca:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Pahami:

- Milestone yang sudah selesai.
- Current milestone.
- Design sign-off.
- Pending issues.
- Quality gates.
- Bukti yang sudah tersedia.
- Ketergantungan M0 terhadap pekerjaan sebelumnya.

Jangan menghapus histori checkpoint D0–D5.

## 3.4 Hasil desain FigCraft D5

Temukan dan baca laporan terbaru:

`d5-design-gap-closure-signoff.md`

Lokasi sebelumnya berada dalam folder artefak Antigravity.

Periksa juga:

- `design-verification-signoff-report.md` sebagai laporan D4 historis.
- `design-qa-handoff.md` jika tersedia.
- `phase-a-ux-architecture.md` jika tersedia.
- `D:\figcraft\test-output\agroniaga-tbs-perumda-tuah-sekata.figcraft`
- `D:\figcraft\test-output\tokens.tailwind.css`
- `D:\figcraft\test-output\tokens.json`

Periksa akses nyata terhadap file tersebut.

**PENTING: D4 bukan D5.**

Laporan D4 lama masih memiliki status CONDITIONAL.

Gunakan laporan D5 terbaru dengan keputusan `READY — FIGCRAFT_DESIGN_SIGNOFF` jika keberadaan dan isinya dapat diverifikasi.

Hasil D5 yang dilaporkan sebelumnya mencakup:

- 26/26 rute AFD dengan layar desktop mandiri.
- 50 frame/board readyForDev.
- 393 instance komponen.
- 45 design variables.
- 14 prototype flows.
- 215 interaksi prototype.
- 15 critical UI/business states.
- Form FLOW-05 dan FLOW-06.
- Tujuh layar mobile bisnis prioritas.
- Design token Tailwind CSS v4.

Angka tersebut adalah referensi laporan, bukan pengganti pemeriksaan terhadap artefak.

Jika file `.figcraft` tidak dapat diproses langsung, gunakan laporan D5, inventaris layar, dan dokumen handoff yang tersedia. Jangan memodifikasi desain.

Jika laporan D5 dan checkpoint yang diperlukan tidak dapat ditemukan atau diverifikasi, tandai M0 sebagai `BLOCKED — REQUIRED_SOURCE_MISSING`. Jangan menggantinya dengan D4 secara diam-diam.

## 3.5 Contract discovery

Periksa apakah folder `contracts/` sudah ada.

Jika sudah ada:

- Inventarisasi seluruh file.
- Baca isinya.
- Identifikasi kontrak yang masih relevan.
- Pertahankan ID dan keputusan yang valid.
- Catat konflik.
- Perbarui secara terkontrol.

Jika belum ada, buat sesuai struktur M0.

Jangan menimpa file yang sudah ada tanpa memahami isinya.

---

# 4. SOURCE OF TRUTH

Gunakan pembagian otoritas berikut.

| Sumber                     | Kewenangan                                                   |
| -------------------------- | ------------------------------------------------------------ |
| PRD V1.1                   | Produk, aktor, ruang lingkup, kebutuhan fungsional           |
| TRD V1.1                   | Arsitektur, API conventions, keamanan, performa, teknologi   |
| AFD V1.1                   | Workflow, navigasi, status dan state transitions             |
| DBD V1.1                   | Entitas, relasi, tipe data, constraint, snapshot             |
| BSD V1.1                   | Business rules, kalkulasi, persetujuan, otorisasi bisnis     |
| IPD V1.1                   | Milestone, deliverables, quality gates, pembagian pekerjaan  |
| FigCraft D5                | Layout, komponen visual, kebutuhan layar, interaction states |
| IMPLEMENTATION_CHECKPOINTS | Progres, hasil pemeriksaan, blockers, sign-off               |

FigCraft tidak boleh mengubah business rules yang sudah didefinisikan oleh BSD.

DBD tidak boleh digunakan untuk menetapkan kebijakan bisnis baru yang belum disahkan.

OpenAPI harus merepresentasikan kebutuhan, bukan membuat kebutuhan baru.

Jika terjadi konflik, catat:

- Conflict ID.
- Dokumen dan lokasi sumber.
- Perbedaan.
- Dampak.
- Usulan penyelesaian.
- Status keputusan.
- Pihak yang perlu mengesahkan.

Gunakan status:

- RESOLVED.
- PROPOSED.
- PENDING_SOP.
- BLOCKING.
- DEFERRED.

---

# 5. PROJECT ARCHITECTURE — NON-NEGOTIABLE

M0 tidak melakukan coding aplikasi, tetapi harus menghasilkan kontrak yang kompatibel dengan keputusan arsitektur berikut.

## Backend

- Python 3.12+.
- FastAPI.
- Modular Monolith.
- Four-Layer Clean Architecture di setiap modul.
- SOLID pragmatis.
- SQLAlchemy.
- PostgreSQL.
- Alembic.
- Redis caching.
- Structured logging.
- Request ID.
- RBAC.
- Resource scope authorization.
- CSRF.
- Server-side session.
- Idempotency.
- Transaction safety.
- Concurrency control.
- Query optimization.
- Database indexing.
- Connection pooling.

Four-layer:

1. Domain.
2. Application.
3. Infrastructure.
4. Presentation.

Kontrak API tidak boleh memaksa backend menggabungkan domain berbeda atau menempatkan business logic dalam HTTP router.

## Frontend

- React.
- TypeScript strict.
- Vite.
- Tailwind CSS v4.
- Atomic Design lima level.
- Feature-Based Organization.
- TanStack Router.
- TanStack Query.
- React Hook Form.
- Zod.
- MSW.
- Playwright.

Kontrak harus dapat dipakai oleh API client bertipe dan mock API frontend.

## Performance

Redis tetap wajib tersedia sejak milestone B0, tetapi caching diterapkan hanya pada use case yang relevan.

PostgreSQL adalah source of truth.

M0 mendokumentasikan kebutuhan caching, pagination, filtering, concurrency, dan idempotency.

M0 tidak mengimplementasikan Redis atau query database.

---

# 6. SCOPE M0 — ALLOWED AND FORBIDDEN CHANGES

## Allowed

Boleh membuat atau mengubah:

- `contracts/`
- `contracts/fixtures/`
- `contracts/tests/`
- `contracts/scripts/` jika diperlukan untuk validasi kontrak
- `docs/IMPLEMENTATION_CHECKPOINTS.md`
- `docs/m0/`
- `docs/adr/` untuk keputusan arsitektur M0
- Dokumen laporan dan change log khusus M0

Boleh menjalankan:

- OpenAPI lint.
- YAML/JSON parsing.
- JSON Schema validation.
- Schema reference validation.
- Fixture validation.
- Contract consistency checks.
- Documentation checks.
- Read-only Git inspection.
- Pemeriksaan TypeScript type generation ke lokasi sementara jika tool tersedia.

## Forbidden

DILARANG mengedit:

- `backend/`
- `frontend/`
- `alembic/`
- `infra/`
- File desain `.figcraft`
- Design tokens asli
- Keenam dokumen PRD, TRD, AFD, DBD, BSD, IPD

DILARANG:

- Membuat aplikasi FastAPI.
- Membuat route handler.
- Membuat ORM models.
- Membuat migrations.
- Membuat komponen React.
- Membuat UI.
- Menginstal seluruh dependency aplikasi.
- Menjalankan deployment.
- Mengubah data operasional.
- Mengisi secrets nyata.
- Membuat mock server sebagai aplikasi runtime.

Script untuk **validasi kontrak** diperbolehkan, tetapi tidak boleh berubah menjadi implementasi backend atau frontend.

Jika perubahan dokumen V1.1 diperlukan, buat Change Request. Jangan mengeditnya secara sepihak.

---

# 7. OUTPUT DIRECTORY STRUCTURE

Gunakan struktur sederhana yang mudah dipelihara solo developer.

```text
contracts/
├── openapi.v1.yaml
├── error-catalog.yaml
├── state-catalog.yaml
├── role-permissions.yaml
├── fixtures/
│   ├── README.md
│   ├── actors.json
│   ├── public-prices.json
│   ├── mills.json
│   ├── master-data.json
│   ├── tbs-receipts.json
│   ├── contracts-quota.json
│   ├── delivery-orders.json
│   ├── mill-tickets.json
│   ├── reconciliations.json
│   ├── invoices-payments.json
│   └── error-scenarios.json
├── tests/
│   └── ...
└── scripts/
    └── ...

docs/
├── PRD.md
├── TRD.md
├── AFD.md
├── DBD.md
├── BSD.md
├── IPD.md
├── IMPLEMENTATION_CHECKPOINTS.md
├── m0/
│   ├── M0_DOCUMENT_AUDIT.md
│   ├── M0_REQUIREMENT_TRACEABILITY.md
│   ├── M0_DECISION_REGISTER.md
│   ├── M0_CONTRACT_VALIDATION_REPORT.md
│   ├── M0_CHANGELOG.md
│   └── M0_HANDOFF.md
└── adr/
```

Nama file fixtures boleh disesuaikan jika terdapat alasan teknis dan semua referensi diperbarui.

Jangan memecah satu kontrak sederhana menjadi puluhan file tanpa manfaat.

`openapi.v1.yaml` tetap menjadi satu entrypoint kanonis.

Jika kontraknya perlu dipisahkan menjadi beberapa berkas, pastikan semua reference dapat di-resolve oleh toolchain yang dipilih dan entrypoint tetap jelas.

---

# 8. PHASE A — REQUIREMENTS COMPREHENSION

## Objective

Memahami seluruh kebutuhan sebelum menulis kontrak.

## Task A1 — Business Domain Inventory

Identifikasi domain:

1. Identity & Access.
2. Public Portal.
3. Master Data.
4. Pricing.
5. TBS Receiving.
6. Contracts & Quota.
7. Logistics.
8. Mill Weighing.
9. Reconciliation & Dispute.
10. Finance/Settlement.
11. Reporting.
12. Audit.

Gunakan nama modul kanonis yang berlaku di TRD dan IPD.

Modul Finance boleh merupakan subdomain dari Reconciliation sesuai keputusan dokumentasi, tetapi kepemilikan use case dan otorisasinya harus jelas.

Jangan membuat microservices.

## Task A2 — Functional Requirement Inventory

Ekstrak seluruh requirement ID dari PRD.

Kelompokkan:

- Core MVP.
- Research Evaluation.
- Deferred/Future.

Hubungkan setiap requirement ke:

- Aktor.
- Business flow.
- Business rule.
- Data entity.
- API operation jika membutuhkan backend.
- UI route jika relevan.
- Test case.
- Milestone implementasi.

Jangan otomatis membuat endpoint untuk requirement yang tidak membutuhkan API.

## Task A3 — Business Flow Inventory

Baca seluruh FLOW dari AFD.

Termasuk alur:

- Informasi publik.
- Harga.
- Login.
- Master data.
- Penerimaan.
- Penimbangan.
- Kontrak.
- Kuota.
- Surat jalan.
- Tiket PKS.
- Rekonsiliasi.
- Dispute.
- Pembayaran.
- Reporting.
- Audit.

Periksa `AFD §36` untuk peta rute frontend yang berlaku.

Pastikan 26 rute yang dilaporkan pada D5 terpetakan.

Setiap rute harus memiliki:

- Role.
- Purpose.
- API dependencies atau keterangan tidak membutuhkan API.
- Data yang ditampilkan.
- Aksi.
- Error/empty/loading state.
- Requirement reference.

**Tidak wajib ada satu endpoint per satu halaman.**

Satu layar dapat memakai beberapa API, dan satu API dapat digunakan oleh beberapa layar.

## Task A4 — Business Rule Inventory

Baca BSD dan AFD.

Ekstrak:

- Semua rule ID.
- Formula.
- Preconditions.
- Invariants.
- Authorization requirements.
- Required evidence.
- Forbidden transitions.
- Pending SOP decisions.

Buat traceability yang dapat dipakai untuk pengujian.

## Task A5 — Data Inventory

Baca DBD.

Petakan:

- Entitas.
- Primary identifier.
- Relationships.
- Data ownership.
- Field precision.
- Optional/required.
- Sensitive/public data.
- Historical snapshot.
- Versioning.
- Concurrency information.

Jangan mengubah desain database melalui kontrak tanpa Change Request.

---

# 9. PHASE B — API DESIGN DECISIONS

Sebelum menulis OpenAPI, tetapkan standar berikut berdasarkan dokumen.

## 9.1 API Prefix

Gunakan baseline:

`/api/v1`

Jangan membuat endpoint versi lain tanpa kebutuhan.

## 9.2 REST Conventions

Gunakan method secara konsisten:

- GET untuk read.
- POST untuk create dan action/command.
- PATCH untuk partial update bila sesuai.
- PUT hanya bila semantik penggantian resource penuh diperlukan.
- DELETE hanya jika sesuai kebijakan penghapusan/deaktivasi.

Jangan menganggap seluruh tabel harus mempunyai CRUD publik.

Business command seperti verify, approve, publish, issue, resolve harus mempunyai semantik eksplisit.

## 9.3 Response Envelope

Ikuti standar response yang berlaku dalam IPD.

Contoh kesuksesan:

```json
{
  "success": true,
  "data": {},
  "meta": null,
  "request_id": "req_example"
}
```

Contoh kegagalan:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Data tidak valid.",
    "details": null
  },
  "request_id": "req_example"
}
```

Contoh hanya menjadi baseline.

Pastikan detail final sesuai dokumentasi.

Definisikan komponen reusable:

- SuccessResponse.
- ErrorResponse.
- PaginationMeta.
- RequestId.
- ValidationErrorDetail.

Jangan membuat nested generic envelope yang menyulitkan frontend type generation.

## 9.4 Decimal Precision

Gunakan:

- Berat: `NUMERIC(14,3)`.
- Harga: `NUMERIC(18,2)`.
- Nominal uang: `NUMERIC(20,2)`.

Transport nilai presisi menggunakan string desimal sebagaimana ditetapkan IPD.

Contoh:

```json
{
  "gross_weight_kg": "10250.000",
  "tare_weight_kg": "350.000",
  "net_weight_kg": "9900.000",
  "price_per_kg": "2850.00",
  "amount": "28215000.00"
}
```

Angka hanya data ilustrasi.

Gunakan `type: string` dan pola/format yang dapat diverifikasi pada OpenAPI jika sesuai.

Jangan menggunakan binary floating point sebagai kontrak nilai keuangan.

Jangan kirim `"Rp2.850"` sebagai nilai dasar kalkulasi.

Frontend bertugas memformat tampilan.

## 9.5 Timestamp

Gunakan ISO 8601/RFC 3339 untuk timestamp.

Tetapkan konvensi konsisten:

- Timestamp instan disimpan dalam UTC.
- Frontend menampilkan WIB sesuai konteks bisnis.
- Business date dibedakan dari timestamp.
- Timezone tidak mengubah makna tanggal transaksi.

## 9.6 IDs

Gunakan UUID sesuai DBD.

Pastikan parameter path menggunakan schema UUID yang konsisten.

Jangan menggunakan UUID sebagai pengganti otorisasi.

## 9.7 Pagination

Untuk endpoint daftar, tentukan:

- Parameter pagination.
- Batas ukuran halaman.
- Meta response.
- Sorting.
- Filtering.
- Stable ordering.

Jika menggunakan cursor pagination, definisikan struktur cursor dan aturan validasinya.

Jangan mencampur offset dan cursor secara ambigu.

Gunakan satu baseline sederhana jika belum ada kebutuhan berbeda.

## 9.8 Request ID

Setiap response harus dapat dikorelasikan dengan Request ID jika ditetapkan TRD/IPD.

Definisikan:

- Cara representasi di response body.
- Header apabila digunakan.
- Penanganan error.
- Penggunaan di laporan debugging.

Jangan mengekspos log internal atau stack trace.

---

# 10. PHASE C — OPENAPI 3.1 CONTRACT

Buat:

`contracts/openapi.v1.yaml`

Gunakan OpenAPI 3.1 atau versi kompatibel yang ditetapkan IPD dan didukung toolchain yang digunakan.

Wajib mencakup:

- `openapi`.
- `info`.
- `servers` yang aman untuk lingkungan development tanpa URL produksi fiktif.
- `tags`.
- `paths`.
- `components.schemas`.
- `components.responses`.
- `components.parameters`.
- `components.securitySchemes`.
- `components.headers` jika diperlukan.
- `operationId` yang unik.
- Examples.
- Error responses.
- Security requirements.

Jangan meninggalkan referensi schema rusak.

## 10.1 Public API

Rancang sesuai PRD, AFD, dan D5:

- GET `/api/v1/public/prices`
- GET `/api/v1/public/prices/{id}`
- GET `/api/v1/public/mills`
- GET `/api/v1/public/mills/{id}`
- GET `/api/v1/public/profile`
- GET `/api/v1/public/notices`

Tambahkan operasi lain hanya jika dibutuhkan untuk fitur yang tercantum dalam dokumen, seperti sumber harga acuan Disbun atau informasi kemitraan.

Pastikan:

- Tidak membutuhkan login.
- Hanya informasi yang berhak dipublikasikan.
- Harga terverifikasi dan berlaku dipisahkan dari harga kedaluwarsa.
- Harga Disbun dibedakan dari penawaran PKS.
- Harga kontrak privat tidak dibocorkan.
- Data petani tidak dikirim.
- Koordinat PKS yang belum diverifikasi tidak dibuat fiktif.
- Data kosong tidak diwakili dengan angka nol palsu.
- Informasi sumber dan waktu pembaruan tersedia.

## 10.2 Authentication API

Baseline:

- POST `/api/v1/auth/login`
- POST `/api/v1/auth/logout`
- GET `/api/v1/auth/me`
- GET `/api/v1/auth/csrf`

Definisikan:

- Login request.
- Login result.
- Session cookie.
- CSRF contract.
- Session expiration.
- Logout.
- 
- 
- Rate limiting errors.
- Generic authentication error.

Gunakan server-side session dengan secure HttpOnly cookie.

Jangan menyimpan raw session token pada contoh payload.

Jangan mengembalikan password hash.

Gunakan OpenAPI security scheme sesuai model cookie sebenarnya.

Nama cookie harus selaras dengan keputusan kontrak, tidak dikarang seolah-olah sudah diimplementasikan.

## 10.3 Master Data API

Cakup:

- Farmers.
- Farms.
- Cooperatives.
- Cooperative memberships bila diperlukan.
- Mill companies dan mills.
- Lokasi PKS.
- Informasi perusahaan yang boleh dipublikasikan.
- Data pendukung MVP.

Pastikan mendukung kebutuhan FLOW-05 dan FLOW-06 yang telah diselesaikan pada FigCraft D5.

Definisikan field, validasi, uniqueness, serta resource scope.

Contoh aturan:

- Koperasi hanya dapat mengelola petani yang berhak diakses.
- Data master yang sudah digunakan transaksi tidak boleh dihapus secara sembarangan.
- Koordinat harus valid.
- Informasi PKS privat dan informasi profil PKS publik harus dibedakan.

## 10.4 Pricing API

Cakup:

- Membuat draft harga.
- Melihat daftar/detail harga.
- Mengubah draft sesuai kewenangan.
- Submit verification.
- Verify/reject.
- Publish.
- Riwayat harga.
- Sumber harga.
- Kategori harga.
- Harga acuan Disbun.

Gunakan endpoint action sesuai konvensi pada IPD.

Pastikan:

- Harga draft tidak tampil di portal publik.
- Maker/checker mengikuti aturan dokumen.
- Riwayat tidak hilang.
- Validity period jelas.
- Data transaksi historis tidak berubah karena harga publik berubah.
- Cache invalidation merupakan kewajiban implementasi setelah commit, bukan aksi yang dipercayakan kepada frontend.

## 10.5 TBS Receiving API

Cakup:

- Daftar penerimaan.
- Membuat draft.
- Detail penerimaan.
- Timbangan.
- Revisi timbangan.
- Grading.
- Validasi.
- Riwayat status.

Definisikan error untuk:

- Tara melebihi bruto.
- Berat negatif.
- Data petani tidak valid.
- Scope tidak sesuai.
- Transaksi duplikat.
- Status tidak mengizinkan perubahan.
- Versi konflik.

Berat netto merupakan aturan backend.

Frontend boleh menampilkan preview, tetapi server tetap menentukan hasil akhir.

## 10.6 Contracts & Quota API

Cakup:

- Kontrak niaga.
- Detail kontrak.
- Periode kuota.
- Kuota tersedia.
- Reservasi.
- Konsumsi.
- Pelepasan reservasi.
- Status kontrak.

Definisikan:

- Concurrency-sensitive operations.
- Idempotency.
- Over-quota rejection.
- Expired contract handling.
- Optimistic version/conflict bila digunakan.
- Perbedaan kuota total, terpakai, dan terreservasi.

M0 hanya menetapkan kontrak; mekanisme locking SQL menjadi tanggung jawab backend milestone terkait.

Model principal/agent yang belum disahkan harus tetap memiliki penanda UNCONFIRMED.

## 10.7 Logistics & e-DO API

Cakup:

- Pembuatan delivery order.
- Detail e-DO.
- Daftar muatan.
- Hubungan multi-petani.
- Penerbitan e-DO.
- QR/token verification.
- Status pengiriman.
- Pembatalan sesuai aturan.
- Riwayat status.

Definisikan:

- Idempotency-Key.
- Duplicate request handling.
- Invalid state transition.
- Unauthorized cancellation.
- Multi-receipt allocation.
- Anti-double-allocation.
- No GPS live tracking in Core MVP.

Jangan menganggap isi QR sebagai rahasia atau otorisasi tunggal tanpa verifikasi server.

## 10.8 Mill Weighing API

Cakup:

- Pencatatan tiket timbang PKS.
- Detail tiket.
- Verifikasi.
- Grading PKS.
- Revisi.
- Referensi e-DO.
- Status penerimaan.

Definisikan:

- Satu tiket current sesuai aturan MVP.
- Duplicate ticket prevention.
- Gross/tare/net validation.
- Historical version.
- Cross-PKS access denial.
- Pembatasan perubahan setelah tahapan bisnis tertentu.

## 10.9 Reconciliation & Dispute API

Cakup:

- Kasus rekonsiliasi.
- Detail rekonsiliasi.
- Perhitungan.
- Hasil selisih.
- Matched.
- Dispute/Hold.
- Review.
- Resolution.
- Riwayat keputusan.

Definisikan data:

- Origin weight.
- Mill weight.
- Difference kg.
- Difference percentage.
- Rule version.
- Tolerance status.
- Review reason.
- Evidence reference.
- Actor.
- Decision timestamp.

Jangan menetapkan toleransi 1,5% sebagai SOP resmi.

Jika dipakai untuk fixture, beri label SIMULATION.

Selisih berat yang membutuhkan pemeriksaan tidak boleh langsung menghasilkan settlement final.

Periksa aturan anomali surplus PKS pada BSD.

## 10.10 Finance, Invoice & Payment API

Cakup:

- Invoice.
- Invoice lines.
- Draft.
- Verification.
- Issuance.
- Payment approval.
- Payment evidence.
- Payment verification.
- Payment records.
- Settlement status.
- Farmer allocation bila sudah memenuhi syarat.

Bedakan:

- Incoming payment dari PKS ke Perumda.
- Outgoing payment dari Perumda ke koperasi/petani.
- Invoice issued.
- Approval granted.
- Payment pending.
- Payment verified.
- PAID.

**APPROVED tidak sama dengan PAID.**

**PKS membayar Perumda tidak berarti petani sudah dibayar.**

Model principal/agent yang belum disahkan harus menghentikan finalisasi transaksi keuangan yang bergantung padanya.

Tidak boleh ada auto-bank-transfer endpoint pada MVP.

Jangan membuat endpoint yang mengeksekusi transfer nyata.

## 10.11 Reporting API

Cakup:

- Operational overview.
- Pasokan TBS.
- Harga.
- Pengiriman.
- Rekonsiliasi.
- Keuangan.
- Dashboard Direksi.
- Ringkasan yang relevan untuk role lain.

Definisikan:

- Filter tanggal.
- Scope organisasi.
- Pagination jika perlu.
- Export jika termasuk MVP.
- Empty data.
- Permission.
- Data freshness.

Jangan mengirim angka margin yang belum memiliki komponen perhitungan lengkap.

## 10.12 Audit API

Cakup kebutuhan audit internal:

- Daftar aktivitas.
- Filter waktu.
- Actor.
- Action.
- Entity reference.
- Request ID.
- Event detail yang aman.
- Pagination.

Audit API harus memerlukan permission eksplisit.

Jangan mengekspos raw secrets, session, payload sensitif, atau informasi lintas scope.

---

# 11. PHASE D — STATE CATALOG

Buat:

`contracts/state-catalog.yaml`

Jangan hanya membuat daftar enum.

Setiap state machine minimal mempunyai:

- Machine ID.
- Business resource.
- State.
- Initial state.
- Terminal states jika ada.
- Allowed transitions.
- Transition action.
- Required permission.
- Required scope.
- Preconditions.
- Business rule reference.
- Side effects yang diharapkan.
- Relevant error code.
- Audit requirement.
- Pending-SOP classification jika relevan.

Cakup:

1. Harga.
2. Penerimaan.
3. Kontrak.
4. Reservasi kuota.
5. e-DO.
6. Tiket timbang.
7. Rekonsiliasi.
8. Dispute.
9. Invoice.
10. Payment approval.
11. Payment verification.

Periksa dengan teliti perbedaan antara:

- Status persisten.
- Status turunan waktu, misalnya EXPIRED.
- Status UI.
- Error state.
- Status simulasi.

Jangan mengubah status turunan menjadi status persisten tanpa alasan.

Contoh:

Harga dapat menjadi expired berdasarkan periode berlaku, sehingga perlu ditentukan apakah EXPIRED adalah persisted state atau derived presentation state.

Gunakan keputusan DBD/AFD.

Jangan menciptakan alur transisi hanya agar state machine tampak lengkap.

Setiap transition harus dapat ditelusuri ke dokumen.

---

# 12. PHASE E — ERROR CATALOG

Buat:

`contracts/error-catalog.yaml`

Definisikan struktur setiap error:

- Code.
- HTTP status.
- Description.
- Triggering condition.
- Field details jika relevan.
- Client-safe message.
- Retryable flag.
- Required user action.
- Security considerations.
- Related operation.
- Requirement/business-rule reference.

Kelompokkan:

## Authentication

- Invalid credentials.
- Session expired.
- Authentication required.
- CSRF invalid.

## Authorization

- Permission denied.
- Resource outside scope.
- Forbidden operation.
- Conflict of duties.

## Validation

- Required field.
- Invalid format.
- Invalid numeric precision.
- Invalid weight.
- Invalid coordinates.

## Business Conflicts

- Duplicate receipt.
- Insufficient quota.
- Invalid state transition.
- Duplicate allocation.
- Stale record version.
- Duplicate ticket.
- Payment blocked.
- Business policy unconfirmed.

## Availability

- Backend unavailable.
- Dependency unavailable.
- Request timeout.

## Rate Limiting

- Too many requests.

## Internal Error

- Unexpected server failure.

Periksa penggunaan status:

- 
- 
- 
- 
- 
- 
- 
- 
- 

Gunakan sesuai semantik dan ketentuan dokumen.

Jangan otomatis menggunakan 500 untuk seluruh error domain.

Hindari detail error yang membocorkan keberadaan resource privat.

Katalog harus cocok dengan OpenAPI, state catalog, dan test fixtures.

---

# 13. PHASE F — ROLE-PERMISSION MATRIX

Buat:

`contracts/role-permissions.yaml`

Gunakan role kanonis sesuai PRD/TRD/DBD.

Minimal identifikasi:

- PUBLIC.
- FARMER.
- COOPERATIVE_OPERATOR.
- PERUMDA_OPERATIONS.
- PERUMDA_FINANCE.
- MILL_OPERATOR.
- DIRECTOR.
- SYSTEM_ADMIN.

Periksa apakah nama/kode final berbeda dalam dokumen.

Jika role publik bukan akun database, tandai sebagai anonymous actor, bukan membuat user publik palsu.

Definisikan:

- Role.
- Permission.
- Resource.
- Operation.
- Scope.
- Conditions.
- Separation of duties.
- Approval rules.
- Public/private boundary.

Contoh resource:

- Prices.
- Farmers.
- Farms.
- Cooperatives.
- Mills.
- Contracts.
- Quotas.
- Receipts.
- Delivery Orders.
- Mill Tickets.
- Reconciliations.
- Disputes.
- Invoices.
- Payments.
- Reports.
- Audit.
- Users.
- Settings.

## Scope

Periksa scope:

- FARMER.
- COOPERATIVE.
- MILL.
- PERUMDA_GLOBAL.

Buat aturan matrix yang jelas:

- Petani tidak dapat mengakses transaksi petani lain.
- Operator koperasi tidak dapat membaca transaksi koperasi lain.
- Petugas PKS tidak dapat memodifikasi tiket PKS lain.
- Administrator teknis tidak otomatis memiliki approval permission.
- Pengguna publik tidak dapat membaca data transaksi privat.
- Petugas yang membuat keputusan tidak otomatis dapat memverifikasi keputusan sendiri jika aturan maker/checker melarang.

Jangan hanya mencantumkan role secara umum.

Untuk setiap endpoint internal, tentukan permission dan scope requirement.

Jangan menjadikan penyembunyian tombol frontend sebagai mekanisme keamanan.

Backend wajib memvalidasi scope.

---

# 14. PHASE G — SHARED TEST FIXTURES

Buat fixtures JSON yang deterministik.

Semua fixtures wajib:

- Tidak mengandung data pribadi nyata.
- Tidak mengandung credential produksi.
- Tidak menggunakan nomor rekening asli.
- Memakai UUID valid.
- Memakai format decimal string.
- Memakai timestamp sesuai kontrak.
- Memakai state yang terdaftar.
- Memiliki referensi antarentitas yang valid.
- Membedakan data simulasi dan data operasional.
- Dapat digunakan ulang oleh backend tests dan MSW frontend.

## Required Fixture Scenarios

### Public Pricing

- Harga aktif.
- Harga terverifikasi.
- Harga belum diverifikasi.
- Harga kedaluwarsa.
- Harga Disbun.
- PKS dengan harga berbeda.
- Harga kategori tidak sebanding.
- Tidak ada harga tersedia.

### Mills

- PKS aktif.
- PKS tanpa koordinat.
- PKS dengan koordinat terverifikasi.
- PKS tidak dipublikasikan.
- Scope PKS berbeda.

### Identity

- Farmer.
- Cooperative operator.
- Perumda operations.
- Perumda finance.
- Mill operator.
- Director.
- System admin.
- No-session visitor.

Jangan simpan plaintext password yang menyerupai credential nyata.

### Master Data

- Petani aktif.
- Petani nonaktif.
- Dua koperasi dengan scope berbeda.
- Kebun terkait petani.
- PKS dan perusahaan terkait.
- Konflik kode unik.

### Receiving

- Receipt draft.
- Valid receipt.
- Invalid tare.
- Duplicate request.
- Version conflict.
- Grading simulation.

### Contracts & Quota

- Active contract.
- Expired contract.
- Sufficient quota.
- Insufficient quota.
- Concurrent reservation scenario.
- Principal/agent UNCONFIRMED.

### Logistics

- e-DO draft.
- e-DO issued.
- Multi-farmer delivery.
- Duplicate allocation.
- Cancellation denied.
- Arrival/receipt workflow.

### Mill Weighing

- Valid mill ticket.
- Duplicate mill ticket.
- Correction history.
- Cross-mill unauthorized scenario.

### Reconciliation

- Matched.
- Dispute/Hold.
- Missing ticket.
- Surplus anomaly.
- Pending review.
- Unconfirmed tolerance.

### Finance

- Invoice draft.
- Invoice issued.
- Pending approval.
- Approval granted but unpaid.
- Payment awaiting verification.
- Verified payment.
- Incoming and outgoing transaction distinction.
- Finalization blocked by pending SOP.

### API Errors

- 
- 
- 
- 
- 
- 
- Timeout.
- Empty results.
- Stale data.

Buat fixture response yang sesuai OpenAPI.

Jika diperlukan, buat expected-error scenario yang menghubungkan request dan error response.

---

# 15. PHASE H — API SECURITY CONTRACT

M0 wajib menetapkan kontrak security, tetapi tidak membuat implementasi security.

Definisikan:

## Authentication

Server-side sessions.

- Session cookie.
- HttpOnly.
- Secure pada HTTPS.
- SameSite sesuai arsitektur deployment.
- Session expiry.
- Logout revocation.

## CSRF

CSRF token untuk operasi mutasi yang membutuhkan autentikasi cookie.

Definisikan:

- Endpoint pengambilan.
- Header/token representation.
- Error response.
- Session binding yang diperlukan.
- Ketentuan refresh.

## Authorization

- RBAC.
- Resource scope.
- Deny by default.
- Explicit permissions.
- Maker-checker constraints.

## Idempotency

Untuk operasi kritis:

- e-DO issue.
- Quota reservation.
- Mill ticket.
- Reconciliation.
- Payment approval.
- Payment recording.

Definisikan kontrak Idempotency-Key sesuai kebutuhan, termasuk:

- Header.
- Repeated identical request.
- Repeated key with different payload.
- Scope key.
- Expected conflict response.
- Retry behavior.

Jangan mengarang retention period final jika belum ditentukan.

## Concurrency

Definisikan cara client menghadapi:

- Stale version.
- Optimistic lock.
- Duplicate submission.
- Quota conflict.
- Concurrent approval.

Perilaku respons harus konsisten.

Mekanisme PostgreSQL row locking menjadi pekerjaan backend, bukan M0.

---

# 16. PHASE I — PERFORMANCE CONTRACT

Jangan menghapus performance requirements hanya karena M0 belum menulis kode.

Dokumentasikan kebutuhan kontraktual:

- Pagination.
- Maximum page size.
- Filtering.
- Sorting.
- Stable query ordering.
- ETag/versioning jika dipilih.
- Cache freshness.
- Cache invalidation expectations.
- Timeouts.
- Retry semantics.
- Request limits.
- Idempotency.
- Safe handling of expensive reports.

Buat klasifikasi kandidat Redis:

**Public Read Cache**

- Harga.
- Direktori PKS.
- Data referensi publik.

**Internal Read Cache**

- Agregasi dashboard yang sesuai.

**Do Not Treat as Cached Source of Truth**

- Kuota tersedia untuk keputusan reservasi kritis.
- Status pembayaran final.
- Settlement.
- Approval.
- Transactional reconciliation.

Jika data privat di-cache, scope isolation wajib direncanakan.

Kegagalan cache baca nonkritis dapat menggunakan database fallback.

Kegagalan komponen keamanan tidak boleh menghasilkan fail-open.

Jangan menetapkan target performa sebagai hasil tes yang sudah tercapai.

Bedakan:

- Performance target.
- Measurement method.
- Actual benchmark result.

Actual benchmark baru diperoleh pada milestone implementasi.

---

# 17. PHASE J — REQUIREMENT TRACEABILITY MATRIX

Buat:

`docs/m0/M0_REQUIREMENT_TRACEABILITY.md`

Matrix minimal:

| Field              | Keterangan               |
| ------------------ | ------------------------ |
| Requirement ID     | Dari PRD                 |
| Business Flow      | FLOW dari AFD            |
| Business Rule      | BSD                      |
| Data Entity        | DBD                      |
| API Operation      | OpenAPI operationId      |
| Role/Permission    | Role matrix              |
| Frontend Route     | AFD §36 / FigCraft D5   |
| Fixture            | File/scenario            |
| Test Case          | Contract test            |
| Milestone Backend  | IPD                      |
| Milestone Frontend | IPD                      |
| Status             | Covered/Deferred/Pending |

Tidak semua requirement harus memiliki endpoint.

Untuk requirement UI-only, jelaskan mengapa tidak memerlukan API.

Untuk future scope, gunakan DEFERRED, bukan menambahkan API produksi fiktif.

Untuk pending SOP, gunakan PENDING_SOP.

Jika ada Core MVP requirement yang belum memiliki kontrak memadai, jadikan temuan M0.

---

# 18. PHASE K — VALIDATION & CONTRACT TESTING

M0 wajib mempunyai pengujian nyata.

Boleh membuat script pengujian khusus kontrak di `contracts/tests/` dan `contracts/scripts/`.

Gunakan dependency minimal yang tersedia atau dapat ditentukan secara reproducible.

Jangan membuat aplikasi backend untuk melakukan validasi.

## K1 — YAML & JSON Syntax

Validasi:

- Semua YAML dapat diparse.
- Semua JSON dapat diparse.
- Tidak ada malformed syntax.
- Tidak ada duplicate key ambigu.

## K2 — OpenAPI Schema Validation

Validasi:

- OpenAPI document valid.
- Schema valid.
- `$ref` resolvable.
- OperationId unik.
- Path parameter lengkap.
- Required fields konsisten.
- Nullable schema konsisten.
- Security scheme valid.
- Response schema tersedia.
- Example conforms to schema.

Gunakan validator OpenAPI yang benar-benar tersedia atau dapat dipasang secara aman untuk kebutuhan M0.

Catat versi tool.

## K3 — Error Catalog Consistency

Pastikan:

- Setiap error code yang dipakai ada dalam katalog.
- HTTP status sesuai katalog.
- Tidak ada error code duplikat.
- Public message aman.
- Retryability konsisten.

## K4 — State Catalog Consistency

Pastikan:

- State yang dipakai OpenAPI tersedia pada state catalog.
- Setiap transition mengacu pada state valid.
- Initial state valid.
- Terminal states valid.
- Tidak ada transition yang melanggar aturan bisnis.
- Pending SOP tidak diperlakukan sebagai confirmed rule.

## K5 — Role-Permission Consistency

Pastikan:

- Permission code unik.
- Semua role terdaftar.
- Semua internal operations mempunyai security/authorization metadata sesuai standar kontrak.
- Public operations tidak mewajibkan login.
- Scoped resources mempunyai scope policy.
- Tidak ada admin approval privilege implisit.

## K6 — Fixtures Validation

Pastikan:

- Valid JSON.
- UUID valid.
- Decimal fields berbentuk string sesuai schema.
- Date/time valid.
- Entity references konsisten.
- State terdaftar.
- Tidak ada secret.
- Tidak ada data privat nyata.
- Contoh response memenuhi OpenAPI.
- Error scenarios memenuhi Error Catalog.

## K7 — Cross-Document Traceability

Pastikan:

- Seluruh domain Core MVP terpetakan.
- Seluruh FLOW inti terpetakan.
- Rute AFD memiliki API dependency atau alasan tanpa API.
- Business rules kritis memiliki skenario validasi.
- Deferred scope tidak menjadi kewajiban implementasi tanpa keputusan.
- Tidak ada perubahan dokumen spesifikasi secara tersembunyi.

## K8 — Frontend Consumer Compatibility

Apabila tool tersedia, lakukan pemeriksaan:

- OpenAPI dapat dibaca type generator.
- Response schema menghasilkan tipe yang berguna.
- Enum dan nullability konsisten.
- Decimal string tetap string.
- Fixture cocok untuk MSW.

Gunakan temporary directory.

Jangan membuat source code frontend pada M0.

## K9 — Backend Provider Compatibility

Lakukan pemeriksaan statis bahwa:

- Operation schemas jelas.
- Auth requirements jelas.
- Error responses tersedia.
- Numeric precision jelas.
- API conventions kompatibel dengan implementasi FastAPI yang direncanakan.

Jangan membuat aplikasi FastAPI untuk menguji hal ini.

## K10 — Repository Scope Check

Jalankan pemeriksaan Git.

Pastikan:

- Tidak ada perubahan `backend/`.
- Tidak ada perubahan `frontend/`.
- Tidak ada migration.
- Tidak ada perubahan desain.
- Tidak ada perubahan enam dokumen V1.1.
- Hanya file M0 yang diizinkan berubah.

Jalankan `git diff --check`.

Jangan otomatis mengembalikan perubahan yang sudah ada sebelum pekerjaan M0.

Catat baseline Git sebelum mulai untuk membedakan perubahan lama dan perubahan M0.

---

# 19. NEGATIVE TEST CASES

Selain contoh yang berhasil, M0 harus menyediakan kontrak untuk penolakan berikut.

| Scenario                                                  | Expected Behavior                                |
| --------------------------------------------------------- | ------------------------------------------------ |
| Publik mengakses data petani                              | Ditolak                                          |
| Operator koperasi membaca koperasi lain                   | Ditolak                                          |
| Petugas PKS mengubah tiket PKS lain                       | Ditolak                                          |
| Admin teknis menyetujui pembayaran tanpa izin             | Ditolak                                          |
| Harga draft dipublikasikan                                | Ditolak                                          |
| Harga expired dinyatakan sebagai harga aktif              | Ditolak/difilter sesuai kebijakan                |
| Tara lebih besar dari bruto                               | Validation error                                 |
| Satu receipt dialokasikan dua kali                        | Conflict                                         |
| Kuota tidak mencukupi                                     | Business conflict                                |
| Request e-DO duplikat                                     | Tidak menghasilkan transaksi ganda               |
| Tiket PKS duplikat                                        | Conflict                                         |
| Rekonsiliasi dispute menghasilkan invoice final           | Ditahan                                          |
| Maker menyetujui transaksi sendiri                        | Ditolak jika aturan separation-of-duties berlaku |
| Payment approval dianggap PAID                            | Dilarang                                         |
| Principal/agent UNCONFIRMED menghasilkan settlement final | Ditahan                                          |
| CSRF invalid                                              | Ditolak                                          |
| Sesi kedaluwarsa                                          | Unauthorized                                     |
| Data PKS tanpa koordinat                                  | Tidak menghasilkan marker fiktif                 |

Gunakan kode HTTP dan error code kanonis yang ditetapkan pada katalog final.

Jangan menganggap tabel di atas sebagai pengganti pembacaan 30 skenario BIZ dan aturan bisnis lain dalam BSD.

---

# 20. PENDING SOP POLICY

Identifikasi seluruh keputusan yang masih membutuhkan validasi Perumda.

Contohnya:

- Model principal/agent.
- Formula grading.
- Toleransi timbang.
- Alokasi susut multi-petani.
- Dasar settlement.
- Kewenangan pembayaran.
- Hak penerbitan atau pembatalan e-DO.
- Publikasi informasi perusahaan.
- Ketentuan transaksi yang belum disahkan.

Gunakan klasifikasi:

- CONFIRMED.
- SIMULATION_ONLY.
- PENDING_SOP.
- FUTURE.

Ketentuan:

1. Nilai simulasi boleh dipakai dalam fixture.
2. Nilai simulasi harus ditandai.
3. Tidak boleh mengklaim nilai simulasi merupakan SOP resmi.
4. Tidak boleh membuat settlement final dari aturan belum disahkan.
5. Kontrak dapat mengakomodasi nilai yang akan ditentukan kemudian.
6. Jika keputusan belum diperlukan untuk B0/F0, catat sebagai non-blocking.
7. Jika keputusan diperlukan untuk operasi finansial, tetapkan blocking condition yang jelas.
8. Jangan mengisi kebijakan yang belum tersedia dengan asumsi tersembunyi.

---

# 21. DECISION REGISTER

Buat:

`docs/m0/M0_DECISION_REGISTER.md`

Untuk setiap keputusan, catat:

- Decision ID.
- Subject.
- Context.
- Source documents.
- Alternatives jika relevan.
- Decision.
- Reason.
- Consequences.
- Status.
- Owner/approval requirement.
- Affected files.
- Next action.

Minimal keputusan teknis M0:

- OpenAPI version.
- API response envelope.
- Pagination model.
- Decimal transport.
- Timestamp convention.
- Cookie/CSRF contract.
- Idempotency conventions.
- Error structure.
- State modeling.
- Role/permission naming.
- Resource scope.
- Cache-related API expectations.
- Contract change policy.

Pemisahan keputusan teknis dengan keputusan SOP bisnis harus eksplisit.

---

# 22. CONTRACT CHANGE MANAGEMENT

Buat prosedur sederhana dan mudah dipelihara solo developer.

Dokumentasikan:

- Satu sumber kontrak kanonis.
- Perubahan schema harus melalui review.
- Breaking change harus dinilai dampaknya.
- operationId stabil.
- Tidak menghapus field yang digunakan tanpa rencana kompatibilitas.
- Backend dan frontend menggunakan versi kontrak yang sama.
- Mock fixtures diperbarui saat kontrak berubah.
- Tests dijalankan setelah setiap perubahan kontrak.
- Checkpoint mencatat versi baseline dan hasil validasi.

Jangan membuat proses birokrasi enterprise yang tidak diperlukan.

Gunakan mekanisme yang praktis untuk satu developer dan beberapa coding agents.

---

# 23. M0 QUALITY GATES

M0 hanya boleh dinyatakan PASS jika seluruh quality gate wajib telah diperiksa.

## G-M0-01 — Documentation

- Enam dokumen V1.1 dibaca.
- D5 dibaca dan diverifikasi.
- Checkpoint dibaca.
- Tidak ada dokumen wajib hilang.
- Audit awal tersedia.

## G-M0-02 — Domain Alignment

- Core business domains terpetakan.
- Requirement traceability tersedia.
- Business decisions pending tercatat.
- Tidak ada asumsi tersembunyi.

## G-M0-03 — OpenAPI

- OpenAPI valid.
- OperationId unik.
- Semua core endpoint prioritas memiliki method dan schema.
- Security requirements tersedia.
- Error responses tersedia.
- Examples valid.
- Tidak ada unresolved references.

## G-M0-04 — State & Error Catalog

- Status kanonis.
- Transitions jelas.
- Error codes konsisten.
- Pending SOP diidentifikasi.
- Tidak ada perbedaan kritis yang tidak tercatat.

## G-M0-05 — Role & Scope

- Roles lengkap.
- Permissions terdefinisi.
- Resource scope jelas.
- Public/internal separation jelas.
- Separation of duties ditangani.

## G-M0-06 — Fixtures

- Deterministik.
- Schema valid.
- Tidak ada data sensitif nyata.
- Referensi antarentitas konsisten.
- Positive/negative scenarios tersedia.

## G-M0-07 — Independent Development Readiness

Backend B0 dapat dimulai tanpa frontend.

Frontend F0 dapat dimulai tanpa backend.

Kedua jalur mengetahui:

- Kontrak API.
- State.
- Error.
- Permission.
- Mock fixtures.
- Batas perubahan kontrak.

## G-M0-08 — Automated Validation

- Pemeriksaan kontrak benar-benar dijalankan.
- Hasil dilaporkan dengan command dan exit code.
- Semua kegagalan dicatat.
- Tidak ada klaim PASS tanpa bukti.

## G-M0-09 — Scope Integrity

- Tidak ada coding backend.
- Tidak ada coding frontend.
- Tidak ada migration database.
- Tidak ada perubahan desain.
- Enam dokumen baseline tetap utuh.
- Git diff diverifikasi.

## G-M0-10 — Checkpoint & Handoff

- Checkpoint diperbarui.
- Laporan testing tersedia.
- Known limitations tersedia.
- Next actions jelas.
- Handoff Backend dan Frontend tersedia.

---

# 24. ACCEPTANCE CRITERIA DETAIL

M0 dinyatakan siap apabila:

1. Seluruh sumber utama tersedia.
2. Seluruh dokumen telah dibaca.
3. Kontrak tidak mengarang aturan bisnis.
4. Seluruh domain Core MVP memiliki coverage yang memadai.
5. Endpoint memiliki request schema yang konkret.
6. Endpoint memiliki response schema yang konkret.
7. Endpoint memiliki HTTP method yang jelas.
8. Endpoint memiliki operationId unik.
9. Endpoint internal memiliki security policy.
10. Resource scope didefinisikan.
11. Status bisnis konsisten.
12. Error codes konsisten.
13. Decimal fields konsisten.
14. Timestamp konsisten.
15. Pagination konsisten.
16. Idempotency untuk operasi kritis terdefinisi.
17. Fixture data konsisten.
18. Fixture data tidak menggunakan identitas pribadi nyata.
19. Test cases normal dan negatif tersedia.
20. D5 frontend routes terpetakan.
21. Backend dapat mengimplementasikan API tanpa desain frontend.
22. Frontend dapat menggunakan MSW tanpa backend.
23. Tidak ada konflik kritis yang diabaikan.
24. Pending SOP dipisahkan.
25. Tidak ada coding aplikasi.
26. Validation scripts berjalan.
27. Hasil pengujian dapat direproduksi.
28. Checkpoint mencerminkan hasil aktual.
29. Dokumentasi handoff tersedia.
30. Git diff menunjukkan scope yang benar.

---

# 25. CHECKPOINT MANAGEMENT

Gunakan file yang sudah tersedia:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Jangan membuat tracker kedua yang menduplikasi fungsi file ini.

Jangan menghapus checkpoint desain D0–D5.

## Sebelum Eksekusi

Catat:

- Current milestone: M0.
- Status: IN_PROGRESS.
- Baseline commit jika tersedia.
- Start date.
- Objective.
- Planned deliverables.
- Known blockers.

## Selama Eksekusi

Update setelah unit pekerjaan yang benar-benar selesai:

- M0-A Documentation.
- M0-B Domain Alignment.
- M0-C OpenAPI.
- M0-D State Catalog.
- M0-E Error Catalog.
- M0-F Role/Permission.
- M0-G Fixtures.
- M0-H Validation.
- M0-I Final Handoff.

Gunakan status:

- NOT_STARTED.
- IN_PROGRESS.
- PASS.
- FAIL.
- BLOCKED.

## Setelah Eksekusi

Catat:

- Milestone outcome.
- Files changed.
- Test commands.
- PASS/FAIL results.
- Evidence path.
- Remaining decisions.
- Next milestone recommendation.

Jangan mengubah M0 menjadi PASS jika tes yang wajib belum dijalankan.

Jangan melanjutkan coding B0 atau F0 dalam task ini.

---

# 26. REPORTING DOCUMENTS

## A. M0_DOCUMENT_AUDIT.md

Berisi:

- Inventaris sumber.
- Versi.
- Hasil pembacaan.
- Temuan kontradiksi.
- Kebutuhan teknis.
- Kebutuhan yang belum cukup jelas.
- Data dan status yang membutuhkan perhatian.

## B. M0_REQUIREMENT_TRACEABILITY.md

Berisi mapping:

PRD → AFD → BSD → DBD → API → Permission → Fixture → Test → Milestone → FigCraft.

## C. M0_DECISION_REGISTER.md

Berisi:

- Keputusan teknis M0.
- Pending SOP.
- Keputusan yang memerlukan approval.
- Alasan dan konsekuensi.

## D. M0_CONTRACT_VALIDATION_REPORT.md

Berisi:

- Command.
- Tool version.
- Exit code.
- Test count.
- Passed.
- Failed.
- Skipped.
- Warnings.
- Coverage per domain.
- Contract references.
- Remaining issues.

## E. M0_CHANGELOG.md

Berisi:

- File baru.
- File yang diubah.
- Alasan perubahan.
- Kompatibilitas.
- Known limitations.

## F. M0_HANDOFF.md

Berisi dua bagian.

**Backend Handoff**

- API operations.
- Schemas.
- Error catalog.
- State catalog.
- Security.
- Scope.
- Idempotency.
- Fixtures.
- Performance expectations.
- Acceptance criteria B0/B1 dan modul berikutnya.

**Frontend Handoff**

- API operations.
- Generated-type compatibility.
- Error and state handling.
- Route-to-operation mapping.
- Mock fixtures.
- Role-based UI metadata.
- Design handoff D5 reference.
- F0/F1 readiness.

Jangan menyalin ulang seluruh kontrak ke handoff.

Gunakan referensi file dan operationId.

---

# 27. VALIDATION EXECUTION POLICY

Jalankan pengujian langsung pada workspace.

Jangan hanya menulis rencana tes.

Utamakan pengujian yang:

- Deterministik.
- Reproducible.
- Tidak membutuhkan backend.
- Tidak membutuhkan frontend.
- Tidak membutuhkan database berjalan.
- Tidak membutuhkan Redis berjalan.
- Tidak membutuhkan layanan eksternal.
- Tidak membutuhkan secrets.
- Tidak mengubah data bisnis.

Jika alat validasi belum tersedia, cari solusi tooling yang paling sederhana.

Jika dependency/tool perlu dipasang, batasi pada tooling validasi M0 dan catat perubahan serta versi yang digunakan. Jangan memasang seluruh stack aplikasi.

Jika tool tertentu tidak dapat dijalankan, laporkan `NOT_RUN`, bukan PASS.

Jika ada error, perbaiki dan jalankan ulang.

Jangan melewatkan pengujian kritis demi mencapai status READY.

---

# 28. FINAL DECISION RULE

Gunakan salah satu keputusan berikut.

## READY — M0_CONTRACT_ALIGNMENT_VERIFIED

Hanya jika:

- Source documents lengkap.
- OpenAPI dan seluruh catalog valid.
- Required fixtures valid.
- Traceability memadai.
- Security dan state consistency lulus.
- Tidak ada critical unresolved contract conflicts.
- Tests wajib PASS.
- Checkpoint sudah diperbarui.
- Backend/Frontend handoff tersedia.

Keputusan SOP bisnis yang tidak menghalangi B0/F0 dapat tetap PENDING_SOP, dengan batas implementasi yang terdokumentasi.

## CONDITIONALLY_READY — NON_BLOCKING_M0_ISSUES

Jika:

- Kontrak dasar B0/F0 sudah valid.
- Sebagian operasi bisnis hilir masih memerlukan definisi tambahan atau keputusan SOP.
- Operasi tersebut secara eksplisit ditandai belum siap implementasi.
- Tidak ada klaim bahwa seluruh Core MVP contract sudah final.

Sebutkan secara presisi pekerjaan yang boleh dimulai dan yang harus ditahan.

## BLOCKED — M0_ALIGNMENT_INCOMPLETE

Jika:

- Dokumen wajib tidak tersedia.
- Laporan D5 tidak dapat diverifikasi.
- OpenAPI invalid.
- Security contract kritis belum jelas.
- State/error conflicts belum terselesaikan.
- Required tests gagal.
- Fixtures tidak konsisten.
- Ada kebutuhan inti yang tidak memiliki kontrak memadai.
- Tidak dapat menyatakan pengembangan B0/F0 aman dimulai.

Jangan memberikan status READY secara administratif.

---

# 29. FINAL RESPONSE FORMAT

Setelah selesai, berikan laporan dengan struktur:

### A. Executive Summary

- Status akhir.
- Baseline.
- Ringkasan tujuan yang tercapai.

### B. Documents Reviewed

- Enam dokumen.
- FigCraft D5.
- Checkpoint.
- Kontrak sebelumnya.

### C. Contract Deliverables

- File.
- Tujuan.
- Coverage.
- Validity status.

### D. API Coverage

- Endpoint counts.
- Operations by domain.
- Authenticated vs public.
- Core MVP vs deferred.

### E. State/Error/Permission Coverage

- State machines.
- Error codes.
- Roles.
- Permission mappings.
- Pending decisions.

### F. Fixture Coverage

- Jumlah fixture.
- Skenario positif.
- Skenario negatif.
- Schema validation.

### G. Validation Results

- Commands.
- PASS/FAIL.
- Exit codes.
- Warnings.
- Unexecuted tests.

### H. File Change Report

- Created.
- Modified.
- Untouched.
- Git diff review.

### I. Pending SOP / Open Decisions

- Decision ID.
- Impact.
- Blocking status.
- Next action.

### J. Checkpoint Status

- M0 completion.
- Evidence.
- Next milestone.

### K. Final Decision

Gunakan status resmi yang sesuai bukti.

---

# 30. EXECUTION DIRECTIVE

Mulai kerjakan seluruh Milestone M0 sekarang.

Urutan wajib:

1. Temukan workspace.
2. Verifikasi Git baseline.
3. Baca seluruh dokumen V1.1.
4. Baca checkpoint.
5. Baca laporan FigCraft D5.
6. Audit kebutuhan dan keputusan terbuka.
7. Buat domain dan requirement mapping.
8. Tetapkan standar API.
9. Buat OpenAPI.
10. Buat State Catalog.
11. Buat Error Catalog.
12. Buat Role-Permission Matrix.
13. Buat Shared Fixtures.
14. Buat traceability matrix.
15. Buat decision register.
16. Jalankan contract validation.
17. Perbaiki seluruh kesalahan yang dapat diselesaikan tanpa mengarang kebijakan bisnis.
18. Jalankan ulang seluruh pemeriksaan.
19. Periksa Git diff.
20. Perbarui IMPLEMENTATION_CHECKPOINTS.
21. Buat laporan dan handoff.
22. Berikan keputusan akhir berdasarkan bukti.

Jika seluruh sumber tersedia, selesaikan seluruh tahapan dalam pekerjaan ini, bukan hanya menghasilkan rencana.

Jika terjadi hambatan, selesaikan bagian lain yang independen tanpa menyembunyikan blocker.

Jangan melanjutkan ke backend B0 atau frontend F0.

Jangan mengubah source code aplikasi.

Jangan mengubah keenam dokumen baseline V1.1.

## FINAL OBJECTIVE

Menghasilkan **Shared Contract Foundation yang stabil, tervalidasi, traceable, secure, maintainable, dan siap digunakan untuk pengembangan backend dan frontend secara independen**.

Arsitektur sistem tetap:

**FastAPI Modular Monolith 4 Layer + SOLID + PostgreSQL + Redis + Performance Engineering + React/TypeScript Atomic Design.**

Milestone M0 dinyatakan selesai hanya jika hasil kontrak, dokumentasi, pengujian, dan checkpoint dapat dibuktikan.

**START WITH DOCUMENT DISCOVERY AND COMPREHENSION.**
