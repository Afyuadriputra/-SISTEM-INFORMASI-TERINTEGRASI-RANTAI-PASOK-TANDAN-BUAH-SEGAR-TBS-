# IMPLEMENTATION CHECKPOINTS — Rantai Pasok TBS Perumda Tuah Sekata (Unit Agro Niaga)

> **Catatan Tata Kelola Dokumen:** Dokumen ini mencatat progres checkpoint verifikasi desain dan handoff implementasi secara terpisah agar **6 dokumen baseline V1.1** (`PRD.md`, `TRD.md`, `AFD.md`, `DBD.md`, `BSD.md`, dan `IPD.md`) tetap murni sebagai sumber kebutuhan dan *master implementation plan* tanpa perubahan untuk pencatatan progres rutin.
> Seluruh angka dan aturan bisnis yang belum disahkan Perumda tetap ditandai **`Data Simulasi`**, **`Aturan Simulasi`**, atau **`Pending SOP`** (`AFD §41`).

---

## Ringkasan Status Lintas Checkpoint

| Checkpoint | Fase | Status Aktual | Tanggal / Referensi | Ringkasan Hasil |
| :--- | :--- | :--- | :--- | :--- |
| **D4** | Design Verification & Audit | `CONDITIONALLY_READY — DESIGN_FIXES_PENDING` | 2026-11-10 ([design-verification-signoff-report.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/design-verification-signoff-report.md)) | Perbaikan temuan kritis awal (kontras sidebar `#B8C7BE`, privasi pencarian publik, `2105` Detail PKS `/pks/:id`, `2153` Logistik, `2009` 15-State Matrix, `W03.2B`/`W04.2B`, token Tailwind v4); 6 rute mandiri & 2 form master data masih terbuka untuk ditutup di D5. |
| **D5** | Design Gap Closure & Final Sign-Off | **`READY — FIGCRAFT_DESIGN_SIGNOFF`** | 2026-11-10 ([d5-design-gap-closure-signoff.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/d5-design-gap-closure-signoff.md)) | **26/26 (100%)** cakupan rute mandiri `AFD §36`, form penuh `FLOW-05` & `FLOW-06`, refactor `Organism/InternalSidebar #275` pada seluruh 21 layar internal desktop, 14 prototype flow penuh (`215` interaksi, `0` dangling), 7 layar bisnis mobile prioritas, `0/1451` gagal kontras WCAG, `0` missing font, dan `50` board/frame `readyForDev`. |

---

## Checkpoint D4 — Design Verification

### 1. Status & Cakupan Awal
- **Status Akhir D4:** `CONDITIONALLY_READY — DESIGN_FIXES_PENDING`
- **File Desain:** `D:\figcraft\test-output\agroniaga-tbs-perumda-tuah-sekata.figcraft`
- **Token Ekspor:** `D:\figcraft\test-output\tokens.tailwind.css` & `D:\figcraft\test-output\tokens.json`

### 2. Perbaikan yang Diselesaikan pada D4
- **Privasi Data Publik (`BR-PUB-001..005`):** Membersihkan kebocoran pencarian PKS/koperasi pada komponen pencarian publik (`#209`, `#490`, `#626`) agar portal publik hanya mengekspos data publik terkurasi.
- **Kontras Sidebar Internal:** Memperbarui warna teks/ikon menu pada 15 layar internal gelap menjadi `#B8C7BE` (rasio `9.32:1`, WCAG AAA terhadap latar gelap).
- **Rute & Modul Tambahan:** Menambahkan frame `/pks/:id` (`id: 2105` di Page 4), `/app/perumda/logistik` (`id: 2153` di Page 8), shell Tablet (`768px`, `id: 830`) & Mobile (`375px`/`390px`, `id: 837`), matriks `15` variasi state (`id: 2009`), serta dialog konfirmasi `W03.2B` / `W04.2B`.
- **Token Semantic Refactors:** Memperbarui 6 penamaan semantic token agar kompatibel dengan Tailwind v4 `@theme static`.

