# IMPLEMENTATION PLAN DOCUMENT (IPD)

## SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TANDAN BUAH SEGAR (TBS)

### PERUMDA TUAH SEKATA — UNIT AGRO NIAGA

**Versi:** 1.0 — Parallel Development & Execution Baseline
**Tanggal:** 10 November 2026
**Status:** Draft Rencana Implementasi
**Pendekatan:** Contract-First, Modular Development, Independent Testing, Parallel Execution
**Backend:** FastAPI + PostgreSQL + Redis
**Frontend:** React + TypeScript + Vite
**Arsitektur Backend:** Modular Monolith — 4 Layer per Modul
**Arsitektur Frontend:** Atomic Design — 5 Levels
**Dokumen Acuan:** PRD V1.0, TRD V1.0, AFD V1.0, DBD V1.0, BSD V1.0
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

# 2. MODEL PENGEMBANGAN PARALEL

## 2.1 Pendekatan yang Dipilih

Model pengembangan menggunakan **Contract-First Parallel Development**.

Pada model ini, backend dan frontend tidak menunggu implementasi satu sama lain.

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
- Backend dan frontend dapat memulai pekerjaan masing-masing tanpa asumsi tersembunyi.

**Setelah M0 PASS, Backend Track dan Frontend Track dapat berjalan paralel.**

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

# 10. BACKEND MILESTONE B0 — PROJECT FOUNDATION

## 10.1 Pekerjaan

1. Inisialisasi Python project.
2. Konfigurasi uv.
3. Instalasi FastAPI.
4. Konfigurasi Pydantic Settings.
5. Konfigurasi PostgreSQL.
6. Konfigurasi SQLAlchemy Async.
7. Konfigurasi Alembic.
8. Konfigurasi Redis.
9. Struktur modular.
10. Dependency Injection.
11. Global exception handler.
12. Request ID middleware.
13. Structured logging.
14. Health endpoints.
15. Pengujian awal.
16. Docker Compose untuk database dan cache.

## 10.2 Output

- Backend dapat dijalankan.
- `/health/live` tersedia.
- `/health/ready` tersedia.
- PostgreSQL dapat diakses.
- Redis dapat diakses.
- Alembic baseline berjalan.
- Modul mengikuti template empat layer.
- Logging awal berfungsi.

## 10.3 Test

- Application startup test.
- Database connectivity test.
- Redis connectivity test.
- Dependency injection test.
- Logging test.
- Health endpoint test.
- Architecture test.

## 10.4 Exit Gate

B0 PASS apabila:

- Server berjalan.
- Konfigurasi tervalidasi.
- Semua tes foundation lulus.
- Tidak ada secret dalam kode.
- Tidak ada pelanggaran aturan layer.
- Dokumentasi setup tersedia.

---

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

# 52. MULTI-DEVELOPER / MULTI-AGENT WORKFLOW

## 52.1 Tujuan

Memungkinkan beberapa pengembang atau coding agent bekerja secara paralel tanpa saling merusak pekerjaan.

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

| Kode        | Keputusan                            | Status                        |
| ----------- | ------------------------------------ | ----------------------------- |
| IPD-DEC-001 | Model bisnis principal/agent         | Perlu validasi                |
| IPD-DEC-002 | Formula grading                      | Perlu validasi                |
| IPD-DEC-003 | Toleransi timbang                    | Perlu validasi                |
| IPD-DEC-004 | Metode alokasi multi-petani          | Perlu validasi                |
| IPD-DEC-005 | Kewenangan pembayaran                | Perlu validasi                |
| IPD-DEC-006 | Sumber harga resmi PKS               | Perlu validasi                |
| IPD-DEC-007 | Hak publikasi lokasi mitra           | Perlu validasi                |
| IPD-DEC-008 | Ketersediaan API PKS                 | Belum dipastikan              |
| IPD-DEC-009 | Spesifikasi deployment server        | Belum final                   |
| IPD-DEC-010 | Jumlah developer dan kapasitas kerja | Belum final                   |
| IPD-DEC-011 | Target waktu penyelesaian kalender   | Belum final                   |
| IPD-DEC-012 | Persyaratan penggunaan produksi      | Menunggu keputusan organisasi |

Keputusan terbuka tidak menghalangi pengembangan fitur yang tidak bergantung pada keputusan tersebut.

Namun, keputusan kritis dapat menghalangi pengesahan workflow keuangan nyata.

---

# 64. KESIMPULAN

Implementation Plan Document V1.0 menetapkan model pengembangan paralel untuk Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata, Unit Agro Niaga.

Pengembangan dibagi menjadi:

1. Backend Development Track.
2. Frontend Development Track.
3. Shared Contract & Integration Track.

Backend dikembangkan secara independen menggunakan FastAPI, PostgreSQL, Redis, Clean Architecture empat layer per modul, prinsip SOLID, serta pengujian domain, integrasi, keamanan, concurrency, dan performa.

Frontend dikembangkan secara independen menggunakan React, TypeScript, Atomic Design lima tingkat, Mock Service Worker, pengujian komponen, browser E2E, accessibility testing, dan prinsip UI/UX yang ditetapkan.

Kedua jalur menggunakan enam dokumen kebutuhan yang sama serta kontrak OpenAPI yang disetujui.

Frontend dapat diselesaikan menggunakan mock API tanpa menunggu backend.

Backend dapat diselesaikan serta diuji melalui API tanpa memerlukan frontend.

Integrasi dilakukan bertahap setelah setiap modul memenuhi readiness gate.

Seluruh milestone wajib menghasilkan bukti implementasi dan pengujian.

Pendekatan ini memungkinkan pengembangan yang lebih terstruktur, mengurangi konflik antarbagian, menjaga konsistensi implementasi, dan mendukung evaluasi penelitian tesis berbasis DSRM.

**STATUS: IPD V1.0 — PARALLEL DEVELOPMENT & EXECUTION BASELINE**

**URUTAN IMPLEMENTASI: M0 CONTRACT ALIGNMENT → BACKEND DAN FRONTEND PARALEL → INCREMENTAL INTEGRATION → FULL-STACK VERIFICATION → EVALUASI TESIS**

**Akhir Dokumen — Implementation Plan Document V1.c**


# BUSINESS SYSTEM DOCUMENT (BSD)

## SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TANDAN BUAH SEGAR (TBS)

### PERUMDA TUAH SEKATA — UNIT AGRO NIAGA

**Versi:** 1.0 — Business Rules & Operations Baseline
**Tanggal:** 10 November 2026
**Status:** Draft untuk Validasi Operasional
**Dokumen Induk:** PRD V1.0, TRD V1.0, AFD V1.0, DBD V1.0
**Arsitektur:** Modular Monolith — Clean Architecture 4 Layer
**Lingkup Bisnis:** Unit Agro Niaga Perumda Tuah Sekata
**Metodologi Penelitian:** Design Science Research Methodology (DSRM)

---

# 1. PENDAHULUAN

## 1.1 Tujuan Dokumen

Business System Document (BSD) merupakan dokumen yang mengatur bagaimana proses bisnis perdagangan Tandan Buah Segar (TBS) dijalankan di dalam Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata.

Dokumen ini mendefinisikan:

1. Model operasional perdagangan TBS.
2. Hubungan dan tanggung jawab antaraktor.
3. Kebijakan akses informasi publik.
4. Aturan validasi dan publikasi harga TBS.
5. Aturan pengelolaan petani, koperasi, dan PKS.
6. Aturan penerimaan serta penimbangan TBS.
7. Ketentuan grading dan potongan mutu.
8. Aturan kontrak dan kuota pasokan.
9. Aturan pengiriman dan surat jalan elektronik.
10. Ketentuan penerimaan serta tiket timbang PKS.
11. Metode pencocokan dan rekonsiliasi.
12. Mekanisme penyelesaian sengketa.
13. Perhitungan nilai transaksi.
14. Alokasi nilai transaksi multi-petani.
15. Proses penagihan, persetujuan, dan pembayaran.
16. Aturan laporan manajemen.
17. Pengendalian risiko, audit, dan pengecualian.
18. Kriteria penerimaan aturan bisnis.

BSD menjadi rujukan langsung implementasi aturan bisnis pada Domain Layer dan Application Layer setiap modul backend.

## 1.2 Kedudukan BSD

Hubungan dokumen:

- PRD menetapkan kebutuhan produk.
- TRD menetapkan arsitektur dan standar teknis.
- AFD menetapkan alur aplikasi dan perubahan status.
- DBD menetapkan struktur serta integritas data.
- **BSD menetapkan aturan dan keputusan bisnis.**
- IPD menetapkan tahapan implementasi serta pengujian.

Tidak semua aturan di dalam BSD merupakan SOP yang sudah berlaku di Perumda.

Aturan dibedakan menjadi:

**Baseline Sistem:** Aturan rancangan yang diperlukan agar prototipe konsisten dan dapat diuji.

**Aturan Bersyarat:** Aturan yang hanya diterapkan setelah data atau kondisi tertentu tersedia.

**Perlu Validasi SOP:** Aturan operasional yang belum dapat dinyatakan final sebelum mendapat konfirmasi dari Perumda atau mitra terkait.

## 1.3 Batasan

BSD hanya mencakup perdagangan TBS pada Unit Agro Niaga.

Unit usaha Listrik dan Gas berada di luar cakupan.

BSD tidak menetapkan sendiri harga pembelian resmi, formula grading yang mengikat, batas potongan, komisi perdagangan, atau kebijakan pembayaran yang belum disahkan.

---

# 2. GAMBARAN MODEL BISNIS

## 2.1 Aktor Rantai Pasok

Aktor utama:

1. Petani kelapa sawit swadaya.
2. Koperasi atau kelembagaan pengumpul.
3. Unit Agro Niaga Perumda Tuah Sekata.
4. Pabrik Kelapa Sawit (PKS).
5. Pihak pengangkutan.
6. Staf keuangan dan pimpinan Perumda.

Pengunjung masyarakat umum merupakan pengguna informasi, bukan otomatis peserta transaksi perdagangan.

## 2.2 Alur Perdagangan Konseptual

Petani menyerahkan TBS kepada koperasi.

Koperasi mencatat penerimaan, melakukan penimbangan, dan menyiapkan muatan.

Perumda mengelola proses niaga sesuai hubungan kontrak yang berlaku.

Muatan dikirim ke PKS.

PKS memeriksa dan menimbang TBS.

Sistem mencocokkan catatan asal dengan hasil pabrik.

Setelah data sesuai atau sengketa diselesaikan, nilai transaksi dihitung dan proses keuangan dilanjutkan.

**Alur konseptual:**

Petani → Koperasi → Perumda/Proses Niaga → PKS → Rekonsiliasi → Penagihan/Pembayaran → Pelaporan.

## 2.3 Status Kepemilikan dan Model Usaha

Hal yang sangat penting untuk ditetapkan adalah apakah Perumda bertindak sebagai:

**Model A — Pedagang Utama (Principal)**

Perumda membeli TBS dari pemasok atau koperasi, kemudian menjualnya kembali ke PKS.

Karakteristik:

