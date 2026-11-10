
# PRODUCT REQUIREMENTS DOCUMENT (PRD)

## SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TANDAN BUAH SEGAR (TBS)

### PERUMDA TUAH SEKATA — UNIT AGRO NIAGA

**Versi:** 1.0 — Draft Baseline
**Tanggal:** 10 November 2026
**Status:** Draft untuk Validasi Kebutuhan
**Jenis Produk:** Aplikasi Web Enterprise dan Portal Informasi Publik
**Organisasi:** Perumda Tuah Sekata, Kabupaten Pelalawan, Riau
**Bidang Usaha:** Agro Niaga — Perdagangan Tandan Buah Segar Kelapa Sawit
**Metodologi Penelitian:** Design Science Research Methodology (DSRM)
**Dokumen Terkait:** Proposal Tesis Givo Vrabora Revisi Final V2

---

# 1. PENDAHULUAN

## 1.1 Latar Belakang

Perumda Tuah Sekata merupakan Badan Usaha Milik Daerah (BUMD) di Kabupaten Pelalawan, Provinsi Riau. Berdasarkan informasi kebutuhan yang disampaikan, kegiatan usaha Perumda mencakup dua kelompok usaha, yaitu Listrik dan Gas serta Agro Niaga.

Pengembangan sistem informasi dalam dokumen ini difokuskan pada unit usaha Agro Niaga, khususnya kegiatan pengelolaan perdagangan Tandan Buah Segar (TBS) kelapa sawit.

Proses perdagangan TBS melibatkan berbagai pihak, di antaranya petani kelapa sawit, koperasi atau lembaga pengumpul, Perumda Tuah Sekata, perusahaan pengangkutan, dan Pabrik Kelapa Sawit (PKS).

Setiap pihak menjalankan aktivitas yang saling berkaitan, mulai dari penyediaan hasil panen, penetapan harga, penerimaan buah, penimbangan, pengiriman, pemeriksaan mutu, rekonsiliasi hasil timbangan, hingga penyelesaian pembayaran.

Berdasarkan permasalahan yang diuraikan dalam proposal tesis, proses tersebut berisiko mengalami kendala ketika informasi transaksi masih dicatat secara terpisah, menggunakan dokumen manual, atau dikomunikasikan melalui media yang tidak terintegrasi.

Di sisi lain, masyarakat dan petani membutuhkan akses yang mudah untuk mengetahui informasi harga pembelian TBS dari beberapa pabrik, lokasi perusahaan, serta informasi kemitraan.

Oleh karena itu, diperlukan sistem informasi berbasis web yang mampu mengintegrasikan proses bisnis internal unit Agro Niaga dan menyediakan portal informasi publik yang dapat diakses masyarakat tanpa keharusan membuat akun.

## 1.2 Tujuan Dokumen

Product Requirements Document (PRD) disusun sebagai dokumen acuan kebutuhan produk sebelum tahapan perancangan teknis dan implementasi perangkat lunak.

Dokumen ini bertujuan untuk:

1. Menjelaskan visi, tujuan, dan ruang lingkup sistem informasi Agro Niaga.
2. Mengidentifikasi kategori pengguna beserta kebutuhan dan batasan aksesnya.
3. Mendefinisikan fitur fungsional dan perilaku yang diharapkan dari sistem.
4. Menggambarkan alur bisnis perdagangan TBS dari hulu hingga hilir.
5. Mendefinisikan aturan bisnis, validasi, dan proses persetujuan.
6. Menetapkan kebutuhan portal informasi publik tanpa login.
7. Menentukan prioritas pengembangan agar sesuai ruang lingkup penelitian tesis.
8. Menetapkan indikator keberhasilan produk dan kriteria penerimaan fitur.
9. Menjadi dasar penyusunan TRD, AFD, DBD, BSD, dan IPD.

Dokumen ini tidak menetapkan bahasa pemrograman, framework, struktur tabel final, atau detail infrastruktur. Keputusan tersebut dijabarkan dalam dokumen teknis berikutnya.

## 1.3 Status dan Sumber Kebutuhan

Kebutuhan dalam PRD dibedakan menjadi tiga kategori:

| Kategori           | Keterangan                                                                                                |
| ------------------ | --------------------------------------------------------------------------------------------------------- |
| Baseline Proposal  | Kebutuhan yang telah tercantum dalam proposal tesis Revisi Final V2                                       |
| Tambahan Kebutuhan | Kebutuhan baru yang disampaikan untuk Portal Publik, harga multi-PKS, dan lokasi perusahaan               |
| Rekomendasi Desain | Penyempurnaan produk yang diusulkan untuk menjamin konsistensi data, keamanan, dan kelayakan implementasi |

Semua rekomendasi desain yang belum dikonfirmasi oleh pengguna atau pihak Perumda berstatus **perlu validasi** sebelum ditetapkan sebagai kebutuhan final.

---

# 2. VISI DAN TUJUAN PRODUK

## 2.1 Visi Produk

Mewujudkan platform informasi Agro Niaga terintegrasi yang transparan, mudah digunakan, dan dapat ditelusuri, untuk mendukung pengelolaan perdagangan TBS kelapa sawit dari petani hingga pabrik.

Sistem diharapkan menjadi sarana informasi bagi masyarakat sekaligus mendukung tata kelola operasional Perumda Tuah Sekata secara lebih terstruktur, akuntabel, dan efisien.

## 2.2 Tujuan Utama Produk

Tujuan utama pengembangan meliputi:

1. **Integrasi Data:** Menyatukan informasi petani, koperasi, PKS, harga, kontrak, penimbangan, pengiriman, rekonsiliasi, dan pembayaran.
2. **Transparansi Harga:** Menyediakan informasi harga TBS dari berbagai PKS serta harga acuan resmi yang relevan.
3. **Aksesibilitas Publik:** Memberikan akses informasi harga dan lokasi perusahaan tanpa login.
4. **Keterlacakan Transaksi:** Memungkinkan transaksi TBS ditelusuri dari penerimaan hasil panen sampai penyelesaian pembayaran.
5. **Otomatisasi Administrasi:** Mengurangi pencatatan berulang, mempercepat perhitungan, dan mengurangi risiko kesalahan input.
6. **Rekonsiliasi Terstruktur:** Mendukung pencocokan hasil timbang koperasi dan PKS dengan penanganan selisih yang terdokumentasi.
7. **Monitoring Manajemen:** Menyediakan informasi operasional dan keuangan yang dapat digunakan Direksi untuk pengambilan keputusan.
8. **Evaluasi Ilmiah:** Menghasilkan artefak sistem informasi yang dapat diuji melalui pendekatan DSRM.

## 2.3 Prinsip Produk

Pengembangan sistem harus mengikuti prinsip berikut:

- **Public First:** Informasi publik dapat diakses tanpa login.
- **Role-Based Access:** Data internal hanya dapat diakses sesuai kewenangan.
- **Single Source of Truth:** Data transaksi yang sama menggunakan referensi yang konsisten.
- **Traceability:** Setiap perubahan penting dapat ditelusuri.
- **Human-in-the-Loop:** Keputusan yang berdampak pada pembayaran dan sengketa tetap memerlukan verifikasi pihak berwenang.
- **Mobile-First:** Antarmuka publik dan aktivitas lapangan dioptimalkan untuk ponsel.
- **Data Integrity:** Sistem mencegah duplikasi dan perubahan transaksi yang tidak sah.
- **Research-Oriented:** Seluruh fungsi penting harus dapat didemonstrasikan dan dievaluasi.

---

# 3. RUANG LINGKUP PRODUK

## 3.1 Ruang Lingkup Organisasi

Sistem dikembangkan khusus untuk unit Agro Niaga Perumda Tuah Sekata.

Cakupan pihak yang terlibat:

1. Perumda Tuah Sekata.
2. Petani kelapa sawit swadaya.
3. Koperasi atau kelompok tani mitra.
4. Pabrik Kelapa Sawit (PKS) mitra.
5. Pihak pengangkutan TBS sebagai entitas operasional.
6. Masyarakat umum sebagai pengguna informasi publik.

Unit Listrik dan Gas tidak termasuk cakupan sistem.

## 3.2 Jenis Platform

Sistem dirancang sebagai aplikasi web responsif dengan dua lingkungan akses.

### A. Portal Publik

Portal Publik merupakan website yang dapat diakses siapa saja tanpa akun.

Fungsi utama:

- Menampilkan informasi Perumda dan unit Agro Niaga.
- Menampilkan harga pembelian TBS dari beberapa PKS.
- Menampilkan harga acuan Disbun.
- Membandingkan harga antar-PKS berdasarkan informasi yang telah diverifikasi.
- Menampilkan lokasi perusahaan dan PKS mitra.
- Menyediakan pencarian dan penyaringan informasi pabrik.
- Menampilkan informasi kerja sama atau kemitraan.
- Menyediakan kontak dan informasi layanan.
- Menyediakan akses login bagi pengguna resmi.

### B. Portal Internal

Portal Internal diperuntukkan bagi pengguna yang memiliki akun resmi.

Fungsi utama:

- Pengelolaan master data.
- Administrasi harga TBS.
- Pengelolaan koperasi dan petani.
- Penerimaan TBS.
- Penimbangan dan grading.
- Kontrak dan kuota pasokan.
- Surat jalan elektronik.
- Pencatatan hasil timbang PKS.
- Rekonsiliasi transaksi.
- Administrasi dan otorisasi pembayaran.
- Dashboard serta laporan.
- Manajemen pengguna dan audit aktivitas.

## 3.3 Batasan Sistem

Pengembangan pada tahap tesis dibatasi pada prototipe web fungsional.

Sistem tidak diwajibkan melakukan:

- Pengelolaan operasional unit Listrik dan Gas.
- Transfer dana otomatis melalui bank.
- Integrasi wajib dengan seluruh sistem PKS di Kabupaten Pelalawan.
- Pelacakan GPS armada secara langsung.
- Pengendalian fisik mesin timbangan.
- Prediksi harga sawit berbasis AI.
- Otomatisasi keputusan sengketa tanpa pemeriksaan manusia.
- Implementasi sistem ERP penuh untuk seluruh divisi Perumda.
- Pengoperasian infrastruktur enterprise berskala produksi penuh.

