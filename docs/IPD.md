
# IMPLEMENTATION PLAN DOCUMENT (IPD)

## SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TANDAN BUAH SEGAR (TBS)

### PERUMDA TUAH SEKATA — UNIT AGRO NIAGA

**Versi:** 1.1 — Solo Developer Execution Baseline
**Tanggal:** 10 November 2026
**Status:** Draft Rencana Implementasi
**Pendekatan:** Contract-First, Modular Development, Independent Testing, Incremental Integration
**Backend:** FastAPI + PostgreSQL + Redis
**Frontend:** React + TypeScript + Vite
**Arsitektur Backend:** Modular Monolith — 4 Layer per Modul
**Arsitektur Frontend:** Atomic Design — 5 Levels
**Dokumen Acuan:** PRD V1.1, TRD V1.1, AFD V1.1, DBD V1.1, BSD V1.1
**Metodologi Penelitian:** Design Science Research Methodology (DSRM)

---

# 1. PENDAHULUAN

## 1.1 Tujuan Dokumen

Implementation Plan Document (IPD) merupakan dokumen rencana pelaksanaan pengembangan Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata.

IPD menerjemahkan kebutuhan produk, rancangan teknis, alur aplikasi, database, serta aturan bisnis menjadi pekerjaan implementasi yang terstruktur, terukur, dan dapat diverifikasi.

Tujuan utama IPD adalah:

1. Memisahkan pekerjaan backend dan frontend.
2. Memungkinkan kedua jalur dikembangkan secara paralel.
3. Memastikan kedua jalur menggunakan spesifikasi yang sama.
4. Menghilangkan ketergantungan frontend terhadap ketersediaan backend saat pengembangan awal.
5. Menghilangkan ketergantungan backend terhadap implementasi frontend.
6. Menetapkan kontrak integrasi yang stabil.
7. Menentukan urutan implementasi berdasarkan dependensi.
8. Menetapkan standar pengujian masing-masing jalur.
9. Mencegah regresi dari perubahan modul.
10. Menegakkan arsitektur empat layer pada setiap modul backend.
11. Menegakkan Atomic Design pada frontend.
12. Mengoptimalkan keamanan, performa, dan maintainability.
13. Menentukan prosedur integrasi backend dan frontend.
14. Menetapkan quality gate pada setiap milestone.
15. Menentukan bukti yang diperlukan sebelum sign-off.
16. Menjaga kesesuaian implementasi dengan tujuan penelitian tesis.

## 1.2 Prinsip Pelaksanaan

Pengembangan mengikuti prinsip:

- Contract-First Development.
- Independent Backend Development.
- Independent Frontend Development.
- Parallel Execution.
- Domain-Driven Modular Boundaries.
- SOLID and Clean Architecture.
- Test-Driven Verification.
- Security by Design.
- Performance by Design.
- Observable by Design.
- Atomic Design.
- User-Centered Design.
- Continuous Integration.
- Traceability.
- Incremental Delivery.
- Evidence-Based Sign-Off.

Setiap milestone harus menghasilkan pekerjaan yang dapat diperiksa, bukan hanya kode yang telah ditulis.

## 1.3 Ruang Lingkup

Produk mencakup:

- Portal Publik tanpa login.
- Informasi harga TBS multi-PKS.
- Perbandingan harga.
- Lokasi kantor dan PKS mitra.
- Autentikasi pengguna internal.
- Master data petani, koperasi, kebun, dan PKS.
- Penerimaan TBS.
- Penimbangan dan grading.
- Kontrak serta kuota.
- Pengiriman dan e-DO.
- Tiket timbang PKS.
- Rekonsiliasi.
- Dispute.
- Faktur serta pembayaran.
- Dashboard.
- Audit dan monitoring teknis.

Pengembangan unit usaha Listrik dan Gas tidak termasuk cakupan.

---

# 2. MODEL PENGEMBANGAN INDEPENDEN DAN PARALEL

## 2.1 Pendekatan yang Dipilih

Model pengembangan menggunakan **Contract-First, Independently Testable Development**. Baseline pelaksanaan adalah satu developer manusia dengan coding agent sebagai opsi paralel, bukan asumsi tim multi-developer.

Backend dan frontend tidak saling menunggu karena OpenAPI dan MSW memungkinkan pengembangan mandiri. Satu developer dapat memilih backend-first, frontend-first, bergantian per fitur, atau memakai coding agent paralel dengan batas edit yang jelas.

Keduanya menggunakan kontrak, kebutuhan, dan skenario pengujian yang disepakati.

### Backend Track

Mengerjakan:

- Database.
- Domain rules.
- Application use cases.
- API.
- Security.
- Caching.
- Middleware.
- Logging.
- Audit.
- Testing backend.

### Frontend Track

Mengerjakan:

- Design system.
- Komponen Atomic Design.
- Portal Publik.
- Dashboard internal.
- Formulir.
- Navigasi.
- API client.
- Mock API.
- Micro-interactions.
- Responsiveness.
- Accessibility.
- Testing frontend.

### Shared Integration Track

Mengerjakan:

- API contract.
- Shared fixtures.
- Contract validation.
- Integration testing.
- Full-stack testing.
- Security review.
- Performance review.
- Acceptance testing.

## 2.2 Prinsip Independensi

Backend harus dapat:

- Berjalan tanpa frontend.
- Menjalankan database migration.
- Menyediakan API.
- Menguji domain rules.
- Menguji transaksi bisnis.
- Menguji autentikasi.
- Menguji otorisasi.
- Menguji caching.
- Menguji performa.
- Menguji security.
- Menjalankan simulasi end-to-end melalui API.

Frontend harus dapat:

- Berjalan tanpa backend.
- Menampilkan seluruh halaman.
- Menggunakan mock API.
- Menguji seluruh navigasi.
- Menguji role-based UI.
- Menguji formulir.
- Menguji kondisi loading dan error.
- Mensimulasikan transaksi.
- Menjalankan browser testing.
- Menjalankan accessibility testing.
- Menghasilkan production build.

Pengujian independen tidak dianggap sebagai pengujian integrasi.

## 2.3 Kapan Integrasi Dilakukan?

Integrasi dilakukan setelah kedua jalur memenuhi readiness gate masing-masing.

Namun, integrasi dapat dilakukan secara bertahap per modul tanpa harus menunggu seluruh produk selesai.

Contoh:

Modul harga backend dan halaman harga frontend dapat diintegrasikan ketika keduanya sudah memenuhi kontrak dan pengujian yang relevan, meskipun modul rekonsiliasi belum selesai.

---

# 3. SUMBER KEBENARAN DOKUMENTASI

## 3.1 Dokumen Utama

Kedua jalur wajib menggunakan enam dokumen berikut.

| Dokumen | Fungsi                                          |
| ------- | ----------------------------------------------- |
| PRD     | Kebutuhan dan tujuan produk                     |
| TRD     | Standar arsitektur dan teknologi                |
| AFD     | Navigasi, workflow, dan state transition        |
| DBD     | Data model, relasi, dan constraint              |
| BSD     | Aturan dan kalkulasi bisnis                     |
| IPD     | Urutan implementasi, quality gate, dan sign-off |

## 3.2 Prioritas Keputusan

Jika terjadi perbedaan informasi:

- Kebutuhan produk ditelusuri ke PRD.
- Keputusan arsitektur ditelusuri ke TRD.
- Perubahan status ditelusuri ke AFD.
- Struktur serta integritas data ditelusuri ke DBD.
- Formula dan kewenangan ditelusuri ke BSD.
- Urutan pelaksanaan ditelusuri ke IPD.

Apabila dua dokumen bertentangan, pengembang tidak boleh diam-diam memilih salah satunya.

Perbedaan harus dicatat dalam Decision Register, diperiksa, lalu dokumen yang terdampak diperbarui.

## 3.3 Kontrak Bersama

Selain enam dokumen, diperlukan artefak yang dapat langsung dipakai oleh kode:

1. OpenAPI Specification.
2. API Error Catalog.
3. Business State Catalog.
4. Shared Test Fixtures.
5. Role-Permission Matrix.
6. Requirement Traceability Matrix.
7. Architecture Decision Records.
8. Change Log.

Artefak tersebut bukan pengganti PRD–IPD, melainkan turunan yang mempermudah implementasi paralel.

---

# 4. CONTRACT-FIRST DEVELOPMENT

## 4.1 Keputusan Utama

**IPD-CON-001**

Kontrak REST API harus disepakati sebelum fitur backend atau frontend yang bergantung pada endpoint tersebut mulai dikembangkan.

**IPD-CON-002**

Kontrak API menggunakan OpenAPI 3.1 atau versi yang kompatibel dengan seluruh toolchain terpilih.

**IPD-CON-003**

Satu file OpenAPI yang disetujui menjadi sumber utama definisi request dan response.

**IPD-CON-004**

Backend wajib mengimplementasikan perilaku sesuai kontrak.

**IPD-CON-005**

Frontend wajib membangun API client berdasarkan kontrak yang sama.

**IPD-CON-006**

Perubahan kontrak harus melalui prosedur review.

**IPD-CON-007**

Perubahan kontrak yang berpotensi merusak kompatibilitas tidak boleh dilakukan sepihak.

## 4.2 Isi Kontrak API

Kontrak harus mendefinisikan:

- Endpoint.
- HTTP method.
- Parameter path.
- Query parameter.
- Request body.
- Response body.
- HTTP status.
- Error code.
- Authentication.
- Authorization scope.
- Pagination.
- Filtering.
- Sorting.
- Idempotency.
- Contoh data.
- Tanggal atau format waktu.
- Satuan nilai.
- Nullable fields.
- Required fields.

## 4.3 Contoh Standar Response

Response sukses:

```json
{
  "success": true,
  "data": {
    "id": "example-id",
    "status": "PUBLISHED"
  },
  "meta": null,
  "request_id": "req_example_001"
}
```

Response gagal:

```json
{
  "success": false,
  "error": {
    "code": "PRICE_NOT_VERIFIED",
    "message": "Harga belum dapat dipublikasikan.",
    "details": null
  },
  "request_id": "req_example_002"
}
```

Contoh tersebut merupakan standar rancangan awal. Response daftar memiliki struktur `meta` untuk pagination dan informasi tambahan jika diperlukan.

## 4.4 Standar Nilai Numerik pada API

Nilai berat dan uang harus mempunyai representasi konsisten.

Rekomendasi:

- Nilai uang presisi dikirim sebagai string desimal.
- Nilai berat presisi dikirim sebagai string desimal.
- Persentase yang berdampak pada aturan bisnis dikirim sebagai nilai desimal yang terdokumentasi.
- Frontend menggunakan format tampilan rupiah dan kilogram tanpa mengubah nilai sumber.

Contoh:

```json
{
  "weight_kg": "9900.000",
  "price_per_kg": "2850.00",
  "total_amount": "28215000.00"
}
```

Backend tidak boleh mengirim format rupiah seperti `Rp28.215.000` sebagai nilai numerik untuk kalkulasi.

