
# APPLICATION FLOW DOCUMENT (AFD)

## SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TANDAN BUAH SEGAR (TBS)

### PERUMDA TUAH SEKATA — UNIT AGRO NIAGA

**Versi:** 1.1 — Application Flow Baseline
**Tanggal:** 10 November 2026
**Status:** Draft Perancangan Alur Aplikasi
**Dokumen Induk:** PRD V1.1 dan TRD V1.1
**Arsitektur Backend:** Modular Monolith — Clean Architecture 4 Layer
**Arsitektur Frontend:** React + TypeScript — Atomic Design
**Lingkup:** Portal Publik dan Portal Internal Unit Agro Niaga
**Metodologi Penelitian:** Design Science Research Methodology (DSRM)

---

# 1. PENDAHULUAN

## 1.1 Tujuan Dokumen

Application Flow Document (AFD) merupakan dokumen yang menjelaskan alur interaksi pengguna, urutan proses aplikasi, perubahan status transaksi, komunikasi antar-modul, serta penanganan kondisi normal dan tidak normal.

AFD berfungsi sebagai penghubung antara kebutuhan produk pada PRD dan implementasi teknis pada TRD, DBD, BSD, serta IPD.

Dokumen ini menetapkan:

1. Struktur navigasi aplikasi.
2. Alur akses Portal Publik dan Portal Internal.
3. Alur autentikasi dan otorisasi.
4. Alur penggunaan berdasarkan peran.
5. Alur operasional delapan modul bisnis.
6. Alur pertukaran data antar-modul.
7. Alur rekonsiliasi timbang dan transaksi pembayaran.
8. State transition untuk transaksi.
9. Alur validasi, konfirmasi, dan persetujuan.
10. Penanganan error dan skenario alternatif.
11. Integrasi frontend dan backend.
12. Kriteria penerimaan setiap alur.

Dokumen ini mendefinisikan perilaku aplikasi, bukan implementasi kode program atau struktur database final.

## 1.2 Prinsip Perancangan Alur

Seluruh alur aplikasi harus memenuhi prinsip berikut:

- Alur sederhana dan mudah dipahami.
- Akses berdasarkan peran dan kewenangan.
- Satu sumber data yang konsisten.
- Meminimalkan input berulang.
- Setiap transaksi memiliki referensi unik.
- Data transaksi dapat ditelusuri dari awal sampai akhir.
- Proses kritis memerlukan verifikasi.
- Perubahan status dilakukan secara terkendali.
- Error ditampilkan dengan pesan yang jelas.
- Transaksi tidak boleh diproses ganda.
- Setiap keputusan bisnis penting dapat diaudit.
- Mendukung penggunaan desktop dan ponsel.
- Tidak mengharuskan login untuk informasi publik.

## 1.3 Ruang Lingkup

AFD mencakup dua lingkungan utama.

**Portal Publik**

Digunakan oleh masyarakat umum tanpa login untuk mendapatkan informasi harga sawit dari beberapa pabrik, lokasi PKS, profil Perumda, informasi kemitraan, dan kontak resmi.

**Portal Internal**

Digunakan oleh petani terdaftar, koperasi, staf Perumda, petugas PKS, Direksi, serta administrator untuk mengelola transaksi TBS.

Sistem tidak menangani operasional unit usaha Listrik dan Gas.

---

# 2. IDENTIFIKASI AKTOR

## 2.1 Daftar Aktor

| Kode   | Aktor                             | Jenis Akses |
| ------ | --------------------------------- | ----------- |
| ACT-01 | Pengunjung Umum                   | Tanpa login |
| ACT-02 | Petani Swadaya                    | Login       |
| ACT-03 | Operator Koperasi                 | Login       |
| ACT-04 | Staf Operasional/Keuangan Perumda | Login       |
| ACT-05 | Petugas PKS                       | Login       |
| ACT-06 | Direksi Perumda                   | Login       |
| ACT-07 | Administrator Sistem              | Login       |

Aktor staf operasional dan staf keuangan berada dalam kategori Perumda, tetapi dapat diberikan izin berbeda sesuai tanggung jawab.

## 2.2 Peran Aktor dalam Alur Utama

**Pengunjung Umum**

Mengakses informasi harga, lokasi pabrik, dan informasi perusahaan.

**Petani Swadaya**

Memantau data panen, penimbangan, dan status pembayaran miliknya.

**Operator Koperasi**

Mencatat penerimaan buah, melakukan penimbangan, grading, serta menyiapkan pengiriman.

**Staf Perumda**

Mengelola harga, kontrak, kuota, pemilihan PKS, rekonsiliasi, dan administrasi transaksi.

**Petugas PKS**

Memvalidasi pengiriman, memasukkan hasil penimbangan pabrik, dan mencatat grading.

**Direksi Perumda**

Mengawasi kinerja dan melakukan persetujuan berdasarkan batas kewenangan.

**Administrator**

Mengelola akun, hak akses, konfigurasi, dan pemantauan teknis.

---

# 3. INFORMATION ARCHITECTURE

## 3.1 Struktur Portal Publik

Beranda

- Ringkasan informasi Agro Niaga.
- Ringkasan harga TBS terbaru.
- Akses cepat lokasi PKS.
- Informasi Perumda.

Harga TBS

- Daftar harga multi-PKS.
- Harga acuan Disbun.
- Filter dan pencarian.
- Perbandingan harga.
- Detail harga.
- Riwayat harga.

Lokasi PKS

- Daftar PKS.
- Peta lokasi.
- Detail perusahaan.
- Alamat dan kontak publik.
- Tautan navigasi.

Tentang Perumda

- Profil Perumda.
- Informasi unit Agro Niaga.
- Informasi layanan.

Kemitraan

- Informasi kerja sama.
- Persyaratan yang dipublikasikan.
- Kontak kemitraan.

Kontak

- Informasi kontak resmi.
- Lokasi kantor.

Login

- Akses ke Portal Internal.

## 3.2 Struktur Portal Internal

Setelah autentikasi berhasil, pengguna diarahkan ke dashboard sesuai perannya.

### Petani

- Dashboard Saya.
- Harga TBS.
- Lokasi PKS.
- Profil Kebun.
- Riwayat Panen.
- Hasil Timbang.
- Status Pembayaran.
- Profil Akun.

### Operator Koperasi

- Dashboard.
- Data Petani.
- Penerimaan TBS.
- Penimbangan.
- Grading.
- Surat Jalan.
- Status Pengiriman.
- Riwayat Transaksi.

### Staf Perumda

- Dashboard Operasional.
- Data Master.
- Harga Multi-PKS.
- Verifikasi Harga.
- Kontrak dan Kuota.
- Penerimaan TBS.
- Logistik.
- Tiket PKS.
- Rekonsiliasi.
- Faktur dan Pembayaran.
- Laporan.

### Petugas PKS

- Dashboard Penerimaan.
- Daftar Pengiriman.
- Verifikasi e-DO.
- Tiket Timbang.
- Grading PKS.
- Riwayat Penerimaan.

### Direksi

- Dashboard Eksekutif.
- Monitoring Harga.
- Monitoring Pasokan.
- Kinerja Koperasi.
- Kinerja PKS.
- Rekonsiliasi.
- Monitoring Keuangan.
- Persetujuan.
- Laporan.

### Administrator

- Dashboard Administrasi.
- Manajemen Pengguna.
- Hak Akses.
- Konfigurasi Sistem.
- Audit Aktivitas.
- Monitoring Teknis.

## 3.3 Aturan Navigasi

1. Halaman publik dapat diakses tanpa autentikasi.
2. Halaman internal membutuhkan sesi yang sah.
3. Pengguna tanpa izin tidak boleh mengakses halaman internal tertentu.
4. Menu yang ditampilkan mengikuti hak akses pengguna.
5. Penyembunyian menu tidak menggantikan otorisasi backend.
6. Setiap halaman harus menyediakan navigasi kembali.
7. Perpindahan halaman tidak boleh menghilangkan transaksi yang sudah tersimpan.
8. Formulir dengan perubahan belum disimpan harus memberikan peringatan sebelum pengguna meninggalkan halaman.
9. Kondisi memuat, kosong, gagal, dan berhasil harus ditampilkan dengan jelas.
10. Perubahan status bisnis tidak dilakukan hanya karena pengguna membuka halaman.

---

# 4. FLOW-01 — AKSES PORTAL PUBLIK

## 4.1 Tujuan

Memungkinkan masyarakat melihat informasi Agro Niaga tanpa login.

## 4.2 Aktor

Pengunjung Umum.

## 4.3 Prasyarat

Website dapat diakses.

## 4.4 Alur Utama

1. Pengunjung membuka alamat website.
2. Sistem menampilkan halaman Beranda.
3. Pengunjung melihat informasi umum.
4. Pengunjung memilih fitur yang dibutuhkan.
5. Sistem mengambil data publik dari backend.
6. Backend mengambil data melalui cache atau database.
7. Backend mengembalikan data yang diizinkan untuk publik.
8. Frontend menampilkan informasi.

**Alur ringkas:**

Pengunjung → Beranda → Pilih Menu → Public API → Data Publik → Tampilan Informasi.

## 4.5 Kondisi Alternatif

**Data tidak tersedia**

Sistem menampilkan pesan:

"Informasi belum tersedia."

**Server tidak dapat dihubungi**

Sistem menampilkan halaman kesalahan dengan opsi mencoba kembali.

**Informasi telah kedaluwarsa**

Sistem menampilkan status pembaruan data dan tidak menyajikan harga tersebut sebagai harga terbaru.

## 4.6 Kriteria Penerimaan

- Beranda dapat dibuka tanpa login.
- Menu publik dapat digunakan.
- Data pribadi tidak tampil.
- API internal tidak dapat diakses secara anonim.
- Kondisi tanpa data ditangani dengan benar.

---

# 5. FLOW-02 — INFORMASI HARGA TBS MULTI-PKS

## 5.1 Tujuan

Memungkinkan masyarakat dan pengguna internal melihat serta membandingkan harga pembelian TBS dari beberapa PKS.

## 5.2 Aktor

- Pengunjung Umum.
- Petani.
- Koperasi.
- Staf Perumda.
- Direksi.

## 5.3 Alur Utama

1. Pengguna memilih menu Harga TBS.
2. Frontend meminta data harga publik.
3. Backend memeriksa cache harga.
4. Jika cache valid, data diambil dari Redis.
5. Jika cache tidak tersedia atau kedaluwarsa, data diambil dari PostgreSQL.
6. Backend menyaring harga yang telah disetujui untuk publikasi.
7. Sistem mengembalikan daftar harga beserta sumber dan periode.
8. Frontend menampilkan daftar harga.
9. Pengguna memilih filter atau pengurutan.
10. Sistem memperbarui daftar berdasarkan kriteria.
11. Pengguna memilih salah satu PKS.
12. Sistem membuka halaman detail harga dan informasi PKS.

## 5.4 Informasi yang Ditampilkan

- Nama PKS.
- Lokasi atau wilayah.
- Harga per kilogram.
- Kategori harga.
- Tanggal mulai berlaku.
- Tanggal akhir berlaku jika ada.
- Tanggal pembaruan.
- Sumber harga.
- Status kesegaran data.