Integrasi eksternal dapat dikembangkan kemudian apabila izin, akses, dan kebutuhan operasional telah tersedia.

---

# 4. IDENTIFIKASI PENGGUNA DAN HAK AKSES

## 4.1 Kategori Pengguna

Sistem memiliki enam kategori akses utama, terdiri dari satu kategori pengguna publik dan lima kategori pengguna terautentikasi.

Administrator teknis merupakan peran sistem tambahan.

| Kode    | Pengguna             | Login | Tujuan Penggunaan                                                         |
| ------- | -------------------- | ----- | ------------------------------------------------------------------------- |
| ROLE-01 | Masyarakat Umum      | Tidak | Mengakses harga, lokasi PKS, dan informasi perusahaan                     |
| ROLE-02 | Petani Swadaya       | Ya    | Melihat riwayat hasil panen, hasil timbang, dan status pembayaran pribadi |
| ROLE-03 | Operator Koperasi    | Ya    | Mengelola penerimaan, penimbangan, grading, dan pengiriman                |
| ROLE-04 | Staf Perumda         | Ya    | Mengelola harga, kontrak, rekonsiliasi, dan administrasi niaga            |
| ROLE-05 | Petugas PKS          | Ya    | Memverifikasi pengiriman dan memasukkan tiket timbang pabrik              |
| ROLE-06 | Direksi Perumda      | Ya    | Monitoring operasional, keuangan, dan persetujuan sesuai kewenangan       |
| ROLE-07 | Administrator Sistem | Ya    | Mengelola akun, peran, konfigurasi, dan keamanan sistem                   |

ROLE-07 merupakan peran pendukung, bukan penambahan kelompok utama responden penelitian tesis.

## 4.2 Hak Akses Pengguna Publik

Pengguna publik dapat:

- Mengunjungi website.
- Melihat harga TBS yang dipublikasikan.
- Membandingkan harga pembelian beberapa PKS.
- Melihat tanggal dan sumber pembaruan harga.
- Melihat alamat dan lokasi PKS yang dipublikasikan.
- Membuka navigasi menuju lokasi yang tersedia.
- Melihat profil Perumda.
- Melihat informasi kemitraan.
- Menghubungi kontak resmi yang dipublikasikan.

Pengguna publik tidak dapat:

- Melihat identitas pribadi petani lain.
- Melihat data transaksi internal.
- Melihat dokumen kontrak rahasia.
- Mengakses data rekening dan pembayaran.
- Mengubah harga.
- Menginput penimbangan.
- Mengubah status pengiriman.
- Menjalankan rekonsiliasi.
- Mengakses dashboard keuangan internal.

## 4.3 Hak Akses Petani

Petani yang memiliki akun dapat melihat:

- Profil dan informasi kebun miliknya.
- Harga TBS publik.
- Riwayat penyerahan panen miliknya.
- Berat dan hasil grading yang relevan.
- Rincian nilai transaksi miliknya.
- Status proses pembayaran.
- Riwayat pembayaran yang sudah tercatat.

Petani tidak memiliki kewenangan untuk mengubah timbangan dan menyetujui pembayaran.

## 4.4 Hak Akses Koperasi

Operator koperasi dapat:

- Mengelola data petani yang berada dalam cakupan koperasinya.
- Mencatat penerimaan TBS.
- Menginput berat timbangan.
- Mencatat hasil grading.
- Menyiapkan dan menerbitkan e-DO sesuai otorisasi.
- Memantau pengiriman yang terkait dengan koperasinya.
- Melihat hasil rekonsiliasi yang relevan.

Operator koperasi tidak dapat mengubah transaksi milik koperasi lain atau mengotorisasi pencairan dana Perumda.

## 4.5 Hak Akses Staf Perumda

Staf Perumda dapat:

- Mengelola data PKS mitra.
- Memperbarui informasi harga.
- Memverifikasi harga sebelum dipublikasikan.
- Mengelola kontrak dan kuota.
- Mengawasi penerimaan dan pengiriman.
- Memeriksa tiket timbang.
- Melakukan rekonsiliasi.
- Memproses perhitungan tagihan.
- Menyiapkan dan memverifikasi administrasi pembayaran.
- Menghasilkan laporan operasional.

Kewenangan operasional dan keuangan harus dipisahkan jika diperlukan oleh SOP Perumda.

## 4.6 Hak Akses Petugas PKS

Petugas PKS dapat:

- Melihat pengiriman yang ditujukan ke PKS-nya.
- Memverifikasi surat jalan.
- Mencatat kedatangan truk.
- Memasukkan data tiket timbang.
- Mencatat hasil pemeriksaan mutu.
- Mengonfirmasi penerimaan TBS.

Petugas PKS tidak dapat mengubah data perusahaan PKS lain.

## 4.7 Hak Akses Direksi

Direksi dapat:

- Melihat dashboard operasional.
- Melihat laporan tonase dan transaksi.
- Melihat laporan margin usaha berdasarkan data tersedia.
- Memantau status pembayaran.
- Memantau transaksi yang bermasalah.
- Menyetujui transaksi sesuai batas kewenangan.
- Mengakses laporan pengambilan keputusan.

---

# 5. MASALAH PENGGUNA DAN SOLUSI PRODUK

| Masalah                                              | Dampak Potensial                     | Solusi Sistem                            |
| ---------------------------------------------------- | ------------------------------------ | ---------------------------------------- |
| Informasi harga dari beberapa PKS tersebar           | Sulit membandingkan penawaran        | Dashboard harga multi-PKS                |
| Masyarakat kesulitan menemukan informasi PKS         | Akses informasi terbatas             | Portal Publik dan peta lokasi            |
| Pencatatan petani dan koperasi terpisah              | Data ganda dan tidak konsisten       | Master data terpusat                     |
| Penimbangan menggunakan dokumen berbeda              | Sulit melakukan verifikasi           | Pencatatan timbangan digital             |
| Dokumen pengiriman manual                            | Kesulitan menelusuri pengiriman      | Surat jalan elektronik                   |
| Hasil timbang koperasi berbeda dari PKS              | Sengketa dan pemeriksaan berulang    | Rekonsiliasi otomatis                    |
| Verifikasi pembayaran membutuhkan pencocokan dokumen | Proses administrasi lambat           | Faktur dan status pembayaran terstruktur |
| Informasi manajemen tersebar                         | Pengambilan keputusan kurang efisien | Dashboard eksekutif                      |

Masalah tersebut merupakan dasar rancangan produk. Besarnya dampak aktual perlu divalidasi melalui wawancara, observasi, dan data lapangan.

---

# 6. STRUKTUR PRODUK DAN NAVIGASI

## 6.1 Portal Publik

Navigasi utama:

1. Beranda
2. Harga TBS
3. Lokasi PKS
4. Tentang Perumda
5. Informasi Kemitraan
6. Kontak
7. Login

### Halaman Beranda

Menampilkan:

- Identitas Perumda Tuah Sekata.
- Penjelasan singkat Unit Agro Niaga.
- Informasi harga terbaru yang telah dipublikasikan.
- Ringkasan jumlah PKS mitra yang datanya tersedia untuk publik.
- Akses cepat ke perbandingan harga.
- Akses cepat ke peta PKS.
- Informasi tanggal pembaruan.
- Kontak resmi.

### Halaman Harga TBS

Menampilkan:

- Nama PKS.
- Harga pembelian per kilogram.
- Kategori atau spesifikasi harga.
- Tanggal dan waktu berlaku.
- Waktu pembaruan.
- Sumber informasi.
- Status verifikasi.
- Riwayat harga.
- Perbandingan harga.

### Halaman Lokasi PKS

Menampilkan:

- Daftar perusahaan atau PKS mitra.
- Alamat.
- Titik lokasi pada peta.
- Nama perusahaan.
- Informasi kontak publik jika tersedia.
- Harga terbaru yang tersedia.
- Tautan navigasi.
- Filter berdasarkan wilayah.

### Halaman Informasi Kemitraan

Menampilkan:

- Gambaran proses menjadi mitra.
- Persyaratan yang telah disetujui Perumda untuk dipublikasikan.
- Kontak atau kanal komunikasi.
- Informasi pelayanan Agro Niaga.

## 6.2 Portal Internal

### Menu Petani

- Dashboard Saya
- Harga TBS
- Lokasi PKS
- Profil Kebun
- Riwayat Panen
- Hasil Penimbangan
- Status Pembayaran
- Profil Akun

### Menu Operator Koperasi

- Dashboard
- Data Petani
- Penerimaan TBS
- Penimbangan
- Grading
- Surat Jalan
- Status Pengiriman
- Riwayat Transaksi

### Menu Staf Perumda

- Dashboard Operasional
- Master Data
- Harga Multi-PKS
- Kontrak dan Kuota
- Penerimaan TBS
- Logistik
- Tiket Timbang PKS
- Rekonsiliasi
- Pembayaran
- Laporan

### Menu Petugas PKS

- Dashboard Penerimaan
- Daftar Pengiriman
- Verifikasi e-DO
- Tiket Timbang
- Hasil Grading
- Riwayat Penerimaan

### Menu Direksi

- Dashboard Eksekutif
- Monitoring Harga
- Monitoring Pasokan
- Kinerja Koperasi
- Kinerja PKS
- Monitoring Rekonsiliasi
- Monitoring Keuangan
- Laporan

### Menu Administrator

- Pengguna
- Hak Akses
- Data Referensi
- Konfigurasi
- Audit Aktivitas
- Pengaturan Sistem

---

# 7. KEBUTUHAN FUNGSIONAL PORTAL PUBLIK

## 7.1 Akses Tanpa Login

**ID: FR-PUB-001**

Sistem harus menyediakan Portal Publik yang dapat diakses tanpa autentikasi.

Kriteria penerimaan:

- Pengunjung dapat membuka halaman publik tanpa akun.
- Tidak ada kewajiban login untuk melihat harga TBS dan lokasi PKS.
- Halaman internal tetap terlindungi.
- Data internal tidak dikirim melalui layanan publik.

## 7.2 Informasi Harga TBS

**ID: FR-PUB-002**

Sistem harus menampilkan daftar harga TBS yang telah disetujui untuk dipublikasikan.

Informasi minimal:

- Nama PKS.
- Nominal harga.
- Satuan harga.
- Kategori atau dasar penetapan harga.
- Tanggal berlaku.
- Waktu pembaruan.
- Sumber harga.

Kriteria penerimaan:

- Hanya harga berstatus terverifikasi dan aktif yang ditampilkan sebagai harga berlaku.
- Informasi yang kedaluwarsa tidak ditampilkan sebagai harga terbaru.
- Pengunjung dapat mengetahui kapan informasi diperbarui.
- Informasi kosong tidak diganti dengan harga buatan.

## 7.3 Perbandingan Harga Multi-PKS

**ID: FR-PUB-003**

Sistem harus menyediakan perbandingan harga dari beberapa PKS.

Fungsi:

- Urutkan harga tertinggi.
- Urutkan harga terendah.
- Cari berdasarkan nama PKS.
- Filter berdasarkan wilayah.
- Filter berdasarkan tanggal berlaku.
- Bandingkan kategori harga yang setara.

Kriteria penerimaan:

- Sistem tidak membandingkan dua harga yang memiliki spesifikasi berbeda tanpa penjelasan.
- Harga yang belum diverifikasi tidak dijadikan dasar peringkat.
- Perbandingan dapat dilakukan tanpa login.

## 7.4 Harga Acuan Disbun

**ID: FR-PUB-004**

Sistem harus dapat menampilkan harga acuan yang bersumber dari informasi resmi Dinas Perkebunan.

Ketentuan:

- Harga acuan dibedakan dari penawaran harga PKS.
- Periode penetapan dicantumkan.
- Sumber informasi dicantumkan.
- Harga berdasarkan kelompok umur tanaman dapat ditampilkan apabila datanya tersedia.

Sistem tidak boleh mengasumsikan harga acuan sama dengan harga transaksi aktual di semua PKS.

## 7.5 Informasi Lokasi Perusahaan

**ID: FR-PUB-005**

Sistem menyediakan halaman lokasi perusahaan dan PKS mitra.

Informasi minimal:

- Nama PKS/perusahaan.
- Alamat.
- Kabupaten/kecamatan.
- Koordinat jika tersedia.
- Titik peta.
- Tautan navigasi.

Kriteria penerimaan:

- Lokasi ditampilkan berdasarkan koordinat yang telah diverifikasi.
- Pengguna dapat membuka detail lokasi.
- Jika koordinat belum tersedia, sistem tetap dapat menampilkan alamat tanpa menciptakan titik lokasi fiktif.
- Tidak diperlukan login.

## 7.6 Profil Perusahaan

**ID: FR-PUB-006**

Sistem menyediakan halaman profil Perumda Tuah Sekata dan informasi Unit Agro Niaga.

Konten harus dapat diperbarui oleh petugas berwenang.

## 7.7 Informasi dan Kontak Kemitraan

**ID: FR-PUB-007**

Sistem menampilkan kontak resmi dan informasi kemitraan yang telah disetujui untuk dipublikasikan.

Pengunjung dapat menghubungi pihak Perumda melalui kanal yang tersedia.

Pendaftaran mitra secara otomatis tidak termasuk kewajiban tahap awal.

---

# 8. MODUL 1 — MASTER DATA AKTOR DAN PROFIL KEBUN

## 8.1 Deskripsi

Modul Master Data mengelola informasi dasar seluruh aktor yang terlibat dalam rantai pasok TBS.

Modul ini menjadi sumber referensi bagi transaksi lain.

## 8.2 Fitur Utama

**FR-MD-001 — Manajemen Petani**

Sistem dapat mencatat dan memperbarui:

- Identitas petani.
- Kode petani.
- Informasi kontak.
- Status keanggotaan koperasi.
- Status aktif/nonaktif.

Data identitas pribadi harus dibatasi aksesnya.

**FR-MD-002 — Manajemen Kebun**

Sistem mencatat:

- Kode kebun.
- Pemilik kebun.
- Lokasi dan luas kebun.
- Informasi umur tanaman.
- Nomor STDB jika tersedia.
- Status verifikasi data kebun.

**FR-MD-003 — Manajemen Koperasi**

Sistem mencatat:

- Kode koperasi.
- Nama koperasi.
- Alamat dan kontak.
- Petugas/operator.
- Status kerja sama.
- Daftar petani terkait.

**FR-MD-004 — Manajemen PKS**

Sistem mencatat:

- Kode PKS.
- Nama perusahaan.
- Nama pabrik.
- Alamat.
- Koordinat lokasi.
- Kontak yang disetujui.
- Status kemitraan.
- Status publikasi profil.

**FR-MD-005 — Validasi Data Unik**

Sistem harus mencegah duplikasi identitas referensi dan mempertahankan konsistensi hubungan data.

## 8.3 Aturan Bisnis

- Setiap entitas memiliki ID unik.
- Data master yang sudah digunakan transaksi tidak boleh dihapus secara sembarangan.
- Data dapat dinonaktifkan tanpa menghilangkan riwayat.
- Setiap perubahan penting dicatat.
- Koperasi hanya dapat mengelola petani sesuai cakupannya.
- Data PKS yang dipublikasikan tidak boleh memuat informasi rahasia perusahaan.

## 8.4 Kriteria Penerimaan

- Petani dapat didaftarkan tanpa membuat entri ganda.
- Koperasi dapat dikaitkan dengan petani.
- PKS dapat dikaitkan dengan harga dan kontrak.
- Data kebun dapat ditelusuri ke petani terkait.
- Referensi transaksi lama tetap valid setelah data master diperbarui.

---

# 9. MODUL 2 — MONITORING DAN MANAJEMEN HARGA TBS

## 9.1 Deskripsi

Modul Harga mengelola informasi harga pembelian TBS dari berbagai PKS mitra serta informasi harga acuan Disbun.

Modul ini menjadi salah satu fitur utama produk.

## 9.2 Fitur Utama

**FR-HRG-001 — Input Harga PKS**

Staf berwenang dapat memasukkan:

- PKS sumber harga.
- Harga pembelian per kilogram.
- Kategori atau spesifikasi harga.
- Tanggal mulai berlaku.
- Tanggal akhir berlaku jika ada.
- Sumber informasi.
- Catatan.
- Bukti pendukung jika tersedia.

**FR-HRG-002 — Verifikasi Harga**

Sistem menyediakan proses validasi sebelum harga dipublikasikan.

Status yang disarankan:

- Draft.
- Menunggu Verifikasi.
- Terverifikasi.
- Dipublikasikan.
- Kedaluwarsa.
- Ditolak.

**FR-HRG-003 — Riwayat Harga**

Sistem menyimpan riwayat perubahan harga untuk setiap PKS.

Harga historis tidak boleh hilang akibat pembaruan harga terbaru.

**FR-HRG-004 — Perbandingan Harga**

Sistem dapat membandingkan harga beberapa PKS pada kategori dan periode yang setara.

**FR-HRG-005 — Harga Acuan Disbun**

Sistem dapat menyimpan harga acuan resmi secara terpisah.

**FR-HRG-006 — Publikasi Harga**

Harga yang telah diverifikasi dapat ditampilkan pada Portal Publik.

**FR-HRG-007 — Indikator Kesegaran Data**

Sistem menampilkan tanggal berlaku dan waktu pembaruan agar pengguna dapat membedakan informasi terbaru dengan informasi lama.

## 9.3 Aturan Bisnis

1. Harga harus memiliki nilai positif.
2. Harga menggunakan satuan yang jelas, seperti rupiah per kilogram.
3. Harga harus memiliki sumber dan periode berlaku.
4. Harga PKS dan harga acuan Disbun merupakan jenis informasi yang berbeda.
5. Harga yang belum diverifikasi tidak boleh dipublikasikan sebagai harga resmi yang berlaku.
6. Riwayat harga harus dipertahankan.
7. Harga transaksi yang telah disepakati berdasarkan kontrak tidak berubah otomatis hanya karena harga publik diperbarui.
8. Perubahan harga setelah transaksi dibentuk tidak boleh mengubah nominal historis tanpa mekanisme koreksi resmi.
9. Sistem harus menampilkan pesan apabila tidak tersedia harga terbaru.
10. Pembaruan otomatis melalui API hanya diterapkan jika sumber resmi dan akses integrasi tersedia.

## 9.4 Kriteria Penerimaan

- Petugas dapat memasukkan harga dari beberapa PKS.
- Harga baru melalui proses verifikasi.
- Harga terverifikasi muncul di Portal Publik.
- Harga yang belum disetujui tidak muncul sebagai harga berlaku.
- Riwayat pembaruan dapat ditampilkan.
- Pengunjung dapat mengurutkan harga.
- Data harga lama tidak merusak perhitungan transaksi yang telah disahkan.

---

# 10. MODUL 3 — PENERIMAAN DAN PENIMBANGAN TBS

## 10.1 Deskripsi

Modul ini digunakan untuk mencatat hasil panen yang diterima dari petani melalui koperasi atau lembaga pengumpul.

## 10.2 Fitur Utama

**FR-TBS-001 — Penerimaan TBS**

Petugas mencatat:

- Nomor penerimaan.
- Tanggal penerimaan.
- Identitas petani.
- Koperasi.
- Asal kebun.
- Informasi panen.
- Jumlah atau berat buah.
- Petugas penerima.

**FR-TBS-002 — Penimbangan**

Sistem mencatat:

- Berat bruto.
- Berat tara.
- Berat netto.
- Identitas alat atau lokasi timbang jika tersedia.
- Waktu penimbangan.

**FR-TBS-003 — Grading**

Sistem mencatat:

- Kategori mutu.
- Potongan yang diterapkan.
- Dasar potongan.
- Hasil pemeriksaan.
- Catatan petugas.

