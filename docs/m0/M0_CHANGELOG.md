# M0 Change Log & Contract Change Management

**Milestone:** `M0 — Requirements & Contract Alignment`  
**Tanggal:** 2026-11-10  
**Git Baseline:** `main @ b081695`

---

## 1. Daftar Perubahan File pada Milestone M0

> Seluruh 6 dokumen spesifikasi V1.1 (`PRD.md`, `TRD.md`, `AFD.md`, `DBD.md`, `BSD.md`, `IPD.md`), berkas `.figcraft`, design tokens asli (`D:\figcraft\test-output\tokens.*`), serta direktori aplikasi (`backend/`, `frontend/`, `alembic/`, `infra/`) **tidak diubah atau dibuat** selama M0.

### A. Kontrak Mesin Kanonis (`contracts/`)
| Berkas | Aksi | Tujuan Perubahan | Dampak Kompatibilitas |
| :--- | :--- | :--- | :--- |
| `contracts/openapi.v1.yaml` | Dibuat baru (+ penyesuaian skema DTO `K2`/`K6`) | Spesifikasi API kanonis OpenAPI `3.1.0` (`75` paths, `95` operations, `191` schemas, envelope & presisi desimal string). | Sumber tunggal generasi tipe TypeScript frontend (`F0+`) dan skema Pydantic FastAPI (`B0+`). |
| `contracts/error-catalog.yaml` | Dibuat baru | Katalog `69` kode error kanonis (`MODULE_CATEGORY_DESCRIPTION`), pemetaan alias `BSD §29.1`, HTTP status, `retryable`, dan pesan aman. | Mengikat pesan error seragam backend <-> frontend <-> CCTV Digital Admin. |
| `contracts/state-catalog.yaml` | Dibuat baru | Definisi formal `11` state machine (`SM-01..11`), `41` transisi, pemisahan state persisten vs turunan vs UI, dan penanda `PENDING_SOP`. | Mencegah pencampuran status `EXPIRED` atau `APPROVED == PAID`. |
| `contracts/role-permissions.yaml` | Dibuat baru (+ perbaikan quoting path YAML) | Definisi `PUBLIC` + `7` peran DB, `4` scope, `6` aturan Separation of Duties, `64` permission, serta matriks `1:1` atas seluruh `95` operasi API. | Mengunci otorisasi fail-closed di server & sinkronisasi guard menu UI (`BR-SYS-002`). |

### B. Fixtures & Suite Validasi Deterministik (`contracts/fixtures/`, `contracts/scripts/`, `contracts/tests/`)
| Berkas | Aksi | Tujuan Perubahan | Dampak Kompatibilitas |
| :--- | :--- | :--- | :--- |
| `contracts/fixtures/README.md` | Dibuat baru | Panduan struktur, konvensi UUID deterministik, penanda `SIMULATION_ONLY`, dan larangan PII/secret nyata. | Acuan bersama seed test backend & MSW mock handlers frontend. |
| `contracts/fixtures/actors.json` | Dibuat baru | Aktor `PUBLIC`, 12 akun uji tiap peran & scope (+ maker/checker kedua yang disinkronkan 1:1 ke `role_grants`), & 9 `parties`. | Memungkinkan pengujian RBAC, scope, & `SOD-01..06`. |
| `contracts/fixtures/public-prices.json` | Dibuat baru | Sumber harga, kategori Swadaya vs Plasma non-comparable, 6 kutipan harga multi-status (`EXPIRED`, `DRAFT`, dll.), Disbun, & respons kosong. | Menjamin kesetaraan tabel perbandingan Portal Publik (`I0`). |
| `contracts/fixtures/mills.json` | Dibuat baru | 2 perusahaan induk, 3 PKS (`is_public=true/false`, koordinat null/terverifikasi), `public_profile` (eksklusi Listrik/Gas), & pengumuman publik. | Menjamin privasi data Portal Publik & form `FLOW-06`. |
| `contracts/fixtures/master-data.json` | Dibuat baru | 2 koperasi, 5 petani, 3 kebun (koordinat valid vs null, nomor STDB), 2 kendaraan, & 1 sopir simulasi. | Sumber uji `FLOW-05`, isolasi antar koperasi & petani. |
| `contracts/fixtures/tbs-receipts.json` | Dibuat baru | 5 penerimaan TBS (`DRAFT`, `VALIDATED`, `SHIPPED` multi-petani `3000/2000/5000 = 10000 kg`, revisi tara, simulasi grading `2%`). | Menguji rumus `Bruto - Tara = Netto` dan penguncian alokasi. |
| `contracts/fixtures/contracts-quota.json` | Dibuat baru | 3 kontrak (`ACTIVE`, kedaluwarsa, `UNCONFIRMED`), kuota periode, 2 reservasi, dan kasus uji paralel over-quota. | Menguji pencegahan transaksi tanpa kuota & konflik konkurensi. |
| `contracts/fixtures/delivery-orders.json` | Dibuat baru | 5 e-DO lintas status (`DRAFT`, `IN_TRANSIT`, `RECEIVED` aktif & historis, token QR, `gps_tracking_supported=false`). | Menguji alur logistik koperasi-Perumda-PKS tanpa kebocoran antar-PKS. |
| `contracts/fixtures/mill-tickets.json` | Dibuat baru | 4 tiket PKS (`VERIFIED` revisi ke-2 `9900.000 kg`, revisi v1 `DRAFT`, serta tiket historis `0098` & `0099`). | Menguji revisi berversi dan integritas bukti slip jembatan timbang. |
| `contracts/fixtures/reconciliations.json` | Dibuat baru | 3 `system_rule_versions` (`1,5%` simulasi, model usaha `UNCONFIRMED`, alokasi proporsional) & 4 kasus rekonsiliasi (`MATCHED`, `WAITING_TICKET`, `DISPUTE_HOLD`, selisih negatif `UNDER_REVIEW`). | Menguji ketiadaan selisih pembulatan pada `farmer_allocations` & guard selisih negatif. |
| `contracts/fixtures/invoices-payments.json` | Dibuat baru | 3 `file_assets`, faktur `AR` terbayar penuh vs faktur `AP` masih `AWAITING_PAYMENT` (`BIZ-027` / `BR-PAY-010`), dan faktur `DRAFT` berstatus `UNCONFIRMED`. | Memverifikasi isolasi AR vs AP & blokir `FIN_POLICY_UNCONFIRMED`. |
| `contracts/fixtures/error-scenarios.json` | Dibuat baru | `22` skenario negatif (`NEG-01`..`NEG-22`) berstruktur `ErrorResponse` untuk auth, CSRF, RBAC, scope, kuota, idempotency, dispute, partial pay, optimistic lock, & 503/504. | Memastikan penanganan error konsisten di backend middleware & UI error banners. |
| `contracts/scripts/validate_contracts.py` | Dibuat baru | Validator deterministik `K1–K10` tanpa server (YAML duplicate keys, `openapi_pydantic`, `Draft202012Validator`, FK & aritmetika, `openapi-typescript`). | Gerbang otomatis anti-drift sebelum pekerjaan `B0+` / `F0+`. |
| `contracts/tests/test_contracts.py` | Dibuat baru | Suite `unittest` yang membungkus `K1–K10` agar dapat dijalankan lewat test runner standar Python. | Regresi kontrak terotomasi (`10` unit test case). |

