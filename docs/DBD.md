
# DATABASE DESIGN DOCUMENT (DBD)

## SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TANDAN BUAH SEGAR (TBS)

### PERUMDA TUAH SEKATA — UNIT AGRO NIAGA

**Versi:** 1.1 — Database & UX Data Architecture Baseline
**Tanggal:** 10 November 2026
**Status:** Draft Rancangan Database dan Pendukung UI/UX
**Dokumen Induk:** PRD V1.1, TRD V1.1, AFD V1.1
**Database:** PostgreSQL 17+
**ORM:** SQLAlchemy 2.x
**Migration:** Alembic
**Caching:** Redis
**Backend Architecture:** Modular Monolith — Clean Architecture 4 Layer
**Frontend Architecture:** Atomic Design — 5 Levels
**UX Principles:** 25 Prinsip UX Terpilih, Golden Ratio, dan Micro-interactions

---

# BAGIAN I — DATABASE ARCHITECTURE

# 1. PENDAHULUAN

## 1.1 Tujuan Dokumen

Database Design Document (DBD) menjelaskan rancangan penyimpanan, pengolahan, penghubungan, perlindungan, dan pengambilan data yang digunakan oleh Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata.

Dokumen ini bertujuan untuk:

1. Menetapkan arsitektur database utama.
2. Memetakan kepemilikan data berdasarkan modul bisnis.
3. Mendefinisikan entitas dan hubungan antarentitas.
4. Menentukan tipe data dan batasan integritas.
5. Menghindari duplikasi dan inkonsistensi.
6. Mendukung transaksi bisnis yang aman dan atomik.
7. Menentukan strategi penyimpanan riwayat perubahan.
8. Mendukung rekonsiliasi penimbangan yang dapat diaudit.
9. Mendukung pengelolaan harga TBS multi-PKS.
10. Mendukung pelaporan keuangan dan transaksi.
11. Mengoptimalkan performa query dan akses database.
12. Menentukan strategi indexing, caching, dan migration.
13. Menentukan pengamanan informasi pribadi dan keuangan.
14. Mendukung kebutuhan antarmuka pengguna dan interaksi yang responsif.
15. Menjadi baseline implementasi database dan pengujian.

## 1.2 Ruang Lingkup

Database mendukung dua lingkungan:

**Portal Publik**

- Informasi Perumda.
- Harga TBS multi-PKS.
- Harga acuan Disbun.
- Perbandingan harga.
- Lokasi perusahaan dan PKS.
- Informasi kemitraan.
- Konten publik.

**Portal Internal**

- Pengguna dan hak akses.
- Master data petani dan koperasi.
- Master data PKS.
- Penerimaan TBS.
- Penimbangan dan grading.
- Kontrak dan kuota.
- Pengiriman dan e-DO.
- Tiket timbang PKS.
- Rekonsiliasi.
- Faktur dan pembayaran.
- Dashboard.
- Audit dan monitoring operasional.

## 1.3 Prinsip Perancangan Database

Database harus menerapkan:

- Relational Data Modeling.
- Normalisasi hingga minimal 3NF untuk data operasional yang sesuai.
- Referential Integrity.
- Atomic Transaction.
- Consistent Data Types.
- Optimistic/Pessimistic Concurrency Control.
- Immutable Transaction History untuk data yang memerlukan histori.
- Controlled Data Access.
- Defense in Depth.
- Indexing berdasarkan pola query.
- Data Retention Policy.
- Backup dan Recovery.
- Schema Versioning.
- Performance Monitoring.

PostgreSQL menjadi sumber kebenaran utama.

Redis tidak menggantikan database transaksi.

---

# 2. ARSITEKTUR DATABASE

## 2.1 Pendekatan

Sistem menggunakan satu PostgreSQL database dalam arsitektur Modular Monolith.

Setiap modul memiliki kepemilikan logis terhadap tabel dan aturan pengelolaan datanya.

Pada baseline prototipe, seluruh tabel dapat berada dalam schema PostgreSQL `public`, dengan penamaan yang konsisten dan pemisahan repository di masing-masing modul.

Penggunaan schema PostgreSQL terpisah berdasarkan domain dapat dipertimbangkan kemudian apabila memberi manfaat operasional yang jelas.

## 2.2 Pembagian Kepemilikan Data

| Modul                      | Tanggung Jawab Data                                                 |
| -------------------------- | ------------------------------------------------------------------- |
| identity_access            | Akun, peran, permission, session                                    |
| public_portal              | Konten dan informasi publik                                         |
| master_data                | Petani, kebun, koperasi, PKS, kendaraan, sopir                      |
| pricing                    | Harga Disbun, harga PKS, riwayat dan verifikasi                     |
| tbs_receiving              | Penerimaan TBS, timbangan asal, grading                             |
| contracts                  | Kontrak, kuota, reservasi                                           |
| logistics                  | e-DO, detail muatan, status pengiriman                              |
| mill_weighing              | Tiket timbang PKS dan grading pabrik                                |
| reconciliation             | Rekonsiliasi, dispute, perhitungan penyelesaian, faktur, pembayaran |
| reporting                  | Query agregasi dan data laporan                                     |
| audit                      | Audit aktivitas bisnis                                              |
| core/shared infrastructure | Idempotency, file metadata, outbox, konfigurasi teknis              |

## 2.3 Aturan Kepemilikan

- Setiap tabel memiliki satu modul penanggung jawab.
- Modul lain dapat membaca data melalui kontrak aplikasi yang disetujui.
- Perubahan data hanya dilakukan melalui use case pemilik domain.
- Foreign key lintas modul diperbolehkan untuk menjaga integritas.
- Foreign key tidak berarti modul boleh bebas mengubah tabel modul lain.
- Operasi lintas modul yang perlu atomik dikoordinasikan melalui Application Layer.
- Tidak dibuat database per modul pada tahap tesis.
- Perubahan struktur database dilakukan melalui Alembic.

---

# 3. STANDAR PENAMAAN DAN TIPE DATA

## 3.1 Naming Convention

Ketentuan:

- Nama tabel menggunakan `snake_case` bentuk jamak.
- Nama kolom menggunakan `snake_case`.
- Primary key menggunakan `id`.
- Foreign key menggunakan pola `{entity}_id`.
- Unique constraint menggunakan awalan `uq_`.
- Foreign key constraint menggunakan `fk_`.
- Check constraint menggunakan `ck_`.
- Index menggunakan `ix_`.
- Partial unique index menggunakan `ux_`.

Contoh:

- `tbs_receipts`
- `delivery_orders`
- `mill_weighing_tickets`
- `reconciliation_cases`
- `payment_records`

## 3.2 Primary Key

Primary key menggunakan UUID.

UUID dapat dihasilkan melalui PostgreSQL `gen_random_uuid()` atau generator UUID yang sesuai pada Application Layer.

Baseline tidak mewajibkan UUIDv7.

UUID internal tidak digunakan sebagai satu-satunya bukti otorisasi.

## 3.3 Standar Tipe Data

| Data               | PostgreSQL Type |
| ------------------ | --------------- |
| Primary Key        | UUID            |
| Foreign Key        | UUID            |
| Nama               | VARCHAR / TEXT  |
| Kode bisnis        | VARCHAR         |
| Status             | VARCHAR + CHECK |
| Boolean            | BOOLEAN         |
| Tanggal            | DATE            |
| Waktu kejadian     | TIMESTAMPTZ     |
| Berat (kg)         | NUMERIC(14,3)   |
| Harga (Rp/kg)      | NUMERIC(18,2)   |
| Nominal uang       | NUMERIC(20,2)   |
| Persentase         | NUMERIC(9,4)    |
| Latitude           | NUMERIC(9,6)    |
| Longitude          | NUMERIC(9,6)    |
| Metadata fleksibel | JSONB           |
| Deskripsi panjang  | TEXT            |

Penetapan presisi aktual mengikuti kebutuhan transaksi yang divalidasi.

## 3.4 Aturan Nilai Numerik

Uang dan berat tidak boleh dihitung menggunakan floating point biner.

Backend menggunakan `Decimal`.

Database menggunakan `NUMERIC`.

Aturan pembulatan ditentukan oleh Business System Document (BSD).

Nilai bruto, tara, netto, potongan grading, berat dasar pembayaran, dan nilai transaksi harus dibedakan secara eksplisit.

## 3.5 Timestamp

Tabel transaksi utama memiliki:

- `created_at`
- `updated_at`
- `created_by`
- `updated_by`, jika relevan.

Waktu disimpan menggunakan `TIMESTAMPTZ`.

Tampilan menggunakan zona waktu WIB atau zona waktu sesuai lokasi bisnis.

Sistem tidak boleh mengubah makna tanggal transaksi ketika melakukan konversi timezone.

---

# 4. RANCANGAN ENTITAS UTAMA

## 4.1 Kelompok Identitas dan Akses

1. `user_accounts`
2. `roles`
3. `permissions`
4. `role_permissions`
5. `user_role_grants`
6. `user_access_scopes`
7. `auth_sessions`

## 4.2 Kelompok Master Data

8. `parties`
9. `farmers`
10. `farms`
11. `cooperatives`
12. `cooperative_memberships`
13. `mill_companies`
14. `mills`
15. `perumda_offices`
16. `vehicles`
17. `drivers`

## 4.3 Kelompok Harga

18. `price_sources`
19. `price_categories`
20. `mill_price_quotes`
21. `price_verification_events`
22. `disbun_reference_prices`

## 4.4 Kelompok Penerimaan TBS

23. `tbs_receipts`
24. `receipt_weighing_revisions`
25. `receipt_grading_items`

## 4.5 Kelompok Kontrak

26. `trade_contracts`
27. `contract_quota_periods`
28. `quota_reservations`

## 4.6 Kelompok Logistik

29. `delivery_orders`
30. `delivery_order_lines`
31. `delivery_status_events`

## 4.7 Kelompok Timbangan PKS

32. `mill_weighing_tickets`
33. `mill_grading_items`

## 4.8 Kelompok Rekonsiliasi

34. `reconciliation_cases`
35. `dispute_reviews`
36. `farmer_settlement_allocations`

## 4.9 Kelompok Keuangan

37. `invoices`
38. `invoice_lines`
39. `payment_approvals`
40. `payment_records`

## 4.10 Kelompok Publik dan Pendukung

41. `public_pages`
42. `public_notices`
43. `file_assets`
44. `audit_events`
45. `idempotency_records`
46. `outbox_events`
47. `system_rule_versions`
48. `user_notifications`

**Jumlah: 48 tabel kandidat pada model logis awal.**

Jumlah ini merupakan inventaris desain, bukan kewajiban membuat seluruh tabel sekaligus pada migrasi pertama. Tabel yang tidak diperlukan pada scope MVP dapat ditunda, selama kontrak bisnis inti tetap terpenuhi.

---

# 5. ENTITY RELATIONSHIP MODEL

## 5.1 Hubungan Data Utama

Relasi yang direncanakan:

- Satu pihak bisnis dapat memiliki satu profil khusus sesuai jenisnya.
- Satu koperasi memiliki banyak anggota petani.
- Satu petani dapat mempunyai beberapa kebun.
- Satu petani dapat mempunyai banyak penerimaan TBS.
- Satu penerimaan dapat mempunyai revisi penimbangan.
- Satu penerimaan dapat mempunyai beberapa rincian grading.
- Satu PKS dapat memiliki banyak harga.
- Satu PKS dapat memiliki banyak kontrak.
- Satu kontrak dapat mempunyai beberapa periode kuota.
- Satu e-DO dapat mengandung banyak penerimaan TBS.
- Satu penerimaan hanya boleh berada pada satu alokasi pengiriman aktif.
- Satu e-DO mempunyai satu tiket timbang final yang berlaku pada baseline MVP.
- Satu tiket dapat memiliki beberapa versi jika dikoreksi.
- Satu e-DO dapat memiliki riwayat rekonsiliasi.
- Satu rekonsiliasi aktif menjadi dasar proses penyelesaian.
- Satu faktur memiliki satu atau beberapa rincian nilai.
- Satu pembayaran mengacu pada faktur atau kewajiban yang telah disahkan sesuai alur bisnis.

## 5.2 Diagram ERD Konseptual

**[PLACEHOLDER GAMBAR DBD-01 — ERD SISTEM KESELURUHAN]**

Diagram dapat digambar melalui dbdiagram.io, Mermaid, atau alat pemodelan ERD lainnya.

Relasi inti:

Petani → Kebun → Penerimaan TBS → Penimbangan → Detail Muatan → e-DO → Tiket PKS → Rekonsiliasi → Faktur → Pembayaran.

Relasi pendukung:

Koperasi → Petani dan Penerimaan.

PKS → Harga, Kontrak, e-DO, dan Tiket Timbang.

Kontrak → Kuota → Reservasi Pengiriman.

Pengguna → Hak Akses dan Audit.

## 5.3 Aturan Kardinalitas

| Relasi                       | Kardinalitas                     |
| ---------------------------- | -------------------------------- |
| Petani → Kebun              | 1:N                              |
| Koperasi → Keanggotaan      | 1:N                              |
| Petani → Keanggotaan        | 1:N historis                     |
| Petani → Penerimaan         | 1:N                              |
| Penerimaan → Revisi Timbang | 1:N                              |
| PKS → Harga                 | 1:N                              |
| PKS → Kontrak               | 1:N                              |
| Kontrak → Periode Kuota     | 1:N                              |
| e-DO → Detail Muatan        | 1:N                              |
| Penerimaan → Detail Muatan  | 1:N historis, maksimum 1 aktif   |
| e-DO → Tiket PKS            | 1:N versi, maksimum 1 current    |
| e-DO → Kasus Rekonsiliasi   | 1:N historis, maksimum 1 current |
| Faktur → Detail Faktur      | 1:N                              |
| Faktur → Catatan Pembayaran | 1:N, sesuai kebijakan pembayaran |
| Pengguna → Audit            | 1:N                              |

---

# 6. IDENTITAS, AKUN, DAN OTORISASI

## 6.1 Tabel `user_accounts`

Menyimpan identitas akun pengguna internal.

| Kolom              | Tipe              | Keterangan              |
| ------------------ | ----------------- | ----------------------- |
| id                 | UUID PK           | ID pengguna             |
| username           | VARCHAR(100)      | Username unik           |
| email              | VARCHAR(255) NULL | Email                   |
| password_hash      | TEXT              | Hash Argon2id           |
| linked_party_id    | UUID FK NULL      | Identitas pihak terkait |
| status             | VARCHAR(20)       | ACTIVE/INACTIVE/LOCKED  |
| failed_login_count | INTEGER           | Jumlah gagal login      |
| last_login_at      | TIMESTAMPTZ NULL  | Login terakhir          |
| created_at         | TIMESTAMPTZ       | Waktu pembuatan         |
| updated_at         | TIMESTAMPTZ       | Waktu perubahan         |

Aturan:

- Username unik.
- Password disimpan sebagai hash.
- Email disimpan dalam format konsisten jika digunakan.
- Akun dapat dinonaktifkan.
- Riwayat transaksi tidak dihapus saat akun dinonaktifkan.

## 6.2 Tabel `roles`

Kolom:

- id.
- code.
- name.
- description.
- is_active.

Contoh kode:

- FARMER.
- COOPERATIVE_OPERATOR.
- PERUMDA_OPERATIONS.
- PERUMDA_FINANCE.
- MILL_OPERATOR.
- DIRECTOR.
- SYSTEM_ADMIN.

## 6.3 Tabel `permissions`

Kolom:

- id.
- code.
- module.
- resource.
- action.
- description.

Contoh:

- `prices.read`.
- `prices.create`.
- `prices.verify`.
- `receipts.create`.
- `delivery_orders.issue`.
- `reconciliations.resolve`.
- `payments.approve`.
- `audit.read`.

## 6.4 Tabel `role_permissions`

Kolom:

- role_id FK.
- permission_id FK.

Unique:

`(role_id, permission_id)`.

## 6.5 Tabel `user_role_grants`

Kolom:

- id.
- user_id FK.
- role_id FK.
- granted_by FK.
- granted_at.
- revoked_at NULL.

Digunakan untuk mempertahankan riwayat pemberian peran.

## 6.6 Tabel `user_access_scopes`

Membatasi cakupan data pengguna.

Kolom:

- id.
- user_id FK.
- scope_type.
- farmer_id FK NULL.
- cooperative_id FK NULL.
- mill_id FK NULL.
- granted_by.
- created_at.
- revoked_at.

Contoh scope:

- FARMER.
- COOPERATIVE.
- MILL.
- PERUMDA_GLOBAL.

Aturan:

- Scope FARMER wajib menunjuk petani.
- Scope COOPERATIVE wajib menunjuk koperasi.
- Scope MILL wajib menunjuk PKS.
- Scope global hanya diberikan berdasarkan kewenangan.
- Kombinasi scope yang tidak valid ditolak.

## 6.7 Tabel `auth_sessions`

Kolom:

- id.
- user_id FK.
- session_token_hash.
- created_at.
- expires_at.
- revoked_at NULL.
- last_seen_at.
- metadata keamanan yang telah dibatasi.

Session token mentah tidak disimpan.

Session yang kedaluwarsa atau dicabut tidak dapat dipakai lagi.

---

# 7. MASTER DATA PIHAK BISNIS

## 7.1 Tabel `parties`

Merupakan registry pihak bisnis yang digunakan lintas modul, termasuk untuk relasi keuangan.

Kolom:

- id UUID PK.
- party_type.
- display_name.
- status.
- created_at.
- updated_at.

Jenis pihak:

- PERUMDA.
- FARMER.
- COOPERATIVE.
- MILL_COMPANY.

Satu party dapat memiliki profil khusus sesuai jenisnya.

Aplikasi harus memastikan konsistensi antara `party_type` dan tabel profil terkait.

## 7.2 Tabel `farmers`

Kolom:

- id.
- party_id FK UNIQUE.
- farmer_code UNIQUE.
- full_name.
- contact_phone.
- identity_reference NULL.
- status.
- created_at.
- updated_at.

Data identitas sensitif hanya disimpan jika benar-benar diperlukan dan memiliki dasar pemrosesan yang sah.

## 7.3 Tabel `farms`

Kolom:

- id.
- farmer_id FK.
- farm_code UNIQUE.
- farm_name.
- area_hectares NUMERIC(12,4).
- planting_year NULL.
- stdb_number NULL.
- village.
- district.
- latitude NULL.
- longitude NULL.
- verification_status.
- created_at.
- updated_at.

Koordinat kebun merupakan data terbatas dan tidak otomatis dipublikasikan.

## 7.4 Tabel `cooperatives`

Kolom:

- id.
- party_id FK UNIQUE.
- cooperative_code UNIQUE.
- cooperative_name.
- address.
- contact_phone.
- status.
- created_at.
- updated_at.

## 7.5 Tabel `cooperative_memberships`

Kolom:

- id.
- cooperative_id FK.
- farmer_id FK.
- membership_number.
- joined_at.
- ended_at NULL.
- status.

Aturan:

- Riwayat keanggotaan tidak dihapus.
- Satu petani dapat memiliki riwayat keanggotaan.
- Jika SOP mensyaratkan satu koperasi aktif per petani, sistem menerapkan constraint atau validasi yang sesuai.

## 7.6 Tabel `mill_companies`

Kolom:

- id.
- party_id FK UNIQUE.
- company_code UNIQUE.
- company_name.
- contact_phone.
- address.
- status.
- created_at.
- updated_at.

## 7.7 Tabel `mills`

Kolom:

- id.
- mill_company_id FK.
- mill_code UNIQUE.
- mill_name.
- address.
- district.
- regency.
- province.
- latitude NULL.
- longitude NULL.
- contact_phone NULL.
- partnership_status.
- is_public.
- location_verified_at NULL.
- created_at.
- updated_at.

Aturan koordinat:

- Latitude antara -90 dan 90.
- Longitude antara -180 dan 180.
- Koordinat harus lengkap berpasangan.
- Lokasi yang belum diverifikasi tidak ditampilkan sebagai koordinat pasti.

## 7.8 Tabel `perumda_offices`

Kolom:

- id.
- office_name.
- address.
- latitude NULL.
- longitude NULL.
- public_contact NULL.
- is_public.
- created_at.
- updated_at.

## 7.9 Tabel `vehicles`

Kolom:

- id.
- plate_number UNIQUE.
- vehicle_type.
- nominal_capacity_kg NULL.
- status.
- created_at.
- updated_at.

## 7.10 Tabel `drivers`

Kolom:

- id.
- full_name.
- contact_phone.
- driver_reference NULL.
- status.
- created_at.
- updated_at.

---

# 8. DATABASE HARGA TBS MULTI-PKS

## 8.1 Tujuan

Menyimpan informasi harga TBS dari beberapa PKS, memisahkan harga acuan Disbun, dan mempertahankan riwayat perubahan.

## 8.2 Tabel `price_sources`

Kolom:

- id.
- source_code UNIQUE.
- source_name.
- source_type.
- source_url NULL.
- description.
- status.

Contoh kategori:

- DISBUN.
- MILL_OFFICIAL.
- MILL_DOCUMENT.
- VERIFIED_MANUAL.

Sumber informasi tidak otomatis dinyatakan resmi hanya karena tercatat pada database.

## 8.3 Tabel `price_categories`

Kolom:

- id.
- category_code UNIQUE.
- name.
- description.
- unit.
- quality_basis.
- age_group NULL.
- is_active.

Kategori ini mencegah sistem membandingkan harga yang tidak sepadan.

## 8.4 Tabel `mill_price_quotes`

Kolom utama:

| Kolom              | Tipe             | Fungsi           |
| ------------------ | ---------------- | ---------------- |
| id                 | UUID PK          | ID harga         |
| mill_id            | UUID FK          | PKS              |
| price_category_id  | UUID FK          | Kategori         |
| source_id          | UUID FK          | Sumber           |
| price_per_kg       | NUMERIC(18,2)    | Harga            |
| effective_from     | TIMESTAMPTZ      | Awal berlaku     |
| effective_until    | TIMESTAMPTZ NULL | Akhir berlaku    |
| status             | VARCHAR(25)      | Status workflow  |
| submitted_by       | UUID FK          | Penginput        |
| verified_by        | UUID FK NULL     | Verifikator      |
| verified_at        | TIMESTAMPTZ NULL | Waktu verifikasi |
| published_at       | TIMESTAMPTZ NULL | Waktu publikasi  |
| source_document_id | UUID FK NULL     | Bukti            |
| notes              | TEXT NULL        | Keterangan       |
| created_at         | TIMESTAMPTZ      | Pembuatan        |
| updated_at         | TIMESTAMPTZ      | Perubahan        |

Status:

- DRAFT.
- PENDING_VERIFICATION.
- VERIFIED.
- REJECTED.
- PUBLISHED.
- REVOKED.

Status kedaluwarsa ditentukan dari periode berlaku dan dapat ditampilkan sebagai EXPIRED pada aplikasi.

## 8.5 Aturan Harga

- Harga harus positif.
- Periode berlaku harus valid.
- PKS dan kategori harus tersedia.
- Sumber harus jelas.
- Harga publik harus terverifikasi.
- Harga lama tidak dihapus.
- Harga transaksi historis tidak boleh berubah karena pembaruan harga publik.
- Publikasi yang bertumpang tindih harus dicegah atau memiliki aturan prioritas yang disahkan.

## 8.6 Tabel `price_verification_events`

Kolom:

- id.
- price_quote_id FK.
- action.
- previous_status.
- new_status.
- actor_id FK.
- reason.
- created_at.

Riwayat verifikasi bersifat append-only pada jalur aplikasi.

## 8.7 Tabel `disbun_reference_prices`

Kolom:

- id.
- price_source_id FK.
- price_category_id FK.
- price_per_kg.
- effective_from.
- effective_until.
- source_document_id NULL.
- verification_status.
- created_at.

Harga Disbun memiliki tabel terpisah karena makna bisnisnya berbeda dari harga pembelian PKS.

## 8.8 Query Publik

Backend harus menyediakan query yang mengambil:

- PKS aktif yang diizinkan tampil.
- Harga yang telah dipublikasikan.
- Kategori yang sesuai.
- Periode berlaku yang masih aktif.
- Sumber dan waktu pembaruan.

Query dapat menggunakan PostgreSQL dan cache Redis.

Harga yang tidak tersedia harus dikembalikan sebagai kondisi kosong, bukan angka nol yang disalahartikan sebagai harga berlaku.

---

# 9. DATABASE PENERIMAAN TBS

## 9.1 Tabel `tbs_receipts`

Kolom:

- id.
- receipt_number UNIQUE.
- farmer_id FK.
- farm_id FK.
- cooperative_id FK.
- harvest_date NULL.
- received_at.
- status.
- created_by.
- created_at.
- updated_at.
- version INTEGER.

Status:

- DRAFT.
- VALIDATED.
- ALLOCATED.
- SHIPPED.
- CLOSED.
- CANCELLED.

## 9.2 Tabel `receipt_weighing_revisions`

Digunakan untuk menyimpan hasil timbang dan koreksi.

Kolom:

- id.
- receipt_id FK.
- revision_number INTEGER.
- gross_weight_kg NUMERIC(14,3).
- tare_weight_kg NUMERIC(14,3).
- net_weight_kg.
- weighed_at.
- weighed_by.
- is_current BOOLEAN.
- correction_reason NULL.
- created_at.

Aturan:

- Bruto tidak negatif.
- Tara tidak negatif.
- Tara tidak melebihi bruto.
- Netto = bruto − tara.
- Satu penerimaan hanya mempunyai satu versi timbang current.
- Revisi lama tetap tersimpan.

Netto dapat diimplementasikan sebagai generated column jika struktur final mendukung.

## 9.3 Tabel `receipt_grading_items`

Kolom:

- id.
- weighing_revision_id FK.
- grading_category.
- measurement_value.
- deduction_type.
- deduction_value.
- deduction_weight_kg NULL.
- deduction_amount NULL.
- calculation_basis.
- notes.
- created_at.

Pemotongan berbasis berat dan pemotongan berbasis uang harus dibedakan.

Perhitungan tidak boleh menggunakan satu kolom potongan ambigu.

---

# 10. DATABASE KONTRAK DAN KUOTA

## 10.1 Tabel `trade_contracts`

Kolom:

- id.
- contract_number UNIQUE.
- mill_id FK.
- start_date.
- end_date.
- price_rule_type.
- agreed_price_per_kg NULL.
- grading_policy_reference.
- payment_terms.
- status.
- approved_by NULL.
- approved_at NULL.
- created_at.
- updated_at.

Harga kontrak dan harga publik adalah data berbeda.

## 10.2 Tabel `contract_quota_periods`

Kolom:

- id.
- contract_id FK.
- period_start.
- period_end.
- quota_limit_kg.
- status.
- created_at.
- updated_at.

## 10.3 Tabel `quota_reservations`

Kolom:

- id.
- quota_period_id FK.
- delivery_order_id FK.
- reserved_weight_kg.
- consumed_weight_kg.
- status.
- reserved_at.
- released_at NULL.
- consumed_at NULL.

Status:

- RESERVED.
- CONSUMED.
- RELEASED.

## 10.4 Aturan Kuota

Kuota tersedia dihitung berdasarkan:

Kuota Total − Kuota yang Sudah Dikonsumsi − Reservasi Aktif yang Belum Dikonsumsi.

Satu reservasi hanya boleh dihitung satu kali.

Penggunaan nilai `consumed_weight_kg` harus mengikuti aturan kontrak yang disahkan, apakah berdasarkan berat asal atau berat diterima PKS.

## 10.5 Concurrency

Pembuatan reservasi harus berlangsung dalam transaksi database yang aman.

Gunakan row-level locking atau mekanisme concurrency setara.

Sistem harus mencegah dua request menggunakan kuota tersisa yang sama secara berlebihan.

---

# 11. DATABASE LOGISTIK DAN e-DO

## 11.1 Tabel `delivery_orders`

Kolom:

- id.
- delivery_order_number UNIQUE.
- cooperative_id FK.
- mill_id FK.
- contract_id FK.
- vehicle_id FK.
- driver_id FK.
- status.
- issued_at NULL.
- departed_at NULL.
- arrived_at NULL.
- completed_at NULL.
- qr_reference_hash NULL.
- created_by.
- version INTEGER.
- created_at.
- updated_at.

## 11.2 Tabel `delivery_order_lines`

Tabel ini menghubungkan satu surat jalan dengan beberapa penerimaan TBS.

Kolom:

- id.
- delivery_order_id FK.
- receipt_id FK.
- origin_weight_snapshot_kg.
- allocation_status.
- created_at.
- released_at NULL.

Status alokasi:

- ACTIVE.
- RELEASED.

Aturan:

- Satu e-DO dapat memiliki banyak baris muatan.
- Pada baseline, satu penerimaan dialokasikan utuh.
- Satu penerimaan hanya boleh memiliki satu alokasi ACTIVE.
- Jika pengiriman dibatalkan secara sah, alokasi dapat dilepaskan.
- Riwayat alokasi lama tidak dihapus.

## 11.3 Snapshot Berat

`origin_weight_snapshot_kg` menyimpan berat yang digunakan saat alokasi disahkan.

Nilai tersebut tidak berubah otomatis apabila catatan penerimaan mengalami koreksi pada masa berikutnya.

Koreksi setelah pengiriman memerlukan workflow resmi.

## 11.4 Tabel `delivery_status_events`

Kolom:

- id.
- delivery_order_id FK.
- previous_status.
- new_status.
- actor_id FK.
- event_time.
- reason NULL.
- metadata JSONB NULL.

Status pengiriman harus mengikuti state transition yang ditetapkan AFD dan BSD.

## 11.5 QR Code

Database hanya menyimpan referensi identitas atau hash token verifikasi yang aman.

QR Code tidak boleh memuat password, token sesi, atau data pribadi sensitif.

---

# 12. DATABASE TIKET TIMBANG PKS

## 12.1 Tabel `mill_weighing_tickets`

Kolom:

- id.
- delivery_order_id FK.
- mill_id FK.
- ticket_number.
- revision_number.
- previous_ticket_id FK NULL.
- gross_weight_kg.
- tare_weight_kg.
- net_weight_kg.
- weighed_at.
- verified_at NULL.
- verified_by NULL.
- is_current BOOLEAN.
- status.
- proof_file_id FK NULL.
- correction_reason NULL.
- created_at.

## 12.2 Aturan

- Nomor tiket harus unik menurut cakupan PKS dan versi.
- Satu e-DO memiliki maksimum satu tiket current pada baseline.
- Revisi membuat versi baru.
- Versi lama tetap tersimpan.
- Seluruh nilai bruto, tara, dan netto divalidasi.
- Tiket belum diverifikasi tidak digunakan sebagai dasar rekonsiliasi final.

## 12.3 Tabel `mill_grading_items`

Kolom:

- id.
- mill_ticket_id FK.
- grading_category.
- deduction_type.
- deduction_value.
- calculation_basis.
- notes.

## 12.4 Pencocokan Dokumen

Sistem harus memvalidasi:

- Identitas e-DO.
- PKS tujuan.
- Nomor tiket.
- Status tiket.
- Status pengiriman.
- Hubungan dokumen.

---

# 13. DATABASE REKONSILIASI

## 13.1 Tabel `reconciliation_cases`

Kolom:

| Kolom                | Tipe             | Fungsi                  |
| -------------------- | ---------------- | ----------------------- |
| id                   | UUID PK          | ID kasus                |
| delivery_order_id    | UUID FK          | Pengiriman              |
| mill_ticket_id       | UUID FK          | Tiket pabrik            |
| revision_number      | INTEGER          | Versi proses            |
| origin_weight_kg     | NUMERIC(14,3)    | Berat asal              |
| mill_weight_kg       | NUMERIC(14,3)    | Berat PKS               |
| difference_weight_kg | NUMERIC(14,3)    | Selisih                 |
| difference_percent   | NUMERIC(9,4)     | Persentase              |
| tolerance_percent    | NUMERIC(9,4)     | Toleransi saat evaluasi |
| rule_version_id      | UUID FK          | Versi aturan            |
| status               | VARCHAR(25)      | Hasil                   |
| is_current           | BOOLEAN          | Versi aktif             |
| calculated_at        | TIMESTAMPTZ      | Waktu hitung            |
| resolved_at          | TIMESTAMPTZ NULL | Waktu penyelesaian      |
| created_by           | UUID FK          | Pelaksana               |
| created_at           | TIMESTAMPTZ      | Pembuatan               |

## 13.2 Rumus Selisih

Selisih Berat = Berat Asal − Berat PKS.

Persentase Selisih = (Selisih Berat / Berat Asal) × 100%.