**FR-TBS-004 — Kalkulasi Berat Bersih**

Sistem menghitung berat berdasarkan rumus yang sudah ditetapkan.

Berat netto = Berat bruto − Berat tara.

Jika terdapat potongan mutu berbasis berat, sistem harus mencatat berat sebelum dan sesudah potongan secara terpisah.

**FR-TBS-005 — Riwayat Penerimaan**

Setiap petani dan koperasi dapat melihat riwayat transaksi sesuai kewenangannya.

## 10.3 Aturan Bisnis

- Berat tidak boleh negatif.
- Berat tara tidak boleh melebihi berat bruto.
- Nomor penerimaan harus unik.
- Transaksi harus memiliki identitas petani atau sumber pasokan yang sah.
- Transaksi tidak dapat dimasukkan ke pengiriman lebih dari satu kali tanpa prosedur yang jelas.
- Setelah disahkan, koreksi harus melalui proses revisi dan audit.
- Jenis serta formula potongan grading harus mengikuti kebijakan yang disetujui.

## 10.4 Kriteria Penerimaan

- Sistem menghitung netto dengan benar.
- Input tidak valid ditolak.
- Transaksi tersimpan dengan ID unik.
- Transaksi dapat ditelusuri ke petani dan koperasi.
- Data penerimaan dapat digunakan untuk membentuk surat jalan.

---

# 11. MODUL 4 — KONTRAK NIAGA DAN ALOKASI KUOTA

## 11.1 Deskripsi

Modul Kontrak mengelola hubungan perdagangan TBS antara Perumda dan PKS mitra.

## 11.2 Fitur Utama

**FR-KTR-001 — Manajemen Kontrak**

Data kontrak meliputi:

- Nomor kontrak.
- PKS tujuan.
- Periode berlaku.
- Jenis atau spesifikasi TBS.
- Ketentuan harga.
- Kuota pasokan.
- Ketentuan grading.
- Ketentuan penyelesaian pembayaran.
- Status kontrak.

**FR-KTR-002 — Monitoring Kuota**

Sistem menampilkan:

- Total kuota.
- Kuota yang sudah dialokasikan.
- Kuota yang sudah diterima PKS.
- Sisa kuota.
- Periode kuota.

**FR-KTR-003 — Pemilihan PKS Tujuan**

Petugas dapat mempertimbangkan:

- Harga yang tersedia.
- Kontrak aktif.
- Sisa kuota.
- Lokasi PKS.
- Ketentuan mutu.
- Perkiraan biaya pengiriman, jika datanya tersedia.

**FR-KTR-004 — Riwayat Kontrak**

Sistem menyimpan histori kontrak dan perubahan status.

## 11.3 Aturan Bisnis

- Kontrak harus berada dalam periode aktif untuk digunakan.
- Alokasi pasokan harus mempertimbangkan sisa kuota.
- Pemilihan harga tertinggi tidak otomatis menentukan pabrik terbaik.
- Informasi kontrak yang bersifat rahasia tidak dipublikasikan.
- Perubahan kontrak tidak boleh mengubah transaksi historis yang sudah disetujui.
- Mekanisme reservasi dan pengurangan kuota harus konsisten untuk mencegah alokasi ganda.

## 11.4 Kriteria Penerimaan

- Kontrak dapat dibuat dan dikelola.
- Pengiriman dapat dihubungkan dengan kontrak yang sesuai.
- Sisa kuota dihitung secara konsisten.
- Kontrak tidak aktif tidak dapat dipakai untuk transaksi baru tanpa otorisasi khusus.

---

# 12. MODUL 5 — LOGISTIK DAN SURAT JALAN ELEKTRONIK

## 12.1 Deskripsi

Modul Logistik mengelola proses pengiriman TBS dari lokasi pengumpul menuju PKS.

## 12.2 Fitur Utama

**FR-LOG-001 — Data Kendaraan dan Sopir**

Sistem mencatat:

- Nomor polisi.
- Identitas kendaraan.
- Nama sopir.
- Kontak operasional.
- Status kendaraan jika diperlukan.

**FR-LOG-002 — Pembuatan e-DO**

Surat jalan elektronik memuat:

- Nomor e-DO.
- Tanggal pengiriman.
- Koperasi asal.
- PKS tujuan.
- Nomor kendaraan.
- Identitas sopir.
- Daftar transaksi penerimaan yang menjadi muatan.
- Total berat yang tercatat.
- Referensi kontrak.

**FR-LOG-003 — QR Code**

Sistem menghasilkan QR Code atau referensi digital unik untuk memudahkan verifikasi surat jalan.

Kode tidak boleh memberikan akses ke data rahasia tanpa pemeriksaan kewenangan.

**FR-LOG-004 — Status Pengiriman**

Status yang disarankan:

1. Draft.
2. Siap Dikirim.
3. Dalam Perjalanan.
4. Tiba di PKS.
5. Diterima.
6. Selesai.
7. Dibatalkan.

**FR-LOG-005 — Informasi Lokasi Tujuan**

Sistem menampilkan alamat dan peta lokasi PKS tujuan.

**FR-LOG-006 — Konsolidasi Muatan**

Satu e-DO dapat mengandung beberapa transaksi penerimaan dari petani yang berbeda.

## 12.3 Aturan Bisnis

- Setiap e-DO harus memiliki nomor unik.
- Pengiriman harus memiliki PKS tujuan.
- Muatan yang sama tidak boleh dikirim dua kali dalam transaksi aktif.
- Perubahan tujuan setelah keberangkatan harus memerlukan otorisasi dan pencatatan alasan.
- Status pengiriman harus mengikuti perpindahan yang diperbolehkan.
- Pembatalan tidak boleh menghapus riwayat transaksi.
- Sistem tidak mengklaim lokasi truk secara langsung apabila GPS tidak tersedia.

## 12.4 Kriteria Penerimaan

- e-DO dapat dibuat dari transaksi penerimaan valid.
- Nomor dan QR Code unik.
- Data muatan tersimpan.
- Perubahan status tercatat.
- PKS tujuan dapat memverifikasi referensi pengiriman.
- Transaksi asal dapat ditelusuri dari satu e-DO.

---

# 13. MODUL 6 — INTEGRASI TIKET TIMBANG PKS

## 13.1 Deskripsi

Modul ini mencatat hasil penerimaan TBS di PKS dan menghubungkannya dengan pengiriman yang berasal dari koperasi.

## 13.2 Fitur Utama

**FR-PKS-001 — Verifikasi Pengiriman**

Petugas memeriksa nomor e-DO dan identitas kendaraan.

**FR-PKS-002 — Pencatatan Tiket Timbang**

Data tiket meliputi:

- Nomor tiket PKS.
- Nomor e-DO.
- PKS penerima.
- Tanggal dan waktu timbang.
- Berat bruto.
- Berat tara.
- Berat netto.
- Identitas petugas.
- Referensi bukti timbang.

**FR-PKS-003 — Pencatatan Grading Pabrik**

Sistem dapat mencatat:

- Hasil pemeriksaan mutu.
- Kategori potongan.
- Persentase atau jumlah potongan.
- Berat diterima sesuai ketentuan PKS.
- Catatan pemeriksaan.

**FR-PKS-004 — Unggah Bukti Tiket**

Jika diizinkan, petugas dapat mengunggah salinan tiket sebagai lampiran.

**FR-PKS-005 — Verifikasi Data**

Tiket yang sudah dimasukkan melalui proses validasi sebelum dipakai dalam rekonsiliasi.

## 13.3 Alternatif Mekanisme Integrasi

Sistem mendukung dua pendekatan:

**A. Input Terverifikasi**

Petugas PKS atau staf Perumda yang diberi kewenangan memasukkan hasil timbang berdasarkan dokumen resmi.

**B. Integrasi API**

Data diperoleh dari sistem PKS melalui API apabila kerja sama dan akses teknis tersedia.

Untuk prototipe tesis, pendekatan A dapat menjadi baseline agar sistem tetap dapat diuji tanpa bergantung pada ketersediaan API pihak ketiga.

## 13.4 Kriteria Penerimaan

- Tiket dapat dihubungkan dengan e-DO.
- Nomor tiket tidak tercatat ganda dalam cakupan PKS yang sama.
- Sistem menghitung netto secara benar.
- Bukti timbang dapat ditelusuri.
- Data tervalidasi dapat diproses oleh modul rekonsiliasi.

---

# 14. MODUL 7 — REKONSILIASI OTOMATIS DAN PEMBAYARAN

## 14.1 Deskripsi

Modul Rekonsiliasi menjadi salah satu fitur inti penelitian.

Modul ini membandingkan data penimbangan dari koperasi dengan tiket timbang PKS, mengidentifikasi perbedaan, dan mendukung penyusunan rincian transaksi keuangan.

## 14.2 Fitur Utama

**FR-REC-001 — Pencocokan Dokumen**

Sistem mencocokkan:

- Nomor e-DO.
- Identitas PKS.
- Nomor tiket timbang.
- Identitas kendaraan.
- Referensi muatan.
- Data berat penimbangan.

**FR-REC-002 — Perhitungan Selisih Berat**

Rumus dasar:

Selisih Berat = Berat Acuan Koperasi − Berat Acuan PKS

Persentase Selisih = (Selisih Berat / Berat Acuan Koperasi) × 100%

Dasar berat yang dibandingkan harus konsisten. Berat netto sebelum grading tidak boleh dicampur dengan berat setelah potongan grading tanpa penyesuaian.

**FR-REC-003 — Penerapan Toleransi**

Proposal tesis menggunakan contoh ambang toleransi susut 1,5%.

Untuk implementasi, ambang harus dapat dikonfigurasi sesuai ketentuan dan perjanjian yang berlaku.

**FR-REC-004 — Status Rekonsiliasi**

Status yang disarankan:

- Menunggu Tiket PKS.
- Siap Direkonsiliasi.
- Matched.
- Dispute/Hold.
- Dalam Pemeriksaan.
- Diselesaikan.
- Dibatalkan.

**FR-REC-005 — Pemeriksaan Sengketa**

