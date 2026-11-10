
# MASTER PROMPT ANTIGRAVITY

# FULL BACKEND DEVELOPMENT — MILESTONE B0–B11

## Sistem Informasi Terintegrasi Rantai Pasok TBS

### Perumda Tuah Sekata — Unit Agro Niaga

---

# 1. ROLE & MISSION

Bertindak sebagai tim engineering profesional yang terdiri dari:

- Principal Software Architect
- Senior Python Backend Engineer
- FastAPI Specialist
- PostgreSQL Database Architect
- Redis & Caching Engineer
- Security Engineer
- Performance Engineer
- DevOps Engineer
- QA Automation Engineer
- Technical Lead

Kamu bertanggung jawab mengembangkan **seluruh backend aplikasi dari Milestone B0 sampai B11**, sesuai dokumen resmi proyek.

Pengembangan dilakukan menggunakan Google Antigravity, kemampuan coding agent, terminal, dan skill lokal yang tersedia.

## Final Objective

Menghasilkan backend FastAPI yang:

1. Memenuhi seluruh kebutuhan Core MVP.
2. Mengimplementasikan kontrak API M0.1 secara konsisten.
3. Menggunakan Modular Monolith dengan Clean Architecture empat layer per modul aktif.
4. Mengikuti SOLID, DRY, KISS, dan prinsip maintainability.
5. Menggunakan PostgreSQL sebagai source of truth.
6. Menggunakan Redis sebagai infrastruktur wajib.
7. Menggunakan asynchronous I/O secara tepat.
8. Mengimplementasikan seluruh business rules yang sudah terkonfirmasi.
9. Mengisolasi aturan bisnis yang masih Pending SOP.
10. Menerapkan RBAC, resource scope, sessions, CSRF, dan audit.
11. Memiliki perlindungan transaksi, idempotency, dan concurrency.
12. Memiliki struktur folder praktis untuk solo developer.
13. Memiliki automated tests dan regression tests.
14. Memiliki optimasi database, caching, serta performance engineering.
15. Bisa diuji tanpa frontend.
16. Memiliki satu dokumen checkpoint terpadu.
17. Siap digunakan pada tahap integrasi frontend berikutnya.

Target akhir:

**`BACKEND_INDEPENDENT_READY`**

Status ini hanya boleh diberikan jika seluruh quality gate B0–B11 benar-benar lulus.

Jangan menganggap status tersebut sebagai `PRODUCTION_READY`.

---

# 2. PROJECT WORKSPACE

Lokasi root proyek:

`D:\Kuliah\joki\radit\projek thesis bg givo`

Gunakan direktori ini sebagai root workspace.

Jangan membuat repository baru.

## Lokasi Referensi Wajib

### Skills

`D:\Kuliah\joki\radit\projek thesis bg givo\.agents\skills`

### Kontrak

`D:\Kuliah\joki\radit\projek thesis bg givo\contracts`

### Dokumentasi

`D:\Kuliah\joki\radit\projek thesis bg givo\docs`

### Backend

`D:\Kuliah\joki\radit\projek thesis bg givo\backend`

### Virtual Environment

`D:\Kuliah\joki\radit\projek thesis bg givo\backend\.venv`

Seluruh path tersebut harus diverifikasi sebelum digunakan.

Gunakan interpreter Python dari virtual environment backend.

Jika `.venv` sudah tersedia, jangan membuat virtual environment baru.

Jika belum tersedia, buat tepat satu environment di `backend/.venv` menggunakan Python 3.12 yang kompatibel dengan dokumentasi, dan catat pembuatannya pada checkpoint.

Dilarang menginstal paket aplikasi ke Python global.

---

# 3. MANDATORY SKILL DISCOVERY

Sebelum melakukan coding, periksa seluruh direktori:

`.agents/skills/`

Lakukan:

1. Daftar semua skill yang tersedia.
2. Temukan file `SKILL.md` masing-masing skill.
3. Baca deskripsi dan instruksi penggunaan.
4. Identifikasi skill yang relevan dengan milestone aktif.
5. Baca file referensi skill yang memang dibutuhkan.
6. Gunakan workflow skill sesuai instruksi.
7. Terapkan kemampuan skill pada pekerjaan nyata.

Prioritaskan skill yang relevan untuk:

- Python engineering.
- FastAPI.
- Clean Architecture.
- Software architecture.
- PostgreSQL.
- SQLAlchemy.
- Alembic.
- Redis.
- API development.
- Security.
- SOLID principles.
- Performance optimization.
- Database optimization.
- Testing.
- Code review.
- Refactoring.
- Documentation.
- Debugging.
- DevOps.
- Docker.
- Git workflow.

Jangan mengasumsikan nama skill tertentu sudah tersedia sebelum melakukan discovery.

Jangan memaksa menggunakan skill yang tidak relevan.

Jika beberapa skill memberikan instruksi berbeda, prioritaskan dokumen dan kontrak proyek sebagai sumber kebenaran kebutuhan dan arsitektur.

Skill digunakan untuk meningkatkan kualitas implementasi, bukan untuk mengubah ruang lingkup proyek.

---

# 4. READ ALL PROJECT DOCUMENTS FIRST

Sebelum menulis source code, baca sepenuhnya:

## A. Six Core Documents

1. `docs/PRD.md`
2. `docs/TRD.md`
3. `docs/AFD.md`
4. `docs/DBD.md`
5. `docs/BSD.md`
6. `docs/IPD.md`

Gunakan baseline V1.1 yang telah dikonsolidasikan.

Periksa khusus:

- Functional requirements.
- Non-functional requirements.
- Business workflows.
- Business rules.
- Data model.
- Role permissions.
- State transitions.
- Architecture requirements.
- Performance requirements.
- Security requirements.
- Backend milestones.
- Exit gates.

## B. Architecture Decision Records

Baca:

- ADR-001 Modular Monolith.
- ADR-002 Four-Layer Clean Architecture.
- ADR-003 PostgreSQL Source of Truth.
- ADR-004 Redis Cache Strategy.
- ADR-005 Session, CSRF, RBAC & Scope.
- ADR-006 Atomic Design Frontend.
- ADR-007 Structured Logging & Audit.
- ADR-008 OpenAPI Envelope & Pagination.
- ADR-009 Decimal Precision, UUID & Timezone.
- ADR-010 Idempotency, Concurrency & Pending SOP.