- Perumda mempunyai transaksi pembelian.
- Perumda mempunyai transaksi penjualan.
- Terdapat harga beli dan harga jual.
- Perumda dapat menanggung risiko tertentu sesuai kontrak.
- Margin dapat dihitung dari selisih penjualan, pembelian, dan biaya yang relevan.

**Model B — Perantara/Agen (Agent)**

Perumda memfasilitasi hubungan transaksi dan menerima imbalan jasa atau komisi sesuai kesepakatan.

Karakteristik:

- Kepemilikan TBS dapat tetap berada pada pihak lain.
- Perumda memperoleh pendapatan jasa/komisi.
- Nilai seluruh penjualan tidak otomatis menjadi pendapatan Perumda.
- Pembayaran dapat dilakukan antara pihak lain sesuai kontrak.

**Model C — Kombinasi**

Perumda menjalankan kedua model untuk kontrak atau mitra yang berbeda.

**Keputusan BSD-DEC-001: PERLU VALIDASI.**

Untuk rancangan sistem, setiap kontrak harus memiliki klasifikasi model transaksi sehingga penghitungan nilai, penagihan, pendapatan, dan kewajiban pembayaran dapat mengikuti hubungan hukum yang sebenarnya.

Sistem tidak boleh mengasumsikan seluruh transaksi selalu menggunakan Model A.

---

# 3. KEBIJAKAN REGULASI DAN KEPATUHAN

## 3.1 Referensi Regulasi

Referensi yang relevan untuk divalidasi dalam operasional:

1. Peraturan Menteri Pertanian Nomor 13 Tahun 2024 tentang Pembelian TBS Kelapa Sawit Produksi Pekebun Mitra.
2. Peraturan Gubernur Riau Nomor 77 Tahun 2020 tentang Tata Cara Penetapan Harga Pembelian TBS Kelapa Sawit Produksi Pekebun di Provinsi Riau.
3. Peraturan Gubernur Riau Nomor 5 Tahun 2021 tentang perubahan atas Pergub Nomor 77 Tahun 2020.
4. Ketentuan terbaru yang berlaku dari Pemerintah Provinsi Riau, Dinas Perkebunan, dan instansi berwenang.
5. Kontrak serta SOP yang sah dan berlaku pada Perumda serta mitranya.

Referensi hukum tersebut perlu diperiksa kesesuaiannya dengan kategori pekebun, bentuk kemitraan, tanggal transaksi, dan model usaha yang dijalankan.

## 3.2 Prinsip Kepatuhan Harga

**BR-CMP-001**

Sistem harus membedakan harga acuan resmi dari informasi harga pabrik.

**BR-CMP-002**

Sistem harus mencatat dasar atau kategori hubungan kemitraan jika memengaruhi ketentuan harga.

**BR-CMP-003**

Harga transaksi tidak boleh ditentukan hanya berdasarkan peringkat tertinggi pada Portal Publik.

**BR-CMP-004**

Aturan harga kontrak harus diverifikasi terhadap kewajiban regulasi yang relevan sebelum diterapkan pada transaksi nyata.

**BR-CMP-005**

Perubahan regulasi tidak boleh mengubah transaksi historis secara otomatis.

**BR-CMP-006**

Aturan operasional yang bergantung pada regulasi wajib mempunyai referensi, tanggal efektif, dan versi kebijakan.

## 3.3 Pembatasan Klaim

Sistem tidak boleh mengklaim bahwa suatu harga pasti sesuai peraturan hanya karena data harga sudah diinput.

Pemeriksaan kepatuhan dilakukan berdasarkan ketentuan dan informasi yang telah divalidasi.

Sistem dapat menampilkan status:

- Terverifikasi sebagai informasi.
- Berlaku pada periode tertentu.
- Memerlukan pemeriksaan kepatuhan.
- Tidak tersedia.

Status verifikasi sumber informasi tidak otomatis sama dengan persetujuan hukum atas transaksi.

---

# 4. PENGGUNA DAN TANGGUNG JAWAB

## 4.1 Aktor dan Kewenangan

| Aktor                     | Tanggung Jawab Utama                                             |
| ------------------------- | ---------------------------------------------------------------- |
| Pengunjung Umum           | Mengakses informasi publik                                       |
| Petani                    | Melihat informasi panen dan pembayaran pribadi                   |
| Operator Koperasi         | Mencatat penerimaan, penimbangan, dan persiapan pengiriman       |
| Staf Operasional Perumda  | Mengelola harga, kontrak, logistik, dan rekonsiliasi sesuai izin |
| Staf Keuangan Perumda     | Memeriksa tagihan serta mencatat pembayaran                      |
| Petugas PKS               | Memvalidasi kedatangan dan hasil timbang                         |
| Direksi/Pejabat Berwenang | Mengawasi serta menyetujui keputusan sesuai batas kewenangan     |
| Administrator Sistem      | Mengelola akun, konfigurasi teknis, dan keamanan                 |

## 4.2 Prinsip Pemisahan Tugas

Sistem menerapkan prinsip *maker-checker* pada tindakan berisiko.

Contoh:

- Petugas menginput harga; verifikator menyetujui publikasinya.
- Petugas mencatat revisi timbang; pejabat berwenang mengesahkan koreksi penting.
- Staf menyiapkan transaksi pembayaran; pihak berwenang memberikan persetujuan.

Pemisahan orang yang membuat dan menyetujui transaksi diwajibkan pada tindakan yang diklasifikasikan kritis, kecuali terdapat mekanisme pengecualian resmi yang disahkan dan diaudit.

## 4.3 Matriks Kewenangan

| Aktivitas                   | Pelaksana         | Persetujuan                                             |
| --------------------------- | ----------------- | ------------------------------------------------------- |
| Input harga PKS             | Staf berwenang    | Verifikator harga                                       |
| Publikasi harga             | Staf/verifikator  | Sesuai SOP                                              |
| Pendaftaran petani          | Koperasi/Perumda  | Sesuai kebijakan                                        |
| Penimbangan koperasi        | Operator koperasi | Verifikasi bila diperlukan                              |
| Penetapan tujuan pengiriman | Staf Perumda      | Sesuai batas kontrak/kuota                              |
| Penerbitan e-DO             | Petugas berwenang | Sesuai SOP                                              |
| Tiket timbang PKS           | Petugas PKS       | Verifikator yang ditetapkan                             |
| Rekonsiliasi                | Staf Perumda      | Otomatis untuk aturan normal; pemeriksaan untuk anomali |
| Penyelesaian sengketa       | Petugas pemeriksa | Pejabat berwenang                                       |
| Persetujuan pembayaran      | Pejabat berwenang | Sesuai matriks otorisasi                                |
| Pencatatan pembayaran       | Staf keuangan     | Verifikator pembayaran                                  |

Nama jabatan dan batas nominal persetujuan belum ditetapkan dalam dokumen ini.

---

# 5. ATURAN PORTAL PUBLIK

## 5.1 Prinsip Akses

**BR-PUB-001**

Masyarakat umum dapat mengakses Portal Publik tanpa login.

**BR-PUB-002**

Portal Publik hanya menampilkan informasi yang diizinkan untuk dipublikasikan.

**BR-PUB-003**

Data petani, kontrak rahasia, rincian pembayaran, dan informasi rekening tidak boleh ditampilkan melalui API publik.

**BR-PUB-004**

Setiap informasi harga harus mempunyai sumber dan waktu pembaruan.

**BR-PUB-005**

Sistem harus memberi tahu pengguna apabila informasi harga belum tersedia atau sudah tidak berlaku.

## 5.2 Informasi Publik

Informasi yang dapat dipublikasikan:

- Profil Perumda.
- Profil Unit Agro Niaga.
- Harga TBS yang telah diverifikasi untuk publikasi.
- Harga acuan Disbun dengan sumber yang jelas.
- Nama dan lokasi PKS yang diizinkan.
- Kontak resmi.
- Informasi kemitraan.

## 5.3 Informasi Terbatas

Informasi yang tidak boleh dipublikasikan tanpa dasar dan otorisasi:

- Nomor identitas petani.
- Data rekening.
- Kontrak rahasia.
- Harga pembelian khusus yang bersifat internal.
- Margin bisnis internal.
- Dokumen pengiriman privat.
- Tiket timbang yang memuat data sensitif.
- Riwayat pembayaran pribadi.
- Informasi audit dan keamanan.

## 5.4 Akses Petani

Petani dapat melihat informasi publik tanpa login.

Jika ingin melihat hasil panen dan pembayaran pribadinya, petani harus melakukan autentikasi.

Nomor telepon, nama, atau nomor penerimaan saja tidak boleh dijadikan bukti yang cukup untuk membuka data pribadi secara anonim.

---

# 6. ATURAN MASTER DATA

## 6.1 Identitas Petani

**BR-MD-001**

Setiap petani memiliki identitas sistem yang unik.

**BR-MD-002**

Data petani harus dikaitkan dengan koperasi atau hubungan pemasok yang relevan pada saat transaksi.

**BR-MD-003**

Petani yang dinonaktifkan tetap mempunyai riwayat transaksi.

**BR-MD-004**

Petani tidak dapat mengubah hasil timbangan yang telah disahkan melalui portal pribadinya.

**BR-MD-005**

Data identitas pribadi dikumpulkan hanya sesuai kebutuhan dan dasar pemrosesan yang sah.

## 6.2 Identitas Kebun

**BR-MD-006**

Satu petani dapat mempunyai lebih dari satu kebun.

**BR-MD-007**

Satu penerimaan TBS harus memiliki sumber pasokan yang dapat ditelusuri.

**BR-MD-008**

Data lokasi kebun tidak otomatis menjadi informasi publik.

## 6.3 Identitas Koperasi

**BR-MD-009**

Koperasi hanya dapat mengelola petani sesuai cakupan kewenangannya.

**BR-MD-010**

Perubahan keanggotaan tidak boleh mengubah hubungan historis transaksi lama.

## 6.4 Identitas PKS

**BR-MD-011**

Setiap PKS memiliki identitas unik.

**BR-MD-012**

Satu perusahaan dapat mempunyai lebih dari satu PKS.

**BR-MD-013**

PKS yang dinonaktifkan tidak dapat menjadi tujuan transaksi baru tanpa otorisasi khusus.

**BR-MD-014**

Alamat dan koordinat yang dipublikasikan harus berdasarkan data yang telah diperiksa.

---

# 7. ATURAN HARGA TBS

## 7.1 Klasifikasi Harga

Sistem harus membedakan minimal tiga kelompok harga.

| Jenis Harga             | Fungsi                                                                            |
| ----------------------- | --------------------------------------------------------------------------------- |
| Harga Acuan Disbun      | Informasi penetapan resmi yang relevan untuk kategori dan periode tertentu        |
| Harga Informasi PKS     | Informasi harga pembelian yang disampaikan atau bersumber dari PKS                |
| Harga Kontrak/Transaksi | Nilai harga yang sah digunakan berdasarkan hubungan niaga dan ketentuan transaksi |

Ketiga jenis harga tidak boleh disamakan hanya karena mempunyai satuan rupiah per kilogram.

## 7.2 Aturan Input Harga

**BR-PRC-001**

Harga harus bernilai positif.

**BR-PRC-002**

Harga harus mempunyai satuan yang jelas.

**BR-PRC-003**

