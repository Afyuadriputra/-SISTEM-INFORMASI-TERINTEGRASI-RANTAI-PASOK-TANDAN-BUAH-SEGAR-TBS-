# ADR-009: Transport Desimal String, Identifier UUID & Konvensi UTC/WIB

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `DBD §3.2–3.5`, `TRD §10.3`, `IPD §4.4`, `task2.md §9.4–9.6`

## Konteks
Perhitungan berat timbang (`kg`), harga per kg (`Rp/kg`), nominal faktur/pembayaran, dan persentase selisih rekonsiliasi tidak boleh terkena galat pembulatan binary `float` IEEE-754 di Python atau JavaScript.

## Keputusan
1. **Transport Desimal String Eksplisit:** Seluruh angka presisi di OpenAPI & JSON fixtures bertipe `type: string` dengan pola regex & presisi tepat sesuai `DBD §3.3`:
   - Berat (`kg`): `NUMERIC(14,3)` -> `DecimalKgString` (`^-?\d{1,11}\.\d{3}$` atau non-negatif `^\d{1,11}\.\d{3}$`).
   - Harga (`Rp/kg`): `NUMERIC(18,2)` -> `DecimalPriceString` (`^\d{1,16}\.\d{2}$`).
   - Nominal Uang (`IDR`): `NUMERIC(20,2)` -> `DecimalMoneyString` (`^-?\d{1,18}\.\d{2}$`).
   - Persentase (`%`): `NUMERIC(9,4)` -> `DecimalPercentString` (`^-?\d{1,5}\.\d{4}$`).
   - Luas Kebun (`ha`): `NUMERIC(12,4)` -> `DecimalAreaString` (`^\d{1,8}\.\d{4}$`).
   - Koordinat (`lat/lng`): `NUMERIC(9,6)` -> `DecimalLatString` / `DecimalLngString` (`-90..90`, `-180..180`).
2. **Tanpa Simbol Mata Uang di Payload Kalkulasi:** Backend tidak pernah mengirim `"Rp2.850"`; frontend bertanggung jawab atas format `Intl.NumberFormat('id-ID')` dan `tabular-nums`.
3. **Identifier & Timestamp:** Seluruh primary/foreign ID menggunakan string `uuid` (`format: uuid`); seluruh instant waktu menggunakan RFC 3339 / ISO 8601 UTC (`format: date-time` berakhiran `Z`), sedangkan tanggal kalender transaksi memakai `format: date` (`YYYY-MM-DD`). Konversi ke `WIB (Asia/Jakarta, UTC+7)` dilakukan konsisten di layer tampilan UI.

## Konsekuensi
- **Positif:** Nol selisih pembulatan lintas Python `Decimal` -> PostgreSQL `NUMERIC` -> JSON -> TypeScript `string`, serta aman dari pergeseran tanggal antar-zona waktu.