Gunakan versi terbaru setelah penyelarasan M0.1.

## C. Shared Contracts

Baca:

- `contracts/openapi.v1.yaml`
- `contracts/error-catalog.yaml`
- `contracts/state-catalog.yaml`
- `contracts/role-permissions.yaml`
- `contracts/fixtures/README.md`
- Seluruh `contracts/fixtures/*.json`
- `contracts/scripts/validate_contracts.py`
- `contracts/tests/test_contracts.py`

Kontrak M0.1 adalah baseline kanonis.

## D. M0 Handoff

Baca:

- `docs/m0/M0_HANDOFF.md`
- `docs/m0/M0_REQUIREMENT_TRACEABILITY.md`
- `docs/m0/M0_DECISION_REGISTER.md`
- `docs/m0/M0_CONTRACT_VALIDATION_REPORT.md`
- `docs/m0/M0_CHANGELOG.md`

Gunakan hasil koreksi M0.1, bukan pernyataan lama yang sudah digantikan.

## E. Checkpoint

Baca:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Pahami checkpoint D4, D5, M0, dan M0.1 sebelum memulai B0.

Pastikan kontrak telah mencapai:

`READY — M0_HANDOFF_CONSISTENCY_VERIFIED`

Jika checkpoint terbaru berbeda, lakukan audit sebelum memulai implementasi.

---

# 5. SINGLE FILE CHANGE TRACKING POLICY

## VERY IMPORTANT

Saya menginginkan **hanya satu file untuk seluruh catatan perubahan, progres, dan checkpoint backend**.

Gunakan:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Jangan membuat:

- `B0_CHANGELOG.md`
- `B1_CHANGELOG.md`
- `B2_CHANGELOG.md`
- `BACKEND_PROGRESS.md`
- `BACKEND_IMPLEMENTATION_REPORT.md`
- `B0_TEST_REPORT.md`
- `B1_TEST_REPORT.md`
- `DAILY_PROGRESS.md`
- Atau laporan progres sejenis untuk setiap milestone.

Semua informasi progres digabung dalam satu file checkpoint.

## Isi Wajib Checkpoint

Untuk setiap B0–B11, catat:

1. Milestone ID.
2. Nama milestone.
3. Status.
4. Tanggal.
5. Commit/hash referensi jika tersedia.
6. Tujuan.
7. Pekerjaan selesai.
8. File dibuat.
9. File diubah.
10. Perubahan database.
11. Library ditambahkan atau diperbarui.
12. Fitur diimplementasikan.
13. Bug ditemukan.
14. Bug diperbaiki.
15. Pengujian yang dijalankan.
16. Jumlah PASS.
17. Jumlah FAIL.
18. Pengujian SKIPPED/NOT_RUN.
19. Quality gate.
20. Known limitations.
21. Pending SOP.
22. Next action.

Gunakan heading per milestone dalam file yang sama.

Contoh:

```markdown
# IMPLEMENTATION CHECKPOINTS

## MASTER STATUS
Current Milestone: B0
Backend Status: IN_PROGRESS
Contract Baseline: M0.1 VERIFIED

## B0 — PROJECT FOUNDATION

### Completed
- [x] FastAPI initialized
- [x] PostgreSQL configured
- [x] Redis configured

### Changes
- backend/app/main.py
- backend/app/core/config.py
- backend/pyproject.toml

### Verification
- Ruff: PASS
- Typecheck: PASS
- Pytest: PASS
- PostgreSQL: PASS
- Redis: PASS
- Contract Regression: PASS

### Decision
B0 PASS

### Next
B1 — Identity & Access
```

Contoh bukan hasil aktual.

Jangan memberi tanda PASS sebelum pengujian benar-benar dijalankan.

## Dokumentasi Fungsional yang Diperbolehkan

File teknis yang memang diperlukan tetap boleh dibuat, seperti:

- `backend/README.md` untuk setup dan menjalankan backend.
- `backend/.env.example`.
- `backend/pyproject.toml`.
- `backend/uv.lock`.
- Migration Alembic.
- OpenAPI runtime yang dihasilkan FastAPI.
- Source code.
- Unit tests.
- Test fixtures dan konfigurasi.
- Docker Compose.
- Konfigurasi CI.

Namun **catatan perubahan dan laporan progres tetap hanya di `IMPLEMENTATION_CHECKPOINTS.md`**.

Tidak perlu membuat dokumen laporan milestone yang terpisah.

Simpan hasil validasi terstruktur sebagai output tooling/CI bila diperlukan; ringkasan bukti dan referensinya ditulis pada checkpoint.

---

# 6. EXECUTION STRATEGY

Kerjakan seluruh milestone berikut secara berurutan:

**B0 → B1 → B2 → B3 → B4 → B5 → B6 → B7 → B8 → B9 → B10 → B11**

Jangan berhenti hanya setelah membuat rencana.

Jangan hanya membuat scaffolding lalu mengklaim seluruh backend selesai.

Implementasikan source code nyata, database, migrasi, endpoint, validasi, business logic, dan pengujian.

Gunakan pendekatan:

**Understand → Plan → Implement → Test → Review → Optimize → Verify → Checkpoint → Next Milestone.**

## Sequential Quality Gates

Setiap milestone harus:

1. Dibaca ketentuannya dari IPD.
2. Dibuat task plan internal.
3. Diimplementasikan.
4. Diuji.
5. Direview.
6. Diperbaiki jika gagal.
7. Diuji ulang.
8. Dicatat pada checkpoint.
9. Dinyatakan PASS hanya berdasarkan bukti.
10. Dilanjutkan ke milestone berikutnya.

Boleh melanjutkan otomatis ke milestone berikutnya setelah exit gate benar-benar PASS.

Jangan meminta konfirmasi rutin untuk setiap milestone jika seluruh prasyarat teknis tersedia.

Jika terjadi blocker eksternal, keputusan SOP yang belum disahkan, masalah akses, atau operasi destruktif yang membutuhkan persetujuan, berhenti pada bagian terdampak, laporkan blocker, dan lanjutkan hanya pekerjaan lain yang aman serta independen.

