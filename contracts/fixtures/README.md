# Shared Test & MSW Fixtures — AgroNiaga TBS (M0-V1.1)

Seluruh berkas JSON di direktori ini merupakan **data simulasi deterministik** untuk pengujian bersama **Backend FastAPI (`pytest`)** dan **Frontend React (`MSW` / `Vitest` / `Playwright`)**.

## Aturan Ketat Fixture (`task2.md §14`)
1. **Tanpa Data Pribadi Nyata / Secret:** Tidak ada NIK asli, rekening bank asli, nomor HP pribadi warga nyata, token sesi mentah, atau password produksi.
2. **UUID & Presisi Numerik:** Seluruh `id` berformat UUID v4 deterministik (`10000000-...` s.d. `a0000000-...`); berat (`kg`) 3 desimal string, harga & uang 2 desimal string, persentase & luas 4 desimal string (`ADR-009`).
3. **Timestamp UTC:** Seluruh waktu instan berakhiran `Z` (ISO 8601 UTC); tanggal bisnis memakai `YYYY-MM-DD`.
4. **Klasifikasi Kebijakan:** Skenario berbasis nilai sementara (`toleransi 1,5000%`, `grading 2,0000%`, `alokasi proporsional 30/20/50%`, `kontrak PRINCIPAL/AGENT contoh`) diberi penanda eksplisit `SIMULATION_ONLY` atau `PENDING_SOP` dan dilarang diperlakukan sebagai SOP resmi Perumda Tuah Sekata.

## Peta Blok UUID Deterministik
- `10000000-0000-4000-8000-0000000000xx`: User Accounts & Access Scopes & Parties
- `20000000-0000-4000-8000-0000000000xx`: Price Sources, Categories, PKS Quotes, & Disbun References
- `30000000-0000-4000-8000-0000000000xx`: Mill Companies, Mills, Perumda Offices, Public Notices
- `40000000-0000-4000-8000-0000000000xx`: Cooperatives, Farmers, Farms, Vehicles, Drivers
- `50000000-0000-4000-8000-0000000000xx`: TBS Receipts, Weighing Revisions, Grading Items
- `60000000-0000-4000-8000-0000000000xx`: Trade Contracts, Quota Periods, Quota Reservations
- `70000000-0000-4000-8000-0000000000xx`: Delivery Orders (e-DO), Lines, Status Events
- `80000000-0000-4000-8000-0000000000xx`: Mill Weighing Tickets & Mill Grading
- `90000000-0000-4000-8000-0000000000xx`: System Rule Versions, Reconciliation Cases, Dispute Reviews, Allocations
- `a0000000-0000-4000-8000-0000000000xx`: Invoices, Invoice Lines, Payment Approvals, Payment Records, File Assets
- `b0000000-0000-4000-8000-0000000000xx`: Sample Audit Events
