
# ANTIGRAVITY — LOCAL DEMO ENVIRONMENT & REAL DATA INTEGRATION

## Sistem Informasi Rantai Pasok TBS Perumda Tuah Sekata

### MISSION

Siapkan aplikasi agar dapat dijalankan dan digunakan secara lokal di Windows 11, dengan:

- React frontend nyata.
- FastAPI backend nyata.
- PostgreSQL berisi data sintetis/Faker yang saling terhubung.
- Redis untuk session dan cache.
- Login menggunakan akun demo tujuh peran.
- Semua halaman mengambil data melalui backend, bukan MSW.
- Workflow bisnis berjalan menggunakan database demo.
- Satu perintah sederhana untuk menjalankan sistem.

**Ini tugas implementasi dan setup nyata. Jangan hanya membuat panduan.**

## 1. WORKSPACE

Root:

`D:\Kuliah\joki\radit\projek thesis bg givo`

Referensi:

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
- `.agents/skills/`

Baca seluruh referensi yang relevan.

Gunakan skills dari `.agents/skills/` sesuai kebutuhan.

Status dasar proyek:

- Backend B11.1 VERIFIED.
- Frontend F11.1 VERIFIED.
- 95 operasi API kanonis.
- 26 rute frontend.
- Tujuh peran internal.
- PostgreSQL + Redis telah digunakan dalam pengujian.
- Mode frontend `VITE_API_MODE=real` telah diuji.

**Jangan membuat ulang backend atau frontend.**

## 2. LOCAL DEMO ARCHITECTURE

Target:

```text
Browser
  |
  v
React + Vite :5173
  |
  | VITE_API_MODE=real
  | Proxy /api
  v
FastAPI :8000
  |
  +---- PostgreSQL agroniaga_demo
  |
  +---- Redis DB /2
```

Lingkungan yang sebelumnya digunakan:

- PostgreSQL 16 di WSL2.
- PostgreSQL host `127.0.0.1`.
- PostgreSQL port `15432`.
- Redis host `127.0.0.1`.
- Redis port `6379`.

Verifikasi kondisi aktual sebelum menggunakan konfigurasi tersebut.

## 3. ISOLATED DEMO DATABASE

Buat database khusus:

`agroniaga_demo`

Gunakan Redis logical DB:

`/2`

Jangan menggunakan atau melakukan reset terhadap:

- `agroniaga_dev`
- `agroniaga_test`
- Database PostgreSQL 17 lain pada port 5432
- Redis DB `/0`
- Redis DB `/1`

Jangan menggunakan database produksi.

Gunakan role PostgreSQL dengan hak akses yang diperlukan khusus untuk database demo.

Pastikan nama database dan koneksi diverifikasi secara eksplisit sebelum operasi tulis atau migrasi.

Jika database demo belum tersedia, buat secara aman.

Jika sudah tersedia, jangan hapus isinya otomatis.

Gunakan Alembic resmi untuk membuat seluruh skema:

`0011_b10_reporting_indexes`

Jangan membuat tabel manual baru yang tidak dibutuhkan.

Jangan mengubah migrasi B0–B11.

## 4. ENVIRONMENT CONFIGURATION

Buat konfigurasi lokal yang jelas untuk demo.

Contoh file:

`backend/.env.demo`

File ini harus masuk `.gitignore`.

Ambil nama environment variable sebenarnya dari `backend/app/core/config.py` dan `.env.example`.

Jangan menebak nama konfigurasi.

Konfigurasi harus menunjuk ke:

- PostgreSQL `agroniaga_demo`
- Redis `/2`
- Environment development/demo, bukan production
- Cookie dan CSRF yang kompatibel dengan localhost
- File storage demo terisolasi
- Logging development yang tidak memuat kredensial

Gunakan mekanisme pengaktifan konfigurasi demo yang eksplisit, misalnya melalui launcher PowerShell.

Jangan mengganti `backend/.env` milik pengguna.

Frontend wajib berjalan dengan:

`VITE_API_MODE=real`

Tidak boleh menggunakan mode `mock` atau MSW.

Jika diperlukan, tambahkan penanda demo yang terpisah dari API mode, sehingga aplikasi tetap memakai API nyata tetapi menampilkan label:

**MODE DEMO — DATA SINTETIS**

Jangan menampilkan data dummy seolah-olah merupakan informasi operasional resmi Perumda.

## 5. CREATE FAKER SEEDER

Buat seeder yang terstruktur dan maintainable.

Contoh lokasi:

`backend/scripts/seed_demo.py`

Gunakan Faker dengan locale Indonesia (`id_ID`) apabila tersedia/kompatibel.

Jika membutuhkan library baru, pasang dan catat melalui dependency management backend.

Seeder harus:

1. Reproducible menggunakan random seed tetap.
2. Idempotent.
3. Memiliki stable identifiers/reference codes.
4. Mempertahankan foreign-key integrity.
5. Menghasilkan data yang masuk akal secara bisnis.
6. Menggunakan Decimal untuk berat dan keuangan.
7. Mengikuti schema dan enum DBD/M0.1.
8. Menghormati state machines.
9. Menghormati role scopes.
10. Menghormati Pending SOP.
11. Tidak membuat transaksi pembayaran riil.
12. Tidak membuat PII orang nyata.
13. Tidak memakai data Perumda/PKS aktual tanpa sumber sah.
14. Menggunakan email domain contoh yang tidak dapat menerima email operasional.
15. Menandai record sintetis dengan identitas/nama/kode DEMO yang mudah dikenali.

Seeder tidak boleh membuat data dengan foreign key rusak hanya demi mencapai jumlah target.

Gunakan repository/use case yang sudah ada jika memungkinkan, terutama untuk transaksi yang perlu audit, state transition, atau side effects.

Jika bootstrap seed memerlukan penulisan SQLAlchemy secara langsung, pastikan setiap record memenuhi business invariants dan database constraints.

Jangan menonaktifkan triggers, check constraints, atau RBAC sebagai jalan pintas.

## 6. DEMO DATA TARGET

Target data awal:

| Entity                | Target |
| --------------------- | -----: |
| Mill companies / PKS  |      5 |
| Cooperatives          |      4 |
| Farmers               |     60 |
| Farms                 |     75 |
| Vehicles              |     12 |
| Drivers               |     12 |
| TBS price quotations  |     20 |
| Trade contracts       |      8 |
| TBS receipts          |     80 |
| Delivery orders       |     18 |
| Mill weighing tickets |     12 |
| Reconciliation cases  |     10 |

Jumlah boleh disesuaikan untuk memenuhi invariants dan skenario bisnis resmi.

Lengkapi juga:

- Parties.
- Cooperative memberships.
- Price categories.
- Price sources.
- Disbun reference prices.
- Quota periods.
- Quota reservations.
- Receipt weighing revisions.
- Grading items.
- Delivery lines.
- Delivery status events.
- Mill grading items.
- Dispute reviews.
- Farmer settlement allocation simulations.
- Invoice drafts dan status yang sah.
- Payment approval examples.
- Payment evidence simulations.
- Public pages.
- Public notices.
- Offices.
- Audit events yang dihasilkan proses sah.
- System rule versions yang sudah sah secara struktur.
- Data dashboard dan reporting yang berasal dari agregasi nyata.

Jangan membuat data keuangan final yang melewati `FIN_POLICY_UNCONFIRMED`.

## 7. CREATE COHERENT BUSINESS STORIES

Jangan menghasilkan setiap tabel secara independen tanpa relasi.

Minimal buat beberapa kelompok transaksi yang saling terhubung.

### Scenario A — Harga TBS

- PKS publik.
- Harga DRAFT.
- Harga PENDING_VERIFICATION.
- Harga VERIFIED.
- Harga PUBLISHED.
- Harga EXPIRED jika sesuai aturan derivasi.

Pastikan portal publik hanya menampilkan data yang boleh dipublikasikan.

### Scenario B — Penerimaan TBS

- Petani memiliki kebun.
- Petani terhubung ke koperasi.
- Koperasi mencatat penerimaan.
- Bruto dan tara konsisten.
- Netto dihitung benar.
- Grading bertanda simulasi.
- Beberapa receipt berstatus DRAFT.
- Beberapa VALIDATED.
- Beberapa ALLOCATED.

### Scenario C — Kontrak & Kuota