Frontend bertanggung jawab terhadap formatting tampilan.

## 4.5 State Catalog

Semua status bisnis harus mempunyai definisi yang sama.

Contoh:

- `PENDING_VERIFICATION`
- `PUBLISHED`
- `VALIDATED`
- `READY`
- `IN_TRANSIT`
- `ARRIVED`
- `RECEIVED`
- `MATCHED`
- `DISPUTE_HOLD`
- `UNDER_REVIEW`
- `RESOLVED`
- `APPROVED`
- `PAID`

Frontend tidak boleh membuat nama status baru tanpa persetujuan kontrak.

Backend tidak boleh mengganti nama status yang sudah digunakan tanpa proses perubahan.

## 4.6 API Contract Testing

Pengujian harus memastikan:

- Response memenuhi schema.
- Required fields tersedia.
- Nullable fields sesuai definisi.
- Error response konsisten.
- Status code benar.
- Authentication dan authorization diterapkan.
- Enum status konsisten.
- Pagination sesuai kontrak.

---

# 5. STRUKTUR REPOSITORY DAN BATAS PEKERJAAN

## 5.1 Strategi Repository

Baseline menggunakan satu repository dengan pemisahan folder yang jelas.

```text
agroniaga-tbs/
├── docs/
│   ├── PRD.md
│   ├── TRD.md
│   ├── AFD.md
│   ├── DBD.md
│   ├── BSD.md
│   ├── IPD.md
│   └── adr/
│
├── contracts/
│   ├── openapi.v1.yaml
│   ├── error-catalog.yaml
│   ├── state-catalog.yaml
│   ├── role-permissions.yaml
│   └── fixtures/
│
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   ├── scripts/
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── tests/
│   ├── package.json
│   └── package-lock.json
│
├── integration/
│   ├── tests/
│   ├── scripts/
│   └── reports/
│
├── infra/
│   ├── docker/
│   ├── compose/
│   └── monitoring/
│
├── .github/
│   └── workflows/
│
└── README.md
```

Nama folder dapat disesuaikan saat inisialisasi proyek, tetapi batas kepemilikan harus dipertahankan.

## 5.2 Batas Edit Backend Track

Backend Track boleh mengubah:

- `backend/`
- Dokumentasi implementasi backend.
- Test backend.
- Konfigurasi backend yang menjadi tanggung jawabnya.

Backend Track tidak boleh mengubah komponen frontend secara sepihak.

Perubahan OpenAPI harus melalui Shared Contract Review.

## 5.3 Batas Edit Frontend Track

Frontend Track boleh mengubah:

- `frontend/`
- Dokumentasi implementasi frontend.
- Test frontend.
- Design tokens dan komponen UI.

Frontend Track tidak boleh mengubah model database atau implementasi backend secara sepihak.

Perubahan kebutuhan endpoint harus diajukan pada kontrak bersama.

## 5.4 Batas Edit Shared Track

Shared Track mengelola:

- `contracts/`
- `integration/`
- Dokumentasi keputusan.
- Quality gates.
- Integrasi CI.
- Konfigurasi lintas layanan.

## 5.5 Migrasi Database

File migration PostgreSQL dikelola melalui backend track dengan satu pemilik perubahan aktif untuk setiap migrasi.

Pengembang frontend tidak membuat atau mengedit migrasi database.

Perubahan DBD harus disetujui sebelum migrasi yang memengaruhi kontrak data bisnis ditetapkan.

---

# 6. MILESTONE SHARED FOUNDATION

## 6.1 M0 — Requirements & Contract Alignment

**Tujuan:** Menetapkan dasar bersama sebelum backend dan frontend berjalan secara independen.

### Pekerjaan

1. Membaca dan memeriksa PRD–BSD.
2. Membuat Requirement Traceability Matrix.
3. Memeriksa konsistensi istilah.
4. Menetapkan domain bisnis.
5. Menetapkan status transaksi.
6. Menetapkan role dan scope.
7. Menyusun kontrak API.
8. Menyusun error catalog.
9. Menyusun test fixtures.
10. Menentukan mock policy untuk aturan yang belum disahkan.
11. Mencatat keputusan yang masih terbuka.
12. Menetapkan proses perubahan kontrak.

### Output

- OpenAPI baseline.
- Error catalog.
- State catalog.
- Role-permission matrix.
- Shared fixtures.
- Decision register.
- Architecture Decision Records awal.
- Requirement Traceability Matrix.

### Quality Gate M0

M0 dinyatakan PASS apabila:

- Semua domain utama terpetakan.
- Endpoint prioritas memiliki definisi.
- Kontrak dapat divalidasi.
- Contoh response konsisten.
- Status dan error code konsisten.
- Tidak ada konflik dokumen kritis yang tidak tercatat.
- Backend dapat diuji tanpa frontend dan frontend dapat diuji dengan OpenAPI/MSW tanpa backend.\n- Satu developer dapat memilih urutan kerja; batas edit dan pemilik migrasi jelas.\n- Keputusan SOP pending memiliki simulasi berlabel, tidak dianggap sebagai kebijakan resmi.

**Setelah M0 PASS, developer dapat memilih Backend Track atau Frontend Track terlebih dahulu, bergantian per fitur, atau menjalankan keduanya paralel dengan coding agent. Kontrak dan batas edit tetap wajib.**

---

# 7. SHARED CONTRACT DELIVERABLES

## 7.1 OpenAPI Baseline

Minimal mencakup:

### Public API

- GET `/api/v1/public/prices`
- GET `/api/v1/public/prices/{id}`
- GET `/api/v1/public/mills`
- GET `/api/v1/public/mills/{id}`
- GET `/api/v1/public/profile`
- GET `/api/v1/public/notices`

### Authentication API

- POST `/api/v1/auth/login`
- POST `/api/v1/auth/logout`
- GET `/api/v1/auth/me`
- GET `/api/v1/auth/csrf`

### Master Data API

- `/api/v1/farmers`
- `/api/v1/farms`
- `/api/v1/cooperatives`
- `/api/v1/mills`

### Pricing API

- `/api/v1/prices`
- `/api/v1/prices/{id}/submit`
- `/api/v1/prices/{id}/verify`
- `/api/v1/prices/{id}/publish`

### Receiving API

- `/api/v1/receipts`
- `/api/v1/receipts/{id}/weighing`
- `/api/v1/receipts/{id}/grading`
- `/api/v1/receipts/{id}/validate`

### Contracts API

- `/api/v1/contracts`
- `/api/v1/contracts/{id}`
- `/api/v1/contracts/{id}/quota`

### Logistics API

- `/api/v1/delivery-orders`
- `/api/v1/delivery-orders/{id}`
- `/api/v1/delivery-orders/{id}/issue`
- `/api/v1/delivery-orders/{id}/status`

### Mill Weighing API

- `/api/v1/mill-tickets`
- `/api/v1/mill-tickets/{id}`
- `/api/v1/mill-tickets/{id}/verify`

### Reconciliation API

- `/api/v1/reconciliations`
- `/api/v1/reconciliations/{id}`
- `/api/v1/reconciliations/{id}/calculate`
- `/api/v1/reconciliations/{id}/review`
- `/api/v1/reconciliations/{id}/resolve`

### Finance API

- `/api/v1/invoices`
- `/api/v1/payments`
- `/api/v1/payments/{id}/approve`
- `/api/v1/payments/{id}/verify`

### Reporting API

- `/api/v1/reports/overview`
- `/api/v1/reports/supply`
- `/api/v1/reports/reconciliation`
- `/api/v1/reports/finance`

Daftar tersebut adalah inventaris awal. HTTP method, schema, status, kewenangan, dan idempotency harus dijabarkan secara lengkap pada OpenAPI sebelum endpoint dikerjakan.

## 7.2 Shared Fixtures

Sediakan fixture simulasi:

- Pengguna publik.
- Petani.
- Operator koperasi.
- Staf operasional.
- Staf keuangan.
- Petugas PKS.
- Direksi.
- Administrator.
- Beberapa PKS dengan harga berbeda.
- PKS tanpa koordinat.
- Harga kedaluwarsa.
- Harga belum diverifikasi.
- Petani dan kebun.
- Kontrak aktif dan kedaluwarsa.
- Kuota cukup dan tidak cukup.
- Penerimaan TBS.
- Pengiriman multi-petani.
- Tiket timbang.
- Rekonsiliasi Matched.
- Rekonsiliasi Dispute.
- Faktur.
- Pembayaran terverifikasi dan belum terverifikasi.

Semua data simulasi harus ditandai sebagai nonproduksi.

Fixture tidak boleh berisi data pribadi nyata atau secret.

---

# BAGIAN I — BACKEND DEVELOPMENT TRACK

# 8. TUJUAN BACKEND TRACK

Backend Track dikembangkan secara independen untuk menghasilkan backend API yang aman, modular, dapat diuji, dan memenuhi aturan bisnis PRD–BSD.

Backend harus siap digunakan oleh frontend berdasarkan kontrak yang telah ditentukan.

Sistem harus dapat didemonstrasikan melalui API sebelum frontend diintegrasikan.

---

# 9. STANDAR WAJIB BACKEND

## 9.1 Arsitektur

Backend menggunakan Modular Monolith dengan Clean Architecture.

Setiap modul domain wajib memiliki empat layer:

1. Domain.
2. Application.
3. Infrastructure.
4. Presentation.

## 9.2 Aturan Dependency

- Domain tidak mengimpor FastAPI.
- Domain tidak mengimpor SQLAlchemy.
- Domain tidak mengimpor Redis.
- Domain tidak mengimpor Presentation.
- Application tidak mengimpor implementation repository konkret.
- Infrastructure mengimplementasikan port.
- Presentation menggunakan application use cases.
- Dependency Injection dilakukan pada composition root.

## 9.3 SOLID

Wajib menerapkan:

- Single Responsibility Principle.
- Open/Closed Principle.
- Liskov Substitution Principle.
- Interface Segregation Principle.
- Dependency Inversion Principle.

## 9.4 Architecture Enforcement

Gunakan:

- Import Linter.
- Architecture Tests.
- Code Review.
- Unit Tests.

Aturan import harus diuji dalam CI.

Larangan dependency lintas modul tidak hanya dijelaskan dalam dokumentasi, tetapi diperiksa secara otomatis sejauh memungkinkan.

## 9.5 Performance

- Async I/O yang sesuai.
- Connection pooling.
- Query profiling.
- Indexing.
- Pagination.
- Transaction management.
- Cache-aside.
- Controlled concurrency.
- Idempotency.
- Resource cleanup.

## 9.6 Security

- Server-side session.
- HttpOnly Secure cookie.
- CSRF protection.
- RBAC.
- Resource scope.
- Password hashing Argon2id.
- Rate limiting.
- Audit logging.
- Secrets management.
- Input validation.
- File upload protection.
- Least privilege database account.

## 9.7 Observability

- Request ID.
- Structured logging.
- Error catalog.
- Error correlation.
- Access logs.
- Security event logs.
- Business audit events.
- Metrics.
- Health checks.
- Tracing jika diperlukan.