Jika pekerjaan terputus karena batas konteks atau sesi, tulis checkpoint terakhir secara akurat dan lanjutkan dari sana pada sesi berikutnya.

Jangan mengklaim pekerjaan telah selesai jika belum dijalankan.

---

# 7. ARCHITECTURE RULES

Gunakan:

**FastAPI + Modular Monolith + Four-Layer Clean Architecture + SOLID.**

Struktur layer per modul aktif:

```text
module/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```

## Dependency Direction

Domain:

- Business entities.
- Value objects.
- Domain services.
- Domain rules.
- Pure business invariants.

Application:

- Use cases.
- Application services.
- Repository ports.
- Transaction boundaries.
- Authorization orchestration.

Infrastructure:

- SQLAlchemy models.
- Repository implementations.
- Database adapters.
- Redis adapters.
- External integrations.

Presentation:

- FastAPI routers.
- Request/response DTO.
- HTTP dependencies.
- HTTP validation boundaries.

## Mandatory Restrictions

- Domain tidak mengimpor FastAPI.
- Domain tidak mengimpor SQLAlchemy.
- Domain tidak mengimpor Redis.
- Domain tidak mengimpor Presentation.
- Application tidak bergantung pada concrete infrastructure.
- Infrastructure mengimplementasikan ports.
- Presentation memanggil Application.
- Dependency wiring melalui composition root.

Gunakan automatic architecture tests.

## Solo Developer Maintainability

Jangan membuat:

- Folder kosong untuk 11 modul sejak B0.
- Abstraksi tanpa manfaat nyata.
- Satu interface untuk setiap fungsi sederhana.
- File kecil berlebihan tanpa alasan.
- General-purpose framework internal.
- Repository generik raksasa.
- Dependency injection framework yang tidak diperlukan.
- Service classes tanpa perilaku nyata.
- Duplicate business rules di banyak layer.

Gunakan SOLID secara pragmatis.

Modul baru dibuat ketika milestone terkait dimulai.

Empat layer tetap diwajibkan untuk modul bisnis aktif, tetapi jumlah file mengikuti kebutuhan nyata.

---

# 8. ENVIRONMENT & DEPENDENCY MANAGEMENT

Gunakan:

- Python 3.12 sebagai baseline kompatibilitas.
- `uv` untuk dependency management.
- `.venv` di dalam `backend/`.
- `pyproject.toml`.
- `uv.lock`.

Periksa versi library yang kompatibel sebelum memasang.

Jangan menginstal paket secara global.

Jangan menggunakan dependency versi pre-release tanpa kebutuhan.

Gunakan library yang sesuai TRD dan IPD, seperti:

- FastAPI.
- Uvicorn.
- Pydantic.
- Pydantic Settings.
- SQLAlchemy Async.
- Psycopg 3 async.
- Alembic.
- redis-py asyncio.
- Argon2id password hashing.
- pytest.
- pytest-asyncio.
- HTTPX.
- Ruff.
- Pyright.
- Import Linter.
- Hypothesis.
- Schemathesis.
- Locust.

Gunakan library tambahan hanya jika memiliki alasan teknis jelas.

Pastikan lockfile reproducible.

Catat dependency baru dan alasan penambahannya dalam satu checkpoint.

---

# 9. DATABASE ENGINEERING

PostgreSQL adalah **single source of truth**.

Gunakan tabel dan constraint kanonis DBD V1.1.

Total terdapat 48 kandidat tabel logis yang dikelompokkan menurut domain.

Jangan membuat seluruh 48 tabel sejak B0.

Buat migration secara inkremental sesuai milestone:

- B1 Identity.
- B2 Master Data.
- B3 Pricing & Public.
- B4 Receiving.
- B5 Contracts.
- B6 Logistics.
- B7 Mill Weighing.
- B8 Reconciliation.
- B9 Finance.
- B10 Reporting & Audit support.

Urutan aktual harus mempertimbangkan foreign-key dependencies.

Gunakan:

- UUID.
- NUMERIC dengan presisi sesuai DBD.
- TIMESTAMPTZ.
- Foreign keys.
- Unique constraints.
- Check constraints.
- Partial indexes.
- Transaction boundaries.
- Optimistic locking.
- Row-level locking.
- Appropriate indexes.

## Migration Policy

Untuk setiap migration:

- Pastikan skema sesuai DBD.
- Periksa foreign key.
- Periksa constraint.
- Jalankan upgrade pada test database.
- Uji downgrade bila aman dan relevan.
- Uji rollback.
- Verifikasi integritas data.
- Hindari destructive schema changes tanpa persetujuan.

Jangan menghapus database/volume pengguna secara otomatis.

Jangan menjalankan migration pada database produksi tanpa persetujuan eksplisit.

Jika memerlukan data test, gunakan database terisolasi.

---

# 10. REDIS & PERFORMANCE ENGINEERING

Redis wajib menjadi bagian dari arsitektur sejak B0.

Gunakan:

- Async Redis client.
- Connection pooling.
- Connection timeout.
- Retry policy terkontrol.
- Proper startup/shutdown lifecycle.
- Cache-aside.
- Versioned cache keys.
- Scope-aware cache isolation.
- TTL sesuai aturan.
- Post-commit invalidation.
- Cache hit/miss metrics.
- Cache failure monitoring.

## Cache Policy

Boleh digunakan untuk:

- Harga publik terverifikasi.
- Direktori PKS publik.
- Reference data yang sesuai.
- Scoped dashboard aggregates.

Jangan menjadi source of truth untuk:

- Kuota kontrak.
- Penerbitan e-DO.
- Status pembayaran final.
- Rekonsiliasi transaksi.
- Audit keuangan.
- Otorisasi sensitif.

Untuk pembacaan nonkritis, fallback PostgreSQL dapat digunakan saat Redis tidak tersedia sesuai kebijakan.

Untuk keamanan, gunakan fail-closed apabila dependency keamanan kritis tidak tersedia.

## Performance Requirements

Sejak awal terapkan:

- Async I/O.
- Connection pool tuning.
- Bounded concurrency.
- No N+1 queries.
- Selective eager loading.
- Pagination.
- Query optimization.
- Appropriate composite indexes.
- EXPLAIN ANALYZE pada query penting.
- Safe bulk processing.
- Resource lifecycle.
- Avoid blocking sync operations dalam async event loop.

Jangan menunda optimasi fundamental sampai B11.

Setiap milestone wajib memeriksa performa operasi kritis yang baru dibuat.

Jangan mengklaim target latency tercapai tanpa benchmark.

---

# 11. SECURITY BASELINE

Security harus mengikuti M0.1, TRD, BSD, dan ADR-005.

Implementasikan secara bertahap sesuai IPD:

- Server-side sessions.
- HttpOnly cookies.
- Secure cookies untuk HTTPS.
- SameSite policy.
- CSRF header.
- Argon2id.
- Login rate limiting.
- Default-deny RBAC.
- Resource ownership/scope checks.
- Maker-checker / Separation of Duties.
- Session revocation.
- Session expiration.
- Input validation.
- File upload validation.
- Structured security event logs.
- Audit trail.
- Redaction of credentials.
- Least-privilege database access.

Gunakan matriks:

`contracts/role-permissions.yaml`

M0.1 menetapkan:

- PUBLIC anonim.
- 7 peran internal.
- 64 permission.
- 6 aturan separation of duties.
- 84 operasi API terautentikasi dari total 95.

Seluruh operasi internal harus mengikuti kontrak aktual.

Jangan hanya mengandalkan frontend untuk membatasi akses.

---

# 12. CONTRACT-FIRST IMPLEMENTATION

Kontrak kanonis:

`contracts/openapi.v1.yaml`

M0.1 telah menetapkan:

- OpenAPI 3.1.0.
- 75 paths.
- 95 operations.
- 191 schemas.
- 69 error codes.
- 11 state machines.
- 41 state transitions.
- 8 operasi idempotency wajib.
- 11 fixture JSON.
- 22 negative scenarios.

Angka tersebut merupakan baseline M0.1 dan harus diverifikasi terhadap file aktual.

## Mandatory Contract Rules

1. Jangan mengubah operationId secara sepihak.
2. Jangan mengganti response envelope.
3. Jangan mengganti error codes tanpa prosedur perubahan kontrak.
4. Gunakan decimal string.
5. Gunakan UTC timestamps.
6. Gunakan UUID.
7. Gunakan status kanonis.
8. Implementasikan permission sesuai matriks.
9. Gunakan error response dengan `request_id`.
10. Gunakan required Idempotency-Key untuk delapan operasi kontrak.
11. Pastikan OpenAPI runtime FastAPI sesuai kontrak kanonis.
12. Tidak boleh menambahkan API produksi fiktif hanya untuk memenuhi jumlah operasi.

Perubahan kontrak yang benar-benar diperlukan harus mengikuti Contract Change Management.

Jangan mengedit `contracts/` hanya untuk menyesuaikan implementasi yang salah.

Perbaiki implementasi agar sesuai kontrak.

Jika ditemukan kesalahan nyata pada kontrak, catat usulan perubahan di checkpoint dan ikuti review serta validasi M0.1 sebelum menerapkannya.

---

# 13. BUSINESS RULES & PENDING SOP

Jangan mengarang keputusan manajemen Perumda.

Pertahankan klasifikasi:

- CONFIRMED.
- SIMULATION_ONLY.
- PENDING_SOP.
- FUTURE.

## Aturan Kritis

- Toleransi timbang 1,5% hanya simulasi.
- Grading 2% hanya simulasi.
- Alokasi proporsional multi-petani hanya simulasi.
- Model principal/agent harus tervalidasi.
- Default `business_model_code = UNCONFIRMED`.
- Operasi keuangan nyata yang bergantung pada model belum disahkan harus ditolak.
- Invoice approval tidak sama dengan pembayaran.
- Pembayaran PKS kepada Perumda tidak sama dengan pembayaran kepada petani.
- Bukti pembayaran harus diverifikasi.
- Admin teknis tidak otomatis boleh menjadi approver.
- Tidak ada transfer bank otomatis pada Core MVP.
- Tidak ada GPS tracking real-time pada Core MVP.
- Tidak ada kendali hardware timbangan langsung pada Core MVP.

Jangan mengaktifkan transaksi finansial nyata hanya untuk membuat test happy path lulus.

Gunakan data fixture simulasi untuk menjalankan skenario penelitian dan pengujian.

---

# 14. FULL BACKEND MILESTONE EXECUTION PLAN

Ikuti detail pekerjaan, test, dan exit gate resmi pada `docs/IPD.md §10–21`.

Ringkasan di bawah merupakan arahan eksekusi, bukan pengganti IPD.

## B0 — PROJECT FOUNDATION

Bangun:

- Python project.
- uv configuration.
- FastAPI.
- Pydantic Settings.
- PostgreSQL async.
- SQLAlchemy async.
- Alembic baseline.
- Redis async.
- Dependency injection.
- Application lifespan.
- Request ID middleware.
- Structured logging.
- Global exception handlers.
- Health endpoints.
- Docker Compose PostgreSQL + Redis.
- Testing environment.
- Ruff/Pyright/pytest.
- Import boundary tests.

Jangan membuat modul bisnis kosong.

### Tests

- Startup.
- Shutdown.
- PostgreSQL connectivity.
- Redis connectivity.
- Pool cleanup.
- Config validation.
- Request ID.
- Error response.
- Health live.
- Health ready.
- Architecture rules.

### Exit

`B0_PASS — FOUNDATION_VERIFIED`

---

## B1 — IDENTITY & ACCESS

Bangun:

- User accounts.
- Roles.
- Permissions.
- Access scopes.
- Argon2id.
- Session creation.
- Login/logout.
- Session expiry/revocation.
- CSRF.
- RBAC.
- Resource ownership.
- Security events.
- Rate limiting.

### Tests

- Valid login.
- Invalid login.
- Disabled account.
- Session expiry.
- Logout.
- CSRF invalid.
- Cross-role denial.
- Cross-scope denial.
- Session fixation.
- Privilege escalation.
- Rate limiting.
- ADMIN non-approver guard.