### C. Dokumentasi Audit, ADR, Penelusuran, & Checkpoint (`docs/m0/`, `docs/adr/`, `docs/IMPLEMENTATION_CHECKPOINTS.md`)
| Berkas | Aksi | Tujuan Perubahan |
| :--- | :--- | :--- |
| `docs/m0/M0_DOCUMENT_AUDIT.md` | Dibuat baru | Inventaris baseline 6 dokumen V1.1 + D4/D5 FigCraft, 11 modul backend, serta katalog 10 temuan konflik `CNF-01..CNF-10`. |
| `docs/m0/M0_DECISION_REGISTER.md` | Dibuat baru | Keputusan terkontrol `M0-CNF-01..10`, `M0-TECH-01..13`, dan tracking status SOP `SOP-01..15`. |
| `docs/m0/M0_REQUIREMENT_TRACEABILITY.md` | Dibuat baru | Matriks ujung-ke-ujung (`56` FR + `20` NFR + `24` FLOW + `26` rute `AFD §36` + `30` BIZ + `95` `operationId` -> IPD `B0..B11`/`F0..F11`). |
| `docs/m0/M0_CONTRACT_VALIDATION_REPORT.md` | Dibuat baru | Bukti eksekusi perintah, versi tool, metrik kontrak, hasil `K1–K10`, serta daftar temuan yang telah ditutup. |
| `docs/m0/M0_CHANGELOG.md` | Dibuat baru | Catatan perubahan berkas M0 & prosedur Tata Kelola Perubahan Kontrak. |
| `docs/m0/M0_HANDOFF.md` | Dibuat baru | Panduan eksekusi track paralel Backend (`B0–B11`) dan Frontend (`F0–F11`). |
| `docs/adr/README.md` + `ADR-001`..`ADR-010` | Dibuat baru | 10 Architecture Decision Records mengunci batasan arsitektur utama tanpa menyentuh dokumen baseline. |
| `docs/IMPLEMENTATION_CHECKPOINTS.md` | Diperbarui | Memperbarui status M0 menjadi `READY — M0_CONTRACT_ALIGNMENT_VERIFIED` (`M0-A..M0-I` `PASS`) sambil menjaga riwayat D4 & D5 utuh. |