---

# 10. BACKEND MILESTONE B0 - PROJECT FOUNDATION

## 10.1 Pekerjaan

1. Inisialisasi Python project dan dependency lock.
2. FastAPI dan Pydantic Settings.
3. PostgreSQL, SQLAlchemy Async, Alembic.
4. Redis client, connection pool, timeout, lifecycle, dan Docker Compose PostgreSQL + Redis.
5. Struktur Modular Monolith; setiap modul menggunakan empat layer.
6. Wiring dependency eksplisit, tanpa container kompleks.
7. Global exception handler, Request ID middleware, structured logging.
8. Health/readiness checks untuk dependensi wajib.
9. Architecture, startup, database, dan Redis tests.

## 10.2 Output dan Tes

- Backend dapat dimulai; /health/live dan /health/ready tersedia.
- PostgreSQL dan Redis tersambung melalui lifecycle client yang terkelola.
- Alembic baseline berjalan.
- Logging dan Request ID berfungsi.
- Connectivity, timeout/pool lifecycle, Redis health/readiness, wiring, logging, dan architecture tests lulus.
- Docker Compose menjalankan PostgreSQL dan Redis.

## 10.3 Exit Gate

B0 PASS apabila konfigurasi tervalidasi, database dan Redis tersedia, semua foundation tests lulus, readiness memeriksa dependensi wajib, tidak ada secret dalam kode, dan dokumentasi setup tersedia.

# 11. BACKEND MILESTONE B1 — IDENTITY & ACCESS

## 11.1 Pekerjaan

- User accounts.
- Roles.
- Permissions.
- Access scopes.
- Password hashing.
- Session management.
- Login.
- Logout.
- Session expiration.
- CSRF protection.
- Authorization dependencies.
- Resource ownership checks.
- Login rate limiting.
- Security event logging.

## 11.2 Test

- Login valid.
- Login salah.
- Akun nonaktif.
- Sesi kedaluwarsa.
- Logout.
- Session revocation.
- Role access.
- Cross-scope access.
- CSRF protection.
- Session fixation prevention.
- Unauthorized request.
- Privilege escalation attempt.
- Rate limiting.

## 11.3 Exit Gate

- Login dan logout bekerja.
- Session aman.
- Pengguna tidak dapat melewati hak akses.
- Scope diuji.
- Security tests kritis lulus.
- API sesuai kontrak.

---

# 12. BACKEND MILESTONE B2 — MASTER DATA

## 12.1 Pekerjaan

- Parties.
- Farmers.
- Farms.
- Cooperatives.
- Memberships.
- Mill companies.
- Mills.
- Perumda offices.
- Vehicles.
- Drivers.

## 12.2 Test

- CRUD terotorisasi.
- Unique constraints.
- Foreign keys.
- Soft deactivation.
- Historical references.
- Cross-cooperative access.
- Cross-mill access.
- Invalid coordinates.
- Duplicate codes.
- Concurrent update conflict.

## 12.3 Exit Gate

- Data master konsisten.
- Tidak ada referensi rusak.
- Otorisasi scope bekerja.
- Migrasi lulus.
- Repository integration tests lulus.

---

# 13. BACKEND MILESTONE B3 — PUBLIC PORTAL & PRICING API

## 13.1 Pekerjaan

- Harga TBS multi-PKS.
- Kategori harga.
- Sumber harga.
- Harga acuan Disbun.
- Input harga.
- Verifikasi harga.
- Publikasi harga.
- Riwayat harga.
- API informasi publik.
- Direktori lokasi PKS.
- Redis caching.
- Cache invalidation.
- Pagination dan filtering.

## 13.2 Test

- Public endpoint tanpa login.
- Private endpoint memerlukan login.
- Harga Draft tidak tampil publik.
- Harga kedaluwarsa ditangani benar.
- Harga kategori berbeda tidak dibandingkan sembarangan.
- Harga historis tetap tersedia.
- Redis cache hit.
- Cache invalidation.
- Redis failure fallback.
- Concurrent publication conflict.
- API pagination.
- Response schema.

## 13.3 Exit Gate

- Harga terverifikasi tampil publik.
- Data pribadi tidak bocor.
- Cache bekerja sesuai kebijakan.
- Harga historis konsisten.
- Public API contract tests lulus.

---

# 14. BACKEND MILESTONE B4 — TBS RECEIVING & GRADING

## 14.1 Pekerjaan

- Penerimaan TBS.
- Data sumber petani.
- Hubungan koperasi.
- Penimbangan bruto dan tara.
- Perhitungan netto.
- Grading.
- Potongan.
- Riwayat revisi.
- Status penerimaan.

## 14.2 Test

- Bruto valid.
- Tara valid.
- Tara lebih besar dari bruto ditolak.
- Decimal calculation.
- Correct grading basis.
- Tidak ada potongan ganda.
- Penerimaan duplikat.
- Revision history.
- Unauthorized correction.
- State transition.
- Farmer ownership.
- Idempotency.

## 14.3 Exit Gate

- Perhitungan benar.
- Data konsisten.
- Revisi terjaga.
- Domain unit tests lulus.
- API contract tests lulus.

---

# 15. BACKEND MILESTONE B5 — CONTRACTS & QUOTA

## 15.1 Pekerjaan

- Kontrak niaga.
- Status kontrak.
- Periode kontrak.
- Klasifikasi model usaha.
- Ketentuan harga.
- Periode kuota.
- Reservasi kuota.
- Konsumsi kuota.
- Pelepasan kuota.
- Concurrency control.

## 15.2 Test

- Kontrak valid.
- Kontrak kedaluwarsa.
- Kuota cukup.
- Kuota tidak cukup.
- Concurrent reservation.
- Quota release.
- Double consumption prevention.
- Contract scope.
- Contract version.
- Database rollback.

## 15.3 Exit Gate

- Kuota tidak dapat dilampaui melalui request bersamaan.
- Kontrak tidak aktif tidak digunakan secara tidak sah.
- Transaksi aman.
- Seluruh tes kritis lulus.

---

# 16. BACKEND MILESTONE B6 — LOGISTICS & e-DO

## 16.1 Pekerjaan

- Data pengiriman.
- Konsolidasi muatan.
- Pembuatan e-DO.
- Nomor dokumen.
- QR Code.
- Reservasi kuota.
- Status pengiriman.
- Riwayat perubahan status.
- Pembatalan.
- Idempotency.

## 16.2 Test

- Satu e-DO berisi beberapa penerimaan.
- Penerimaan tidak dialokasikan ganda.
- QR Code unik.
- Kontrak tidak valid.
- Kuota tidak cukup.
- Concurrent issuance.
- Request retry.
- Transaction rollback.
- Invalid state transition.
- Unauthorized status change.

## 16.3 Exit Gate

- e-DO berhasil diterbitkan melalui API.
- Reservasi dan alokasi konsisten.
- Tidak terdapat duplikasi.
- Status dapat ditelusuri.
- Test E2E logistik lulus.

---

# 17. BACKEND MILESTONE B7 — MILL WEIGHING

## 17.1 Pekerjaan

- Verifikasi kedatangan.
- Verifikasi e-DO.
- Tiket timbang PKS.
- Bruto, tara, netto.
- Grading PKS.
- Bukti dokumen.
- Versi tiket.
- Validasi PKS tujuan.
- Status penerimaan.

## 17.2 Test

- e-DO tidak ditemukan.
- e-DO salah PKS.
- Nomor tiket duplikat.
- Berat tidak valid.
- Ticket revision.
- Current ticket uniqueness.
- Unauthorized mill access.
- Proof upload validation.
- Cross-module references.

## 17.3 Exit Gate

- Tiket valid terhubung dengan pengiriman.
- Tiket current unik.
- Revisi tercatat.
- API dan integration tests lulus.

---

# 18. BACKEND MILESTONE B8 — RECONCILIATION & DISPUTE

## 18.1 Pekerjaan

- Pencocokan e-DO dan tiket.
- Validasi berat pembanding.
- Perhitungan selisih.
- Persentase selisih.
- Toleransi versi.
- Status Matched.
- Status Dispute/Hold.
- Dispute review.
- Penyelesaian sengketa.
- Reconciliation revisions.
- Audit keputusan.

## 18.2 Test

- Selisih normal.
- Selisih melampaui toleransi.
- Selisih negatif.
- Berat nol.
- Data tidak setara.
- Tiket belum diverifikasi.
- Rekonsiliasi ganda.
- Perubahan aturan toleransi.
- Penyelesaian tanpa izin.
- Penyelesaian tanpa alasan.
- Concurrent reconciliation.
- Revision history.

## 18.3 Exit Gate

- Semua rumus benar.
- Status sesuai aturan.
- Dispute tidak lolos otomatis.
- Riwayat tersedia.
- Domain dan integration tests kritis lulus.

---

# 19. BACKEND MILESTONE B9 — FINANCE & SETTLEMENT

## 19.1 Pekerjaan

- Settlement calculation.
- Farmer allocation.
- Invoice.
- Invoice lines.
- Payment approvals.
- Payment records.
- Payment verification.
- Separation of incoming and outgoing payments.
- Reversal/adjustment policy.
- Financial audit.

## 19.2 Prasyarat

Model usaha Perumda, formula grading, metode alokasi multi-petani, dan otorisasi pembayaran harus diperiksa.

Jika keputusan resmi belum tersedia, implementasi menggunakan mode simulasi yang diberi label dan tidak mengizinkan penyelesaian transaksi finansial nyata.

## 19.3 Test

- Decimal accuracy.
- Invoice totals.
- Correct parties.
- Valid approval.
- Unauthorized approval.
- Duplicate payment.
- Unverified payment.
- Dispute hold.
- Allocation total consistency.
- Historical price snapshot.
- Financial revision impact.
- Principal versus agent scenario.
- Cross-role financial access.

## 19.4 Exit Gate

- Perhitungan konsisten.
- Tidak ada pembayaran ganda.
- Tidak ada transaksi bermasalah yang melewati otorisasi.
- Audit lengkap.
- Mode simulasi tidak disalahartikan sebagai pembayaran nyata.
- Semua tes kritis lulus.

---

# 20. BACKEND MILESTONE B10 — REPORTING & AUDIT

## 20.1 Pekerjaan

- Dashboard aggregates.
- Supply reporting.
- Pricing reporting.
- Reconciliation reporting.
- Finance reporting.
- Audit event queries.
- Filtering.
- Export jika termasuk prioritas.
- Query optimization.
- Cache dashboard berdasarkan scope.

## 20.2 Test

- Total tonase benar.
- Transaksi dibatalkan tidak dihitung berhasil.
- Status pembayaran tidak tercampur.
- Margin sesuai model usaha.
- Data direksi sesuai kewenangan.
- Data koperasi dibatasi scope.
- Aggregation queries.
- Pagination.
- Slow query profiling.
- Cache isolation.

## 20.3 Exit Gate