### 3. Gap Terbuka Hasil D4 (Menjadi Target Wajib D5)
1. **6 Rute Mandiri `AFD §36` masih terkompresi dalam frame komposit / belum memiliki layar desktop `1440px` mandiri:** `/tentang`, `/kemitraan`, `/kontak` (`P06–P08` di frame komposit `645`), `/app/perumda`, `/app/direksi/persetujuan`, dan `/app/admin`. (Serta resolusi tabrakan koordinat antara `645` dan `2105` di Page 4).
2. **Form `FLOW-05` & `FLOW-06` Belum Lengkap:** Belum memiliki alur penuh validasi `422`, error konflik `409`, konfirmasi `Organism/ConfirmDialog`, dan feedback sukses untuk Master Data Petani/Kebun (`FLOW-05`) serta Master Data PKS & publikasi `is_public` (`FLOW-06`).
3. **Adopsi Komponen Atomic Design Lokal:** `Organism/InternalSidebar #275` belum menggantikan sidebar lokal pada 16 layar internal sebelumnya, dan `Molecule/WeightInputGroup #227` belum terpasang langsung pada layar penimbangan mobile prioritas.
4. **Prototype Antar-Portal Terpotong & Penempatan Page 1:** Sebagian flow belum menghubungkan rute baru dan beberapa flow masih menempel di Page 1 alih-alih halaman portalnya masing-masing.
5. **Layar Bisnis Mobile Prioritas (`390px`/`375px`):** Layar operasional inti masih terlalu bergantung pada shell mobile generik (`837`).

---

## Checkpoint D5 — Design Gap Closure & Final Sign-Off

### 1. Status Aktual
- **Status Akhir D5:** **`READY — FIGCRAFT_DESIGN_SIGNOFF`**
- **Cakupan Rute Mandiri terhadap `AFD §36`:** **`26 / 26` rute (`100%`)** tersedia sebagai frame desktop `1440px` mandiri beserta label rute/role eksplisit dan tanpa ketergantungan pada frame komposit lama (`id: 645` dipindahkan ke arsip `(0, 2250)` dengan `devStatus: "none"`).

### 2. Screen & Form yang Diselesaikan pada D5

#### A. Enam Rute Desktop `1440px` Mandiri Baru
| Rute `AFD §36` | Node ID | Page | Koordinat & Ukuran | Ringkasan Isi & Kepatuhan V1.1 |
| :--- | :--- | :--- | :--- | :--- |
| `/tentang` | `2281` | Page 4 | `(8000, 0)`, `1440x880` | `PUB / P06 Tentang Perumda & Unit Agro Niaga (/tentang) / Desktop` — hero proporsional Golden Ratio, eksklusi eksplisit Unit Listrik & Gas, 3 pilar layanan Agro Niaga, navbar `Tentang` aktif. |
| `/kemitraan` | `2327` | Page 4 | `(9600, 0)`, `1440x900` | `PUB / P07 Informasi Kemitraan (/kemitraan) / Desktop` — 3 kartu mitra inti, alur 4 tahap kemitraan, penjaga privasi komersial `BR-PUB-003`. |
| `/kontak` | `2372` | Page 4 | `(11200, 0)`, `1440x820` | `PUB / P08 Kontak Resmi & Lokasi Kantor (/kontak) / Desktop` — data `perumda_offices`, `LocationLink #240`, guard privasi kontak `BSD §5.4`, pratinjau peta kantor MapLibre. |
| `/app/perumda` | `2444` | Page 8 | `(8000, 0)`, `1440x900` | `OPS / Dashboard Operasional Perumda (/app/perumda) / Desktop` — 4 kartu KPI operasional lintas alur, antrean prioritas, akses cepat SOP (`Pending SOP`) & Master PKS. |
| `/app/direksi/persetujuan` | `2514` | Page 10 | `(3200, 0)`, `1440x900` | `DIR / Daftar & Detail Persetujuan Kewenangan (/app/direksi/persetujuan) / Desktop` — pencarian & filter tanggal, antrean 3 item otorisasi, panel validasi `Maker != Checker`. |
| `/app/admin` | `2576` | Page 11 | `(3200, 0)`, `1440x900` | `ADM / Dashboard Administrator Sistem (/app/admin) / Desktop` — KPI kesehatan teknis non-transaksional (`/healthz`, Redis, error 5xx `req_8f2a1c90`), lencana `BR-SYS-002 Dilarang Approver`, feed audit keamanan. |