## 5.5 Alur Perbandingan

Pengguna dapat memilih:

- Harga tertinggi.
- Harga terendah.
- Nama PKS.
- Wilayah.
- Periode berlaku.

Sistem hanya membandingkan harga dengan kategori yang sebanding.

Harga dengan syarat pembelian berbeda harus diberi keterangan yang jelas.

## 5.6 Aturan Penting

Harga tertinggi tidak otomatis ditetapkan sebagai pabrik tujuan pengiriman.

Pemilihan tujuan pengiriman merupakan proses bisnis internal yang juga mempertimbangkan kontrak, kuota, dan biaya operasional.

## 5.7 Kondisi Alternatif

- Tidak ada PKS dengan harga aktif.
- Harga belum diverifikasi.
- Harga kedaluwarsa.
- PKS tidak memiliki informasi harga terbaru.
- Cache Redis gagal.
- Backend gagal mengambil data.

Dalam kondisi kegagalan Redis, sistem dapat membaca PostgreSQL sesuai mekanisme fallback yang aman.

## 5.8 Kriteria Penerimaan

- Daftar harga tampil tanpa login.
- Data berasal dari catatan terverifikasi.
- Harga acuan Disbun tidak dicampur dengan harga PKS.
- Filter dan sorting bekerja.
- Riwayat harga tetap tersedia.
- Tanggal pembaruan terlihat.

---

# 6. FLOW-03 — PETA LOKASI PERUSAHAAN DAN PKS

## 6.1 Tujuan

Memudahkan pengguna mengetahui lokasi kantor Perumda serta perusahaan/PKS mitra yang informasinya dipublikasikan.

## 6.2 Alur Utama

1. Pengguna membuka menu Lokasi PKS.
2. Frontend meminta daftar lokasi publik.
3. Backend mengambil data PKS.
4. Backend hanya mengembalikan profil dan koordinat yang diizinkan dipublikasikan.
5. Frontend menampilkan daftar PKS.
6. Jika koordinat tersedia, frontend menampilkan marker pada peta.
7. Pengguna memilih marker atau item daftar.
8. Sistem menampilkan detail PKS.
9. Pengguna dapat memilih buka navigasi.
10. Browser membuka layanan navigasi berdasarkan koordinat atau alamat yang tersedia.

## 6.3 Informasi Detail

- Nama perusahaan.
- Nama PKS.
- Alamat.
- Wilayah.
- Koordinat jika tersedia.
- Kontak publik jika tersedia.
- Informasi harga terbaru jika tersedia.
- Tautan navigasi.

## 6.4 Kondisi Alternatif

**Koordinat tidak tersedia**

Sistem menampilkan alamat tanpa menambahkan titik peta palsu.

**Peta gagal dimuat**

Sistem tetap menampilkan daftar lokasi dan alamat.

**Harga PKS tidak tersedia**

Sistem menampilkan informasi lokasi tanpa menciptakan harga.

## 6.5 Kriteria Penerimaan

- Peta dan daftar lokasi saling terhubung.
- Marker menggunakan koordinat yang benar.
- Pengguna dapat melihat detail PKS.
- Tidak diperlukan login.
- Fallback daftar lokasi tetap tersedia apabila peta gagal.

---

# 7. FLOW-04 — LOGIN DAN MANAJEMEN SESI

## 7.1 Tujuan

Memastikan hanya pengguna terdaftar yang dapat mengakses Portal Internal.

## 7.2 Alur Login Berhasil

1. Pengguna membuka halaman Login.
2. Pengguna memasukkan kredensial.
3. Frontend melakukan validasi format awal.
4. Frontend mengirim request autentikasi.
5. Backend memeriksa kredensial.
6. Backend memeriksa status akun.
7. Jika valid, server membuat sesi baru.
8. Session identifier disampaikan melalui cookie aman.
9. Sistem mencatat aktivitas login.
10. Frontend mengambil informasi pengguna dan hak akses.
11. Pengguna diarahkan ke dashboard sesuai peran.

## 7.3 Alur Login Gagal

Jika kredensial tidak valid:

1. Backend menolak autentikasi.
2. Sistem mencatat kejadian login gagal secara aman.
3. Frontend menampilkan pesan umum.
4. Pengguna dapat mencoba kembali sesuai kebijakan pembatasan percobaan.

Pesan yang ditampilkan:

"Username atau kata sandi tidak sesuai."

Sistem tidak mengungkap apakah username tertentu terdaftar.

## 7.4 Alur Pengguna Belum Login

1. Pengguna membuka URL internal.
2. Frontend meminta atau memverifikasi status sesi.
3. Backend menyatakan tidak terautentikasi.
4. Sistem mengarahkan pengguna ke halaman Login.
5. Setelah login berhasil, pengguna hanya dikembalikan ke halaman tujuan jika halaman tersebut valid dan diizinkan.

## 7.5 Alur Akses Ditolak

1. Pengguna berhasil login.
2. Pengguna mencoba membuka resource di luar kewenangan.
3. Backend memeriksa role dan scope.
4. Backend mengembalikan HTTP 403.
5. Frontend menampilkan halaman akses ditolak.

Pesan:

"Anda tidak memiliki izin untuk mengakses halaman ini."

## 7.6 Alur Sesi Kedaluwarsa

1. Pengguna melakukan operasi.
2. Backend mendeteksi sesi tidak valid atau kedaluwarsa.
3. Backend mengembalikan HTTP 401.
4. Frontend menghentikan akses data privat.
5. Pengguna diarahkan untuk login kembali.
6. Mutasi yang gagal tidak otomatis dikirim ulang tanpa memastikan status sebelumnya.

## 7.7 Alur Logout

1. Pengguna memilih Logout.
2. Sistem meminta konfirmasi jika diperlukan.
3. Frontend mengirim request logout.
4. Backend mencabut sesi.
5. Cookie sesi dihapus atau dinonaktifkan.
6. Cache data privat pada frontend dibersihkan.
7. Pengguna diarahkan ke Portal Publik atau Login.

---

# 8. FLOW-05 — MASTER DATA PETANI DAN KEBUN

## 8.1 Tujuan

Menyediakan data petani dan kebun sebagai identitas sumber pasokan TBS.

## 8.2 Aktor

- Operator Koperasi.
- Staf Perumda.
- Administrator sesuai kewenangan.

## 8.3 Alur Penambahan Petani

1. Operator membuka Data Petani.
2. Operator memilih Tambah Petani.
3. Sistem menampilkan formulir.
4. Operator mengisi informasi wajib.
5. Operator memilih koperasi terkait.
6. Frontend memvalidasi kelengkapan formulir.
7. Backend memvalidasi kewenangan.
8. Backend memeriksa potensi duplikasi.
9. Jika valid, data disimpan.
10. Sistem menghasilkan ID petani.
11. Audit aktivitas dicatat.
12. Sistem menampilkan detail petani.

## 8.4 Alur Penambahan Kebun

1. Operator memilih petani.
2. Operator membuka Profil Kebun.
3. Operator menambahkan kebun.
4. Sistem menerima informasi lokasi, luas, umur tanaman, dan STDB jika tersedia.
5. Backend memeriksa validitas.
6. Kebun dihubungkan dengan pemiliknya.
7. Sistem menyimpan data.
8. Riwayat perubahan dicatat.

## 8.5 Alur Perubahan Data

1. Petugas membuka detail.
2. Petugas memilih Edit.
3. Sistem memeriksa hak akses.
4. Petugas mengubah data.
5. Sistem memvalidasi.
6. Perubahan disimpan.
7. Riwayat perubahan dicatat.

## 8.6 Kondisi Alternatif

- Data wajib belum lengkap.
- Referensi identitas telah digunakan.
- Petugas tidak memiliki hak akses.
- Petani terkait sudah nonaktif.
- Data kebun sedang digunakan dalam transaksi.
- Dua petugas memperbarui data yang sama.

Untuk konflik perubahan bersamaan, sistem harus mendeteksi konflik versi atau menggunakan strategi konsistensi yang ditetapkan.

## 8.7 Kriteria Penerimaan

- ID petani unik.
- Petani terhubung dengan koperasi yang benar.
- Kebun terhubung dengan pemilik.
- Data dari koperasi berbeda tidak dapat diakses sembarangan.
- Riwayat transaksi lama tidak hilang akibat perubahan master data.

---

# 9. FLOW-06 — MASTER DATA PKS

## 9.1 Tujuan

Menyimpan identitas perusahaan dan lokasi PKS mitra.

## 9.2 Alur Utama

1. Staf Perumda membuka menu Data PKS.
2. Petugas memilih Tambah PKS.
3. Sistem menampilkan formulir.
4. Petugas memasukkan identitas perusahaan dan pabrik.
5. Petugas memasukkan alamat.
6. Petugas dapat memilih atau memasukkan koordinat yang telah diverifikasi.
7. Petugas menentukan status kerja sama.
8. Petugas menentukan bagian informasi yang boleh dipublikasikan.
9. Backend memvalidasi data.
10. Data disimpan.
11. Sistem memperbarui daftar PKS.
12. Cache direktori publik yang relevan diinvalidasi setelah commit.

## 9.3 Alur Publikasi Profil PKS

1. Petugas membuka detail PKS.
2. Petugas memeriksa data yang dapat dipublikasikan.
3. Petugas berwenang menyetujui publikasi.
4. Sistem mengubah status publikasi.
5. Portal Publik menampilkan data yang diizinkan.

## 9.4 Aturan

Status PKS aktif secara internal tidak otomatis berarti seluruh informasinya boleh dipublikasikan.

Data kontrak dan informasi bisnis rahasia tidak ditampilkan pada portal umum.

---

# 10. FLOW-07 — INPUT, VERIFIKASI, DAN PUBLIKASI HARGA

## 10.1 Tujuan

Menjamin pembaruan harga TBS dapat diketahui masyarakat tanpa mengorbankan validitas informasi.

## 10.2 Aktor

- Staf Perumda penginput.
- Petugas verifikator berwenang.
- Pengunjung Portal Publik sebagai pembaca.

## 10.3 Alur Input Harga

1. Petugas login.
2. Petugas membuka Harga Multi-PKS.
3. Petugas memilih Tambah Harga.
4. Sistem menampilkan formulir.
5. Petugas memilih PKS.
6. Petugas memasukkan nominal.
7. Petugas menentukan kategori dan dasar harga.
8. Petugas memasukkan periode berlaku.
9. Petugas memasukkan sumber informasi.
10. Petugas dapat melampirkan bukti.
11. Sistem memvalidasi input.
12. Harga disimpan berstatus Draft.

## 10.4 Alur Pengajuan Verifikasi

1. Petugas membuka harga Draft.
2. Petugas memeriksa data.
3. Petugas memilih Ajukan Verifikasi.
4. Backend memeriksa kelengkapan dan status.
5. Status menjadi Menunggu Verifikasi.
6. Harga masuk antrean verifikator.

## 10.5 Alur Persetujuan