- Dashboard data akurat.
- Agregasi dapat ditelusuri.
- Query utama telah diprofiling.
- Tidak ada kebocoran lintas scope.

---

# 21. BACKEND MILESTONE B11 — HARDENING & FINAL VERIFICATION

## 21.1 Pekerjaan

- Security review.
- Architecture review.
- Database performance review.
- Cache review.
- Middleware observability review.
- Error catalog validation.
- Dependency audit.
- Concurrency regression testing.
- Load testing.
- Backup and restore testing.
- API documentation.
- Full backend E2E.
- Final regression testing.

## 21.2 Exit Gate

Backend dinyatakan **BACKEND_INDEPENDENT_READY** apabila:

1. Seluruh modul prioritas terimplementasi.
2. Semua kontrak API wajib terpenuhi.
3. Seluruh Domain Layer dapat diuji terpisah.
4. Tidak ada import dependency terlarang.
5. Migrasi database berjalan.
6. Security tests kritis lulus.
7. Concurrency tests kritis lulus.
8. Logging dan audit dapat ditelusuri.
9. Pengujian performa telah dilakukan dan hasilnya dicatat.
10. Backend E2E berjalan tanpa frontend.
11. Tidak ada kegagalan regresi yang belum diselesaikan.
12. Dokumen implementasi diperbarui.

Status ini tidak berarti full-stack sudah siap atau sistem sudah layak digunakan untuk transaksi keuangan nyata.

---

# 22. BACKEND TESTING MATRIX

| Kategori       | Tools                     | Fokus                        |
| -------------- | ------------------------- | ---------------------------- |
| Formatting     | Ruff                      | Konsistensi kode             |
| Linting        | Ruff                      | Code quality                 |
| Type Checking  | Pyright                   | Konsistensi tipe             |
| Architecture   | Import Linter             | Batas antar-layer            |
| Unit           | pytest                    | Domain rules                 |
| Property-Based | Hypothesis                | Invariant dan kasus ekstrem  |
| Integration    | pytest + PostgreSQL       | Repository dan transaksi     |
| API Contract   | pytest + Schemathesis     | Kesesuaian OpenAPI           |
| Security       | pytest + security tooling | Auth, RBAC, scope, CSRF      |
| Concurrency    | pytest + PostgreSQL       | Race conditions              |
| Cache          | pytest + Redis            | TTL, invalidation, isolation |
| Performance    | Locust                    | Load dan latency             |
| E2E            | API-driven tests          | Workflow bisnis penuh        |

## 22.1 Perintah Validasi Dasar