#### B. Form Bisnis Lengkap (`FLOW-05` & `FLOW-06`)
| Alur Bisnis | Node ID | Page | Koordinat & Ukuran | State & Validasi Terverifikasi |
| :--- | :--- | :--- | :--- | :--- |
| **`FLOW-05`** Master Data Petani & Kebun | `2641` | Page 7 | `(4800, 0)`, `1440x960` | Field `DBD farmers/farms` (`farmer_code`, `full_name`, `contact_phone`, kunci scope `KOP-01`, `farm_code`, `area_hectares`, `planting_year`), `Molecule/FormField #210` (error validasi berpasangan `422` koordinat + guard privasi `BR-MD-008`), `Atom/Input` (`Default`/`Focus`/`Disabled`), `Organism/ConfirmDialog #288` (`BR-MD-003/010` nonaktif tanpa hapus histori), kartu sukses `201 Created`, & `Organism/StateFeedbackCard #296` (guard konflik `409`/jaringan). |
| **`FLOW-06`** Master Data PKS & Publikasi Profil (`/app/perumda/pks`) | `2741` | Page 8 | `(9600, 0)`, `1440x960` | Field `DBD mill_companies/mills`, `Molecule/FormField #210` (error validasi `422` Lat `[-90..90]`/Lng berpasangan sesuai `DBD §7.7`), `Checkbox` pemisah status kemitraan internal vs publikasi portal `is_public` (`AFD §9.4`, menyembunyikan kontrak/kuota `BR-PUB-003`), `Organism/ConfirmDialog #288`, banner sukses `200 OK` cache invalidation, & `LocationLink #240`. |

#### C. Layar Bisnis Mobile Prioritas (`390px` / `375px`)
| Domain / Layar | Node ID | Page | Catatan Implementasi D5 |
| :--- | :--- | :--- | :--- |
| `PUB / P05 Detail PKS Mitra (/pks/:id) / Mobile (390px)` | `2414` | Page 4 | Menghindari clip kanan pada `LocationLink`, layout bertumpuk ramah sentuh (`>=44px`). |
| `AUTH / P09 Login Portal Internal / Mobile (390px)` | `2841` | Page 5 | Input kredensial, tombol aksi penuh, informasi error RBAC/lockout. |
| `PET / Ringkasan Pembayaran & Riwayat Panen / Mobile (390px)` | `2864` | Page 6 | Pemecahan bertahap ringkasan pembayaran (`BR-PAY-010`) + pengetatan `980` (`sizingV: "hug"`). |
| `KOP / Form Input Penerimaan TBS Lapangan / Mobile (390px)` | `1232` | Page 7 | Di-upgrade memakai instance live `Molecule/WeightInputGroup #227` (fit `17.340,000` kg bersih di `390px`/`375px`). |
| `KOP / Detail e-DO Konsolidasi & QR / Mobile (390px)` | `2887` | Page 7 | Verifikasi QR konsolidasi e-DO, identitas armada, dan status penimbangan. |
| `OPS / Detail Rekonsiliasi Timbang / Mobile (390px)` | `2908` | Page 8 | Ringkasan selisih Ramp vs PKS, pemicu eskalasi rekonsiliasi, & label `Aturan Simulasi`. |
| `PKS / Input Tiket Timbang PKS / Mobile (390px)` | `2931` | Page 9 | Memakai instance live `Molecule/WeightInputGroup #227` + aksi kirim tiket PKS. |

