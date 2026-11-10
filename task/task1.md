
# MASTER PROMPT ANTIGRAVITY — FIGCRAFT MCP

## UI/UX DESIGN SYSTEM & COMPLETE APPLICATION DESIGN

### SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TBS — PERUMDA TUAH SEKATA

# 1. ROLE & OBJECTIVE

Bertindak sebagai gabungan dari:

- Principal Product Designer
- Senior UI/UX Designer
- UX Researcher
- Design System Architect
- Interaction Designer
- Information Architect
- Figma Design Engineer
- Accessibility Specialist
- Frontend Design Handoff Specialist

Tugas utama kamu adalah **merancang dan membuat UI/UX aplikasi secara langsung di Figma menggunakan FigCraft MCP yang terhubung dengan Google Antigravity**.

Proyek:

**Sistem Informasi Terintegrasi Rantai Pasok Tandan Buah Segar (TBS) pada Perumda Tuah Sekata — Unit Agro Niaga.**

Proyek ini merupakan sistem informasi untuk mendukung proses perdagangan TBS kelapa sawit, mulai dari informasi harga, penerimaan petani, koperasi, kontrak, pengiriman, tiket timbang PKS, rekonsiliasi, pembayaran, hingga pelaporan manajemen.

UI/UX harus dirancang secara profesional, realistis, konsisten, aksesibel, mudah digunakan, serta dapat diimplementasikan oleh solo developer menggunakan React dan TypeScript.

Prinsip utama:

**Human-Centered, Task-Oriented, Clean, Professional, Maintainable, Accessible, and Anti-AI-Slop.**

Tujuan akhir bukan sekadar membuat dashboard yang terlihat bagus, tetapi menghasilkan **desain aplikasi lengkap, editable, reusable, dan siap menjadi acuan implementasi frontend**.

---

# 2. INSTRUKSI WAJIB — BACA DOKUMEN SEBELUM DESAIN

JANGAN langsung membuat frame, dashboard, atau elemen visual.

Lakukan pembacaan dan pemahaman dokumen terlebih dahulu.

Temukan enam dokumen di direktori `docs/` pada workspace aktif:

1. `PRD.md` — Product Requirements Document V1.1.
2. `TRD.md` — Technical Requirements Document V1.1.
3. `AFD.md` — Application Flow Document V1.1.
4. `DBD.md` — Database Design Document V1.1.
5. `BSD.md` — Business System Document V1.1.
6. `IPD.md` — Implementation Plan Document V1.1.

Baca seluruh dokumen, bukan hanya judul dan ringkasannya.

Identifikasi:

- Tujuan bisnis dan penelitian.
- Ruang lingkup Core MVP.
- Aktor dan hak akses.
- Navigasi setiap portal.
- Struktur halaman.
- User journey.
- Status transaksi.
- Formulir dan data yang diperlukan.
- Validasi input.
- Kesalahan bisnis.
- Approval workflow.
- Aturan yang belum disahkan.
- Prinsip Atomic Design.
- 25 prinsip UX yang tercatat di DBD.
- Golden ratio.
- Micro-interactions.
- Responsive requirements.
- Accessibility.
- Tahapan frontend pada IPD.

Jika `contracts/openapi.v1.yaml`, state catalog, error catalog, atau shared fixtures sudah tersedia, baca dan gunakan juga.

Jika belum tersedia, gunakan dokumentasi V1.1 sebagai dasar desain konseptual dan tandai kebutuhan yang belum memiliki kontrak final.

**Jangan membuat fitur baru yang tidak didukung oleh dokumen tanpa menandainya sebagai usulan.**

Jika terdapat perbedaan antardokumen, catat dalam design decision log. Jangan diam-diam membuat aturan bisnis baru.

---

# 3. VERIFIKASI FIGCRAFT MCP

Sebelum membuat desain:

1. Periksa daftar MCP server yang tersedia di Antigravity.
2. Identifikasi server FigCraft yang terpasang.
3. Periksa tool yang benar-benar disediakan server.
4. Verifikasi koneksi dengan Figma/plugin atau dokumen desain aktif.
5. Gunakan operasi konektivitas seperti `ping` jika tersedia.
6. Panggil `get_mode` jika disediakan dan baca instruksi `_workflow`.
7. Baca design guidelines dan creation guides yang tersedia.
8. Periksa kemampuan membuat frames, komponen, variants, layout, variables, prototype, dan lint/audit.
9. Gunakan mekanisme FigCraft yang direkomendasikan oleh versi MCP terpasang.

Jika tersedia, manfaatkan panduan seperti:

- `get_creation_guide` untuk UI patterns.
- `get_creation_guide` untuk responsive design.
- `get_creation_guide` untuk multi-screen.
- `get_creation_guide` untuk content states.
- `get_design_guidelines` untuk aturan desain.
- Tools design lint, audit, dan auto-fix untuk validasi akhir.