Jika terjadi perbedaan yang melebihi ketentuan:

- Sistem menandai transaksi.
- Sistem mencatat selisih.
- Petugas melakukan pemeriksaan.
- Petugas memasukkan alasan atau hasil klarifikasi.
- Transaksi dapat diteruskan setelah mendapat otorisasi.

**FR-REC-006 — Kalkulasi Nilai Transaksi**

Sistem menghitung nilai transaksi berdasarkan:

- Berat yang disetujui sebagai dasar pembayaran.
- Harga kontrak atau harga transaksi yang berlaku.
- Potongan sesuai ketentuan.
- Biaya yang diakui jika relevan.
- Nilai akhir transaksi.

**FR-REC-007 — Pembuatan Faktur**

Sistem dapat menyiapkan dokumen perhitungan atau faktur berdasarkan transaksi yang telah memenuhi persyaratan.

**FR-REC-008 — Persetujuan Pembayaran**

Pembayaran harus melalui proses persetujuan sesuai kewenangan.

**FR-REC-009 — Pencatatan Pembayaran**

Sistem mencatat:

- Nomor pembayaran.
- Transaksi terkait.
- Nilai pembayaran.
- Tanggal pembayaran.
- Metode pembayaran.
- Bukti atau referensi pembayaran.
- Petugas pencatat.
- Status verifikasi.

**FR-REC-010 — Transparansi Status Petani**

Petani dapat melihat status hasil transaksi dan pembayaran miliknya setelah data tersedia serta disahkan untuk ditampilkan.

## 14.3 Aturan Bisnis Rekonsiliasi

1. Rekonsiliasi hanya dapat dilakukan pada data yang valid.
2. e-DO harus terhubung dengan tiket PKS yang benar.
3. Referensi tiket yang sama tidak boleh digunakan untuk pembayaran ganda.
4. Ambang toleransi merupakan parameter yang harus disahkan.
5. Selisih dalam toleransi dapat diberi status Matched.
6. Selisih di luar toleransi harus diperiksa.
7. Hasil Matched tidak otomatis berarti dana sudah dibayarkan.
8. Harga yang digunakan harus berasal dari transaksi atau kontrak yang berlaku.
9. Selisih negatif, ketika berat PKS lebih besar daripada berat koperasi, tetap memerlukan penanganan eksplisit dan tidak boleh otomatis dianggap sebagai susut normal.
10. Setiap perubahan nilai final harus memiliki alasan dan identitas petugas.
11. Penyelesaian sengketa memerlukan keputusan manusia.
12. Transaksi yang ditahan tidak boleh dilanjutkan ke pembayaran tanpa penyelesaian resmi.

## 14.4 Aturan Bisnis Pembayaran

- Pencatatan pembayaran dipisahkan dari eksekusi transfer bank.
- Persetujuan pembayaran tidak otomatis berarti transfer berhasil.
- Status pembayaran harus mencerminkan bukti atau hasil konfirmasi yang tersedia.
- Pembayaran ganda harus dicegah.
- Koreksi pembayaran dicatat melalui mekanisme pembatalan atau penyesuaian, bukan penghapusan riwayat.
- Data rekening tidak ditampilkan pada Portal Publik.
- Pembagian nilai hasil pengiriman gabungan kepada petani harus mengikuti dasar perhitungan dan kesepakatan yang disahkan.

## 14.5 Kriteria Penerimaan

- Dua data timbang dapat dicocokkan berdasarkan referensi transaksi.
- Persentase selisih dihitung dengan benar.
- Sistem membedakan Matched dan Dispute/Hold.
- Transaksi sengketa tidak langsung menghasilkan pembayaran final.
- Rincian kalkulasi dapat ditelusuri.
- Riwayat persetujuan tersedia.
- Petani hanya dapat melihat informasi pembayaran yang menjadi hak aksesnya.

---

# 15. MODUL 8 — DASHBOARD EKSEKUTIF DAN ANALITIK

## 15.1 Deskripsi

Dashboard Eksekutif menyediakan ringkasan informasi operasional dan keuangan Unit Agro Niaga.

## 15.2 Fitur Utama

**FR-DSH-001 — Monitoring Tonase**

Menampilkan total tonase TBS berdasarkan periode, koperasi, dan PKS.

**FR-DSH-002 — Monitoring Harga**

Menampilkan harga dari beberapa PKS serta perubahan harga berdasarkan periode.

**FR-DSH-003 — Monitoring Transaksi**

Menampilkan jumlah transaksi penerimaan dan pengiriman.

**FR-DSH-004 — Monitoring Rekonsiliasi**

Menampilkan jumlah transaksi:

- Menunggu rekonsiliasi.
- Matched.
- Dispute/Hold.
- Selesai.

**FR-DSH-005 — Monitoring Keuangan**

Menampilkan nilai transaksi, pembayaran, dan margin yang dapat dihitung berdasarkan data tervalidasi.

**FR-DSH-006 — Kinerja Mitra**

Menampilkan informasi volume pasokan berdasarkan koperasi serta volume penerimaan berdasarkan PKS.

**FR-DSH-007 — Laporan**

Sistem menyediakan penyaringan data dan ekspor laporan sesuai kebutuhan operasional.

## 15.3 Aturan Bisnis

- Data dashboard berasal dari catatan transaksi sistem.
- Setiap metrik harus memiliki definisi perhitungan yang jelas.
- Transaksi dibatalkan tidak boleh dihitung sebagai transaksi berhasil.
- Margin tidak boleh ditampilkan sebagai keuntungan bersih apabila komponen biaya belum lengkap.
- Status pembaruan data harus dapat diketahui.
- Informasi keuangan hanya dapat diakses pengguna berwenang.

## 15.4 Kriteria Penerimaan

- Dashboard menampilkan informasi sesuai hak akses.
- Total transaksi konsisten dengan data sumber.
- Filter periode bekerja dengan benar.
- Nilai agregasi diperbarui setelah transaksi sumber berubah.
- Laporan dapat ditelusuri ke transaksi pembentuknya.

---

# 16. ALUR BISNIS END-TO-END

## 16.1 Alur Informasi Publik

1. Masyarakat membuka website.
2. Sistem menampilkan halaman Portal Publik.
3. Pengunjung memilih menu Harga TBS.
4. Sistem menampilkan harga terverifikasi dari PKS yang datanya tersedia.
5. Pengunjung membandingkan harga.
6. Pengunjung memilih salah satu PKS.
7. Sistem menampilkan detail perusahaan dan harga.
8. Pengunjung membuka lokasi PKS.
9. Sistem menyediakan informasi alamat dan navigasi.

**Hasil:** Masyarakat memperoleh informasi tanpa login.

## 16.2 Alur Pembaruan Harga

1. Petugas memperoleh informasi harga dari sumber yang diizinkan.
2. Petugas memasukkan harga PKS.
3. Sistem memvalidasi format, kategori, sumber, dan periode.
4. Harga masuk status menunggu verifikasi.
5. Petugas berwenang memeriksa harga.
6. Harga disetujui atau ditolak.
7. Harga yang disetujui dipublikasikan.
8. Sistem menyimpan riwayat.
9. Portal Publik menampilkan harga terbaru yang tersedia.

**Hasil:** Informasi harga dapat dipertanggungjawabkan.

## 16.3 Alur Penerimaan Panen

1. Petani menyerahkan TBS kepada koperasi.
2. Operator koperasi memilih identitas petani.
3. Operator membuat transaksi penerimaan.
4. TBS ditimbang.
5. Hasil grading dicatat.
6. Sistem menghitung berat.
7. Operator menyimpan transaksi.
8. Sistem memberikan nomor transaksi.
9. Transaksi masuk daftar muatan yang dapat dialokasikan.

**Hasil:** Penerimaan TBS memiliki catatan digital yang dapat ditelusuri.

## 16.4 Alur Pengiriman TBS

1. Petugas memeriksa daftar penerimaan siap kirim.
2. Perumda menentukan PKS tujuan berdasarkan kontrak dan informasi operasional.
3. Petugas memilih transaksi muatan.
4. Sistem memeriksa alokasi dan kuota.
5. Data kendaraan dan sopir dimasukkan.
6. Sistem menghasilkan e-DO.
7. Muatan diberangkatkan.
8. Status pengiriman diperbarui.
9. PKS menerima kendaraan.
10. Petugas memverifikasi e-DO.

**Hasil:** Data pengiriman terhubung dengan asal muatan dan tujuan.

## 16.5 Alur Penimbangan PKS

1. Petugas PKS membuka data pengiriman.
2. Petugas memverifikasi kendaraan dan e-DO.
3. Penimbangan pabrik dilakukan.
4. Petugas memasukkan hasil tiket.
5. Hasil grading dicatat.
6. Bukti tiket dilampirkan jika tersedia.
7. Data diverifikasi.
8. Sistem menandai transaksi siap direkonsiliasi.

**Hasil:** Data timbang pabrik tersedia dan terhubung dengan pengiriman.

## 16.6 Alur Rekonsiliasi

1. Sistem mengambil data berat koperasi.
2. Sistem mengambil data berat PKS.
3. Sistem memeriksa kesesuaian referensi.
4. Sistem menghitung selisih.
5. Sistem membandingkan hasil dengan aturan toleransi.
6. Jika sesuai, transaksi berstatus Matched.
7. Jika tidak sesuai, transaksi berstatus Dispute/Hold.
8. Petugas memeriksa transaksi bermasalah.
9. Hasil pemeriksaan dan otorisasi dicatat.
10. Transaksi yang memenuhi persyaratan dapat dilanjutkan.

**Hasil:** Proses pencocokan dokumen lebih terstruktur dan dapat diaudit.

## 16.7 Alur Pembayaran

1. Transaksi telah melewati validasi yang diperlukan.
2. Sistem menyiapkan kalkulasi nilai pembayaran.
3. Staf keuangan memeriksa rincian.
4. Pihak berwenang memberikan persetujuan.
5. Pembayaran dilakukan melalui prosedur keuangan yang berlaku di luar atau melalui proses terintegrasi yang kelak disetujui.
6. Bukti pembayaran dicatat dan diverifikasi.
7. Status transaksi diperbarui.
8. Petani melihat status pembayaran sesuai hak akses.

