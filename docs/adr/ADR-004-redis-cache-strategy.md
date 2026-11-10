# ADR-004: Strategi Caching Redis Cache-Aside & Fail-Closed Security

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `TRD §11`, `DBD §24`, `AFD §5.7`, `BSD BIZ-028`

## Konteks
Portal Publik (`/api/v1/public/*`) berpotensi diakses berulang tanpa autentikasi, sementara operasi kritikal kuota, rekonsiliasi, dan pembayaran menuntut konsistensi real-time terhadap PostgreSQL.

## Keputusan
Redis wajib tersedia sejak `B0`, dipakai dengan pola **cache-aside** hanya pada use case baca yang relevan:
- **Public Read Cache:** Harga TBS publik aktif (TTL awal 30–60 dtk), direktori PKS publik (5–15 mnt), profil perusahaan (15 mnt). Key berversioning tanpa PII (`public:prices:v1:region:{region}`).
- **Internal Read Cache:** Agregasi dashboard ber-scope (`dashboard:v1:scope:{scope}:period:{period}`, TTL 15–60 dtk), wajib isolasi antar-scope.
- **Dilarang Dipercaya sebagai Source of Truth:** Sisa kuota reservasi, validasi konflik alokasi, keputusan rekonsiliasi, status faktur/approval/settlement final.
- **Invalidasi:** Hanya dieksekusi backend **setelah database commit** berhasil (`FLOW-06`, `FLOW-07`).
- **Degradasi:** Read cache nonkritis boleh fallback ke PostgreSQL secara terkontrol; komponen keamanan (`auth_sessions`, `rate_limit`) bersifat **fail-closed**.

## Konsekuensi
- **Positif:** Portal publik responsif tanpa membebani PostgreSQL dan bebas kebocoran data lintas scope atau kegagalan otorisasi saat Redis terganggu.
