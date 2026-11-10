# ADR-003: PostgreSQL sebagai Single Source of Truth

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `TRD §10`, `DBD §1.3, §18–21`, `IPD §5.5`

## Konteks
Rantai pasok TBS menuntut integritas referensial ketat, pembukuan nilai uang/berat bebas galat floating point, riwayat revisi tak terhapus, serta pencegahan alokasi ganda maupun over-quota secara konkuren.

## Keputusan
**PostgreSQL 17+** ditetapkan sebagai satu-satunya *source of truth* transaksional menggunakan SQLAlchemy 2.x Async + Alembic (single migration owner di Backend Track). Invariant kritis ditopang oleh `CHECK` constraints (`tare <= gross`), generated column `net_weight_kg`, dan partial unique indexes (`ux_receipt_current_weighing`, `ux_active_receipt_allocation`, `ux_current_mill_ticket`, `ux_current_reconciliation`). Snapshot historis transaksi (`origin_weight_snapshot_kg`, harga kontrak, `rule_version_id`) wajib disimpan agar perubahan master data di masa depan tidak merusak catatan historis.

## Konsekuensi
- **Positif:** Konsistensi ACID penuh, riwayat audit tidak terhapus fisik, perlindungan terhadap race condition melalui row locking dan constraint DB.
- **Kewajiban:** Skema API tidak pernah mengasumsikan Redis menyimpan satu-satunya salinan transaksi atau hasil keputusan finansial.