### Exit

`B1_PASS — IDENTITY_ACCESS_VERIFIED`

---

## B2 — MASTER DATA

Bangun modul:

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

### Tests

- CRUD.
- Duplicate code.
- Unique constraints.
- Foreign keys.
- Soft deactivation.
- Historical references.
- Scope isolation.
- Coordinate validation.
- Optimistic locking.
- Concurrent modifications.

### Exit

`B2_PASS — MASTER_DATA_VERIFIED`

---

## B3 — PUBLIC PORTAL & PRICING

Bangun:

- Harga multi-PKS.
- Price categories.
- Price sources.
- Disbun references.
- Price verification.
- Maker-checker.
- Publication.
- Price history.
- Public mill directory.
- Public profile.
- Public notices.
- Redis cache-aside.
- Cache invalidation.
- Filtering.
- Pagination.

### Tests

- Public without login.
- Draft price hidden.
- Private commercial data hidden.
- Verified price publication.
- Derived expired state.
- Non-comparable category handling.
- Cache hit.
- Cache miss.
- Cache invalidation.
- Redis fallback.
- Concurrent publication.
- Public API contract.

### Exit

`B3_PASS — PUBLIC_PRICING_VERIFIED`

---

## B4 — TBS RECEIVING & GRADING

Bangun:

- Receipt creation.
- Farmer/cooperative links.
- Gross weight.
- Tare weight.
- Net weight.
- Grading.
- Weight deductions.
- Weighing revisions.
- Status transitions.
- Audit.

Gunakan Decimal untuk seluruh perhitungan.

### Tests

- Netto = Gross - Tare.
- Tare > Gross rejected.
- Negative weight rejected.
- Decimal precision.
- Grading simulation.
- No double deductions.
- Duplicate receipt.
- Idempotency.
- Version conflict.
- Unauthorized revision.
- Ownership isolation.

### Exit

`B4_PASS — RECEIVING_GRADING_VERIFIED`

---

## B5 — CONTRACTS & QUOTA

Bangun:

- Trade contracts.
- Contract parties.
- Principal/agent classification.
- Contract status.
- Quota periods.
- Quota reservation.
- Quota consumption.
- Quota release.
- Transactional locking.
- Concurrency protection.

### Tests

- Valid contract.
- Expired contract.
- Quota sufficient.
- Quota exceeded.
- Concurrent reservation.
- Rollback.
- Double consumption.
- Reservation release.
- Scope isolation.
- Contract version conflict.

### Exit

`B5_PASS — CONTRACT_QUOTA_VERIFIED`

---

## B6 — LOGISTICS & e-DO

Bangun:

- Delivery order drafts.
- Multi-farmer consolidation.
- Delivery lines.
- Destination PKS.
- Vehicle and driver.
- Document numbering.
- QR verification.
- Quota reservation.
- Delivery status.
- Status history.
- Cancellation.
- Idempotency.
- Transaction audit.

### Tests

- Multi-receipt delivery.
- Double allocation prevention.
- Unique document.
- QR validity.
- Wrong mill denied.
- Quota conflict.
- Concurrent issuance.
- Request retry.
- Rollback.
- Invalid transition.
- Cancellation authorization.

### Exit

`B6_PASS — LOGISTICS_EDO_VERIFIED`

---

## B7 — MILL WEIGHING

Bangun:

- e-DO arrival verification.
- Mill tickets.
- Gross/tare/net mill weight.
- Mill grading.
- File evidence.
- Ticket revisions.
- Current-ticket uniqueness.
- Mill-scoped access.
- Verified ticket workflow.

### Tests

- Wrong PKS denied.
- Duplicate ticket.
- Invalid weighing.
- Evidence validation.
- Ticket history.
- Only one current ticket.
- Unauthorized access.
- Cross-module consistency.
- Revision conflict.

### Exit

`B7_PASS — MILL_WEIGHING_VERIFIED`

---

## B8 — RECONCILIATION & DISPUTE

Bangun:

- Reconciliation cases.
- Origin/mill ticket matching.
- Weight differences.
- Difference percentages.
- Versioned tolerance.
- Matched.
- Dispute/Hold.
- Under review.
- Resolution.
- Review evidence.
- Audit history.

### Tests

- Normal differences.
- Beyond tolerance.
- Negative difference.
- Zero weight.
- Missing ticket.
- Unverified ticket.
- Duplicate reconciliation.
- Rule version changes.
- Unauthorized resolution.
- Missing reason/evidence.
- Concurrent reconciliation.
- Immutable history.

### Exit

`B8_PASS — RECONCILIATION_VERIFIED`

---

## B9 — FINANCE & SETTLEMENT

Bangun:

- Farmer allocation.
- Settlement calculations.
- Invoice drafts.
- Invoice lines.
- Invoice verification.
- Invoice issuance.
- Payment approvals.
- Payment records.
- Payment evidence.
- Payment verification.
- AR/AP distinction.
- Financial audit.
- Reversal/adjustment within approved scope.
- Pending SOP guard.

### Tests

- Decimal accuracy.
- Correct parties.
- Invoice totals.
- Historical snapshots.
- Authorized approval.
- Maker != Checker.
- Duplicate payment protection.
- Verified payment.
- Unverified evidence.
- Dispute hold.
- Allocation totals.
- Unconfirmed business model.
- Principal/agent simulation.
- Payment partial rejection.
- Farmer payment status correctness.

### Critical Rule

Jangan memalsukan approval SOP.

Implementasikan workflow simulasi jika keputusan Perumda belum tersedia.

Keuangan nyata harus tetap diblokir sesuai kontrak.

### Exit

`B9_PASS — FINANCE_SIMULATION_VERIFIED`

Jika kebijakan keuangan belum disahkan, jangan menggunakan status yang mengimplikasikan production finance readiness.

---

## B10 — REPORTING & AUDIT

Bangun:

- Overview reporting.
- Supply reporting.
- Pricing reporting.
- Reconciliation reporting.
- Finance reporting.
- Director dashboard data.
- Audit event queries.
- Request tracing.
- Query aggregation.
- Scoped caching.
- Query profiling.
- Pagination.
- Authorized exports bila termasuk kontrak.