Harga harus dikaitkan dengan PKS atau sumber penetapan yang benar.

**BR-PRC-004**

Harga mempunyai kategori, periode berlaku, dan sumber.

**BR-PRC-005**

Harga yang baru dimasukkan berstatus Draft.

**BR-PRC-006**

Harga tidak boleh dipublikasikan tanpa verifikasi yang diwajibkan.

## 7.3 Status Harga

Alur:

DRAFT → PENDING_VERIFICATION → VERIFIED → PUBLISHED.

Jika ditolak:

PENDING_VERIFICATION → REJECTED.

Jika periode berlaku telah berakhir:

PUBLISHED → Ditampilkan sebagai EXPIRED.

EXPIRED dapat berupa status tampilan yang diturunkan dari periode berlaku, bukan perubahan fisik status yang harus dijalankan secara manual.

## 7.4 Perbandingan Harga Antar-PKS

**BR-PRC-007**

Sistem hanya membandingkan harga dengan spesifikasi yang setara.

Contoh kesetaraan:

- Jenis komoditas sama.
- Kategori kualitas sebanding.
- Periode berlaku relevan.
- Satuan sama.
- Hubungan kemitraan atau ketentuan harga tidak menimbulkan perbandingan yang menyesatkan.

**BR-PRC-008**

Jika dua harga tidak sebanding, sistem harus menampilkan keterangan perbedaan atau memisahkannya ke kategori lain.

**BR-PRC-009**

Harga tertinggi tidak otomatis menjadi rekomendasi pengiriman terbaik.

## 7.5 Harga dan Lokasi PKS

Harga dapat ditampilkan bersama lokasi perusahaan.

Namun, sistem tidak boleh menyimpulkan pabrik paling menguntungkan hanya berdasarkan harga dan jarak geografis.

Biaya operasional, akses jalan, kuota, ketentuan mutu, dan kontrak tetap perlu dipertimbangkan.

## 7.6 Riwayat Harga

**BR-PRC-010**

Harga yang sudah diterbitkan harus mempunyai riwayat.

**BR-PRC-011**

Harga historis yang menjadi referensi transaksi harus tetap dapat ditelusuri.

**BR-PRC-012**

Pembaruan harga tidak boleh mengubah nilai transaksi yang sudah disepakati.

## 7.7 Harga Kedaluwarsa

Jika tidak terdapat harga aktif:

- Sistem menampilkan informasi tidak tersedia.
- Harga historis boleh ditampilkan dengan penanda bahwa harga tersebut bukan harga berlaku.
- Sistem tidak boleh menampilkan harga lama seolah-olah masih berlaku.

## 7.8 Simulasi

Contoh harga fiktif:

| PKS   | Harga Informasi |
| ----- | --------------: |
| PKS A |      Rp2.850/kg |
| PKS B |      Rp2.920/kg |
| PKS C |      Rp2.800/kg |

PKS B mempunyai nilai harga tertinggi pada contoh tersebut.

Namun, pilihan pengiriman tetap memerlukan pemeriksaan kontrak, ketentuan harga yang berlaku, kuota, mutu, dan biaya operasional.

Data ini hanya ilustrasi sistem.

---

# 8. ATURAN PENERIMAAN TBS

## 8.1 Prasyarat

Penerimaan TBS dapat dibuat apabila:

- Operator mempunyai izin.
- Koperasi atau sumber penerimaan terdaftar.
- Petani atau pemasok teridentifikasi.
- Sumber panen tersedia sesuai ketentuan.
- Tanggal penerimaan valid.

## 8.2 Aturan Pencatatan

**BR-RCV-001**

Setiap penerimaan memiliki nomor unik.

**BR-RCV-002**

Penerimaan harus terhubung dengan petani, koperasi, serta sumber kebun apabila diwajibkan.

**BR-RCV-003**

Tanggal penerimaan dicatat berdasarkan kejadian sebenarnya.

**BR-RCV-004**

Satu transaksi penerimaan tidak boleh diduplikasi oleh request berulang.

**BR-RCV-005**

Penerimaan yang belum divalidasi tidak dapat digunakan sebagai muatan pengiriman final.

## 8.3 Status

- DRAFT.
- VALIDATED.
- ALLOCATED.
- SHIPPED.
- CLOSED.
- CANCELLED.

## 8.4 Perubahan Penerimaan

Data Draft dapat diedit oleh petugas berwenang.

Setelah VALIDATED, koreksi harus tercatat.

Setelah ALLOCATED, perubahan yang memengaruhi berat atau sumber panen harus melalui pemeriksaan dampak terhadap e-DO.

Setelah SHIPPED, data tidak boleh diubah secara langsung sehingga menghilangkan sejarah transaksi.

## 8.5 Penolakan Penerimaan

Penerimaan dapat ditolak sebelum disahkan jika tidak memenuhi persyaratan.

Alasan harus dicatat.

Jika penerimaan telah digunakan pada pengiriman, penanganannya mengikuti prosedur koreksi atau pembatalan resmi.

---

# 9. ATURAN PENIMBANGAN

## 9.1 Komponen Berat

Sistem membedakan:

1. Berat bruto.
2. Berat tara.
3. Berat netto.
4. Potongan berat akibat grading jika berlaku.
5. Berat yang diakui untuk dasar penyelesaian.
6. Berat yang disepakati sebagai dasar pembayaran.

## 9.2 Rumus Dasar

**Berat Netto = Berat Bruto − Berat Tara**

Syarat:

- Bruto ≥ 0.
- Tara ≥ 0.
- Tara ≤ Bruto.
- Netto ≥ 0.

## 9.3 Contoh Perhitungan

Data simulasi:

- Bruto: 8.500 kg.
- Tara: 3.200 kg.

Hasil:

Berat Netto = 8.500 − 3.200 = **5.300 kg**.

Jika kemudian terdapat potongan grading 2% dari netto, dan dasar tersebut memang telah disetujui:

Potongan Berat = 5.300 × 2% = **106 kg**.

Berat Setelah Potongan = 5.300 − 106 = **5.194 kg**.

Ketiga angka berikut mempunyai makna berbeda:

- 5.300 kg: netto hasil timbangan.
- 106 kg: potongan grading.
- 5.194 kg: berat setelah potongan.

Sistem harus mempertahankan ketiganya secara terpisah.

## 9.4 Aturan Pembulatan

Berat disimpan dengan presisi yang ditetapkan dalam DBD.

Pembulatan pada tampilan tidak boleh mengubah data sumber.

Perhitungan nilai final harus menggunakan aturan pembulatan yang konsisten.

Metode pembulatan operasional masih perlu divalidasi.

## 9.5 Koreksi Penimbangan

**BR-WGT-001**

Setiap koreksi harus memiliki alasan.

**BR-WGT-002**

Versi penimbangan lama tetap disimpan.

**BR-WGT-003**

Koreksi yang memengaruhi transaksi terbit harus melalui otorisasi.

**BR-WGT-004**

Sistem harus menandai proses turunan yang perlu dihitung ulang atau diperiksa.

**BR-WGT-005**

Tidak boleh terdapat dua versi timbangan aktif yang bertentangan.

---

# 10. ATURAN GRADING DAN POTONGAN

## 10.1 Tujuan

Grading mencatat kondisi mutu buah dan ketentuan perlakuannya.

Contoh indikator yang mungkin relevan:

- Buah mentah.
- Buah terlalu matang.
- Buah busuk.
- Tandan kosong.
- Kotoran atau material bukan TBS.
- Kategori mutu lain sesuai ketentuan PKS.

Daftar dan definisi grading final harus mengikuti kontrak, ketentuan yang berlaku, dan SOP mitra.

## 10.2 Jenis Potongan

Sistem mendukung klasifikasi:

**Potongan Berat**

Mengurangi dasar berat menurut aturan yang disahkan.

**Potongan Nilai**

Mengurangi nilai uang transaksi tanpa mengubah catatan berat fisik.

**Penolakan Muatan**

Muatan atau sebagian muatan tidak diterima berdasarkan syarat yang berlaku.

Jenis perlakuan tersebut tidak boleh disamakan.

## 10.3 Aturan Grading

**BR-GRD-001**

Setiap aturan grading memiliki nama, dasar, formula, dan periode berlaku.

**BR-GRD-002**

Potongan harus dikaitkan dengan hasil pemeriksaan.

**BR-GRD-003**

Potongan tidak boleh diterapkan dua kali terhadap komponen yang sama.

**BR-GRD-004**

Perbedaan grading koperasi dan PKS harus disimpan sebagai data masing-masing.

**BR-GRD-005**

Sistem tidak otomatis menganggap grading koperasi sama dengan grading pabrik.

**BR-GRD-006**

Hasil grading yang disengketakan mengikuti proses pemeriksaan.

## 10.4 Aturan Penolakan

Penolakan TBS atau muatan hanya dilakukan berdasarkan syarat penerimaan yang relevan.

Sistem harus mencatat:

- Pihak yang menolak.
- Alasan.
- Referensi muatan.
- Tanggal.
- Bukti jika tersedia.
- Keputusan tindak lanjut.

Prosedur pengembalian atau pengalihan muatan masih memerlukan validasi SOP.

---

# 11. ATURAN KONTRAK NIAGA

## 11.1 Tujuan

Kontrak menjadi dasar hubungan perdagangan dan ketentuan transaksi.

## 11.2 Elemen Kontrak

Minimal sesuai kebutuhan bisnis:

- Nomor kontrak.
- Identitas para pihak.
- Model usaha.
- PKS atau mitra terkait.
- Periode berlaku.
- Ketentuan harga.
- Ketentuan mutu.
- Kuota.
- Hak dan kewajiban.
- Ketentuan pembayaran.
- Ketentuan sengketa.
- Status kontrak.

Kelengkapan hukum aktual harus mengikuti ketentuan peraturan dan dokumen kerja sama yang sah.

## 11.3 Aturan Kontrak

**BR-CON-001**

Kontrak harus mempunyai nomor unik.

**BR-CON-002**

Kontrak harus memiliki periode berlaku.

**BR-CON-003**

Kontrak harus disetujui sebelum digunakan untuk transaksi sesuai SOP.

**BR-CON-004**

Pengiriman tidak boleh dikaitkan dengan kontrak yang telah berakhir tanpa dasar perpanjangan atau pengecualian yang sah.

**BR-CON-005**

Ketentuan harga yang digunakan harus sesuai kategori transaksi.

**BR-CON-006**

Perubahan kontrak tidak mengubah transaksi historis secara otomatis.

## 11.4 Harga Kontrak

Sistem dapat mendukung:

- Harga tetap.
- Harga berdasarkan referensi yang sah.
- Harga mengikuti ketentuan formula kontrak.
- Harga berdasarkan periode tertentu.

Pilihan yang digunakan harus ditetapkan secara eksplisit dalam kontrak.

Sistem tidak boleh mengambil harga publik tertinggi sebagai harga transaksi secara otomatis.

---

# 12. ATURAN KUOTA PASOKAN

## 12.1 Tujuan

Menjaga agar alokasi pengiriman tidak melampaui kuota yang disepakati.

## 12.2 Komponen Kuota

- Kuota total.
- Reservasi aktif.
- Kuota telah dikonsumsi.
- Kuota tersedia.

