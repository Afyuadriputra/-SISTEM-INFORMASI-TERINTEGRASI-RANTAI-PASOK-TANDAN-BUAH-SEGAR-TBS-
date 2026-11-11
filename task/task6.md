
# ANTIGRAVITY — F11.1 FINAL FRONTEND UAT & INTEGRATION VERIFICATION

## Mission

Lakukan verifikasi final terhadap frontend F0–F11 Sistem Informasi Terintegrasi Rantai Pasok TBS Perumda Tuah Sekata.

Frontend telah dilaporkan mencapai `READY — FRONTEND_BACKEND_INTEGRATION_VERIFIED`, tetapi masih memerlukan perluasan bukti pengujian live, verifikasi UI/UX, serta penutupan validator kontrak K10.

**Jangan membangun ulang aplikasi. Jangan melakukan redesign menyeluruh. Jangan menambahkan fitur di luar Core MVP.**

## 1. Mandatory Read First

Baca:

- `docs/PRD.md`, `TRD.md`, `AFD.md`, `DBD.md`, `BSD.md`, `IPD.md`
- `docs/adr/`
- `docs/m0/`
- Seluruh kontrak pada `contracts/`
- `docs/IMPLEMENTATION_CHECKPOINTS.md`
- Frontend dan test suite aktual
- Backend B11.1 handoff
- FigCraft D5 dan screenshot referensi

Gunakan skill relevan dari:

`D:\Kuliah\joki\radit\projek thesis bg givo\.agents\skills`

## 2. Fix K10 Contract Validator

Periksa `contracts/scripts/validate_contracts.py`.

K10 sebelumnya menandai folder `frontend/` sebagai perubahan terlarang, meskipun proyek sudah memasuki Frontend Track.

Perbaiki validasi agar memahami fase M0, Backend Track, dan Frontend Track.

Tetap cegah modifikasi kontrak atau baseline V1.1 yang tidak sah.

Jangan sekadar menonaktifkan K10 atau menghapus assertion.

Tambahkan regression test untuk aturan scope baru.

Jalankan seluruh K1–K11 hingga PASS.

Catat perubahan sebagai penyelarasan tooling validasi, bukan perubahan business contract.

## 3. Real Backend Integration Audit

Gunakan `VITE_API_MODE=real`.

Pastikan MSW benar-benar tidak aktif.

Gunakan FastAPI, PostgreSQL, dan Redis nyata pada lingkungan pengujian terisolasi.

Verifikasi secara eksplisit:

- Backend PostgreSQL 16 WSL2 vs PostgreSQL 17 Windows.
- Host, port, nama database, Alembic HEAD.
- Test database terpisah dari data operasional.
- Tidak ada penggunaan credentials produksi.

Jangan melakukan destructive reset pada database yang sudah ada.

## 4. Seven-Role Browser Testing

Perluas Playwright untuk seluruh peran:

1. FARMER.
2. COOPERATIVE_OPERATOR.
3. PERUMDA_OPERATIONS.
4. PERUMDA_FINANCE.
5. MILL_OPERATOR.
6. DIRECTOR.
7. SYSTEM_ADMIN.

Wajib menguji:

- Login.
- Logout.
- Session reload.
- Session expiry.
- Allowed routes.
- Forbidden routes.
- Permission-aware navigation.
- Cross-scope access denial.
- Unauthorized mutations.

Jangan hanya menguji penampilan menu. Verifikasi juga respons backend nyata untuk penolakan akses.

## 5. Complete Critical Workflow E2E

Buat skenario Playwright live menggunakan dataset sintetis yang deterministik.

### Workflow A — Master Data

Petani → Kebun → Koperasi → PKS → validasi dan pembatasan scope.

### Workflow B — Pricing

Draft harga → Submit → Maker/Checker → Publish → tampil di portal publik sesuai hak publikasi.

### Workflow C — Receiving & Logistics

Penerimaan TBS → Penimbangan → Grading → Validasi → Kontrak/Kuota → e-DO → QR.

### Workflow D — Mill & Reconciliation

Verifikasi e-DO → Tiket timbang PKS → Unggah bukti → Verifikasi → Rekonsiliasi → Dispute/Hold → Review sesuai izin.

### Workflow E — Finance Simulation