Contoh perintah yang digunakan setelah konfigurasi proyek selesai:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run lint-imports
uv run pytest -q
uv run pytest --cov=app --cov-report=term-missing
```

Perintah quality gate dapat dipisahkan menurut jenis tes agar unit test tetap cepat dan pengujian database berjalan pada environment yang sesuai.

## 22.2 Standar Test Independence

Backend tidak boleh membutuhkan:

- Browser.
- React development server.
- Frontend build.
- Manual login melalui UI.
- Frontend API client.

Skenario bisnis harus dapat dijalankan melalui test client, HTTP test, atau service-level integration test.

---

# BAGIAN II — FRONTEND DEVELOPMENT TRACK

# 23. TUJUAN FRONTEND TRACK

Frontend Track menghasilkan antarmuka Portal Publik dan Portal Internal yang mudah digunakan, konsisten, responsif, aksesibel, serta sesuai proses bisnis.

Pengembangan frontend dilakukan menggunakan kontrak API dan mock service.

Frontend tidak memerlukan backend aktif untuk menyelesaikan rancangan halaman, komponen, navigasi, dan pengujian alur interaksi.

---

# 24. STANDAR WAJIB FRONTEND

## 24.1 Technology Stack

- React.
- TypeScript.
- Vite.
- Tailwind CSS.
- shadcn/ui.
- Radix UI.
- TanStack Router.
- TanStack Query.
- Zustand.
- React Hook Form.
- Zod.
- TanStack Table.
- Recharts.
- MapLibre.
- Lucide React.
- Sonner.
- Vitest.
- React Testing Library.
- Playwright.
- axe-core.
- Mock Service Worker.

## 24.2 Atomic Design

Frontend menggunakan lima level:

1. Atoms.
2. Molecules.
3. Organisms.
4. Templates.
5. Pages.

## 24.3 Feature-Based Architecture

Logika fitur dikelompokkan berdasarkan domain:

- Auth.
- Public Pricing.
- Public Mills.
- Master Data.
- Receiving.
- Contracts.
- Logistics.
- Mill Weighing.
- Reconciliation.
- Payments.
- Reporting.

## 24.4 UI/UX Requirements

Antarmuka menerapkan:

- 25 prinsip UX yang telah ditetapkan.
- Golden ratio sebagai pedoman komposisi.
- Micro-interactions relevan.
- Mobile-first untuk Portal Publik.
- Responsive desktop dan tablet.
- Accessibility.
- Reduced motion.
- Design tokens.
- Consistent feedback.
- Loading, empty, success, dan error states.

## 24.5 Frontend Security

- Tidak menyimpan session identifier pada localStorage.
- Tidak menyimpan secret pada frontend.
- Tidak mengandalkan menu tersembunyi sebagai otorisasi.
- Tidak menampilkan data privat dari pengguna sebelumnya setelah logout.
- Tidak mengasumsikan request berhasil sebelum ada konfirmasi backend.
- Menangani CSRF sesuai kontrak autentikasi.

---

# 25. FRONTEND MOCK API STRATEGY

## 25.1 Tujuan

Membuat frontend tetap dapat dikembangkan tanpa backend aktif.

## 25.2 Tool

Gunakan **Mock Service Worker (MSW)**.

MSW mengintersep request HTTP dari frontend dan mengembalikan data simulasi.

## 25.3 Aturan

- Mock endpoint mengikuti OpenAPI.
- Mock response sesuai schema.
- Mock error sesuai error catalog.
- Mock status sesuai state catalog.
- Mock role sesuai permission matrix.
- Mock data bersumber dari shared fixtures.
- Tidak membuat endpoint fiktif yang tidak tercatat dalam kontrak.
- Tidak melakukan hardcode response transaksi di dalam komponen visual.
- Mock hanya aktif dalam mode development/test yang diizinkan.

## 25.4 Skenario Mock

Minimal:

- Public prices available.
- No public prices.
- Price expired.
- Mill with coordinates.
- Mill without coordinates.
- Login success.
- Login failed.
- Session expired.
- Unauthorized role.
- Empty farmer list.
- Receipt validation error.
- Delivery order issued.
- Quota insufficient.
- Duplicate delivery request.
- Mill ticket verified.
- Reconciliation matched.
- Reconciliation dispute.
- Invoice rejected.
- Payment pending.
- Payment verified.
- API timeout.
- Server error.
- Network failure.

## 25.5 Stateful Mock

Untuk alur CRUD dan state transition, mock tidak cukup hanya mengembalikan JSON statis.

Gunakan state simulasi yang konsisten dalam memory atau test harness sehingga:

1. Pengguna membuat Draft.
2. Draft muncul dalam daftar.
3. Status dapat berubah.
4. Data detail diperbarui.
5. Kondisi konflik dapat disimulasikan.

State mock harus di-reset sebelum pengujian agar hasil deterministik.

## 25.6 Penanda Data Simulasi

Lingkungan mock harus menampilkan penanda yang jelas bahwa data bersifat simulasi.

Tidak diperbolehkan menyajikan harga, pembayaran, atau transaksi simulasi sebagai data operasional Perumda.

---

# 26. FRONTEND MILESTONE F0 — PROJECT FOUNDATION

## 26.1 Pekerjaan

1. Inisialisasi React + TypeScript.
2. Konfigurasi Vite.
3. Konfigurasi Tailwind.
4. Konfigurasi ESLint dan Prettier.
5. Konfigurasi Atomic Design.
6. Konfigurasi feature folders.
7. Konfigurasi routing.
8. Konfigurasi TanStack Query.
9. Konfigurasi MSW.
10. Konfigurasi API client.
11. Konfigurasi generated API types.
12. Konfigurasi testing.
13. Konfigurasi design tokens.
14. Konfigurasi responsive baseline.

## 26.2 Exit Gate

- Frontend berjalan tanpa backend.
- Mock API berfungsi.
- TypeScript strict mode aktif.
- Router berjalan.
- Tests dapat dijalankan.
- Production build berhasil.
- Struktur Atomic Design tersedia.

---

# 27. FRONTEND MILESTONE F1 — DESIGN SYSTEM

## 27.1 Pekerjaan

Bangun komponen dasar Atomic Design.

### Atoms

- Button.
- Input.
- Label.
- Text.
- Heading.
- Icon.
- Badge.
- Checkbox.
- Radio.
- Spinner.
- Skeleton.

### Molecules

- SearchField.
- FormField.
- PriceDisplay.
- StatusIndicator.
- DateFilter.
- PaginationControl.
- WeightInputGroup.
- LocationLink.

### Organisms

- PublicNavbar.
- InternalSidebar.
- DataTable.
- FilterPanel.
- FormSection.
- PageHeader.
- ConfirmDialog.
- StatusTimeline.
- KPIGrid.

### Templates

- PublicTemplate.
- AuthTemplate.
- DashboardTemplate.
- TransactionTemplate.
- DataManagementTemplate.
- ExecutiveTemplate.

## 27.2 Test

- Component rendering.
- Keyboard navigation.
- Focus states.
- Disabled states.
- Loading states.
- Error states.
- Responsive behavior.
- Accessibility.
- Reduced motion.

## 27.3 Exit Gate

- Design tokens konsisten.
- Komponen dapat digunakan ulang.
- Tidak ada style duplikat yang tidak diperlukan.
- Komponen utama lulus testing.
- Tidak ada masalah aksesibilitas kritis pada komponen dasar.

---

# 28. FRONTEND MILESTONE F2 — PUBLIC PORTAL

## 28.1 Pekerjaan

- Public Home.
- Harga TBS.
- Perbandingan harga.
- Filter harga.
- Detail PKS.
- Lokasi PKS.
- Peta.
- Profil Perumda.
- Kemitraan.
- Kontak.
- Empty states.
- Error states.
- Mobile-first responsiveness.

## 28.2 Test

- Bisa dibuka tanpa login.
- Harga tampil sesuai mock.
- Harga kedaluwarsa diberi status benar.
- Sorting bekerja.
- Filtering bekerja.
- Lokasi tanpa koordinat ditangani.
- Peta memiliki fallback.
- Mobile 375–390 px.
- Tablet 768 px.
- Desktop 1280–1440 px.
- Accessibility checks.

## 28.3 Exit Gate

- Seluruh halaman publik dapat diuji tanpa backend.
- Navigasi mudah digunakan.
- Tidak ada horizontal overflow yang tidak disengaja.
- Tidak ada data privat.
- Mock contract sesuai OpenAPI.

---

# 29. FRONTEND MILESTONE F3 — AUTHENTICATION & APP SHELL

## 29.1 Pekerjaan

- Login page.
- Session state.
- Route guards.
- RBAC UI.
- Role-based dashboard routing.
- Internal sidebar.
- Topbar.
- User menu.
- Logout.
- Unauthorized page.
- Session expired state.
- CSRF-aware API client.

## 29.2 Test

- Login sukses.
- Login gagal.
- Logout.
- Protected route.
- Unauthorized role.
- Session expired.
- Private query cache cleared.
- Back navigation after logout.
- Responsive navigation.
- Keyboard access.

## 29.3 Exit Gate

- Login flow bekerja menggunakan mock.
- Halaman sesuai role.
- Tidak ada UI bocor lintas role dalam pengujian simulasi.
- Semua state autentikasi tertangani.

Penegakan keamanan sesungguhnya tetap menjadi tanggung jawab backend.

---

# 30. FRONTEND MILESTONE F4 — MASTER DATA INTERFACE

## 30.1 Pekerjaan

- Farmer list.
- Farmer detail.
- Farmer form.
- Farm form.
- Cooperative list.
- Mill management.
- Vehicle and driver forms.
- Search.
- Filter.
- Pagination.
- Confirmation.
- Validation.

## 30.2 Test

- Create.
- Read.
- Update.
- Validation error.
- Duplicate error.
- Cross-scope UI behavior.
- Form unsaved warning.
- Large list loading.
- Empty state.
- Responsive tables.

## 30.3 Exit Gate

- Form sesuai API schema.
- Validasi bekerja.
- Semua state ditangani.
- Mock CRUD berfungsi konsisten.

---

# 31. FRONTEND MILESTONE F5 — PRICING MANAGEMENT

## 31.1 Pekerjaan

- Input harga.
- Daftar harga.
- Detail harga.
- Riwayat harga.
- Verifikasi harga.
- Publikasi harga.
- Penolakan harga.
- Status badge.
- Confirmation dialog.
- Feedback.

## 31.2 Test

- Draft.
- Submit verification.
- Approve.
- Reject.
- Publish.
- Invalid price.
- Expired period.
- Unauthorized publish.
- Duplicate action.
- Loading/error/empty states.

## 31.3 Exit Gate

- Alur harga dapat disimulasikan lengkap.
- Status UI sesuai state catalog.
- Pesan error sesuai error catalog.
- Tidak ada optimistic success yang menyesatkan.

---

# 32. FRONTEND MILESTONE F6 — RECEIVING & GRADING

## 32.1 Pekerjaan

- Receiving list.
- Receiving form.
- Farmer selector.
- Farm selector.
- Weighing form.
- Netto preview.
- Grading form.
- Receipt detail.
- Revision history.
- Status timeline.

## 32.2 Test

- Valid input.
- Invalid gross.
- Invalid tare.
- Nett preview.
- Form submission.
- Validation error.
- Duplicate receipt.
- Status transition.
- Correction flow.
- Mobile form.

## 32.3 Exit Gate

- Alur penerimaan dapat disimulasikan.
- Tidak ada duplikasi input yang tidak perlu.
- Feedback jelas.
- Data sesuai kontrak.

---

# 33. FRONTEND MILESTONE F7 — CONTRACTS & LOGISTICS

## 33.1 Pekerjaan

- Contract list.
- Contract form.
- Quota display.
- Mill selector.
- Available receipt selector.
- Delivery order form.
- Multi-receipt summary.
- e-DO detail.
- QR Code view.
- Delivery timeline.
- Delivery status actions.

## 33.2 Test

- Contract active.
- Contract expired.
- Quota insufficient.
- Select multiple receipts.
- Duplicate allocation error.
- Issue e-DO.
- State transition.
- Cancellation.
- Request retry.
- Mobile workflow.

## 33.3 Exit Gate

- Workflow logistik lengkap pada mock.
- Error state jelas.
- Tidak ada success palsu.
- Alur mudah digunakan petugas.

---

# 34. FRONTEND MILESTONE F8 — MILL WEIGHING & RECONCILIATION

## 34.1 Pekerjaan

- Delivery verification.
- Mill ticket form.
- Mill grading.
- Proof upload interface.
- Ticket detail.
- Reconciliation list.
- Reconciliation detail.
- Weight comparison.
- Difference indicator.
- Dispute workflow.
- Review history.

## 34.2 Test

- Valid ticket.
- Invalid ticket.
- Wrong mill.
- Duplicate ticket.
- Matched state.
- Dispute state.
- Negative difference.
- Missing ticket.
- Unauthorized action.
- Resolve dispute.
- Error and confirmation.
- Accessibility.

## 34.3 Exit Gate

- Semua status dapat dipahami.
- Perbedaan berat disajikan jelas.
- Pengguna tahu tindakan berikutnya.
- Mock workflow lengkap.
- Hasil kalkulasi final tetap berasal dari server pada mode live.

---

# 35. FRONTEND MILESTONE F9 — FINANCE & APPROVAL UI

## 35.1 Pekerjaan

- Settlement summary.
- Farmer allocation view.
- Invoice list.
- Invoice detail.
- Payment request.
- Approval panel.
- Payment proof.
- Payment status.
- Financial history.
- Restricted access interface.

## 35.2 Test

- Invoice draft.
- Invoice verified.
- Approval.
- Rejection.
- Dispute hold.
- Payment pending.
- Payment verified.
- Unauthorized action.
- Missing proof.
- Error state.
- Duplicate submit.
- Confirmation dialog.

## 35.3 Exit Gate

- Alur sesuai BSD.
- Nominal mudah dibaca.
- Tidak ada data keuangan yang tampil pada portal publik.
- Tidak ada status PAID sebelum konfirmasi.
- Data mock diberi penanda simulasi.

---

# 36. FRONTEND MILESTONE F10 — DASHBOARDS & ANALYTICS

## 36.1 Pekerjaan

- Farmer dashboard.
- Cooperative dashboard.
- Perumda operations dashboard.
- Mill dashboard.
- Director dashboard.
- Admin monitoring page.
- Charts.
- KPI cards.
- Filters.
- Drill-down.
- Export UI jika relevan.

## 36.2 Test

- Dashboard sesuai role.
- Loading states.
- Empty states.
- Data accuracy terhadap fixture.
- Filter periode.
- Chart readability.
- Responsive chart.
- Keyboard accessibility.
- Scope-based UI.
- No horizontal overflow.

## 36.3 Exit Gate

- Setiap peran hanya melihat informasi yang relevan.
- Semua indikator memiliki label jelas.
- Data simulasi tidak dinyatakan sebagai data operasional.
- Dashboard dapat diuji tanpa backend.

---

# 37. FRONTEND MILESTONE F11 — UI/UX HARDENING

## 37.1 Pekerjaan

- Design consistency audit.
- Atomic Design audit.
- 25 UX principles review.
- Golden ratio composition review.
- Micro-interactions review.
- Accessibility review.
- Responsive review.
- Performance profiling.
- Bundle optimization.
- Final UI regression tests.
- Browser smoke tests.

## 37.2 Viewport

Minimal diuji pada:

- 375 px.
- 390 px.
- 768 px.
- 1024 px.
- 1280 px.
- 1440 px.

## 37.3 Micro-Interaction Review

Periksa:

- Hover.
- Focus.
- Press.
- Loading.
- Success.
- Error.
- Dialog.
- Toast.
- Skeleton.
- Search feedback.
- Form validation.
- Reduced motion.

Animasi harus mendukung pemahaman tindakan dan tidak menjadi dekorasi berlebihan.

## 37.4 Exit Gate

Frontend dinyatakan **FRONTEND_MOCK_READY** apabila:

1. Seluruh halaman prioritas selesai.
2. Atomic Design diterapkan.
3. Mock API sesuai OpenAPI.
4. Role-based navigation berjalan.
5. Seluruh formulir utama bekerja dalam simulasi.
6. Semua state penting tersedia.
7. TypeScript typecheck lulus.
8. Frontend tests lulus.
9. Browser E2E mock lulus.
10. Production build berhasil.
11. Tidak ada aksesibilitas kritis yang belum ditangani pada alur utama.
12. Tidak terdapat horizontal overflow yang tidak disengaja.
13. Data mock diberi label.
14. Dokumentasi UI diperbarui.

Status ini tidak berarti backend sudah terintegrasi.

---

# 38. FRONTEND TESTING MATRIX

| Kategori          | Tools                        | Fokus                  |
| ----------------- | ---------------------------- | ---------------------- |
| Linting           | ESLint                       | Code quality           |
| Formatting        | Prettier                     | Konsistensi            |
| Type Checking     | TypeScript                   | Type safety            |
| Unit Testing      | Vitest                       | Hooks dan utility      |
| Component Testing | React Testing Library        | UI behavior            |
| Mock API          | MSW                          | Simulasi network       |
| Browser E2E       | Playwright                   | Alur pengguna          |
| Accessibility     | axe-core                     | Aksesibilitas          |
| Build             | Vite                         | Production compilation |
| Performance       | Lighthouse/Browser profiling | UX performance         |
| API Type Contract | openapi-typescript           | Keselarasan schema     |

## 38.1 Perintah Validasi Dasar

Contoh:

```bash
npm ci
npm run lint
npm run typecheck
npm run test
npm run build
npx playwright test
```

Script pada `package.json` harus dikonfigurasi sebelum perintah tersebut digunakan sebagai quality gate.

## 38.2 API Type Generation

Frontend menggunakan generated types:

```bash
npx openapi-typescript ../contracts/openapi.v1.yaml \
  -o src/lib/api/generated.d.ts