#### D. Konsolidasi Atomic Design & Prototype Interactive
- **Refactor `Organism/InternalSidebar #275`:** Ditingkatkan dengan Brand Header + `7` slot menu `44px` (`Nav/Slot-1..7`) + tombol bawah `Nav/Logout` (`Keluar Akun -> /login`, `#B8C7BE`, rasio `9.32:1` AAA), serta pembersihan wrapper fill `#FFFFFF` (`fills: []`). Seluruh **16** sidebar lokal pada frame internal lama (`844, 917, 1017, 1101, 1163, 1261, 1324, 1384, 1447, 2153, 1509, 1560, 1611, 1677, 1719, 1779`) berhasil diganti non-destruktif menjadi instance live `#275` -> total **`21` instance aktif** pada 21 layar internal desktop.
- **Katalog Komponen (`component.list`):** **`48` entri (`3 COMPONENT_SET` + `45 COMPONENT`)**, **`39 / 45` (`86.7%`) komponen aktif terpakai (`>0` instance)**, total **`393` instance** di seluruh dokumen. Hanya `6` varian mikro showcase (`Icon/PriceTag`, `Icon/Scale`, `Icon/Truck`, `Icon/Lock`, `Button Hover`, `Checkbox-Unchecked`) yang dipertahankan di showcase Page 3 sebagai referensi implementasi CSS/React.
- **Prototype Flows (`14` Flow, `215` Interaksi, `0` Target Rusak/Dangling):**
  - Page 4: `Portal Publik Penuh (P01->P08 Desktop) -> 329` (`60` interactions)
  - Page 5: `Auth & App Shell (/login) -> 755` (`5` interactions)
  - Page 6: `Portal Petani Penuh -> 844` (`11` interactions)
  - Page 7: `Koperasi End-to-End Penuh (Ramp -> Timbang -> e-DO) -> 1017` (`25` interactions)
  - Page 8: `Perumda Operations & Finance Penuh -> 2444` (`56` interactions)
  - Page 9: `PKS Penerimaan & Timbang Penuh -> 1509` (`7` interactions)
  - Page 10: `Direksi Eksekutif & Persetujuan Penuh -> 1611` (`15` interactions)
  - Page 11: `Administrator RBAC & CCTV Digital Penuh -> 2576` (`15` interactions)
  - Page 12: `W01–W06` (`6` storyboards, `21` interactions tetap utuh)
- **Batasan Prototype vs React/Backend:** Interaksi FigCraft hanya memodelkan navigasi antar-layar, pemilihan tab, modal konfirmasi, dan showcase state statis. Autentikasi (`JWT`/`Cookie`, lockout), query filter/paginasi server, perhitungan netto/potongan/harga TBS, penguncian transaksi (`Maker != Checker`), enkripsi QR, serta invalidasi cache `is_public` **harus diimplementasikan di React + FastAPI + PostgreSQL**.