Invoice → Approval → Bukti bayar → Verifikasi → Status settlement.

Pastikan:

- APPROVED tidak otomatis PAID.
- Pending SOP tetap diblokir.
- Maker != Checker.
- Tidak ada double payment.
- AR/AP terpisah.
- Tidak ada transfer bank otomatis.

### Workflow F — Reporting & Admin

Dashboard Direksi → Reports → Audit → User management → Session revocation → System health.

Untuk setiap skenario, dokumentasikan operasi API nyata, role, hasil, dan error code jika gagal.

Jangan memaksakan happy path finansial dengan mengubah aturan bisnis.

## 6. Complete Route & Responsive Audit

Uji 26 rute sesuai AFD §36.

Viewport wajib:

- 1440px.
- 1280px.
- 768px.
- 390px.
- 375px.

Verifikasi:

- Tidak ada global horizontal overflow.
- Sidebar desktop tetap stabil.
- Drawer mobile bekerja.
- Tabel dapat digunakan.
- Form tidak terpotong.
- Button dan dialog bisa diakses.
- Navigasi aktif benar.
- Tidak ada dead-end interaction.

Prioritaskan tujuh layar mobile bisnis FigCraft D5.

## 7. Accessibility & Visual Verification

Lakukan axe-core pada halaman bisnis prioritas, bukan hanya homepage.

Tambahkan pemeriksaan manual/otomatis yang relevan:

- Tab order.
- Keyboard-only navigation.
- Escape dialog/drawer.
- Focus trap.
- Focus restoration.
- Form labels.
- Error announcements.
- Reduced motion.
- Contrast.
- Target sentuh.
- Screen reader compatibility sejauh alat tersedia.

Bandingkan screenshot browser dengan FigCraft D5.

Perbaiki hanya ketidaksesuaian visual nyata.

Jangan menilai kepatuhan anti-AI-slop menggunakan jumlah karakter em dash.

## 8. Mock/Real Safety

Pastikan:

- Build `real` tidak menyertakan MSW.
- Tidak ada fallback tersembunyi ke fixture.
- Build yang dimaksudkan untuk integrasi/produksi tidak dapat diam-diam memakai mode mock.
- Error API ditampilkan dengan benar.
- Tidak ada fake success.
- Session dan data sensitif dibersihkan saat logout.

## 9. Final Regression

Jalankan:

- Typecheck.
- ESLint.
- Vitest.
- Production build real.
- Playwright live.
- Accessibility checks.
- Responsive checks.
- Contract K1–K11.
- Backend pytest.
- `git diff --check`.

Jangan melaporkan PASS untuk tes yang belum dijalankan.

## 10. Strict Edit Boundary

Boleh mengubah:

- `frontend/` untuk perbaikan defect yang terbukti.
- `frontend/tests/` untuk meningkatkan cakupan.
- Validator dan tes K10 secara terbatas.
- `docs/IMPLEMENTATION_CHECKPOINTS.md`.

Dilarang mengubah:

- Enam dokumen V1.1.
- Definisi bisnis di kontrak M0.1.
- Business logic backend tanpa Change Request.
- Migrasi database produksi.
- FigCraft D5.

Tidak boleh menghapus perubahan pengguna atau mengubah data produksi.

## 11. Single Checkpoint Policy

Catat seluruh hasil pada:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Tambahkan checkpoint:

`F11.1 — Final Frontend UAT & Integration Verification`

Jangan membuat laporan milestone atau changelog terpisah.

## 12. Final Decision

Gunakan:

`READY — F11_1_FULL_INTEGRATION_AND_UX_VERIFIED`

Hanya apabila seluruh quality gate kritis benar-benar PASS.

Jika masih ada celah nonkritis:

`CONDITIONALLY_READY — F11_1_LIMITED_UAT`

Jika ditemukan defect kritis:

`BLOCKED — F11_1_CRITICAL_DEFECTS`

Berikan ringkasan:

- 26-route coverage.
- Seven-role coverage.
- Critical workflow coverage.
- Responsive results.
- Accessibility results.
- Real API integration.
- K1–K11.
- Regression.
- Defects found/fixed.
- Remaining limitations.
- Git status.

Mulai audit dan pengujian sekarang, lalu lakukan perbaikan minimal yang diperlukan berdasarkan temuan nyata.