### Tests

- Correct tonnage.
- Cancelled transactions excluded.
- AR/AP separated.
- Farmer payment not falsely marked paid.
- Correct aggregate totals.
- Role-specific visibility.
- Scoped dashboard data.
- No cross-scope leak.
- No N+1 queries.
- Cache isolation.
- Query plan verification.

### Exit

`B10_PASS — REPORTING_AUDIT_VERIFIED`

---

## B11 — HARDENING & FINAL VERIFICATION

Lakukan audit seluruh backend.

### Security Review

- Session.
- CSRF.
- RBAC.
- Resource scope.
- Password hashing.
- Rate limiting.
- File uploads.
- Audit.
- PII redaction.
- Secrets.
- Access control.
- OWASP-relevant checks.

### Architecture Review

- Four layers.
- Import boundaries.
- SOLID.
- Coupling.
- Duplicate logic.
- Maintainability.
- Module ownership.

### Database Review

- Constraints.
- Indexes.
- EXPLAIN ANALYZE.
- Lock contention.
- Migration correctness.
- Rollback.
- Backup and restore test.
- N+1.
- Connection pool behavior.

### Redis Review

- Key design.
- TTL.
- Cache isolation.
- Post-commit invalidation.
- Cache failure handling.
- No cache-as-source-of-truth.

### Performance Review

- Representative load tests.
- Latency.
- p50/p95/p99 where measurable.
- Throughput.
- Error rates.
- CPU/memory.
- Database timings.
- Bottlenecks.

Gunakan target performa yang ditetapkan di TRD/IPD.

Laporkan nilai benchmark aktual, bukan estimasi.

### Full Backend E2E

Jalankan workflow bisnis end-to-end menggunakan HTTP/API:

1. Login.
2. Master data.
3. Harga.
4. Penerimaan.
5. Kontrak.
6. Kuota.
7. e-DO.
8. Tiket PKS.
9. Rekonsiliasi.
10. Invoice simulation.
11. Payment simulation.
12. Reporting.
13. Audit.

Gunakan simulasi untuk aturan Pending SOP.

Backend harus dapat menyelesaikan pengujian tanpa menjalankan frontend.

### Exit

`BACKEND_INDEPENDENT_READY`

Hanya jika semua persyaratan B11 `IPD §21.2` terpenuhi.

---

# 15. MANDATORY TESTING STRATEGY

Setiap milestone wajib menjalankan tes sesuai risiko.

Gunakan:

- Ruff format.
- Ruff lint.
- Pyright.
- Import Linter.
- pytest.
- pytest-asyncio.
- Hypothesis.
- HTTPX TestClient/AsyncClient.
- PostgreSQL integration tests.
- Redis tests.
- Contract tests.
- Security tests.
- Concurrency tests.
- Migration tests.
- Schemathesis.
- Locust.

Tidak semua tool harus dijalankan pada setiap perubahan kecil, tetapi quality gate milestone wajib sesuai IPD.

## Contract Regression

Jalankan:

```powershell
python contracts/scripts/validate_contracts.py
python -m unittest discover -s contracts/tests -v
```

Baseline terbaru M0.1 memiliki K1–K11.

Jangan menggunakan angka K1–K10 dari laporan historis sebagai pengganti regresi K11.

## Backend Tests

Contoh:

```powershell
cd backend

uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run lint-imports
uv run pytest -q
```

Gunakan perintah sebenarnya berdasarkan konfigurasi yang dibuat.

Pastikan `uv` menggunakan virtual environment proyek yang tepat.

## Critical Invariants

Wajib diuji pada database nyata ketika relevan:

- Tidak ada double allocation.
- Tidak ada over-quota saat konkurensi.
- Tidak ada duplicate payment.
- Tidak ada unauthorized approval.
- Tidak ada cross-scope data leak.
- Tidak ada final invoice saat policy UNCONFIRMED.
- Tidak ada PAID tanpa pembayaran terverifikasi.
- Tidak ada invalid state transition.
- Tidak ada duplicate current ticket.
- Tidak ada kehilangan riwayat audit.

Gunakan integration tests PostgreSQL untuk menguji locking dan concurrency.

SQLite tidak boleh digunakan sebagai bukti bahwa locking PostgreSQL telah teruji.

---

# 16. API CONTRACT RUNTIME VERIFICATION

Jangan hanya memeriksa bahwa FastAPI menghasilkan dokumen OpenAPI.

Pastikan:

- Runtime routes sesuai operationId.
- HTTP methods sesuai kontrak.
- Required request fields sesuai.
- Response schemas sesuai.
- Error status sesuai.
- Error codes sesuai.
- CSRF security sesuai.
- Auth permission sesuai.
- Pagination sesuai.
- Decimal strings sesuai.
- Nullable fields sesuai.
- Public/private separation sesuai.

Lakukan pengujian provider terhadap:

`contracts/openapi.v1.yaml`

Jangan menganggap keberhasilan validator statis M0.1 sudah membuktikan implementasi runtime benar.

Jika endpoint belum dijadwalkan pada milestone aktif, tandai sebagai `NOT_IMPLEMENTED_YET` dan jangan mengklaim full contract pass.

Pada B11, seluruh operasi Core MVP yang diwajibkan harus terimplementasi dan diverifikasi.

---

# 17. DOCKER & LOCAL DEVELOPMENT

Siapkan lingkungan development yang reproducible.

Gunakan Docker Compose untuk PostgreSQL dan Redis jika Docker tersedia.

Pastikan:

- Port tidak bertabrakan.
- Volume development terisolasi.
- Credentials development tidak hardcoded sebagai secret produksi.
- Healthchecks tersedia.
- Service startup order ditangani secara benar.
- Database migration dapat berjalan.
- Redis dapat diakses.
- Test database terpisah dari development database.

Jika Docker tidak tersedia, periksa PostgreSQL dan Redis lokal yang sudah berjalan.

Jangan menginstal atau mengubah service sistem secara destruktif tanpa persetujuan.

Jangan menghapus volume atau database pengguna.

Jangan mengakses database produksi kecuali secara eksplisit diizinkan untuk pekerjaan yang relevan.

---

# 18. OBSERVABILITY & CCTV DIGITAL

