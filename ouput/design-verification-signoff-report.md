# Laporan Audit Verifikasi & Sign-Off Desain FigCraft — AgroNiaga TBS (Perumda Tuah Sekata)

> [!IMPORTANT]
> **Keputusan Sign-Off Akhir:** `CONDITIONALLY_READY — DESIGN_FIXES_PENDING`
> Secara **visual, kontras aksesibilitas (`0` kegagalan kontras `< 4.5:1` dari `991` node teks), ketersediaan font (`0` missing fonts), keterbacaan tabel/angka tabular, state error/loading/konfirmasi (`15` state), dan ekspor token Tailwind CSS v4**, desain FigCraft **sudah solid dan bebas blocker visual**. Namun secara **ketat terhadap kelengkapan AFD `§36` & standar Atomic Design**, status ditetapkan **`CONDITIONALLY_READY`** karena masih terdapat gap non-visual terstruktur (6 sub-rute masih digabung dalam frame komposit, form CRUD `FLOW-06 Master Data PKS` & edit kebun belum dibuat sebagai layar terpisah, `Organism/InternalSidebar` & beberapa atom/molecule form belum di-instansiasi di layar internal, serta navigasi prototype layar penuh `1440px` belum dihubungkan di Pages 6, 8, 9, 10, dan 11).

**Sumber Objek Audit:**
- Dokumen Desain FigCraft: `D:\figcraft\test-output\agroniaga-tbs-perumda-tuah-sekata.figcraft` (`332.780 bytes`, `dirty: false`, `14 halaman`, `38 styles`, `45 variables`, `37` frame/board berstatus `readyForDev`).
- Design Tokens CSS: `D:\figcraft\test-output\tokens.tailwind.css` (`1.471 bytes`, `53 baris`).
- Design Tokens JSON: `D:\figcraft\test-output\tokens.json` (`29.391 bytes`).
- Dokumen Acuan Baseline V1.1: `docs/PRD.md`, `docs/TRD.md`, `docs/AFD.md`, `docs/DBD.md`, `docs/BSD.md`, `docs/IPD.md`.

---

## 1. Inventaris Layar & Persentase Coverage terhadap AFD (`§36` & `FLOW-01..24`)

### 1.1 Cakupan Rute Frontend (`AFD.md §36` — 26 Route Target)

- **Terwakili Total di Kanvas:** **26 / 26 rute (`100%` kehadiran fungsional)**, terdiri dari:
  - **20 / 26 rute (`76,9%`) memiliki layar desktop penuh individual**.
  - **6 / 26 rute (`23,1%`) berstatus parsial / tergabung** dalam frame komposit multi-bagian (belum dipisah menjadi halaman penuh mandiri).
- **Layar Tambahan di Luar 26 Route §36:** `+5` layar utama (`P03 Detail Harga & Riwayat`, `Mobile Menu Open 390px`, `DIR Laporan Eksekutif & Rekonsiliasi`, `Tablet App Shell 768px`, `Mobile App Shell 390px`), ditambah `4` papan sistem (`00 Overview`, `01 Foundations`, `02 Atomic`, `13 QA/Handoff`), `2` papan `12 Responsive & 15 States`, dan `20` artboard storyboard `W01–W06`.