- Kontrak terkait dengan PKS dan pihak yang sah.
- Quota periods konsisten.
- Total reserved/consumed tidak melebihi kuota.
- Beberapa transaksi menunjukkan kuota tersedia.
- Beberapa transaksi menunjukkan kondisi hampir penuh.

Pertahankan model bisnis `UNCONFIRMED` untuk skenario yang memang menunggu SOP.

Gunakan data `SIMULATION_ONLY` hanya jika diizinkan kontrak dan backend.

### Scenario D — Pengiriman e-DO

- e-DO terhubung ke koperasi, receipt, armada, driver, PKS, dan kontrak.
- Ada status DRAFT, READY, IN_TRANSIT, ARRIVED, dan RECEIVED sesuai workflow.
- Tidak ada receipt yang teralokasi ganda.
- QR token dan verifikasi harus mengikuti implementasi backend.
- Jangan membuat QR palsu tanpa referensi transaksi.

### Scenario E — Penimbangan PKS & Rekonsiliasi

- Tiket timbang terhubung dengan e-DO yang benar.
- Bruto, tara, dan netto valid.
- Ada kasus rekonsiliasi normal.
- Ada kasus selisih berat.
- Ada kasus DISPUTE_HOLD.
- Toleransi 1,5% tetap bertanda SIMULATION_ONLY.
- Riwayat audit dan rule snapshot konsisten.

### Scenario F — Keuangan Simulasi

- Invoice draft.
- Invoice menunggu verifikasi.
- Payment approval yang sah.
- Bukti bayar sintetis bila workflow mengizinkan.
- APPROVED berbeda dari PAID.
- Data AR/AP dipisahkan.
- Model UNCONFIRMED memblokir finalisasi yang tidak sah.
- Tidak melakukan transfer nyata.
- Jika status pembayaran simulasi tervalidasi dimasukkan, pastikan diperoleh melalui alur backend yang sah dan ditandai sebagai data demo, bukan kejadian perbankan nyata.

### Scenario G — Dashboard

Dashboard harus mengambil data agregat dari tabel-tabel demo.

Tidak boleh hardcode:

- Total tonase.
- Jumlah petani.
- Jumlah e-DO.
- Nilai transaksi.
- Jumlah sengketa.
- Status pembayaran.

Verifikasi perhitungan dashboard terhadap query database.

## 8. DEMO USER ACCOUNTS

Buat akun demo untuk seluruh tujuh peran:

- FARMER.
- COOPERATIVE_OPERATOR.
- PERUMDA_OPERATIONS.
- PERUMDA_FINANCE.
- MILL_OPERATOR.
- DIRECTOR.
- SYSTEM_ADMIN.

Tambahkan akun yang diperlukan untuk:

- Maker / Checker.
- Cross-scope denial.
- Koperasi berbeda.
- PKS berbeda.

Setiap akun harus:

- Memiliki role yang benar.
- Memiliki access scope yang sah.
- Memiliki password Argon2id.
- Aktif.
- Bisa login menggunakan endpoint FastAPI resmi.
- Tidak menggunakan kredensial produksi.

Buat password acak khusus lingkungan lokal dan simpan hanya pada file lokal yang di-gitignore, misalnya:

`backend/.demo-credentials.local.txt`

Tampilkan lokasi file tersebut setelah seeding selesai.

Jangan memasukkan username/password demo ke source code frontend, Git, ataupun dokumentasi publik.

Jangan membuat bypass login.

## 9. SEED SAFETY

Perintah seed default harus aman untuk dijalankan berulang kali.

Aturan:

- Jika belum ada data demo, populate.
- Jika sudah ada data demo, tidak menduplikasi.
- Jangan menimpa data yang telah diubah pengguna secara diam-diam.
- Jangan menghapus data demo secara otomatis.
- Jangan menghapus DB dev/test.
- Jangan menghapus volume.
- Jangan mengubah data produksi.

Jika membutuhkan kemampuan reset demo, sediakan opsi terpisah dengan konfirmasi eksplisit dan pemeriksaan nama database yang ketat.

Seeder harus menolak eksekusi jika target bukan `agroniaga_demo`.

Gunakan transaction handling dan rollback yang benar.