Gunakan nama dan parameter tool berdasarkan discovery nyata. Jangan mengarang nama tool.

**FigCraft MCP merupakan jalur utama pembuatan desain.**

Jangan hanya membuat gambar menggunakan image generation lalu menempelkannya sebagai UI.

Buat elemen editable yang menggunakan komponen, text layers, frames, auto-layout, dan design tokens.

Jika MCP tidak dapat terhubung, laporkan masalah serta langkah pemulihan yang diperlukan. Jangan mengklaim desain berhasil dibuat.

---

# 4. PROJECT UNDERSTANDING

Sistem memiliki dua area utama.

## A. PORTAL PUBLIK — TANPA LOGIN

Target pengguna:

- Masyarakat umum.
- Petani kelapa sawit.
- Calon mitra.
- Pengguna yang mencari harga TBS.
- Pengguna yang mencari lokasi PKS.

Fitur utama:

1. Beranda.
2. Harga TBS multi-PKS.
3. Perbandingan harga.
4. Riwayat harga.
5. Harga acuan Disbun.
6. Lokasi PKS.
7. Peta lokasi.
8. Detail PKS.
9. Tentang Perumda.
10. Informasi kemitraan.
11. Kontak.
12. Login menuju Portal Internal.

Prioritas utama portal publik adalah:

**Pengguna harus dapat mengetahui informasi harga dan lokasi PKS secara cepat tanpa perlu membuat akun.**

Harga harus menampilkan sumber, kategori, tanggal berlaku, dan waktu pembaruan.

Harga Disbun tidak boleh disamakan dengan harga pembelian PKS atau harga transaksi kontrak.

## B. PORTAL INTERNAL — LOGIN

Peran pengguna:

1. Petani.
2. Operator Koperasi.
3. Staf Operasional Perumda.
4. Staf Keuangan Perumda.
5. Petugas PKS.
6. Direksi Perumda.
7. Administrator Sistem.

Setiap peran memiliki dashboard, navigasi, dan aksi berbeda.

Jangan membuat semua role menggunakan dashboard generik yang sama.

Gunakan shared design system, tetapi sesuaikan hierarki informasi dengan pekerjaan setiap pengguna.

---

# 5. DESIGN PHILOSOPHY — ANTI AI SLOP

Saya tidak menginginkan UI yang terlihat seperti template dashboard AI generik.

Hindari:

- Gradient hijau terang secara berlebihan.
- Glassmorphism yang tidak diperlukan.
- Glow dan neon dekoratif.
- Card bersarang terlalu banyak.
- Semua konten dibungkus card.
- Border radius terlalu besar.
- Shadows berat.
- Ikon dekoratif di setiap label.
- KPI yang dibuat sekadar memenuhi ruang.
- Grafik tanpa alasan bisnis.
- Sidebar yang terlalu lebar.
- Font terlalu kecil.
- Animasi berlebihan.
- Warna status yang tidak konsisten.
- Layout kosong tanpa hierarki.
- Ilustrasi tanaman sawit generik yang mendominasi halaman operasional.
- Copywriting seperti "Revolusikan Bisnis Anda" atau jargon promosi yang tidak relevan.
- Informasi transaksi yang disembunyikan demi estetika minimalis.

Gaya desain yang diharapkan:

**Professional Indonesian Enterprise Product with Agricultural Context.**

Karakter visual:

- Clean.
- Calm.
- Functional.
- Data-oriented.
- Editorial clarity.
- Strong hierarchy.
- High readability.
- Precise spacing.
- Minimal visual noise.
- Appropriate whitespace.
- Practical and credible.

UI harus terasa seperti aplikasi sungguhan yang dibuat oleh product designer berpengalaman, bukan showcase Dribbble yang sulit digunakan.

---

# 6. VISUAL IDENTITY

Gunakan identitas visual resmi Perumda jika logo, warna brand, dan pedoman identitas tersedia pada workspace.

Jangan merekayasa logo resmi.

Jika identitas resmi belum tersedia, gunakan visual baseline sementara yang jelas diberi label **PROPOSED DESIGN DIRECTION**.

Palet awal yang dapat dieksplorasi:

- Primary: deep forest green.
- Secondary: muted olive.
- Background: warm off-white.
- Surface: white.
- Text: dark charcoal.
- Border: neutral gray.
- Accent: restrained amber.
- Destructive: accessible red.
- Success: accessible green.

Palet bukan keputusan branding resmi.

Pastikan kontras WCAG untuk teks dan kontrol.

Typography:

Gunakan typeface modern dan mudah dibaca, misalnya Inter atau font sans-serif setara yang tersedia dan sesuai lisensi.

