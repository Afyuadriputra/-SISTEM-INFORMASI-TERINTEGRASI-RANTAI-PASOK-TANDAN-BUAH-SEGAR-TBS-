# ADR-001: Arsitektur Backend Modular Monolith

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `TRD §2.2, §7`, `DBD §2.1–2.3`, `IPD §9.1`

## Konteks
Sistem mengintegrasikan Portal Publik dan proses perdagangan TBS multi-aktor dalam lingkup proyek tesis dengan satu pengembang utama dan opsi agent paralel. Pemecahan langsung menjadi microservices menimbulkan overhead jaringan, transaksi terdistribusi, dan deployment tanpa kebutuhan skala yang sebanding.

## Keputusan
Backend dibangun sebagai **satu unit deploy FastAPI Modular Monolith** dengan cakupan hingga 11 modul domain kanonis (`identity_access`, `public_portal`, `master_data`, `pricing`, `tbs_receiving`, `contracts`, `logistics`, `mill_weighing`, `reconciliation`, `reporting`, `audit`) plus shared `core/`. Modul domain dibuat **secara inkremental sesuai milestone IPD (`B1`..`B10`)** tanpa membuat puluhan folder modul/subfolder kosong di milestone fondasi `B0` (`TRD §5.1, §6`). Setiap modul yang diimplementasikan menjaga batas kepemilikan tabel secara ketat, dengan koordinasi lintas modul melalui port aplikasi terdefinisi.

## Konsekuensi
- **Positif:** Transaksi atomik SQL lintas modul (mis. penerbitan e-DO + reservasi kuota + update status penerimaan + audit) berjalan dalam satu unit commit PostgreSQL; operasional dan testing sederhana.
- **Kewajiban:** Disiplin batas impor antar-modul wajib ditegakkan di CI (`Import Linter` / architecture tests) mulai milestone `B0`.