| No. | Halaman & Route `AFD §36` | Node ID Frame di FigCraft | Page | Status Coverage | Catatan Audit Jujur (Fakta Nyata) |
| --- | --- | --- | --- | --- | --- |
| 1 | Beranda Publik (`/`) | `329` (Desktop), `680` (390px), `739` (Mobile Menu) | 03 | **Lengkap** | Desktop + Mobile + CTA prototype terhubung |
| 2 | Harga Publik (`/harga-tbs`) | `445` (Desktop), `700` (390px), `539` (`P03` Riwayat) | 03 | **Lengkap** | Termasuk pemisahan Acuan Disbun & detail riwayat |
| 3 | Detail PKS Publik (`/pks/:id`) | `2105` (Desktop `1440px`) + ringkasan `645` | 03 | **Lengkap (Desktop)** | Layar mandiri ditambahkan saat audit; variasi `390px` khusus `/pks/:id` belum dibuat |
| 4 | Lokasi PKS (`/lokasi-pks`) | `598` (Desktop), `719` (390px) | 03 | **Lengkap** | Termasuk penanganan PKS tanpa koordinat terverifikasi |
| 5 | Profil Perumda (`/tentang`) | `645` (`PUB / P05-P08`) | 03 | **Parsial / Tergabung** | Tampil sebagai kartu bagian komposit, bukan frame `1440px` penuh tersendiri |
| 6 | Kemitraan (`/kemitraan`) | `645` (`PUB / P05-P08`) | 03 | **Parsial / Tergabung** | Digabung bersama `P05–P08` di frame `645` (`height: 512px`) |
| 7 | Kontak (`/kontak`) | `645` (`PUB / P05-P08`) | 03 | **Parsial / Tergabung** | Digabung bersama `P05–P08` di frame `645`; formulir/interaksi kirim belum dipisah |
| 8 | Login (`/login`) | `755` (Default), `790` (Error/Expired/Role Picker) | 04 | **Lengkap (Desktop)** | Mencakup 401/expired & banner simulasi; versi `390px` terpisah belum dibuat |
| 9 | Dashboard Petani (`/app/petani`) | `844` (Desktop), `980` (390px) | 05 | **Lengkap** | Pemisahan tegas status PKS vs pembayaran ke petani |
| 10 | Riwayat Panen (`/app/petani/panen`) | `917` (Desktop) | 05 | **Lengkap (Gabung Profil Kebun)** | Mencakup daftar panen, rincian timbangan & daftar 2 kebun (modal tambah/edit kebun `FLOW-05` belum terpisah) |
| 11 | Dashboard Koperasi (`/app/koperasi`) | `1017` (Desktop) | 06 | **Lengkap** | Mencakup antrean penerimaan & daftar petani binaan |
| 12 | Penerimaan TBS (`/app/koperasi/penerimaan`) | `1101` (Desktop), `1232` (390px) | 06 | **Lengkap** | Validasi Tara > Bruto (`422`), Netto otomatis & grading terpisah |
| 13 | Surat Jalan (`/app/koperasi/surat-jalan`) | `1163` (Desktop) | 06 | **Lengkap** | Konsolidasi multi-petani, QR code & status pengiriman |
| 14 | Dashboard Perumda (`/app/perumda`) | `1261` (gabung Harga) | 07 | **Parsial / Tergabung** | Digabung dengan Manajemen Harga (`1261`); belum ada ringkasan dashboard ops tersendiri |
| 15 | Harga Internal (`/app/perumda/harga`) | `1261` (Desktop) | 07 | **Lengkap** | Alur Maker-Checker harga PKS + acuan |
| 16 | Kontrak (`/app/perumda/kontrak`) | `1324` (Desktop) | 07 | **Lengkap** | Kontrak niaga, kuota pasokan & penentuan PKS tujuan |
| 17 | Logistik (`/app/perumda/logistik`) | `2153` (Desktop) | 07 | **Lengkap** | Layar ditambahkan saat audit: monitoring `IN_TRANSIT` & `Batalkan e-DO` |
| 18 | Rekonsiliasi (`/app/perumda/rekonsiliasi`) | `1384` (Desktop) | 07 | **Lengkap** | Menampilkan `MATCHED`, `DISPUTE/HOLD`, & `ANOMALI SURPLUS` (`BR-REC-009`) |
| 19 | Pembayaran (`/app/perumda/pembayaran`) | `1447` (Desktop) | 07 | **Lengkap** | Faktur AR/AP terpisah & pencatatan bukti transfer |
| 20 | Dashboard PKS (`/app/pks`) | `1509` (Desktop) | 08 | **Lengkap** | Verifikasi QR/token e-DO masuk & daftar kedatangan |
| 21 | Tiket Timbang (`/app/pks/tiket-timbang`) | `1560` (Desktop) | 08 | **Lengkap** | Input tiket unik 1-e-DO, grading terpisah, revisi & blokir pasca-faktur (`409`) |
| 22 | Dashboard Direksi (`/app/direksi`) | `1611` (Desktop) + `1677` (Laporan) | 09 | **Lengkap** | Kas vs Piutang (`BR-PAY-008`), Disetujui vs Dibayar (`BR-PAY-009`), Kontribusi Kotor (`BR-MRG-005`) |
| 23 | Persetujuan (`/app/direksi/persetujuan`) | `1611` (antrean di dashboard) | 09 | **Parsial / Tergabung** | Tampil sebagai panel antrean persetujuan di `1611`, belum halaman tabel/riwayat tersendiri |
| 24 | Dashboard Admin (`/app/admin`) | `1719` (gabung Pengguna) | 10 | **Parsial / Tergabung** | Digabung ke manajemen pengguna (`1719`); kesehatan sistem terlihat di `1779` |
| 25 | Pengguna (`/app/admin/pengguna`) | `1719` (Desktop) | 10 | **Lengkap** | Daftar RBAC, scope lock, larangan Approver (`BR-SYS-002`) & toleransi berversi |
| 26 | Audit (`/app/admin/audit`) | `1779` (Desktop) | 10 | **Lengkap** | Log permintaan HTTP (`request_id`), business audit, dan CCTV error monitoring |

### 1.2 Kesenjangan Modul Fungsional (`FLOW-01..24`) & Variasi State

- **Belum Dibuat Khusus:**
  - `FLOW-06` Form/Modal CRUD **Master Data PKS** dan alur publikasi profil PKS pada peran Perumda.
  - Modal/Form Tambah & Edit **Kebun/Petani (`FLOW-05`)** sebagai layar interaktif tersendiri.
  - Layar desktop full-screen untuk pembatalan e-DO konfirmasi modal di `2153` dan resolusi mobile `390px` bagi portal Perumda, PKS, Direksi, serta Admin (saat ini diwakili oleh `SHELL / Tablet App Shell` & `Mobile App Shell` generik plus `6` halaman mobile utama).
