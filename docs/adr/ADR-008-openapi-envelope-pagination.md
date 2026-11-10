# ADR-008: Standar Kontrak OpenAPI 3.1.0, Envelope Response & Pagination

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `TRD §16`, `IPD §4.1–4.3, §7.1`

## Konteks
Backend FastAPI dan frontend React (`openapi-typescript` + MSW) memerlukan kontrak tunggal yang prediktabel, bebas nested generic envelope yang menyulitkan codegen TypeScript, serta memiliki paginasi yang seragam untuk daftar transaksi besar.

## Keputusan
1. **Format:** OpenAPI `3.1.0` kanonis dalam berkas tunggal [openapi.v1.yaml](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/contracts/openapi.v1.yaml) dengan prefix API `/api/v1` (dan health probes `/health/live`, `/health/ready`).
2. **Response Envelope:** Menggunakan komponen standar datar `request_id` + `success`:
   - Sukses: `{ "success": true, "data": <Schema>, "meta": <PaginationMeta | ResponseMeta | null>, "request_id": "<RequestId>" }`.
   - Gagal: `{ "success": false, "error": { "code": "<ERROR_CODE>", "message": "<ID message>", "details": <object | null> }, "request_id": "<RequestId>" }`.
3. **Pagination Baseline:** Menggunakan **offset/page pagination** deterministik (`page >= 1`, `page_size` default `20`, maksimum `100`, plus `sort_by` & `sort_dir` whitelist + tie-breaker deterministik `id` di server) dengan `PaginationMeta { page, page_size, total_items, total_pages, has_next, has_prev }` sebagai satu pola seragam (`task2.md §9.7` melarang pencampuran offset & cursor secara ambigu). Daftar audit atau event dapat tetap memakai model yang sama + index komposit waktu/id agar antarmuka konsisten.

## Konsekuensi
- **Positif:** `openapi-typescript` menghasilkan tipe deterministik untuk setiap endpoint tanpa ambiguitas envelope atau campuran cursor/offset.
