# ADR-007: Pemisahan Structured Access/Security Logs & Business Audit Trail

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `TRD §14`, `DBD §16.2`, `BSD §28`, `AFD §34`

## Konteks
Investigasi kendala teknis (CCTV Digital via `request_id`) dan penelusuran keputusan bisnis bernilai uang (verifikasi harga, revisi timbang, dispute, persetujuan pembayaran) memiliki kebutuhan privasi, skema, dan akses yang berbeda.

## Keputusan
1. Memisahkan **tiga jalur pencatatan**: Access Logging (`http_request_completed` dengan `request_id` & `trace_id`), Security Event Logging (login gagal, `403`, privilege change), dan **Business Audit Trail** (`audit_events`, bersifat *append-only* pada jalur aplikasi dengan `previous_state`, `new_state`, `reason`, `request_id`).
2. Setiap response API menyertakan `request_id` di JSON body dan header `X-Request-ID`. Stack trace internal tidak pernah dikembalikan ke client.
3. Log dan audit wajib menyaring/meredaksi password, token sesi, cookie, token CSRF, dan nomor rekening bank. Retensi log dan audit tidak boleh tanpa batas (*infinite retention forbidden*), angka periode retensi menunggu penetapan `BSD-DEC-020`.

## Konsekuensi
- **Positif:** Error produksi/simulasi dapat dikorelasikan instan dari layar error (`req_...`) ke CCTV Digital Administrator tanpa membocorkan secrets.