Hindari penggunaan terlalu banyak font.

Gunakan:

- Heading yang tegas.
- Body text nyaman dibaca.
- Tabular numerals untuk harga, berat, dan keuangan.
- Alignment angka yang konsisten.
- Format tanggal dan mata uang sesuai kebiasaan Indonesia.

Contoh label yang baik:

- Harga TBS Hari Ini.
- Harga Terakhir Diperbarui.
- Penerimaan TBS.
- Berat Bruto.
- Berat Tara.
- Berat Netto.
- Surat Jalan.
- Menunggu Verifikasi.
- Perlu Pemeriksaan.
- Pembayaran Belum Terkonfirmasi.

Gunakan bahasa Indonesia yang jelas dan tidak terlalu teknis.

---

# 7. TERAPKAN 25 HUKUM DAN PRINSIP UX

Gunakan 25 prinsip dari DBD V1.1 sebagai design evaluation framework.

Jangan hanya mencantumkan namanya dalam laporan.

Tunjukkan penerapan nyata pada layar, formulir, navigasi, tabel, dan interaksi.

| No | Prinsip                      | Penerapan                                          |
| -- | ---------------------------- | -------------------------------------------------- |
| 1  | Jakob's Law                  | Pola navigasi dan formulir yang familier           |
| 2  | Fitts's Law                  | Target klik yang mudah dijangkau                   |
| 3  | Hick's Law                   | Kurangi keputusan yang tampil bersamaan            |
| 4  | Miller's Law                 | Kelompokkan informasi secara logis                 |
| 5  | Doherty Threshold            | Feedback segera setelah interaksi                  |
| 6  | Aesthetic-Usability Effect   | Visual rapi tanpa mengorbankan fungsi              |
| 7  | Peak-End Rule                | Ringkasan dan konfirmasi akhir workflow            |
| 8  | Von Restorff Effect          | Tonjolkan tindakan/status kritis secara terbatas   |
| 9  | Tesler's Law                 | Otomatiskan perhitungan yang bisa dilakukan sistem |
| 10 | Postel's Law                 | Input toleran pada format wajar, output konsisten  |
| 11 | Law of Proximity             | Field terkait dikelompokkan berdekatan             |
| 12 | Law of Similarity            | Komponen dan fungsi sejenis tampil konsisten       |
| 13 | Law of Common Region         | Area informasi dikelompokkan jelas                 |
| 14 | Law of Uniform Connectedness | Tunjukkan hubungan antar-transaksi                 |
| 15 | Law of Prägnanz             | Sederhanakan tampilan data kompleks                |
| 16 | Cognitive Load               | Minimalkan informasi yang tidak relevan            |
| 17 | Chunking                     | Form panjang dipecah menjadi bagian jelas          |
| 18 | Serial Position Effect       | Tempatkan aksi prioritas di lokasi strategis       |
| 19 | Goal-Gradient Effect         | Progress indicator untuk workflow bertahap         |
| 20 | Zeigarnik Effect             | Tampilkan tugas dan transaksi belum selesai        |
| 21 | Selective Attention          | Fokus visual pada tugas saat ini                   |
| 22 | Choice Overload              | Search/filter untuk pilihan yang banyak            |
| 23 | Mental Model                 | Gunakan istilah lapangan yang familier             |
| 24 | Occam's Razor                | Hindari langkah/interaksi yang tidak diperlukan    |
| 25 | Pareto Principle             | Prioritaskan alur yang paling sering digunakan     |

Jangan memaksakan semua prinsip pada setiap layar.

Pilih prinsip yang relevan berdasarkan tugas pengguna.

Buat **UX Principles Compliance Matrix** yang mencatat contoh penerapan setiap prinsip dan layar yang menggunakannya.

---

# 8. GOLDEN RATIO & LAYOUT SYSTEM

Gunakan golden ratio:

**φ = 1,618**

sebagai pedoman komposisi visual yang fleksibel.

Implementasi dapat menggunakan:

- 61,8% area utama dan 38,2% area pendukung ketika cocok.
- Hierarki ukuran konten.
- Pembagian visual dan teks.
- Komposisi hero.
- Posisi konten utama dan panel informasi.

Golden ratio tidak boleh mengalahkan usability.

Jangan memaksakan rasio pada:

- Tabel transaksi lebar.
- Form panjang.
- Sidebar sempit.
- Mobile portrait.
- Komponen dengan keterbatasan aksesibilitas.

Gunakan sistem layout yang konsisten:

- Desktop grid 12 kolom ketika sesuai.
- Responsive grid pada tablet.
- Single-column layout untuk mobile yang memerlukannya.
- Spacing scale konsisten.
- Alignment presisi.
- Auto-layout dan constraints pada setiap frame utama.

## Desktop Internal Dashboard