**Hasil:** Informasi pembayaran dapat dilacak tanpa mengasumsikan transfer bank otomatis.

---

# 17. ATURAN BISNIS LINTAS MODUL

## 17.1 Identitas dan Referensi

**BR-001:** Setiap petani, koperasi, PKS, kontrak, penerimaan, e-DO, tiket timbang, rekonsiliasi, dan pembayaran harus memiliki referensi unik.

**BR-002:** Hubungan antartransaksi harus mempertahankan asal data.

**BR-003:** Transaksi historis harus tetap dapat ditelusuri meskipun data master diperbarui.

## 17.2 Harga

**BR-004:** Harga PKS dan harga Disbun harus memiliki kategori sumber berbeda.

**BR-005:** Harga harus memiliki periode berlaku.

**BR-006:** Perubahan harga wajib tercatat dalam riwayat.

**BR-007:** Harga belum diverifikasi tidak dapat diklaim sebagai harga yang berlaku pada Portal Publik.

## 17.3 Penimbangan

**BR-008:** Nilai berat tidak boleh negatif.

**BR-009:** Tara tidak boleh melebihi bruto.

**BR-010:** Perhitungan berat dan potongan harus memiliki satuan serta dasar yang konsisten.

**BR-011:** Perubahan data timbang yang sudah disahkan memerlukan mekanisme koreksi dan audit.

## 17.4 Pengiriman

**BR-012:** Satu transaksi penerimaan tidak boleh dialokasikan ganda ke pengiriman aktif.

**BR-013:** Satu pengiriman dapat memuat beberapa transaksi penerimaan.

**BR-014:** Status pengiriman harus mengikuti aturan perpindahan status.

**BR-015:** Perubahan tujuan dan muatan setelah penerbitan harus melalui validasi.

## 17.5 Rekonsiliasi

**BR-016:** Rekonsiliasi memerlukan data koperasi dan PKS yang dapat dicocokkan.

**BR-017:** Transaksi yang melebihi toleransi memerlukan pemeriksaan.

**BR-018:** Ambang toleransi disimpan sebagai konfigurasi yang memiliki riwayat.

**BR-019:** Status Matched tidak berarti pembayaran selesai.

## 17.6 Pembayaran

**BR-020:** Nilai pembayaran harus berasal dari data yang disetujui.

**BR-021:** Pembayaran memerlukan otorisasi.

**BR-022:** Pembayaran ganda harus dicegah.

**BR-023:** Riwayat transaksi keuangan tidak boleh dihapus secara langsung.

## 17.7 Keamanan

**BR-024:** Portal Publik tidak boleh mengakses data pribadi atau keuangan internal.

**BR-025:** Seluruh aktivitas penting dicatat dalam audit log.

**BR-026:** Akses ditentukan oleh peran dan cakupan data.

---

# 18. KEBUTUHAN DATA TINGKAT PRODUK

PRD menetapkan objek data bisnis yang diperlukan tanpa menentukan struktur tabel fisik.

| Objek Data      | Informasi Utama                                 |
| --------------- | ----------------------------------------------- |
| Pengguna        | Identitas akun, peran, status                   |
| Petani          | Identitas petani, koperasi terkait              |
| Kebun           | Pemilik, lokasi, luas, STDB                     |
| Koperasi        | Identitas, alamat, status kerja sama            |
| PKS             | Perusahaan, pabrik, alamat, koordinat           |
| Harga TBS       | PKS, kategori, nominal, sumber, periode, status |
| Harga Disbun    | Kategori, nominal, sumber resmi, periode        |
| Kontrak         | PKS, harga/ketentuan, periode, kuota            |
| Penerimaan      | Petani, koperasi, waktu, hasil timbang          |
| Grading         | Hasil pemeriksaan, potongan, dasar perhitungan  |
| Armada          | Kendaraan, sopir, identitas operasional         |
| e-DO            | Nomor dokumen, muatan, tujuan, status           |
| Detail Muatan   | Hubungan e-DO dengan penerimaan TBS             |
| Tiket PKS       | Nomor tiket, referensi e-DO, berat, mutu        |
| Rekonsiliasi    | Data pembanding, selisih, keputusan, status     |
| Faktur          | Referensi transaksi, nilai, status              |
| Pembayaran      | Nilai, bukti, tanggal, verifikasi               |
| Audit Aktivitas | Pelaku, tindakan, waktu, perubahan              |

Kebutuhan relasi, kardinalitas, indeks, normalisasi, dan struktur database akan dirinci dalam Database Design Document (DBD).

---

# 19. KEBUTUHAN NON-FUNGSIONAL

Target dalam bagian ini adalah sasaran desain dan pengujian yang diusulkan, bukan hasil ukur aktual.

## 19.1 Keamanan

**NFR-001**

Sistem harus menerapkan autentikasi yang aman untuk pengguna internal.

**NFR-002**

Password tidak boleh disimpan dalam bentuk teks asli.

**NFR-003**

Hak akses harus diverifikasi pada server, bukan hanya menyembunyikan menu frontend.

**NFR-004**

Sistem harus melindungi data dari akses tidak sah, manipulasi, dan injeksi masukan berbahaya.

**NFR-005**

Perubahan data sensitif harus memiliki jejak audit.

## 19.2 Kinerja

**NFR-006**

Sebagai target awal sesuai proposal, operasi transaksi penimbangan dan rekonsiliasi diupayakan memiliki waktu respons maksimal 3 detik pada kondisi pengujian yang didefinisikan.

**NFR-007**

Portal Publik harus dioptimalkan untuk koneksi seluler.

**NFR-008**

Pencarian harga dan lokasi harus dapat digunakan tanpa menunggu pemuatan keseluruhan data internal.

Kinerja aktual harus dibuktikan menggunakan skenario, perangkat, dan kondisi jaringan yang terdokumentasi.

## 19.3 Ketersediaan

**NFR-009**

Target rancangan ketersediaan adalah minimal 99% pada jam operasional yang ditetapkan, mengikuti arah proposal.

Target tersebut memerlukan definisi lingkungan, mekanisme pemantauan, serta periode pengukuran. Prototipe lokal tidak dapat diklaim memenuhi target uptime produksi tanpa pengujian yang sesuai.

## 19.4 Kemudahan Penggunaan

**NFR-010**

Portal Publik harus dapat digunakan tanpa pelatihan khusus.

**NFR-011**

Antarmuka harus berbahasa Indonesia yang mudah dipahami.

**NFR-012**

Halaman publik dan formulir operasional lapangan harus responsif.

**NFR-013**

Pesan kesalahan harus menjelaskan masalah dan tindakan perbaikan yang dapat dilakukan pengguna.

## 19.5 Integritas Data

**NFR-014**

Operasi transaksi penting harus menjaga konsistensi data.

**NFR-015**

Pencatatan transaksi harus memiliki waktu pembuatan dan pembaruan.

**NFR-016**

Pengubahan transaksi yang sudah disahkan harus dapat ditelusuri.

**NFR-017**

Sistem harus mencegah transaksi dan pembayaran ganda.

## 19.6 Pemeliharaan

**NFR-018**

Sistem harus memiliki pemisahan fungsi yang memudahkan pengembangan dan pengujian.

**NFR-019**

Aturan harga, grading, dan toleransi yang dapat berubah tidak boleh dipaksakan sebagai nilai permanen pada antarmuka.

**NFR-020**

Sistem harus memiliki dokumentasi teknis dan prosedur pengujian.

---

# 20. PERSYARATAN UI/UX

## 20.1 Prinsip Desain

Desain aplikasi harus:

- Profesional dan sederhana.
- Memprioritaskan keterbacaan.
- Menghindari istilah teknis yang tidak diperlukan.
- Konsisten dalam warna, navigasi, dan komponen.
- Menampilkan informasi terpenting terlebih dahulu.
- Mengurangi jumlah langkah untuk pekerjaan rutin.
- Memberikan umpan balik setelah tindakan.
- Menyediakan konfirmasi sebelum tindakan penting.
- Menampilkan kondisi kosong, memuat, gagal, dan berhasil secara jelas.
- Mempertimbangkan pengguna dengan kemampuan teknologi yang beragam.

## 20.2 Portal Publik

Portal Publik harus mengutamakan penggunaan melalui ponsel.

Prioritas tampilan:

1. Informasi harga TBS.
2. Perbandingan PKS.
3. Lokasi pabrik.
4. Informasi perusahaan.
5. Kontak dan kemitraan.

Pengunjung tidak perlu melihat menu teknis, dashboard keuangan, atau struktur modul internal.

## 20.3 Portal Internal

Portal Internal harus menggunakan navigasi sesuai tugas masing-masing peran.

Untuk desktop:

- Navigasi utama mudah ditemukan.
- Tabel dapat dicari dan difilter.
- Formulir memiliki label yang jelas.
- Status transaksi ditampilkan konsisten.
- Aksi kritis dibedakan dari aksi biasa.

Untuk mobile:

- Fitur penimbangan dan penerimaan tetap dapat digunakan.
- Tidak ada horizontal overflow yang menghambat pekerjaan.
- Ukuran tombol sesuai penggunaan layar sentuh.
- Formulir panjang dibagi menjadi bagian yang mudah dipahami.

## 20.4 Aksesibilitas

Sistem perlu memperhatikan:

- Kontras teks.
- Ukuran tulisan.
- Label formulir.
- Navigasi keyboard.
- Pesan kesalahan yang dapat dipahami.
- Indikator status yang tidak hanya mengandalkan warna.
- Tampilan yang tetap dapat digunakan ketika ukuran layar berubah.

---

# 21. INTEGRASI PIHAK KETIGA

## 21.1 Sumber Harga TBS

Mekanisme utama tahap awal:

- Petugas memasukkan harga dari sumber yang diizinkan.
- Sumber dan periode disimpan.
- Harga diverifikasi.
- Harga dipublikasikan.

Jika PKS menyediakan API resmi, integrasi dapat dipertimbangkan pada tahap berikutnya.

