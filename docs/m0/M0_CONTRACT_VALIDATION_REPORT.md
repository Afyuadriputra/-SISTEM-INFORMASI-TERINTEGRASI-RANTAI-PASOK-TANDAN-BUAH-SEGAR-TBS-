# M0 Contract Validation Report (`M0-H`)

**Milestone:** `M0 — Requirements & Contract Alignment`  
**Tanggal Verifikasi:** 2026-11-10  
**Keputusan Kesiapan Kontrak:** `PASS (0 Issues across K1–K11)`

---

## 1. Perintah, Versi Perkakas, & Ruang Lingkup Eksekusi

Pengujian dijalankan **sepenuhnya secara offline dan deterministik** di direktori kerja repositori tanpa menjalankan server backend FastAPI, database PostgreSQL, Redis, atau frontend build runtime:

- **Perintah Validator Utama:** `python contracts/scripts/validate_contracts.py`
- **Perintah Test Suite `unittest`:** `python -m unittest discover -s contracts/tests -v`
- **Perintah Typegen Frontend (`K8`):** `npx --yes openapi-typescript contracts/openapi.v1.yaml -o <tmpdir>/openapi-types.d.ts`
- **Versi Runtime & Library Terverifikasi:**
  - `Python 3.12.0`
  - `PyYAML 6.0.2`
  - `jsonschema 4.23.0` (`Draft202012Validator` + `FormatChecker`)
  - `pydantic 2.13.0`
  - `openapi-pydantic 0.5.1`
  - `Node.js v24.21.0` / `npm 11.9.0` / `openapi-typescript v7.13.0`

---

## 2. Ringkasan Metrik Kontrak Tervalidasi

| Artefak Kontrak | Jumlah / Metrik Terukur |
| :--- | :--- |
| `contracts/openapi.v1.yaml` | OpenAPI `3.1.0`, **`75` paths**, **`95` operations** (`2` health + `7` public + `4` auth [`2` unauthenticated, `2` authenticated] + `82` internal = `11` unauthenticated & `84` authenticated), **`191` schemas**, **`8` operasi `Idempotency-Key`** |
| `contracts/error-catalog.yaml` | **`69` kode error** unik berformat `MODULE_CATEGORY_DESCRIPTION` (`1:1` dengan `ErrorCode` enum OpenAPI) |
| `contracts/state-catalog.yaml` | **`11` state machine persisten** (`SM-01`..`SM-11`), **`41` transisi**, pemisahan `derived_states` & flag `PENDING_SOP` |
| `contracts/role-permissions.yaml` | `PUBLIC` + `7` peran DB (`8` role_grants), **`64` permissions**, **`95` baris `operation_access_matrix`** (`1:1` OpenAPI, termasuk `8` operasi idempoten) |
| `contracts/fixtures/*.json` | **`11` berkas fixture domain & aktor**, termasuk **`22` skenario negatif** (`error-scenarios.json`) |
| Tabel & Konsistensi Dokumen M0.1 | **`48/48` nama tabel kanonis `DBD §4`** terindeks di `M0_REQUIREMENT_TRACEABILITY.md`, **`0` legacy table alias**, `TanStack Router` konsisten di ADR & handoff, `M0-CNF-05` seragam **`RESOLVED`** |

---

## 3. Hasil Eksekusi Uji Validasi `K1`–`K11`