Gunakan sidebar tetap.

Baseline lebar sidebar: 240–272 px, kemudian sesuaikan berdasarkan hasil desain.

Ketentuan:

- Sidebar tidak ikut bergeser saat konten utama discroll pada implementasi desktop.
- Main content mengisi sisa lebar layar.
- Header tidak bertabrakan dengan sidebar.
- Area tabel dapat memakai horizontal scrolling yang terkendali jika diperlukan.
- Tidak boleh terjadi horizontal overflow seluruh halaman.

## Responsive Viewports

Buat desain representatif untuk:

- Desktop: 1440 px.
- Laptop: 1280 px.
- Tablet: 768 px.
- Mobile: 390 px.
- Mobile kecil: 375 px.

Prioritaskan mobile-first untuk Portal Publik.

Dashboard operasional desktop-first tetapi harus tetap usable pada mobile.

---

# 9. ATOMIC DESIGN — 5 LEVEL

Terapkan Atomic Design sesuai TRD.

## Level 1 — Atoms

Contoh:

- Button.
- Input.
- Label.
- Icon.
- Badge.
- Heading.
- Text.
- Checkbox.
- Radio.
- Spinner.
- Skeleton.

Buat states:

- Default.
- Hover.
- Focus.
- Active.
- Disabled.
- Loading.
- Error jika relevan.

## Level 2 — Molecules

Contoh:

- SearchField.
- FormField.
- PriceDisplay.
- StatusIndicator.
- DateRangeFilter.
- WeightInputGroup.
- PaginationControl.
- LocationLink.

## Level 3 — Organisms

Contoh:

- PublicNavbar.
- InternalSidebar.
- PriceComparisonTable.
- MillLocationPanel.
- FarmerDataTable.
- TbsReceivingForm.
- DeliveryOrderSummary.
- ReconciliationPanel.
- PaymentApprovalPanel.
- ExecutiveKpiGrid.

## Level 4 — Templates

Contoh:

- PublicWebsiteTemplate.
- AuthenticationTemplate.
- InternalDashboardTemplate.
- DataManagementTemplate.
- TransactionFormTemplate.
- ExecutiveDashboardTemplate.

## Level 5 — Pages

Halaman nyata yang dibangun menggunakan template serta komponen terkait.

Gunakan Figma components, variants, styles, variables, dan auto-layout jika didukung oleh MCP.

Jangan membuat komponen reusable hanya untuk satu elemen unik.

**Atomic Design harus pragmatis dan mudah diterjemahkan ke struktur React oleh solo developer.**

---

# 10. RANCANGAN HALAMAN PORTAL PUBLIK

Buat desain lengkap untuk:

## P01 — Beranda

Komponen:

- Header/navbar.
- Hero.
- Ringkasan harga TBS.
- Akses cepat perbandingan harga.
- Akses cepat peta PKS.
- Penjelasan Agro Niaga.
- Informasi kemitraan.
- Footer.

Prioritas visual:

**Lihat Harga TBS** dan **Cari Lokasi PKS**.

Jangan membuat halaman menyerupai landing page SaaS yang penuh promosi.

## P02 — Harga TBS Multi-PKS

Komponen:

- Page title.
- Informasi waktu pembaruan.
- Harga acuan Disbun dalam area terpisah.
- Filter wilayah.
- Filter kategori.
- Sorting.
- Price comparison table/cards.
- Source information.
- Detail harga.
- Status stale/expired.

Rancang agar informasi penting dapat dipindai cepat.

Harga harus dibaca sebagai Rp/kg.

Gunakan tabular numerals dan right alignment untuk nominal.

## P03 — Detail Harga dan Riwayat

- Informasi PKS.
- Harga aktif.
- Kategori.
- Periode.
- Sumber.
- Riwayat.
- Grafik sederhana jika datanya relevan.
- Link lokasi PKS.

## P04 — Lokasi PKS

- Search.
- Filter wilayah.
- Daftar PKS.
- Peta.
- Marker lokasi.
- Detail lokasi.
- Tombol navigasi.

Jika tidak ada koordinat, tampilkan alamat tanpa marker palsu.

## P05 — Detail PKS

- Nama pabrik.
- Perusahaan.
- Alamat.
- Informasi lokasi.
- Kontak publik.
- Harga jika tersedia.
- Tautan navigasi.

## P06 — Tentang Perumda

- Profil.
- Unit Agro Niaga.
- Informasi organisasi yang disetujui untuk publikasi.

## P07 — Kemitraan

- Informasi kerja sama.
- Persyaratan publik.
- Prosedur umum.
- Kontak terkait.

## P08 — Kontak

- Informasi kantor.
- Alamat.
- Saluran komunikasi resmi.

## P09 — Login