1. Verifikator membuka antrean.
2. Sistem menampilkan informasi harga.
3. Verifikator memeriksa sumber, periode, dan nominal.
4. Verifikator memilih Setujui atau Tolak.
5. Backend memvalidasi kewenangan.
6. Jika disetujui, status menjadi Terverifikasi.
7. Harga dapat dipublikasikan sesuai periode berlaku.
8. Jika ditolak, alasan penolakan dicatat.
9. Perubahan dicatat dalam audit.

## 10.6 Alur Publikasi

1. Harga sudah terverifikasi.
2. Sistem memeriksa periode berlaku.
3. Harga dipublikasikan jika memenuhi syarat.
4. Riwayat harga terdahulu tetap disimpan.
5. Cache harga publik diperbarui atau diinvalidasi setelah commit.
6. Portal Publik menampilkan data yang sesuai.

## 10.7 Aturan Versi Harga

Setiap perubahan harga harus menghasilkan riwayat yang dapat ditelusuri.

Harga yang sudah dipakai sebagai dasar transaksi tidak berubah secara retrospektif.

Transaksi menyimpan referensi dan nilai harga yang disepakati pada saat transaksi dibuat atau disahkan.

## 10.8 Kondisi Alternatif

- Harga negatif.
- Harga tanpa sumber.
- Periode tidak valid.
- Harga bertumpang tindih untuk kategori yang sama dan belum memiliki aturan penyelesaian.
- PKS tidak aktif.
- Verifikator tidak berwenang.
- Informasi ditolak.
- Periode harga belum dimulai.
- Harga sudah kedaluwarsa.

## 10.9 Kriteria Penerimaan

- Harga dapat diajukan.
- Harga dapat disetujui atau ditolak.
- Hanya harga memenuhi syarat yang dipublikasikan.
- Perubahan harga tidak mengubah transaksi lama.
- Riwayat harga dapat ditelusuri.
- Status publikasi konsisten dengan periode berlaku.

---

# 11. FLOW-08 — PENERIMAAN TBS DARI PETANI

## 11.1 Tujuan

Mencatat penyerahan hasil panen petani melalui koperasi.

## 11.2 Aktor

Operator Koperasi.

## 11.3 Prasyarat

- Pengguna telah login.
- Koperasi memiliki izin operasional.
- Petani telah terdaftar.
- Informasi sumber kebun tersedia sesuai kebijakan.

## 11.4 Alur Utama

1. Operator membuka menu Penerimaan TBS.
2. Operator memilih Tambah Penerimaan.
3. Sistem menampilkan formulir.
4. Operator memilih petani.
5. Operator memilih kebun asal.
6. Operator memasukkan tanggal panen atau penerimaan.
7. Operator memasukkan informasi buah.
8. Operator menyimpan Draft.
9. Sistem melakukan validasi.
10. Operator memeriksa ulang data.
11. Operator mengonfirmasi penerimaan.
12. Backend menyimpan transaksi yang telah divalidasi.
13. Sistem menghasilkan nomor penerimaan unik.
14. Transaksi masuk daftar yang dapat diproses untuk penimbangan atau alokasi berikutnya.

## 11.5 Alur Koreksi

Sebelum transaksi disahkan, operator dapat memperbaiki informasi sesuai kewenangan.

Setelah transaksi disahkan, perubahan memerlukan proses koreksi yang mencatat:

- Petugas.
- Waktu.
- Data yang dikoreksi.
- Alasan.
- Persetujuan bila diperlukan.

## 11.6 Kondisi Alternatif

- Petani tidak ditemukan.
- Petani tidak berada dalam cakupan koperasi.
- Data kebun tidak valid.
- Transaksi terduplikasi.
- Operator tidak memiliki izin.
- Request gagal karena koneksi.
- Transaksi sudah masuk pengiriman.

## 11.7 Kriteria Penerimaan

- Transaksi memiliki nomor unik.
- Petani dan koperasi tercatat benar.
- Transaksi dapat ditemukan melalui pencarian.
- Pengguna tidak dapat mengakses transaksi di luar cakupannya.
- Request berulang tidak menghasilkan transaksi ganda apabila menggunakan idempotency key yang sama.

---

# 12. FLOW-09 — PENIMBANGAN DAN GRADING KOPERASI

## 12.1 Tujuan

Mencatat berat dan mutu TBS sebelum pengiriman.

## 12.2 Alur Penimbangan

1. Operator membuka transaksi penerimaan.
2. Operator memilih menu Penimbangan.
3. Operator memasukkan berat bruto.
4. Operator memasukkan berat tara.
5. Frontend menampilkan estimasi netto.
6. Backend memvalidasi nilai berat.
7. Backend menghitung netto secara otoritatif.
8. Operator memeriksa hasil.
9. Data penimbangan disimpan.
10. Sistem mencatat identitas petugas dan waktu.

## 12.3 Rumus

Berat Netto = Berat Bruto − Berat Tara.

Hasil akhir tidak boleh negatif.

Perhitungan menggunakan tipe numerik presisi sesuai ketentuan DBD.

## 12.4 Alur Grading

1. Operator membuka tab Grading.
2. Operator memasukkan kategori hasil sortasi.
3. Sistem mengambil aturan grading yang berlaku.
4. Sistem menghitung potongan sesuai dasar perhitungan.
5. Operator memeriksa hasil.
6. Operator menyimpan data.
7. Sistem menyimpan berat serta potongan sebagai komponen berbeda.

## 12.5 Aturan Penting

Berat netto hasil timbangan dan berat setelah potongan mutu tidak boleh dicampur.

Sistem harus menyimpan nilai dasar serta rincian potongan agar tidak terjadi pemotongan ganda.

## 12.6 Kondisi Alternatif

- Bruto bernilai negatif.
- Tara lebih besar dari bruto.
- Input melebihi batas alat yang dikonfigurasi.
- Potongan grading tidak valid.
- Data belum lengkap.
- Transaksi sudah terkunci setelah pengiriman.

## 12.7 Kriteria Penerimaan

- Netto dihitung dengan benar.
- Validasi server diterapkan.
- Perhitungan grading dapat ditelusuri.
- Hasil akhir konsisten.
- Riwayat koreksi tersedia.

---

# 13. FLOW-10 — KONTRAK DAN KUOTA PKS

## 13.1 Tujuan

Mengelola hubungan perdagangan dan kapasitas pasokan untuk setiap PKS.

## 13.2 Alur Membuat Kontrak

1. Staf Perumda membuka Kontrak Niaga.
2. Staf memilih Tambah Kontrak.
3. Sistem menampilkan formulir.
4. Staf memilih PKS.
5. Staf memasukkan nomor kontrak.
6. Staf memasukkan periode berlaku.
7. Staf memasukkan ketentuan harga.
8. Staf memasukkan kuota pasokan.
9. Staf memasukkan ketentuan transaksi lain yang relevan.
10. Sistem memvalidasi.
11. Kontrak disimpan.
12. Kontrak diaktifkan berdasarkan persetujuan yang berlaku.

## 13.3 Alur Monitoring Kuota

1. Staf membuka detail kontrak.
2. Sistem mengambil data alokasi.
3. Sistem menghitung kuota tersedia.
4. Sistem menampilkan kuota total, teralokasi, diterima, dan tersisa.

## 13.4 Alur Reservasi Kuota

Ketika e-DO disahkan:

1. Sistem memeriksa kontrak aktif.
2. Sistem memeriksa kuota tersedia.
3. Sistem memeriksa muatan.
4. Sistem mengunci atau mengendalikan perubahan kuota secara transaksional.
5. Sistem mencatat reservasi kuota.
6. e-DO dapat disahkan jika seluruh pemeriksaan berhasil.

Saat pengiriman dibatalkan dengan sah, reservasi yang belum dikonsumsi dilepaskan.

Saat penerimaan PKS disahkan, reservasi dikonversi menjadi penggunaan kuota sesuai aturan kontrak.

## 13.5 Kondisi Alternatif

- Kontrak kedaluwarsa.
- PKS tidak sesuai kontrak.
- Kuota tidak mencukupi.
- Kontrak belum disetujui.
- Dua pengguna mencoba menggunakan sisa kuota yang sama.
- Pengiriman dibatalkan.

## 13.6 Kriteria Penerimaan

- Kontrak tidak aktif ditolak untuk transaksi baru.
- Kuota tidak teralokasi melebihi batas.
- Race condition tidak menciptakan reservasi ganda.
- Pembatalan mengikuti kebijakan pelepasan kuota.
- Seluruh perubahan kuota dapat ditelusuri.

---

# 14. FLOW-11 — PENENTUAN PKS TUJUAN

## 14.1 Tujuan

Membantu staf Perumda menentukan PKS tujuan berdasarkan informasi bisnis yang tersedia.

## 14.2 Alur Utama

1. Staf membuka daftar muatan siap kirim.
2. Staf memilih kumpulan penerimaan TBS.
3. Sistem menghitung total berat.
4. Sistem menampilkan daftar PKS yang dapat dipilih.
5. Sistem menampilkan kontrak aktif dan kuota yang tersedia.
6. Sistem menampilkan harga serta lokasi jika tersedia.
7. Staf mempertimbangkan pilihan.
8. Staf memilih PKS tujuan.
9. Sistem memvalidasi kesesuaian kontrak.
10. Pilihan disimpan sebagai bagian dari Draft pengiriman.

## 14.3 Informasi Pendukung

- Nama PKS.
- Harga yang berlaku menurut sumbernya.
- Kontrak aktif.
- Kuota.
- Lokasi.
- Ketentuan mutu.
- Perkiraan biaya operasional jika tersedia.

## 14.4 Aturan

Sistem tidak otomatis memilih PKS dengan harga tertinggi.

Sistem dapat memberikan perbandingan, tetapi keputusan akhir tetap menjadi tanggung jawab petugas berwenang.

Fitur optimasi tujuan pengiriman tidak termasuk kewajiban MVP.

---

# 15. FLOW-12 — PEMBUATAN SURAT JALAN ELEKTRONIK (e-DO)

## 15.1 Tujuan

Mendokumentasikan pengiriman TBS dari koperasi menuju PKS.

## 15.2 Aktor

Operator Koperasi atau Staf Perumda sesuai SOP yang disahkan.

## 15.3 Prasyarat

- Penerimaan TBS valid.
- Data penimbangan tersedia.
- Muatan belum dialokasikan ke pengiriman aktif.
- PKS tujuan ditentukan.
- Kontrak memenuhi persyaratan.
- Kuota mencukupi.

## 15.4 Alur Utama

1. Petugas membuka menu Surat Jalan.
2. Petugas memilih Buat e-DO.
3. Sistem menampilkan daftar penerimaan siap kirim.
4. Petugas memilih satu atau beberapa transaksi penerimaan.
5. Sistem menghitung total muatan.
6. Petugas memilih PKS tujuan.
7. Petugas memilih kendaraan.
8. Petugas memilih atau memasukkan sopir.
9. Sistem memeriksa kontrak dan kuota.
10. Sistem menyimpan Draft e-DO.
11. Petugas memeriksa ringkasan.
12. Petugas memilih Terbitkan.
13. Backend memeriksa kembali seluruh persyaratan dalam transaksi yang aman.
14. Backend melakukan reservasi kuota.
15. Backend mengunci alokasi muatan.
16. Backend menghasilkan nomor e-DO.
17. Sistem menghasilkan QR Code atau kode verifikasi.
18. Status e-DO menjadi Siap Dikirim.
19. Audit penerbitan dicatat.