## 12.3 Rumus

**Kuota Tersedia = Kuota Total − Reservasi Aktif − Kuota Terkonsumsi**

Rumus ini berlaku jika reservasi dan kuota terkonsumsi tidak saling dihitung ganda.

## 12.4 Contoh

Kuota kontrak: 100.000 kg.

Sudah diterima dan dihitung sebagai penggunaan kuota: 60.000 kg.

Reservasi pengiriman belum selesai: 15.000 kg.

Kuota tersedia = 100.000 − 60.000 − 15.000 = **25.000 kg**.

Jika petugas mencoba menerbitkan e-DO sebesar 30.000 kg, sistem harus menolak atau meminta penyesuaian yang sah.

## 12.5 Aturan Kuota

**BR-QTA-001**

Pengiriman harus menggunakan periode kuota yang sesuai.

**BR-QTA-002**

Reservasi kuota dilakukan secara atomik.

**BR-QTA-003**

Reservasi tidak boleh dihitung dua kali.

**BR-QTA-004**

Pembatalan yang sah harus melepaskan reservasi yang belum dikonsumsi.

**BR-QTA-005**

Perubahan berat final tidak otomatis mengubah kuota historis tanpa aturan kontrak.

**BR-QTA-006**

Dasar kuota, apakah berat asal atau berat diterima PKS, harus ditentukan melalui kontrak.

## 12.6 Concurrency

Jika dua petugas mencoba menggunakan sisa kuota yang sama:

- Sistem memeriksa ketersediaan secara transaksional.
- Hanya alokasi yang memenuhi constraint yang berhasil.
- Request lain mendapat status konflik atau penolakan yang jelas.

---

# 13. ATURAN PEMILIHAN PKS TUJUAN

## 13.1 Tujuan

Mendukung penentuan tujuan pengiriman berdasarkan informasi bisnis yang valid.

## 13.2 Kriteria Pemilihan

- Status PKS.
- Kontrak aktif.
- Kuota tersedia.
- Kategori TBS.
- Ketentuan mutu.
- Harga yang sah untuk transaksi.
- Lokasi.
- Biaya pengangkutan jika tersedia.
- Kemampuan penerimaan PKS jika informasinya tersedia.

## 13.3 Aturan

**BR-DST-001**

PKS tujuan harus mempunyai status yang memperbolehkan transaksi.

**BR-DST-002**

Kontrak dan kuota harus memenuhi persyaratan.

**BR-DST-003**

Sistem tidak boleh memilih PKS hanya berdasarkan harga tertinggi.

**BR-DST-004**

Keputusan akhir berada pada petugas berwenang.

**BR-DST-005**

Alasan pemilihan dapat dicatat untuk kebutuhan evaluasi dan audit.

## 13.4 Evaluasi Ekonomi

Jika biaya yang diperlukan tersedia, sistem dapat menampilkan estimasi:

**Kontribusi Kotor Pengiriman = Estimasi Nilai Penjualan − Estimasi Nilai Pembelian − Estimasi Biaya Langsung**

Nilai ini merupakan estimasi operasional.

Jika Perumda bertindak sebagai agen, metrik yang digunakan harus mengikuti model komisi dan tidak boleh memakai rumus margin pedagang utama secara otomatis.

Fitur rekomendasi ekonomi otomatis bukan persyaratan wajib MVP.

---

# 14. ATURAN SURAT JALAN ELEKTRONIK (e-DO)

## 14.1 Prasyarat

e-DO dapat diterbitkan jika:

- Muatan tersedia.
- Penerimaan telah divalidasi.
- Timbangan lengkap.
- PKS tujuan valid.
- Kontrak sesuai.
- Kuota tersedia.
- Kendaraan dan sopir terdata sesuai kebutuhan.
- Pengguna memiliki izin.

## 14.2 Aturan Penerbitan

**BR-DO-001**

Setiap e-DO memiliki nomor unik.

**BR-DO-002**

Satu e-DO dapat mengandung beberapa transaksi penerimaan.

**BR-DO-003**

Satu penerimaan tidak boleh berada pada dua pengiriman aktif.

**BR-DO-004**

Penerbitan e-DO dan reservasi kuota harus konsisten secara atomik.

**BR-DO-005**

Penerbitan harus tercatat dalam audit.

**BR-DO-006**

e-DO terbit memiliki referensi verifikasi.

## 14.3 Konsolidasi Multi-Petani

Contoh:

| Petani          |          Berat Asal |
| --------------- | ------------------: |
| Petani A        |            3.000 kg |
| Petani B        |            2.000 kg |
| Petani C        |            5.000 kg |
| **Total** | **10.000 kg** |

Sistem membuat satu e-DO untuk tiga transaksi penerimaan.

Setiap transaksi asal tetap tersimpan.

Penggabungan muatan tidak boleh menghilangkan asal-usul panen.

## 14.4 QR Code

QR Code digunakan sebagai pengenal dokumen.

QR Code tidak otomatis memberi akses ke data rahasia.

Petugas tetap harus terautentikasi dan berwenang untuk membuka rincian internal.

## 14.5 Pembatalan e-DO

Pembatalan dapat diproses jika kondisi dan SOP mengizinkan.

Jika belum diberangkatkan, reservasi dapat dilepaskan.

Jika sudah diberangkatkan atau diterima PKS, proses pembatalan memerlukan penanganan khusus.

Sistem tidak boleh menghapus pengiriman yang sudah memiliki bukti kejadian fisik.

---

# 15. ATURAN STATUS PENGIRIMAN

## 15.1 Status Normal

| Status     | Makna                                 |
| ---------- | ------------------------------------- |
| DRAFT      | Dokumen disiapkan                     |
| READY      | e-DO telah diterbitkan                |
| IN_TRANSIT | Pengiriman dalam perjalanan           |
| ARRIVED    | Truk tiba di PKS                      |
| RECEIVED   | Penerimaan pabrik dikonfirmasi        |
| COMPLETED  | Proses operasional pengiriman selesai |
| CANCELLED  | Pengiriman dibatalkan secara sah      |

## 15.2 Transisi Normal

DRAFT → READY → IN_TRANSIT → ARRIVED → RECEIVED → COMPLETED.

## 15.3 Aturan Transisi

**BR-SHP-001**

Perubahan status hanya melalui aksi yang berwenang.

**BR-SHP-002**

Status tidak boleh dilompati tanpa prosedur pengecualian.

**BR-SHP-003**

Timestamp perubahan status harus dicatat.

**BR-SHP-004**

Status selesai tidak otomatis berarti pembayaran selesai.

**BR-SHP-005**

Setiap kejadian tidak normal harus mempunyai alasan atau catatan.

## 15.4 Kejadian Tidak Normal

Contoh:

- Truk mengalami kendala.
- Kendaraan berubah.
- PKS tidak dapat menerima muatan.
- Muatan ditolak.
- Perbedaan identitas kendaraan.
- Kerusakan atau kehilangan muatan.
- Pengiriman dialihkan ke PKS lain.

Untuk MVP, kejadian tersebut dicatat sebagai pengecualian operasional dan dapat menyebabkan pengiriman ditahan untuk pemeriksaan.

Status terminal tambahan seperti RETURNED atau REJECTED dapat ditambahkan jika telah disahkan pada AFD dan DBD.

---

# 16. ATURAN TIKET TIMBANG PKS

## 16.1 Fungsi

Tiket timbang merupakan catatan hasil penerimaan dan penimbangan PKS yang dijadikan dasar pemeriksaan transaksi.

## 16.2 Komponen Wajib

- PKS.
- Nomor tiket.
- Nomor atau referensi e-DO.
- Tanggal timbang.
- Berat bruto.
- Berat tara.
- Berat netto.
- Data grading.
- Identitas petugas.
- Bukti dokumen jika diwajibkan.

## 16.3 Aturan

**BR-MILL-001**

Tiket harus terkait dengan e-DO yang sah.

**BR-MILL-002**

PKS penerima harus sesuai dengan tujuan yang telah disahkan atau perubahan resmi.

**BR-MILL-003**

Nomor tiket tidak boleh duplikat dalam cakupan penomoran yang relevan.

**BR-MILL-004**

Tiket harus divalidasi sebelum menjadi dasar rekonsiliasi final.

**BR-MILL-005**

Tiket yang dikoreksi menggunakan versi baru.

**BR-MILL-006**

Versi lama tidak dihapus.

## 16.4 Jumlah Tiket

Baseline MVP menggunakan satu tiket timbang final aktif untuk satu e-DO.

Apabila praktik lapangan menggunakan beberapa tiket, beberapa kali penimbangan, atau pembagian muatan, rancangan ini harus disesuaikan berdasarkan observasi.

## 16.5 Ketidaksesuaian Tiket

Jika terdapat ketidaksesuaian:

- Sistem menahan proses finalisasi yang bergantung pada tiket.
- Petugas memeriksa referensi.
- Koreksi dilakukan melalui prosedur yang sah.
- Riwayat tetap tersimpan.

---

# 17. ATURAN REKONSILIASI TIMBANGAN

## 17.1 Tujuan

Rekonsiliasi dilakukan untuk membandingkan hasil timbang asal dengan hasil timbang PKS berdasarkan referensi dan definisi berat yang setara.

## 17.2 Prasyarat

- e-DO sah.
- Tiket PKS tersedia.
- Tiket sudah diverifikasi.
- Berat asal tersedia.
- Berat pabrik tersedia.
- Toleransi dan versi aturan tersedia.
- Tidak ada proses rekonsiliasi current yang bertentangan.

## 17.3 Dasar Pembanding

Sistem harus menentukan secara eksplisit berat yang digunakan untuk perbandingan.

Contoh:

- Total berat netto asal sebelum potongan grading.
- Berat netto PKS sebelum potongan grading.

Jika kedua nilai menggunakan dasar berbeda, hasil tidak boleh langsung dibandingkan sebagai selisih fisik.

## 17.4 Rumus

**Selisih Berat = Berat Asal − Berat PKS**

**Persentase Selisih = (Selisih Berat / Berat Asal) × 100%**

Syarat:

- Berat Asal > 0.
- Data valid.
- Satuan sama.
- Definisi berat setara.

## 17.5 Contoh Matched

Data simulasi:

- Berat asal: 10.000 kg.
- Berat PKS: 9.900 kg.

Selisih:

10.000 − 9.900 = 100 kg.

Persentase:

(100 / 10.000) × 100% = **1%**.

Jika toleransi contoh adalah 1,5%, transaksi dapat berstatus MATCHED.

## 17.6 Contoh Dispute

Data simulasi:

- Berat asal: 10.000 kg.
- Berat PKS: 9.600 kg.

Selisih:

400 kg.

Persentase:

(400 / 10.000) × 100% = **4%**.

Jika toleransi contoh adalah 1,5%, transaksi berstatus DISPUTE_HOLD.

## 17.7 Toleransi

**BR-REC-001**

Toleransi harus berasal dari aturan yang disahkan.

**BR-REC-002**

Nilai toleransi harus dapat dikonfigurasi dan mempunyai riwayat versi.

**BR-REC-003**

Nilai 1,5% digunakan sebagai contoh rancangan penelitian dan belum dinyatakan sebagai batas resmi Perumda.