### D. M0.1 Final Handoff Consistency Patch (`2026-11-10`)
Perbaikan terbatas pasca-audit sebelum implementasi `B0` dan `F0` tanpa mengubah dokumen V1.1, kontrak kanonis OpenAPI/YAML, maupun folder runtime:
1. **Frontend Router (`A`):** `docs/m0/M0_HANDOFF.md` dan `docs/IMPLEMENTATION_CHECKPOINTS.md` diselaraskan ke **`TanStack Router`** sesuai `TRD §3, §17` dan `ADR-006` (menghapus rujukan library router yang keliru sebelumnya).
2. **48 Tabel Kanonis DBD (`B`):** `docs/m0/M0_REQUIREMENT_TRACEABILITY.md` mengoreksi `user_accounts`, `user_role_grants`, `receipt_weighing_revisions`, `delivery_order_lines`, `delivery_status_events` serta mengindeks seluruh 48 tabel kanonis `DBD §4` berdasarkan tahapan `DBD §4.11`.
3. **Hitungan Operasi OpenAPI (`C`):** `docs/m0/M0_HANDOFF.md` & `M0_CONTRACT_VALIDATION_REPORT.md` dikoreksi dari keliru `91` ke rincian aktual **`95` total (`2` health + `7` public + `2` auth bootstrap + `2` auth session + `82` internal bisnis/admin = `11` unauthenticated & `84` authenticated)**.
4. **Idempotency Operations (`D`):** `ADR-010`, `M0_DECISION_REGISTER.md` (`M0-TECH-07`), `M0_REQUIREMENT_TRACEABILITY.md`, dan `M0_HANDOFF.md` diselaraskan dari keliru `7` menjadi **`8` operasi mutasi wajib `Idempotency-Key`** (mewakili 7 kategori proses kritis `BSD §27.2`, menambahkan operasi ke-8 `createOrTriggerReconciliation` di samping `calculateReconciliation` sesuai `openapi.v1.yaml` & `role-permissions.yaml`).
5. **Konsistensi Decision Register (`E`):** `M0-CNF-05` pada `M0_DOCUMENT_AUDIT.md`, `M0_DECISION_REGISTER.md`, dan `M0_CHANGELOG.md` diseragamkan ke status akhir **`RESOLVED`** (menutup status awal M0-A yang sempat tertinggal).
6. **Clean Architecture & Struktur Solo Developer (`F` & `G`):** `ADR-001`, `ADR-002`, `M0_HANDOFF.md`, dan `IMPLEMENTATION_CHECKPOINTS.md` menegaskan bahwa `B0` hanya membangun fondasi `main.py` & `core/` tanpa membuat puluhan folder modul/subfolder kosong (`TRD §5.1, §6`), modul ditambah inkremental per milestone IPD (`B1–B10`) dengan 4 layer (`domain` bebas `infrastructure`, `application` memakai port, `infrastructure` mengimplementasi port, `presentation` memanggil `application`, composition root wiring), serta PostgreSQL/Redis/performance/security/testing tetap wajib.
7. **Pencegahan Regresi Otomatis (`K11 / validate_contracts.py`):** Menambahkan pemeriksaan silang otomatis di `contracts/scripts/validate_contracts.py` dan `contracts/tests/test_contracts.py`.

---

## 2. Keterbatasan Diketahui (Known Limitations & Scope Guard)

1. **Aturan Bisnis `PENDING_SOP` / `SIMULATION_ONLY`:** Nilai toleransi (`1.5000%`), grading (`2.0000%`), formula alokasi multi-petani proporsional, serta penetapan resmi model usaha (`PRINCIPAL`/`AGENT`) masih berstatus belum final secara organisasional dan diproteksi oleh error guard eksplisit pada kontrak (`FIN_POLICY_UNCONFIRMED`, `REC_ALLOCATION_POLICY_UNCONFIRMED`).
2. **Validasi Dinamis Server Belum Ada di M0:** Validasi M0 bersifat *static & schema-level* (`K1–K11`). Pengujian konkurensi row-level lock PostgreSQL nyata (`SELECT FOR UPDATE`), Cookie `HttpOnly` lewat browser/proxy, serta benchmark P95 dijalankan mulai milestone `B1–B11`, `F0–F11`, dan `I0–I4`.

---

## 3. Prosedur Perubahan Kontrak (`Contract Change Management` per `IPD §46`)

Apabila selama `B0–B11` atau `F0–F11` ditemukan kebutuhan penyesuaian endpoint, field, enum, atau kode error:
1. **Dilarang Mengubah Sepihak:** Backend maupun frontend dilarang menyimpang diam-diam dari `contracts/openapi.v1.yaml` atau katalog kontrak.
2. **Pembaruan Berkas Tunggal + Register:** Ajukan perubahan pada `contracts/openapi.v1.yaml` (serta `error-catalog.yaml`, `state-catalog.yaml`, `role-permissions.yaml`, dan `contracts/fixtures/*.json` yang relevan) disertai catatan perubahan pada `M0_DECISION_REGISTER.md` atau `M0_CHANGELOG.md`.
3. **Verifikasi Ulang Gerbang `K1–K11`:** Jalankan `python contracts/scripts/validate_contracts.py` dan `python -m unittest discover -s contracts/tests -v` hingga seluruh pemeriksaan kembali `PASS (0 issues)`.
4. **Sinkronisasi Konsumen:** Regenerasi tipe TypeScript (`npx openapi-typescript`) untuk Frontend (`F0+`) dan perbarui skema Pydantic / handler MSW sebelum merge integrasi.