## 15.5 Konsolidasi Muatan

Satu e-DO dapat berisi beberapa transaksi penerimaan.

Contoh simulasi:

- Penerimaan Petani A: 2.000 kg.
- Penerimaan Petani B: 3.000 kg.
- Penerimaan Petani C: 5.000 kg.

Total muatan: 10.000 kg.

Masing-masing penerimaan tetap memiliki identitas dan hubungan dengan petani asal.

Pada baseline MVP, satu transaksi penerimaan dialokasikan secara utuh ke satu pengiriman aktif. Pemecahan satu penerimaan menjadi beberapa submuatan memerlukan aturan tambahan dan tidak dilakukan otomatis.

## 15.6 Alur QR Code

1. e-DO diterbitkan.
2. Sistem menghasilkan kode referensi unik.
3. QR Code ditampilkan pada dokumen.
4. Petugas PKS memindai atau memasukkan kode.
5. Backend memverifikasi referensi.
6. Sistem mengembalikan informasi sesuai hak akses petugas.

QR Code tidak boleh secara otomatis membuka dokumen rahasia kepada pengguna anonim.

## 15.7 Kondisi Alternatif

- Muatan sudah digunakan.
- Kuota tidak cukup.
- Kontrak tidak aktif.
- Kendaraan tidak valid.
- Data timbang belum lengkap.
- Terjadi permintaan penerbitan ganda.
- Kegagalan menghasilkan dokumen.
- Terjadi konflik saat dua petugas menerbitkan e-DO yang sama.

Jika proses penerbitan gagal sebelum transaksi berhasil, tidak boleh terdapat alokasi muatan atau reservasi kuota yang tertinggal secara tidak konsisten.

## 15.8 Kriteria Penerimaan

- e-DO memiliki nomor unik.
- Satu e-DO dapat memuat beberapa penerimaan.
- Muatan tidak dialokasikan ganda.
- Kuota diperiksa dengan benar.
- QR Code dapat digunakan untuk verifikasi.
- Audit penerbitan tersedia.

---

# 16. FLOW-13 — STATUS PENGIRIMAN TBS

## 16.1 Tujuan

Memantau kemajuan pengiriman berdasarkan pembaruan petugas.

## 16.2 Status Pengiriman

| Status     | Makna                                          |
| ---------- | ---------------------------------------------- |
| DRAFT      | Surat jalan sedang disiapkan                   |
| READY      | Surat jalan sudah diterbitkan dan siap dikirim |
| IN_TRANSIT | Muatan sedang dalam perjalanan                 |
| ARRIVED    | Truk telah tiba di PKS                         |
| RECEIVED   | Penerimaan PKS telah dikonfirmasi              |
| COMPLETED  | Proses operasional pengiriman telah selesai    |
| CANCELLED  | Pengiriman dibatalkan secara sah               |

## 16.3 Alur Normal

DRAFT → READY → IN_TRANSIT → ARRIVED → RECEIVED → COMPLETED.

## 16.4 Alur Perubahan Status

1. Petugas membuka pengiriman.
2. Sistem menampilkan status saat ini.
3. Petugas memilih tindakan yang tersedia.
4. Backend memeriksa peran.
5. Backend memeriksa status awal.
6. Backend memvalidasi persyaratan perpindahan.
7. Status diperbarui.
8. Audit dicatat.
9. Tampilan diperbarui.

## 16.5 Aturan

- Status tidak boleh dilompati secara sembarangan.
- Pengiriman yang sudah selesai tidak dapat dikembalikan menjadi Draft.
- Pembatalan hanya diperbolehkan pada kondisi yang ditetapkan.
- Pengiriman yang sudah diterima PKS tidak boleh dibatalkan melalui proses sederhana.
- Semua koreksi status penting harus diaudit.

## 16.6 Kondisi Alternatif

- Kendaraan mengalami kendala.
- Tujuan pengiriman perlu diubah.
- Pengiriman dibatalkan sebelum tiba.
- Petugas salah mengubah status.
- PKS menolak penerimaan.
- Koneksi internet terputus.

Untuk penolakan atau kendala di lapangan, sistem harus menyediakan pencatatan kejadian dan proses penyelesaian.

Pada baseline, sistem tidak menggunakan GPS real-time.

---

# 17. FLOW-14 — VERIFIKASI e-DO OLEH PKS

## 17.1 Tujuan

Memastikan pengiriman yang datang sesuai surat jalan terdaftar.

## 17.2 Alur Utama

1. Truk tiba di PKS.
2. Petugas PKS login.
3. Petugas membuka Daftar Pengiriman.
4. Petugas memasukkan atau memindai kode e-DO.
5. Backend mencari pengiriman.
6. Backend memeriksa apakah pengiriman ditujukan ke PKS tersebut.
7. Sistem menampilkan data yang relevan.
8. Petugas mencocokkan kendaraan dan dokumen.
9. Petugas mengonfirmasi kedatangan.
10. Status menjadi ARRIVED jika seluruh persyaratan terpenuhi.
11. Aktivitas dicatat.

## 17.3 Kondisi Alternatif

**e-DO tidak ditemukan**

Sistem menolak verifikasi.

**e-DO untuk PKS lain**

Sistem menolak akses atau penerimaan sesuai kewenangan.

**e-DO dibatalkan**

Sistem menampilkan bahwa dokumen tidak berlaku.

**Nomor kendaraan berbeda**

Sistem menandai ketidaksesuaian dan meminta klarifikasi.

**Data tidak sinkron**

Sistem menyediakan referensi kejadian untuk pemeriksaan oleh Perumda.

---

# 18. FLOW-15 — PENCATATAN TIKET TIMBANG PKS

## 18.1 Tujuan

Mencatat hasil penimbangan aktual di pabrik dan menghubungkannya dengan pengiriman.

## 18.2 Alur Utama

1. Petugas PKS membuka pengiriman ARRIVED.
2. Petugas memilih Tambah Tiket Timbang.
3. Sistem menampilkan referensi e-DO.
4. Petugas memasukkan nomor tiket.
5. Petugas memasukkan tanggal dan waktu.
6. Petugas memasukkan berat bruto.
7. Petugas memasukkan berat tara.
8. Sistem menghitung netto.
9. Petugas memasukkan hasil grading.
10. Petugas melampirkan bukti tiket jika tersedia.
11. Sistem melakukan validasi.
12. Petugas memeriksa ringkasan.
13. Tiket disimpan.
14. Tiket menjalani verifikasi sesuai kewenangan.
15. Setelah valid, data tersedia untuk rekonsiliasi.

## 18.3 Hubungan Tiket dan e-DO

Baseline MVP menggunakan satu tiket timbang final yang sah untuk satu e-DO.

Apabila PKS menghasilkan tiket koreksi, sistem harus menjaga versi dan referensi tiket asli.

Jika satu pengiriman secara operasional membutuhkan beberapa tiket independen, kebutuhan tersebut harus divalidasi dan dirancang secara eksplisit sebelum implementasi.

## 18.4 Kondisi Alternatif

- Nomor tiket duplikat.
- e-DO tidak sesuai.
- Bruto tidak valid.
- Tara melebihi bruto.
- Tiket sudah diverifikasi.
- Dokumen bukti gagal diunggah.
- Pengguna bukan petugas PKS tujuan.

## 18.5 Kriteria Penerimaan

- Tiket terkait e-DO yang benar.
- Netto dihitung benar.
- Nomor tiket memiliki constraint unik sesuai cakupan PKS.
- Bukti dapat ditelusuri.
- Tiket valid menjadi input rekonsiliasi.
- Revisi tiket tidak menghapus riwayat sebelumnya.

---

# 19. FLOW-16 — REKONSILIASI OTOMATIS

## 19.1 Tujuan

Mencocokkan data penimbangan asal dengan hasil timbang pabrik.

## 19.2 Aktor

Staf Perumda yang memiliki izin rekonsiliasi.

## 19.3 Prasyarat

- e-DO valid.
- Tiket timbang PKS telah diverifikasi.
- Data berat tersedia.
- Aturan toleransi tersedia.
- Tidak terdapat rekonsiliasi aktif yang bertentangan untuk referensi yang sama.

## 19.4 Alur Utama

1. Petugas membuka menu Rekonsiliasi.
2. Sistem menampilkan transaksi siap direkonsiliasi.
3. Petugas memilih salah satu transaksi.
4. Backend memeriksa referensi e-DO dan tiket.
5. Backend memeriksa kesesuaian PKS dan identitas transaksi.
6. Backend mengambil berat asal yang menjadi dasar pembanding.
7. Backend mengambil berat PKS dengan dasar yang setara.
8. Backend menghitung selisih berat.
9. Backend menghitung persentase selisih.
10. Backend membaca aturan toleransi yang berlaku.
11. Backend menentukan status hasil.
12. Hasil disimpan.
13. Audit aktivitas dicatat.
14. Frontend menampilkan hasil.

## 19.5 Rumus

Selisih Berat = Berat Asal − Berat PKS.

Persentase Selisih = (Selisih Berat / Berat Asal) × 100%.

Jika berat asal bernilai nol atau dasar perbandingan tidak setara, sistem tidak boleh menjalankan perhitungan normal.

## 19.6 Contoh Transaksi Matched

Data simulasi:

- Berat asal: 10.000 kg.
- Berat PKS: 9.900 kg.
- Selisih: 100 kg.
- Persentase: 1%.

Dengan asumsi toleransi yang disahkan sebesar 1,5%, transaksi dapat dikategorikan Matched.

Status Matched tidak berarti pembayaran otomatis dilakukan.

## 19.7 Contoh Transaksi Dispute

Data simulasi:

- Berat asal: 10.000 kg.
- Berat PKS: 9.600 kg.
- Selisih: 400 kg.
- Persentase: 4%.

Dengan asumsi toleransi 1,5%, sistem memberi status Dispute/Hold.

Transaksi harus diperiksa sebelum penyelesaian.

## 19.8 Selisih Negatif

Jika hasil timbang PKS lebih besar daripada berat asal, sistem harus menandai anomali dan mengikuti mekanisme pemeriksaan.

Selisih negatif tidak diperlakukan sebagai penyusutan normal.

## 19.9 Aturan Rekonsiliasi

- Data referensi harus cocok.
- Berat yang dibandingkan harus menggunakan definisi setara.
- Perhitungan dilakukan pada backend.
- Aturan toleransi harus memiliki versi.
- Transaksi bermasalah tidak boleh lolos otomatis.
- Hasil rekonsiliasi harus dapat ditelusuri.
- Rekonsiliasi ulang wajib menggunakan mekanisme koreksi.
- Dua proses bersamaan tidak boleh menghasilkan keputusan final yang saling bertentangan.

## 19.10 Kriteria Penerimaan

- Perhitungan selisih akurat.
- Toleransi diterapkan dengan benar.
- Matched dan Dispute dapat dibedakan.
- Anomali selisih negatif ditangani.
- Data koreksi tetap memiliki riwayat.
- Rekonsiliasi tidak dapat diproses ganda secara tidak sah.

