# ADR-010: Idempotency-Key, Concurrency Locking & Pending SOP Guards

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `BSD §27`, `DBD §16.3, §21`, `AFD §38, §41`, `task2.md §15 & §20`

## Konteks
Pengiriman lapangan dengan koneksi tidak stabil rentan memicu retry/double-click pada penerbitan e-DO, tiket PKS, rekonsiliasi, serta persetujuan/pencatatan pembayaran; sementara sejumlah kebijakan bisnis Perumda (`AFD §41`, `BSD §35`) masih menunggu pengesahan resmi.

## Keputusan
1. **Idempotency-Key Contract:** Seluruh **8 operasi mutasi kritis** (mencakup 7 kategori operasi kritis `BSD §27.2`, di mana modul Rekonsiliasi memiliki operasi trigger awal maupun eksekusi pencocokan ulang: `createReceiptDraft` [`POST /receipts`], `reserveContractQuota` [`POST /contracts/{contract_id}/reservations`], `issueDeliveryOrder` [`POST /delivery-orders/{delivery_order_id}/issue`], `createMillTicket` [`POST /mill-tickets`], `createOrTriggerReconciliation` [`POST /reconciliations`], `calculateReconciliation` [`POST /reconciliations/{reconciliation_id}/calculate`], `approveOrRejectInvoicePayment` [`POST /payments/{id}/approve`], dan `recordPaymentEvidence` [`POST /payments`]) mewajibkan header `Idempotency-Key` (string unik per permintaan klien, maks 128 karakter), diikat di server dengan scope `(actor_id, operation_key, idempotency_key)` + hash payload:
   - Key sama + payload identik -> mengembalikan hasil commit asli tanpa efek ganda.
   - Key sama + payload berbeda -> ditolak HTTP `409 Conflict` (`IDM_KEY_CONFLICT_PAYLOAD_MISMATCH`).
   - Retensi kunci ditetapkan saat implementasi `B0/B4` mengikuti kebijakan retensi `BSD-DEC-020` (*tidak dikarang angka retensi final di M0*).
2. **Optimistic Concurrency Token (`version`):** Entitas master dan transaksional yang dapat diedit menyertakan integer `version` (`If-Match` atau body `version`), menolak update usang dengan `409` (`*_STALE_RECORD_VERSION`). Reservasi kuota & penguncian alokasi muatan wajib memakai transaksi SQL + row-level lock / partial unique index di PostgreSQL.
3. **Explicit Pending SOP / Simulation Guard:** Field/endpoint yang bergantung pada kebijakan belum disahkan menyertakan metadata `policy_classification` (`CONFIRMED | SIMULATION_ONLY | PENDING_SOP | FUTURE`) dan `simulation_label`, serta menahan finalisasi finansial otomatis bila `business_model_code == "UNCONFIRMED"`.

## Konsekuensi
- **Positif:** Antarmuka lapangan & backend bebas transaksi ganda, konflik edit konkuren terdeteksi eksplisit, dan kebijakan simulasi tidak akan pernah tersamar sebagai SOP resmi Perumda.