- **Variasi State (`AFD §38`):** Terwakili lengkap pada `STATES` (`2009`) sebanyak **15 State** (`Default`, `Loading Skeleton`, `Empty`, `Success`, `Validation 422`, `Server 503 + Retry`, `Offline`, `401 Expired`, `403 RBAC`, `Disabled v1`, `Pending Approval`, `409 Optimistic Lock`, `Stale/Expired Price`, `Anomali Surplus PKS`, dan `Unsaved Changes Guard AFD §38.7`), serta terpasang di formulir kunci (`1101`, `1384`, `1560`, `2246`, `2257`), namun **belum setiap halaman punya sub-frame 7 state terpisah masing-masing** (misalnya empty-state inline khusus pada setiap tabel ops/direksi masih mengacu pada komponen pola di `2009`).

---

## 2. Hasil Pemeriksaan Visual Layar Utama (`Screenshot Audit`)

Pemeriksaan gambar PNG hasil render `FigCraft screenshot` dilakukan secara bertahap sebelum dan sesudah perbaikan akhir. Berikut bukti visual terbaru setelah seluruh perbaikan terakhir disimpan (`dirty: false`):

### Portal Publik (`P01 Beranda` & `P05 Detail PKS`) & Shell Responsif (`Tablet 768px` / `Mobile 390px`)
![P01 Beranda Desktop](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/p01-beranda.png)
![P05 Detail PKS Mitra Desktop](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/p05-detail-pks.png)
![Tablet dan Mobile App Shell](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/shell-tablet-mobile.png)

### Alur Operasional Inti (`Koperasi Penimbangan`, `Perumda Logistik`, `Perumda Rekonsiliasi`)
![Form Penerimaan dan Penimbangan Koperasi](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/kop-timbang.png)
![Monitoring Logistik e-DO Perumda](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/ops-logistik.png)
![Rekonsiliasi Timbangan Kebun vs PKS](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/ops-rekonsiliasi.png)

### Hilir & Governance (`PKS Tiket Timbang`, `Direksi Eksekutif`, `Administrator RBAC`)
![Input Tiket Timbang PKS](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/pks-tiket.png)
![Dashboard Eksekutif Direksi](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/dir-dashboard.png)
![Manajemen Pengguna RBAC dan Toleransi Admin](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/adm-rbac.png)

### Responsif (`375px Live Reflow`), Matriks `15 State`, dan `W04.2B Dialog Konfirmasi`
![Breakpoints Matrix dan Live 375px Reflow](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/resp-375px.png)
![Matriks 15 State UI dan Bisnis Kritis](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/states-15-matrix.png)
![Dialog Konfirmasi e-DO W04.2B](C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/w04-2b-confirmdialog.png)