---

# 20. FLOW-17 — PENANGANAN DISPUTE

## 20.1 Tujuan

Menangani perbedaan hasil penimbangan yang memerlukan pemeriksaan manusia.

## 20.2 Alur Utama

1. Sistem mendeteksi selisih di luar toleransi.
2. Status rekonsiliasi menjadi Dispute/Hold.
3. Transaksi masuk daftar pemeriksaan.
4. Staf Perumda membuka detail.
5. Sistem menampilkan berat asal, berat PKS, selisih, dan dokumen pendukung.
6. Petugas melakukan pemeriksaan.
7. Petugas mencatat hasil klarifikasi.
8. Jika diperlukan, petugas melampirkan bukti.
9. Petugas mengajukan keputusan penyelesaian.
10. Pejabat berwenang meninjau keputusan sesuai SOP.
11. Jika disetujui, sengketa dinyatakan selesai.
12. Berat atau nilai dasar penyelesaian dicatat beserta dasar keputusannya.
13. Sistem memperbarui status.
14. Audit keputusan disimpan.
15. Transaksi dapat dilanjutkan ke proses keuangan jika memenuhi syarat.

## 20.3 Alternatif Hasil Pemeriksaan

- Tidak ditemukan kesalahan; nilai awal disahkan.
- Terdapat koreksi data yang disetujui.
- Dokumen perlu dilengkapi.
- Transaksi dikembalikan untuk verifikasi.
- Sengketa ditahan sampai terdapat keputusan.
- Transaksi dibatalkan atau diselesaikan melalui proses khusus berdasarkan SOP.

## 20.4 Aturan

Sistem hanya membantu mendeteksi perbedaan data.

Sistem tidak boleh menyimpulkan secara otomatis adanya manipulasi atau menentukan pihak yang bersalah berdasarkan persentase selisih saja.

## 20.5 Kriteria Penerimaan

- Transaksi Dispute/Hold tidak otomatis masuk pembayaran final.
- Petugas dapat mencatat hasil pemeriksaan.
- Penyelesaian memiliki alasan dan bukti yang dapat ditelusuri.
- Audit menyimpan identitas pengambil keputusan.
- Riwayat nilai sebelum dan sesudah koreksi tetap tersedia.

---

# 21. FLOW-18 — PERHITUNGAN NILAI TRANSAKSI

## 21.1 Tujuan

Menghitung nilai transaksi berdasarkan berat, harga, dan ketentuan potongan yang disetujui.

## 21.2 Alur Utama

1. Rekonsiliasi telah memenuhi persyaratan.
2. Sistem mengambil nilai berat yang disahkan.
3. Sistem mengambil harga transaksi atau kontrak yang berlaku.
4. Sistem mengambil ketentuan grading.
5. Sistem mengambil biaya atau potongan lain yang disahkan.
6. Sistem menghitung nilai transaksi.
7. Sistem menyusun rincian perhitungan.
8. Staf Perumda memeriksa rincian.
9. Jika terdapat ketidaksesuaian, transaksi dikembalikan untuk pemeriksaan.
10. Jika sesuai, perhitungan dapat dilanjutkan ke dokumen keuangan.

## 21.3 Komponen Perhitungan

Secara konseptual:

Nilai Bruto = Berat Dasar Pembayaran × Harga Berlaku.

Nilai Akhir = Nilai Bruto − Potongan yang Sah ± Penyesuaian yang Disahkan.

Formula sebenarnya harus ditetapkan dalam BSD berdasarkan ketentuan kontrak dan SOP.

## 21.4 Ketentuan

- Harga dan berat dasar harus jelas.
- Potongan tidak boleh diterapkan dua kali.
- Perhitungan harus menggunakan Decimal.
- Sistem menyimpan rincian komponen nilai.
- Pembulatan mengikuti aturan yang disahkan.
- Nilai final tidak boleh diubah tanpa proses koreksi.

## 21.5 Alokasi Hasil Pengiriman Gabungan

Jika satu e-DO memuat buah dari beberapa petani, sistem harus menjaga hubungan transaksi setiap petani.

Pembagian nilai harus mengikuti metode yang disetujui, termasuk penanganan selisih dan potongan.

Sistem tidak boleh membagi selisih atau hasil pembayaran secara otomatis kepada seluruh petani dengan metode yang belum disahkan.

---

# 22. FLOW-19 — FAKTUR DAN PEMBAYARAN

## 22.1 Tujuan

Mencatat kewajiban dan penerimaan pembayaran dalam rantai niaga.

## 22.2 Konsep Aliran Keuangan

Secara konseptual, proposal menggambarkan hubungan finansial antara PKS, Perumda, koperasi, dan petani.

Namun, status pembayaran harus dipisahkan berdasarkan pihak yang membayar serta penerima dana.

Sistem minimal membedakan:

1. Tagihan Perumda kepada PKS atau piutang hasil penjualan.
2. Kewajiban pembayaran Perumda kepada koperasi atau mitra sesuai kontrak.
3. Status pembayaran kepada petani apabila bukti atau konfirmasi tersebut tersedia dan menjadi bagian dari proses yang disepakati.

Pembayaran PKS kepada Perumda tidak otomatis berarti petani sudah menerima pembayaran.

## 22.3 Alur Penerbitan Faktur

1. Transaksi telah memenuhi persyaratan rekonsiliasi.
2. Staf keuangan membuka transaksi.
3. Sistem menampilkan rincian nilai.
4. Staf melakukan pemeriksaan.
5. Sistem menyiapkan Draft faktur.
6. Staf memeriksa pihak penagih dan pihak tertagih.
7. Faktur diajukan untuk verifikasi.
8. Verifikator memeriksa kelengkapan.
9. Faktur diterbitkan atau dikembalikan untuk koreksi.
10. Sistem menyimpan nomor dan riwayat faktur.

## 22.4 Alur Persetujuan Pembayaran

1. Staf keuangan membuka kewajiban pembayaran.
2. Sistem menampilkan nominal dan dokumen terkait.
3. Staf memeriksa kelengkapan.
4. Staf mengajukan persetujuan.
5. Pihak berwenang membuka antrean persetujuan.
6. Pihak berwenang memeriksa transaksi.
7. Persetujuan diberikan atau ditolak.
8. Sistem mencatat keputusan.
9. Status diperbarui.

## 22.5 Alur Pencatatan Pembayaran

1. Transaksi sudah disetujui untuk dibayar.
2. Pembayaran dilakukan melalui prosedur keuangan yang berlaku.
3. Petugas mencatat referensi pembayaran.
4. Petugas melampirkan bukti jika diperlukan.
5. Petugas verifikator memeriksa bukti.
6. Sistem mengubah status pembayaran jika terkonfirmasi.
7. Audit aktivitas disimpan.
8. Informasi status tersedia bagi pengguna yang berhak.

## 22.6 Alur Pembayaran kepada Petani

1. Sistem mengidentifikasi transaksi milik petani.
2. Sistem menampilkan nilai yang terkait dengan petani berdasarkan perhitungan yang disahkan.
3. Sistem membaca status pembayaran pada jalur yang relevan.
4. Jika pembayaran kepada petani belum dibuktikan, status tidak boleh ditampilkan sebagai sudah diterima.
5. Setelah konfirmasi pembayaran yang sah dicatat, petani dapat melihat status tersebut.

## 22.7 Kondisi Alternatif

- Dokumen belum lengkap.
- Rekonsiliasi masih Dispute.
- Faktur ditolak.
- Nominal berbeda.
- Persetujuan belum diberikan.
- Bukti pembayaran belum terverifikasi.
- Request pembayaran duplikat.
- Pembayaran dilakukan sebagian jika kebijakan mendukung.
- Pembayaran perlu dibatalkan atau dikoreksi.

Pada baseline, pembayaran sebagian merupakan kebutuhan bersyarat yang harus dikonfirmasi melalui SOP. Jika tidak termasuk MVP, sistem hanya menerima pencatatan pembayaran penuh.

## 22.8 Kriteria Penerimaan

- Faktur memiliki referensi transaksi.
- Pembayaran hanya diproses setelah memenuhi syarat.
- Persetujuan tercatat.
- Bukti pembayaran dapat ditelusuri.
- Duplikasi pembayaran dicegah.
- Status penerimaan dana dan pembayaran kepada mitra tidak tercampur.
- Petani hanya melihat pembayaran miliknya.

---

# 23. FLOW-20 — DASHBOARD PETANI

## 23.1 Tujuan

Menyediakan informasi sederhana mengenai hasil panen dan pembayaran milik petani.

## 23.2 Alur Utama

1. Petani login.
2. Sistem memvalidasi identitas dan scope.
3. Petani diarahkan ke Dashboard Saya.
4. Backend mengambil data transaksi miliknya.
5. Sistem menampilkan ringkasan panen dan penimbangan.
6. Petani memilih transaksi.
7. Sistem menampilkan detail.
8. Petani dapat melihat status pembayaran yang relevan.

## 23.3 Informasi Dashboard

- Jumlah transaksi panen.
- Berat TBS yang tercatat.
- Riwayat penimbangan.
- Potongan mutu.
- Status transaksi.
- Status pembayaran.
- Informasi harga publik.

## 23.4 Aturan

Petani tidak boleh melihat transaksi petani lain.

Petani tidak dapat mengedit nilai berat yang telah dicatat dan disahkan oleh petugas.

Jika pembayaran belum terverifikasi, sistem menampilkan status sebenarnya.

---

# 24. FLOW-21 — DASHBOARD KOPERASI

## 24.1 Tujuan

Membantu operator koperasi memantau aktivitas penerimaan dan pengiriman.

## 24.2 Informasi Dashboard

- Penerimaan hari ini.
- Total berat masuk.
- Transaksi belum ditimbang.
- Transaksi siap dikirim.
- Pengiriman aktif.
- Pengiriman selesai.
- Transaksi memerlukan pemeriksaan.

## 24.3 Alur Utama

1. Operator login.
2. Sistem menentukan koperasi yang dapat diakses.
3. Dashboard mengambil transaksi dalam cakupan koperasi.
4. Sistem menampilkan ringkasan.
5. Operator memilih kartu atau menu.
6. Sistem membuka daftar transaksi terkait.
7. Operator melanjutkan tugas sesuai hak akses.

---

# 25. FLOW-22 — DASHBOARD OPERASIONAL PERUMDA

## 25.1 Tujuan

Memantau perdagangan TBS pada tingkat operasional.

## 25.2 Informasi Dashboard

- Total tonase penerimaan.
- Pengiriman aktif.
- PKS tujuan.
- Harga terkini.
- Kuota kontrak.
- Tiket timbang menunggu verifikasi.
- Rekonsiliasi Matched.
- Rekonsiliasi Dispute.
- Faktur yang perlu diproses.
- Pembayaran yang menunggu pemeriksaan.

## 25.3 Alur Utama

1. Staf login.
2. Backend memeriksa kewenangan.
3. Dashboard meminta ringkasan data sesuai scope.
4. Sistem mengambil agregasi yang relevan.
5. Frontend menampilkan informasi.
6. Staf memilih indikator.
7. Sistem menampilkan daftar transaksi yang membentuk indikator tersebut.