Jika berat asal nol, rekonsiliasi normal tidak boleh dijalankan.

Jika dasar berat tidak setara, transaksi harus ditandai untuk koreksi atau pemeriksaan.

## 13.3 Aturan Versi

- Satu e-DO memiliki satu rekonsiliasi current.
- Rekonsiliasi ulang membuat versi baru.
- Toleransi disimpan sebagai snapshot.
- Perubahan toleransi masa depan tidak mengubah keputusan historis.
- Hasil pemeriksaan tidak boleh menghapus rekonsiliasi sebelumnya.

## 13.4 Tabel `dispute_reviews`

Kolom:

- id.
- reconciliation_case_id FK.
- reviewer_id FK.
- previous_status.
- decision.
- reason.
- evidence_file_id FK NULL.
- approved_by FK NULL.
- reviewed_at.
- created_at.

## 13.5 Tabel `farmer_settlement_allocations`

Tabel ini dirancang untuk menghubungkan nilai penyelesaian pengiriman dengan kontribusi petani asal.

Kolom:

- id.
- reconciliation_case_id FK.
- receipt_id FK.
- farmer_id FK.
- allocation_basis_weight_kg.
- agreed_weight_kg NULL.
- allocation_policy_version_id FK.
- gross_amount.
- deduction_amount.
- net_amount.
- status.
- approved_at NULL.
- created_at.

Aturan penting:

- Tidak boleh menghasilkan pembagian nilai final tanpa kebijakan alokasi yang disahkan.
- Setiap penerimaan yang dialokasikan harus dapat ditelusuri.
- Jumlah nilai alokasi harus direkonsiliasi terhadap nilai total yang menjadi dasar penyelesaian.
- Perbedaan pembulatan harus ditangani dengan aturan eksplisit.
- Riwayat koreksi alokasi harus tersimpan.

---

# 14. DATABASE FAKTUR DAN PEMBAYARAN

## 14.1 Prinsip Pemisahan Arus Keuangan

Database harus membedakan:

- Piutang/tagihan Perumda kepada PKS.
- Kewajiban Perumda kepada koperasi atau mitra.
- Pembayaran kepada petani jika pencatatannya menjadi bagian dari sistem.

Pembayaran masuk dari PKS tidak otomatis berarti pembayaran kepada petani selesai.

## 14.2 Tabel `invoices`

Kolom:

- id.
- invoice_number UNIQUE.
- invoice_type.
- creditor_party_id FK.
- debtor_party_id FK.
- reconciliation_case_id FK NULL.
- invoice_date.
- due_date NULL.
- gross_amount.
- deduction_amount.
- total_amount.
- status.
- issued_at NULL.
- verified_by NULL.
- created_at.
- updated_at.

`invoice_type`:

- ACCOUNTS_RECEIVABLE.
- ACCOUNTS_PAYABLE.

## 14.3 Tabel `invoice_lines`

Kolom:

- id.
- invoice_id FK.
- reference_type.
- description.
- quantity.
- unit.
- unit_price.
- line_amount.
- created_at.

Referensi transaksi detail perlu dimodelkan menggunakan foreign key yang konkret untuk setiap jenis hubungan yang diwajibkan, bukan hanya string referensi yang tidak dapat diverifikasi.

## 14.4 Tabel `payment_approvals`

Kolom:

- id.
- invoice_id FK.
- requested_by.
- approver_id.
- decision.
- decision_reason.
- requested_at.
- decided_at NULL.

## 14.5 Tabel `payment_records`

Kolom:

- id.
- payment_number UNIQUE.
- invoice_id FK.
- amount NUMERIC(20,2).
- payment_date.
- payment_method.
- payment_reference.
- proof_file_id FK NULL.
- status.
- recorded_by.
- verified_by NULL.
- verified_at NULL.
- created_at.

Status:

- DRAFT.
- PENDING_VERIFICATION.
- VERIFIED.
- REJECTED.
- REVERSED.

## 14.6 Aturan Pembayaran

- Nilai pembayaran harus positif.
- Pembayaran tidak boleh melampaui kewajiban yang sah tanpa prosedur khusus.
- Pembayaran memerlukan referensi faktur.
- Bukti yang belum diverifikasi tidak menghasilkan status PAID.
- Duplikasi referensi pembayaran harus dicegah sesuai cakupan sumber.
- Pembayaran yang dibatalkan atau dikoreksi tetap memiliki riwayat.
- Status invoice dihitung berdasarkan verifikasi dan nilai pembayaran terkait.
- Jika pembayaran sebagian tidak didukung MVP, proses harus menolak pembayaran sebagian secara eksplisit.

## 14.7 Pengamanan

Data rekening dan bukti pembayaran hanya dapat diakses oleh pihak berwenang.

Informasi tersebut tidak boleh dimasukkan ke Portal Publik atau log HTTP.

---

# 15. DATABASE KONTEN PORTAL PUBLIK

## 15.1 Tabel `public_pages`

Kolom:

- id.
- slug UNIQUE.
- title.
- content.
- publication_status.
- published_at.
- updated_by.
- updated_at.

Contoh halaman:

- Tentang Perumda.
- Tentang Agro Niaga.
- Informasi Kemitraan.
- Kontak.

## 15.2 Tabel `public_notices`

Kolom:

- id.
- title.
- body.
- start_at.
- end_at.
- status.
- created_by.
- created_at.

Digunakan untuk pengumuman yang diizinkan dipublikasikan.

## 15.3 Aturan

- Hanya konten berstatus PUBLISHED ditampilkan.
- Konten internal tidak boleh muncul melalui API publik.
- HTML atau konten kaya harus disanitasi sebelum ditampilkan.
- Riwayat perubahan konten penting harus dapat ditelusuri.

---

# 16. DATABASE PENDUKUNG SISTEM

## 16.1 Tabel `file_assets`

Kolom:

- id.
- storage_provider.
- storage_key.
- original_filename.
- mime_type.
- size_bytes.
- checksum.
- classification.
- uploaded_by.
- created_at.

Berkas disimpan di storage yang sesuai.

Database menyimpan metadata dan referensi, bukan seluruh isi berkas besar secara default.

## 16.2 Tabel `audit_events`

Kolom:

- id.
- actor_id NULL.
- event_type.
- module.
- resource_type.
- resource_id.
- previous_state JSONB NULL.
- new_state JSONB NULL.
- reason NULL.
- request_id.
- occurred_at.

Aturan:

- Audit bisnis disimpan append-only melalui jalur aplikasi.
- Field rahasia harus disaring.
- Audit tidak boleh berisi password atau token.
- Penghapusan dan akses audit dibatasi.
- Audit dan perubahan transaksi kritis harus disimpan secara konsisten.

## 16.3 Tabel `idempotency_records`

Kolom:

- id.
- actor_id.
- operation_key.
- idempotency_key.
- request_hash.
- processing_status.
- response_reference NULL.
- created_at.
- expires_at.

Unique:

`(actor_id, operation_key, idempotency_key)`.

Digunakan untuk melindungi operasi mutasi dari pengulangan request yang tidak disengaja.

## 16.4 Tabel `outbox_events`

Kolom:

- id.
- event_type.
- aggregate_type.
- aggregate_id.
- payload JSONB.
- status.
- attempt_count.
- created_at.
- processed_at NULL.

Dipakai apabila diperlukan pemrosesan durable seperti invalidasi cache, notifikasi, atau sinkronisasi eksternal setelah commit transaksi.

## 16.5 Tabel `system_rule_versions`

Kolom:

- id.
- rule_code.
- version_number.
- effective_from.
- effective_until NULL.
- rule_config JSONB.
- approval_status.
- approved_by NULL.
- created_at.

Contoh:

- Toleransi timbang.
- Aturan pembulatan.
- Kebijakan alokasi penyelesaian.
- Parameter grading yang disahkan.

Tidak semua aturan harus berada dalam JSONB.

Struktur numerik penting tetap menggunakan kolom bertipe eksplisit jika memerlukan constraint, query, dan integritas referensial yang kuat.

## 16.6 Tabel `user_notifications`

Kolom:

- id.
- user_id FK.
- notification_type.
- title.
- message.
- resource_type NULL.
- resource_id NULL.
- read_at NULL.
- created_at.

Notifikasi tidak boleh mengandung rahasia atau data keuangan yang tidak perlu.

---

# 17. NORMALISASI DATABASE

## 17.1 First Normal Form

Setiap kolom harus menyimpan nilai atomik yang sesuai.

Contoh tidak disarankan:

Satu kolom berisi daftar seluruh nama petani dalam satu surat jalan.

Solusi:

Gunakan `delivery_order_lines`.

## 17.2 Second Normal Form

Atribut non-kunci harus bergantung pada keseluruhan kunci entitas yang relevan.

Data petani tidak diduplikasi pada setiap detail transaksi sebagai sumber master.

## 17.3 Third Normal Form

Atribut non-kunci tidak boleh bergantung secara transitif pada atribut non-kunci lain.

Contoh:

Informasi nama perusahaan PKS disimpan dalam tabel perusahaan dan direferensikan oleh PKS.

Nama perusahaan tidak harus disalin secara bebas ke seluruh tiket timbang.

## 17.4 Snapshot Historis

Pengecualian terkontrol terhadap pengulangan data diperbolehkan untuk kebutuhan snapshot transaksi.

Contoh:

- Harga yang disepakati.
- Berat muatan saat e-DO diterbitkan.
- Toleransi saat rekonsiliasi.
- Ketentuan kontrak yang berlaku pada transaksi.

Snapshot tersebut bukan duplikasi master data yang tidak terkendali, melainkan catatan fakta historis.

---

# 18. CONSTRAINT DAN INTEGRITAS REFERENSIAL

## 18.1 Primary Key

Seluruh tabel utama menggunakan primary key.

## 18.2 Foreign Key

Hubungan bisnis penting harus menggunakan foreign key.

## 18.3 Unique Constraint

Diterapkan pada:

- Username.
- Kode petani.
- Kode koperasi.
- Kode PKS.
- Nomor penerimaan.
- Nomor kontrak.
- Nomor e-DO.
- Nomor faktur.
- Nomor pembayaran.
- Kombinasi nomor tiket dan PKS/versi yang relevan.

## 18.4 Check Constraint

Contoh:

- Harga > 0.
- Berat >= 0.
- Tara <= bruto.
- Latitude dan longitude berada dalam rentang.
- Kuota >= 0.
- Persentase potongan valid menurut jenisnya.
- Nilai pembayaran > 0.
- Tanggal akhir tidak mendahului tanggal awal.

## 18.5 Partial Unique Index

Digunakan untuk menjamin:

- Satu timbangan current per penerimaan.
- Satu alokasi aktif per penerimaan.
- Satu tiket current per e-DO.
- Satu rekonsiliasi current per e-DO.

## 18.6 Delete Policy

Penghapusan berantai tidak digunakan sembarangan pada data transaksi.

Data yang telah digunakan umumnya dinonaktifkan atau dikoreksi dengan riwayat.

Penghapusan fisik hanya dilakukan berdasarkan kebijakan retensi dan kewenangan yang sah.

