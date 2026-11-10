
# BUSINESS SYSTEM DOCUMENT (BSD)

## SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TANDAN BUAH SEGAR (TBS)

### PERUMDA TUAH SEKATA — UNIT AGRO NIAGA

**Versi:** 1.1 — Business Rules & Operations Baseline
**Tanggal:** 10 November 2026
**Status:** Draft untuk Validasi Operasional
**Dokumen Induk:** PRD V1.1, TRD V1.1, AFD V1.1, DBD V1.1
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

Tidak semua aturan dalam BSD merupakan SOP Perumda. Setiap aturan memakai salah satu status berikut dan status dicatat bersama sumber, pemilik keputusan, serta tanggal peninjauan bila tersedia:

| Status | Makna |
| --- | --- |
| **Confirmed Business Rule** | Didukung SOP, kontrak, regulasi, atau konfirmasi pemilik proses yang terdokumentasi. |
| **Prototype Simulation Rule** | Nilai/perilaku untuk demonstrasi terkontrol; bukan ketentuan resmi Perumda. |
| **Pending SOP Validation** | Menunggu keputusan Perumda atau mitra; implementasi tidak boleh menganggap nilai resmi. |
| **Future Business Rule** | Di luar baseline sampai ada kebutuhan, otorisasi, dan scope yang disetujui. |

Rancangan tanpa bukti konfirmasi berstatus Pending SOP Validation. Contoh angka/formula yang digunakan pada demo diberi status Prototype Simulation Rule.

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

Business System Document V1.1 menetapkan aturan bisnis awal untuk pengembangan Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata, Unit Agro Niaga.

Dokumen mengatur proses dari publikasi informasi harga, penerimaan petani, penimbangan, grading, kontrak, kuota, pengiriman, tiket PKS, rekonsiliasi, penyelesaian sengketa, penagihan, hingga pencatatan pembayaran.

Aturan utama yang ditekankan adalah keterlacakan sumber panen, konsistensi berat dan harga, pencegahan transaksi ganda, pengendalian kewenangan, serta pemisahan status operasional dan keuangan.

Informasi harga acuan, harga informasi PKS, dan harga transaksi harus dibedakan.

Perhitungan grading dan selisih timbang harus menggunakan dasar yang jelas agar tidak terjadi pemotongan ganda atau kesalahan nilai.

Transaksi multi-petani harus mempertahankan hubungan asal muatan dan menggunakan metode alokasi yang telah disahkan.

Keputusan pembayaran harus mengikuti model bisnis dan kewenangan yang sah.

BSD ini menjadi dasar implementasi business logic pada Domain Layer setiap modul backend, sekaligus sumber penyusunan pengujian aturan bisnis dan skenario end-to-end.

**STATUS: BSD V1.1 — BUSINESS RULES BASELINE, MENUNGGU VALIDASI KEPUTUSAN OPERASIONAL**

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

- Product Requirements Document V1.1.
- Technical Requirements Document V1.1.
- Application Flow Document V1.1.
- Database Design Document V1.1.
- Proposal Tesis Givo Vrabora Revisi Final V2.

**Akhir Dokumen — Business System Document V1.1**