---

# 26. FLOW-23 — DASHBOARD EKSEKUTIF

## 26.1 Tujuan

Menyediakan ringkasan kinerja Agro Niaga untuk Direksi.

## 26.2 Indikator Utama

- Total tonase berdasarkan periode.
- Nilai transaksi.
- Perbandingan harga PKS.
- Volume pasokan koperasi.
- Volume penerimaan PKS.
- Rekonsiliasi bermasalah.
- Status piutang.
- Status kewajiban pembayaran.
- Margin usaha berdasarkan komponen data yang tersedia.

## 26.3 Alur Utama

1. Direksi login.
2. Sistem memeriksa hak akses.
3. Dashboard mengambil data agregasi.
4. Data ditampilkan dalam grafik dan ringkasan.
5. Direksi memilih periode.
6. Sistem memperbarui informasi.
7. Direksi memilih indikator untuk melihat rincian.
8. Sistem menampilkan informasi sesuai kewenangan.

## 26.4 Aturan

Dashboard tidak boleh menghitung transaksi dibatalkan sebagai transaksi berhasil.

Nilai yang menggunakan data simulasi harus diberi penanda.

Margin kotor tidak boleh diberi label sebagai laba bersih.

Waktu pembaruan data harus terlihat.

---

# 27. FLOW-24 — ADMINISTRATOR SISTEM

## 27.1 Alur Pengelolaan Pengguna

1. Administrator login.
2. Membuka menu Pengguna.
3. Memilih Tambah atau Edit.
4. Memasukkan identitas dan peran.
5. Menetapkan scope organisasi.
6. Sistem memvalidasi.
7. Perubahan disimpan.
8. Audit perubahan hak akses dicatat.

## 27.2 Alur Penonaktifan Akun

1. Administrator memilih akun.
2. Sistem menampilkan status sesi dan hubungan akun.
3. Administrator memilih Nonaktifkan.
4. Sistem meminta konfirmasi.
5. Backend memverifikasi hak akses.
6. Akun dinonaktifkan.
7. Sesi aktif dicabut sesuai kebijakan.
8. Audit dicatat.

## 27.3 Alur Pengubahan Konfigurasi Bisnis

Konfigurasi seperti toleransi timbang hanya dapat diubah oleh pihak berwenang berdasarkan kebijakan resmi.

Perubahan harus memiliki:

- Nilai sebelumnya.
- Nilai baru.
- Tanggal efektif.
- Alasan perubahan.
- Identitas pemberi persetujuan.

Administrator teknis tidak otomatis berwenang mengubah keputusan bisnis keuangan.

## 27.4 Alur Monitoring Error

1. Administrator membuka monitoring teknis.
2. Sistem menampilkan ringkasan error.
3. Administrator memilih kejadian.
4. Sistem menampilkan Request ID dan metadata teknis yang aman.
5. Administrator dapat menelusuri log terkait.
6. Tindak lanjut teknis dilakukan sesuai kewenangan.

---

# 28. STATE TRANSITION — PENERIMAAN TBS

## 28.1 Daftar Status

| Status    | Makna                                                                  |
| --------- | ---------------------------------------------------------------------- |
| DRAFT     | Penerimaan sedang dibuat                                               |
| VALIDATED | Data penerimaan dan timbang telah divalidasi                           |
| ALLOCATED | Penerimaan telah dialokasikan ke pengiriman                            |
| SHIPPED   | Muatan telah diberangkatkan                                            |
| CLOSED    | Proses penerimaan terkait telah ditutup                                |
| CANCELLED | Transaksi dibatalkan sebelum mencapai kondisi yang melarang pembatalan |

## 28.2 Transisi Normal

DRAFT → VALIDATED → ALLOCATED → SHIPPED → CLOSED.

## 28.3 Aturan

- VALIDATED memerlukan data wajib lengkap.
- ALLOCATED memerlukan e-DO yang sah.
- SHIPPED mengikuti keberangkatan pengiriman.
- CLOSED memerlukan penyelesaian operasional terkait.
- Pembatalan hanya diperbolehkan menurut keadaan transaksi dan SOP.
- Koreksi transaksi yang sudah digunakan tidak dilakukan dengan mengembalikan status secara sembarangan.

---

# 29. STATE TRANSITION — HARGA TBS

## 29.1 Daftar Status

- DRAFT.
- PENDING_VERIFICATION.
- VERIFIED.
- REJECTED.
- PUBLISHED.
- EXPIRED.

## 29.2 Alur Normal

DRAFT → PENDING_VERIFICATION → VERIFIED → PUBLISHED → EXPIRED.

## 29.3 Alur Penolakan

PENDING_VERIFICATION → REJECTED.

Setelah penolakan, perubahan dilakukan melalui revisi sesuai aturan.

## 29.4 Aturan

PUBLISHED hanya diperbolehkan setelah verifikasi dan pada periode berlaku yang sesuai.

Harga yang kedaluwarsa tetap berada dalam riwayat.

---

# 30. STATE TRANSITION — REKONSILIASI

## 30.1 Daftar Status

| Status         | Makna                                             |
| -------------- | ------------------------------------------------- |
| WAITING_TICKET | Tiket timbang belum tersedia                      |
| READY          | Data siap diproses                                |
| MATCHED        | Data memenuhi aturan pencocokan                   |
| DISPUTE_HOLD   | Selisih memerlukan pemeriksaan                    |
| UNDER_REVIEW   | Pemeriksaan sedang berjalan                       |
| RESOLVED       | Sengketa telah diselesaikan                       |
| CANCELLED      | Rekonsiliasi dibatalkan melalui prosedur yang sah |

## 30.2 Transisi Normal

WAITING_TICKET → READY → MATCHED.

## 30.3 Transisi Sengketa

WAITING_TICKET → READY → DISPUTE_HOLD → UNDER_REVIEW → RESOLVED.

## 30.4 Aturan

- MATCHED dan RESOLVED merupakan hasil rekonsiliasi yang dapat menjadi prasyarat proses keuangan.
- Keputusan RESOLVED memerlukan alasan dan bukti.
- Perubahan nilai yang sudah disahkan menggunakan mekanisme koreksi terversi.
- Pembayaran tetap mempunyai state tersendiri.

---

# 31. STATE TRANSITION — FAKTUR DAN PEMBAYARAN

## 31.1 Status Faktur

- DRAFT.
- PENDING_VERIFICATION.
- VERIFIED.
- ISSUED.
- REJECTED.
- VOID.

Alur umum:

DRAFT → PENDING_VERIFICATION → VERIFIED → ISSUED.

Faktur yang dibatalkan secara sah masuk status VOID dan tetap memiliki riwayat.

## 31.2 Status Pembayaran

- PENDING_APPROVAL.
- APPROVED.
- REJECTED.
- AWAITING_PAYMENT.
- PENDING_VERIFICATION.
- PAID.
- CANCELLED.

Alur normal pembayaran keluar:

PENDING_APPROVAL → APPROVED → AWAITING_PAYMENT → PENDING_VERIFICATION → PAID.

Alur penolakan:

PENDING_APPROVAL → REJECTED.

## 31.3 Aturan

- Status PAID memerlukan konfirmasi pembayaran yang sah.
- Persetujuan tidak berarti dana telah ditransfer.
- Pembayaran yang gagal atau belum terbukti tidak boleh dinyatakan PAID.
- Pembayaran masuk dari PKS dan pembayaran keluar kepada mitra memiliki pencatatan dan workflow yang berbeda.
- Detail penyelesaian pembayaran masuk akan mengikuti BSD.

---

# 32. INTERAKSI ANTAR-MODUL BACKEND

## 32.1 Prinsip Komunikasi

Backend menggunakan Modular Monolith.

Setiap modul memiliki:

1. Presentation Layer.
2. Application Layer.
3. Domain Layer.
4. Infrastructure Layer.

Frontend tidak mengakses database secara langsung.

## 32.2 Alur Request Dasar

Frontend → API Router → Application Use Case → Domain Rules → Repository Port → Infrastructure Repository → PostgreSQL.

Setelah proses berhasil:

Database Commit → Response Mapping → API Response → Frontend.

## 32.3 Contoh Interaksi Modul Harga

1. Presentation menerima request harga.
2. Application menjalankan use case yang sesuai.
3. Domain memvalidasi aturan harga.
4. Infrastructure membaca atau menulis PostgreSQL.
5. Application mengoordinasikan hasil.
6. Presentation mengembalikan response.

## 32.4 Contoh Interaksi Penerbitan e-DO

Logistics Application berkoordinasi dengan:

- TBS Receiving untuk status dan ketersediaan muatan.
- Contracts untuk kontrak serta reservasi kuota.
- Master Data untuk referensi PKS dan kendaraan.
- Audit untuk pencatatan tindakan penting.

Operasi lintas modul yang memerlukan atomisitas harus dikoordinasikan melalui transaksi yang aman.

Modul tidak boleh mengubah tabel domain lain secara bebas.

## 32.5 Contoh Interaksi Rekonsiliasi

Reconciliation Application menggunakan:

- Data e-DO dari Logistics.
- Data tiket dari Mill Weighing.
- Ketentuan bisnis dari Domain Reconciliation.
- Data harga dan kontrak yang disepakati.
- Repository rekonsiliasi untuk menyimpan hasil.

Pengambilan data melalui port atau kontrak modul yang terdokumentasi.

## 32.6 Observability

Request masuk melalui middleware yang menghasilkan Request ID.

Middleware dapat mencatat durasi request dan informasi route.

Error dicatat dengan identitas yang dapat ditelusuri.

Audit bisnis disimpan saat tindakan penting terjadi.

Logging tidak boleh memuat seluruh data pribadi atau informasi pembayaran secara sembarangan.

---

# 33. ALUR PENANGANAN ERROR GLOBAL

## 33.1 Validation Error

1. Pengguna mengirim formulir.
2. Frontend memeriksa format.
3. Backend tetap memvalidasi seluruh input.
4. Jika tidak valid, backend mengembalikan error terstandar.
5. Frontend menampilkan pesan pada field atau bagian yang relevan.
6. Data yang masih valid tetap dipertahankan pada formulir sejauh aman.

## 33.2 Unauthorized Error

1. Pengguna mengakses resource privat.
2. Sesi tidak valid.
3. Backend mengembalikan 401.
4. Frontend meminta login kembali.

## 33.3 Forbidden Error

1. Pengguna memiliki sesi.
2. Pengguna tidak memiliki izin.
3. Backend mengembalikan 403.
4. Frontend menampilkan Akses Ditolak.

## 33.4 Conflict Error

1. Pengguna memproses transaksi.
2. Backend menemukan konflik state atau data.
3. Backend mengembalikan 409.
4. Frontend menjelaskan konflik.
5. Pengguna diarahkan untuk memuat ulang status terbaru atau melakukan pemeriksaan.

## 33.5 Internal Error

1. Backend mengalami kesalahan tak terduga.
2. Error ditangkap oleh mekanisme penanganan global.
3. Sistem membuat atau mempertahankan Request ID.
4. Informasi teknis dicatat secara aman.
5. Frontend menampilkan pesan umum dan kode referensi.

