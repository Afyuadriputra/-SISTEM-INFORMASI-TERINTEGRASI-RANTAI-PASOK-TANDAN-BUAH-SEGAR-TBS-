# M0 Document Discovery & Baseline Audit Report (`M0-A`)

**Milestone:** `M0 — Requirements & Contract Alignment`  
**Tanggal:** 2026-11-10  
**Git Baseline:** Branch `main`, commit `b081695` (`baru`)  
**Status Fase M0-A:** `PASS`

---

## 1. Inventaris Sumber & Verifikasi Keberadaan Nyata

| Sumber Dokumen / Artefak | Path Terverifikasi | Ukuran / Baris | Versi & Status Sumber | Keterangan Pemeriksaan |
| :--- | :--- | :---: | :--- | :--- |
| **PRD** | [PRD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/PRD.md) | 1.999 baris (66.992 B) | `V1.1 — Draft Baseline` (10 Nov 2026) | Dibaca penuh (`1–1999`). Sumber prioritas kebutuhan, aktor (`ROLE-01..07`), `FR-*`, `NFR-*`, `BR-*`, `AC-*`, `DEC-001..015`. |
| **TRD** | [TRD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/TRD.md) | 1.980 baris (62.684 B) | `V1.1 — Technical Architecture Baseline` | Dibaca penuh (`1–1980`). Sumber 11 modul backend, 4 layer Clean Architecture, security, Redis cache, CCTV Digital observability, standar REST `/api/v1/`, health checks. |
| **AFD** | [AFD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/AFD.md) | 2.462 baris (71.451 B) | `V1.1 — Application Flow Baseline` | Dibaca penuh (`1–2462`). Sumber `FLOW-01..24`, state transitions (§28–31), 26 rute frontend (§36), page states (§38), 15 validasi SOP (§41), skenario E2E (§35). |
| **DBD** | [DBD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/DBD.md) | 2.816 baris (77.316 B) | `V1.1 — Database & UX Data Architecture Baseline` | Dibaca penuh (`1–2816`). Sumber 48 tabel logis, presisi numerik (`NUMERIC(14,3)/(18,2)/(20,2)/(9,4)`), UUID, partial unique indexes, 25 Laws of UX, `DBD-DEC-001..015`. |
| **BSD** | [BSD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/BSD.md) | 2.461 baris (70.333 B) | `V1.1 — Business Rules & Operations Baseline` | Dibaca penuh (`1–2461`). Sumber aturan domain (`BR-*`), 30 skenario uji `BIZ-001..030`, SOP-01..08, 20 keputusan bisnis `BSD-DEC-001..020`. |
| **IPD** | [IPD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/IPD.md) | 3.205 baris (75.657 B) | `V1.1 — Solo Developer Execution Baseline` | Dibaca penuh (`1–3205`). Sumber milestone `M0`, `B0–B11`, `F0–F11`, `I0–I4`, format envelope response API (§4.3), daftar endpoint minimum (§7.1), `IPD-DEC-001..012`. |
| **Checkpoints** | [IMPLEMENTATION_CHECKPOINTS.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/IMPLEMENTATION_CHECKPOINTS.md) | Diperbarui untuk M0 | `D4` + `D5 READY` + `M0` | Riwayat D4 & D5 dipelihara utuh tanpa penghapusan. |
| **FigCraft D5 Report** | [d5-design-gap-closure-signoff.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/d5-design-gap-closure-signoff.md) | 165 baris | **`READY — FIGCRAFT_DESIGN_SIGNOFF`** | Diverifikasi: 26/26 rute mandiri `AFD §36`, 50 frame/board `readyForDev`, 393 instance komponen, 45 variabel, 14 flow (215 interaksi, 0 dangling), 7 layar bisnis mobile `390px`, `0/1451` fail kontras. |
| **FigCraft Historis (D4 & Handoff)** | [design-verification-signoff-report.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/design-verification-signoff-report.md), [design-qa-handoff.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/design-qa-handoff.md), [phase-a-ux-architecture.md](file:///C:/Users/M-SI/.gemini/antigravity/brain/c367ac0e-9189-476d-b1f9-69ba6e1730ec/phase-a-ux-architecture.md) | Diverifikasi | D4 historis (`CONDITIONALLY_READY`) & Handoff UX | Diperiksa hanya sebagai konteks historis; D5 dipakai sebagai baseline desain aktif (`READY — FIGCRAFT_DESIGN_SIGNOFF`). Salinan `ouput/design-verification-signoff-report.md` terverifikasi identik dengan artefak D4 (`Compare-Object = 0`). |
| **Berkas & Token FigCraft** | [agroniaga-tbs-perumda-tuah-sekata.figcraft](file:///D:/figcraft/test-output/agroniaga-tbs-perumda-tuah-sekata.figcraft), [tokens.tailwind.css](file:///D:/figcraft/test-output/tokens.tailwind.css), [tokens.json](file:///D:/figcraft/test-output/tokens.json) | 399.987 B / 1.471 B / 29.391 B | Tersimpan (`dirty: false`) | Token `@theme static` (`53` baris) & Figma Variables JSON (`45` variabel) terverifikasi ada dan tidak dimodifikasi di M0. |
| **Kontrak Sebelumnya (`contracts/`)** | Tidak ada saat discovery | — | Belum dibuat | Folder `contracts/`, `docs/m0/`, dan `docs/adr/` belum ada sebelum eksekusi M0; dibuat baru dari nol sesuai baseline V1.1. |

> **Catatan Infrastruktur Repo Saat Discovery:** Direktori awal repositori hanya berisi `.agents/`, `docs/`, `ouput/`, `task/`, dan `README.md`. Belum ada `backend/`, `frontend/`, `alembic/`, atau `infra/`.

---

## 2. Inventaris Modul Backend & Domain Kanonis (`TRD §7` & `DBD §2.2`)

Seluruh 8 modul PRD dipetakan secara konsisten ke **11 modul backend Modular Monolith** (+ `core/shared` infrastruktur untuk `idempotency_records`, `outbox_events`, `file_assets`, `system_rule_versions`, health probes `/health/live` & `/health/ready`):
1. `identity_access` (`user_accounts`, `roles`, `permissions`, `role_permissions`, `user_role_grants`, `user_access_scopes`, `auth_sessions`)
2. `public_portal` (`public_pages`, `public_notices` + agregasi baca publik `mills`, `perumda_offices`, `mill_price_quotes`, `disbun_reference_prices`)
3. `master_data` (`parties`, `farmers`, `farms`, `cooperatives`, `cooperative_memberships`, `mill_companies`, `mills`, `perumda_offices`, `vehicles`, `drivers`)
4. `pricing` (`price_sources`, `price_categories`, `mill_price_quotes`, `price_verification_events`, `disbun_reference_prices`)
5. `tbs_receiving` (`tbs_receipts`, `receipt_weighing_revisions`, `receipt_grading_items`)
6. `contracts` (`trade_contracts`, `contract_quota_periods`, `quota_reservations`)
7. `logistics` (`delivery_orders`, `delivery_order_lines`, `delivery_status_events`)
8. `mill_weighing` (`mill_weighing_tickets`, `mill_grading_items`)
9. `reconciliation` *(mencakup Finance subdomain sesuai TRD §7 & IPD)* (`reconciliation_cases`, `dispute_reviews`, `farmer_settlement_allocations`, `invoices`, `invoice_lines`, `payment_approvals`, `payment_records`)
10. `reporting` (query agregasi dashboard & ekspor laporan sesuai scope)
11. `audit` (`audit_events` append-only + pemantauan teknis CCTV Digital terpisah dari business audit)

*Catatan Penegasan Ruang Lingkup:* Unit Usaha Listrik & Gas secara eksplisit dikecualikan (`PRD §3.1`, `BSD §1.3`). Tidak ada transfer bank otomatis, kontrol fisik mesin jembatan timbang, ataupun pelacakan GPS armada real-time di Core MVP (`PRD §3.3`).

---

## 3. Temuan Kontradiksi, Kerancuan Lintas Dokumen, dan Resolusi Resmi

Setiap perbedaan di bawah dicatat lebih lanjut sebagai entri terkontrol dalam `docs/m0/M0_DECISION_REGISTER.md` tanpa mengubah keenam dokumen V1.1:

| Conflict ID | Lokasi Sumber | Perbedaan yang Ditemukan | Dampak terhadap Kontrak M0 | Resolusi Berdasarkan Hierarki Sumber (`IPD §3.2`) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CNF-01** | `PRD §4.1` vs `DBD §6.2` / `BSD §4.1` / `FigCraft D5` | PRD mencantumkan `ROLE-04 Staf Perumda` tunggal (`7` kode termasuk publik), sedangkan DBD/BSD/D5 memisahkan `PERUMDA_OPERATIONS` dan `PERUMDA_FINANCE` (`7` role login + `PUBLIC` anonim). | Penamaan enum role di `role-permissions.yaml` dan RBAC claims pada `/auth/me`. | Menggunakan **`PUBLIC` (anonymous, bukan baris akun DB)** + **7 peran login kanonis `DBD §6.2`**: `FARMER`, `COOPERATIVE_OPERATOR`, `PERUMDA_OPERATIONS`, `PERUMDA_FINANCE`, `MILL_OPERATOR`, `DIRECTOR`, `SYSTEM_ADMIN` beserta pemetaan ke `ROLE-01..07`. (`BSD` & `DBD` sebagai pemilik aturan kewenangan & skema peran). | `RESOLVED` |
| **CNF-02** | `AFD §29.1` vs `DBD §8.4` & `BSD §7.3` | AFD mencantumkan `EXPIRED` sebagai status harga, sementara DBD & BSD menetapkan status persisten adalah `DRAFT`, `PENDING_VERIFICATION`, `VERIFIED`, `REJECTED`, `PUBLISHED`, `REVOKED`, dan `EXPIRED` adalah status tampilan turunan dari `effective_until < NOW()`. | Skema status API `mill_price_quotes` & `state-catalog.yaml`. | Persisted state menggunakan **`DBD §8.4` (`DRAFT`, `PENDING_VERIFICATION`, `VERIFIED`, `REJECTED`, `PUBLISHED`, `REVOKED`)**, sedangkan API & UI mengekspos properti turunan **`display_status`** (`EXPIRED` bila periode berakhir) dan **`is_active`** (`BSD §7.3`). | `RESOLVED` |
| **CNF-03** | `AFD §31.2` / `BSD §22.4` vs `DBD §14.2` & `§14.5` | AFD §31.2 & BSD §22.4 menjelaskan alur pembayaran keluar (`PENDING_APPROVAL -> APPROVED -> AWAITING_PAYMENT -> PENDING_VERIFICATION -> PAID`), sementara `DBD §14.5` mendefinisikan `payment_records.status` sebagai (`DRAFT`, `PENDING_VERIFICATION`, `VERIFIED`, `REJECTED`, `REVERSED`) dan `payment_approvals` sebagai entitas persetujuan terpisah. | Desain endpoint `/invoices` & `/payments`, schema response, dan state machine keuangan. | Menggunakan mekanisme ganda yang dirujukkan sendiri oleh **`BSD §22.4` paragraf 2**: `invoices` punya status penerbitan + derived **`settlement_status`** (`UNPAID`, `PENDING_APPROVAL`, `APPROVED_UNPAID`, `AWAITING_PAYMENT`, `PENDING_VERIFICATION`, `PAID`); `payment_approvals` menyimpan siklus `PENDING -> APPROVED/REJECTED`; `payment_records` menyimpan siklus bukti `DRAFT -> PENDING_VERIFICATION -> VERIFIED/REJECTED/REVERSED`. Tidak ada `APPROVED` yang langsung dianggap `PAID` (`BR-PAY-010`). | `RESOLVED` |
| **CNF-04** | `TRD §15.4` vs `BSD §29.1` | `TRD §15.4` menetapkan format kode error `MODULE_CATEGORY_DESCRIPTION` (mis. `AUTH_INVALID_CREDENTIALS`, `MILL_DUPLICATE_TICKET`, `REC_WEIGHT_DISPUTE`), sementara tabel ilustratif `BSD §29.1` memakai nama pendek tanpa awalan modul (`PRICE_NOT_VERIFIED`, `QUOTA_EXCEEDED`, `INVALID_WEIGHT`). | Standar `error.code` di `error-catalog.yaml` & OpenAPI `ErrorResponse`. | Menetapkan konvensi kanonis **`TRD §15.4`** (`MODULE_CATEGORY_DESCRIPTION`: mis. `PRICE_NOT_VERIFIED`, `CONTRACT_QUOTA_EXCEEDED`, `TBS_INVALID_WEIGHT`, `MILL_DUPLICATE_TICKET`, `REC_WEIGHT_DISPUTE`) serta mencantumkan alias/mapping referensi ke `BSD §29.1` di `error-catalog.yaml`. | `RESOLVED` |
| **CNF-05** | `TRD §16.2` vs `IPD §7.1` & `AFD §8–9` (`FLOW-05`, `FLOW-06`) | `IPD §7.1` mencantumkan endpoint inti minimal (`/farmers`, `/farms`, `/cooperatives`, `/mills`, `/prices`, `/receipts`, `/contracts`, `/delivery-orders`, `/mill-tickets`, `/reconciliations`, `/invoices`, `/payments`, `/reports/*`), namun belum mencantumkan path rinci untuk `/public/disbun-prices`, `/vehicles`, `/drivers`, `/mill-companies`, `/audit-events`, `/admin/rule-versions`, `/admin/system-health`, atau `/reconciliations/{id}/allocations` yang tergambar di `DBD §4`, `AFD §36`, dan D5. | Cakupan path `openapi.v1.yaml` agar mendukung seluruh 26 rute `AFD §36` tanpa membuat endpoint fiktif. | `IPD §7.1` menyatakan *"Daftar tersebut adalah inventaris awal"*. M0 mempertahankan seluruh path baseline `IPD §7.1` dan melengkapi hanya endpoint resmi yang dibutuhkan PRD/AFD/DBD/D5, terkunci bersama di `openapi.v1.yaml` & `M0_REQUIREMENT_TRACEABILITY.md` *(usulan awal pada M0-A telah tervalidasi penuh sebagai `RESOLVED` di M0-C/M0.1)*. | `RESOLVED` |
| **CNF-06** | `TRD §25.1` (`/health/live`, `/health/ready`) vs D5 Admin `2576` (`/healthz`) | TRD menspesifikasikan `/health/live` dan `/health/ready`, sedangkan teks label UI ilustrasi pada FigCraft D5 (`2576`) menyinggung `/healthz`. | Path health probe pada kontrak & frontend admin metrics. | Mengunci **`/health/live`** dan **`/health/ready`** sebagai path kontrak resmi sesuai otoritas **`TRD §25.1`** dan mencatat `/healthz` di Admin UI hanya sebagai label deskriptif ringkas / alias non-wajib. | `RESOLVED` |
| **CNF-07** | `DEC-008` / `AFD §15.2` & `BSD §4.3` (Penerbit e-DO) | AFD menyebut Operator Koperasi atau Staf Perumda sebagai penerbit e-DO tergantung SOP yang disahkan (`AFD §41 #1`). | Policy permission `delivery_orders.issue` di `role-permissions.yaml`. | Kedua peran (`COOPERATIVE_OPERATOR` dalam `COOPERATIVE` scope & `PERUMDA_OPERATIONS` dalam `PERUMDA_GLOBAL` scope) didokumentasikan memiliki syarat kondisi SOP dengan flag `pending_sop_ref: DEC-008`, bukan hak sepihak tanpa pencatatan peran penerbit. | `PENDING_SOP` |
| **CNF-08** | `BSD §2.3` / `DBD §10.1` vs `BSD §22.5` (Principal/Agent & Pembayaran Parsial) | Model usaha `PRINCIPAL`/`AGENT`/`UNCONFIRMED` belum disahkan resmi oleh Perumda; pembayaran parsial berstatus di luar baseline wajib MVP (`DEC-010`, `BSD-DEC-017`). | Finalisasi invoice/settlement & validasi `payment_records` nominal < `total_amount`. | Kontrak OpenAPI menyertakan `business_model_code` wajib dengan guard penolakan transaksi keuangan nyata apabila `UNCONFIRMED` (`409` / `POLICY_UNCONFIRMED`), dan pembayaran parsial ditolak eksplisit (`422 PAY_PARTIAL_NOT_SUPPORTED`) di baseline MVP sampai SOP mengesahkan. | `PENDING_SOP` |
| **CNF-09** | `BSD §15.4` (`RETURNED`/`REJECTED` muatan ditolak PKS) vs `AFD §16.2` | AFD §16.2 menetapkan status pengiriman `DRAFT..COMPLETED, CANCELLED`, sedangkan BSD §15.4 menyebut status tambahan `RETURNED` atau `REJECTED` baru dapat ditambahkan jika disahkan pada AFD & DBD. | Enum `delivery_orders.status` dan `state-catalog.yaml`. | Baseline MVP M0 menjaga enum resmi AFD/DBD (`DRAFT`, `READY`, `IN_TRANSIT`, `ARRIVED`, `RECEIVED`, `COMPLETED`, `CANCELLED`) sambil mendokumentasikan `delivery_status_events.metadata` & flag pengecualian penolakan muatan PKS (`BSD-DEC-010` `PENDING_SOP`). | `PENDING_SOP` |
| **CNF-10** | `AFD §36` (`26` routes) vs tabel UI/Admin & Koperasi | `AFD §36` punya `/app/perumda/pks` ditambahkan di D5 (`2741`, `FLOW-06`), sementara `FLOW-05` CRUD Petani & Kebun disiapkan di Page 7 (`2641`) di bawah `/app/koperasi`. | Route-to-API traceability UI. | Seluruh **26 rute kanonis `AFD §36` + sub-modul/modal D5 (`FLOW-05` & `/app/perumda/pks` `FLOW-06`)** terpetakan lengkap di `M0_REQUIREMENT_TRACEABILITY.md` dengan dependensi API masing-masing. | `RESOLVED` |

---

## 4. Ringkasan Parameter & Keputusan SOP Belum Final (`AFD §41`, `BSD §35`, `PRD §27`)

Empat klasifikasi resmi dipakai seragam di seluruh artefak M0 (`task2.md §20`):
- **`CONFIRMED`:** Aturan yang ditegaskan sebagai baseline arsitektur/sistem (mis. `Netto = Bruto - Tara`, larangan `Tara > Bruto`, `1` tiket current per e-DO di MVP `BSD §16.4`, larangan auto-bank-transfer, `BR-SYS-002`, `BR-PAY-010`).
- **`SIMULATION_ONLY`:** Nilai uji & demo yang **dilarang** dianggap SOP resmi (`toleransi 1,5000%` `BR-REC-003`, contoh potongan grading `2,0000%` `BSD §9.3`, pembagian proporsional multi-petani `BSD §20.3`, kontrak `PRINCIPAL`/`AGENT` contoh dalam fixtures).
- **`PENDING_SOP`:** Keputusan organisasi yang wajib disahkan Perumda sebelum transaksi keuangan/operasional nyata (`BSD-DEC-001..020`, `AFD §41 #1..15` — khususnya model bisnis principal/agent, dasar kuota origin vs mill, batas kewenangan approval Direksi, retensi audit/idempotency, SLA dispute, mekanisme penolakan muatan di PKS, jalur bukti terima dana ke petani).
- **`FUTURE`:** Di luar ruang lingkup Core MVP (`pembayaran parsial/termin`, `API integrasi timbangan/PKS otomatis`, `live GPS armada`, `prediksi AI`, `auto bank transfer`, `penjualan Listrik & Gas`).

---

## 5. Kesesuaian Lingkup Keamanan & Kesiapan Alat Validasi

- **Lingkungan Pengujian Kontrak M0:** Python `3.12.0`, `PyYAML 6.0.2`, `jsonschema 4.23.0`, `Pydantic 2.13.0`, Node.js `v24.21.0` / `npm 11.9.0`. Seluruh pengujian validasi kontrak dijalankan **offline/deterministik tanpa FastAPI server, React dev server, PostgreSQL, atau Redis**.
- **Kesimpulan Fase M0-A:** Seluruh 6 dokumen V1.1, D4/D5 FigCraft sign-off, design tokens, dan perbedaan lintasan dokumen telah teraudit tuntas tanpa modifikasi sumber V1.1 maupun kode aplikasi. Siap menyusun `M0-B` hingga `M0-H`.