## 10. CREATE ONE-COMMAND LOCAL LAUNCHER

Buat launcher Windows PowerShell yang dapat digunakan pengguna nonteknis.

Target antarmuka perintah:

```powershell
.\scripts\demo-setup.ps1
.\scripts\demo-start.ps1
.\scripts\demo-stop.ps1
```

Nama file boleh disesuaikan jika struktur proyek mempunyai standar yang lebih tepat.

### demo-setup

- Periksa Python `.venv`.
- Periksa Node/npm.
- Periksa PostgreSQL.
- Periksa Redis.
- Verifikasi database demo.
- Pastikan migrasi sesuai HEAD.
- Instal/sinkronkan dependency jika diperlukan.
- Jalankan seeder jika belum ada data.
- Tampilkan ringkasan jumlah record.
- Tampilkan lokasi file kredensial demo.

### demo-start

- Jalankan backend menggunakan konfigurasi demo.
- Jalankan frontend menggunakan `VITE_API_MODE=real`.
- Gunakan port 8000 dan 5173 jika tersedia.
- Verifikasi readiness.
- Verifikasi koneksi API.
- Tampilkan URL aplikasi.
- Tampilkan URL backend health.
- Jangan mematikan proses pengguna lain.
- Tangani error startup dengan pesan yang jelas.
- Pastikan proses dapat dihentikan secara bersih.

### demo-stop

- Hentikan hanya proses yang dibuat oleh demo-start.
- Jangan mematikan PostgreSQL/Redis milik pekerjaan lain.
- Jangan menghapus data.
- Jangan menghentikan aplikasi lain pada port yang sama.

Jangan mengandalkan task ID sementara milik sesi Antigravity sebelumnya.

## 11. REAL API VERIFICATION

Setelah seed berhasil:

1. Jalankan FastAPI.
2. Jalankan React Vite.
3. Buka browser Playwright.
4. Login sebagai tujuh peran.
5. Pastikan halaman membaca record database demo.
6. Pastikan tidak ada MSW.
7. Pastikan request menuju `/api/v1/*`.
8. Pastikan Vite proxy meneruskan request.
9. Periksa status HTTP dan response JSON.
10. Periksa cookie dan CSRF.
11. Periksa access scopes.

Lakukan pengujian paling penting:

**Buat satu record baru melalui UI, lalu cek bahwa record itu benar-benar tersimpan di `agroniaga_demo` dan masih muncul setelah halaman di-refresh.**

Ini adalah bukti integrasi persistensi yang tidak dapat digantikan oleh mock fixture.

Pastikan operasi baru tidak masuk `agroniaga_dev` atau `agroniaga_test`.

## 12. DEMO SMOKE TEST

Minimal periksa:

- Portal publik menampilkan harga TBS.
- Halaman daftar PKS menampilkan PKS demo publik.
- Login tujuh role berhasil.
- Koperasi melihat petani dalam scope-nya.
- Petani tidak melihat data orang lain.
- Operator membuat penerimaan TBS.
- Netto tersimpan dengan benar.
- Operator membuat e-DO sesuai kuota.
- PKS membuka e-DO yang ditujukan kepadanya.
- Tiket timbang tampil.
- Rekonsiliasi tampil.
- Invoice/pembayaran simulasi mengikuti guard.
- Direksi melihat laporan yang berwenang.
- Administrator mengelola pengguna tanpa hak approver.
- Logout mengakhiri sesi.
- Reload browser mempertahankan session selama masih valid.

Jika ada operasi yang diblokir Pending SOP, tampilkan error yang benar; jangan menjadikannya alasan mem-bypass aturan.

## 13. DEVELOPMENT EXPERIENCE

Buat proses development nyaman untuk solo developer.

Hasil yang diharapkan:

- Satu kali setup.
- Satu perintah start.
- Satu perintah stop.
- Tidak perlu mengedit file environment berulang kali.
- Data seed dapat digunakan setelah restart.
- Session/cache memakai Redis demo.
- Tidak ada input UUID teknis di UI yang seharusnya memakai dropdown.
- Tidak ada endpoint mock tersembunyi.
- Dokumentasi menjalankan demo mudah dipahami.

Jangan melakukan redesign UI besar.