Contoh:

"Terjadi kendala pada sistem. Silakan coba kembali atau hubungi administrator dengan kode referensi yang ditampilkan."

## 33.6 Network Failure

1. Browser gagal menerima response.
2. Frontend menampilkan informasi koneksi.
3. Pengguna dapat mencoba kembali.
4. Untuk operasi mutasi, sistem perlu memeriksa status transaksi sebelum mengirim ulang.
5. Jika tersedia idempotency key, pengulangan harus menjaga hasil yang konsisten.

---

# 34. ALUR AUDIT DAN MONITORING

## 34.1 HTTP Request Logging

Setiap request relevan dapat dicatat menggunakan:

- Request ID.
- Trace ID.
- Route.
- HTTP method.
- Status.
- Duration.
- Actor ID bila tersedia.
- Timestamp.

## 34.2 Business Audit

Peristiwa bisnis yang diaudit antara lain:

- Publikasi harga.
- Revisi berat.
- Penerbitan e-DO.
- Verifikasi tiket PKS.
- Penyelesaian dispute.
- Persetujuan pembayaran.
- Perubahan hak akses.

## 34.3 Error Investigation Flow

Pengguna mengalami error → Sistem menampilkan Request ID → Administrator mencari log → Administrator mengidentifikasi modul → Masalah dianalisis → Perbaikan dan pengujian dilakukan.

## 34.4 Security Monitoring

Sistem memantau:

- Login gagal.
- Akses tanpa izin.
- Perubahan hak akses.
- Aktivitas administrator.
- Percobaan request berulang yang mencurigakan.
- Perubahan konfigurasi sensitif.

Observability tidak boleh memperlambat transaksi penting secara berlebihan atau membocorkan data.

---

# 35. SKENARIO END-TO-END UTAMA

## 35.1 Skenario E2E-01 — Informasi Publik

**Aktor:** Pengunjung Umum.

1. Membuka Beranda.
2. Membuka Harga TBS.
3. Melihat harga beberapa PKS.
4. Mengurutkan harga.
5. Membuka detail PKS.
6. Melihat lokasi PKS.
7. Membuka navigasi.

**Hasil yang diharapkan:**

Seluruh informasi publik dapat diakses tanpa login dan tidak menampilkan data rahasia.

## 35.2 Skenario E2E-02 — Pembaruan Harga

**Aktor:** Staf Perumda dan Verifikator.

1. Menginput harga PKS.
2. Menyimpan Draft.
3. Mengajukan verifikasi.
4. Memverifikasi harga.
5. Mempublikasikan harga.
6. Memeriksa Portal Publik.

**Hasil yang diharapkan:**

Harga terverifikasi tampil sesuai periode dan riwayatnya tersedia.

## 35.3 Skenario E2E-03 — Transaksi TBS Normal

**Aktor:** Koperasi, Staf Perumda, PKS, dan Keuangan.

1. Memilih petani.
2. Mencatat penerimaan.
3. Menimbang TBS.
4. Mencatat grading.
5. Memilih PKS.
6. Memeriksa kontrak.
7. Menerbitkan e-DO.
8. Memberangkatkan muatan.
9. Memverifikasi kedatangan.
10. Mencatat tiket PKS.
11. Menjalankan rekonsiliasi.
12. Memperoleh status Matched.
13. Menghitung nilai transaksi.
14. Memverifikasi faktur.
15. Menyetujui pembayaran sesuai kewenangan.
16. Mencatat dan memverifikasi bukti pembayaran.
17. Memeriksa dashboard.

**Hasil yang diharapkan:**

Transaksi dapat ditelusuri dari penerimaan sampai penyelesaian finansial yang tercatat.

## 35.4 Skenario E2E-04 — Transaksi Dispute

1. Penerimaan dan pengiriman dibuat.
2. Tiket PKS dimasukkan.
3. Sistem menghitung selisih di luar toleransi.
4. Sistem memberi status Dispute/Hold.
5. Pembayaran final ditahan.
6. Petugas melakukan pemeriksaan.
7. Hasil klarifikasi disimpan.
8. Keputusan disetujui sesuai kewenangan.
9. Rekonsiliasi diselesaikan.
10. Transaksi keuangan dapat dilanjutkan.

**Hasil yang diharapkan:**

Tidak ada pembayaran final yang melewati pemeriksaan sengketa secara tidak sah.

## 35.5 Skenario E2E-05 — Multi-Petani Satu Pengiriman

1. Tiga petani melakukan penyerahan TBS.
2. Sistem mencatat tiga transaksi penerimaan.
3. Operator menggabungkan transaksi dalam satu e-DO.
4. Pengiriman dilakukan.
5. PKS menghasilkan tiket timbang.
6. Sistem merekonsiliasi data pengiriman.
7. Rincian asal muatan tetap dapat ditemukan.
8. Perhitungan hasil tiap petani mengikuti aturan alokasi yang disahkan.

**Hasil yang diharapkan:**

Tidak ada kehilangan identitas sumber panen maupun penghitungan ganda.

## 35.6 Skenario E2E-06 — Akses Tidak Sah

1. Petani A login.
2. Petani A mencoba membuka transaksi Petani B.
3. Backend memeriksa kepemilikan.
4. Backend menolak akses.
5. Sistem mencatat kejadian relevan.

**Hasil yang diharapkan:**

Data pribadi tidak bocor lintas pengguna.

## 35.7 Skenario E2E-07 — Request Ganda

1. Petugas mengirim permintaan membuat e-DO.
2. Koneksi terputus sebelum response diterima.
3. Petugas mencoba kembali.
4. Backend memeriksa idempotency key dan transaksi yang sudah ada.
5. Backend mengembalikan hasil yang konsisten.

**Hasil yang diharapkan:**

Tidak terdapat e-DO ganda atau reservasi kuota ganda akibat pengulangan request yang sama.

## 35.8 Skenario E2E-08 — Harga Berubah Setelah Transaksi

1. Kontrak atau transaksi menggunakan harga yang berlaku.
2. Harga publik diperbarui.
3. Transaksi lama dibuka.
4. Sistem menampilkan harga historis yang telah disepakati.
5. Harga baru hanya diterapkan pada transaksi yang memenuhi aturan periode dan kontrak.

**Hasil yang diharapkan:**

Tidak terjadi perubahan nilai transaksi historis secara otomatis.

## 35.9 Skenario E2E-09 — Redis Tidak Tersedia

1. Pengunjung membuka halaman harga.
2. Redis tidak tersedia.
3. Backend menerapkan mekanisme fallback yang aman.
4. Sistem membaca data dari PostgreSQL apabila layanan masih memungkinkan.
5. Kegagalan Redis tercatat.

**Hasil yang diharapkan:**

Cache tidak menjadi sumber data permanen dan kegagalannya tidak menyebabkan kebocoran data.

---

# 36. RANCANGAN ROUTE FRONTEND

Route berikut merupakan rancangan awal dan dapat disesuaikan sebelum implementasi.

| Halaman            | Route                     |
| ------------------ | ------------------------- |
| Beranda Publik     | /                         |
| Harga Publik       | /harga-tbs                |
| Detail PKS Publik  | /pks/:id                  |
| Lokasi PKS         | /lokasi-pks               |
| Profil Perumda     | /tentang                  |
| Kemitraan          | /kemitraan                |
| Kontak             | /kontak                   |
| Login              | /login                    |
| Dashboard Petani   | /app/petani               |
| Riwayat Panen      | /app/petani/panen         |
| Dashboard Koperasi | /app/koperasi             |
| Penerimaan TBS     | /app/koperasi/penerimaan  |
| Surat Jalan        | /app/koperasi/surat-jalan |
| Dashboard Perumda  | /app/perumda              |
| Harga Internal     | /app/perumda/harga        |
| Kontrak            | /app/perumda/kontrak      |
| Logistik           | /app/perumda/logistik     |
| Rekonsiliasi       | /app/perumda/rekonsiliasi |
| Pembayaran         | /app/perumda/pembayaran   |
| Dashboard PKS      | /app/pks                  |
| Tiket Timbang      | /app/pks/tiket-timbang    |
| Dashboard Direksi  | /app/direksi              |
| Persetujuan        | /app/direksi/persetujuan  |
| Dashboard Admin    | /app/admin                |
| Pengguna           | /app/admin/pengguna       |
| Audit              | /app/admin/audit          |

Route hanya merupakan jalur navigasi frontend.

Otorisasi tidak boleh bergantung pada nama atau pola route saja.

---

# 37. RANCANGAN KOMPONEN ATOMIC DESIGN

## 37.1 Atoms

Komponen yang dibutuhkan:

- Button.
- Text.
- Heading.
- Input.
- Label.
- Icon.
- Badge.
- Checkbox.
- Radio.
- Spinner.
- Skeleton.

## 37.2 Molecules

- SearchField.
- PriceItem.
- FilterControl.
- FormField.
- DateRangePicker.
- StatusIndicator.
- PaginationControl.
- LocationLink.
- WeightSummary.

## 37.3 Organisms

- PublicNavbar.
- InternalSidebar.
- PriceComparisonTable.
- MillLocationMap.
- FarmerDataTable.
- TbsReceivingForm.
- WeighingPanel.
- DeliveryOrderForm.
- ReconciliationDetail.
- PaymentApprovalPanel.
- ExecutiveKpiGrid.

## 37.4 Templates

- PublicTemplate.
- AuthTemplate.
- DashboardTemplate.
- DataManagementTemplate.
- TransactionTemplate.
- ExecutiveTemplate.

## 37.5 Pages

Pages menggunakan template dan komponen yang telah ditetapkan.

Komponen bersama tidak boleh menyimpan aturan bisnis pembayaran atau rekonsiliasi.

Aturan bisnis tetap menjadi tanggung jawab backend.

---

# 38. PAGE STATE DAN USER FEEDBACK

Setiap halaman berbasis data harus mendukung kondisi berikut.

## 38.1 Loading

Ditampilkan saat data sedang dimuat.

Gunakan skeleton atau indikator yang relevan.

## 38.2 Empty

Ditampilkan saat tidak ada data.

Contoh:

"Belum ada transaksi penerimaan."

## 38.3 Error

Ditampilkan saat operasi gagal.

Pesan harus menjelaskan tindakan berikutnya.

## 38.4 Success

Ditampilkan setelah operasi berhasil dan telah dikonfirmasi backend.

Contoh:

"Surat jalan berhasil diterbitkan."

## 38.5 Forbidden

Ditampilkan saat pengguna tidak memiliki izin.

## 38.6 Confirmation

Digunakan untuk tindakan penting seperti:

- Menerbitkan e-DO.
- Menyetujui harga.
- Mengubah data timbang.
- Menyelesaikan dispute.
- Menyetujui pembayaran.
- Menonaktifkan akun.

## 38.7 Unsaved Changes

Formulir yang memiliki perubahan belum disimpan harus memberikan peringatan ketika pengguna hendak meninggalkan halaman.

---

# 39. NOTIFIKASI DAN UMPAN BALIK

## 39.1 Notifikasi Minimum

Baseline menggunakan notifikasi dalam aplikasi untuk tindakan operasional yang relevan.

Contoh:

- Harga menunggu verifikasi.
- Harga ditolak.
- Pengiriman menunggu penerimaan PKS.
- Tiket timbang siap direkonsiliasi.
- Transaksi berstatus Dispute.
- Pembayaran menunggu persetujuan.

## 39.2 Aturan Notifikasi

- Notifikasi harus memiliki referensi transaksi.
- Pengguna hanya menerima notifikasi sesuai kewenangan.
- Notifikasi tidak boleh membocorkan informasi pribadi.
- Notifikasi yang dikirim berulang harus dapat dikendalikan.
- Kegagalan notifikasi tidak boleh membatalkan transaksi yang sudah sah.
- Pengiriman notifikasi eksternal merupakan fitur pengembangan tambahan.

---

# 40. TRACEABILITY MATRIX

| Flow ID | Proses                  | Modul                      |
| ------- | ----------------------- | -------------------------- |
| FLOW-01 | Portal Publik           | public_portal              |
| FLOW-02 | Harga multi-PKS         | pricing                    |
| FLOW-03 | Lokasi PKS              | public_portal, master_data |
| FLOW-04 | Login dan sesi          | identity_access            |
| FLOW-05 | Data petani dan kebun   | master_data                |
| FLOW-06 | Data PKS                | master_data                |
| FLOW-07 | Verifikasi harga        | pricing                    |
| FLOW-08 | Penerimaan TBS          | tbs_receiving              |
| FLOW-09 | Penimbangan dan grading | tbs_receiving              |
| FLOW-10 | Kontrak dan kuota       | contracts                  |
| FLOW-11 | Pemilihan PKS           | contracts, pricing         |
| FLOW-12 | Penerbitan e-DO         | logistics                  |
| FLOW-13 | Status pengiriman       | logistics                  |
| FLOW-14 | Verifikasi e-DO         | logistics, mill_weighing   |
| FLOW-15 | Tiket timbang PKS       | mill_weighing              |
| FLOW-16 | Rekonsiliasi            | reconciliation             |
| FLOW-17 | Penyelesaian dispute    | reconciliation             |
| FLOW-18 | Perhitungan nilai       | reconciliation             |
| FLOW-19 | Faktur dan pembayaran   | reconciliation             |
| FLOW-20 | Dashboard Petani        | reporting                  |
| FLOW-21 | Dashboard Koperasi      | reporting                  |
| FLOW-22 | Dashboard Perumda       | reporting                  |
| FLOW-23 | Dashboard Direksi       | reporting                  |
| FLOW-24 | Administrasi sistem     | identity_access, audit     |

Traceability detail terhadap API, database, dan aturan bisnis akan diperluas dalam dokumen lanjutan.

---

# 41. HAL YANG MASIH PERLU DIVALIDASI

Sebelum rancangan dianggap final, beberapa keputusan operasional masih perlu dikonfirmasi.

| No. | Keputusan                                        | Status                                      |
| --- | ------------------------------------------------ | ------------------------------------------- |
| 1   | Pihak yang berwenang menerbitkan e-DO            | Perlu validasi SOP                          |
| 2   | Batas toleransi penimbangan                      | Perlu validasi                              |
| 3   | Formula potongan grading                         | Perlu validasi                              |
| 4   | Mekanisme pembagian hasil multi-petani           | Perlu validasi                              |
| 5   | Harga yang berlaku untuk transaksi kontrak       | Perlu validasi                              |
| 6   | Jumlah tiket timbang per pengiriman              | Baseline satu tiket final, perlu konfirmasi |
| 7   | Kewenangan penyelesaian dispute                  | Perlu validasi                              |
| 8   | Kewenangan persetujuan pembayaran                | Perlu validasi                              |
| 9   | Jalur pembayaran kepada petani                   | Perlu validasi                              |
| 10  | Mekanisme pembayaran sebagian                    | Belum termasuk baseline wajib               |
| 11  | Prosedur penolakan TBS oleh PKS                  | Perlu validasi                              |
| 12  | Persyaratan perubahan e-DO setelah keberangkatan | Perlu validasi                              |
| 13  | Mekanisme integrasi langsung dengan PKS          | Bergantung ketersediaan akses               |
| 14  | Sumber dan periode harga publik                  | Perlu validasi                              |
| 15  | Data lokasi PKS yang boleh dipublikasikan        | Perlu validasi                              |

Apabila keputusan belum tersedia, prototipe dapat menggunakan aturan simulasi yang dijelaskan secara eksplisit dan tidak diklaim sebagai kebijakan operasional resmi.

---

# 42. KRITERIA PENERIMAAN AFD

Application Flow dinyatakan siap menjadi dasar implementasi apabila:

1. Semua peran memiliki jalur navigasi yang jelas.
2. Portal Publik dapat diakses tanpa login.
3. Pengguna internal memiliki autentikasi dan otorisasi.
4. Perbedaan hak akses pengguna terdokumentasi.
5. Alur informasi harga multi-PKS tersedia.
6. Alur lokasi PKS tersedia.
7. Alur master data tersedia.
8. Alur penerimaan TBS tersedia.
9. Alur penimbangan dan grading tersedia.
10. Alur kontrak dan kuota tersedia.
11. Alur pemilihan PKS tersedia.
12. Alur penerbitan e-DO tersedia.
13. Alur perubahan status pengiriman jelas.
14. Alur verifikasi tiket PKS tersedia.
15. Alur rekonsiliasi normal tersedia.
16. Alur dispute tersedia.
17. Alur perhitungan nilai transaksi tersedia.
18. Alur faktur dan pembayaran tersedia.
19. Alur dashboard tiap peran tersedia.
20. Semua operasi kritis memiliki penanganan gagal.
21. Setiap state transition memiliki aturan validasi.
22. Tidak ada perpindahan status yang melewati otorisasi.
23. Hubungan transaksi antar-modul jelas.
24. Request ganda tidak menciptakan transaksi ganda.
25. Data historis tetap dapat ditelusuri.
26. Pengguna tidak dapat mengakses data di luar cakupannya.
27. Logging dan audit mendukung investigasi error.
28. Skenario end-to-end dapat diterjemahkan menjadi pengujian.
29. Alur sesuai dengan kebutuhan PRD.
30. Implementasi dapat mengikuti arsitektur TRD tanpa menempatkan aturan bisnis di frontend.

---

# 43. KETERKAITAN DENGAN DOKUMEN BERIKUTNYA

## 43.1 Database Design Document (DBD)

DBD harus menerjemahkan seluruh alur AFD menjadi:

- Struktur entitas.
- Relasi data.
- Cardinality.
- Primary key.
- Foreign key.
- Unique constraint.
- Status dan riwayat.
- Struktur transaksi.
- Struktur alokasi muatan.
- Struktur kuota.
- Struktur audit.
- Struktur rekonsiliasi.
- Struktur faktur dan pembayaran.
- Indeks database.
- Strategi konsistensi data.

## 43.2 Business System Document (BSD)

BSD harus memperinci:

- Aturan operasional.
- Rumus bisnis.
- Penetapan harga.
- Validasi kontrak.
- Kuota pasokan.
- Perhitungan grading.
- Toleransi susut.
- Penyelesaian sengketa.
- Pembagian nilai transaksi.
- Kewenangan pembayaran.
- SOP perubahan status.
- Penanganan pengecualian bisnis.

## 43.3 Implementation Plan Document (IPD)

IPD harus menyusun:

- Urutan pembangunan backend dan frontend.
- Milestone.
- Ketergantungan modul.
- Rencana migrasi.
- Strategi pengujian.
- Jadwal integrasi.
- Quality gate.
- Kriteria sign-off.

---

# 44. KESIMPULAN

Application Flow Document ini mendefinisikan alur penggunaan Sistem Informasi Terintegrasi Rantai Pasok Tandan Buah Segar pada Perumda Tuah Sekata, Unit Agro Niaga.

Sistem memiliki dua lingkungan penggunaan, yaitu Portal Publik tanpa login dan Portal Internal dengan autentikasi serta pembatasan hak akses.

Portal Publik menyediakan alur informasi harga TBS multi-PKS, perbandingan harga, lokasi pabrik, dan informasi perusahaan.

Portal Internal menyediakan proses bisnis perdagangan TBS, mulai dari master data, penerimaan, penimbangan, grading, kontrak, pemilihan PKS, pengiriman e-DO, penerimaan pabrik, rekonsiliasi, faktur, hingga pencatatan pembayaran.

Alur transaksi memiliki status yang jelas, validasi, pemeriksaan kewenangan, penanganan error, dan audit aktivitas.

Perancangan mempertahankan prinsip Modular Monolith dengan Clean Architecture empat layer pada setiap modul backend, serta Atomic Design lima tingkat pada frontend.

Seluruh flow dirancang agar dapat diterjemahkan menjadi use case, pengujian end-to-end, model database, aturan bisnis, dan tahapan implementasi secara terstruktur.

**Status Dokumen: AFD V1.1 — APPLICATION FLOW BASELINE**

**Dokumen Selanjutnya: Database Design Document (DBD).**

**Akhir Dokumen — Application Flow Document V1.1**

# 45. PRIORITAS DAN KONTRAK FLOW V1.1

Bagian ini mengklasifikasikan flow tanpa menghapus alur atau ID yang telah ditetapkan. Alur operasional inti tetap: Petani → Koperasi → Perumda/Proses Niaga → PKS → Rekonsiliasi → Penagihan/Pembayaran → Pelaporan.

## 45.1 Prioritas

Core: portal publik dan harga multi-PKS; login/session/RBAC/scope; master data; input, verifikasi dan publikasi harga; penerimaan, timbang dan grading; kontrak/kuota; penentuan tujuan dan e-DO; status pengiriman; verifikasi/tiket PKS; rekonsiliasi/dispute; nilai transaksi, faktur dan pencatatan pembayaran sesuai SOP; dashboard inti dan audit.

Integrasi API PKS, GPS langsung, notifikasi tingkat lanjut, transfer bank otomatis, serta analitik lanjutan adalah conditional/deferred. Simulasi diberi label dan tidak dinyatakan sebagai kebijakan Perumda.

## 45.2 Kontrak Tiap Flow

Setiap flow MVP memetakan aktor/scope, prasyarat, input/validasi, satu use case/API operation, transisi yang diizinkan, efek transaksi dan audit, hasil sukses, error code, dan pemulihan. Error tidak menghapus jejak transaksi; mutasi yang dapat diulang memakai idempotency sesuai kebutuhan. Approval, rekonsiliasi, dispute, dan perlindungan transaksi tidak boleh dilewati.

State pembayaran terpisah dari timbang/pengiriman serta membedakan arus masuk/keluar. Otorisasi final mengikuti SOP, tanpa mengasumsikan kewenangan baru.

## 45.3 Pengujian Mandiri dan Integrasi

Backend flow diuji tanpa frontend melalui API/OpenAPI: validasi, otorisasi, efek database, state, error, dan audit. Frontend menguji journey yang sama dengan OpenAPI dan MSW, termasuk loading, empty, error, dan success. Integrasikan per fitur saat kontrak kedua sisi siap. Setiap flow ditelusuri ke requirement PRD, rule BSD, data DBD, dan milestone IPD.