---

# 19. CONTOH SQL KRITIS

Bagian ini adalah ilustrasi implementasi constraint utama, bukan migration lengkap seluruh database.

## 19.1 Validasi Berat

```sql
CREATE TABLE receipt_weighing_revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id UUID NOT NULL
        REFERENCES tbs_receipts(id),
    revision_number INTEGER NOT NULL,
    gross_weight_kg NUMERIC(14,3) NOT NULL,
    tare_weight_kg NUMERIC(14,3) NOT NULL,
    net_weight_kg NUMERIC(14,3)
        GENERATED ALWAYS AS
        (gross_weight_kg - tare_weight_kg) STORED,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    correction_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_receipt_gross_nonnegative
        CHECK (gross_weight_kg >= 0),

    CONSTRAINT ck_receipt_tare_valid
        CHECK (
            tare_weight_kg >= 0
            AND tare_weight_kg <= gross_weight_kg
        ),

    CONSTRAINT uq_receipt_weighing_revision
        UNIQUE (receipt_id, revision_number)
);

CREATE UNIQUE INDEX ux_receipt_current_weighing
ON receipt_weighing_revisions (receipt_id)
WHERE is_current = TRUE;
```

## 19.2 Pencegahan Alokasi Ganda

```sql
CREATE UNIQUE INDEX ux_active_receipt_allocation
ON delivery_order_lines (receipt_id)
WHERE allocation_status = 'ACTIVE';
```

Dengan indeks ini, satu penerimaan tidak dapat memiliki dua alokasi aktif.

Prosedur pembatalan yang sah harus mengubah status alokasi dalam transaksi yang konsisten.

## 19.3 Satu Tiket Current per e-DO

```sql
CREATE UNIQUE INDEX ux_current_mill_ticket
ON mill_weighing_tickets (delivery_order_id)
WHERE is_current = TRUE;
```

## 19.4 Satu Rekonsiliasi Current per e-DO

```sql
CREATE UNIQUE INDEX ux_current_reconciliation
ON reconciliation_cases (delivery_order_id)
WHERE is_current = TRUE;
```

## 19.5 Indeks Harga Publik

```sql
CREATE INDEX ix_public_mill_prices
ON mill_price_quotes (
    mill_id,
    price_category_id,
    effective_from DESC
)
WHERE status = 'PUBLISHED';
```

Pengujian query plan tetap diperlukan untuk memastikan indeks bermanfaat terhadap query aktual.

---

# 20. INDEXING DAN QUERY OPTIMIZATION

## 20.1 Prinsip

Indeks dibuat berdasarkan pola query utama.

Tidak semua kolom harus diberi indeks.

## 20.2 Indeks Prioritas

| Tabel                   | Kolom                                   |
| ----------------------- | --------------------------------------- |
| user_accounts           | username                                |
| farmers                 | farmer_code                             |
| farms                   | farmer_id                               |
| cooperative_memberships | cooperative_id, farmer_id               |
| mills                   | mill_code, regency                      |
| mill_price_quotes       | mill_id, category, effective_from       |
| tbs_receipts            | cooperative_id, received_at             |
| tbs_receipts            | farmer_id, received_at                  |
| trade_contracts         | mill_id, status                         |
| delivery_orders         | status, created_at                      |
| delivery_order_lines    | delivery_order_id, receipt_id           |
| mill_weighing_tickets   | delivery_order_id                       |
| reconciliation_cases    | status, calculated_at                   |
| invoices                | status, due_date                        |
| payment_records         | invoice_id, status                      |
| audit_events            | resource_type, resource_id, occurred_at |

## 20.3 Pengujian Query

Gunakan:

- EXPLAIN.
- EXPLAIN ANALYZE.
- Query execution monitoring.
- Slow query logging.
- Benchmark pagination.

Indeks harus dievaluasi apabila menyebabkan overhead penulisan yang tidak sebanding.

## 20.4 Pagination

Daftar transaksi harus mendukung pagination.

Untuk data yang besar, pertimbangkan keyset pagination dengan urutan stabil.

## 20.5 Query Aggregation

Agregasi dashboard dijalankan melalui query khusus.

Jangan mengambil seluruh data transaksi ke frontend hanya untuk menjumlahkannya.

## 20.6 Materialized View

Materialized view dapat digunakan untuk laporan berat yang membutuhkan agregasi besar.

Namun, data ringkasan harus memiliki waktu pembaruan yang jelas.

Materialized view tidak boleh digunakan untuk mengambil keputusan pembayaran yang membutuhkan informasi transaksi terbaru secara konsisten.

---

# 21. CONCURRENCY DAN TRANSACTION SAFETY

## 21.1 Transaksi Penerbitan e-DO

Seluruh proses berikut berada dalam unit transaksi yang konsisten:

1. Periksa status penerimaan.
2. Periksa apakah penerimaan sudah dialokasikan.
3. Periksa kontrak.
4. Periksa kuota.
5. Buat reservasi kuota.
6. Simpan e-DO.
7. Simpan detail muatan.
8. Perbarui status penerimaan.
9. Simpan audit bisnis.
10. Commit.

Jika gagal, perubahan terkait harus di-rollback.

## 21.2 Transaksi Rekonsiliasi

1. Ambil tiket current.
2. Ambil data berat asal.
3. Verifikasi referensi.
4. Hitung selisih.
5. Ambil versi aturan.
6. Simpan hasil.
7. Perbarui status terkait.
8. Simpan audit.
9. Commit.

## 21.3 Transaksi Persetujuan Pembayaran

1. Periksa kewenangan.
2. Periksa status faktur.
3. Periksa status rekonsiliasi.
4. Periksa apakah persetujuan sudah dilakukan.
5. Simpan keputusan.
6. Perbarui status.
7. Simpan audit.
8. Commit.

## 21.4 Optimistic Locking

Entitas yang sering diubah dapat menggunakan kolom `version`.

Jika dua pengguna menyimpan perubahan berdasarkan versi lama, sistem menampilkan konflik.

## 21.5 Pessimistic Locking

Digunakan apabila operasi membutuhkan perlindungan langsung atas baris tertentu, seperti reservasi kuota.

Pemilihan strategi concurrency ditentukan melalui pengujian.

---

# 22. DATABASE SECURITY

## 22.1 Role Database

Penggunaan akun database harus dipisahkan menurut kebutuhan.

Contoh:

- Akun migration.
- Akun aplikasi.
- Akun monitoring read-only jika diperlukan.

Akun aplikasi tidak menggunakan superuser PostgreSQL.

## 22.2 Least Privilege

Setiap akun database hanya memiliki izin yang diperlukan.

## 22.3 Row-Level Security

PostgreSQL Row-Level Security dapat digunakan sebagai lapisan pertahanan tambahan untuk data yang memerlukan scope ketat.

Namun, kontrol utama tetap dilakukan pada Application Layer.

Jika RLS diterapkan, konteks pengguna dan scope harus disetel secara aman per transaksi. Koneksi pool tidak boleh mewariskan konteks pengguna sebelumnya.

## 22.4 Data Privacy

- Data pribadi tidak masuk API publik.
- Data sensitif tidak dicatat di access log.
- Data rekening tidak disimpan tanpa kebutuhan.
- Berkas rahasia tidak menggunakan URL publik permanen.
- Backup harus terlindungi.
- Akses langsung ke database production dibatasi.

## 22.5 Audit

Perubahan penting wajib dicatat.

Auditing teknis dan audit bisnis dipisahkan.

---

# 23. DATABASE BACKUP DAN RECOVERY

## 23.1 Backup

Sistem harus memiliki strategi backup sesuai lingkungan deployment.

Contoh:

- Backup penuh berkala.
- Backup sebelum migrasi besar.
- Penyimpanan backup terlindungi.
- Retensi backup berdasarkan kebijakan.

## 23.2 Recovery

Prosedur restore harus diuji.

Database tidak dianggap aman hanya karena berkas backup tersedia.

## 23.3 Migration

Alembic digunakan untuk seluruh perubahan schema.

Aturan:

- Migration memiliki revisi jelas.
- Tidak mengubah schema production secara manual.
- Migrasi diuji.
- Perubahan destruktif memerlukan pemeriksaan dampak.
- Backup tersedia sebelum perubahan berisiko.

---

# 24. REDIS CACHING

## 24.1 Prinsip

Redis digunakan sebagai cache sementara.

PostgreSQL tetap menjadi sumber kebenaran.

## 24.2 Data Cache

| Data                  | TTL Awal         | Invalidation                    |
| --------------------- | ---------------- | ------------------------------- |
| Harga publik          | 30–60 detik     | Setelah publikasi harga         |
| Direktori PKS         | 5–15 menit      | Setelah perubahan data PKS      |
| Profil Perumda        | 15 menit         | Setelah publikasi konten        |
| Konfigurasi referensi | Sesuai kebutuhan | Setelah perubahan versi         |
| Agregasi dashboard    | 15–60 detik     | Setelah perubahan data atau TTL |

TTL merupakan rekomendasi awal dan dapat berubah berdasarkan benchmark.

## 24.3 Cache Key

Contoh:

- `public:prices:v1:region:{region}`
- `public:mills:v1:region:{region}`
- `public:profile:v1`
- `dashboard:v1:scope:{scope}:period:{period}`

## 24.4 Aturan Cache

- Cache publik tidak berisi data pribadi.
- Cache privat harus menggunakan scope yang benar.
- Mutasi database diselesaikan sebelum invalidasi cache.
- Harga kedaluwarsa tidak boleh ditampilkan sebagai harga aktif.
- Redis gagal tidak boleh menyebabkan bypass autentikasi.
- Operasi keuangan tidak boleh menjadikan cache sebagai sumber status final.

---

# BAGIAN II — DATA CONTRACT UNTUK UI/UX

# 25. HUBUNGAN DATABASE DAN ANTARMUKA

Database tidak menentukan desain visual secara langsung.

Namun, rancangan database harus memungkinkan frontend menampilkan informasi dengan cepat, lengkap, dan konsisten.

Kebutuhan data untuk UI meliputi:

- Pagination.
- Search.
- Filtering.
- Sorting.
- Loading state.
- Empty state.
- Error state.
- Status transaksi.
- Timestamp pembaruan.
- Informasi sumber.
- Validation feedback.
- Activity history.
- Data version.
- Audit reference.

## 25.1 Portal Harga Multi-PKS

Response API harus menyediakan data yang diperlukan untuk:

- Kartu harga.
- Tabel perbandingan.
- Filter wilayah.
- Urutkan harga.
- Riwayat harga.
- Status kesegaran data.
- Detail lokasi.

## 25.2 Form Penerimaan TBS

Frontend membutuhkan:

- Daftar petani yang diizinkan.
- Daftar kebun terkait.
- Referensi koperasi.
- Aturan validasi.
- Preview berat netto.
- Status penyimpanan.
- Nomor penerimaan setelah berhasil.

## 25.3 Form e-DO

Frontend membutuhkan:

- Daftar muatan tersedia.
- Kontrak aktif.
- Kuota.
- PKS tujuan.
- Kendaraan.
- Sopir.
- Ringkasan muatan.
- Status validasi.
- Hasil penerbitan.

## 25.4 Halaman Rekonsiliasi

Frontend membutuhkan:

- Berat asal.
- Berat PKS.
- Selisih.
- Persentase selisih.
- Toleransi.
- Status.
- Dokumen bukti.
- Riwayat pemeriksaan.
- Aksi yang diizinkan.

## 25.5 Halaman Pembayaran

Frontend membutuhkan:

- Nomor faktur.
- Pihak pembayar dan penerima.
- Nominal.
- Status persetujuan.
- Bukti pembayaran.
- Status verifikasi.
- Riwayat keputusan.

---

# BAGIAN III — UI/UX DESIGN REQUIREMENTS

# 26. STANDAR UTAMA UI/UX

## 26.1 Pendekatan Desain

Frontend menggunakan kombinasi:

- Atomic Design.
- Feature-Based Architecture.
- 25 Prinsip UX Terpilih.
- Golden Ratio sebagai pedoman visual.
- Micro-interactions.
- Responsive Design.
- Accessibility.
- Data-Dense Interface Design.
- Usability Testing.

## 26.2 Tujuan

UI/UX harus:

1. Mudah dipahami masyarakat awam.
2. Tidak memaksa login untuk informasi publik.
3. Mempermudah pekerjaan petugas.
4. Mengurangi beban kognitif.
5. Mempercepat pencarian informasi.
6. Menurunkan kemungkinan kesalahan input.
7. Memberikan respons interaksi yang jelas.
8. Mengutamakan informasi penting.
9. Tetap konsisten di desktop dan mobile.
10. Mendukung tingkat literasi digital yang beragam.

---

# 27. PENERAPAN 25 HUKUM DAN PRINSIP UX

Daftar berikut merupakan 25 prinsip yang dipilih dari koleksi Laws of UX, bukan klaim bahwa ilmu UX secara universal hanya memiliki 25 hukum.

Sumber utama: https://lawsofux.com/laws/

| No. | Hukum/Prinsip                | Implementasi pada Aplikasi                                                                                                                 |
| --- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Jakob's Law                  | Gunakan pola navigasi, tabel, pencarian, dan formulir yang familier.                                                                       |
| 2   | Fitts's Law                  | Tombol aksi utama cukup besar dan mudah dijangkau, terutama pada ponsel.                                                                   |
| 3   | Hick's Law                   | Kurangi pilihan yang ditampilkan sekaligus; tampilkan tindakan sesuai konteks.                                                             |
| 4   | Miller's Law                 | Kelompokkan informasi agar pengguna tidak perlu mengingat banyak hal sekaligus; jangan menjadikan angka 7±2 sebagai batas menu yang kaku. |
| 5   | Doherty Threshold            | Berikan umpan balik segera; optimalkan interaksi cepat dan hindari antarmuka yang terasa tidak merespons.                                  |
| 6   | Aesthetic-Usability Effect   | Gunakan desain bersih, konsisten, dan profesional tanpa mengorbankan fungsi.                                                               |
| 7   | Peak-End Rule                | Pastikan penyelesaian transaksi memberikan ringkasan dan konfirmasi yang jelas.                                                            |
| 8   | Von Restorff Effect          | Buat satu tindakan penting atau status risiko menonjol tanpa memakai terlalu banyak warna perhatian.                                       |
| 9   | Tesler's Law                 | Pindahkan kerumitan kalkulasi ke sistem, bukan membebankannya kepada pengguna.                                                             |
| 10  | Postel's Law                 | Terima format input yang wajar, tetapi validasi dan keluarkan data secara konsisten.                                                       |
| 11  | Law of Proximity             | Kelompokkan field yang saling berhubungan, misalnya bruto, tara, dan netto.                                                                |
| 12  | Law of Similarity            | Gunakan bentuk dan warna yang konsisten untuk fungsi sejenis.                                                                              |
| 13  | Law of Common Region         | Pisahkan informasi menjadi panel atau area dengan batas yang jelas.                                                                        |
| 14  | Law of Uniform Connectedness | Tunjukkan keterhubungan data e-DO, tiket PKS, dan rekonsiliasi.                                                                            |
| 15  | Law of Prägnanz             | Sederhanakan representasi informasi kompleks agar mudah dipahami.                                                                          |
| 16  | Cognitive Load               | Kurangi istilah teknis dan informasi yang tidak dibutuhkan pada suatu langkah.                                                             |
| 17  | Chunking                     | Pecah formulir panjang ke dalam bagian-bagian yang bermakna.                                                                               |
| 18  | Serial Position Effect       | Tempatkan menu dan tindakan yang paling penting pada posisi mudah ditemukan.                                                               |
| 19  | Goal-Gradient Effect         | Tampilkan progres pada formulir atau workflow bertahap.                                                                                    |
| 20  | Zeigarnik Effect             | Berikan indikator pekerjaan yang belum selesai, seperti Draft dan Menunggu Verifikasi.                                                     |
| 21  | Selective Attention          | Utamakan informasi yang relevan terhadap tugas pengguna saat ini.                                                                          |
| 22  | Choice Overload              | Gunakan filter dan pencarian daripada menampilkan terlalu banyak pilihan tanpa pengelompokan.                                              |
| 23  | Mental Model                 | Gunakan istilah bisnis yang sudah dikenal petugas, seperti Surat Jalan, Timbangan, dan Pembayaran.                                         |
| 24  | Occam's Razor                | Pilih interaksi paling sederhana yang memenuhi kebutuhan.                                                                                  |
| 25  | Pareto Principle             | Prioritaskan fitur dan tindakan yang paling sering dipakai dalam operasional sehari-hari berdasarkan observasi.                            |

## 27.1 Contoh Penerapan pada Portal Publik

Beranda memprioritaskan:

1. Lihat Harga TBS.
2. Bandingkan Harga.
3. Cari Lokasi PKS.
4. Informasi Kemitraan.

Pengunjung tidak perlu melihat seluruh menu administrasi.

## 27.2 Contoh Penerapan pada Form Timbangan

Form menggunakan tiga field utama:

- Berat Bruto.
- Berat Tara.
- Berat Netto otomatis.

Field netto tidak diketik ulang.

Sistem memberikan peringatan langsung jika tara melebihi bruto.

Validasi server tetap menjadi penentu akhir.

## 27.3 Contoh Penerapan pada Rekonsiliasi

Tampilkan informasi:

- Berat koperasi.
- Berat PKS.
- Selisih.
- Toleransi.
- Status.
- Tindakan berikutnya.

Hindari menampilkan tabel teknis panjang ketika petugas hanya ingin mengetahui apakah transaksi perlu diperiksa.

---

# 28. GOLDEN RATIO DESIGN SYSTEM

## 28.1 Prinsip

Golden ratio mempunyai nilai:

φ ≈ 1,618.

Golden ratio dapat digunakan sebagai referensi komposisi visual untuk menciptakan keseimbangan.

Namun, proporsi ini bukan standar usability yang wajib dipenuhi pada setiap komponen.

Keterbacaan, aksesibilitas, dan kebutuhan responsif tetap menjadi prioritas.

## 28.2 Penggunaan pada Layout

Contoh komposisi desktop yang dapat dieksplorasi:

- Area konten utama: sekitar 61,8%.
- Area informasi pendukung: sekitar 38,2%.

Proporsi tersebut cocok untuk beberapa halaman yang memiliki konten utama dan informasi tambahan.

Untuk dashboard transaksi yang membutuhkan tabel lebar, proporsi tidak harus dipaksakan.

## 28.3 Sidebar Internal

Sidebar desktop menggunakan lebar yang tetap dan konsisten.

Rekomendasi awal:

- Lebar sidebar sekitar 240–272 px.
- Konten utama mengisi sisa area.
- Sidebar tidak ikut bergeser ketika konten utama discroll.
- Area konten utama dapat discroll secara independen bila diperlukan.

Lebar final ditentukan melalui pengujian responsif, bukan hanya rumus golden ratio.

## 28.4 Typography

Gunakan hierarki tipografi yang jelas.

Contoh skala awal:

- Body: 14–16 px.
- Label: 12–14 px.
- Subheading: 18–22 px.
- Heading: 24–32 px.
- Hero heading: 32–44 px sesuai layar.

Rasio sekitar 1,2–1,333 dapat dipakai untuk modular typography.

Golden ratio 1,618 dapat dieksplorasi pada komposisi tertentu, tetapi tidak wajib digunakan pada setiap kenaikan ukuran teks karena dapat menghasilkan perbedaan yang terlalu besar.

## 28.5 Spacing

Gunakan sistem spacing yang konsisten, misalnya:

- 4 px.
- 8 px.
- 12 px.
- 16 px.
- 24 px.
- 32 px.
- 48 px.

Spacing harus mengikuti hubungan antar-elemen, bukan sekadar angka dekoratif.

## 28.6 Penerapan pada Portal Publik

Golden ratio dapat digunakan sebagai inspirasi untuk:

- Komposisi hero.
- Pembagian teks dan visual.
- Perbandingan kartu informasi.
- Proporsi grafik pendukung.
- Area konten dan navigasi.

Pada mobile, semua layout harus beradaptasi agar informasi tidak menjadi terlalu sempit.

---

# 29. MICRO-INTERACTIONS

## 29.1 Definisi

Micro-interaction merupakan umpan balik kecil yang terjadi ketika pengguna melakukan aksi atau ketika sistem mengalami perubahan status.

Micro-interaction harus menjelaskan apa yang sedang terjadi, bukan hanya mempercantik aplikasi.

Referensi:

https://www.nngroup.com/articles/microinteractions/

## 29.2 Prinsip

- Cepat.
- Relevan.
- Konsisten.
- Tidak mengganggu.
- Memberikan feedback.
- Tidak memblokir tugas utama.
- Menghormati preferensi reduced motion.
- Tidak menggantikan pesan status yang jelas.

## 29.3 Micro-Interaction pada Tombol

Saat tombol ditekan:

- Tampilkan perubahan visual ringan.
- Tampilkan loading jika operasi membutuhkan waktu.
- Nonaktifkan aksi duplikat ketika diperlukan.
- Tampilkan hasil setelah backend memberikan konfirmasi.

Durasi visual awal yang dapat diuji:

- Hover/press: 100–180 ms.
- Transisi status ringan: 150–250 ms.
- Dialog/drawer: 180–300 ms.

Nilai tersebut merupakan pedoman desain awal, bukan standar wajib.

## 29.4 Micro-Interaction pada Form

Contoh:

Ketika petugas memasukkan berat bruto dan tara:

- Netto ditampilkan otomatis sebagai preview.
- Input tidak valid diberi penanda.
- Pesan kesalahan muncul dekat field.
- Fokus diarahkan ke field yang perlu diperbaiki saat submit gagal.

Penghitungan frontend tidak menggantikan validasi backend.

## 29.5 Micro-Interaction pada Pencarian

Saat pengguna mengetik nama PKS:

- Pencarian dapat menggunakan debounce sekitar 300–500 ms.
- Loading indicator ditampilkan bila diperlukan.
- Hasil diperbarui.
- Kondisi tanpa hasil ditampilkan.
- Permintaan pencarian lama tidak boleh menimpa hasil terbaru.

## 29.6 Micro-Interaction pada Harga TBS

Saat pengguna mengganti urutan harga:

- Daftar diperbarui.
- Pilihan sorting tetap terlihat.
- Tidak diperlukan animasi kartu yang berlebihan.
- Tanggal pembaruan dan kategori harga tetap terlihat.

Jika harga berubah:

- Tampilkan nilai terbaru setelah response sah.
- Gunakan indikator perubahan bila data sebelumnya tersedia.
- Jangan menampilkan animasi naik/turun tanpa data historis yang valid.

## 29.7 Micro-Interaction pada Peta

Ketika marker PKS dipilih:

- Marker mendapat status terpilih.
- Panel detail PKS tampil.
- Item daftar yang bersesuaian ikut ditandai.
- Pengguna dapat membuka navigasi.

Hindari animasi peta yang memutar atau melakukan zoom berlebihan secara otomatis.

## 29.8 Micro-Interaction pada e-DO

Ketika e-DO diterbitkan:

1. Tombol menampilkan status pemrosesan.
2. Sistem menunggu konfirmasi backend.
3. Jika berhasil, nomor e-DO ditampilkan.
4. QR Code ditampilkan.
5. Pengguna dapat melihat dokumen.
6. Jika gagal, pesan dan Request ID ditampilkan.

Tidak boleh menampilkan "Berhasil diterbitkan" sebelum server mengonfirmasi commit yang relevan.

## 29.9 Micro-Interaction pada Rekonsiliasi

Jika Matched:

- Tampilkan status yang jelas.
- Berikan ringkasan selisih.
- Tampilkan tindakan berikutnya.

Jika Dispute/Hold:

- Tampilkan peringatan yang mudah terlihat.
- Jelaskan alasan.
- Tampilkan langkah pemeriksaan.
- Jangan menggunakan animasi berkedip atau efek dramatis.

## 29.10 Micro-Interaction pada Pembayaran

Pada operasi persetujuan:

- Tampilkan ringkasan nominal.
- Tampilkan pihak penerima.
- Minta konfirmasi.
- Gunakan loading state selama request.
- Tampilkan hasil yang benar-benar dikonfirmasi backend.

Jangan menggunakan optimistic success untuk status pembayaran final.

## 29.11 Reduced Motion

Frontend harus menghormati:

`prefers-reduced-motion`.

Jika pengguna memilih pengurangan animasi, transisi non-esensial harus diminimalkan atau dinonaktifkan.

Micro-interaction penting tetap harus mempunyai feedback teks atau status yang dapat dipahami tanpa animasi.

---

# 30. PERFORMA UI/UX BERBASIS DATA

## 30.1 Prinsip

Antarmuka cepat membutuhkan dukungan query database yang efisien.

## 30.2 Public Price Performance

Sistem menggunakan:

- Query terfilter.
- Indeks.
- Redis cache.
- Pagination jika diperlukan.
- Response field minimal.
- Data freshness metadata.

## 30.3 Form Performance

Dropdown besar menggunakan pencarian server-side.

Jangan memuat seluruh petani Kabupaten Pelalawan sekaligus ke browser.

## 30.4 Dashboard Performance

Dashboard menggunakan endpoint agregasi.

Hindari N+1 query dan pengambilan data transaksi mentah yang tidak diperlukan.

## 30.5 Data Synchronization

TanStack Query digunakan untuk:

- Fetch.
- Caching frontend.
- Refetch.
- Mutation.
- Invalidation.
- Loading.
- Error.

Setelah mutasi:

- Query terkait diinvalidasi.
- Data terbaru dimuat kembali.
- Feedback ditampilkan setelah server mengonfirmasi.

## 30.6 Data Version

Untuk data sensitif yang dapat diedit bersama, response dapat menyertakan `version` atau concurrency token.

Jika versi data sudah berubah, frontend menampilkan konflik daripada menimpa perubahan pihak lain.

---

# 31. DESIGN SYSTEM ATOMIC DESIGN

## 31.1 Atoms

Komponen:

- Button.
- Input.
- Label.
- Icon.
- Text.
- Badge.
- Checkbox.
- Spinner.
- Skeleton.

## 31.2 Molecules

Komponen:

- SearchField.
- FormField.
- PriceDisplay.
- StatusIndicator.
- WeightInputGroup.
- DateFilter.
- LocationLink.

## 31.3 Organisms

Komponen:

- PriceComparisonTable.
- PublicNavbar.
- InternalSidebar.
- TbsReceivingForm.
- ReconciliationPanel.
- MillLocationMap.
- PaymentApprovalPanel.

## 31.4 Templates

Komponen:

- PublicTemplate.
- DashboardTemplate.
- TransactionTemplate.
- DataManagementTemplate.
- ExecutiveTemplate.

## 31.5 Pages

Contoh:

- PublicHomePage.
- PublicPricesPage.
- PublicMillsPage.
- FarmerDashboardPage.
- CooperativeReceivingPage.
- ReconciliationPage.
- ExecutiveDashboardPage.

Atomic Design mengatur komposisi visual.

Aturan transaksi tidak ditempatkan di komponen UI bersama.

---

# 32. UI/UX TRACEABILITY TERHADAP DATA

| Fitur UI/UX            | Sumber Data                | Prinsip                           |
| ---------------------- | -------------------------- | --------------------------------- |
| Harga multi-PKS        | mill_price_quotes          | Hick, Selective Attention         |
| Riwayat harga          | mill_price_quotes          | Chunking, Cognitive Load          |
| Lokasi pabrik          | mills                      | Jakob, Mental Model               |
| Peta interaktif        | mills                      | Fitts, Common Region              |
| Form penerimaan        | tbs_receipts               | Tesler, Chunking                  |
| Preview netto          | receipt_weighing_revisions | Doherty, Error Prevention         |
| Surat jalan            | delivery_orders            | Goal-Gradient                     |
| Daftar muatan          | delivery_order_lines       | Proximity, Connectedness          |
| Status pengiriman      | delivery_status_events     | Zeigarnik                         |
| Rekonsiliasi           | reconciliation_cases       | Von Restorff, Selective Attention |
| Riwayat dispute        | dispute_reviews            | Peak-End, Transparency            |
| Persetujuan pembayaran | payment_approvals          | Fitts, Cognitive Load             |
| Status pembayaran      | payment_records            | Mental Model                      |
| Dashboard eksekutif    | Query agregasi             | Pareto, Prägnanz                 |
| Audit aktivitas        | audit_events               | Traceability                      |

---

# BAGIAN IV — PENGUJIAN DAN VALIDASI

# 33. DATABASE TESTING

## 33.1 Referential Integrity Testing

Uji:

- Foreign key tidak valid.
- Penghapusan data yang sedang direferensikan.
- Relasi petani-koperasi.
- Relasi e-DO dan tiket.
- Relasi rekonsiliasi dan faktur.

## 33.2 Constraint Testing

Uji:

- Harga negatif.
- Tara melebihi bruto.
- Nomor dokumen duplikat.
- Alokasi ganda.
- Tiket current ganda.
- Rekonsiliasi current ganda.
- Pembayaran tidak valid.

## 33.3 Transaction Testing

Uji rollback pada:

- Penerbitan e-DO.
- Reservasi kuota.
- Pembaruan status.
- Rekonsiliasi.
- Persetujuan pembayaran.

## 33.4 Concurrency Testing

Uji dua request bersamaan pada:

- Kuota yang sama.
- Penerimaan yang sama.
- Penerbitan e-DO.
- Rekonsiliasi.
- Persetujuan pembayaran.

## 33.5 Performance Testing

Uji:

- Pembacaan harga.
- Pencarian petani.
- Daftar penerimaan.
- Daftar pengiriman.
- Daftar rekonsiliasi.
- Dashboard agregasi.
- Database connection pool.
- Cache hit ratio.
- Slow query.

## 33.6 Data Security Testing

Uji:

- Petani A tidak dapat membaca data Petani B.
- Operator koperasi tidak dapat mengakses koperasi lain.
- Petugas PKS tidak dapat mengubah tiket PKS lain.
- Data keuangan tidak dapat dibaca secara anonim.
- API tidak membocorkan informasi sensitif.
- Audit tidak memuat rahasia.

---

# 34. UI/UX TESTING

## 34.1 Functional UI Testing

- Navigasi halaman.
- Filter.
- Sorting.
- Search.
- Form validation.
- Error state.
- Loading state.
- Confirm dialog.
- State transition.
- Responsive behavior.

## 34.2 Accessibility Testing

Target utama mengacu pada WCAG 2.2 Level AA untuk fitur yang relevan.

Pengujian mencakup:

- Navigasi keyboard.
- Focus visible.
- Label formulir.
- Kontras.
- Pembacaan pesan kesalahan.
- Target sentuh.
- Reduced motion.

## 34.3 Responsive Testing

Contoh viewport:

- 375 px.
- 390 px.
- 768 px.
- 1024 px.
- 1280 px.
- 1440 px.

Kriteria:

- Tidak ada horizontal overflow yang tidak disengaja.
- Teks dapat dibaca.
- Tombol dapat dijangkau.
- Form dapat digunakan.
- Tabel mempertahankan informasi penting.
- Navigasi tidak menutupi konten.

## 34.4 Usability Testing

Gunakan SUS sesuai proposal tesis.

Uji juga kemampuan pengguna menyelesaikan tugas:

- Mencari harga PKS.
- Membandingkan harga.
- Menemukan lokasi.
- Mencatat penerimaan.
- Membuat e-DO.
- Memahami hasil rekonsiliasi.

Hasil aktual baru dapat ditentukan setelah pengujian responden.

## 34.5 Micro-Interaction Testing

Periksa:

- Feedback setelah klik.
- Tidak ada success palsu.
- Tidak ada double submit.
- Status loading konsisten.
- Error mudah dipahami.
- Reduced motion berfungsi.
- Tidak ada animasi yang menghalangi pekerjaan.
- Fokus keyboard tetap terkelola.

---

# 35. QUALITY GATES DATABASE

Database dinyatakan memenuhi baseline desain apabila:

1. Seluruh entitas inti memiliki primary key.
2. Relasi penting memiliki foreign key.
3. Struktur memenuhi prinsip normalisasi yang sesuai.
4. Data historis penting tidak berubah tanpa mekanisme koreksi.
5. Harga publik dan harga kontrak dipisahkan.
6. Berat asal dan berat PKS memiliki definisi jelas.
7. Revisi timbang memiliki riwayat.
8. Alokasi pengiriman ganda dicegah.
9. Kuota aman terhadap concurrent request.
10. Tiket current tidak ganda.
11. Rekonsiliasi current tidak ganda.
12. Perhitungan uang menggunakan tipe presisi.
13. Faktur dan pembayaran mempunyai relasi yang jelas.
14. Pembayaran masuk dan keluar dapat dibedakan.
15. Audit aktivitas penting tersedia.
16. Data privat tidak muncul di Portal Publik.
17. Migration dapat dijalankan.
18. Backup dan restore telah diuji pada lingkungan yang sesuai.
19. Indeks diuji berdasarkan query plan.
20. Operasi bisnis kritis mempunyai pengujian concurrency dan integritas.