**BR-REC-004**

Perubahan toleransi tidak boleh mengubah keputusan historis.

## 17.8 Status Rekonsiliasi

- WAITING_TICKET.
- READY.
- MATCHED.
- DISPUTE_HOLD.
- UNDER_REVIEW.
- RESOLVED.
- CANCELLED.

## 17.9 Aturan Hasil

**BR-REC-005**

MATCHED berarti data memenuhi ketentuan pencocokan yang diterapkan.

**BR-REC-006**

MATCHED tidak otomatis berarti faktur disahkan.

**BR-REC-007**

MATCHED tidak otomatis berarti pembayaran selesai.

**BR-REC-008**

Selisih di luar toleransi memerlukan pemeriksaan.

**BR-REC-009**

Selisih negatif juga harus diperiksa atau diklasifikasikan berdasarkan aturan anomali.

**BR-REC-010**

Keputusan final harus dapat ditelusuri ke sumber data dan versi aturan.

## 17.10 Rekonsiliasi Ulang

Jika tiket atau berat asal yang disahkan berubah:

- Sistem memeriksa dampak.
- Rekonsiliasi lama tetap tersimpan.
- Rekonsiliasi versi baru dibuat jika diperlukan.
- Faktur dan pembayaran terkait harus diperiksa.
- Sistem tidak mengubah hasil pembayaran historis secara diam-diam.

---

# 18. ATURAN DISPUTE DAN PENYELESAIAN SENGKETA

## 18.1 Definisi

Dispute merupakan kondisi ketika terdapat perbedaan atau ketidaksesuaian yang memerlukan pemeriksaan sebelum transaksi diselesaikan.

## 18.2 Pemicu

- Selisih melebihi toleransi.
- Berat PKS lebih tinggi dari berat asal dan membutuhkan pemeriksaan.
- Tiket tidak sesuai e-DO.
- Hasil grading diperselisihkan.
- Dokumen tidak lengkap.
- Perubahan timbang setelah pengiriman.
- Ketidaksesuaian identitas muatan atau kendaraan.

## 18.3 Alur

1. Sistem mendeteksi anomali.
2. Transaksi diberi status DISPUTE_HOLD.
3. Petugas membuka pemeriksaan.
4. Dokumen dibandingkan.
5. Klarifikasi dicatat.
6. Bukti dilampirkan jika diperlukan.
7. Keputusan diajukan.
8. Pejabat berwenang memeriksa.
9. Keputusan disahkan atau dikembalikan.
10. Hasil final dicatat.
11. Transaksi dapat dilanjutkan jika memenuhi syarat.

## 18.4 Pilihan Penyelesaian

- Data awal dinyatakan benar.
- Hasil tiket PKS diperbaiki melalui prosedur.
- Data asal diperbaiki melalui prosedur.
- Berat penyelesaian disepakati.
- Potongan yang sah disetujui.
- Transaksi tetap ditahan.
- Transaksi diselesaikan melalui mekanisme khusus sesuai perjanjian.

## 18.5 Aturan Keputusan

**BR-DSP-001**

Tidak boleh ada keputusan sengketa tanpa identitas petugas.

**BR-DSP-002**

Keputusan harus memiliki alasan.

**BR-DSP-003**

Perubahan angka harus mempertahankan nilai sebelumnya.

**BR-DSP-004**

Petugas yang tidak berwenang tidak boleh menyelesaikan sengketa.

**BR-DSP-005**

Sengketa yang belum selesai tidak dapat langsung diproses sebagai pembayaran final.

**BR-DSP-006**

Sistem tidak menyimpulkan pihak yang bersalah hanya berdasarkan selisih berat.

## 18.6 SLA Penyelesaian

Sistem dapat mencatat durasi sengketa dan memberikan peringatan jika terlalu lama.

Batas waktu pemeriksaan final harus mengikuti SOP yang disahkan.

Tidak ditetapkan angka SLA resmi dalam dokumen ini.

---

# 19. ATURAN PERHITUNGAN NILAI TRANSAKSI

## 19.1 Prinsip

Nilai transaksi dihitung berdasarkan ketentuan yang sah.

Sistem harus membedakan:

- Berat fisik.
- Berat setelah grading.
- Berat dasar pembayaran.
- Harga transaksi.
- Potongan nilai.
- Biaya.
- Nilai akhir.

## 19.2 Rumus Dasar

**Nilai Bruto = Berat Dasar Pembayaran × Harga Transaksi**

**Nilai Akhir = Nilai Bruto − Potongan Nilai yang Sah ± Penyesuaian yang Disahkan**

Biaya yang menjadi bagian harga pokok atau beban operasional tidak otomatis dianggap potongan pembayaran kepada pemasok.

Perlakuannya mengikuti model usaha dan kontrak.

## 19.3 Contoh Nilai Penjualan

Data simulasi:

- Berat diterima dan disetujui: 9.900 kg.
- Harga transaksi: Rp2.850/kg.
- Tidak ada potongan tambahan dalam contoh.

Nilai:

9.900 × 2.850 = **Rp28.215.000**.

Angka ini merupakan contoh nilai penjualan bruto yang dihitung dari berat dan harga tersebut.

Nilai tersebut bukan otomatis laba Perumda dan bukan otomatis pembayaran yang diterima petani.

## 19.4 Contoh Potongan Grading

Data simulasi alternatif:

- Berat netto PKS: 9.900 kg.
- Potongan mutu yang disahkan: 2% berbasis berat netto.
- Harga: Rp2.850/kg.

Potongan berat:

9.900 × 2% = 198 kg.

Berat dasar pembayaran:

9.900 − 198 = 9.702 kg.

Nilai bruto setelah dasar berat disesuaikan:

9.702 × 2.850 = **Rp27.650.700**.

Potongan 2% tersebut hanya boleh diterapkan apabila mempunyai dasar yang sah.

Jika potongan sudah tercermin dalam berat dasar pembayaran, sistem tidak boleh kembali mengurangkan nilai potongan yang sama sebagai potongan uang.

## 19.5 Aturan Pembulatan

Perhitungan menggunakan Decimal.

Pembulatan dilakukan pada tahap dan satuan yang telah ditetapkan secara konsisten.

Metode yang dipilih harus didokumentasikan dan diuji.

## 19.6 Harga Historis

Setiap transaksi harus menyimpan atau mereferensikan snapshot harga dan aturan yang digunakan.

Harga yang berubah pada hari berikutnya tidak mengubah perhitungan historis.

---

# 20. ATURAN ALOKASI HASIL MULTI-PETANI

## 20.1 Masalah Bisnis

Satu kendaraan dapat membawa TBS dari beberapa petani.

Hasil timbang PKS umumnya dicatat pada tingkat pengiriman atau tiket.

Sistem harus menjaga agar hasil pengiriman tetap dapat ditelusuri ke transaksi asal.

## 20.2 Dasar Alokasi

Metode alokasi dapat mempertimbangkan:

- Berat asal per petani.
- Berat hasil grading per petani.
- Ketentuan pembagian selisih.
- Harga petani.
- Potongan biaya yang disepakati.
- Kesepakatan koperasi dan Perumda.

## 20.3 Metode Proporsional — Hanya Contoh

Data simulasi:

| Petani          |          Berat Asal |       Proporsi |
| --------------- | ------------------: | -------------: |
| A               |            3.000 kg |            30% |
| B               |            2.000 kg |            20% |
| C               |            5.000 kg |            50% |
| **Total** | **10.000 kg** | **100%** |

Berat diterima PKS:

9.900 kg.

Jika dan hanya jika metode proporsional telah disahkan, alokasi menjadi:

| Petani          |       Proporsi |      Berat Alokasi |
| --------------- | -------------: | -----------------: |
| A               |            30% |           2.970 kg |
| B               |            20% |           1.980 kg |
| C               |            50% |           4.950 kg |
| **Total** | **100%** | **9.900 kg** |

## 20.4 Perhitungan Ilustratif

Pada harga yang sama Rp2.850/kg:

| Petani          |      Berat Alokasi |       Nilai Ilustratif |
| --------------- | -----------------: | ---------------------: |
| A               |           2.970 kg |            Rp8.464.500 |
| B               |           1.980 kg |            Rp5.643.000 |
| C               |           4.950 kg |           Rp14.107.500 |
| **Total** | **9.900 kg** | **Rp28.215.000** |

**Penting:** Tabel tersebut hanya menunjukkan distribusi matematis nilai penjualan pada tingkat pengiriman.

Tabel tersebut belum menetapkan jumlah yang harus dibayarkan kepada masing-masing petani karena harga beli, biaya, potongan yang sah, dan model hubungan niaganya mungkin berbeda.

## 20.5 Aturan Alokasi

**BR-ALC-001**

Setiap alokasi harus mempunyai dasar perhitungan.

**BR-ALC-002**

Jumlah alokasi berat harus dapat direkonsiliasi dengan berat total yang disahkan.

**BR-ALC-003**

Jumlah nilai alokasi harus sesuai dengan dasar nilai yang dibagikan, setelah penanganan pembulatan.

**BR-ALC-004**

Tidak boleh terdapat penerimaan yang dibagikan dua kali dalam satu penyelesaian.

**BR-ALC-005**

Metode alokasi harus disahkan sebelum digunakan untuk pembayaran final.

**BR-ALC-006**

Revisi alokasi harus mempertahankan riwayat.

## 20.6 Penanganan Selisih Pembulatan

Jika total alokasi berbeda akibat pembulatan:

- Sistem menghitung selisih.
- Sistem menerapkan metode pembulatan yang disahkan.
- Selisih tidak boleh hilang.
- Hasil akhir harus tetap konsisten dengan nilai total.

## 20.7 Status Kebijakan

**Metode pembagian hasil multi-petani: PERLU VALIDASI SOP.**

Sistem boleh mensimulasikan metode proporsional untuk pengujian, tetapi tidak boleh menggunakannya sebagai keputusan pembayaran nyata sebelum disahkan.

---

# 21. ATURAN PENAGIHAN DAN PIUTANG

## 21.1 Konsep

Penagihan harus mencerminkan hubungan bisnis yang sah.

Jika Perumda bertindak sebagai pedagang utama, penjualan TBS kepada PKS dapat menimbulkan piutang kepada PKS.

Jika Perumda bertindak sebagai agen, pencatatan dapat lebih menekankan tagihan jasa atau komisi sesuai kontrak.

## 21.2 Faktur

Faktur harus mempunyai:

- Nomor unik.
- Pihak penerbit.
- Pihak tertagih.
- Referensi transaksi.
- Periode.
- Rincian nilai.
- Status.
- Tanggal penerbitan.
- Persetujuan jika diperlukan.

## 21.3 Aturan

**BR-INV-001**

Faktur hanya boleh diterbitkan berdasarkan transaksi yang memenuhi persyaratan.

**BR-INV-002**

Nilai faktur harus dapat ditelusuri ke perhitungan dan dokumen pendukung.

**BR-INV-003**

Faktur yang sudah diterbitkan tidak boleh diubah langsung tanpa mekanisme koreksi.

**BR-INV-004**

Faktur tidak boleh diterbitkan ganda untuk dasar tagihan yang sama tanpa alasan yang sah.

**BR-INV-005**