| Kode Check | Tujuan Verifikasi | Status | Temuan Terbuka | Catatan / Bukti Teknis |
| :--- | :--- | :---: | :---: | :--- |
| **K1** | Parsing sintaks & deteksi duplicate mapping keys (`UniqueKeySafeLoader` YAML + `_reject_duplicate_json_keys` JSON) | `PASS` | `0` | Seluruh 4 berkas `.yaml` dan 11 berkas `.json` valid tanpa kunci ganda. |
| **K2** | Validasi OpenAPI `3.1.0` via `openapi_pydantic.OpenAPI`, resolusi seluruh local `$ref`, parameter path (`required: true`), `operationId` unik (`95`), security schemes | `PASS` | `0` | Menangkap & menutup celah definisi schema `AuthenticatedUser`, `Mill`, `InternalPriceQuote`, dan dereference parameter path. |
| **K3** | Konsistensi `error-catalog.yaml` (penamaan `TRD §15.4`, HTTP status valid termasuk `503`/`504`, `retryable` boolean, pesan aman, kesesuaian `1:1` OpenAPI `ErrorCode`, referensi di `state-catalog.yaml` & `error-scenarios.json`) | `PASS` | `0` | `69/69` kode error sinkron sempurna antara katalog, OpenAPI enum, mesin state, dan 22 skenario error. |
| **K4** | Konsistensi `state-catalog.yaml` (`SM-01..11`, initial/terminal states dalam `persisted_states`, disjungsi `derived_states`, validitas `api_operation_id` & `required_permission`, sinkronisasi 9 enum status OpenAPI) | `PASS` | `0` | Status persisten terpisah tegas dari `EXPIRED` & `settlement_status`, menjaga larangan `APPROVED == PAID`. |
| **K5** | Matriks `role-permissions.yaml` (bijeksi `1:1` 95 operasi OpenAPI, pemisahan endpoint publik vs auth+CSRF wajib pada mutasi internal, aturan `BR-SYS-002` `SYSTEM_ADMIN` non-approver) | `PASS` | `0` | `95/95` operasi dipetakan; `SYSTEM_ADMIN` tidak memegang izin verifikasi/persetujuan transaksi atau keuangan. |
| **K6** | Validasi seluruh entitas di 11 berkas JSON fixture terhadap JSON Schema Draft 2020-12 OpenAPI (`additionalProperties: false`), integritas FK lintas berkas, aritmetika timbangan/kuota/rekonsiliasi/faktur, 22 skenario negatif, & kebersihan secret/PII | `PASS` | `0` | Ditemukan & ditutup selama M0: kunci note liar pada DTO fixture, selisih `permissions` 2 akun checker di `actors.json`, dan relasi FK kasus rekonsiliasi historis (`0103`, `0104`). |
| **K7** | Kelengkapan `M0_REQUIREMENT_TRACEABILITY.md` mencakup 56 `PRD FR-*`, 20 `NFR-*`, 24 `FLOW-01..24`, 26 rute `AFD §36`, 30 `BIZ-001..030`, & 95 `operationId` | `PASS` | `0` | Seluruh kode kebutuhan, alur, rute, aturan uji bisnis, dan operasi OpenAPI tercatat eksplist. |
| **K8** | Kesiapan codegen TypeScript frontend menggunakan `npx openapi-typescript` ke direktori sementara sistem | `PASS` | `0` | Keluaran `.d.ts` tervalidasi menghasilkan `paths`, `components`, `PublicPriceQuote`, `ReconciliationCase`, `ErrorResponse` dengan `exit code 0` tanpa menyisakan artefak build di workspace. |
| **K9** | Kesiapan implementasi backend: seluruh field kuantitas/harga/uang/persentase/luas/koordinat bertipe string terpola regex (tanpa `float` IEEE-754), probe `/health/live` & `/health/ready`, penanda `Pending SOP` | `PASS` | `0` | 8 schema desimal presisi tervalidasi regex ketat; kebijakan `UNCONFIRMED` & `SIMULATION_ONLY` terisolasi. |
| **K10** | Penjaga ruang lingkup & kebersihan repo (`backend/`, `frontend/`, `alembic/`, `infra/` tidak dibuat/disentuh; baseline V1.1 & FigCraft tidak diubah) | `PASS` | `0` | Perubahan tracked git sebelum penutupan hanya berkas yang diizinkan oleh M0/M0.1. |
| **K11** | Audit konsistensi Handoff M0.1 (`48/48` tabel `DBD §4`, bebas alias non-kanonis, `TanStack Router`, breakdown `95` operasi [`11`/`84`], `8` operasi idempoten 1:1, & `M0-CNF-05 = RESOLVED`) | `PASS` | `0` | Menjamin paritas penuh lintas `docs/m0/`, `docs/adr/`, checkpoint, dan kontrak YAML. |