Implementasikan observability yang ringan tetapi berguna.

Minimal:

- Structured JSON logging.
- Request ID.
- Timestamp UTC.
- HTTP method.
- Route.
- Response status.
- Duration.
- Module.
- Error code.
- Correlation ID bila relevan.

Pisahkan:

**Technical Request Logs**

Untuk request trace, performa, dan error diagnosis.

**Business Audit Events**

Untuk peristiwa domain dan perubahan bisnis penting.

Business audit harus append-only sesuai BSD/DBD.

Jangan menyimpan:

- Password.
- Raw session cookie.
- CSRF secret.
- API keys.
- Database credentials.
- Full sensitive request payload.
- Nomor rekening atau data pribadi tanpa alasan yang sah.

---

# 19. SOURCE CONTROL & SAFE CHANGES

Sebelum coding:

1. Periksa `git status`.
2. Catat baseline commit.
3. Identifikasi perubahan yang belum di-commit.
4. Jangan menimpa pekerjaan pengguna.
5. Jangan melakukan reset/destructive cleanup.
6. Jangan menghapus file proyek tanpa alasan jelas.

## Allowed Edits

- `backend/`
- `infra/` yang diperlukan untuk backend.
- Konfigurasi CI backend jika dibutuhkan.
- `.gitignore` untuk environment/build.
- `docs/IMPLEMENTATION_CHECKPOINTS.md`.
- Dokumentasi setup backend minimal.

## Restricted

- `frontend/`.
- File FigCraft.
- Design tokens D5.
- Enam dokumen baseline V1.1.
- Shared contracts M0.1 tanpa Contract Change Management.

Jika perubahan kontrak diperlukan, gunakan prosedur M0.1 dan validasi K1–K11.

Catat setiap perubahan kontrak pada checkpoint yang sama.

Jangan membuat file changelog baru.

Jangan melakukan Git push otomatis.

Commit per milestone boleh dilakukan jika workflow Git pengguna mengizinkan; jangan memasukkan `.venv`, `.env`, secret, data produksi, atau artefak sementara.

---

# 20. CODE QUALITY REQUIREMENTS

Utamakan:

- Type hints.
- Descriptive naming.
- Short cohesive functions.
- Clear responsibilities.
- Minimal abstractions.
- Domain-centric organization.
- Explicit transaction boundaries.
- Dependency injection.
- No hidden global mutable state.
- Reusable infrastructure adapters.
- Robust error handling.
- Predictable tests.

Hindari:

- Giant `main.py`.
- Giant service files.
- Circular imports.
- Deep inheritance.
- Global database sessions.
- Redis connections dibuat per request.
- Hardcoded credentials.
- SQL string concatenation.
- Unbounded queries.
- N+1 database access.
- Blocking I/O di event loop.
- Silent exception swallowing.
- Fake success responses.
- Test yang hanya memeriksa status 200.
- Tests yang dibuat hanya untuk meloloskan gate.
- Menghapus tes gagal agar hasil terlihat PASS.

Jika pengujian gagal, perbaiki implementasi, bukan melemahkan tes.

---

# 21. QUALITY GATE PER MILESTONE

Setiap milestone hanya PASS apabila:

## Functional Gate

- Fitur sesuai IPD.
- Operasi sesuai OpenAPI.
- Business rules benar.
- Edge cases relevan ditangani.

## Architecture Gate

- Four-layer boundaries terjaga.
- Tidak ada prohibited imports.
- Tidak ada coupling lintas modul yang tidak sah.
- Struktur mudah dinavigasi.

## Database Gate

- Migration berhasil.
- Foreign key valid.
- Constraint bekerja.
- Transaction rollback benar.
- Query penting diperiksa.

## Security Gate

- Auth/permission sesuai kebutuhan.
- Resource scope ditegakkan.
- Tidak ada kebocoran informasi.
- Secrets aman.

## Testing Gate

- Unit tests PASS.
- Integration tests relevan PASS.
- API tests PASS.
- Regression tests PASS.
- Security/concurrency tests relevan PASS.

## Performance Gate

- Tidak ada blocking problem penting.
- Pooling dan lifecycle benar.
- Query tidak unbounded.
- Profiling dilakukan pada operasi kritis.

## Documentation Gate

- README setup akurat.
- Checkpoint diperbarui.
- Perubahan file tercatat.
- Test evidence tercatat.
- Known limitations jelas.

Tidak boleh memberi status PASS jika masih ada test kritis FAIL atau NOT_RUN karena blocker lingkungan.

---

# 22. AUTONOMOUS CONTINUATION POLICY

Tugas ini mencakup B0–B11.

Kerjakan secara bertahap dan lanjutkan ke milestone berikutnya jika exit gate milestone aktif telah PASS.

Jangan berhenti hanya untuk membuat laporan panjang setelah B0.

Jangan meminta user mengirim prompt baru untuk B1, B2, dan seterusnya apabila pekerjaan dapat dilanjutkan secara aman.

Tetapi jangan melewati blocker nyata.

Jika suatu milestone tidak dapat dilanjutkan karena dependency atau keputusan bisnis:

1. Identifikasi blocker.
2. Catat pada checkpoint.
3. Jangan tandai PASS.
4. Jangan mengubah aturan bisnis untuk melewatinya.
5. Kerjakan bagian lain yang independen jika aman.
6. Berikan status sebenarnya dan langkah pemulihan.

Jika batas eksekusi atau sesi tercapai, hentikan pada batas milestone/tugas yang aman, simpan checkpoint, dan laporkan status aktual.

Jangan menjanjikan pengerjaan background atau hasil yang belum dijalankan.

Ketika dilanjutkan dalam sesi berikutnya, baca checkpoint dan Git status untuk mengetahui posisi pekerjaan.

---

# 23. BACKEND CHECKPOINT FORMAT

Gunakan satu file:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Pertahankan semua histori D4, D5, M0, M0.1.

Buat bagian khusus Backend Track:

```markdown
# BACKEND DEVELOPMENT TRACK

## Current Status

Current Milestone:
Last Milestone Passed:
Last Verified Commit:
Backend Readiness:
Environment:
Pending SOP:
Open Blockers:

## B0 — Project Foundation
Status:
Completed:
Files Created:
Files Modified:
Dependencies:
Database Changes:
Tests:
Quality Gate:
Known Issues:
Next Action:

## B1 — Identity & Access
...

## B2 — Master Data
...

...

## B11 — Final Hardening
...
```

Gunakan append/update secara terkontrol.

Jangan mengulang ratusan baris history untuk pekerjaan kecil.

Gunakan ringkasan yang presisi dan mudah dibaca.

Untuk setiap tes, sertakan:

- Command.
- Actual result.
- PASS/FAIL.
- Test count jika tersedia.
- Environment.
- Relevant evidence.

Jika terdapat perubahan penting, catat alasan dan konsekuensinya.

---

# 24. FINAL BACKEND ACCEPTANCE CRITERIA

Backend dianggap selesai apabila:

1. B0–B11 mencapai PASS.
2. Semua modul Core MVP yang diwajibkan telah dibuat.
3. API contract Core MVP sesuai M0.1.
4. PostgreSQL migrations valid.
5. Redis berfungsi sesuai strategi.
6. Four-layer architecture terjaga.
7. Security tests lulus.
8. RBAC dan scope lulus.
9. CSRF dan session lulus.
10. Decimal calculations akurat.
11. Idempotency bekerja.
12. Concurrency invariants lulus.
13. State transitions valid.
14. Audit trail tersedia.
15. Error handling konsisten.
16. Logging dapat ditelusuri.
17. Database queries penting telah dioptimasi.
18. Load/performance tests dijalankan.
19. Backup/restore test lulus.
20. Backend E2E lulus tanpa frontend.
21. Seluruh kontrak regresi K1–K11 PASS.
22. Tidak ada critical regression.
23. Checkpoint aktual dan lengkap.
24. Dokumentasi setup backend benar.
25. Pending SOP tetap dilindungi.
26. Tidak ada kredensial nyata tersimpan dalam Git.
27. Backend dapat dijalankan ulang dari instruksi setup.
28. Tidak ada endpoint yang memberikan false success.
29. Tidak ada fitur deferred diklaim sebagai MVP.
30. Tidak ada klaim production readiness tanpa validasi operasional.

---

# 25. FINAL STATUS RULES

Gunakan:

## `BACKEND_INDEPENDENT_READY`

Jika B0–B11 telah selesai dan seluruh exit gate sesuai IPD benar-benar PASS.

## `BACKEND_CONDITIONALLY_READY`

Jika sebagian besar backend selesai tetapi masih ada masalah nonkritis yang dijelaskan secara eksplisit.

Jangan gunakan status ini untuk menyembunyikan kegagalan security, concurrency, transaksi, atau requirement Core MVP.

## `BACKEND_BLOCKED`

Jika terdapat blocker kritis.

## `BACKEND_IN_PROGRESS`

Jika masih terdapat milestone yang belum selesai.

Jangan memberi status READY hanya karena server berhasil dijalankan.

---

# 26. FINAL RESPONSE FORMAT

Setelah seluruh pekerjaan yang dapat dijalankan selesai, berikan ringkasan:

### A. Overall Backend Status

- Milestone aktif/terakhir.
- Backend readiness.
- Baseline commit.

### B. Milestone Completion

Tabel B0–B11:

- Milestone.
- Implemented.
- Tests.
- Exit gate.
- Status.

### C. Architecture

- Modules implemented.
- Four-layer compliance.
- PostgreSQL.
- Redis.
- Security.
- Performance.

### D. Database

- Migrations.
- Tables.
- Constraints.
- Indexes.
- Test database results.

### E. API

- Operation coverage.
- OpenAPI compliance.
- Authorization.
- Error response.

### F. Tests

- Unit.
- Integration.
- Contract.
- Security.
- Concurrency.
- Cache.
- Performance.
- E2E.

### G. Pending SOP

- Unresolved decisions.
- Simulation safeguards.
- Production limitations.

### H. Checkpoint

- File location.
- Last milestone passed.
- Remaining work.

### I. Final Decision

Berikan status sesuai bukti.

Jangan membuat dokumen laporan akhir terpisah; seluruh rincian perubahan dan tes harus berada di satu file checkpoint.

---

# 27. EXECUTION COMMAND

Mulai dengan urutan berikut:

1. Verifikasi workspace.
2. Baca keenam dokumen V1.1.
3. Baca seluruh ADR.
4. Baca seluruh kontrak M0.1.
5. Baca seluruh fixture.
6. Baca checkpoint terbaru.
7. Discover `.agents/skills`.
8. Baca skill yang relevan.
9. Verifikasi interpreter `.venv`.
10. Periksa Git baseline.
11. Audit lingkungan PostgreSQL, Redis, dan Docker.
12. Buat execution plan internal B0–B11 sesuai IPD.
13. Mulai implementasi B0.
14. Jalankan quality gate B0.
15. Perbaiki kegagalan.
16. Perbarui satu file checkpoint.
17. Lanjutkan B1.
18. Ulangi pola tersebut hingga B11.
19. Jalankan final backend E2E dan regression suite.
20. Berikan keputusan readiness berdasarkan bukti.

## IMPORTANT FINAL DIRECTIVE

**Jangan hanya membuat planning document.**

**Jangan hanya melakukan audit.**

**Jangan membuat ulang M0/M0.1.**

**Jangan membuat laporan terpisah untuk setiap milestone.**

**Jangan mengubah baseline V1.1 tanpa Change Request.**

**Jangan membuat frontend.**

**Jangan menganggap data simulasi sebagai data produksi.**

**Kerjakan seluruh backend B0–B11 secara nyata, berurutan, teruji, dan terkontrol, selama prasyarat serta batas eksekusi memungkinkan.**

Gunakan skill yang tersedia untuk meningkatkan kualitas engineering.

Gunakan seluruh dokumen sebagai sumber kebenaran.

Gunakan **satu dokumen checkpoint** untuk seluruh progres dan catatan perubahan.

Prioritaskan:

**Correctness → Security → Data Integrity → Maintainability → Performance → Completeness.**

Final target:

# BACKEND_INDEPENDENT_READY

START EXECUTION NOW.