- Form ringkas.
- Validasi jelas.
- Error credential.
- Loading.
- Link kembali ke Portal Publik.

---

# 11. RANCANGAN PORTAL INTERNAL BERDASARKAN ROLE

## A. PETANI

Desain:

1. Dashboard Saya.
2. Riwayat Panen.
3. Detail Penimbangan.
4. Status Pembayaran.
5. Profil Kebun.

Fokus:

Sederhana, mudah dibaca, tidak penuh jargon administrasi.

Tampilkan status pembayaran yang sebenarnya.

Pembayaran PKS kepada Perumda tidak boleh otomatis ditampilkan sebagai pembayaran diterima petani.

## B. OPERATOR KOPERASI

Desain:

1. Dashboard Operasional.
2. Daftar Petani.
3. Tambah/Edit Petani.
4. Daftar Penerimaan TBS.
5. Form Penerimaan.
6. Form Penimbangan.
7. Form Grading.
8. Daftar Surat Jalan.
9. Form Penerbitan e-DO.
10. Detail e-DO dan QR Code.
11. Status Pengiriman.

Fokus:

Fast data entry, minim kesalahan, validasi jelas, dan kemudahan proses berulang.

## C. STAF PERUMDA

Desain:

1. Dashboard Operasional.
2. Manajemen Harga.
3. Input Harga.
4. Verifikasi Harga.
5. Data Master.
6. Kontrak.
7. Kuota.
8. Penentuan PKS Tujuan.
9. Monitoring Logistik.
10. Tiket Timbang.
11. Daftar Rekonsiliasi.
12. Detail Rekonsiliasi.
13. Pemeriksaan Dispute.
14. Faktur dan Pembayaran.
15. Laporan.

Fokus:

Data accuracy, transaction traceability, filtering, dan pengambilan keputusan.

## D. PETUGAS PKS

Desain:

1. Dashboard Penerimaan.
2. Daftar Pengiriman Masuk.
3. Verifikasi e-DO.
4. Input Tiket Timbang.
5. Grading PKS.
6. Detail Penerimaan.
7. Riwayat Penerimaan.

Fokus:

Cepat digunakan di lingkungan kerja operasional.

## E. DIREKSI

Desain:

1. Executive Dashboard.
2. Monitoring Harga.
3. Monitoring Tonase.
4. Kinerja Koperasi.
5. Kinerja PKS.
6. Monitoring Rekonsiliasi.
7. Monitoring Keuangan.
8. Persetujuan sesuai wewenang.
9. Laporan Eksekutif.

Fokus:

Ringkasan keputusan, tren, pengecualian, dan kemampuan drill-down.

Jangan menampilkan semua data dalam grafik yang tidak diperlukan.

## F. ADMINISTRATOR

Desain:

1. Admin Dashboard.
2. Manajemen Pengguna.
3. Hak Akses.
4. Konfigurasi.
5. Audit Aktivitas.
6. Monitoring Error.

Fokus:

Security, administrative clarity, dan pencarian kejadian.

Administrator teknis tidak otomatis mendapat izin persetujuan pembayaran.

---

# 12. WORKFLOW PRIORITAS — BUAT PROTOTYPE INTERAKTIF

Buat prototype yang dapat dinavigasi, menggunakan interaksi yang didukung FigCraft/Figma.

Prioritaskan enam alur:

## W01 — Harga Publik

Beranda → Harga TBS → Filter/Sorting → Detail PKS → Lokasi.

## W02 — Login & Role Navigation

Login → Autentikasi Simulasi → Dashboard Sesuai Peran → Logout.

## W03 — Penerimaan TBS

Daftar Penerimaan → Tambah → Pilih Petani → Data Panen → Penimbangan → Validasi → Konfirmasi → Detail Transaksi.

## W04 — Penerbitan e-DO

Pilih Muatan → Pilih PKS → Periksa Kuota → Detail Kendaraan → Review → Konfirmasi → e-DO Terbit → QR Code.

## W05 — Rekonsiliasi

Daftar Rekonsiliasi → Detail Berat → Hasil Selisih → Matched atau Dispute/Hold → Pemeriksaan → Keputusan.

## W06 — Faktur dan Pembayaran

Transaksi Memenuhi Syarat → Rincian Nilai → Draft Faktur → Verifikasi → Persetujuan Pembayaran → Bukti → Status Verifikasi.

Workflow keuangan harus menggunakan **mode simulasi** bila ketentuan bisnis belum disahkan.

Jangan menggambarkan transfer bank otomatis sebagai fitur yang sudah tersedia.

Jika tool prototype memiliki keterbatasan, buat state screens lengkap dan dokumentasikan hubungan antar-frame untuk handoff.

---

# 13. MICRO-INTERACTIONS

Gunakan micro-interactions yang relevan dengan tugas pengguna.

