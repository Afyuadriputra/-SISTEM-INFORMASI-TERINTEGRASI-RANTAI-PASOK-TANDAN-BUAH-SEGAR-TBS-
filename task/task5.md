
# MASTER PROMPT ANTIGRAVITY

# FULL FRONTEND DEVELOPMENT — F0 SAMPAI F11

## Sistem Informasi Enterprise Terintegrasi Rantai Pasok TBS

### Perumda Tuah Sekata — Unit Agro Niaga

**Mode:** Full Implementation & Verification
**Frontend:** React 19 + TypeScript + Vite
**Backend:** FastAPI B11.1 — Post-Implementation Verified
**Contracts:** M0.1 — Verified
**Design:** FigCraft D5 — Design Sign-Off
**Progress Tracking:** Single Checkpoint File
**Final Goal:** FRONTEND_BACKEND_INTEGRATION_VERIFIED

---

# 1. ROLE & PRIMARY OBJECTIVE

Bertindak sebagai gabungan tim profesional yang terdiri dari:

- Principal Frontend Architect
- Senior React & TypeScript Engineer
- UI/UX Design Engineer
- Design System Engineer
- Frontend Performance Engineer
- Accessibility Specialist
- API Integration Engineer
- Frontend Security Engineer
- QA Automation Engineer
- Visual Regression Engineer
- Technical Lead

Tugas kamu adalah **mengimplementasikan seluruh Frontend Track F0–F11**, mulai dari proyek React yang sudah terinstal hingga aplikasi frontend yang lengkap, responsif, terintegrasi, dan tervalidasi.

Kamu bekerja menggunakan Google Antigravity, terminal, browser testing, skill lokal, serta FigCraft MCP apabila tersedia.

## Hasil yang wajib dicapai

1. Frontend React + TypeScript berjalan stabil.
2. Seluruh kebutuhan frontend Core MVP terealisasi.
3. Seluruh 26 rute AFD §36 terimplementasi sesuai role dan aksesnya.
4. Desain mengikuti FigCraft D5, bukan desain baru yang dikarang agent.
5. Komponen mengikuti Atomic Design lima level.
6. Seluruh workflow bisnis yang ditampilkan frontend sesuai AFD, BSD, dan kontrak.
7. Integrasi API memakai kontrak OpenAPI M0.1.
8. Login, sesi, CSRF, dan role-based navigation bekerja.
9. Tujuh role internal memiliki pengalaman pengguna yang sesuai kebutuhan.
10. Semua formulir mempunyai validasi dan error handling yang benar.
11. Data keuangan dan penimbangan dipresentasikan dengan presisi.
12. State `Data Simulasi`, `Aturan Simulasi`, dan `Pending SOP` tidak disembunyikan.
13. Aplikasi responsive, accessible, dan dapat digunakan orang awam.
14. Tidak ada navigasi mati, tombol palsu, maupun fitur yang tampak berfungsi tetapi tidak melakukan tindakan.
15. Pengujian otomatis dan browser testing benar-benar dijalankan.
16. Backend B11.1 tidak mengalami regresi akibat pekerjaan frontend.
17. Seluruh hasil perubahan dan pengujian tercatat dalam satu file checkpoint.

Jangan sekadar menghasilkan prototype statis.

Jangan sekadar membuat dashboard yang terlihat cantik.

**Bangun frontend yang benar-benar mengimplementasikan workflow bisnis dan siap digunakan bersama API FastAPI.**

---

# 2. WORKSPACE & EXISTING APPLICATION

Root proyek:

`D:\Kuliah\joki\radit\projek thesis bg givo`

Frontend:

`D:\Kuliah\joki\radit\projek thesis bg givo\frontend`

Backend:

`D:\Kuliah\joki\radit\projek thesis bg givo\backend`

Contracts:

`D:\Kuliah\joki\radit\projek thesis bg givo\contracts`

Documents:

`D:\Kuliah\joki\radit\projek thesis bg givo\docs`

Agent skills:

`D:\Kuliah\joki\radit\projek thesis bg givo\.agents\skills`

## IMPORTANT — REACT ALREADY INSTALLED

User telah memasang React + TypeScript + Vite secara manual.

Karena itu:

- Jangan membuat ulang folder `frontend`.
- Jangan menjalankan Vite scaffolding kedua.
- Jangan menghapus `src/` tanpa pemeriksaan.
- Jangan menghapus konfigurasi dan dependency pengguna secara sembarangan.
- Jangan membuat frontend dalam folder proyek lain.
- Jangan membuat monorepo baru.
- Jangan mengganti npm dengan package manager lain tanpa alasan yang disetujui.