Jika menemukan bug yang menghalangi penggunaan demo, perbaiki minimal dan jalankan regresi.

## 14. TESTING & REGRESSION

Jalankan:

- Backend typecheck/lint yang tersedia.
- Backend pytest.
- Frontend TypeScript check.
- Frontend lint.
- Frontend Vitest.
- Frontend build mode real.
- Kontrak K1–K11.
- Demo seeder tests.
- Demo database integrity checks.
- Real API smoke tests.
- Browser Playwright smoke tests.

Jangan menjalankan suite F11.1 destruktif terhadap `agroniaga_demo`.

Gunakan `agroniaga_test` hanya untuk suite otomatis yang memang dirancang melakukan reset, dengan pengamanan target DB eksplisit.

Jika tes demo perlu mengubah data, gunakan record DEMO khusus yang aman dan tidak merusak skenario presentasi.

## 15. EDIT BOUNDARY

Boleh:

- Menambah seeder di backend.
- Menambah scripts setup/start/stop.
- Menambah konfigurasi demo yang gitignored.
- Menambah tests demo.
- Menambah dependensi Faker jika diperlukan.
- Menambah indikator MODE DEMO di frontend.
- Memperbaiki bug integrasi nyata yang ditemukan dan terbukti.
- Memperbarui README setup jika diperlukan.

Jangan mengubah:

- Enam dokumen baseline V1.1.
- Definisi bisnis shared contracts.
- Migrasi lama tanpa kebutuhan dan change management.
- Keputusan SOP.
- Desain FigCraft D5.
- Logika finance security untuk meloloskan seeding.

Jangan menghapus perubahan yang belum di-commit.

## 16. SINGLE CHECKPOINT POLICY

Seluruh catatan perubahan, hasil seed, pengujian, masalah, dan keputusan ditulis pada:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Tambahkan bagian:

`LOCAL-DEMO-01 — Real API + Faker Seed + One-Command Launch`

Jangan membuat file changelog/progress report baru.

Dokumentasi penggunaan dalam README diperbolehkan.

## 17. ACCEPTANCE CRITERIA

Selesaikan pekerjaan sampai semua poin berikut benar-benar diuji:

- [ ] Database `agroniaga_demo` tersedia.
- [ ] Alembic HEAD sesuai.
- [ ] Redis demo `/2` berfungsi.
- [ ] Faker seed berhasil.
- [ ] Seeder aman diulang tanpa duplikasi.
- [ ] Tidak ada foreign-key violation.
- [ ] Data bisnis saling berhubungan.
- [ ] Akun demo dapat login.
- [ ] Frontend mode `real`.
- [ ] MSW tidak berjalan.
- [ ] FE dapat memanggil BE.
- [ ] Semua role melihat data sesuai hak akses.
- [ ] Data tampil dari database demo.
- [ ] Perubahan UI tersimpan ke PostgreSQL.
- [ ] Reload browser membaca kembali record.
- [ ] Dashboard memakai agregasi database.
- [ ] Pending SOP tetap terlindungi.
- [ ] Build dan regresi PASS.
- [ ] Launcher setup/start/stop bekerja.
- [ ] Database dev/test tidak disentuh.
- [ ] Checkpoint diperbarui.

## 18. FINAL OUTPUT

Berikan ringkasan:

1. Status setup local demo.
2. Database dan Redis yang digunakan.
3. Jumlah data seed per tabel penting.
4. Jumlah akun demo.
5. Hasil pengujian login tujuh role.
6. Bukti UI → API → PostgreSQL.
7. Hasil build dan regression.
8. File yang dibuat/diubah.
9. Perintah menjalankan aplikasi.
10. Lokasi kredensial demo.
11. Known limitations.

Gunakan status:

`READY — LOCAL_DEMO_REAL_API_VERIFIED`

Hanya jika integrasi dan seeding telah benar-benar dibuktikan.

Jika belum:

`CONDITIONALLY_READY — LOCAL_DEMO_SETUP_INCOMPLETE`

atau

`BLOCKED — LOCAL_DEMO_ENVIRONMENT`

Jangan mengklaim READY hanya karena halaman Vite dapat dibuka.

**IMPLEMENT THE LOCAL DEMO NOW. DO NOT STOP AT PLANNING.**