---

# 36. QUALITY GATES UI/UX

Antarmuka dinyatakan memenuhi baseline apabila:

1. Portal Publik dapat digunakan tanpa login.
2. Informasi harga mudah ditemukan.
3. Harga memiliki sumber dan waktu pembaruan.
4. Lokasi PKS dapat diakses dengan mudah.
5. Tampilan mengikuti hierarki informasi.
6. Desain menggunakan Atomic Design secara konsisten.
7. Komponen tidak diduplikasi tanpa alasan.
8. Prinsip UX diterapkan berdasarkan konteks pengguna.
9. Golden ratio digunakan sebagai pedoman fleksibel.
10. Semua interaksi penting memiliki feedback.
11. Tidak ada animasi dekoratif yang mengganggu.
12. Error mudah dimengerti.
13. Form tidak memerlukan input berulang yang tidak perlu.
14. Dashboard sesuai peran.
15. Tampilan responsif.
16. Navigasi keyboard berfungsi.
17. Reduced motion didukung.
18. Operasi keuangan tidak menggunakan konfirmasi berhasil sebelum server memastikan hasilnya.
19. Antarmuka menampilkan status data yang sebenarnya.
20. Uji usability dilakukan pada pengguna sasaran.

---

# 37. TRACEABILITY TERHADAP DOKUMEN SEBELUMNYA

| Dokumen        | Keterkaitan                                                           |
| -------------- | --------------------------------------------------------------------- |
| PRD V1.1       | Sumber kebutuhan produk dan data                                      |
| TRD V1.1       | Sumber arsitektur backend, database, caching, security, dan frontend  |
| AFD V1.1       | Sumber alur aplikasi dan state transition                             |
| DBD V1.1       | Desain entitas, relasi, integritas, penyimpanan, dan dukungan data UI |
| BSD berikutnya | Ketentuan rumus dan kebijakan bisnis final                            |
| IPD berikutnya | Tahapan implementasi, migrasi, pengujian, dan sign-off                |

DBD tidak boleh mendefinisikan aturan bisnis baru yang bertentangan dengan PRD atau AFD.

Jika terdapat perbedaan, keputusan harus dicatat dan diperbarui secara konsisten pada dokumen terkait.

---

# 38. KEPUTUSAN YANG PERLU DIVALIDASI

| Kode        | Keputusan                                                  | Status                         |
| ----------- | ---------------------------------------------------------- | ------------------------------ |
| DBD-DEC-001 | Struktur identitas petani dan data pribadi yang diperlukan | Perlu validasi                 |
| DBD-DEC-002 | Jumlah koperasi aktif per petani                           | Perlu validasi                 |
| DBD-DEC-003 | Kategori harga PKS                                         | Perlu validasi                 |
| DBD-DEC-004 | Aturan periode harga bertumpang tindih                     | Perlu validasi                 |
| DBD-DEC-005 | Presisi dan pembulatan berat                               | Perlu validasi                 |
| DBD-DEC-006 | Formula grading                                            | Perlu validasi BSD             |
| DBD-DEC-007 | Dasar perhitungan kuota                                    | Perlu validasi                 |
| DBD-DEC-008 | Satu tiket final per e-DO                                  | Baseline MVP, perlu konfirmasi |
| DBD-DEC-009 | Ambang toleransi timbang                                   | Perlu validasi                 |
| DBD-DEC-010 | Metode alokasi hasil ke petani                             | Perlu validasi                 |
| DBD-DEC-011 | Pihak penerbit faktur dalam setiap jalur transaksi         | Perlu validasi                 |
| DBD-DEC-012 | Pembayaran sebagian                                        | Di luar baseline wajib         |
| DBD-DEC-013 | Kebijakan retensi audit                                    | Perlu validasi                 |
| DBD-DEC-014 | Data PKS yang boleh dipublikasikan                         | Perlu validasi                 |
| DBD-DEC-015 | Kebutuhan GIS lanjutan/PostGIS                             | Opsional                       |

---

# 39. REFERENSI TEKNIS DAN DESAIN

## Database Engineering

- PostgreSQL Documentation: https://www.postgresql.org/docs/17/
- PostgreSQL Constraints: https://www.postgresql.org/docs/17/ddl-constraints.html
- PostgreSQL Indexes: https://www.postgresql.org/docs/17/indexes.html
- SQLAlchemy: https://docs.sqlalchemy.org/
- Alembic: https://alembic.sqlalchemy.org/
- Redis: https://redis.io/docs/

## UI/UX

- Laws of UX: https://lawsofux.com/laws/
- Golden Ratio and UI Design: https://www.nngroup.com/articles/golden-ratio-ui-design/
- Microinteractions: https://www.nngroup.com/articles/microinteractions/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Reduced Motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion

---

# 40. KESIMPULAN

Database Design Document V1.1 menetapkan rancangan basis data relasional untuk Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata, Unit Agro Niaga.

PostgreSQL digunakan sebagai database utama untuk menjamin integritas, keterlacakan, dan konsistensi transaksi.

Model database dipisahkan berdasarkan kepemilikan domain bisnis dengan tetap menggunakan satu database pada arsitektur Modular Monolith.

Rancangan mencakup identitas pengguna, master data petani dan PKS, informasi harga, penerimaan TBS, penimbangan, grading, kontrak, kuota, e-DO, tiket PKS, rekonsiliasi, faktur, pembayaran, dan audit.

Integritas data dilindungi menggunakan primary key, foreign key, unique constraint, check constraint, transaction management, kontrol concurrency, serta riwayat perubahan.

Redis digunakan untuk mempercepat akses data yang sesuai tanpa menggantikan PostgreSQL sebagai sumber kebenaran transaksi.

Bagian pendukung UI/UX menetapkan penggunaan 25 prinsip UX terpilih, golden ratio sebagai pedoman komposisi fleksibel, Atomic Design, dan micro-interactions yang relevan dengan tugas pengguna.

Desain UI/UX harus mengutamakan kemudahan penggunaan, keterbacaan, aksesibilitas, kecepatan, serta feedback yang benar terhadap status sistem.

Rancangan database dan kebutuhan antarmuka dalam dokumen ini menjadi dasar implementasi yang harus diselaraskan dengan aturan bisnis final dalam BSD.

**STATUS: DBD V1.1 — DATABASE & UX DATA ARCHITECTURE BASELINE**

**DOKUMEN SELANJUTNYA: BUSINESS SYSTEM DOCUMENT (BSD)**

**Akhir Dokumen — Database Design Document V1.1**

# 41. INCREMENTAL DATABASE BASELINE V1.1

Inventaris 48 nama pada Bagian 4 adalah kandidat model logis, bukan instruksi membuat 48 tabel pada migrasi pertama. Tabel dikerjakan bersama milestone modul pemiliknya. Integritas, auditability, dan keselamatan transaksi tetap wajib.

## 41.1 Core MVP Tables

Tabel inti untuk identitas dan alur demo minimum: `user_accounts`, `roles`, `permissions`, `role_permissions`, `user_role_grants`, `user_access_scopes`, `auth_sessions`; master aktor: `parties`, `farmers`, `farms`, `cooperatives`, `cooperative_memberships`, `mill_companies`, `mills`; harga: `price_sources`, `price_categories`, `mill_price_quotes`, `price_verification_events`; penerimaan: `tbs_receipts`, `receipt_weighing_revisions`, `receipt_grading_items`; kontrak/kuota/e-DO: `trade_contracts`, `contract_quota_periods`, `quota_reservations`, `delivery_orders`, `delivery_order_lines`, `delivery_status_events`; PKS/reconciliation/keuangan: `mill_weighing_tickets`, `mill_grading_items`, `reconciliation_cases`, `dispute_reviews`, `farmer_settlement_allocations`, `invoices`, `invoice_lines`, `payment_approvals`, `payment_records`; kontrol minimum: `audit_events`, `idempotency_records`.

Kelompok tersebut tetap dijadwalkan per dependensi, bukan satu migrasi besar. Jika prototipe mendemonstrasikan pembayaran, catat jenis arus masuk/keluar dan statusnya secara eksplisit tanpa menyamakan status pembayaran dengan timbang.

## 41.2 Supporting Tables Added by Milestone

Tambahkan sesuai fitur yang benar-benar dikerjakan: `perumda_offices`, `vehicles`, `drivers` (master/logistik); `disbun_reference_prices` (harga acuan); `file_assets` (lampiran dengan kontrol akses); `system_rule_versions` (snapshot versi aturan bila diperlukan untuk reproduksi historis); `outbox_events` (hanya bila integrasi/asinkron memerlukannya); `user_notifications` (notifikasi dalam aplikasi); `public_pages` dan `public_notices` (bila konten perlu dikelola dari aplikasi).

## 41.3 Deferred/Conditional

Tidak ada nama tabel dari inventaris 48 yang otomatis dibuang. Tabel pendukung di atas bersyarat terhadap scope. Integrasi eksternal, workflow notifikasi, outbox, konten CMS, dan storage tambahan ditunda sampai milestone terkait menetapkan use case dan acceptance criteria. Tinjau kandidat lain bersama pemilik modul bila tidak dibutuhkan MVP; perubahan harus memperbarui traceability dan memakai migrasi aman.

## 41.4 Migrasi dan Konsistensi Bisnis

- Buat migrasi Alembic bersama milestone data; jalankan upgrade dan integration test serta tinjau downgrade bila aman. Jangan membuat seluruh skema di awal.
- FK, unique/check constraints, indeks berbasis query, transaksi, dan concurrency control tetap wajib untuk aturan kritis.
- Harga transaksi, berat, grading, toleransi, dan versi rule yang dipakai disimpan sebagai snapshot/referensi immutable agar perubahan harga publik atau aturan baru tidak mengubah histori.
- Rekonsiliasi menyimpan kasus dan riwayat keputusan/ulangan. Alokasi multi-petani dapat ditelusuri ke penerimaan serta metode yang disahkan; formula simulasi bukan SOP.
- Pembayaran memiliki arah (masuk/keluar), pihak, referensi, nominal presisi finansial, verifikasi/approval dan status terpisah dari timbang. Tidak ada asumsi transfer otomatis.
- Idempotency dan constraint mencegah efek ganda; transaksi dan locking/strategi concurrency menjaga kuota serta alokasi.

## 41.5 Batas Panduan UI

Data UI mendukung loading, empty, error, success, validasi, dan aksesibilitas. Atomic Design lima level, 25 prinsip UX, golden ratio fleksibel, dan micro-interactions dijelaskan pada TRD sebagai pedoman visual. DBD menetapkan kebutuhan data dan tidak menduplikasi panduan UI.