**Ringkasan Evaluasi Visual (Bagian B):**
- **Visual Hierarchy & Typography:** Heading halaman (`22–36px Open Sans Bold`), label uppercase tabel (`11px Bold`), dan angka timbangan/uang memakai proporsi kontras ukuran & `Open Sans`/`Cascadia Mono` tanpa bertabrakan.
- **Spacing, Alignment & Table Readability:** Padding internal konsisten (`16/20/24/28/32px`), tabel terstruktur kolom tetap yang proporsional (`Netto`, `Bruto-Tara`, `Grading`, `Status`, `Tindakan`), dan bebas tumpang tindih.
- **Anti-AI-Slop Restraint:** Palet terkontrol (#14452F Deep Forest Green, #4B5E48 Sage, #B45309 Amber, warm canvas #F8F7F4), zero gradien neon/hero dekoratif kosong, seluruh angka contoh berlabel `Data Simulasi`, dan grafik direksi terbatas pada visualisasi progres terarah tanpa *vanity telemetry* palsu.
- **Clipping & Overflow:** Seluruh temuan clipping dan ruang kosong berlebih (kolom `Batalkan e-DO`, placeholder badge `"Status"`, shell tablet/mobile kosong di tengah) telah diselesaikan dan terkonfirmasi bersih di screenshot terbaru.

---

## 3. Daftar Masalah Berdasarkan Severity

| ID | Severity | Lokasi / Lingkup | Deskripsi Temuan Awal | Status Saat Ini |
| --- | --- | --- | --- | --- |
| **AUD-01** | **High (Privacy / BR-PUB-003)** | `Molecule/SearchField` (`209`), P02 (`490`), P04 (`626`) | Placeholder pencarian pada Portal Publik berbunyi *"Cari PKS, petani, atau nomor e-DO..."* sehingga membocorkan konsep entitas transaksi internal ke publik tanpa login. | **Selesai Diperbaiki & Diverifikasi** (diubah ke *"Cari nama PKS atau kecamatan..."*) |
| **AUD-02** | **High (WCAG 2.2 AA Contrast)** | Sidebar gelap `#12231B` di 15 layar desktop internal (`926, 1028, 1111, 1173, 1272, 1334, 1394, 1457, 1518, 1569, 1620, 1685, 1728, 1787, 2164`) | Teks tautan `"Keluar Akun -> /login"` memakai `#6E6A63` di atas `#12231B` dengan rasio kontras **`3.05:1`** (gagal WCAG 2.2 AA `>= 4.5:1`). | **Selesai Diperbaiki & Diverifikasi** (`#B8C7BE` pada `#12231B` = **`9.32:1` AAA**; scan 991 node = `0` gagal) |
| **AUD-03** | **High (AFD §36 Route Missing)** | `03 - Portal Publik` & `07 - Perumda Operations` | Rute mandiri `/pks/:id` (`P05`) dan `/app/perumda/logistik` belum dibuat sebagai frame halaman penuh (`1440px`). | **Selesai Diperbaiki & Diverifikasi** (`2105` & `2153` ditambahkan & berstatus `readyForDev`) |
| **AUD-04** | **Medium (Clipping & Text Placeholder)** | `2153` (`2188/2193`), `2105` (`2131/2148`), `830` (`2216`) | `"Batalkan e-DO"` terpotong kanan di kolom `220px`; badge di `2105` & `830` masih berbunyi generik `"Status"`; harga PKS Kerinci di `2105` tidak konsisten (`Rp2.850` vs `Rp2.920` di P01/P02). | **Selesai Diperbaiki & Diverifikasi** (`width: 265`, teks `"Terverifikasi · Aktif"`, `"Simulasi Tablet"`, `"Rp2.920 / kg"`) |
| **AUD-05** | **Medium (Layout & Duplicate Prototype UI)** | `830`, `837`, `2257`, `2009` | Tablet/Mobile Shell (`830`/`837`) punya area kosong vertikal `~350px` karena `sizingV: "fill"`; `W04.2B` (`2257`) punya baris tombol duplikat eksternal `2267` di bawah `ConfirmDialog`; header `2009` bertulis `"14 State"` padahal berisi 15 state. | **Selesai Diperbaiki & Diverifikasi** |
| **AUD-06** | **Medium (Tailwind Token Collision)** | `tokens.tailwind.css` & `variable.*` (`24..30`) | Beberapa variabel warna punya segmen penamaan ambigu yang berpotensi bertabrakan ketika diekspor ke Tailwind CSS v4 utilities. | **Selesai Diperbaiki & Diverifikasi** (`--color-brand-hover`, `--color-sidebar-bg/active`, `--color-ink-primary/secondary`, `--color-border-control`) |
| **AUD-07** | **Medium (Scope / Multi-Route Consolidation)** | `645` (`P05–P08`), `1261` (`/app/perumda`), `1611` (`persetujuan`), `1719` (`/app/admin`), & `FLOW-06` CRUD PKS | 6 sub-rute AFD §36 masih digabung menjadi blok/panel komposit dalam halaman bersama; form CRUD Master Data PKS (`FLOW-06`) dan edit Kebun (`FLOW-05`) belum dibuat mandiri; layar mobile baru mencakup `6` halaman utama + Shell generik. | **Terbuka (Pending Keputusan/Iterasi Lanjutan)** |
| **AUD-08** | **Low-Medium (Atomic Instantiation Gap)** | `Organism/InternalSidebar` (`275`), `Atom/Input` (`187/189/195`), `FormField` (`210`), `WeightInputGroup` (`227`) | Ke-14 sidebar internal memakai frame lokal (bukan instance `#275`), dan template input/grup timbangan Page 3 memiliki `0` instance di layar operasional. | **Terbuka (Direkomendasikan Saat Handoff React)** |
| **AUD-09** | **Low-Medium (Unwired Fullscreen Internal Flows)** | Pages `05, 07, 08, 09, 10` (`Petani`, `Perumda`, `PKS`, `Direksi`, `Admin`) | Interaksi prototype klik antar-frame `1440px` penuh baru terpasang di `Portal Publik` (`Page 4`) dan `Koperasi` (`Page 7`). Portal internal lainnya hanya terhubung via storyboard `W01–W06` di `Page 12`. | **Terbuka (Non-Blocking untuk Implementasi Kode)** |

---

## 4. Perbaikan yang Benar-Benar Dieksekusi

Seluruh perbaikan di bawah ini langsung dieksekusi di FigCraft pada dokumen aktif (`id: 2`), disimpan (`save_file`, `dirty: false`), dan diverifikasi ulang via screenshot serta kueri JSON/Python:

1. **Perbaikan Kontras WCAG AA -> AAA pada 15 Sidebar Gelap Internal (`AUD-02`):**
   - Mengubah warna teks link `"Keluar Akun -> /login"` di node `[926, 1028, 1111, 1173, 1272, 1334, 1394, 1457, 1518, 1569, 1620, 1685, 1728, 1787, 2164]` dari `#6E6A63` (`3.05:1` gagal AA) menjadi `#B8C7BE` (`9.32:1` lolos WCAG AAA). Terverifikasi dengan scan Python atas `991` node teks seluruh halaman: **`0` item `< 4.5:1`**.
2. **Penanganan Privasi Pencarian Publik (`AUD-01`):**
   - Mengubah teks `Molecule/SearchField #209`, `490`, dan `626` ke *"Cari nama PKS atau kecamatan..."*, sambil mempertahankan pencarian internal e-DO hanya pada halaman terotentikasi OPS (`2179`).
3. **Penambahan Layar Rute AFD yang Sempat Hilang (`AUD-03`) & Polish Presisi (`AUD-04`):**
   - Membuat **`PUB / P05 Detail PKS Mitra (/pks/:id) / Desktop`** (`id: 2105`), mengoreksi badge `2131` -> `"Terverifikasi · Aktif"`, menyamakan harga `2148` -> `"Rp2.920 / kg"`, dan memverifikasi render di `p05-detail-pks.png`.
   - Membuat **`OPS / Monitoring Logistik e-DO & Pembatalan (/app/perumda/logistik) / Desktop`** (`id: 2153`), mempersempit kolom asal `2186/2191` (`470 -> 425`) dan melebarkan kolom tindakan `2188/2193` (`220 -> 265`) sehingga teks merah `"Batalkan e-DO"` (`2198`, lebar `80px`, total baris `237px <= 265px`) tampil utuh tanpa clipping (`ops-logistik.png`).
4. **Pemadatan Tablet & Mobile Shell (`AUD-05`):**
   - Mengubah `sizingV: "hug"` pada `830, 834, 837, 841` dan `gap: 12`, menghapus ruang kosong tengah `~350px` (`height` ringkas menjadi `324px` & `300px`), serta memperbarui badge `2216` -> `"Simulasi Tablet"` (`shell-tablet-mobile.png`).
5. **Peningkatan Prototype `W03.2B` & `W04.2B` + Pembersihan Duplikat Modal (`AUD-05`):**
   - Menghapus frame tombol eksternal duplikat `2267` dari `W04.2B` (`2257`), lalu menautkan tombol internal **`ConfirmDialog #288`**: `2263` (`Batal`) -> `1907` (`W04.1`) dan `2265` (`Terbitkan e-DO`) -> `1921` (`W04.3`) (`w04-2b-confirmdialog.png`), melengkapi frame `W03.2B` (`2246` loading + skeleton).
6. **Sinkronisasi Matriks 15 State (`2009`), 25 Laws of UX (`2064`), & Active Navbar:**
   - Memperbarui judul & nama frame `2009` / `2011` menjadi **Matriks 15 State UI** (termasuk State 15 `Unsaved Changes Guard AFD §38.7`, `Button Focus #145`, `Button Disabled #147`).
   - Memperbaiki highlight aktif Navbar di `445, 539, 645, 755, 2105` dan merapikan `25 Laws of UX` + rasio kontras matematis persis pada `2064`.
7. **Refactor 6 Token Variabel Tailwind & Ekspor Ulang (`AUD-06`):**
   - Memperbarui 6 variabel tabrakan nama menjadi `--color-brand-hover`, `--color-sidebar-bg`, `--color-sidebar-active`, `--color-ink-primary`, `--color-ink-secondary`, `--color-border-control` dan memverifikasi hasil ekspor `tokens.tailwind.css` & `inspect.code` pada `844`.

---

## 5. Daftar Workflow Prototype yang Diuji (`W01–W06`)

Pengujian membedakan secara ketat **interaksi prototype aktual di FigCraft (`onClick -> navigate 150ms dissolve`)** terhadap **aturan logika bisnis/server yang didokumentasikan pada label & kartu**.

### 5.1 Enam Storyboard Utama di Page 12 (`11 - User Flows & Prototypes`, Total `21` Edge Aktif)

| Workflow | Start Node | Jalur Interaksi FigCraft Aktual (Diverifikasi dari JSON Node `interactions`) | Validitas Tujuan & Kejelasan Aksi | Perilaku yang Baru Didokumentasikan (Perlu Logika Backend/React) |
| --- | --- | --- | --- | --- |
| **W01 — Harga TBS Publik** | `1838` | `1838` (`1848`) -> `1850` (`1856`) -> `1858` (`1863`) -> kembali ke `1838` | Loop tertutup bersih; memisahkan harga beli PKS vs Acuan Disbun & fallback PKS tanpa koordinat | Filter real-time berdasarkan kecamatan/kategori & pengambilan versi harga terbaru dari database |
| **W02 — Login & Navigasi Peran** | `1865` | `1865` (`1870`) -> `1872` (`1877`) -> `1879` (`1884`) -> kembali ke `1865` | Loop lengkap menampilkan Login, Guard `401/403`, App Shell aktif & Logout ke `/login` | Autentikasi session cookie server-side & pencabutan token saat logout (`AFD §7`) |
| **W03 — Penerimaan TBS Koperasi** | `1886` | `1886` (`1891`) -> `1893` (`1898`) -> **`2246` (`W03.2B` Loading `#149` + Skeleton `#202`)** (`2255`) -> `1900` (`1905`) -> `1886` | State **loading idempoten** + error validasi Tara > Bruto + sukses `RCV-025` terhubung utuh | Kalkulasi `Netto = Bruto - Tara`, penolakan server `422`, dan deduplikasi `Idempotency-Key` |
| **W04 — Konsolidasi e-DO & QR** | `1907` | `1907` (`1912`) -> `1914` (`1919`) -> **`2257` (`W04.2B` Modal Konfirmasi `#288`)**: tombol `2263` (`Batal`) -> `1907`; tombol `2265` (`Terbitkan e-DO`) -> `1921` (`1926`) -> `1907` | **Dialog konfirmasi** aktif bercabang dua (`Batal` vs `Terbitkan e-DO`) tanpa jalan buntu | Penguncian lot anti-double-allocation transaksi database & reservasi kuota kontrak atomik |
| **W05 — Penerimaan PKS & Rekonsiliasi** | `1928` | `1928` (`1933`) -> `1935` (`1940`) -> `1942` (`1947`) -> `1928` | Alur Scan QR -> Input Tiket -> Rekonsiliasi (`MATCHED -1,0%` vs `DISPUTE HOLD >1,5% Sim`) utuh | Kalkulasi selisih rekonsiliasi server, deteksi `BR-REC-009` surplus anomali, & blokir faktur saat hold |
| **W06 — Faktur & Pembayaran Simulasi** | `1949` | `1949` (`1954`) -> `1956` (`1961`) -> `1963` (`1968`) -> `1949` | Memisahkan faktur AR (PKS->Perumda) & AP (Perumda->Koperasi/Petani), Maker-Checker Direksi, dan status Lunas terpisah | Penegakan otorisasi `Maker != Checker` oleh server (`BR-PAY-005`) dan status berurutan `BSD §18` |

### 5.2 Prototype Full-Screen `1440px` di Page 4 & Page 7

- **Page 4 — `Portal Publik Penuh (P01->P08 Desktop)`** (start `329`, **`14` interaksi** terverifikasi): Navigasi dua arah terhubung antar `329` (`Beranda`), `445` (`Harga TBS`), `539` (`Detail Harga`), `598` (`Lokasi PKS`), `2105` (`Detail PKS /pks/:id`), dan `645` (`Tentang/Kemitraan/Kontak`). *Catatan:* Tautan navbar `"Kemitraan"`/`"Kontak"` dan tombol `"Login Portal"` pada seluruh navbar tidak semuanya dipasang link klik ke `755` (beda halaman) karena keterbatasan flow antar-halaman Figma standar; hal ini dicatat sebagai navigasi lintas-modul aplikasi React.
- **Page 7 — `Koperasi End-to-End Penuh (Ramp -> Timbang -> e-DO)`** (start `1017`, **`5` interaksi** terverifikasi): Mengalir dari Dashboard Koperasi (`1017`) <-> Form Penerimaan/Timbang (`1101`) <-> e-DO Konsolidasi (`1163`).
- **Portal Internal Lain (`Pages 5, 6, 8, 9, 10, 11`):** Belum memiliki wiring klik layar penuh `1440px` di masing-masing halaman; alurnya masih diwakili lewat `Page 12`.

---

## 6. Pemeriksaan Atomic Design (`component.list` & React Readiness)

Hasil audit langsung perintah `component.list` pada dokumen `id: 2`:
- **Total Definisi di Pustaka (`Page 3: 02 - Atomic Components`):** **`48` item** = **`3 COMPONENT_SET`** (`Atom/Button`, `Atom/Badge`, `Atom/Input`) + **`45 COMPONENT`** varian/definisi.
- **Tingkat Pemakaian Nyata di Layar:**
  - **`33` dari `45` komponen (`73,3%`) terinstansiasi aktif**, menghasilkan **`254` instance total** di seluruh layar (misal: `Atom/Button Default` = `44`, `Outline` = `9`, `Secondary` = `4`, `Destructive` = `3`, `Loading` = `2`, `Focus` = `1`, `Disabled` = `1`; `Atom/Badge Simulation` = `30`, `Success` = `19`, `Warning` = `9`, `Danger` = `3`, `Info` = `3`, `Neutral` = `2`; `Icon/Info` = `35`, `Icon/CheckCircle` = `20`; `Molecule/SearchField` = `6`, `DateRangeFilter` = `4`, `PriceDisplay` = `1`, `LocationLink` = `1`, `PaginationControl` = `1`; `Organism/PublicNavbar-Desktop` = `7`, `PublicNavbar-Mobile` = `3`, `ConfirmDialog` = `2`, `StateFeedbackCard` = `1`).
  - **`12` komponen berstatus showcase-only (`0` instance luar):** `Icon/PriceTag` (`126`), `Icon/Scale` (`128`), `Icon/Truck` (`130`), `Icon/Lock` (`136`), `Atom/Button Hover` (`143`), `Atom/Input Default` (`187`), `Focus` (`189`), `Disabled` (`195`), `Atom/Checkbox-Unchecked` (`201`), `Molecule/FormField` (`210`), `Molecule/WeightInputGroup` (`227`), dan `Organism/InternalSidebar` (`275`).
- **Temuan Kunci Atomic Design:**
  - *Positif:* Komponen spesifik fitur seperti grafik direksi, formulir input tiket timbang, dan matriks rekonsiliasi sengaja tidak dipaksakan masuk ke komponen global agar library tetap ramping sesuai prinsip handoff; `PublicNavbar` (`7+3`) & `ConfirmDialog` (`2`) konsisten variannya.
  - *Gap:* Pada implementasi visual layar internal (`Pages 6–11`), **sidebar `#12231B` masih disalin sebagai frame lokal pada `14` layar** daripada mereferensikan instance `Organism/InternalSidebar #275` — terbukti saat bug kontras `#6E6A63` sebelumnya muncul di 15 tempat alih-alih cukup diubah sekali di komponen induk. Di fase React + TypeScript, developer harus memetakan `InternalSidebar` menjadi **1 komponen layout bersama `<InternalAppShell />`**.
- **Struktur React + Tailwind (`inspect.code`):** Hasil generasi kode `inspect.code {id: 844, language: "tailwind"}` membuktikan struktur flex/grid terkonversi bersih ke `flex-row`, `flex-col`, `max-w-[256px]`, dan utility token `bg-sidebar-bg`, `bg-sidebar-active`, `bg-canvas`, `text-ink-primary`, `text-primary-default`. File `.figcraft` tetap sepenuhnya editable di FigCraft/penyelarasan lanjutan.

---

## 7. Pemeriksaan Design Tokens (`tokens.tailwind.css` & `tokens.json`)

- **Hasil Inspeksi `D:\figcraft\test-output\tokens.tailwind.css` (`53 baris`, `1.471 bytes`):**
  - Menggunakan sintaks resmi Tailwind CSS v4 (`@import "tailwindcss";` + dua blok `@theme static`).
  - **Colors (33 token):** Seluruh penamaan bersih tanpa tabrakan sesudah refactor 6 token kunci:
    `--color-primary-default (#14452F)`, `--color-brand-hover (#0F3524)`, `--color-secondary-default (#4B5E48)`, `--color-accent-default (#B45309)`, `--color-accent-subtle (#FEF3C7)`, `--color-accent-text (#78350F)`, `--color-canvas (#F8F7F4)`, `--color-surface-default (#FFFFFF)`, `--color-surface-subtle (#F2F0EB)`, `--color-sidebar-bg (#12231B)`, `--color-sidebar-active (#1E4D38)`, `--color-sidebar-text (#F4F6F4)`, `--color-sidebar-muted (#B8C7BE)`, `--color-ink-primary (#1C1B18)`, `--color-ink-secondary (#57534E)`, `--color-text-muted (#6E6A63)`, `--color-border-subtle (#E4E1D9)`, `--color-border-control (#948E82)`, plus pasangan status lengkap (`success`, `warning`, `danger`, `info`, `neutral`).
  - **Scale & Tokens (12 token):** `--space-1` (`4px`) s.d. `--space-12` (`48px`), `--radius-sm/md/lg` (`4px/8px/12px`), `--layout-sidebar-width` (`256px`), `--layout-touch-min` (`44px`).
- **Hasil Inspeksi `D:\figcraft\test-output\tokens.json` (`29.391 bytes`):** Memuat 2 Variable Collection (`VariableCollectionId:1 Colors` = `33` ID dan `VariableCollectionId:2 Scale & Tokens` = `12` ID -> total `45` variabel) selaras 1:1 dengan file CSS ekspor dan binding di FigCraft.

---

## 8. Catatan Responsive & Accessibility (Pengujian FigCraft & Python)

- **Cakupan Breakpoint (`Page 03, 04, 05, 06, 12`):**
  - **Desktop Wide (`1440px`) & Compact (`1280px`):** Didokumentasikan & didesain dengan container publik `1280px` serta sidebar internal tetap `256px` (berada dalam rentang Golden Ratio `240–272px` pada `DBD.md §28.3`) tanpa tabrakan saat padding berkurang dari `32px` ke `24px`.
  - **Tablet (`768px`):** `SHELL / Tablet App Shell (768px)` (`830`) melipat sidebar ke drawer atas dengan tombol berlabel jelas dan grid 2-kolom.
  - **Mobile (`390px` & `375px`):** Tersedia `6` frame mobile `390px` aktual (`680, 700, 719, 739, 980, 1232`), `Mobile App Shell (390px)` (`837`), serta **preview langsung reflow `375px`** di `1970` (`resp-375px.png`) tanpa overflow horizontal maupun tabel lebar terpotong. *(Catatan keterbatasan: portal internal OPS/PKS/Direksi/Admin mengandalkan pola shell tablet/mobile generik, bukan layar mobile penuh per rute).*
- **Audit Kontras WCAG 2.2 AA (Terukur Python + Inspeksi Seluruh 14 Halaman):**
  - Scan otomatis `991` node `TEXT` (kedalaman 6 di seluruh 14 halaman setelah perbaikan akhir) menunjukkan **`0` kegagalan `< 4.5:1`** untuk teks aktif.
  - Pasangan utama terverifikasi: Primary `#14452F/#FFF` = `10.93:1`, Teks Utama `#1C1B18/#F8F7F4` = `16.08:1`, Sidebar `#F4F6F4/#12231B` = `15.08:1`, Link Sekunder/Logout Sidebar `#B8C7BE/#12231B` = `9.32:1` *(diperbaiki dari `#6E6A63` `3.05:1`)*, Badge Success `#166534/#DCFCE7` = `6.49:1`, Warning `#92400E/#FEF3C7` = `6.37:1`, Simulation `#78350F/#FEF3C7` = `8.15:1`, Danger `#991B1B/#FEE2E2` = `6.80:1`, Info `#1E40AF/#DBEAFE` = `7.15:1`, Neutral `#44403C/#EFECE6` = `8.71:1`, Teks sekunder `#57534E/#FFF` = `7.63:1`, `#6E6A63/#FFF` = `5.38:1`.
  - Pengecualian sah WCAG 1.4.3: tombol nonaktif `Atom/Button State=Disabled` (`Tidak Tersedia`) pada `2009`.
- **Ketersediaan Font (`file.fontReport` & `text.missingFonts`):** `2` keluarga font digunakan (`Open Sans` dan `Cascadia Mono`), keduanya `available: true`, **`missing: 0`**, `families: []`.
- **Target Sentuh, Focus States & Reduced Motion:**
  - Seluruh tombol aksi utama (`Atom/Button`) berukuran tinggi **`44px`** (memenuhi minimum sentuh `44x44px`).
  - Efek fokus **`Focus/Ring` (`S:17`)** & varian `Button Focus (#145)` + field focus border `#14452F` (`1101`, `1560`) sudah didefinisikan.
  - Spesifikasi transisi **`150ms` & `prefers-reduced-motion`** tercantum di papan QA `2064` dan interaksi prototype (`150ms dissolve`), **namun uji navigasi tab keyboard DOM dan media query `@media (prefers-reduced-motion: reduce)` secara eksekusi runtime baru bisa diverifikasi saat implementasi React/Vite dijalankan di browser**.

---

## 9. Ketidaksesuaian & Catatan terhadap Enam Dokumen V1.1

| Dokumen V1.1 | Aspek Kesesuaian vs Ketidaksesuaian yang Ditemukan |
| --- | --- |
| **`PRD.md` & `BSD.md`** | Sesuai untuk cakupan fungsional inti (Unit Listrik & Gas di luar cakupan, larangan klaim lunas sebelum bukti ke petani `BR-PAY-010`, Maker!=Checker harga & keuangan, AR/AP terpisah, larangan admin sebagai Approver `BR-SYS-002`, & `BR-REC-009` anomali surplus PKS). Seluruh **15 keputusan SOP pending (`AFD §41` / `BSD §2`)** dilabeli eksplisit `Data Simulasi` / `Aturan Simulasi` (contoh: toleransi susut `1,50%`, periode harga, hak penerbitan e-DO). |
| **`AFD.md`** | **20/26 rute §36** berdiri sebagai frame penuh (`1440px`); **6/26 rute** (`P06 /tentang`, `P07 /kemitraan`, `P08 /kontak`, `/app/perumda`, `/app/direksi/persetujuan`, `/app/admin`) masih dikonsolidasi ke layar induk/komposit. **CRUD Master Data PKS (`FLOW-06`)** serta dialog edit/hapus kebun (`FLOW-05`) belum dibuat menjadi frame formulir tersendiri. Seluruh 7+2 kondisi **`AFD §38`** & `25` prinsip UX terpenuhi di `2009` dan `2064`. |
| **`DBD.md`** | **`25 Laws of UX` (`§27`)** terverifikasi selaras kata per kata pada `2064` (Chunking, Selective Attention, Mental Model, Occam's Razor, Pareto, dsb.). **Golden Ratio (`§28`)** diterapkan fleksibel (lebar sidebar `256px` dalam `240–272px`, proporsi ~`61.8/38.2` pada hero/detail PKS tanpa memaksakan pada tabel & formulir timbang). Komponen **Atomic Design (`§31`)** lengkap di library (`48` entri), namun `InternalSidebar` (`275`), `FormField` (`210`), & `WeightInputGroup` (`227`) baru berupa showcase (`0` instance) di halaman operasional. |
| **`TRD.md` & `IPD.md`** | Nama stack terpetakan bersih ke React + TypeScript + Vite + Tailwind CSS (`tokens.tailwind.css` v4 `@theme static`). `inspect.code` menghasilkan kelas Tailwind valid. Porsi *Phase* & kontrak API `request_id` (`CCTV Digital` `1779`, State `503` `req_8f2a1c90`) sejalan dengan arsitektur logging `TRD` dan pembagian rute/role `IPD`. |

---

## 10. Status Akhir & Keputusan Sign-Off

### Keputusan: **`CONDITIONALLY_READY — DESIGN_FIXES_PENDING`**

**Alasan Berbasis Bukti:**
1. **Layak sebagai acuan visual, token, & pola state frontend sekarang juga:** Seluruh temuan visual, clipping (`2153`), privasi pencarian publik (`209/490/626`), inkonsistensi data harga/badge (`2105/830`), dan kontras WCAG sidebar (`0/991` kegagalan `<4.5:1`, `0` missing fonts) telah **diperbaiki dan diverifikasi ulang lewat screenshot + ekspor token `tokens.tailwind.css` (`dirty: false`)**.
2. **Penetapan bersyarat (`DESIGN_FIXES_PENDING`) dijaga secara disiplin** karena 4 kesenjangan arsitektural yang teramati langsung agar tim tidak mengklaim kelengkapan fitur melebihi realitas file:
   - Memecah `P06 (/tentang)`, `P07 (/kemitraan)`, `P08 (/kontak)` (`645`) serta antrean persetujuan direksi / master data PKS (`FLOW-06`) apabila implementasi menghendaki blueprint layar terpisah per rute.
   - Menghubungkan komponen pustaka yang masih `0` instance (`Organism/InternalSidebar`, `Molecule/FormField`, `WeightInputGroup`) di level kode React (`<InternalAppShell />`) agar tidak terjadi duplikasi komponen di implementasi.
   - Melengkapi wiring interaksi prototype layar penuh pada Pages `05, 07, 08, 09, 10` jika review klik stakeholder internal menuntut eksplorasi penuh di luar `Page 12`.
   - Mengunci ulang nilai simulasi (batas toleransi susut `1,50%`, formula grading, jalur bayar) setelah **15 keputusan SOP di `AFD §41` / `BSD`** disahkan resmi oleh Perumda Tuah Sekata.
