# ADR-002: Clean Architecture Empat Layer per Modul & SOLID Pragmatis

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `TRD §5, §8`, `BSD §31`, `IPD §9.1–9.4`

## Konteks
Aturan bisnis seperti kalkulasi berat netto, reservasi kuota, selisih rekonsiliasi, dan pemeriksaan pemisahan tugas mudah bocor ke router FastAPI atau komponen UI jika tidak diisolasi sejak awal.

## Keputusan
Setiap modul domain yang diimplementasikan wajib memiliki empat layer (dibuat bertahap mengikuti kebutuhan nyata modul pada milestone IPD tanpa subfolder kosong `TRD §5.1`):
1. `domain/` — entity, value object, policy, invariant murni (bebas dependency terhadap `infrastructure/`, `presentation/`, FastAPI, SQLAlchemy, maupun Redis).
2. `application/` — koordinasi use case, otorisasi konteks, transaksi, serta antarmuka/port repository atau layanan yang diperlukan (bergantung pada `domain/` dan port, bukan implementasi adapter konkret).
3. `infrastructure/` — repository SQLAlchemy, Redis adapter, file storage adapter yang mengimplementasikan port dari layer dalam.
4. `presentation/` — router HTTP `/api/v1`, Pydantic schemas, validasi protokol, dan pemetaan ke `ErrorResponse` dengan memanggil `application/` use cases.

Arah dependency dan wiring (`TRD §5.3`, `IPD §9.2`): **Domain tidak bergantung pada Infrastructure atau layer luar; Application bergantung pada Domain & port; Infrastructure mengimplementasikan port; Presentation memanggil Application; wiring adapter konkret ke composition root dilakukan eksplisit (mis. melalui FastAPI `Depends` tanpa container DI kompleks).** Prinsip SOLID diterapkan secara pragmatis tanpa abstraksi/hierarki kosong.

## Konsekuensi
- **Positif:** Aturan domain (`BSD`) dapat diuji lewat unit test cepat tanpa server HTTP atau database aktif; kontrak OpenAPI tetap bersih dari detail ORM.
- **Kewajiban:** Kontrak API tidak boleh memaksa endpoint HTTP menggabungkan transaksi antar-domain menjadi route monolitik tanpa use case yang jelas.