Tidak diasumsikan bahwa seluruh PKS menyediakan layanan API terbuka.

## 21.2 Peta Digital

Sistem dapat memanfaatkan layanan peta untuk menampilkan titik lokasi dan navigasi.

Kebutuhan produk tidak mewajibkan penyedia peta tertentu.

Pemilihan penyedia, biaya, syarat pemakaian, dan metode integrasi akan ditentukan dalam TRD.

## 21.3 Sistem Timbangan

Integrasi langsung dengan jembatan timbang bukan persyaratan wajib prototipe.

Sebagai baseline, sistem mendukung input hasil timbang berdasarkan bukti resmi yang diverifikasi.

## 21.4 Sistem Pembayaran

Transfer otomatis melalui bank atau payment gateway tidak termasuk kebutuhan inti tahap tesis.

Sistem cukup mendukung perhitungan, otorisasi, pencatatan pembayaran, serta pemantauan status dan bukti transaksi.

---

# 22. INDIKATOR KEBERHASILAN PRODUK

## 22.1 Keberhasilan Fungsional

Indikator yang diusulkan:

- Seluruh skenario bisnis kritis berhasil dijalankan.
- Perhitungan berat sesuai rumus.
- Perhitungan selisih sesuai data pembanding.
- Hak akses tidak dapat dilewati.
- Dokumen pengiriman terhubung dengan tiket PKS.
- Transaksi pembayaran tidak tercatat ganda.
- Portal Publik dapat digunakan tanpa autentikasi.

Target awal adalah seluruh pengujian kritis berstatus lulus. Hasil aktual harus dicatat setelah implementasi.

## 22.2 Penerimaan Pengguna

Evaluasi dilakukan menggunakan User Acceptance Testing (UAT).

Sasaran awal yang diusulkan adalah tingkat penerimaan minimal 81%, mengikuti kategori "Sangat Layak" dalam instrumen proposal.

Nilai ini merupakan target evaluasi, bukan hasil penelitian yang telah diperoleh.

## 22.3 Usability

Evaluasi dilakukan menggunakan System Usability Scale (SUS).

Sasaran awal adalah rata-rata skor SUS minimal 68.

Interpretasi hasil harus mengikuti referensi dan pedoman yang dipilih secara konsisten dalam metodologi penelitian.

## 22.4 Efisiensi Operasional

Sebagai penguatan terhadap proposal, penelitian sebaiknya mengukur efisiensi menggunakan skenario kerja yang setara.

Indikator yang disarankan:

| Indikator                   | Cara Pengukuran                                                   |
| --------------------------- | ----------------------------------------------------------------- |
| Waktu pencatatan penerimaan | Durasi menyelesaikan transaksi dengan prosedur lama dan prototipe |
| Waktu pembuatan surat jalan | Perbandingan durasi pembuatan dokumen                             |
| Waktu rekonsiliasi          | Durasi mencocokkan data kebun dan tiket PKS                       |
| Kesalahan pencatatan        | Jumlah kesalahan pada skenario pengujian setara                   |
| Kelengkapan data            | Persentase elemen wajib yang tercatat benar                       |
| Keterlacakan dokumen        | Kemampuan menemukan seluruh referensi transaksi terkait           |

Rumus pengurangan waktu proses:

Efisiensi Waktu (%) = ((Waktu Proses Lama − Waktu Proses Baru) / Waktu Proses Lama) × 100%

Pengukuran dilakukan setelah terdapat data baseline yang sah. Tidak boleh menggunakan angka hasil simulasi sebagai hasil lapangan tanpa penjelasan.

## 22.5 Partisipan Evaluasi

Proposal tesis merencanakan delapan responden dari lima kelompok pengguna:

- Dua petani.
- Dua operator koperasi.
- Dua staf operasional atau keuangan Perumda.
- Satu pimpinan Perumda.
- Satu petugas PKS.

Jumlah tersebut merupakan rencana awal dan dapat disesuaikan melalui persetujuan metodologis.

Hasil evaluasi perlu dijelaskan sesuai keterbatasan ukuran dan karakteristik sampel, bukan digeneralisasi secara berlebihan kepada seluruh pengguna.

---

# 23. PRIORITAS PENGEMBANGAN

Prioritas menggunakan kategori Must Have, Should Have, Could Have, dan Won't Have for Now.

## 23.1 Must Have — Wajib

- Portal Publik tanpa login.
- Login dan otorisasi internal.
- Master data petani, koperasi, PKS, dan kebun.
- Informasi harga multi-PKS.
- Verifikasi serta publikasi harga.
- Perbandingan harga.
- Informasi lokasi PKS.
- Penerimaan TBS.
- Penimbangan dan grading.
- Kontrak dan kuota.
- e-DO.
- Tiket timbang PKS.
- Rekonsiliasi.
- Perhitungan dan status pembayaran.
- Dashboard operasional.
- Audit aktivitas penting.
- Pengujian fungsional.
- Skenario bisnis end-to-end.

## 23.2 Should Have — Sangat Dianjurkan

- Riwayat harga.
- Grafik tren harga.
- Ekspor laporan.
- QR Code e-DO.
- Unggah bukti tiket timbang.
- Bukti pembayaran digital.
- Filter lokasi PKS.
- Dashboard khusus Direksi.
- Pengukuran durasi proses operasional.
- Optimasi pengalaman mobile.

## 23.3 Could Have — Pengembangan Tambahan

- Notifikasi perubahan harga.
- Notifikasi status pengiriman.
- Integrasi API harga PKS.
- Perbandingan estimasi margin antar-PKS.
- Perhitungan estimasi biaya logistik.
- Fitur pencarian PKS berdasarkan jarak.
- Ekspor dokumen ke berbagai format.
- Pengingat kontrak berakhir.

## 23.4 Won't Have for Now — Tidak Dikembangkan Saat Ini

- AI prediksi harga.
- GPS real-time.
- Transfer bank otomatis.
- Marketplace jual beli sawit terbuka.
- Integrasi seluruh PKS nasional.
- Aplikasi mobile native terpisah.
- Pengendalian perangkat timbangan industri.
- ERP untuk unit Listrik dan Gas.

---

# 24. TAHAPAN IMPLEMENTASI

## Tahap 1 — Fondasi Produk

Fokus:

- Struktur Portal Publik dan Internal.
- Pengguna dan hak akses.
- Master data.
- PKS dan lokasi.
- Harga multi-PKS.
- Verifikasi harga.
- Peta informasi.
- Kontrak dasar.

Keluaran:

- Masyarakat dapat melihat informasi publik.
- Petugas dapat mengelola data dasar.
- Data PKS dan harga siap digunakan transaksi.

## Tahap 2 — Operasional Rantai Pasok

Fokus:

- Penerimaan TBS.
- Penimbangan.
- Grading.
- Konsolidasi muatan.
- e-DO.
- Penerimaan PKS.
- Tiket timbang.
- Rekonsiliasi.
- Administrasi pembayaran.

Keluaran:

- Satu transaksi dapat dijalankan dari penerimaan hingga penyelesaian pembayaran yang dicatat.

## Tahap 3 — Monitoring dan Evaluasi

Fokus:

- Dashboard eksekutif.
- Laporan.
- Audit aktivitas.
- Pengujian fungsional.
- UAT.
- SUS.
- Pengukuran efisiensi.
- Penyempurnaan berdasarkan hasil evaluasi.

Keluaran:

- Prototipe siap didemonstrasikan.
- Hasil pengujian terdokumentasi.
- Bukti evaluasi tersedia untuk laporan tesis.

---

# 25. KRITERIA PENERIMAAN PRODUK SECARA KESELURUHAN

Produk dapat dinyatakan memenuhi baseline PRD apabila:

**AC-001:** Portal Publik dapat digunakan tanpa login.

**AC-002:** Pengunjung dapat melihat informasi harga TBS yang telah diverifikasi.

**AC-003:** Pengunjung dapat membandingkan harga beberapa PKS yang memiliki data layak dibandingkan.

**AC-004:** Informasi lokasi PKS dapat ditampilkan berdasarkan data yang tersedia.

**AC-005:** Pengguna internal memiliki akses sesuai peran dan cakupan data.

**AC-006:** Data petani, koperasi, PKS, dan kebun dapat dikelola secara konsisten.

**AC-007:** Transaksi penerimaan TBS dapat dicatat dan ditelusuri.

**AC-008:** Perhitungan bruto, tara, netto, dan grading mengikuti aturan yang ditetapkan.

**AC-009:** Kontrak dan kuota dapat dihubungkan dengan pengiriman.

**AC-010:** e-DO memiliki referensi unik dan dapat dikaitkan dengan muatan.

**AC-011:** Tiket timbang PKS dapat dikaitkan dengan e-DO.

**AC-012:** Sistem menghitung selisih penimbangan dengan benar.

**AC-013:** Sistem membedakan transaksi Matched dan Dispute/Hold.

**AC-014:** Transaksi yang memerlukan pemeriksaan tidak dapat melewati otorisasi secara tidak sah.

**AC-015:** Nilai dan status pembayaran dapat dicatat serta diverifikasi.

**AC-016:** Dashboard menyajikan data yang konsisten dengan transaksi.

**AC-017:** Perubahan data penting memiliki jejak audit.

**AC-018:** Proses bisnis utama dapat didemonstrasikan dari awal sampai akhir.

**AC-019:** Skenario pengujian kritis dilaksanakan dan hasilnya terdokumentasi.

**AC-020:** Instrumen UAT dan SUS dapat diterapkan pada prototipe yang telah dikembangkan.

---

# 26. RISIKO DAN MITIGASI