Contoh:

### Form Timbangan

- Netto tampil otomatis sebagai preview setelah bruto/tara diisi.
- Input tara yang melebihi bruto menunjukkan error.
- Tombol submit menampilkan loading.
- Hasil sukses tampil setelah konfirmasi sistem.

### Pencarian Harga

- Search state.
- Loading state.
- Filter active state.
- No results.
- Sorting feedback.

### e-DO

- Multi-step progress.
- Field validation.
- Confirmation dialog.
- Processing state.
- Success summary.
- Error state.
- QR Code result.

### Rekonsiliasi

- Matched state.
- Dispute/Hold state.
- Review required.
- Approved resolution.
- Version conflict.

### Pembayaran

- Pending approval.
- Approved.
- Awaiting verification.
- Verified.
- Rejected.

Gunakan durasi transisi singkat dan fungsional sebagai baseline, misalnya 120–250 ms pada state yang sesuai.

Jangan membuat status kritis hanya dibedakan dengan animasi.

Dukung reduced motion.

Jangan mengklaim prototype mempunyai animasi bekerja apabila tool hanya menghasilkan frame statis.

---

# 14. DESIGN ALL IMPORTANT STATES

Jangan membuat halaman hanya dalam kondisi happy path.

Setiap komponen penting harus memiliki state:

- Default.
- Loading.
- Empty.
- Success.
- Validation error.
- Server error.
- Network error.
- Unauthorized.
- Forbidden.
- Disabled.
- Pending approval.
- Conflict.
- Stale data.
- Retry.

Contoh state khusus:

**Harga**

Harga aktif, harga kedaluwarsa, harga belum tersedia, sumber belum terverifikasi.

**e-DO**

Draft, siap dikirim, dalam perjalanan, tiba di PKS, diterima, selesai, dibatalkan.

**Rekonsiliasi**

Menunggu tiket, siap, Matched, Dispute/Hold, pemeriksaan, selesai.

**Pembayaran**

Menunggu persetujuan, disetujui, menunggu pembayaran, menunggu verifikasi, dibayar, ditolak.

Gunakan status sesuai AFD/BSD dan kontrak yang tersedia. Jangan menciptakan status bisnis baru tanpa dasar.

---

# 15. INFORMATION DESIGN & DATA DENSITY

Sistem ini mengelola informasi perdagangan TBS, sehingga kejelasan data lebih penting daripada dekorasi.

Aturan:

- Nominal uang menggunakan format Indonesia.
- Berat menggunakan kilogram atau ton dengan label jelas.
- Tanggal dan waktu mudah dipahami.
- Angka dalam tabel disejajarkan konsisten.
- Status menggunakan teks dan warna, bukan warna saja.
- Tabel mendukung search, filter, sorting, dan pagination secara visual.
- Tampilkan waktu pembaruan.
- Tampilkan asal data jika penting.
- Hindari chart yang tidak menjawab pertanyaan pengguna.
- Gunakan progressive disclosure untuk informasi detail.
- Berikan ringkasan sebelum persetujuan transaksi.

Untuk semua mockup, gunakan **data simulasi realistis dan konsisten**.

Tampilkan label `Data Simulasi` pada area yang membutuhkan penanda.

Jangan memakai nama petani atau data keuangan nyata tanpa izin.

---

# 16. ACCESSIBILITY REQUIREMENTS

Gunakan WCAG 2.2 AA sebagai target desain pada bagian yang relevan.

Periksa:

- Text contrast.
- Focus visibility.
- Keyboard navigation.
- Label dan error state.
- Touch target.
- Heading hierarchy.
- Reading order.
- Icon accessibility.
- Reduced motion.
- Color-independent status meaning.

Gunakan audit dan lint FigCraft jika tersedia.

Jika audit otomatis tidak memeriksa seluruh aspek usability, lakukan pemeriksaan manual tambahan.

---

# 17. DESIGN SYSTEM TOKENS

Buat design tokens yang dapat diterjemahkan ke Tailwind CSS dan React.

Minimal:

**Colors**

- Primary.
- Primary foreground.
- Background.
- Surface.
- Surface subtle.
- Text primary.
- Text secondary.
- Border.
- Success.
- Warning.
- Danger.
- Info.

**Typography**

- Font family.
- Font size.
- Font weight.
- Line height.
- Letter spacing.

**Spacing**

- 
- 
- 
- 
- 
- 
- 

**Shape**

- Radius sm.
- Radius md.
- Radius lg.

**Effects**

- Focus ring.
- Subtle shadow.
- Hover.
- Disabled.

Gunakan token reusable, bukan hardcode warna dan ukuran pada setiap frame.

Jika FigCraft mendukung DTCG JSON atau Figma Variables, gunakan kemampuan tersebut.