### 3. Pengujian yang Dilakukan & Bukti Terverifikasi
1. **Audit Kontras WCAG (Python JSON Scan kedalaman 12 penuh tanpa truncasi pada `inspect_document`):** Memeriksa **`1.451` node `TEXT` tampak** -> **`0` kegagalan kontras (`< 4.5:1`)** *(catatan: FigCraft MCP tidak memiliki command `design.lint` bawaan, sehingga lint kontras, dangling interaction, dan bounding dijalankan langsung atas output JSON `inspect_document`)*.
2. **Audit Font (`file.fontReport` & `text.missingFonts`):** **`2` font** (`Open Sans`, `Cascadia Mono`), `available: true`, **`missing: 0`**, `families: []`.
3. **Audit Komponen (`component.list`):** **`39/45` (`86.7%`) komponen aktif**, **`393` total instance**, Page 14 `HANDOFF` (`2091`) diperbarui.
4. **Penandaan Dev Handoff (`inspect.readyForDev`):** **`50` board/frame terverifikasi** di Page 4–14 ditandai `readyForDev` (frame arsip komposit `id: 645` sengaja dipertahankan `devStatus: "none"`).
5. **Verifikasi Codegen Tailwind (`inspect.code {id: 2105, mobile: 2414, language: "tailwind"}`):** Mengonfirmasi keluaran JSX mobile-first yang merujuk variabel token `--color-primary-default`, `--color-ink-primary`, dll. sesuai `tokens.tailwind.css`.
6. **Ekspor Token & Penyimpanan File (`save_file` & `variable.export`):**
   - [agroniaga-tbs-perumda-tuah-sekata.figcraft](file:///D:/figcraft/test-output/agroniaga-tbs-perumda-tuah-sekata.figcraft) (`399.987 bytes`, `dirty: false`)
   - [tokens.tailwind.css](file:///D:/figcraft/test-output/tokens.tailwind.css) (`1.471 bytes`, `53` baris, `2` blok `@theme static`)
   - [tokens.json](file:///D:/figcraft/test-output/tokens.json) (`29.391 bytes`, `45` variabel)
7. **Bukti Screenshot:** **29 berkas PNG terverifikasi** (`12` dipertahankan dari D4 + `17` capture baru D5) tersimpan di [screenshots/](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/).

### 4. Temuan Tersisa (Non-Blocking — Diteruskan ke Implementasi React / Keputusan SOP)
1. **15 Keputusan SOP Terbuka (`AFD §41` / `BSD`):** Nilai ambang batas rekonsiliasi timbangan, batas keterlambatan unggah tiket PKS, SLA approval Direksi, retensi log, dan rule harga yang masih berstatus `Pending SOP` tetap diberi penanda **`Data Simulasi`** / **`Aturan Simulasi`** di desain dan UI React hingga Perumda menetapkan SK resmi.
2. **Pengujian Runtime Browser & Aksesibilitas Nyata (Fase `F8` IPD):** Verifikasi DOM `:focus-visible`, `prefers-reduced-motion`, navigasi keyboard Tab-order, ARIA landmark/live-region, serta respons tabel sekunder pada layar Admin Log (`390px`/`768px`) harus diuji langsung di Vite/React + Chrome DevTools.
3. **Varian Interaktif CSS/React (6 item Showcase Page 3):** State hover tombol & unchecked checkbox showcase (`0` instance di kanvas statis) dipetakan ke utility class Tailwind (`hover:`, `:checked`) dan micro-interactions Framer/CSS saat implementasi komponen React.
4. **Arsip Frame Komposit Lama (`id: 645`):** Frame `[ARSIP KOMPOSIT] PUB / P05-P08 Gabungan Lama / Desktop` tetap berada di koordinat `(0, 2250)` Page 4 dengan `devStatus: "none"` sebagai referensi historis D1–D4 dan **bukan acuan implementasi**.

### 5. Referensi Artefak
- Laporan Audit D4: [design-verification-signoff-report.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/design-verification-signoff-report.md)
- Laporan Penutupan Gap & Sign-Off D5: [d5-design-gap-closure-signoff.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/d5-design-gap-closure-signoff.md)
- Direktori Screenshot Bukti: [screenshots/](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/screenshots/)
- Berkas FigCraft Sumber: [agroniaga-tbs-perumda-tuah-sekata.figcraft](file:///D:/figcraft/test-output/agroniaga-tbs-perumda-tuah-sekata.figcraft)
- Ekspor Token CSS & JSON: [tokens.tailwind.css](file:///D:/figcraft/test-output/tokens.tailwind.css) | [tokens.json](file:///D:/figcraft/test-output/tokens.json)

---

## Langkah Berikutnya (Handoff ke Track Implementasi Frontend — `IPD.md`)

Implementasi frontend mengacu pada **Master Implementation Plan** di [IPD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/IPD.md) (Milestone Track Frontend `F1–F8`):
1. **`F1` Design System & Token Setup:** Impor `tokens.tailwind.css` (`@theme static`) ke entry Tailwind CSS v4 React + TypeScript, pasang font `Open Sans` & `Cascadia Mono`, serta bangun primitives Atomic Design (`InternalSidebar`, `PublicNavbar`, `Atom/Input`, `FormField`, `WeightInputGroup`, `ConfirmDialog`, `StateFeedbackCard`, `LocationLink`).
2. **`F2–F3` Public Portal & Auth/AppShell Gate:** Implementasi `P01–P08` sesuai frame `1440px`/`390px` + guard `BR-PUB-003` (`is_public` & sanitasi data privat), serta autentikasi `/login` dengan RBAC route guard dan kebijakan `BR-SYS-002` pada role Administrator.
3. **`F4–F7` Portal Petani, Koperasi (`FLOW-05`), Perumda (`FLOW-06`, Rekonsiliasi), PKS, Direksi, & Admin:** Sambungkan formulir, validasi `422`/`409`, label `Data Simulasi`/`Pending SOP`, `Maker != Checker`, dan responsivitas `1440px / 1280px / 768px / 390px / 375px` dengan endpoint backend FastAPI sesuai kontrak `TRD.md` & `AFD.md`.
4. **`F8` Verification, A11y & Performance Gate:** Jalankan pengujian fokus keyboard, `prefers-reduced-motion`, kontrak API end-to-end, dan uji responsif lintas breakpoint sebelum UAT.