Status faktur tidak sama dengan status penerimaan dana.

## 21.4 Status Faktur

- DRAFT.
- PENDING_VERIFICATION.
- VERIFIED.
- ISSUED.
- REJECTED.
- VOID.

Status pelunasan merupakan informasi tambahan yang dihitung berdasarkan pembayaran terverifikasi.

---

# 22. ATURAN PEMBAYARAN DAN PENCATATAN KEUANGAN

## 22.1 Pemisahan Jalur Pembayaran

Sistem harus memisahkan:

**Jalur A — Penerimaan Dana dari PKS**

Contoh: PKS membayar tagihan penjualan kepada Perumda.

**Jalur B — Pengeluaran Dana kepada Koperasi/Pemasok**

Contoh: Perumda membayar kewajiban pembelian TBS.

**Jalur C — Status Pembayaran Petani**

Hanya ditampilkan sebagai pembayaran yang benar-benar diterima petani apabila terdapat dasar dan bukti yang sah.

Jalur pembayaran yang benar akan mengikuti model usaha Perumda.

## 22.2 Persetujuan Pembayaran

**BR-PAY-001**

Permintaan pembayaran harus memiliki dasar transaksi yang valid.

**BR-PAY-002**

Nominal harus diperiksa.

**BR-PAY-003**

Persetujuan mengikuti matriks kewenangan.

**BR-PAY-004**

Pembayaran tidak boleh disetujui apabila dokumen yang diwajibkan belum lengkap.

**BR-PAY-005**

Transaksi Dispute/Hold tidak boleh diproses sebagai pembayaran final sebelum penyelesaian yang sah.

## 22.3 Pencatatan Pembayaran

**BR-PAY-006**

Pembayaran harus memiliki referensi unik.

**BR-PAY-007**

Nilai pembayaran harus positif.

**BR-PAY-008**

Pembayaran harus mempunyai pihak pembayar dan penerima yang jelas.

**BR-PAY-009**

Bukti pembayaran diperiksa sesuai ketentuan.

**BR-PAY-010**

Status PAID tidak boleh diberikan hanya berdasarkan klik tombol Setujui.

**BR-PAY-011**

Tidak diperbolehkan pencatatan ganda atas pembayaran yang sama.

## 22.4 Status Pembayaran Keluar

Alur yang disarankan:

PENDING_APPROVAL → APPROVED → AWAITING_PAYMENT → PENDING_VERIFICATION → PAID.

Jalur penolakan:

PENDING_APPROVAL → REJECTED.

Status PAID ditentukan setelah bukti pembayaran dinyatakan sah.

Pada tingkat database, catatan pembayaran dapat memiliki status VERIFIED, sedangkan kewajiban/faktur dinyatakan PAID apabila jumlah pembayaran terverifikasi telah memenuhi ketentuan pelunasan.

## 22.5 Pembayaran Parsial

Jika pembayaran sebagian diizinkan oleh kontrak:

- Sistem mencatat setiap pembayaran.
- Sistem menghitung saldo tersisa.
- Sistem mencegah pelunasan berlebih.
- Status menunjukkan belum lunas atau lunas.

Namun, **pembayaran parsial belum termasuk baseline wajib MVP** sampai kebutuhan dikonfirmasi.

Jika belum didukung, sistem harus menolak pembayaran sebagian secara eksplisit.

## 22.6 Koreksi Pembayaran

Koreksi tidak dilakukan dengan menghapus catatan pembayaran.

Gunakan mekanisme reversal atau adjustment yang mempunyai:

- Referensi pembayaran awal.
- Alasan.
- Pihak yang mengajukan.
- Persetujuan.
- Waktu.
- Nilai koreksi.

## 22.7 Status Petani

Petani hanya melihat status pembayaran pribadinya.

Sistem tidak boleh menyatakan "Dana Telah Diterima" jika hanya terdapat bukti bahwa PKS sudah membayar Perumda.

---

# 23. ATURAN PERHITUNGAN MARGIN

## 23.1 Prinsip

Margin harus dihitung sesuai model usaha.

## 23.2 Model Pedagang Utama

Jika Perumda menjadi pihak yang membeli dan menjual TBS:

**Kontribusi Kotor = Nilai Penjualan − Nilai Pembelian − Biaya Langsung yang Diakui**

Contoh biaya langsung yang dapat relevan:

- Biaya angkut.
- Biaya bongkar muat.
- Biaya transaksi langsung lain yang sah.

Rumus ini bukan otomatis laba bersih perusahaan.

## 23.3 Model Agen

Jika Perumda menjadi perantara:

**Pendapatan Jasa = Komisi atau Imbalan yang Sah Berdasarkan Kontrak**

Margin atau kontribusi jasa dihitung berdasarkan pendapatan jasa dan biaya relevan.

Sistem tidak boleh mencatat seluruh nilai penjualan TBS sebagai pendapatan Perumda jika Perumda bukan pihak utama dalam transaksi tersebut.

## 23.4 Aturan Dashboard Keuangan

**BR-MRG-001**

Setiap metrik harus memiliki definisi.

**BR-MRG-002**

Nilai penjualan berbeda dari penerimaan kas.

**BR-MRG-003**

Piutang berbeda dari dana yang sudah diterima.

**BR-MRG-004**

Persetujuan pembayaran berbeda dari dana yang sudah dibayarkan.

**BR-MRG-005**

Margin kotor tidak boleh diberi label laba bersih.

**BR-MRG-006**

Data belum lengkap harus diberi penanda.

---

# 24. ATURAN DASHBOARD DAN LAPORAN

## 24.1 Dashboard Operasional

Menampilkan:

- Tonase penerimaan.
- Tonase pengiriman.
- Tonase diterima PKS.
- Jumlah e-DO.
- Transaksi menunggu tiket.
- Transaksi Matched.
- Transaksi Dispute.
- Status kontrak dan kuota.

## 24.2 Dashboard Direksi

Menampilkan:

- Kinerja pasokan.
- Volume transaksi.
- Harga PKS.
- Kinerja mitra.
- Status rekonsiliasi.
- Piutang.
- Kewajiban pembayaran.
- Pendapatan/margin sesuai model usaha.

## 24.3 Aturan Agregasi

**BR-RPT-001**

Transaksi dibatalkan tidak dihitung sebagai transaksi berhasil.

**BR-RPT-002**

Transaksi yang belum final harus dibedakan dari transaksi selesai.

**BR-RPT-003**

Filter waktu harus menggunakan definisi tanggal yang jelas.

**BR-RPT-004**

Dashboard harus menunjukkan waktu pembaruan.

**BR-RPT-005**

Setiap angka agregat harus dapat ditelusuri ke transaksi pembentuknya sesuai hak akses.

**BR-RPT-006**

Data simulasi tidak boleh ditampilkan sebagai pencapaian bisnis nyata.

## 24.4 Rekap Bulanan

Laporan dapat mencakup:

- Total tonase.
- Koperasi pemasok.
- PKS tujuan.
- Perbandingan harga.
- Rata-rata selisih timbang.
- Jumlah sengketa.
- Durasi rekonsiliasi.
- Nilai tagihan.
- Pembayaran terverifikasi.
- Kinerja kontrak.

---

# 25. ATURAN NOTIFIKASI

## 25.1 Jenis Notifikasi

Sistem dapat memberikan notifikasi untuk:

- Harga menunggu verifikasi.
- Harga ditolak.
- Kontrak mendekati berakhir.
- Kuota hampir habis.
- Pengiriman tiba.
- Tiket siap direkonsiliasi.
- Dispute baru.
- Faktur menunggu pemeriksaan.
- Pembayaran menunggu persetujuan.

## 25.2 Aturan

**BR-NTF-001**

Notifikasi harus sesuai hak akses.

**BR-NTF-002**

Notifikasi harus memiliki referensi kejadian.

**BR-NTF-003**

Kegagalan pengiriman notifikasi tidak boleh otomatis membatalkan transaksi yang sudah sah.

**BR-NTF-004**

Notifikasi tidak boleh mengungkap data sensitif secara berlebihan.

**BR-NTF-005**

Notifikasi berulang perlu dibatasi.

Notifikasi WhatsApp, SMS, dan email eksternal merupakan pengembangan opsional.

---

# 26. ATURAN PERUBAHAN STATUS

## 26.1 Prinsip Umum

Setiap perubahan status harus memenuhi:

1. Status awal valid.
2. Transisi diizinkan.
3. Pengguna berwenang.
4. Persyaratan data terpenuhi.
5. Tidak ada konflik transaksi.
6. Perubahan tersimpan.
7. Audit tercatat jika relevan.

## 26.2 Transisi yang Tidak Diperbolehkan

Contoh:

- Draft harga langsung menjadi Published tanpa verifikasi.
- Penerimaan Draft langsung digunakan untuk e-DO final.
- e-DO Cancelled langsung menjadi Completed.
- Tiket belum diverifikasi langsung digunakan untuk pembayaran.
- Dispute/Hold langsung menjadi Paid tanpa penyelesaian.
- Faktur ditolak langsung menjadi Paid.
- Akun nonaktif mengesahkan transaksi.

## 26.3 Koreksi Status

Koreksi harus menggunakan workflow yang telah ditetapkan.

Perubahan status tidak boleh dilakukan melalui edit database manual oleh petugas operasional.

---

# 27. ATURAN TRANSAKSI GANDA DAN IDEMPOTENCY

## 27.1 Tujuan

Mencegah duplikasi akibat klik berulang, koneksi lambat, atau request yang dikirim ulang.

## 27.2 Operasi Kritis

- Pembuatan penerimaan TBS.
- Penerbitan e-DO.
- Reservasi kuota.
- Pencatatan tiket PKS.
- Rekonsiliasi.
- Persetujuan pembayaran.
- Pencatatan pembayaran.

## 27.3 Aturan

**BR-IDM-001**

Operasi kritis harus mempunyai cara mendeteksi pengulangan permintaan.

**BR-IDM-002**

Request identik dengan idempotency key yang sama tidak boleh membuat efek transaksi ganda.

**BR-IDM-003**

Request dengan key sama tetapi payload berbeda harus ditolak.

**BR-IDM-004**

Hasil operasi harus dapat diperiksa setelah gangguan jaringan.

**BR-IDM-005**

Kontrol tidak hanya mengandalkan tombol frontend yang dinonaktifkan.

---

# 28. ATURAN AUDIT DAN KETERLACAKAN

## 28.1 Tujuan

Setiap tindakan penting dapat ditelusuri kembali kepada pelaku dan dokumen terkait.

## 28.2 Aktivitas yang Diaudit

- Verifikasi harga.
- Publikasi harga.
- Perubahan kontrak.
- Koreksi penimbangan.
- Penerbitan e-DO.
- Pembatalan pengiriman.
- Verifikasi tiket PKS.
- Penyelesaian dispute.
- Persetujuan pembayaran.
- Verifikasi pembayaran.
- Perubahan hak akses.
- Perubahan aturan toleransi atau grading.

## 28.3 Informasi Audit

- Actor ID.
- Waktu.
- Jenis aktivitas.
- Modul.
- Referensi resource.
- Status sebelum.
- Status sesudah.
- Alasan.
- Request ID jika tersedia.

