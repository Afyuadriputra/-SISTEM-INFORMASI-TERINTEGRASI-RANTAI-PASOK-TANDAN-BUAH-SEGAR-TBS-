
# ANTIGRAVITY — B11.1 POST-IMPLEMENTATION VERIFICATION

## TUJUAN

Audit secara independen seluruh backend yang sudah diselesaikan melalui B0–B11.

Proyek: Sistem Informasi Terintegrasi Rantai Pasok TBS Perumda Tuah Sekata.

**Jangan mengimplementasikan backend dari nol. Jangan melakukan redesign arsitektur. Jangan membuat ulang kontrak M0.1.**

Tujuan audit adalah memastikan klaim `BACKEND_INDEPENDENT_READY` benar-benar didukung oleh source code, database, runtime API, dan pengujian yang memadai.

## 1. READ FIRST

Baca:

- `docs/PRD.md`
- `docs/TRD.md`
- `docs/AFD.md`
- `docs/DBD.md`
- `docs/BSD.md`
- `docs/IPD.md`
- `docs/adr/`
- `docs/m0/`
- `contracts/`
- `docs/IMPLEMENTATION_CHECKPOINTS.md`

Periksa seluruh source code `backend/`, migration, konfigurasi, dan pengujian.

Gunakan skill yang relevan dari:

`D:\Kuliah\joki\radit\projek thesis bg givo\.agents\skills`

## 2. CHECKPOINT CONSISTENCY

Perbaiki status stale pada bagian Backend Development Track:

- Current Milestone masih B4.
- Last Milestone Passed masih B3.
- Backend Readiness masih BACKEND_IN_PROGRESS.

Selaraskan dengan status final B11 yang benar-benar diverifikasi.

Periksa juga referensi Frontend F0–F11 dan riwayat milestone.

Jangan menghapus histori D4, D5, M0, M0.1, ataupun B0–B11.

## 3. DATABASE SCHEMA AUDIT

Inspeksi metadata PostgreSQL nyata dan Alembic.

Bandingkan:

- 48 kandidat tabel DBD.
- Tabel yang benar-benar tersedia.
- Tabel tambahan implementasi.
- Tabel yang ditangguhkan.
- Foreign keys.
- Unique/check constraints.
- Partial indexes.
- Migration dependencies.
- Current Alembic HEAD.

Jelaskan mengapa laporan restore mencatat 48 tabel sementara inventaris migration pada checkpoint belum menunjukkan pemetaan yang lengkap.

Jangan mengubah schema hanya untuk menyamakan jumlah tabel.

Jika menemukan perbedaan, klasifikasikan CORE / SUPPORTING / DEFERRED / UNEXPECTED.

## 4. MODULE ARCHITECTURE AUDIT

Petakan semua paket modul aktual ke domain kanonis M0.1.

Periksa arah import:

- Domain tidak mengimpor Infrastructure.
- Application menggunakan ports.
- Infrastructure mengimplementasikan ports.
- Presentation memanggil Application.
- Composition root melakukan wiring.

Periksa coupling lintas modul, duplikasi business rules, dan ketergantungan melingkar.

Jangan memecah atau menggabungkan modul tanpa defect atau manfaat arsitektural yang terbukti.

## 5. LIVE API CONTRACT AUDIT

Jangan berhenti pada pencocokan 95 path/operationId.

Uji runtime API terhadap `contracts/openapi.v1.yaml`:

- HTTP methods.
- Request validation.
- Required fields.
- Response body.
- Response status.
- Error envelope.
- Decimal serialization.
- UUID dan timestamp.
- Pagination.
- Authentication.
- CSRF.
- Role permissions.
- Resource scope.
- Idempotency.
- State transitions.

Periksa seluruh 95 operasi pada level kontrak sesuai teknik verifikasi yang tersedia.

Tandai dengan jelas operasi yang hanya lulus static parity dan operasi yang telah lulus functional runtime tests.

Jangan mengklaim functional conformance 95/95 jika baru memverifikasi daftar route.

## 6. SECURITY & BUSINESS INVARIANTS

Prioritaskan pengujian negatif:

- Cross-role access.
- Cross-cooperative access.
- Cross-mill access.
- Farmer data isolation.
- SYSTEM_ADMIN non-approver.
- Maker-checker.
- CSRF invalid.
- Session expired/revoked.
- Rate limiting.
- Unauthorized file access.
- Invalid state transition.
- Duplicate receipt.
- Double allocation.
- Quota overbooking.
- Concurrent e-DO issuance.
- Duplicate mill ticket.
- Duplicate payment.
- Financial dispute hold.
- UNCONFIRMED policy.
- APPROVED != PAID.
- Final settlement blocked pending SOP.

Pastikan pengujian menggunakan data sintetis dan database test terisolasi.

## 7. PERFORMANCE REVIEW

Lakukan benchmark lebih representatif dari pengujian 60 request GET sebelumnya.

Minimal periksa:

- Read endpoints.
- Authenticated list endpoints.
- Scoped dashboard.
- Quota reservation concurrency.
- Idempotent write retry.
- Reconciliation calculation.
- PostgreSQL query plans.
- N+1 queries.
- Redis cache hit/miss.
- Redis outage fallback.
- Connection pool stability.

Gunakan beban wajar untuk lingkungan lokal, jangan melakukan stress test destruktif.

Catat jumlah request, tingkat error, p50, p95, p99 jika tersedia, serta batasan pengujian.

Bandingkan dengan target TRD/IPD yang sebenarnya.

Jangan mengklaim target tercapai jika workload atau ukuran dataset tidak representatif.

## 8. REGRESSION

Jalankan ulang:

- Ruff format.
- Ruff lint.
- Pyright.
- Import Linter.
- Pytest.
- Unit tests.
- PostgreSQL integration tests.
- Redis tests.
- Migration verification.
- Contract checks K1–K11.
- Git diff check.

Pastikan hasil setelah perbaikan terakhir benar-benar PASS.

Jangan melemahkan atau menghapus test yang gagal.

## 9. GIT & ENVIRONMENT AUDIT

Periksa:

- Current branch.
- HEAD commit.
- Uncommitted changes.
- Untracked files.
- `.venv` exclusions.
- `.env` exclusions.
- No hardcoded secrets.
- Runtime PostgreSQL/Redis configuration.
- Clean setup instructions.

Jangan membuat commit atau push tanpa persetujuan.

Jangan mereset atau menghapus perubahan pengguna.

Jangan menghapus database maupun volume yang sudah ada.

## 10. SINGLE CHECKPOINT FILE POLICY

Semua catatan hasil audit, perubahan, bug, pengujian, dan keputusan akhir harus masuk ke:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Tambahkan bagian:

`B11.1 — Post-Implementation Verification`

Jangan membuat file laporan audit atau changelog baru.

Output terminal dan file temporary untuk alat pengujian diperbolehkan; ringkasan bukti wajib masuk ke checkpoint.

## 11. EDIT BOUNDARIES

Boleh:

- Memperbaiki defect backend yang benar-benar teridentifikasi.
- Menambah tes yang diperlukan.
- Memperbaiki konfigurasi test.
- Memperbarui checkpoint.
- Memperbaiki README backend bila ada instruksi setup yang salah.

Dilarang:

- Mengubah keenam dokumen V1.1.
- Mengubah frontend.
- Mengubah FigCraft.
- Mengubah kontrak M0.1 secara sepihak.
- Melakukan schema change destruktif.
- Mengarang persetujuan SOP.
- Membuat fitur baru di luar audit.

Jika ditemukan kesalahan kontrak, catat Change Request melalui mekanisme M0.1.

## 12. FINAL DECISION

Gunakan salah satu status:

`READY — B11_1_POST_IMPLEMENTATION_VERIFIED`

Jika audit source code, database, security, runtime contract, regression, dan quality gate kritis benar-benar PASS.

`CONDITIONALLY_READY — NON_CRITICAL_ISSUES_REMAIN`

Jika hanya ada kekurangan nonkritis yang tidak membahayakan integrasi awal.

`BLOCKED — CRITICAL_BACKEND_DEFECTS`

Jika masih ada masalah integritas data, security, kontrak inti, concurrency, atau workflow bisnis.

Berikan hasil ringkas di chat:

1. Status akhir.
2. Masalah yang ditemukan.
3. Masalah yang diperbaiki.
4. Hasil validasi.
5. API functional coverage.
6. Database schema coverage.
7. Security findings.
8. Performance findings.
9. Git status.
10. Kesiapan integrasi frontend.

Jangan mengklaim READY tanpa bukti.

**Kerjakan audit aktual, bukan hanya menghasilkan rencana.**