```

File generated tidak diedit manual.

Ketika OpenAPI berubah, types harus di-generate ulang dan diuji.

## 38.3 Frontend Independent Testing

Frontend tidak boleh mensyaratkan:

- PostgreSQL.
- Redis.
- FastAPI server.
- Migration database.
- Data production.
- Login terhadap backend live.

Seluruh interaksi diuji menggunakan mock handlers dan fixtures.

---

# BAGIAN III — PELAKSANAAN PARALEL

# 39. MATRIKS PENGERJAAN PARALEL

Berikut contoh urutan kerja berdasarkan dependensi, bukan kalender yang kaku.

| Gelombang | Backend Track        | Frontend Track            | Shared Track             |
| --------- | -------------------- | ------------------------- | ------------------------ |
| 0         | Persiapan repositori | Persiapan repositori      | M0 Contract Alignment    |
| 1         | B0 Foundation        | F0 Foundation             | Contract validation      |
| 2         | B1 Identity          | F1 Design System          | Auth contract review     |
| 3         | B2 Master Data       | F2 Public Portal          | Fixture validation       |
| 4         | B3 Pricing           | F3 Auth App Shell         | Pricing/auth contracts   |
| 5         | B4 Receiving         | F4 Master Data UI         | Schema review            |
| 6         | B5 Contracts         | F5 Pricing UI             | Workflow contract checks |
| 7         | B6 Logistics         | F6 Receiving UI           | State catalog checks     |
| 8         | B7 Mill Weighing     | F7 Contracts/Logistics UI | Contract regression      |
| 9         | B8 Reconciliation    | F8 Mill/Reconciliation UI | Business rule review     |
| 10        | B9 Finance           | F9 Finance UI             | Financial policy review  |
| 11        | B10 Reporting        | F10 Dashboards            | Reporting contracts      |
| 12        | B11 Hardening        | F11 UX Hardening          | Integration preparation  |

Masing-masing jalur boleh maju lebih cepat atau lambat.

Gelombang yang sama tidak berarti pekerjaan memiliki durasi atau ketergantungan yang identik.

## 39.1 Contoh Backend Lebih Cepat

Jika Backend Track menyelesaikan B6 sementara Frontend Track baru menyelesaikan F3:

- Backend tetap melanjutkan B7.
- Backend menjalankan API testing.
- Backend menjalankan concurrency testing.
- Backend menjalankan domain integration testing.
- Frontend tetap melanjutkan F4.
- Integrasi tidak menghambat pekerjaan backend yang independen.

## 39.2 Contoh Frontend Lebih Cepat

Jika Frontend Track menyelesaikan F8 sementara backend baru B4:

- Frontend tetap melanjutkan F9 atau pekerjaan UX yang tidak bergantung pada backend.
- Mock API tetap digunakan.
- Frontend E2E berjalan.
- Responsiveness diuji.
- Accessibility diuji.
- Contract drift diperiksa.
- Frontend tidak mengarang perilaku backend baru tanpa persetujuan kontrak.

## 39.3 Integrasi Parsial

Jika satu domain di kedua jalur telah siap:

Contoh:

- B3 selesai.
- F2 dan F5 selesai.

Maka integrasi harga dapat dilakukan terlebih dahulu.

Integrasi parsial tidak perlu menunggu seluruh proyek selesai.

---

# 40. INTEGRATION READINESS GATE

Sebelum sebuah fitur diintegrasikan, perlu memenuhi syarat berikut.

## 40.1 Backend Ready

- Endpoint tersedia.
- Kontrak sesuai.
- Response schema valid.
- Error schema valid.
- Authorization bekerja.
- Test terkait lulus.
- Database migration tersedia.
- Test fixtures relevan tersedia.
- Endpoint berjalan pada environment integrasi.

## 40.2 Frontend Ready

- Halaman tersedia.
- API client terhubung ke kontrak.
- Mock tests lulus.
- Loading/error states tersedia.
- Input validation sesuai.
- Role-based UI bekerja.
- Browser tests lulus.
- Tidak ada dependency ke data mock yang hardcoded dalam production path.

## 40.3 Shared Ready

- Contract version cocok.
- Perubahan kontrak telah disetujui.
- Environment integrasi tersedia.
- Test accounts tersedia.
- Test data aman.
- Kriteria penerimaan jelas.

Jika salah satu belum siap, fitur tetap berada pada jalur pengembangan independen.

---

# 41. INTEGRATION MILESTONE I0 — PUBLIC PORTAL

## 41.1 Tujuan

Mengintegrasikan Portal Publik dengan backend asli.

## 41.2 Pekerjaan

- Hubungkan harga publik ke API.
- Hubungkan daftar PKS.
- Hubungkan detail lokasi.
- Hubungkan profil perusahaan.
- Periksa caching.
- Periksa data tidak tersedia.
- Periksa error dan fallback.

## 41.3 Test

- Anonymous access.
- Response schema.
- Price sorting.
- Stale price display.
- Mill coordinates.
- Redis fallback.
- No private data leak.
- Mobile browser smoke.

## 41.4 Exit Gate

Portal Publik menggunakan backend asli dan bekerja sesuai PRD.

---

# 42. INTEGRATION MILESTONE I1 — AUTHENTICATION & MASTER DATA

## 42.1 Pekerjaan

- Hubungkan login.
- Hubungkan sesi.
- Hubungkan logout.
- Hubungkan user info.
- Hubungkan role permissions.
- Hubungkan master data.
- Periksa CSRF.
- Periksa cross-scope access.

## 42.2 Exit Gate

- Sesi nyata bekerja.
- Otorisasi nyata bekerja.
- Frontend menampilkan izin sesuai backend.
- Data privat tidak bocor.
- Full-stack tests lulus.

---

# 43. INTEGRATION MILESTONE I2 — RECEIVING TO DELIVERY

## 43.1 Pekerjaan

- Hubungkan penerimaan.
- Hubungkan penimbangan.
- Hubungkan grading.
- Hubungkan kontrak.
- Hubungkan kuota.
- Hubungkan e-DO.
- Hubungkan status pengiriman.
- Hubungkan QR Code.

## 43.2 Test

- Create receipt.
- Calculate net weight.
- Validate grading.
- Select contract.
- Reserve quota.
- Issue e-DO.
- Prevent duplicate allocation.
- Retry request.
- Update delivery status.

## 43.3 Exit Gate

Transaksi dapat dijalankan dari penerimaan TBS sampai pengiriman menggunakan frontend dan backend asli.

---

# 44. INTEGRATION MILESTONE I3 — MILL, RECONCILIATION & FINANCE

## 44.1 Pekerjaan

- Hubungkan tiket timbang.
- Hubungkan grading PKS.
- Hubungkan rekonsiliasi.
- Hubungkan dispute.
- Hubungkan settlement.
- Hubungkan invoice.
- Hubungkan payment approvals.
- Hubungkan payment records.

## 44.2 Test

- Valid mill ticket.
- Invalid mill ticket.
- Matched transaction.
- Dispute transaction.
- Resolve dispute.
- Invoice issuance.
- Payment approval.
- Payment verification.
- Financial authorization.
- Multi-farmer allocation.

## 44.3 Exit Gate

Workflow TBS sampai pencatatan penyelesaian finansial dapat dijalankan secara end-to-end dalam lingkungan pengujian.

Untuk kebijakan yang belum disahkan, hasil tetap dinyatakan sebagai simulasi.

---

# 45. INTEGRATION MILESTONE I4 — REPORTING & FULL SYSTEM

## 45.1 Pekerjaan

- Integrasi dashboard.
- Validasi agregasi.
- Validasi laporan.
- Full E2E.
- Regression testing.
- Performance testing.
- Security testing.
- Accessibility testing.
- Browser smoke testing.
- Data consistency review.

## 45.2 Exit Gate

Sistem mencapai status:

**FULL_STACK_VERIFIED**

apabila:

- Seluruh alur inti berjalan.
- Kontrak backend dan frontend cocok.
- Tidak ada regresi kritis.
- Data yang disajikan konsisten.
- Keamanan kritis telah diuji.
- Pengujian performa dilakukan.
- Hasil dan batasan terdokumentasi.

Status tersebut belum otomatis berarti production sign-off.

---

# 46. INTEGRATION CONTRACT CHANGE MANAGEMENT

## 46.1 Mengapa Diperlukan?

Jika frontend dan backend berjalan paralel, perubahan kontrak yang tidak dikendalikan akan menghasilkan ketidaksesuaian.

Contoh:

Frontend mengharapkan `price_per_kg`, tetapi backend menggantinya menjadi `price`.

Perubahan semacam ini dapat menyebabkan frontend gagal walaupun masing-masing proyek berhasil dibuild.

## 46.2 Alur Perubahan

1. Pengembang mengidentifikasi kebutuhan perubahan.
2. Pengembang membuat Contract Change Request.
3. Permintaan mencantumkan alasan dan dampak.
4. Shared Track memeriksa.
5. Backend dan frontend menilai perubahan.
6. Keputusan dicatat.
7. OpenAPI diperbarui.
8. Shared fixtures diperbarui.
9. TypeScript types di-generate ulang.
10. Backend implementation diselaraskan.
11. Mock handlers diselaraskan.
12. Contract tests dijalankan.
13. Perubahan digabung setelah gate lulus.

## 46.3 Jenis Perubahan

**Non-Breaking**

Contoh: Menambah field opsional yang tidak mengubah perilaku yang sudah ada.

**Breaking**

Contoh:

- Menghapus field.
- Mengganti nama field.
- Mengubah tipe nilai.
- Mengubah arti status.
- Mengubah endpoint.
- Mengubah authentication requirement.
- Mengubah semantik perhitungan.

Breaking change memerlukan rencana migrasi atau transisi yang disetujui.

## 46.4 Kontrak Tidak Boleh Diubah Diam-Diam

Perubahan implementasi yang bertentangan dengan kontrak tidak boleh dinyatakan selesai hanya karena unit test lokal lulus.

---

# 47. STRATEGI TESTING END-TO-END

## 47.1 Backend E2E

Dijalankan langsung melalui API.

Tidak membutuhkan frontend.

Skenario:

1. Login.
2. Create farmer.
3. Create receipt.
4. Record weighing.
5. Assign contract.
6. Create e-DO.
7. Register mill ticket.
8. Reconcile.
9. Calculate settlement.
10. Issue invoice.
11. Verify payment.
12. Check reporting.

## 47.2 Frontend Mock E2E

Dijalankan melalui browser dengan MSW.

Tidak membutuhkan backend.

Skenario:

1. Open public homepage.
2. Compare prices.
3. Open mill location.
4. Login mock.
5. Enter receiving data.
6. Create delivery order.
7. Simulate mill ticket.
8. Show matched/dispute.
9. Simulate approval.
10. Show result.

## 47.3 Full-Stack E2E

Dijalankan dengan frontend dan backend asli pada environment integrasi.

Skenario menggabungkan:

- Browser.
- HTTP.
- Session.
- PostgreSQL.
- Redis.
- Backend business rules.
- Frontend state transitions.

## 47.4 Perbedaan Hasil

Backend E2E PASS tidak membuktikan UI bekerja.

Frontend Mock E2E PASS tidak membuktikan aturan bisnis backend bekerja.

Full-Stack E2E PASS membuktikan integrasi pada skenario yang diuji, tetapi bukan otomatis membuktikan seluruh keamanan atau performa produksi.

Ketiga jenis pengujian harus dilaporkan terpisah.

---

# 48. TEST ENVIRONMENT STRATEGY

## 48.1 Backend Test Environment

Kebutuhan:

- FastAPI test server.
- PostgreSQL test database.
- Redis test instance.
- Test fixtures.
- Test configuration.
- Mock external API adapters.
- Isolated transactions.

## 48.2 Frontend Mock Environment

Kebutuhan:

- Vite dev/test.
- MSW handlers.
- Shared fixtures.
- Mock session.
- Mock roles.
- Mock state transitions.
- Browser testing.

## 48.3 Integration Environment

Kebutuhan:

- Frontend build.
- Backend API.
- PostgreSQL.
- Redis.
- Seed data.
- Test accounts.
- HTTPS sesuai kebutuhan autentikasi.
- Logging.
- Monitoring.

## 48.4 Larangan

- Jangan memakai data operasional nyata tanpa otorisasi.
- Jangan memakai credential production pada testing.
- Jangan menggunakan pembayaran nyata untuk simulasi.
- Jangan menjalankan stress tests yang mengubah data pada sistem production.
- Jangan mengandalkan browser mock untuk menyatakan backend production-ready.

---

# 49. QUALITY GATES LINTAS PROYEK

## 49.1 Gate Arsitektur

- Backend modules memiliki empat layer.
- Dependency direction benar.
- Frontend Atomic Design dipatuhi.
- Tidak ada circular dependencies.
- Ownership modul jelas.

## 49.2 Gate Fungsional

- Kebutuhan PRD dipenuhi.
- Alur AFD diikuti.
- Aturan BSD diterapkan.
- Struktur DBD konsisten.
- API TRD dipatuhi.

## 49.3 Gate Kualitas Kode

- Formatting PASS.
- Linting PASS.
- Type checking PASS.
- Unit tests PASS.
- Integration tests yang relevan PASS.
- Contract tests PASS.

## 49.4 Gate Keamanan

- Authentication bekerja.
- Authorization bekerja.
- Scope isolation bekerja.
- CSRF bekerja.
- Sensitive logging tidak terjadi.
- Secret tidak bocor.
- File upload aman.
- Security tests kritis PASS.

## 49.5 Gate Database

- Migration PASS.
- Constraint tests PASS.
- Transaction rollback PASS.
- Concurrency tests PASS.
- Index review selesai.
- Query profiling tersedia.

## 49.6 Gate Performa

Target awal mengacu pada TRD:

- P95 transaksi utama ≤ 3 detik.
- P95 pembacaan harga publik ≤ 1,5 detik.
- Tidak terdapat duplikasi transaksi pada skenario retry yang diuji.
- Query kritis dievaluasi.
- Redis cache diuji.
- Beban pengujian terdokumentasi.

Jika target belum tercapai, hasil aktual dan tindakan optimasi wajib dilaporkan.

## 49.7 Gate UI/UX

- Responsive tests PASS.
- Accessibility tests kritis PASS.
- No unintended overflow.
- Loading state.
- Empty state.
- Error state.
- Success feedback.
- Reduced motion.
- Role-based navigation.
- Relevant micro-interactions.
- Visual consistency.

---

# 50. TEST COVERAGE POLICY

## 50.1 Backend

Target awal:

- Domain Layer: minimal 80% coverage sebagai indikator tambahan.
- Application Layer: minimal 80% coverage sebagai indikator tambahan.
- Semua business rules kritis memiliki pengujian bermakna.
- Semua endpoint kritis mempunyai contract tests.
- Semua operasi mutasi sensitif mempunyai authorization tests.
- Semua operasi berisiko concurrency mempunyai concurrency tests.

Coverage bukan pengganti kualitas pengujian.

## 50.2 Frontend

Target:

- Semua flow utama memiliki browser test.
- Form kritis mempunyai validation tests.
- Semua role diuji.
- Semua state utama diuji.
- Halaman publik diuji pada mobile.
- Halaman operasional diuji pada desktop dan mobile.
- Semua operasi kritis memiliki error feedback.

Tidak wajib mengejar angka coverage tinggi pada komponen presentasional jika tidak menambah keyakinan terhadap perilaku aplikasi.

## 50.3 Full Stack

Semua skenario E2E kritis harus berhasil pada environment integrasi.

Kegagalan kontrak, keamanan, dan integritas data merupakan blocker sign-off.

---

# 51. CI/CD STRATEGY

## 51.1 Backend CI

Pipeline:

1. Checkout.
2. Install dependencies.
3. Ruff.
4. Pyright.
5. Import Linter.
6. Unit tests.
7. Integration tests.
8. Security checks.
9. API contract validation.
10. Build container.

## 51.2 Frontend CI

Pipeline:

1. Checkout.
2. Install dependencies.
3. OpenAPI type generation check.
4. ESLint.
5. TypeScript typecheck.
6. Unit tests.
7. Component tests.
8. Browser tests.
9. Accessibility checks.
10. Production build.

## 51.3 Integration CI

Pipeline:

1. Build frontend.
2. Build backend.
3. Start PostgreSQL.
4. Start Redis.
5. Apply migration.
6. Seed test fixtures.
7. Run contract tests.
8. Run API integration tests.
9. Run browser full E2E.
10. Produce test report.

## 51.4 Branch Protection

Perubahan tidak boleh digabung jika:

- CI gagal.
- Kontrak rusak.
- Architecture test gagal.
- Typecheck gagal.
- Security test kritis gagal.
- Test regresi yang relevan gagal.

Pengecualian harus terdokumentasi dan tidak digunakan untuk mengabaikan kegagalan keamanan atau integritas transaksi.

---

# 52. OPTIONAL PARALLEL CODING-AGENT WORKFLOW

## 52.1 Tujuan

Mendukung coding agent secara opsional tanpa mengasumsikan lebih dari satu developer manusia. Backend/frontend dapat dikerjakan berurutan atau paralel. Peran backend, frontend, dan integration reviewer adalah tanggung jawab kerja, bukan asumsi tiga orang; satu developer tetap pemilik integrasi, migrasi, dan keputusan.

## 52.2 Pembagian Tanggung Jawab

**Backend Developer / Agent**

Bertanggung jawab pada:

- Domain.
- Use cases.
- Repository.
- API.
- Database migration.
- Backend testing.

**Frontend Developer / Agent**

Bertanggung jawab pada:

- Atomic components.
- UI layouts.
- Pages.
- Mock handlers.
- API client.
- Frontend testing.

**Integration Reviewer / Agent**

Bertanggung jawab pada:

- Contract alignment.
- Integration tests.
- Architecture review.
- Regression analysis.
- Test evidence.

## 52.3 Batasan Pengeditan

Setiap tugas harus memiliki:

- Objective.
- Scope.
- Allowed paths.
- Forbidden paths.
- Dependencies.
- Acceptance criteria.
- Required tests.
- Deliverables.

Contoh format tugas:

**TASK ID:** B6-DO-001
**Objective:** Implementasi penerbitan e-DO.
**Allowed:** Backend logistics module dan tests terkait.
**Forbidden:** Frontend dan OpenAPI yang telah disetujui tanpa change request.
**Acceptance:** e-DO unik, muatan tidak ganda, reservasi kuota atomik.
**Tests:** Unit, integration, concurrency, contract.
**Output:** Kode, test report, changelog.

## 52.4 Parallel Edit Safety

- Gunakan branch atau worktree terpisah.
- Jangan mengedit file yang sama secara bersamaan tanpa koordinasi.
- Hindari perubahan global ketika tugas hanya menyentuh satu modul.
- Periksa diff sebelum merge.
- Rebase atau merge dilakukan secara terkendali.
- Test regresi dijalankan setelah integrasi.
- Perubahan shared contracts membutuhkan review.

## 52.5 Satu Milestone Satu Hasil Verifikasi

Setiap milestone harus memiliki laporan yang menunjukkan:

- Pekerjaan yang selesai.
- File yang berubah.
- Test yang dijalankan.
- Hasil test.
- Kegagalan.
- Risiko.
- Keputusan PASS/FAIL.
- Pekerjaan lanjutan.

Tidak cukup hanya menyatakan "fitur berhasil dibuat".

---

# 53. STANDAR LAPORAN MILESTONE

Setiap milestone wajib menghasilkan ringkasan dengan struktur:

## 53.1 Identitas

- Milestone ID.
- Nama milestone.
- Track.
- Tanggal.
- Commit reference.

## 53.2 Scope

- Objective.
- Requirements covered.
- Allowed changes.
- Excluded work.

## 53.3 Implementasi

- Modul.
- Komponen.
- Endpoint.
- Migration.
- UI pages.
- Dependency changes.

## 53.4 Testing

- Test command.
- Total pass.
- Total fail.
- Total skip.
- Test environment.
- Coverage jika relevan.
- Performance evidence jika relevan.

## 53.5 Review

- Architecture compliance.
- Contract compliance.
- Security findings.
- Known limitations.
- Regression findings.

## 53.6 Decision

- PASS.
- PASS WITH DOCUMENTED NON-BLOCKING LIMITATIONS.
- FAIL/BLOCKED.

## 53.7 Evidence

- Test logs.
- CI results.
- Screenshot UI jika relevan.
- API response samples.
- Performance results.
- Database migration logs.

Hasil tidak boleh dilaporkan PASS jika pengujian belum dijalankan.

---

# 54. DEFECT MANAGEMENT

## 54.1 Kategori Defect

**Critical**

- Kebocoran data.
- Pelanggaran otorisasi.
- Pembayaran ganda.
- Duplikasi transaksi kritis.
- Inkonsistensi keuangan serius.
- Kehilangan data transaksi.

**High**

- Workflow utama gagal.
- API tidak sesuai kontrak.
- Rekonsiliasi salah.
- Pengiriman tidak dapat diproses.
- Database deadlock tidak tertangani pada operasi penting.

**Medium**

- Form tertentu gagal.
- Filter tidak sesuai.
- Tampilan tidak responsif pada perangkat tertentu.
- Error message tidak jelas.

**Low**

- Masalah visual kecil.
- Spacing.
- Label minor.
- Animasi tidak konsisten tetapi tidak menghalangi tugas.

## 54.2 Release Blocking

Defect Critical dan High pada alur wajib harus diselesaikan sebelum sign-off yang relevan.

Defect Medium dan Low dapat ditangani menurut prioritas selama tidak menimbulkan pelanggaran kriteria penerimaan.

---

# 55. PERFORMANCE OPTIMIZATION PLAN

## 55.1 Backend

Optimasi berdasarkan profiling:

- Slow queries.
- Connection pool.
- N+1 query.
- Index.
- Pagination.
- Data aggregation.
- Cache.
- Blocking I/O.
- Serialization.
- Transaction duration.
- Lock contention.

## 55.2 Frontend

Optimasi berdasarkan pengukuran:

- Bundle size.
- Route lazy loading.
- Re-render.
- API request duplication.
- Large tables.
- Image assets.
- Map loading.
- Chart performance.
- Input responsiveness.

## 55.3 Database

Gunakan:

- EXPLAIN ANALYZE.
- Query profiling.
- Index effectiveness review.
- Concurrency testing.
- Connection pool monitoring.
- Transaction lock analysis.

## 55.4 Benchmark Evidence

Laporan minimal mencantumkan:

- Perangkat/server.
- Jumlah pengguna virtual.
- Durasi pengujian.
- Jumlah request.
- P50 latency.
- P95 latency.
- Error rate.
- Temuan bottleneck.
- Perubahan optimasi.
- Hasil sebelum dan sesudah jika ada.

Tidak boleh mengklaim "optimal" tanpa metrik dan konteks pengujian.

---

# 56. SECURITY HARDENING PLAN

## 56.1 Authentication

- Session security.
- Password hashing.
- Login rate limiting.
- Session expiration.
- Logout revocation.

## 56.2 Authorization

- Role validation.
- Resource scope.
- Cross-user access.
- Cross-cooperative access.
- Cross-mill access.
- Financial permission separation.

## 56.3 API Protection

- Input validation.
- CSRF.
- Strict CORS.
- Safe errors.
- Upload validation.
- Response filtering.
- Rate limiting.

## 56.4 Database Protection

- Least privilege.
- No superuser application account.
- Connection security.
- Backup protection.
- Data retention.
- Migration safety.

## 56.5 Monitoring

- Security event logs.
- Failed login.
- Unauthorized access.
- Permission changes.
- Critical audit events.
- Anomaly monitoring.

## 56.6 Acceptance

Tidak ada defect keamanan kritis yang belum ditangani pada alur wajib.

---

# 57. USER ACCEPTANCE & THESIS EVALUATION

## 57.1 Hubungan dengan DSRM

Pelaksanaan penelitian mengikuti:

1. Problem Identification.
2. Objectives of Solution.
3. Design and Development.
4. Demonstration.
5. Evaluation.
6. Communication.

## 57.2 Demonstration

Demonstrasi produk harus mencakup:

- Akses publik tanpa login.
- Informasi harga multi-PKS.
- Lokasi PKS.
- Penerimaan TBS.
- Pengiriman.
- Tiket PKS.
- Rekonsiliasi.
- Pembayaran tercatat.
- Dashboard.

## 57.3 Black Box Testing

Fungsi utama diuji melalui input dan output sesuai skenario yang dirancang.

Semua hasil dicatat.

## 57.4 User Acceptance Testing

UAT dilakukan menggunakan tugas dan instrumen yang telah ditetapkan atau disesuaikan secara metodologis.

## 57.5 System Usability Scale

SUS digunakan untuk mengevaluasi persepsi kebergunaan.

Target awal mengikuti proposal, yaitu rata-rata skor minimal 68.

Hasil aktual hanya dilaporkan setelah pengujian.

## 57.6 Pengukuran Efisiensi

Jika memungkinkan, lakukan pengukuran:

- Waktu penerimaan.
- Waktu pembuatan surat jalan.
- Waktu rekonsiliasi.
- Jumlah kesalahan.
- Kelengkapan data.
- Kecepatan pencarian informasi.

Bandingkan skenario setara sebelum dan sesudah penggunaan prototipe.

## 57.7 Responden

Rencana awal sesuai proposal:

- Dua petani.
- Dua operator koperasi.
- Dua staf Perumda.
- Satu pimpinan.
- Satu petugas PKS.

Evaluasi publik tanpa login dapat menggunakan tugas demonstrasi atau pengujian tambahan bila disetujui dalam desain penelitian.

---

# 58. PRODUCTION READINESS

## 58.1 Production Gate

Sistem hanya layak dipertimbangkan untuk penggunaan operasional nyata setelah:

- Kebutuhan resmi divalidasi.
- Kebijakan bisnis kritis disahkan.
- Keamanan diperiksa.
- Backup dan restore diuji.
- Monitoring tersedia.
- Deployment tervalidasi.
- Data protection diperiksa.
- Peran dan kewenangan ditetapkan.
- Pelatihan pengguna dilakukan.
- SOP operasional tersedia.
- Seluruh blocker diselesaikan.

## 58.2 Prototipe vs Production

Status:

**PROTOTYPE_VERIFIED**

berarti artefak penelitian dapat didemonstrasikan dan diuji dalam lingkungan yang ditetapkan.

Status:

**PRODUCTION_READY**

membutuhkan tambahan validasi operasional, keamanan, infrastruktur, dan persetujuan organisasi.

Keduanya tidak boleh disamakan.

---

# 59. RISK REGISTER

| Risiko                                           | Dampak                     | Mitigasi                                  |
| ------------------------------------------------ | -------------------------- | ----------------------------------------- |
| Backend dan frontend menggunakan kontrak berbeda | Integrasi gagal            | OpenAPI baseline dan contract tests       |
| Perubahan schema sepihak                         | Frontend rusak             | Contract change process                   |
| Frontend bergantung pada backend belum siap      | Pekerjaan tertunda         | MSW dan shared fixtures                   |
| Backend bergantung pada UI                       | Pengujian terhambat        | Independent API tests                     |
| Modul backend saling bercampur                   | Maintainability menurun    | Four-layer architecture dan Import Linter |
| Migrasi database bentrok                         | Kerusakan skema            | Single migration owner dan review         |
| Business rule belum disahkan                     | Kalkulasi tidak valid      | Decision register dan simulation mode     |
| Query lambat                                     | Performa rendah            | Profiling dan indexing                    |
| Cache menyajikan data usang                      | Informasi harga keliru     | TTL, invalidation, freshness labels       |
| Security lintas role gagal                       | Kebocoran data             | Authorization tests                       |
| Permintaan paralel menghasilkan duplikasi        | Integritas transaksi rusak | Idempotency dan concurrency tests         |
| UI terlalu kompleks                              | Pengguna sulit memahami    | Atomic Design dan usability testing       |
| Pengujian hanya happy path                       | Defect tersembunyi         | Negative, boundary, concurrency tests     |
| Integrasi dilakukan terlalu akhir                | Banyak konflik             | Incremental integration                   |
| Klaim hasil tanpa pengujian                      | Bukti penelitian tidak sah | Evidence-based reporting                  |

---

# 60. DEFINITION OF DONE — BACKEND

Backend Track dinyatakan selesai apabila:

1. Modul wajib selesai.
2. Four-layer architecture dipatuhi.
3. SOLID diterapkan secara bermakna.
4. Architecture tests lulus.
5. Domain tests lulus.
6. Application tests lulus.
7. Repository integration tests lulus.
8. API contract tests lulus.
9. Security tests kritis lulus.
10. Concurrency tests kritis lulus.
11. Database migrations lulus.
12. Cache tests lulus.
13. Error logging bekerja.
14. Audit bekerja.
15. Endpoint terdokumentasi.
16. Backend E2E lulus.
17. Tidak ada regresi blocker.
18. Laporan hasil tersedia.

---

# 61. DEFINITION OF DONE — FRONTEND

Frontend Track dinyatakan selesai apabila:

1. Portal Publik selesai.
2. Portal Internal selesai.
3. Atomic Design diterapkan.
4. Design tokens konsisten.
5. Seluruh halaman prioritas tersedia.
6. Mock API sesuai kontrak.
7. Loading/error/empty states tersedia.
8. Micro-interactions relevan.
9. Accessibility checks lulus.
10. Responsive tests lulus.
11. Tidak terdapat horizontal overflow yang tidak disengaja.
12. TypeScript typecheck lulus.
13. Unit/component tests lulus.
14. Browser mock E2E lulus.
15. Production build berhasil.
16. Tidak ada regresi blocker.
17. Laporan hasil tersedia.

---

# 62. DEFINITION OF DONE — INTEGRATION

Integrasi dinyatakan selesai apabila:

1. Backend dan frontend menggunakan versi kontrak yang kompatibel.
2. Public API terhubung.
3. Authentication terhubung.
4. Master data terhubung.
5. Pricing terhubung.
6. Receiving terhubung.
7. Contracts terhubung.
8. Logistics terhubung.
9. Mill weighing terhubung.
10. Reconciliation terhubung.
11. Finance workflow terhubung sesuai mode yang diizinkan.
12. Reporting terhubung.
13. Full-stack E2E lulus.
14. Security tests kritis lulus.
15. Performance evidence tersedia.
16. Data consistency tests lulus.
17. Tidak ada regression blocker.
18. Dokumentasi dan hasil pengujian diperbarui.

---

# 63. KEPUTUSAN YANG MASIH PERLU DIVALIDASI

| Kode        | Keputusan                               | Status                           |
| ----------- | --------------------------------------- | -------------------------------- |
| IPD-DEC-001 | Model bisnis principal/agent            | Perlu validasi                   |
| IPD-DEC-002 | Formula grading                         | Perlu validasi                   |
| IPD-DEC-003 | Toleransi timbang                       | Perlu validasi                   |
| IPD-DEC-004 | Metode alokasi multi-petani             | Perlu validasi                   |
| IPD-DEC-005 | Kewenangan pembayaran                   | Perlu validasi                   |
| IPD-DEC-006 | Sumber harga resmi PKS                  | Perlu validasi                   |
| IPD-DEC-007 | Hak publikasi lokasi mitra              | Perlu validasi                   |
| IPD-DEC-008 | Ketersediaan API PKS                    | Belum dipastikan                 |
| IPD-DEC-009 | Spesifikasi deployment server           | Belum final                      |
| IPD-DEC-010 | Estimasi kapasitas/waktu solo developer | Perlu estimasi setelah scope MVP |
| IPD-DEC-011 | Target waktu penyelesaian kalender      | Belum final                      |
| IPD-DEC-012 | Persyaratan penggunaan produksi         | Menunggu keputusan organisasi    |

Keputusan terbuka tidak menghalangi pengembangan fitur yang tidak bergantung pada keputusan tersebut.

Namun, keputusan kritis dapat menghalangi pengesahan workflow keuangan nyata.

---

# 64. KESIMPULAN

Implementation Plan Document V1.1 menetapkan pelaksanaan oleh satu developer dengan jalur backend dan frontend yang dapat dikembangkan serta diuji secara independen.

Pengembangan memakai satu developer manusia dengan Backend Track, Frontend Track, dan Shared Contract & Integration Track yang dapat dikerjakan independen. Urutan default adalah M0, B0, B1, modul backend menurut dependensi, F0/F1, frontend dengan mock API, integrasi per fitur, full-stack verification, lalu evaluasi tesis. Urutan dapat dibalik atau diselingi per modul; tidak perlu menunggu seluruh backend selesai.

Backend dikembangkan secara independen menggunakan FastAPI, PostgreSQL, Redis, Clean Architecture empat layer per modul, prinsip SOLID, serta pengujian domain, integrasi, keamanan, concurrency, dan performa.

Frontend dikembangkan secara independen menggunakan React, TypeScript, Atomic Design lima tingkat, Mock Service Worker, pengujian komponen, browser E2E, accessibility testing, dan prinsip UI/UX yang ditetapkan.

Kedua jalur menggunakan enam dokumen kebutuhan yang sama serta kontrak OpenAPI yang disetujui.

Frontend dapat diselesaikan menggunakan mock API tanpa menunggu backend.

Backend dapat diselesaikan serta diuji melalui API tanpa memerlukan frontend.

Integrasi dilakukan bertahap setelah setiap modul memenuhi readiness gate.

Seluruh milestone wajib menghasilkan bukti implementasi dan pengujian.

Pendekatan ini memungkinkan pengembangan yang lebih terstruktur, mengurangi konflik antarbagian, menjaga konsistensi implementasi, dan mendukung evaluasi penelitian tesis berbasis DSRM.

**STATUS: IPD V1.1 — SOLO DEVELOPER EXECUTION BASELINE**

**URUTAN IMPLEMENTASI: M0 -> B0/B1 -> MODUL BACKEND + F0/F1/FRONTEND MOCK -> INTEGRASI PER FITUR -> FULL-STACK VERIFICATION -> EVALUASI TESIS**

**Akhir Dokumen — Implementation Plan Document V1.1**