## 28.4 Aturan Privasi Audit

Audit tidak boleh menyimpan password, token, atau informasi rahasia yang tidak diperlukan.

Hak membaca audit dibatasi.

Audit operasional tidak boleh dapat dihapus secara bebas oleh pengguna biasa.

## 28.5 Monitoring Teknis

Middleware observabilitas mencatat peristiwa teknis, seperti:

- Request.
- Response code.
- Durasi.
- Error code.
- Request ID.
- Modul yang mengalami gangguan.

Monitoring teknis tidak menggantikan audit transaksi bisnis.

---

# 29. STANDAR PENANGANAN KESALAHAN BISNIS

## 29.1 Kategori

| Kode                      | Kondisi                        | Tindakan               |
| ------------------------- | ------------------------------ | ---------------------- |
| PRICE_NOT_VERIFIED        | Harga belum diverifikasi       | Tolak publikasi        |
| PRICE_PERIOD_INVALID      | Periode harga tidak sah        | Minta koreksi          |
| RECEIPT_ALREADY_ALLOCATED | Penerimaan sudah dialokasikan  | Tolak alokasi kedua    |
| INVALID_WEIGHT            | Berat tidak valid              | Tolak penyimpanan      |
| CONTRACT_EXPIRED          | Kontrak tidak berlaku          | Tolak transaksi baru   |
| QUOTA_EXCEEDED            | Kuota tidak mencukupi          | Tolak penerbitan       |
| DELIVERY_INVALID_STATE    | Status pengiriman tidak sesuai | Tolak perubahan        |
| MILL_TICKET_DUPLICATE     | Nomor tiket tidak unik         | Minta pemeriksaan      |
| RECONCILIATION_NOT_READY  | Data belum siap                | Tunda proses           |
| RECONCILIATION_DISPUTE    | Selisih perlu pemeriksaan      | Tahan penyelesaian     |
| INVOICE_NOT_VERIFIED      | Faktur belum diverifikasi      | Tolak penerbitan final |
| PAYMENT_NOT_AUTHORIZED    | Pembayaran tidak disetujui     | Tolak pemrosesan       |
| PAYMENT_DUPLICATE         | Pembayaran tercatat ganda      | Tolak request          |
| ACCESS_OUT_OF_SCOPE       | Akses di luar kewenangan       | Tolak akses            |

## 29.2 Pesan Pengguna

Pesan harus menggunakan bahasa Indonesia yang mudah dipahami.

Contoh:

"Pengiriman belum dapat diterbitkan karena sisa kuota kontrak tidak mencukupi."

Bukan:

"Database constraint violation."

## 29.3 Tindakan Lanjutan

Setiap pesan bisnis penting harus menjelaskan langkah berikutnya, jika memungkinkan.

Contoh:

- Periksa kontrak.
- Pilih muatan lain.
- Lengkapi tiket timbang.
- Ajukan pemeriksaan.
- Hubungi verifikator.
- Periksa status pembayaran terbaru.

---

# 30. MATRIKS BUSINESS RULES DAN MODUL

| Kelompok Aturan | Modul Pemilik                                  |
| --------------- | ---------------------------------------------- |
| BR-CMP          | Pricing, Contracts, Shared Policy              |
| BR-PUB          | Public Portal                                  |
| BR-MD           | Master Data                                    |
| BR-PRC          | Pricing                                        |
| BR-RCV          | TBS Receiving                                  |
| BR-WGT          | TBS Receiving                                  |
| BR-GRD          | TBS Receiving / Mill Weighing sesuai konteks   |
| BR-CON          | Contracts                                      |
| BR-QTA          | Contracts                                      |
| BR-DST          | Contracts / Logistics                          |
| BR-DO           | Logistics                                      |
| BR-SHP          | Logistics                                      |
| BR-MILL         | Mill Weighing                                  |
| BR-REC          | Reconciliation                                 |
| BR-DSP          | Reconciliation                                 |
| BR-ALC          | Reconciliation                                 |
| BR-INV          | Reconciliation — Finance Subdomain            |
| BR-PAY          | Reconciliation — Finance Subdomain            |
| BR-MRG          | Reporting dengan sumber data Finance           |
| BR-RPT          | Reporting                                      |
| BR-NTF          | Modul pemilik peristiwa / Notification Adapter |
| BR-IDM          | Shared Infrastructure                          |
| Audit Rules     | Audit                                          |

Kepemilikan aturan harus jelas agar tidak terdapat implementasi kalkulasi berbeda pada beberapa modul.

---

# 31. RANCANGAN IMPLEMENTASI DOMAIN LAYER

## 31.1 Prinsip

Setiap aturan bisnis utama harus diimplementasikan sebagai fungsi, policy, entity behavior, atau domain service yang dapat diuji.

Domain Layer tidak bergantung pada FastAPI, SQLAlchemy, atau Redis.

## 31.2 Contoh Komponen Domain

**Pricing**

- PriceValidityPolicy.
- PricePublicationPolicy.
- PriceComparabilityPolicy.

**Receiving**

- WeightCalculation.
- ReceiptValidationPolicy.
- GradingCalculationPolicy.

**Contracts**

- ContractEligibilityPolicy.
- QuotaAvailability.
- QuotaReservationPolicy.

**Logistics**

- DeliveryOrderIssuancePolicy.
- DeliveryStatusTransitionPolicy.

**Mill Weighing**

- TicketValidationPolicy.
- WeighingRevisionPolicy.

**Reconciliation**

- WeightDifferenceCalculator.
- ReconciliationTolerancePolicy.
- DisputeResolutionPolicy.
- SettlementAllocationPolicy.

**Finance**

- InvoiceEligibilityPolicy.
- PaymentApprovalPolicy.
- PaymentSettlementPolicy.

Komponen tersebut merupakan rancangan tanggung jawab, bukan kewajiban membuat class untuk setiap aturan tanpa kebutuhan yang jelas.

## 31.3 Aturan Implementasi

- Business rule diuji melalui unit test.
- Tidak ada formula uang berbasis float.
- Rule mempunyai identitas dan versi jika bersifat historis.
- Konfigurasi bisnis penting tidak di-hardcode.
- Perubahan aturan harus didokumentasikan.
- Perubahan yang memengaruhi transaksi lama harus melalui analisis dampak.

---

# 32. SOP OPERASIONAL RINGKAS

## SOP-01 — Publikasi Harga

1. Staf memperoleh sumber harga yang diizinkan.
2. Staf memasukkan informasi.
3. Sistem memvalidasi.
4. Staf mengajukan verifikasi.
5. Verifikator memeriksa.
6. Jika sah untuk dipublikasikan, harga disetujui.
7. Sistem menampilkan harga sesuai periode.
8. Riwayat dan audit disimpan.

## SOP-02 — Penerimaan TBS

1. Identifikasi petani dan kebun.
2. Catat penerimaan.
3. Lakukan penimbangan.
4. Lakukan grading.
5. Validasi dan sahkan data.
6. Simpan bukti yang diwajibkan.
7. Jadikan penerimaan tersedia untuk pengiriman.

## SOP-03 — Pengiriman

1. Pilih penerimaan.
2. Tentukan PKS tujuan.
3. Periksa kontrak dan kuota.
4. Tentukan kendaraan.
5. Buat Draft e-DO.
6. Periksa ringkasan.
7. Terbitkan e-DO.
8. Catat keberangkatan.
9. Pantau status.
10. Verifikasi kedatangan.

## SOP-04 — Tiket Timbang PKS

1. Verifikasi e-DO.
2. Cocokkan kendaraan.
3. Lakukan penimbangan.
4. Catat bruto dan tara.
5. Catat grading.
6. Lampirkan bukti.
7. Verifikasi tiket.
8. Sediakan data untuk rekonsiliasi.

## SOP-05 — Rekonsiliasi

1. Ambil berat asal.
2. Ambil berat PKS.
3. Validasi kesetaraan dasar.
4. Hitung selisih.
5. Periksa toleransi.
6. Tetapkan Matched atau Dispute/Hold.
7. Simpan hasil dan versi aturan.

## SOP-06 — Penyelesaian Dispute

1. Buka transaksi bermasalah.
2. Periksa dokumen.
3. Catat klarifikasi.
4. Ajukan keputusan.
5. Verifikator menyetujui atau mengembalikan.
6. Simpan hasil final.
7. Perbarui status.
8. Lanjutkan transaksi jika memenuhi syarat.

## SOP-07 — Penagihan

1. Pastikan dasar transaksi valid.
2. Hitung nilai.
3. Susun faktur.
4. Verifikasi.
5. Terbitkan.
6. Catat status penagihan.

## SOP-08 — Pembayaran

1. Periksa kewajiban.
2. Periksa dokumen.
3. Ajukan persetujuan.
4. Otorisasi sesuai kewenangan.
5. Lakukan pembayaran melalui prosedur yang sah.
6. Catat bukti.
7. Verifikasi bukti.
8. Perbarui status.
9. Catat audit.

---

# 33. PENGUJIAN ATURAN BISNIS

## 33.1 Tujuan

Memastikan aturan bisnis bekerja benar, termasuk pada input tidak valid dan permintaan bersamaan.

## 33.2 Matriks Uji

| Test ID | Skenario                                                  | Hasil yang Diharapkan                             |
| ------- | --------------------------------------------------------- | ------------------------------------------------- |
| BIZ-001 | Publikasi harga tanpa verifikasi                          | Ditolak                                           |
| BIZ-002 | Harga tanpa sumber                                        | Ditolak                                           |
| BIZ-003 | Harga kedaluwarsa pada halaman harga aktif                | Tidak ditampilkan sebagai harga aktif             |
| BIZ-004 | Tara melebihi bruto                                       | Ditolak                                           |
| BIZ-005 | Netto valid                                               | Hasil sesuai rumus                                |
| BIZ-006 | Potongan grading diterapkan dua kali                      | Dicegah                                           |
| BIZ-007 | Kontrak kedaluwarsa                                       | Tidak dapat digunakan untuk transaksi baru        |
| BIZ-008 | Reservasi melebihi kuota                                  | Ditolak                                           |
| BIZ-009 | Dua request reservasi bersamaan                           | Tidak melampaui kuota                             |
| BIZ-010 | Satu penerimaan masuk dua e-DO aktif                      | Ditolak                                           |
| BIZ-011 | Tiket PKS tidak sesuai e-DO                               | Ditolak atau ditahan                              |
| BIZ-012 | Tiket belum diverifikasi                                  | Tidak dapat direkonsiliasi final                  |
| BIZ-013 | Selisih dalam toleransi yang berlaku                      | MATCHED                                           |
| BIZ-014 | Selisih melampaui toleransi                               | DISPUTE_HOLD                                      |
| BIZ-015 | Berat PKS lebih besar dari berat asal                     | Ditandai untuk pemeriksaan                        |
| BIZ-016 | Dispute belum selesai                                     | Pembayaran final ditahan                          |
| BIZ-017 | Penyelesaian sengketa tanpa alasan                        | Ditolak                                           |
| BIZ-018 | Harga publik berubah setelah transaksi                    | Nilai historis tidak berubah otomatis             |
| BIZ-019 | Alokasi multi-petani tidak seimbang                       | Ditolak                                           |
| BIZ-020 | Pembayaran tanpa persetujuan                              | Ditolak                                           |
| BIZ-021 | Bukti pembayaran belum diverifikasi                       | Tidak dinyatakan PAID                             |
| BIZ-022 | Pembayaran berulang dengan key sama                       | Tidak tercatat ganda                              |
| BIZ-023 | Petani membuka transaksi petani lain                      | Ditolak                                           |
| BIZ-024 | PKS mengakses tiket PKS lain                              | Ditolak                                           |
| BIZ-025 | Transaksi dibatalkan muncul sebagai berhasil              | Tidak boleh terjadi                               |
| BIZ-026 | Perubahan timbang setelah faktur terbit                   | Memicu pemeriksaan dampak                         |
| BIZ-027 | Transfer PKS ke Perumda sudah masuk, petani belum dibayar | Status petani tidak otomatis PAID                 |
| BIZ-028 | Redis tidak tersedia                                      | Tidak menyebabkan bypass keamanan                 |
| BIZ-029 | Perubahan rule tolerance                                  | Transaksi historis tetap memakai versi sebelumnya |
| BIZ-030 | Request paralel menerbitkan e-DO dari muatan sama         | Maksimum satu alokasi aktif berhasil              |

