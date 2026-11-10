# ADR-005: Server-Side Session Cookie, CSRF, RBAC & Scope Isolation

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `TRD §12–13`, `DBD §6`, `BSD §4–5`, `AFD §7`

## Konteks
Portal Publik harus terbuka anonim, sedangkan Portal Internal menangani data pribadi petani, harga kontrak, timbangan, dan persetujuan pembayaran lintas organisasi (Petani, Koperasi, Perumda, PKS, Direksi, Admin).

## Keputusan
1. **Session Cookie:** Autentikasi memakai server-side session (`auth_sessions`, token ter-hash di DB) dengan cookie `ts_agroniaga_session` bertanda `HttpOnly`, `Secure` (HTTPS), `SameSite=Lax`. Token mentah tidak pernah disimpan di `localStorage` atau payload JSON `/auth/login`.
2. **CSRF:** Setiap mutasi terautentikasi (`POST/PATCH/PUT/DELETE` selain `/auth/login`) wajib menyertakan header `X-CSRF-Token` yang diambil dari `GET /api/v1/auth/csrf` dan divalidasi terikat ke sesi aktif.
3. **Password:** Hash Argon2id; login gagal selalu mengembalikan pesan generik `AUTH_INVALID_CREDENTIALS` (`"Username atau kata sandi tidak sesuai."`) agar tidak membocorkan status registrasi akun.
4. **RBAC + Resource Scope + Separation of Duties:** Otorisasi default-deny di server memvalidasi izin granular + cakupan data (`FARMER`, `COOPERATIVE`, `MILL`, `PERUMDA_GLOBAL`) + larangan `Maker == Checker` + larangan Administrator menyetujui operasi transaksi (`BR-SYS-002`).

## Konsekuensi
- **Positif:** Perlindungan berlapis terhadap XSS token theft, CSRF, IDOR lintas koperasi/petani/PKS, dan eskalasi kewenangan admin.