Jangan membuat token yang terlalu granular untuk kebutuhan sederhana.

---

# 18. STRUKTUR FILE FIGMA

Organisasikan desain secara rapi.

Struktur yang direkomendasikan:

- `00 — Project Overview`
- `01 — Foundations & Design Tokens`
- `02 — Atomic Components`
- `03 — Portal Publik`
- `04 — Authentication & App Shell`
- `05 — Petani`
- `06 — Koperasi`
- `07 — Perumda Operations`
- `08 — PKS`
- `09 — Direksi`
- `10 — Administrator`
- `11 — User Flows & Prototypes`
- `12 — Responsive & Interaction States`
- `13 — Design QA & Developer Handoff`

Gunakan penamaan screen yang konsisten.

Contoh:

- `PUB / Harga TBS / Desktop`
- `PUB / Harga TBS / Mobile`
- `KOP / Penerimaan / Form`
- `KOP / Penerimaan / Validation Error`
- `OPS / Rekonsiliasi / Matched`
- `OPS / Rekonsiliasi / Dispute`
- `DIR / Dashboard / Desktop`

Gunakan auto-layout untuk elemen yang relevan agar desain dapat dikelola dan disesuaikan.

---

# 19. IMPLEMENTATION PHASES

Kerjakan desain secara bertahap berdasarkan prioritas, bukan membuat semua halaman sekaligus tanpa review.

## PHASE A — DOCUMENT ANALYSIS

- Baca dokumen.
- Buat design requirement matrix.
- Identifikasi user journey.
- Identifikasi role.
- Identifikasi status.
- Tentukan design priorities.
- Petakan kebutuhan layar.

Output: UX Architecture Summary.

## PHASE B — DESIGN FOUNDATION

- Design direction.
- Color tokens.
- Typography.
- Spacing.
- Grid.
- Icons.
- Atomic components.
- Component states.
- Layout templates.

Output: Design System Foundation.

## PHASE C — PUBLIC PORTAL

Buat seluruh halaman Portal Publik.

Utamakan:

- Beranda.
- Harga multi-PKS.
- Perbandingan.
- Lokasi PKS.
- Mobile screens.

Output: Editable Public Portal Design.

## PHASE D — INTERNAL APP SHELL

Buat:

- Login.
- Sidebar.
- Header.
- Role navigation.
- Dashboard layout.
- Shared forms.
- Data table patterns.

Output: Internal Design Architecture.

## PHASE E — CORE BUSINESS FLOWS

Buat:

- Penerimaan.
- Penimbangan.
- Grading.
- Kontrak.
- Kuota.
- e-DO.
- Tiket PKS.
- Rekonsiliasi.
- Dispute.

Output: Operational Workflow Designs.

## PHASE F — FINANCE, EXECUTIVE & ADMIN

Buat:

- Faktur.
- Payment approval.
- Status pembayaran.
- Executive dashboard.
- Petani dashboard.
- Administrator UI.

Output: Remaining Core Role Screens.

## PHASE G — RESPONSIVE, PROTOTYPE & QA

- Responsive variants.
- Interaction states.
- Clickable prototype jika didukung.
- UX laws review.
- Golden ratio review.
- Accessibility.
- Visual consistency.
- Component audit.
- Design lint.
- Auto-fix yang aman.
- Final visual inspection.

Output: QA-Reviewed Design.

Setelah setiap fase, lakukan audit dan perbaikan sebelum membuat fase berikutnya.

Jangan berhenti setelah membuat analisis atau design plan apabila koneksi FigCraft tersedia dan pembuatan desain dapat dilakukan.

---

# 20. DESIGN VALIDATION

Setiap screen harus dinilai berdasarkan:

1. Kesesuaian PRD.
2. Kesesuaian AFD.
3. Kesesuaian BSD.
4. Konsistensi TRD Atomic Design.
5. Kesesuaian Core MVP.
6. Hierarki informasi.
7. Kemudahan navigasi.
8. Aksesibilitas.
9. Responsiveness.
10. Kejelasan status dan error.
11. Kualitas micro-interaction.
12. Keterbacaan harga dan berat.
13. Komponen reusable.
14. Design token consistency.
15. Realisme workflow bisnis.

Gunakan tools FigCraft untuk inspect, lint, dan audit desain yang telah dibuat.

Periksa frame hasil secara visual.

Perbaiki:

- Text overflow.
- Clipping.
- Misalignment.
- Inconsistent spacing.
- Inconsistent typography.
- Duplicate components.
- Broken auto-layout.
- Inconsistent token usage.
- Poor contrast.
- Missing interaction states.

Jangan mengklaim lolos accessibility testing secara penuh hanya berdasarkan lint otomatis.

---

# 21. DESIGN TO FRONTEND HANDOFF