Mulai dengan audit:

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/tsconfig*.json`
- `frontend/vite.config.ts`
- `frontend/src/`
- `frontend/public/`
- `.gitignore`

Gunakan instalasi React yang sudah ada sebagai fondasi.

Pasang dependency tambahan yang benar-benar diperlukan melalui npm dan simpan lockfile.

Gunakan `npm.cmd` ketika diperlukan pada PowerShell Windows.

---

# 3. MANDATORY SKILLS DISCOVERY

Sebelum coding, lakukan discovery terhadap:

`D:\Kuliah\joki\radit\projek thesis bg givo\.agents\skills`

Wajib:

1. Inventarisasi skill yang terpasang.
2. Baca instruksi dan `SKILL.md` yang relevan.
3. Ikuti workflow skill sesuai konteks.
4. Gunakan contoh dan reference yang disediakan skill.
5. Catat skill yang benar-benar digunakan ke checkpoint.
6. Jangan mengarang keberadaan skill yang tidak ditemukan.

Cari skill yang berkaitan dengan:

- UI/UX anti-AI-slop.
- Professional frontend design.
- Human-centered design.
- React architecture.
- TypeScript.
- Tailwind CSS.
- Atomic Design.
- Design systems.
- Accessibility.
- Responsive design.
- Mobile layout.
- UX copywriting.
- Interaction design.
- Frontend performance.
- API integration.
- Browser automation.
- Testing.
- Code quality.
- Refactoring.

Apabila tersedia, prioritaskan skill yang membahas:

- Antislop UI.
- Antislop responsive/mobile.
- Antislop copywriting.
- UI taste.
- Professional layout.
- UX design principles.
- Frontend engineering.

Gunakan skill yang sesuai kebutuhan, bukan sekadar menyebutkan namanya pada laporan.

Jika instruksi skill bertentangan dengan desain FigCraft D5 atau spesifikasi resmi, ikuti dokumen proyek yang berwenang dan catat konflik.

---

# 4. MANDATORY DOCUMENT COMPREHENSION

**JANGAN LANGSUNG CODING.**

Baca seluruh dokumen berikut sebelum menentukan arsitektur frontend.

## 4.1 Six Core Documents V1.1

- `docs/PRD.md`
- `docs/TRD.md`
- `docs/AFD.md`
- `docs/DBD.md`
- `docs/BSD.md`
- `docs/IPD.md`

Baca seluruhnya, bukan hanya heading.

Perhatikan secara khusus:

- Functional requirements.
- Non-functional requirements.
- AFD business flows.
- AFD §36 route mapping.
- AFD UI states.
- BSD business rules.
- Role authorization.
- Pending SOP.
- Data privacy.
- DBD §27 UX Laws.
- DBD §28 Golden Ratio.
- DBD Atomic Design requirements.
- Backend/frontend integration conventions.
- Milestone F0–F11.
- Quality gates dan acceptance criteria.

## 4.2 Architecture Decisions

Baca seluruh:

`docs/adr/`

Terutama:

- ADR-005 — Session, CSRF, RBAC, Scope.
- ADR-006 — Atomic Design Frontend.
- ADR-008 — OpenAPI Envelope.
- ADR-009 — Decimal, UUID, Timezone.
- ADR-010 — Idempotency & Pending SOP.

Tetap pahami ADR lain agar frontend tidak membuat asumsi yang bertentangan dengan backend.

## 4.3 M0/M0.1 Handoff

Baca seluruh:

`docs/m0/`

Terutama:

- `M0_HANDOFF.md`
- `M0_REQUIREMENT_TRACEABILITY.md`
- `M0_DECISION_REGISTER.md`
- `M0_CONTRACT_VALIDATION_REPORT.md`

Gunakan keputusan hasil koreksi M0.1 sebagai baseline.

## 4.4 Backend B11.1

Baca checkpoint:

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Cari:

`B11.1 — Post-Implementation Verification`

Pahami:

- Status backend.
- 95 OpenAPI operations.
- Error schemas.
- Auth flow.
- Cookie sessions.
- CSRF.
- Scope.
- Idempotency.
- 48 tabel PostgreSQL.
- Redis behavior.
- Pending SOP.
- Bug fixes B11.1.
- Runtime limitations.

Backend dilaporkan memiliki 95 operasi yang telah diuji dan 77 backend tests lulus.

**Verifikasi kembali status aktual, Git working tree, dan konektivitas backend. Jangan menganggap backend selalu sedang berjalan.**

Perubahan backend B11.1 pernah dilaporkan belum di-commit.

Jangan reset, checkout, overwrite, atau menghapus perubahan backend tersebut.

## 4.5 Shared Contracts

Baca:

- `contracts/openapi.v1.yaml`
- `contracts/error-catalog.yaml`
- `contracts/state-catalog.yaml`
- `contracts/role-permissions.yaml`
- `contracts/fixtures/README.md`
- Seluruh `contracts/fixtures/*.json`

Kontrak ini adalah sumber kebenaran.

Jangan membuat model data frontend berdasarkan perkiraan bentuk JSON.

Jangan membuat API endpoint baru hanya karena dibutuhkan oleh UI, sebelum memeriksa apakah kebutuhan tersebut sebenarnya sudah dilayani operasi yang ada.

---

# 5. FIGCRAFT D5 DESIGN HANDOFF

Desain telah mencapai:

`READY — FIGCRAFT_DESIGN_SIGNOFF`

Sumber utama:

`D:\figcraft\test-output\agroniaga-tbs-perumda-tuah-sekata.figcraft`

Design tokens:

`D:\figcraft\test-output\tokens.tailwind.css`

`D:\figcraft\test-output\tokens.json`

Dokumen pendukung:

- `design-qa-handoff.md`
- `design-verification-signoff-report.md`
- `d5-design-gap-closure-signoff.md`

Cari lokasi aktual dokumen di workspace dan folder artefak Antigravity.

Gunakan FigCraft MCP untuk membaca frame, komponen, token, dan screenshot apabila tersedia.

Jika konektor FigCraft tidak dapat diakses, gunakan handoff D5 dan screenshot yang benar-benar tersedia.

Jangan mengarang detail visual yang tidak bisa diperiksa.

Jika visual reference utama tidak tersedia, kerjakan bagian yang independen dan tandai visual sign-off sebagai belum terverifikasi.

## Baseline Design

Desain D5 mencakup:

- 26/26 rute desktop mandiri.
- 50 readyForDev frame/board.
- Atomic component library.
- InternalSidebar reusable.
- Prototype navigasi lintas role.
- Form FLOW-05 dan FLOW-06.
- Layar bisnis mobile prioritas.
- 15 UI/business states.
- Design token Tailwind CSS v4.

## Design Requirements

Gunakan:

- Deep green sebagai warna identitas utama.
- Off-white/neutral sebagai fondasi background.
- Amber untuk konteks perhatian dan status relevan.
- Open Sans untuk teks UI.
- Cascadia Mono untuk nilai teknis/numerik jika sesuai desain.
- Semantic tokens, bukan hardcoded color tersebar.

Gunakan nilai token aktual dari FigCraft.

Jangan membuat palette baru secara sepihak.

Jangan menggunakan warna yang tidak konsisten dengan token.

Jangan mengubah font resmi hanya karena font lain sedang populer.

---

# 6. STRICT ANTI-AI-SLOP DESIGN POLICY

Tampilan harus terasa seperti sistem enterprise yang dirancang manusia secara profesional.

Hindari:

- Gradient berlebihan.
- Glow.
- Glassmorphism dekoratif.
- Neon tanpa fungsi.
- Border radius sangat besar pada semua elemen.
- Shadow berlebihan.
- Floating cards tanpa struktur.
- Hero generik bergaya startup AI.
- Emoji sebagai pengganti ikon profesional.
- Terlalu banyak warna aksen.
- Semua heading berukuran sangat besar.
- Kartu KPI yang tidak memberikan informasi berguna.
- Spacing yang terlalu longgar untuk aplikasi operasional.
- Dashboard penuh ilustrasi dekoratif.
- Layout berbeda-beda antar halaman.
- Komponen yang tampak seperti template acak.
- Animasi hanya untuk terlihat modern.
- Placeholder palsu yang disamarkan sebagai data nyata.

Gunakan ikon profesional yang konsisten, misalnya Lucide React apabila cocok dengan kebutuhan desain.

Gunakan visual hierarchy yang kuat:

1. Page title.
2. Context/breadcrumb.
3. Primary task.
4. Supporting actions.
5. Data/content.
6. Feedback.

UI harus jelas dan mudah digunakan oleh:

- Petani.
- Operator koperasi.
- Staf operasional Perumda.
- Staf finance.
- Petugas PKS.
- Direksi.
- Administrator sistem.

Sebagian pengguna bukan orang IT.

Gunakan bahasa Indonesia yang jelas.

Hindari istilah teknis yang tidak perlu ditampilkan kepada pengguna bisnis.

Contoh:

Gunakan "Data tidak dapat disimpan" alih-alih memunculkan teks exception Python.

Gunakan "Periksa kembali berat tara" alih-alih menampilkan raw validation schema.

Tetap sediakan Request ID ketika berguna untuk bantuan teknis.

---

# 7. APPLY 25 LAWS OF UX & GOLDEN RATIO

Baca ketentuan UX pada DBD, termasuk 25 hukum UX yang telah menjadi bagian spesifikasi.

Terapkan secara kontekstual.

Prioritaskan:

- Hick's Law untuk mengurangi pilihan tidak relevan.
- Fitts's Law untuk ukuran dan penempatan target.
- Jakob's Law untuk pola navigasi familiar.
- Miller's Law untuk pengelompokan informasi.
- Gestalt principles untuk struktur visual.
- Law of Proximity.
- Law of Similarity.
- Aesthetic-Usability Effect.
- Doherty Threshold untuk responsivitas interaksi.
- Peak-End Rule untuk feedback tugas.
- Serial Position Effect.
- Tesler's Law untuk kompleksitas workflow.
- Consistency.
- Recognition over Recall.
- Error Prevention.
- Progressive Disclosure.

Gunakan keseluruhan daftar kanonis dari dokumen proyek, bukan menganggap contoh di atas sebagai daftar lengkap.

## Golden Ratio

Terapkan Golden Ratio secara selektif pada komposisi yang diuntungkan, misalnya hero publik dan keseimbangan layout.

Jangan memaksakan Golden Ratio pada:

- Tabel data.
- Form.
- Sidebar.
- Dashboard grid.
- Tombol.
- Dialog.
- Layar mobile.

Usability, keterbacaan, dan kepadatan informasi harus lebih diutamakan.

---

# 8. FRONTEND TECHNOLOGY BASELINE

Ikuti TRD dan ADR-006.

Baseline:

- React 19.
- TypeScript strict.
- Vite.
- Tailwind CSS v4.
- TanStack Router.
- TanStack Query.
- React Hook Form.
- Zod.
- openapi-typescript.
- MSW.
- Vitest.
- React Testing Library.
- Playwright.

Gunakan library lain hanya jika:

1. Memang dibutuhkan.
2. Kompatibel.
3. Tidak menduplikasi library lain.
4. Memudahkan maintainability.
5. Tidak menyebabkan bundle bloat.
6. Memiliki alasan yang jelas.

## Package Management

Gunakan npm sesuai proyek yang sudah dibuat.

Pertahankan:

- `package.json`.
- `package-lock.json`.

Jangan mencampur npm, pnpm, dan yarn dalam satu proyek.

Jangan membuat dependency ganda.

Audit dependency dan tree shaking.

Gunakan lazy loading untuk route yang sesuai.

---

# 9. ATOMIC DESIGN & FEATURE ORGANIZATION

Gunakan Atomic Design lima level:

1. Atoms.
2. Molecules.
3. Organisms.
4. Templates.
5. Pages.

Kombinasikan dengan feature-based organization.

Contoh struktur konseptual:

```text
frontend/
├── public/
├── src/
│   ├── app/
│   │   ├── providers/
│   │   ├── router/
│   │   └── layouts/
│   ├── components/
│   │   ├── atoms/
│   │   ├── molecules/
│   │   ├── organisms/
│   │   └── templates/
│   ├── features/
│   │   ├── auth/
│   │   ├── public-portal/
│   │   ├── master-data/
│   │   ├── pricing/
│   │   ├── receiving/
│   │   ├── contracts/
│   │   ├── logistics/
│   │   ├── mill-weighing/
│   │   ├── reconciliation/
│   │   ├── finance/
│   │   ├── reporting/
│   │   └── administration/
│   ├── lib/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── decimal/
│   │   ├── errors/
│   │   └── formatting/
│   ├── hooks/
│   ├── routes/
│   ├── styles/
│   ├── test/
│   └── main.tsx
├── package.json
└── vite.config.ts
```

Contoh ini bukan struktur wajib.

Susun berdasarkan kebutuhan aktual agar tidak berlebihan.

## Component Reuse

Bangun komponen reusable yang sesuai FigCraft:

- Button.
- Input.
- Checkbox.
- Select.
- FormField.
- WeightInputGroup.
- PriceTag.
- StatusBadge.
- SearchField.
- DateRangeFilter.
- DataTable.
- ConfirmDialog.
- StateFeedbackCard.
- PublicNavbar.
- InternalSidebar.
- InternalHeader.
- PageHeader.
- Breadcrumb.
- LocationLink.
- LoadingSkeleton.
- EmptyState.
- ErrorState.

Jangan membuat komponen generik abstrak yang menyulitkan penggunaan.

Jangan menduplikasi sidebar untuk setiap role.

Gunakan shared component dengan navigation configuration per role.

---

# 10. APPLICATION SHELL REQUIREMENTS

## Desktop

InternalSidebar harus:

- Memiliki lebar tetap sesuai desain, baseline 256px jika dikonfirmasi token/handoff.
- Berada di sisi kiri.
- Tidak berubah lebar antar halaman.
- Tidak ikut bergeser saat konten kanan panjang.
- Mendukung menu aktif.
- Menampilkan menu sesuai role.
- Menyediakan logout.
- Menggunakan komponen yang sama antar role.

Area konten kanan harus:

- Mengisi sisa viewport.
- Mempunyai scroll vertikal sendiri sesuai desain.
- Tidak menumpuk di bawah sidebar.
- Tidak menyebabkan horizontal overflow halaman.
- Mendukung tabel panjang.

## Tablet

Gunakan pola navigation collapse sesuai FigCraft.

Jangan mempertahankan sidebar desktop penuh jika membuat konten sempit.

## Mobile

Gunakan accessible drawer/sheet.

- Dapat dibuka dan ditutup.
- Bisa ditutup dengan Escape.
- Focus management benar.
- Target sentuh memadai.
- Tidak menghalangi penggunaan form.
- Tidak menyebabkan body horizontal overflow.

Implementasikan loading, error, empty, stale, success, dan permission-denied states pada shell maupun halaman.

---

# 11. ROUTING — 26 CANONICAL ROUTES

Gunakan `AFD.md §36` sebagai daftar resmi 26 rute.

Gunakan TanStack Router.

Jangan mengganti dengan React Router.

Implementasikan:

- Public routes.
- Authentication.
- Farmer routes.
- Cooperative routes.
- Perumda operations routes.
- Finance workflows.
- Mill/PKS routes.
- Director routes.
- Administrator routes.

Contoh rute publik:

- `/`
- `/harga-tbs`
- `/pks/:id`
- `/lokasi-pks`
- `/tentang`
- `/kemitraan`
- `/kontak`
- `/login`

Gunakan seluruh daftar internal sesuai AFD.

Jangan menganggap contoh rute ini sebagai keseluruhan daftar 26.

## Route Acceptance

Setiap rute harus memiliki:

- Page yang benar.
- Layout yang sesuai.
- Navigation.
- Role guard.
- Permission guard jika diperlukan.
- API dependencies.
- Loading state.
- Empty state.
- Error state.
- Responsive behavior.
- Document title.
- Test.
- Kesesuaian dengan FigCraft.

Jangan membuat semua halaman hanya menampilkan "Coming Soon" dan menganggap route coverage selesai.

---

# 12. AUTHENTICATION & API SECURITY

Gunakan backend B11.1 sebagai implementasi otoritatif.

Sesi menggunakan:

- HttpOnly session cookie.
- Server-side sessions.
- CSRF token.
- Role permissions.
- Resource scope.

## Login Workflow

Implementasikan:

1. Login page.
2. CSRF bootstrap sesuai kontrak.
3. Credential submission.
4. Session cookie handling.
5. `/auth/me`.
6. Role-aware redirection.
7. Unauthorized/expired states.
8. Logout.
9. Session revocation handling.

Jangan menyimpan session token pada:

- `localStorage`.
- `sessionStorage`.
- URL query.
- JavaScript-readable cookie buatan frontend.

Gunakan `credentials: "include"` jika sesuai konfigurasi request client.

Gunakan Vite dev proxy atau konfigurasi origin yang cocok dengan kebijakan cookie dan CSRF backend.

Periksa `Origin` serta perilaku cookie pada localhost.

Jangan menonaktifkan CSRF untuk mempermudah development.

Jangan membuat localStorage fallback auth palsu.

## RBAC

Gunakan:

`contracts/role-permissions.yaml`

Frontend hanya melakukan role-aware rendering dan route guard demi UX.

Backend tetap menjadi otoritas keamanan.

Jangan menganggap tombol tersembunyi sebagai authorization.

---

# 13. OPENAPI-FIRST API CLIENT

Buat TypeScript types dari:

`contracts/openapi.v1.yaml`

Gunakan `openapi-typescript` dan API client typed yang sesuai.

Jangan menyalin manual ratusan interface dari OpenAPI.

Jangan menggunakan `any` untuk mempermudah integrasi.

## API Layer

Implementasikan:

- Typed requests.
- Typed responses.
- Standard envelope parsing.
- Error catalog mapping.
- Query keys.
- Cache invalidation.
- Retry policy.
- Pagination.
- Filtering.
- Sorting.
- Request cancellation.
- Authentication handling.
- CSRF propagation.
- Request ID display.
- Idempotency-Key handling.

## Error Handling

Gunakan:

`contracts/error-catalog.yaml`

Tampilkan pesan Indonesia yang jelas.

Pertahankan error code teknis untuk debugging, bukan sebagai pesan utama pengguna.

Tangani:

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 

Jangan menampilkan notifikasi sukses jika backend sebenarnya mengembalikan error.

## Numeric Values

Gunakan decimal string sesuai kontrak.

Jangan memakai JavaScript floating point untuk menghitung atau membulatkan berat, kuota, harga, atau nilai keuangan otoritatif.

Gunakan library desimal presisi jika kalkulasi pratinjau memang diperlukan.

Server tetap otoritas perhitungan final.

Tampilkan angka dalam format Indonesia, tetapi kirim nilai dalam format API kanonis.

## Idempotency

Untuk delapan operasi yang diwajibkan M0.1:

- Buat Idempotency-Key unik untuk satu tindakan logis.
- Pertahankan key ketika mengulangi request yang sama akibat gangguan jaringan.
- Jangan menggunakan key yang sama untuk tindakan bisnis yang berbeda.
- Jangan otomatis mengulang mutasi berisiko tanpa mempertimbangkan response dan retryability.
- Tampilkan state penyimpanan agar pengguna tidak menekan tombol berkali-kali.

---

# 14. MOCK DATA VS REAL DATA

Gunakan fixtures:

`contracts/fixtures/`

MSW boleh digunakan untuk:

- UI development.
- Story/state testing.
- Unit/integration frontend tests.
- Development ketika backend sementara tidak tersedia.

Namun:

**Jangan membuat aplikasi seolah-olah sudah terhubung backend padahal sedang membaca fixture MSW.**

Buat mode development yang jelas:

- MOCK.
- REAL API.

Dalam mode REAL API:

- Jangan diam-diam fallback ke data fixture ketika request gagal.
- Tampilkan network error yang sesuai.
- Jangan membuat harga atau status transaksi palsu.
- Jangan membuat pembayaran palsu terlihat telah selesai.

Data simulasi bisnis tetap harus memiliki penanda.

---

# 15. PUBLIC PORTAL

Implementasikan portal publik sesuai FigCraft D5.

Fitur:

- Homepage.
- Harga TBS multi-PKS.
- Filter harga/kategori/sumber.
- Detail PKS.
- Lokasi PKS.
- Profil Perumda Unit Agro Niaga.
- Kemitraan.
- Kontak.

## Privacy

Pastikan:

- Harga PKS dan referensi Disbun dibedakan.
- Harga belum diverifikasi tidak tampil sebagai harga berlaku.
- Data PKS yang `is_public=false` tidak ditampilkan.
- Koordinat yang belum diverifikasi tidak dibuat-buat.
- Kontrak komersial privat tidak tampil.
- Kuota privat tidak tampil.
- Identitas petani tidak bocor.
- No-data state jelas.

Gunakan MapLibre jika sesuai desain dan ketentuan TRD.

Jangan membuat marker peta fiktif.

Jangan membuat informasi harga live jika data backend sebenarnya kosong.

---

# 16. ROLE-SPECIFIC INTERNAL PORTALS

Implementasikan seluruh halaman berdasarkan AFD dan PRD.

## A. Farmer / Petani

Fokus:

- Ringkasan hasil panen.
- Riwayat penerimaan TBS.
- Status pengiriman yang berhak dilihat.
- Ringkasan settlement.
- Status pembayaran yang sebenarnya.

Jangan menyatakan petani sudah dibayar hanya karena PKS sudah membayar Perumda.

## B. Cooperative Operator

Fokus:

- Master petani.
- Master kebun.
- Penerimaan TBS.
- Penimbangan.
- Grading.
- Konsolidasi muatan.
- Pembuatan e-DO.
- Detail QR.
- Status pengiriman.

Terapkan FLOW-05.

## C. Perumda Operations

Fokus:

- Dashboard operasional.
- Master PKS.
- Harga.
- Kontrak.
- Kuota.
- Logistik.
- Rekonsiliasi.
- Dispute management.

Terapkan FLOW-06.

## D. Perumda Finance

Fokus:

- Invoice.
- Piutang.
- Utang.
- Persetujuan pembayaran.
- Bukti pembayaran.
- Verifikasi.
- Status settlement.
- Pemisahan AR/AP.

## E. PKS Operator

Fokus:

- Verifikasi e-DO/QR.
- Pencatatan tiket timbang.
- Grading.
- Bukti timbang.
- Koreksi dan riwayat tiket.

## F. Director / Direksi

Fokus:

- Dashboard eksekutif.
- KPI terotorisasi.
- Daftar persetujuan.
- Detail keputusan.
- Maker-checker restrictions.

## G. System Administrator

Fokus:

- User management.
- Role/scope management.
- Audit viewer.
- System health.
- Rule versions yang diizinkan.
- CCTV Digital/observability.

**SYSTEM_ADMIN tidak otomatis memiliki hak persetujuan keuangan atau bisnis.**

Gunakan `BR-SYS-002` dan `SOD-01..06`.

---

# 17. BUSINESS WORKFLOW IMPLEMENTATION

Buat antarmuka workflow yang benar-benar terhubung.

Contoh alur utama:

Petani / Koperasi
→ Penerimaan TBS
→ Timbang Ramp
→ Grading
→ Kontrak & Kuota
→ Konsolidasi e-DO
→ Pengiriman
→ Tiket Timbang PKS
→ Rekonsiliasi
→ Persetujuan
→ Invoice
→ Pembayaran Manual
→ Verifikasi
→ Reporting & Audit

Seluruh status dan transisi mengikuti:

`contracts/state-catalog.yaml`

Jangan menentukan sendiri kapan status boleh berubah.

## Critical Guards

- Tidak boleh membuat pengiriman dari receipt yang tidak memenuhi syarat.
- Tidak boleh mengalokasikan receipt dua kali.
- Tidak boleh melampaui kuota.
- Tidak boleh mengubah timbang yang sudah terkunci.
- Tidak boleh menyetujui transaksi sendiri jika SoD melarang.
- Tidak boleh menganggap APPROVED sama dengan PAID.
- Tidak boleh menyelesaikan final settlement saat model bisnis masih UNCONFIRMED.
- Tidak boleh mengabaikan dispute/HOLD.
- Tidak boleh membuat keputusan SOP baru di frontend.

Frontend harus menampilkan penjelasan yang manusiawi ketika aksi diblokir.

---

# 18. FORM UX REQUIREMENTS

Seluruh form bisnis harus menggunakan:

- React Hook Form.
- Zod.
- Typed API client.
- Reusable field components.
- Inline validation.
- Accessible error messages.
- Clear required/optional fields.
- Proper disabled/loading state.
- Confirmation for critical actions.
- Unsaved changes warning jika relevan.

## Required States

- Initial.
- Editing.
- Validating.
- Submitting.
- Success.
- Validation error 422.
- Conflict 409.
- Unauthorized 401.
- Forbidden 403.
- Network failure.
- Session expired.
- Idempotent replay.
- Stale version conflict.

Untuk formulir timbang:

- Bruto.
- Tara.
- Netto hasil server.
- Presisi angka.
- Validasi berat.
- Riwayat revisi.
- Alasan koreksi.

Jangan menghitung netto final hanya di frontend dan mengirimkannya sebagai kebenaran transaksi.

---

# 19. RESPONSIVE REQUIREMENTS

Wajib uji:

- 1440px.
- 1280px.
- 768px.
- 390px.
- 375px.

Gunakan FigCraft sebagai acuan.

## No Horizontal Overflow

Jangan biarkan halaman overflow horizontal secara global.

Untuk tabel:

- Gunakan container scroll horizontal bila benar-benar dibutuhkan.
- Pertahankan label kolom.
- Pertimbangkan kartu/detail drill-down mobile untuk data prioritas.
- Jangan memotong konten kritis.

## Touch Targets

Target interaktif minimal 44 × 44 px pada UI mobile, kecuali pengecualian aksesibilitas yang sah.

## Responsive Business Flows

Prioritaskan:

- Login.
- Input timbang koperasi.
- Detail QR/e-DO.
- Tiket timbang PKS.
- Rekonsiliasi.
- Ringkasan pembayaran petani.
- Detail PKS publik.

Responsivitas tidak boleh hanya sebatas homepage.

---

# 20. ACCESSIBILITY

Target minimum WCAG 2.2 AA yang relevan.

Implementasikan:

- Semantic HTML.
- Label form.
- Heading hierarchy.
- Keyboard navigation.
- Visible focus.
- Skip links.
- ARIA yang tepat.
- Error announcement.
- Live region untuk feedback penting.
- Correct dialog focus trap.
- Accessible dropdown/menu.
- Contrast.
- Reduced motion.
- Accessible data tables.
- Screen-reader friendly status.
- Loading announcements bila dibutuhkan.

Jangan menggunakan ARIA untuk menggantikan elemen HTML semantik yang sebenarnya sudah tersedia.

Lakukan browser accessibility testing nyata.

---

# 21. FRONTEND PERFORMANCE ENGINEERING

Optimalkan:

- Route-level lazy loading.
- Code splitting.
- Tree shaking.
- TanStack Query caching.
- Query stale time sesuai kebutuhan.
- Request deduplication.
- Debounced search.
- Abort/cancellation.
- Pagination.
- Virtualization hanya jika dibutuhkan.
- Efficient React rendering.
- Stable query keys.
- Memoization selektif.
- Avoid unnecessary effects.
- Avoid unnecessary rerenders.
- Avoid large runtime dependencies.
- Asset optimization.
- Font loading.
- Bundle splitting.

Jangan menambahkan `useMemo` atau `useCallback` pada setiap fungsi tanpa alasan.

Jangan membuat dashboard mengirim request berulang tanpa kendali.

Jangan menyimpan cache data sensitif lintas sesi pengguna.

Saat logout, bersihkan cache query sensitif.

Ikuti performance targets dari TRD/IPD.

Ukur hasil aktual menggunakan browser, bukan perkiraan.

---

# 22. VISUAL QA — FIGCRAFT COMPARISON

Setelah layar diimplementasikan:

1. Buka desain FigCraft yang sesuai.
2. Buka frontend pada viewport yang sama.
3. Capture screenshot browser.
4. Bandingkan layout, spacing, warna, font, hierarchy, alignment, dan density.
5. Periksa navigation active state.
6. Periksa form states.
7. Periksa empty/error/loading states.
8. Perbaiki penyimpangan visual.
9. Uji mobile.
10. Lakukan verifikasi ulang.

Jangan menilai kualitas visual hanya dari keberhasilan `npm run build`.

Jangan mengklaim pixel-perfect tanpa membandingkan hasil.

Fokus utama: design fidelity, readability, usability, dan konsistensi.

Tidak perlu menghasilkan file screenshot permanen untuk setiap perubahan kecil; simpan bukti yang penting bagi quality gate saja.

Jika bukti berbentuk file tes atau screenshot diperlukan, jangan membuat changelog/progress report kedua. Catat lokasi dan hasilnya pada checkpoint utama.

---

# 23. COMPLETE F0–F11 IMPLEMENTATION POLICY

**BACA IPD.md TERLEBIH DAHULU UNTUK NAMA, URUTAN, DELIVERABLE, DAN EXIT GATE RESMI SETIAP MILESTONE.**

Jangan mengganti definisi F0–F11 dengan interpretasi sendiri.

Buat mapping awal dari IPD:

| Milestone | Official Name | Dependencies | Deliverables | Exit Gate |
| --------- | ------------- | ------------ | ------------ | --------- |
| F0        | Dari IPD      | Dari IPD     | Dari IPD     | Dari IPD  |
| F1        | Dari IPD      | Dari IPD     | Dari IPD     | Dari IPD  |
| ...       | ...           | ...          | ...          | ...       |
| F11       | Dari IPD      | Dari IPD     | Dari IPD     | Dari IPD  |

Kemudian kerjakan seluruhnya.

Gunakan tahapan pekerjaan berikut sebagai kelompok kebutuhan lintas milestone, dengan urutan resmi tetap mengikuti IPD.

## FOUNDATION

- React/Vite audit.
- Dependency setup.
- TypeScript strict.
- Tailwind CSS v4.
- Design token import.
- Router.
- Query provider.
- Typed API client.
- MSW.
- Environment configuration.
- Testing foundation.

## DESIGN SYSTEM

- Atomic components.
- Layout templates.
- Sidebar.
- Navbar.
- Forms.
- Tables.
- Feedback states.
- Dialogs.
- Role-specific navigation.

## PUBLIC PORTAL

- Delapan rute publik sesuai AFD.
- Harga.
- PKS.
- Profil.
- Kemitraan.
- Kontak.
- Privacy.
- Mobile responsive.

## AUTHENTICATION & APP SHELL

- Login.
- Session.
- CSRF.
- Logout.
- RBAC.
- Scope.
- Route guards.
- Unauthorized/expired states.

## INTERNAL BUSINESS PORTALS

- Petani.
- Koperasi.
- Perumda.
- Finance.
- PKS.
- Direksi.
- Admin.

## BUSINESS WORKFLOWS

- Master Data.
- Receiving.
- Pricing.
- Contracts.
- Quota.
- Logistics.
- Mill weighing.
- Reconciliation.
- Invoices.
- Payments.
- Reporting.
- Audit.

## FINAL VERIFICATION

- Route coverage.
- Contract coverage.
- Real backend integration.
- Accessibility.
- Responsiveness.
- Security.
- Performance.
- Visual parity.
- Browser E2E.
- Regression testing.

Jangan mengabaikan pekerjaan UI hanya karena API backend sudah tersedia.

Jangan mengabaikan integrasi API hanya karena desain terlihat selesai.

---

# 24. TESTING STRATEGY

Jalankan pengujian otomatis pada setiap milestone.

## Static Quality

- TypeScript typecheck.
- ESLint jika dikonfigurasi.
- Formatting.
- Production build.
- Import/module boundaries.
- Dead code review.

## Component Testing

- Component rendering.
- Input behavior.
- Validation.
- Dialog.
- Table.
- Navigation.
- Status badges.
- Accessibility.

## Integration Testing

- TanStack Query hooks.
- MSW contract responses.
- Error handling.
- CSRF.
- Session expiration.
- Form mutation.
- Pagination.
- Cache invalidation.
- Idempotent retry.

## Browser E2E

Gunakan Playwright untuk:

- Public navigation.
- Login/logout.
- Role routing.
- Form validation.
- Receiving workflow.
- e-DO workflow.
- PKS ticket workflow.
- Reconciliation.
- Finance simulation.
- Admin access.
- Error states.
- Responsive navigation.

## Security Negative Testing

Minimal:

- Guest membuka internal route.
- Farmer membuka data farmer lain.
- Cooperative operator membuka koperasi lain.
- PKS operator membuka PKS lain.
- SYSTEM_ADMIN melakukan approval bisnis.
- Expired session.
- Invalid CSRF.
- Duplicate mutation.
- Stale version.
- Pending SOP financial action.

Validasi penolakan backend nyata pada integration tests yang sesuai.

Jangan hanya menguji bahwa tombol frontend tersembunyi.

## Visual Testing

Screenshot pada breakpoint prioritas.

Periksa:

- Sidebar.
- Desktop grids.
- Mobile drawer.
- Forms.
- Tables.
- Dialogs.
- Overflow.
- Alignment.
- Fonts.
- Contrast.
- Loading.
- Empty/error states.

## Contract Regression

Pastikan kontrak tetap valid:

`contracts/scripts/validate_contracts.py`

Dan suite pengujian M0.1 tetap lulus.

Backend tests relevan harus tetap PASS apabila environment tersedia, terutama pada final integration gate.

Jangan mengubah backend hanya untuk memperbaiki test frontend.

---

# 25. REAL BACKEND INTEGRATION POLICY

Backend telah mencapai:

`READY — B11_1_POST_IMPLEMENTATION_VERIFIED`

Namun sebelum tes integrasi:

- Periksa PostgreSQL.
- Periksa Redis.
- Periksa `/health/live`.
- Periksa `/health/ready`.
- Periksa environment backend.
- Periksa base URL API.
- Pastikan database development dan test terpisah.

Gunakan API real untuk integration gate.

Jangan menjalankan automated E2E mutasi terhadap database operasional yang berisi data penting.

Gunakan akun dan data sintetis.

Jangan membuat seed production credentials.

Jika layanan backend belum berjalan dan startup aman dilakukan, gunakan langkah resmi `backend/README.md`.

Jika layanan tidak tersedia:

- Tetap kerjakan unit tests dan MSW.
- Catat real integration sebagai BLOCKED/NOT_RUN.
- Jangan mengklaim end-to-end integrated PASS.

## Backend Scope Protection

Jangan mengubah:

- `backend/app/`
- `backend/alembic/`
- `backend/pyproject.toml`
- `backend/uv.lock`
- `contracts/`
- `docs/PRD.md` sampai `docs/IPD.md`

Jika menemukan masalah kontrak, buat catatan defect di checkpoint dengan operationId, request, response, dan expected behavior.

Jangan memperbaiki backend secara diam-diam.

---

# 26. SECURITY & SOP REPRESENTATION

Frontend harus mempertahankan aturan:

- `CONFIRMED`.
- `SIMULATION_ONLY`.
- `PENDING_SOP`.
- `FUTURE`.

Jika nilai hanya simulasi, tampilkan label secara jelas.

Contoh:

- Data Simulasi.
- Aturan Simulasi.
- Pending SOP.
- Menunggu pengesahan kebijakan.

Jangan menampilkan angka 1,5% atau 2% sebagai kebijakan final tanpa konteks.

Jangan membuat fitur persetujuan keuangan terlihat bebas dipakai ketika backend sedang menolak finalisasi.

Jika backend mengembalikan:

`FIN_POLICY_UNCONFIRMED`

Tampilkan pesan yang menjelaskan bahwa transaksi belum dapat difinalisasi karena kebijakan operasional belum disahkan.

Jangan mencoba mem-bypass guard.

---

# 27. GIT & SAFE EDIT BOUNDARIES

Sebelum coding:

1. Jalankan `git status`.
2. Baca branch aktif.
3. Catat HEAD commit.
4. Deteksi perubahan yang belum di-commit.
5. Pisahkan pekerjaan frontend dari perubahan backend sebelumnya.
6. Jangan reset repository.
7. Jangan menghapus user changes.
8. Jangan membuat Git branch baru tanpa kebutuhan atau kebijakan proyek.

## Allowed Files

- `frontend/**`
- `.gitignore` jika diperlukan
- `docs/IMPLEMENTATION_CHECKPOINTS.md`

Perubahan lain hanya dengan alasan dan otorisasi yang sesuai.

Dilarang mengubah:

- Backend implementation.
- Backend migrations.
- FigCraft source.
- Contracts M0.1.
- Six baseline documents V1.1.

Jangan melakukan `git push` otomatis.

Jangan melakukan commit otomatis kecuali telah mendapat izin atau terdapat workflow repository yang secara eksplisit mengizinkannya.

---

# 28. SINGLE CHANGELOG & CHECKPOINT FILE

**Wajib gunakan hanya satu file pencatatan progres:**

`docs/IMPLEMENTATION_CHECKPOINTS.md`

Jangan membuat:

- `F0_CHANGELOG.md`
- `F1_REPORT.md`
- `FRONTEND_PROGRESS.md`
- `FRONTEND_IMPLEMENTATION_REPORT.md`
- `UIUX_CHANGELOG.md`
- `DAILY_LOG.md`
- `FINAL_FRONTEND_REPORT.md`

Jangan membuat 12 dokumen progres terpisah.

## Checkpoint Contents

Tambahkan bagian:

`FRONTEND DEVELOPMENT TRACK`

Untuk setiap F0–F11 catat:

- Milestone ID.
- Nama resmi.
- Status.
- Tanggal.
- Baseline commit.
- Scope.
- Skill digunakan.
- File dibuat.
- File diubah.
- Library baru.
- Fitur selesai.
- Route coverage.
- API integration coverage.
- Visual QA.
- Responsive QA.
- Accessibility QA.
- Unit/component/integration/E2E tests.
- Build.
- Errors.
- Bugs fixed.
- Quality gate.
- Known limitations.
- Pending SOP.
- Next action.

Gunakan format ringkas, faktual, dan terstruktur.

Pertahankan seluruh histori:

- D4.
- D5.
- M0.
- M0.1.
- B0–B11.
- B11.1.

Jangan menghapus catatan backend atau desain.

Dokumentasi yang diperlukan untuk menjalankan aplikasi, seperti `frontend/README.md`, konfigurasi, generated types, dan test files tetap diperbolehkan. Larangan satu file hanya berlaku untuk **laporan progres serta changelog terpisah**.

---

# 29. MILESTONE QUALITY GATES

Setiap milestone F0–F11 harus melewati:

## Functional

- Requirement terpenuhi.
- Rute berjalan.
- Aksi berfungsi.
- API sesuai kontrak.
- Tidak ada fake success.

## Design

- Mengikuti D5.
- Menggunakan tokens.
- Reusable Atomic Design.
- Visual konsisten.
- Anti-AI-slop.

## Security

- Role guard.
- Permission-aware UI.
- Session/CSRF sesuai kontrak.
- Tidak ada token sensitif dalam browser storage.

## Accessibility

- Keyboard navigation.
- Focus.
- Label.
- Contrast.
- Dialog semantics.
- Screen reader behavior.

## Responsive

- 
- 
- 
- 
- 
- No global horizontal overflow.

## Engineering

- TypeScript strict.
- Tidak ada type errors.
- Tidak ada build errors.
- Tidak ada critical lint errors.
- No unnecessary duplication.
- No uncontrolled dependencies.

## Testing

- Automated tests dijalankan.
- Browser smoke tests dijalankan pada milestone relevan.
- Regression tests PASS.
- Tidak ada critical failure.

## Documentation

- Single checkpoint updated.
- Evidence tercatat.
- Known limitations jelas.

Tidak boleh menandai PASS jika quality gate kritis belum dieksekusi.

---

# 30. AUTONOMOUS EXECUTION POLICY

Kerjakan seluruh frontend F0–F11 dalam satu rangkaian pekerjaan terstruktur selama batas sesi dan lingkungan memungkinkan.

Jangan berhenti setelah membuat rencana.

Jangan berhenti setelah membuat halaman pertama.

Jangan hanya membuat mockup.

Setiap milestone:

1. Read requirement.
2. Discover relevant skills.
3. Inspect current code.
4. Plan small implementation units.
5. Implement.
6. Run tests.
7. Fix defects.
8. Review design.
9. Run browser testing.
10. Update checkpoint.
11. Verify exit gate.
12. Continue to next milestone.

Jangan lanjut jika milestone memiliki blocker kritis.

Jika pekerjaan terhenti karena batas sesi/konteks, simpan status aktual di checkpoint. Sesi berikutnya harus melanjutkan dari hasil terverifikasi, bukan mengulang pekerjaan yang sudah benar.

Jangan mengklaim dapat bekerja di background atau memberikan hasil yang belum dieksekusi.

Gunakan agent subtask jika tersedia dan aman, dengan kepemilikan file jelas agar perubahan tidak bertabrakan.

---

# 31. FINAL FRONTEND ACCEPTANCE CRITERIA

Frontend dianggap selesai jika:

1. F0–F11 mengikuti IPD dan lulus.
2. React 19 + TypeScript strict + Vite berjalan.
3. Tailwind CSS v4 menggunakan token D5.
4. TanStack Router terkonfigurasi.
5. TanStack Query terkonfigurasi.
6. Typed API client menggunakan OpenAPI.
7. Atomic Design lima level diterapkan.
8. Seluruh 26 rute memiliki halaman fungsional.
9. Seluruh role memiliki akses sesuai permission.
10. Login dan logout bekerja.
11. CSRF bekerja.
12. Session expiry ditangani.
13. Role/scope errors ditangani.
14. Public portal tidak mengekspos data privat.
15. Form data bisnis berfungsi.
16. Workflow Receiving berjalan.
17. Workflow Contracts/Quota berjalan.
18. Workflow e-DO berjalan.
19. Workflow PKS Ticket berjalan.
20. Workflow Reconciliation berjalan.
21. Finance simulation mengikuti SOP guards.
22. Reporting terhubung.
23. Audit/admin terhubung.
24. Tidak ada dead button atau dead link untuk fitur MVP.
25. Tidak ada fake success.
26. Tidak ada nilai keuangan yang dihitung dengan float biasa sebagai hasil otoritatif.
27. Responsive 375–1440px.
28. Tidak ada horizontal overflow global.
29. Keyboard accessibility berfungsi.
30. Critical focus/ARIA behavior benar.
31. Loading, empty, error, dan success states tersedia.
32. Unit/component/integration tests lulus.
33. Browser E2E lulus.
34. Visual QA terhadap FigCraft D5 selesai.
35. Production build lulus.
36. Backend integration tests relevan lulus.
37. Pending SOP tetap jelas.
38. Tidak ada perubahan backend tanpa izin.
39. Tidak ada secret terekspos.
40. Checkpoint mencerminkan hasil aktual.

---

# 32. FINAL READINESS LEVELS

Gunakan status yang jujur.

## `FRONTEND_IN_PROGRESS`

Jika F0–F11 belum selesai.

## `FRONTEND_INDEPENDENT_READY`

Jika frontend lengkap dan terverifikasi menggunakan MSW, tetapi belum berhasil menyelesaikan integrasi backend nyata.

## `FRONTEND_BACKEND_INTEGRATION_VERIFIED`

Jika frontend lengkap, seluruh quality gate relevan PASS, dan integrasi dengan FastAPI nyata telah diverifikasi pada environment uji.

## `FRONTEND_CONDITIONALLY_READY`

Jika hanya terdapat kekurangan nonkritis, dengan cakupan dan risiko yang dijelaskan secara eksplisit.

## `FRONTEND_BLOCKED`

Jika ada masalah kritis pada keamanan, fungsi inti, integritas data, kontrak, atau integrasi.

Jangan menggunakan status READY hanya karena `npm run build` berhasil.

Jangan mengklaim production-ready sebelum ada pengujian deployment dan keputusan operasional yang diperlukan.

---

# 33. FINAL RESPONSE FORMAT

Setelah menyelesaikan pekerjaan, tuliskan ringkasan di chat:

### A. Overall Status

- Current milestone.
- Last passed milestone.
- Frontend readiness.
- Baseline Git.

### B. Milestone Results

Tabel F0–F11 berisi status aktual dan quality gate.

### C. Architecture

- React.
- TypeScript.
- Tailwind.
- Atomic Design.
- Routing.
- API layer.
- State management.
- Testing architecture.

### D. UI/UX

- FigCraft parity.
- Reusable components.
- Responsive.
- Accessibility.
- Anti-AI-slop compliance.

### E. Functional Coverage

- Public portal.
- Petani.
- Koperasi.
- Perumda.
- Finance.
- PKS.
- Direksi.
- Admin.

### F. API Coverage

- Integrated operations.
- MSW operations.
- Missing operations.
- Error handling.
- Auth/CSRF.
- Idempotency.

### G. Testing

- Typecheck.
- Lint.
- Build.
- Unit tests.
- Component tests.
- Integration tests.
- Playwright.
- Visual verification.
- Accessibility.
- Performance.

### H. Problems and Fixes

- Bugs found.
- Bugs fixed.
- Unresolved blockers.
- Pending SOP.

### I. Checkpoint

- File updated.
- Last quality gate.
- Next recommended action.

### J. Final Decision

Gunakan status berdasarkan bukti.

Tidak perlu membuat file laporan progres terpisah.

---

# 34. START EXECUTION NOW

Urutan eksekusi wajib:

1. Verifikasi root workspace.
2. Catat Git baseline dan perubahan yang sudah ada.
3. Periksa React frontend existing.
4. Baca enam dokumen V1.1.
5. Baca ADR.
6. Baca M0/M0.1.
7. Baca contracts dan fixtures.
8. Baca checkpoint B11.1.
9. Discover skill lokal.
10. Baca skill relevan.
11. Periksa FigCraft D5.
12. Ekstrak seluruh F0–F11 dari IPD.
13. Petakan 26 rute AFD.
14. Petakan role, permission, dan API dependencies.
15. Mulai F0 pada frontend yang sudah terinstal.
16. Jalankan quality gate F0.
17. Perbaiki kegagalan F0.
18. Catat hasil di checkpoint.
19. Lanjutkan F1.
20. Ulangi sampai F11.
21. Jalankan full regression.
22. Jalankan live backend integration.
23. Jalankan responsive/a11y/browser QA.
24. Periksa Git diff.
25. Tetapkan final readiness.
26. Berikan ringkasan hasil dan bukti.

## FINAL NON-NEGOTIABLE INSTRUCTIONS

- Jangan membuat ulang frontend.
- Jangan membuat ulang backend.
- Jangan mengubah shared contracts tanpa proses change management.
- Jangan mengubah desain FigCraft D5 secara sepihak.
- Jangan mengabaikan skill yang relevan.
- Jangan membuat UI bergaya AI-slop.
- Jangan membuat halaman dummy sebagai pengganti fitur Core MVP.
- Jangan menganggap mock API sebagai bukti integrasi backend.
- Jangan mengabaikan permission dan session security.
- Jangan mengarang data operasional.
- Jangan menyembunyikan Pending SOP.
- Jangan membuat laporan progres terpisah per milestone.
- Jangan menghapus perubahan B11.1 yang belum di-commit.
- Jangan melewati quality gate.
- Jangan menyatakan PASS tanpa menjalankan tes.

**Target utama: frontend yang profesional secara visual, benar secara workflow, aman secara integrasi, nyaman digunakan oleh manusia, dan mudah dipelihara.**

**Final objective: `FRONTEND_BACKEND_INTEGRATION_VERIFIED`**

START WITH DOCUMENT, CONTRACT, SKILL, AND FIGCRAFT DISCOVERY. THEN EXECUTE F0–F11.