---

## 4. Masalah yang Ditemukan & Ditutup Selama Validasi Kontrak

Selama eksekusi `K1–K11`, suite validasi secara aktif mendeteksi inkonsistensi nyata sebelum diserahkan ke Backend/Frontend:
1. **Sintaks YAML `role-permissions.yaml` (`line 422`):** Parameter path `{id}` dalam flow mapping tanpa tanda kutip menyebabkan parser error — ditutup dengan pengutipan `"..."` pada seluruh `path` matriks (`95/95`).
2. **Ketidakcocokan Schema OpenAPI vs Fixture (`additionalProperties: false`):**
   - Menambahkan `linked_party_id` (`NullableUuid`) pada `AuthenticatedUser`, `has_verified_coordinates` pada `Mill`, serta metadata tampilan non-N+1 (`mill_code`, `regency`, `price_category_*`, `unit`, `source_*`, `is_simulation`) pada `InternalPriceQuote`.
   - Menghapus properti penjelasan non-DTO (`*_note`) dari entitas fixture dan menambahkan `created_at` pada `mill_price_quotes`.
3. **Drift Hak Akses & Foreign Key Fixture:**
   - Menyamakan array `permissions` akun `sim_perumda_ops_02` dan `sim_perumda_fin_02` pada `actors.json` terhadap `role_grants` di `role-permissions.yaml`.
   - Menambahkan 2 catatan e-DO & 2 tiket timbang PKS historis (`0098`, `0099`) sehingga kasus rekonsiliasi historis (`0103` `DISPUTE_HOLD`, `0104` `UNDER_REVIEW`) memiliki FK lintas berkas yang valid 100%, serta memperkaya `error-scenarios.json` dari 19 menjadi **22 skenario negatif**.
4. **Penelusuran Persyaratan `K7`:** Memastikan seluruh kode individu `FR-*`, `NFR-001..020`, `FLOW-01..24`, 26 rute kanonis `AFD §36` (`/harga-tbs`, `/lokasi-pks`, `/app/petani/panen`, `/app/koperasi/surat-jalan`, dll.), dan `BIZ-001..030` tercantum eksplisit 1:1.
5. **Audit Konsistensi Handoff M0.1 (`K11` di `validate_contracts.py`):**
   - Menyelaraskan seluruh 48 nama tabel kanonis `DBD §4` di `M0_REQUIREMENT_TRACEABILITY.md` (`user_accounts`, `user_role_grants`, `receipt_weighing_revisions`, `delivery_order_lines`, `delivery_status_events`, dll.) serta memblokir otomatis alias tabel non-kanonis pada seluruh dokumen & kontrak.
   - Memverifikasi hitungan operasi OpenAPI (`2` health + `7` public + `2` unauth bootstrap + `2` auth authenticated + `82` internal = `95`), keselarasan **`8` operasi wajib `Idempotency-Key`**, konsistensi **TanStack Router** (`TRD §17`/`ADR-006`/`M0_HANDOFF.md`), dan status `M0-CNF-05 = RESOLVED` across Audit, Decision Register, & Changelog.

---

## 5. Catatan & Peringatan Non-Blocking

- **Lingkungan Windows CRLF:** Git menampilkan peringatan standar `LF will be replaced by CRLF` pada `docs/IMPLEMENTATION_CHECKPOINTS.md`; integritas konten bersih (`git diff --check` tanpa error whitespace).
- **Keterbatasan Status Bisnis:** Kelulusan M0 memverifikasi konsistensi kontrak teknis dan isolasi kebijakan, namun transaksi settlement/keuangan nyata (`business_model_code = UNCONFIRMED`, ambang batas toleransi 1,5%, alokasi multi-petani) tetap berstatus `PENDING_SOP` / `SIMULATION_ONLY` hingga keputusan resmi Perumda Tuah Sekata.