| Risiko                                     | Dampak                                            | Mitigasi                                                    |
| ------------------------------------------ | ------------------------------------------------- | ----------------------------------------------------------- |
| PKS tidak menyediakan API                  | Harga dan tiket tidak dapat disinkronkan langsung | Input manual terverifikasi sebagai baseline                 |
| Informasi harga terlambat                  | Informasi publik tidak mutakhir                   | Tanggal berlaku, waktu pembaruan, dan indikator kedaluwarsa |
| Data lokasi tidak lengkap                  | Peta kurang akurat                                | Verifikasi koordinat dan dukungan alamat tanpa pin          |
| Selisih timbang dipengaruhi banyak faktor  | Kesimpulan rekonsiliasi keliru                    | Pemeriksaan manusia dan audit                               |
| Aturan grading antar-PKS berbeda           | Perhitungan tidak sesuai kontrak                  | Konfigurasi berdasarkan kesepakatan                         |
| Data pembayaran sensitif                   | Risiko kebocoran informasi                        | RBAC, audit, dan pembatasan data                            |
| Pengguna memiliki literasi digital berbeda | Kesulitan mengoperasikan aplikasi                 | Desain sederhana dan pengujian SUS                          |
| Koneksi internet terbatas                  | Proses lapangan terganggu                         | Formulir ringan, pesan kegagalan, dan mekanisme retry aman  |
| Keterbatasan data penelitian               | Evaluasi kurang representatif                     | Skenario terkontrol dan dokumentasi keterbatasan            |
| Ruang lingkup terlalu luas                 | Pengembangan tidak selesai                        | Prioritas fitur dan tahapan implementasi                    |

---

# 27. ASUMSI DAN KEPUTUSAN YANG PERLU DIVALIDASI

Beberapa aspek berikut tidak ditetapkan secara final oleh proposal dan informasi tambahan, sehingga memerlukan konfirmasi dari pihak terkait.

| Kode    | Hal yang Perlu Divalidasi                | Keputusan Sementara                                                       |
| ------- | ---------------------------------------- | ------------------------------------------------------------------------- |
| DEC-001 | Nama resmi dan struktur unit usaha       | Menggunakan istilah Unit Agro Niaga                                       |
| DEC-002 | Cakupan perusahaan pada peta             | Kantor Perumda serta PKS mitra yang informasinya diizinkan dipublikasikan |
| DEC-003 | Sumber harga masing-masing PKS           | Input terverifikasi oleh petugas                                          |
| DEC-004 | Frekuensi pembaruan harga                | Berdasarkan periode berlaku dan ketersediaan sumber                       |
| DEC-005 | Kategori harga antar-PKS                 | Mengikuti spesifikasi harga yang dapat dibandingkan                       |
| DEC-006 | Batas toleransi berat                    | Contoh awal 1,5%, menunggu validasi SOP                                   |
| DEC-007 | Formula grading                          | Mengikuti aturan kontrak/PKS                                              |
| DEC-008 | Pihak penerbit e-DO                      | Operator koperasi atau staf Perumda sesuai SOP                            |
| DEC-009 | Akses langsung petugas PKS               | Diberikan untuk PKS pilot jika disetujui                                  |
| DEC-010 | Proses pembayaran aktual                 | Pencatatan dan verifikasi tanpa transfer otomatis                         |
| DEC-011 | Alokasi hasil gabungan untuk tiap petani | Berdasarkan metode yang disepakati Perumda dan koperasi                   |
| DEC-012 | Sumber data observasi awal dan baseline  | Menunggu pengumpulan data lapangan                                        |
| DEC-013 | Ambang persetujuan pembayaran Direksi    | Berdasarkan kewenangan resmi                                              |
| DEC-014 | Kelengkapan data lokasi                  | Alamat wajib, koordinat untuk PKS yang dipetakan                          |
| DEC-015 | Bentuk dokumen ekspor                    | Ditentukan dari kebutuhan pengguna saat validasi                          |

Keputusan yang belum disahkan tidak boleh diperlakukan sebagai fakta operasional Perumda atau hasil penelitian.

---

# 28. KETERKAITAN PRODUK DENGAN TESIS

## 28.1 Fokus Ilmiah

Produk dikembangkan sebagai artefak penelitian terapan dengan metode Design Science Research Methodology.

## 28.2 Luaran yang Diharapkan

1. Model proses bisnis rantai pasok TBS.
2. Spesifikasi kebutuhan sistem multi-aktor.
3. Model arsitektur sistem informasi enterprise.
4. Prototipe web terintegrasi.
5. Mekanisme rekonsiliasi data timbangan.
6. Hasil evaluasi fungsionalitas.
7. Hasil evaluasi penerimaan pengguna.
8. Hasil evaluasi kebergunaan.
9. Hasil pengukuran efisiensi operasional jika data dan rancangan evaluasi memungkinkan.

## 28.3 Implementasi Tahapan DSRM

| Tahap DSRM                   | Aktivitas Produk                         | Luaran                       |
| ---------------------------- | ---------------------------------------- | ---------------------------- |
| Identifikasi Masalah         | Observasi, wawancara, analisis proses    | Daftar masalah dan kebutuhan |
| Perumusan Tujuan             | Penyusunan PRD dan kriteria keberhasilan | Sasaran solusi               |
| Perancangan dan Pengembangan | TRD, AFD, DBD, BSD, IPD dan implementasi | Model serta prototipe        |
| Demonstrasi                  | Simulasi transaksi end-to-end            | Bukti demonstrasi            |
| Evaluasi                     | Black Box, UAT, SUS, efisiensi           | Hasil pengujian              |
| Komunikasi                   | Dokumentasi penelitian dan rekomendasi   | Laporan tesis                |

## 28.4 Penegasan Kontribusi

Kebaruan penelitian tidak boleh hanya dinyatakan karena aplikasi menggunakan website atau memiliki banyak fitur.

Kontribusi yang akan dievaluasi meliputi:

- Kesesuaian model proses bisnis dengan kebutuhan rantai pasok Agro Niaga BUMD.
- Integrasi data dan keterlacakan transaksi antaraktor.
- Mekanisme pencocokan dan penanganan selisih timbang.
- Kelayakan artefak dalam mendukung pekerjaan pengguna.
- Bukti perubahan efisiensi operasional jika dapat diukur.

Klaim kebaruan final harus disusun berdasarkan kajian penelitian terdahulu yang sumbernya telah diverifikasi.

---

# 29. HUBUNGAN PRD DENGAN DOKUMEN LANJUTAN

PRD merupakan dokumen induk kebutuhan produk.

Kelima dokumen berikutnya harus mengacu pada baseline ini.

## 29.1 Technical Requirements Document (TRD)

Mendefinisikan:

- Pilihan teknologi.
- Arsitektur teknis.
- Kebutuhan backend dan frontend.
- Sistem autentikasi.
- Kontrak API.
- Keamanan teknis.
- Performa.
- Integrasi.
- Deployment dan pengujian.

## 29.2 Application Flow Document (AFD)

Mendefinisikan:

- User journey.
- Alur navigasi.
- Alur transaksi per peran.
- Perpindahan status.
- Percabangan proses.
- Penanganan error.
- Diagram alur.
- Interaksi antarmodul.

## 29.3 Database Design Document (DBD)

Mendefinisikan:

- Entitas dan atribut.
- Primary key dan foreign key.
- Relasi data.
- Normalisasi.
- Aturan integritas.
- Indeks dan constraint.
- Riwayat perubahan.
- Skema migrasi.

## 29.4 Business System Document (BSD)

Mendefinisikan:

- SOP bisnis.
- Aturan harga.
- Aturan kontrak.
- Perhitungan timbangan.
- Ketentuan grading.
- Rekonsiliasi.
- Persetujuan pembayaran.
- Penanganan sengketa.
- Kebijakan audit dan kewenangan.

## 29.5 Implementation Plan Document (IPD)

Mendefinisikan:

- Tahapan pekerjaan.
- Urutan implementasi.
- Milestone.
- Ketergantungan.
- Strategi pengujian.
- Kriteria penyelesaian.
- Manajemen risiko.
- Validasi akhir.

---

# 30. DEFINITION OF DONE

Suatu fitur dinyatakan selesai apabila:

1. Kebutuhannya memiliki identitas requirement yang jelas.
2. Alur penggunaan telah diimplementasikan.
3. Hak akses telah diterapkan.
4. Validasi input telah tersedia.
5. Kondisi berhasil dan gagal ditangani.
6. Data disimpan atau diambil secara konsisten.
7. Operasi penting memiliki jejak audit jika relevan.
8. Skenario pengujian lulus.
9. Tidak menimbulkan regresi pada fitur terkait.
10. Dokumentasi fitur telah diperbarui.

Produk secara keseluruhan dinyatakan siap untuk evaluasi tesis apabila alur transaksi inti dapat didemonstrasikan, skenario uji kritis selesai, dan instrumen evaluasi dapat digunakan oleh responden penelitian.

---

# 31. KESIMPULAN

Product Requirements Document ini menetapkan kebutuhan awal pengembangan Sistem Informasi Terintegrasi Rantai Pasok Tandan Buah Segar pada Perumda Tuah Sekata, dengan fokus pada Unit Agro Niaga.

Sistem dirancang memiliki dua lingkungan utama, yaitu Portal Publik yang dapat diakses tanpa login serta Portal Internal yang mengelola proses perdagangan TBS secara terintegrasi.

Portal Publik difokuskan pada transparansi informasi harga pembelian TBS dari beberapa pabrik, perbandingan harga, informasi lokasi PKS, serta informasi perusahaan.

Portal Internal mendukung pengelolaan master data, penerimaan dan penimbangan TBS, kontrak niaga, logistik, tiket timbang pabrik, rekonsiliasi otomatis, administrasi pembayaran, dan dashboard eksekutif.

Pengembangan mengikuti delapan modul utama yang telah ditetapkan pada proposal tesis dengan penyesuaian kebutuhan publik dan informasi multi-PKS.

PRD ini menjadi baseline kebutuhan yang akan diturunkan menjadi rancangan teknis, alur aplikasi, desain basis data, aturan bisnis terperinci, dan rencana implementasi.

**Status akhir dokumen: DRAFT PRD V1.0 — SIAP MENJADI DASAR PENYUSUNAN TRD, DENGAN SEJUMLAH KEPUTUSAN OPERASIONAL YANG MASIH MEMERLUKAN VALIDASI.**

**Akhir Dokumen — Product Requirements Document V1.0**