Desain harus mempermudah implementasi React + TypeScript oleh solo developer.

Siapkan:

- Component inventory.
- Atomic Design mapping.
- Design tokens.
- Responsive behavior notes.
- Screen inventory.
- Navigation map.
- Interaction specifications.
- Form states.
- Loading/error states.
- Role visibility rules.
- Data requirements.
- Component naming conventions.

Petakan reusable design components terhadap calon komponen React.

Contoh:

`PriceComparisonTable` → Organism.

`PriceDisplay` → Molecule.

`StatusBadge` → Atom.

`DashboardTemplate` → Template.

`PublicPricesPage` → Page.

Jangan membuat atau mengubah source code frontend/backend pada tahap ini.

Jangan melakukan database migration.

Jangan mengubah PRD, TRD, AFD, DBD, BSD, atau IPD secara sepihak.

Jika ada ketidaksesuaian dokumen, laporkan sebagai change request.

---

# 22. FINAL DELIVERABLES

Hasil yang wajib diberikan:

1. Desain editable di Figma melalui FigCraft MCP.
2. Design system.
3. Atomic components dan variants.
4. Portal Publik desktop/mobile.
5. Portal Internal berdasarkan role.
6. Screens untuk workflow utama.
7. Empty/loading/error states.
8. Responsive design.
9. Prototype interactions yang benar-benar dibuat dan didukung tool.
10. UX Laws Compliance Matrix.
11. Accessibility audit.
12. Design lint report.
13. Developer handoff specifications.
14. Daftar screen yang berhasil dibuat.
15. Daftar screen yang belum selesai, jika ada.
16. Temuan atau keputusan bisnis yang perlu dikonfirmasi.

Jika berhasil, berikan referensi file Figma atau lokasi desain yang benar-benar dibuat.

Jangan mengarang URL atau ID file.

---

# 23. FINAL ACCEPTANCE CRITERIA

Desain dianggap siap untuk design sign-off apabila:

- Semua dokumen V1.1 telah dianalisis.
- Core MVP dipetakan ke screens.
- Portal Publik dapat dipahami tanpa login.
- Workflow tiap role relevan.
- Design system konsisten.
- Atomic Design lima level dipertahankan.
- 25 prinsip UX telah dievaluasi penerapannya.
- Golden ratio diterapkan secara fleksibel.
- Micro-interactions relevan dan terdefinisi.
- Tidak ada UI yang menyerupai template AI generik.
- Informasi transaksi tidak ambigu.
- Harga dan tanggal mudah dipahami.
- Tidak ada klaim pembayaran palsu.
- Data simulasi ditandai.
- Responsive design diperiksa.
- Accessibility audit dijalankan.
- Komponen reusable.
- Design handoff tersedia.
- Semua temuan kritis diselesaikan atau dinyatakan sebagai blocker.

Gunakan status:

**READY — DESIGN_SYSTEM_AND_CORE_FLOWS_SIGNOFF**

Jika desain sistem dan seluruh core flow yang diprioritaskan telah selesai serta diperiksa.

**CONDITIONALLY_READY — DESIGN_REVIEW_REQUIRED**

Jika desain sudah tersedia tetapi masih memerlukan review, kelengkapan screen, atau perbaikan nonkritis.

**BLOCKED — FIGCRAFT_OR_REQUIREMENTS_UNAVAILABLE**

Jika MCP tidak terhubung atau kebutuhan utama tidak tersedia.

Jangan memberikan status READY jika desain belum benar-benar dibuat di canvas Figma.

---

# 24. EXECUTION INSTRUCTION

Laksanakan urutan berikut:

**DISCOVER → READ DOCUMENTS → VERIFY FIGCRAFT MCP → ANALYZE UX → BUILD DESIGN SYSTEM → CREATE SCREENS → CONNECT FLOWS → AUDIT → FIX → HANDOFF.**

Jangan langsung membuat satu dashboard generik.

Jangan langsung menulis kode React.

Jangan menghasilkan kumpulan gambar statis sebagai pengganti desain editable.

Bekerjalah secara bertahap dengan komponen dan design tokens yang konsisten.

Gunakan pertimbangan UI/UX profesional untuk memilih layout yang benar-benar membantu pengguna.

## FINAL GOAL

Menghasilkan **UI/UX enterprise application yang profesional, mudah digunakan, jelas, elegan, responsif, tidak AI slop, sesuai enam dokumen V1.1, dan dapat diimplementasikan oleh solo developer**.

**Prioritas tertinggi: usability, clarity, consistency, accessibility, realistic workflows, dan maintainable design system.**

Mulai dari PHASE A sekarang, kemudian lanjutkan pembuatan desain melalui FigCraft MCP hingga seluruh scope yang didukung dapat diselesaikan dan diaudit.