## 33.3 Metode

Pengujian dapat menggunakan:

- Unit Testing Domain Layer.
- Application Use Case Testing.
- Integration Testing.
- Contract Testing.
- Concurrency Testing.
- End-to-End Testing.
- Black Box Testing.

## 33.4 Kriteria Keberhasilan

Semua aturan bisnis kritis harus mempunyai skenario pengujian yang memeriksa kondisi normal dan kondisi gagal.

Nilai aktual pengujian baru dilaporkan setelah implementasi selesai.

---

# 34. INDIKATOR KINERJA BISNIS

## 34.1 Tujuan Evaluasi

Sistem dikembangkan untuk mendukung tata kelola yang lebih terstruktur dan efisien.

Keberhasilan tidak cukup diukur dari jumlah fitur yang tersedia.

## 34.2 Indikator

| Indikator                           | Definisi Pengukuran                              |
| ----------------------------------- | ------------------------------------------------ |
| Waktu pencatatan penerimaan         | Durasi membuat transaksi penerimaan              |
| Waktu penerbitan e-DO               | Durasi dari data siap hingga dokumen terbit      |
| Waktu rekonsiliasi                  | Durasi dari data siap hingga hasil rekonsiliasi  |
| Persentase kesalahan input          | Jumlah kesalahan terhadap skenario pengujian     |
| Kelengkapan transaksi               | Persentase data wajib yang valid                 |
| Jumlah transaksi bermasalah         | Total Dispute/Hold per periode                   |
| Durasi penyelesaian sengketa        | Waktu dari pembukaan hingga penyelesaian         |
| Keterlacakan dokumen                | Kelengkapan hubungan dokumen asal dan akhir      |
| Kecepatan pencarian informasi harga | Durasi menyelesaikan tugas pencarian             |
| Keberhasilan tugas pengguna         | Persentase tugas yang diselesaikan tanpa bantuan |

## 34.3 Pengukuran Efisiensi

Rumus:

Efisiensi Waktu (%) = ((Waktu Lama − Waktu Baru) / Waktu Lama) × 100%.

Pengukuran harus menggunakan skenario setara.

Tidak boleh menggunakan angka asumsi sebagai hasil penelitian lapangan.

---

# 35. KEPUTUSAN BISNIS YANG WAJIB DIVALIDASI

Sebelum implementasi transaksi nyata, keputusan berikut perlu memperoleh persetujuan resmi.

| Kode        | Keputusan                                                 | Status                        |
| ----------- | --------------------------------------------------------- | ----------------------------- |
| BSD-DEC-001 | Perumda bertindak sebagai principal, agent, atau keduanya | Belum final                   |
| BSD-DEC-002 | Hubungan hukum dan kontrak dengan koperasi serta PKS      | Belum final                   |
| BSD-DEC-003 | Penerapan harga acuan pada kategori mitra yang relevan    | Perlu pemeriksaan regulasi    |
| BSD-DEC-004 | Kategori harga PKS yang dapat dipublikasikan              | Belum final                   |
| BSD-DEC-005 | Penanggung jawab verifikasi harga                         | Belum final                   |
| BSD-DEC-006 | Formula grading dan potongan                              | Belum final                   |
| BSD-DEC-007 | Ambang toleransi timbang                                  | Belum final; 1,5% contoh      |
| BSD-DEC-008 | Dasar berat untuk kuota                                   | Belum final                   |
| BSD-DEC-009 | Pihak penerbit dan pengesah e-DO                          | Belum final                   |
| BSD-DEC-010 | Mekanisme muatan ditolak PKS                              | Belum final                   |
| BSD-DEC-011 | Jumlah tiket final per e-DO                               | Baseline satu, perlu validasi |
| BSD-DEC-012 | Pejabat penyelesai dispute                                | Belum final                   |
| BSD-DEC-013 | Metode alokasi hasil multi-petani                         | Belum final                   |
| BSD-DEC-014 | Harga beli dan dasar penyelesaian kepada pemasok          | Belum final                   |
| BSD-DEC-015 | Alur faktur dan siapa pihak tertagih                      | Belum final                   |
| BSD-DEC-016 | Matriks persetujuan pembayaran                            | Belum final                   |
| BSD-DEC-017 | Pembayaran parsial                                        | Belum termasuk baseline       |
| BSD-DEC-018 | Bukti yang diperlukan untuk status pembayaran petani      | Belum final                   |
| BSD-DEC-019 | SLA operasional dan penyelesaian sengketa                 | Belum final                   |
| BSD-DEC-020 | Kebijakan retensi data dan audit                          | Belum final                   |

Untuk prototipe tesis, keputusan yang belum divalidasi dapat menggunakan kebijakan simulasi yang dinyatakan secara eksplisit.

Kebijakan simulasi tidak boleh digunakan sebagai dasar transaksi nyata.

---

# 36. REKOMENDASI PENYESUAIAN DOKUMEN SEBELUMNYA

BSD ini memperjelas beberapa aspek yang perlu diselaraskan dengan dokumen sebelumnya.

## 36.1 PRD

Perlu memperjelas pilihan model bisnis Perumda sebagai principal, agent, atau kombinasi.

## 36.2 TRD

Perlu memastikan aturan perhitungan harga, berat, grading, dan pembayaran diimplementasikan sebagai domain policy yang terpisah.

## 36.3 AFD

Perlu membedakan alur pembayaran masuk dari PKS, pembayaran keluar Perumda, dan pembayaran akhir kepada petani.

Prosedur muatan ditolak atau dikembalikan perlu ditambahkan jika terbukti digunakan di lapangan.

## 36.4 DBD

Perlu memastikan kontrak menyimpan klasifikasi model usaha.

Jika satu faktur dapat terkait beberapa pengiriman atau penyelesaian, struktur relasi harus diperluas secara eksplisit.

Jika pengembalian muatan, pembayaran parsial, atau koreksi keuangan termasuk cakupan MVP, entitas serta constraint tambahan perlu dirancang.

Aturan kepatuhan harga dan versi ketentuan kontrak perlu mempunyai referensi historis.

## 36.5 IPD

Implementasi aturan keuangan dan rekonsiliasi tidak boleh dianggap final sebelum keputusan bisnis yang mengikatnya tervalidasi.

Pengembangan UI dapat dimulai menggunakan data simulasi, tetapi pengujian hasil finansial memerlukan aturan yang disahkan.

---

# 37. DEFINITION OF DONE — BUSINESS RULES

Suatu aturan bisnis dinyatakan selesai apabila:

1. Mempunyai ID yang konsisten.
2. Memiliki penanggung jawab domain.
3. Memiliki deskripsi dan tujuan jelas.
4. Memiliki input serta output.
5. Memiliki prasyarat.
6. Memiliki hasil normal.
7. Memiliki penanganan pengecualian.
8. Memiliki kewenangan pelaksana.
9. Memiliki ketentuan audit jika relevan.
10. Memiliki unit test.
11. Memiliki pengujian integrasi jika diperlukan.
12. Tidak bertentangan dengan aturan modul lain.
13. Mempunyai referensi kebijakan apabila bergantung pada SOP atau regulasi.
14. Perubahan aturan historis dikendalikan.
15. Sudah diperiksa sesuai status validasinya.

---

# 38. KESIMPULAN

Business System Document V1.0 menetapkan aturan bisnis awal untuk pengembangan Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata, Unit Agro Niaga.

Dokumen mengatur proses dari publikasi informasi harga, penerimaan petani, penimbangan, grading, kontrak, kuota, pengiriman, tiket PKS, rekonsiliasi, penyelesaian sengketa, penagihan, hingga pencatatan pembayaran.

Aturan utama yang ditekankan adalah keterlacakan sumber panen, konsistensi berat dan harga, pencegahan transaksi ganda, pengendalian kewenangan, serta pemisahan status operasional dan keuangan.

Informasi harga acuan, harga informasi PKS, dan harga transaksi harus dibedakan.

Perhitungan grading dan selisih timbang harus menggunakan dasar yang jelas agar tidak terjadi pemotongan ganda atau kesalahan nilai.

Transaksi multi-petani harus mempertahankan hubungan asal muatan dan menggunakan metode alokasi yang telah disahkan.

Keputusan pembayaran harus mengikuti model bisnis dan kewenangan yang sah.

BSD ini menjadi dasar implementasi business logic pada Domain Layer setiap modul backend, sekaligus sumber penyusunan pengujian aturan bisnis dan skenario end-to-end.

**STATUS: BSD V1.0 — BUSINESS RULES BASELINE, MENUNGGU VALIDASI KEPUTUSAN OPERASIONAL**

**DOKUMEN SELANJUTNYA: IMPLEMENTATION PLAN DOCUMENT (IPD)**

---

## REFERENSI UTAMA

### Regulasi

1. Peraturan Menteri Pertanian Nomor 13 Tahun 2024 tentang Pembelian Tandan Buah Segar Kelapa Sawit Produksi Pekebun Mitra.https://peraturan.bpk.go.id/Details/311731/permentan-no-13-tahun-2024
2. Peraturan Gubernur Riau Nomor 77 Tahun 2020 tentang Tata Cara Penetapan Harga Pembelian TBS Kelapa Sawit Produksi Pekebun di Provinsi Riau.https://peraturan.bpk.go.id/Details/189418/pergub-prov-riau-no-77-tahun-2020
3. Peraturan Gubernur Riau Nomor 5 Tahun 2021 tentang Perubahan atas Pergub Nomor 77 Tahun 2020.https://peraturan.bpk.go.id/Details/189186/pergub-prov-riau-no-5-tahun-2021
4. Dinas Perkebunan Provinsi Riau — Informasi dan Pengumuman Harga TBS.
   https://disbun.riau.go.id/

### Dokumen Internal Pengembangan

- Product Requirements Document V1.0.
- Technical Requirements Document V1.0.
- Application Flow Document V1.0.
- Database Design Document V1.0.
- Proposal Tesis Givo Vrabora Revisi Final V2.

**Akhir Dokumen — Business System Document V1.0**
