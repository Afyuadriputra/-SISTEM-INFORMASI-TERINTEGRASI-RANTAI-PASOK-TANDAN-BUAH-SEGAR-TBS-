
# TECHNICAL REQUIREMENTS DOCUMENT (TRD)

## SISTEM INFORMASI TERINTEGRASI RANTAI PASOK TANDAN BUAH SEGAR (TBS)

### PERUMDA TUAH SEKATA — UNIT AGRO NIAGA

**Versi:** 1.1 — Technical Architecture Baseline
**Tanggal:** 10 November 2026
**Status:** Draft Rancangan Teknis
**Dokumen Induk:** PRD V1.1
**Pendekatan Arsitektur:** Modular Monolith + Clean Architecture
**Backend:** Python, FastAPI, PostgreSQL, Redis
**Frontend:** React, TypeScript, Vite, Tailwind CSS
**Frontend Architecture:** Atomic Design (5 Levels)
**Metodologi Penelitian:** Design Science Research Methodology (DSRM)

---

# 1. PENDAHULUAN

## 1.1 Tujuan Dokumen

Technical Requirements Document (TRD) menjabarkan kebutuhan teknis untuk pengembangan Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata.

Dokumen ini menetapkan:

1. Arsitektur sistem secara keseluruhan.
2. Pemisahan backend berdasarkan modul bisnis.
3. Standar empat layer untuk setiap modul backend.
4. Prinsip SOLID dan standar kualitas kode.
5. Strategi optimasi performa backend.
6. Perancangan database dan integritas transaksi.
7. Strategi caching menggunakan Redis.
8. Keamanan autentikasi, otorisasi, dan perlindungan data.
9. Middleware observabilitas dan pemantauan aktivitas.
10. Standar logging dan penanganan error.
11. Arsitektur frontend Atomic Design.
12. Pengelolaan state, routing, dan komunikasi API.
13. Library serta tooling yang digunakan.
14. Strategi pengujian, deployment, dan monitoring.
15. Kriteria penerimaan teknis sebelum sistem dinyatakan siap digunakan untuk evaluasi tesis.

Dokumen ini merupakan spesifikasi rancangan teknis. Pemenuhan target performa dan keamanan tetap harus dibuktikan melalui implementasi serta pengujian.

## 1.2 Ruang Lingkup

Pengembangan berfokus pada Unit Agro Niaga Perumda Tuah Sekata.

Sistem meliputi Portal Publik tanpa login dan Portal Internal dengan autentikasi, serta delapan modul utama:

1. Master Data Aktor dan Profil Kebun.
2. Monitoring dan Manajemen Harga TBS Multi-PKS.
3. Penerimaan, Penimbangan, dan Grading TBS.
4. Kontrak Niaga dan Alokasi Kuota.
5. Logistik dan Surat Jalan Elektronik.
6. Tiket Timbang Pabrik.
7. Rekonsiliasi dan Pembayaran.
8. Dashboard Eksekutif dan Analitik.

Selain delapan modul tersebut, sistem membutuhkan modul pendukung platform, seperti Identity and Access Management, Public Portal, Audit, dan Observability.

Modul pendukung bukan penambahan cakupan bisnis penelitian, melainkan kebutuhan teknis untuk menjalankan sistem dengan aman.

---

# 2. PRINSIP ARSITEKTUR DAN REKAYASA PERANGKAT LUNAK

## 2.1 Prinsip Utama

Sistem wajib dirancang menggunakan prinsip berikut:

**TR-ARCH-001 — Modular Architecture**

Setiap domain bisnis memiliki modul tersendiri dengan batas tanggung jawab yang jelas.

**TR-ARCH-002 — Clean Architecture**

Aturan bisnis tidak boleh bergantung langsung pada framework, database, atau antarmuka pengguna.

**TR-ARCH-003 — SOLID Principles**

Komponen harus mengikuti Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, dan Dependency Inversion.

**TR-ARCH-004 — Dependency Injection**

Dependensi service, repository, dan komponen eksternal disediakan melalui mekanisme Dependency Injection.

**TR-ARCH-005 — Separation of Concerns**

Logika HTTP, validasi aturan bisnis, pengelolaan data, dan integrasi eksternal harus dipisahkan.

**TR-ARCH-006 — Secure by Default**

Akses internal ditolak secara default apabila pengguna tidak memiliki izin eksplisit.

**TR-ARCH-007 — Performance by Design**

Efisiensi query, pemakaian memori, caching, dan penanganan concurrency menjadi bagian dari proses desain.

**TR-ARCH-008 — Observable by Design**

Aktivitas penting, kegagalan sistem, dan masalah performa harus dapat ditelusuri melalui logging, metrics, dan tracing.

**TR-ARCH-009 — Testability**

Logika bisnis harus dapat diuji tanpa memerlukan server HTTP atau database yang selalu berjalan.

**TR-ARCH-010 — Maintainability**

Perubahan pada satu modul diupayakan tidak memaksa perubahan pada modul lain selama kontrak publiknya tetap berlaku.

## 2.2 Keputusan Arsitektur

Arsitektur yang dipilih adalah **Modular Monolith**.

Seluruh modul berjalan dalam satu backend yang dapat dideploy sebagai satu aplikasi, tetapi implementasinya dipisahkan berdasarkan batas domain.

Alasan pemilihan:

- Lebih realistis untuk lingkup pengembangan tesis.
- Memudahkan pengembangan dan debugging.
- Mengurangi kompleksitas komunikasi antarservice.
- Mendukung transaksi database lintas modul yang konsisten.
- Mengurangi kebutuhan infrastruktur.
- Memudahkan pengujian.
- Menyediakan jalur pemisahan menjadi service mandiri apabila diperlukan pada masa depan.

Microservices tidak digunakan pada baseline karena kompleksitas operasionalnya belum memberikan manfaat yang sebanding dengan kebutuhan penelitian.

---

# 3. TECHNOLOGY STACK

## 3.1 Backend Stack

| Komponen               | Teknologi/Library | Fungsi                                      |
| ---------------------- | ----------------- | ------------------------------------------- |
| Bahasa                 | Python 3.12+      | Bahasa utama backend                        |
| Framework API          | FastAPI           | REST API dan dependency injection           |
| ASGI Server            | Uvicorn           | Menjalankan aplikasi ASGI                   |
| Validasi Data          | Pydantic          | Validasi request, response, dan konfigurasi |
| ORM                    | SQLAlchemy 2.x    | Akses data dan pemetaan objek relasional    |
| Database Driver        | asyncpg           | Koneksi PostgreSQL asynchronous             |
| Migrasi Database       | Alembic           | Migrasi skema database                      |
| Database               | PostgreSQL 17+    | Penyimpanan data transaksi                  |
| Cache                  | Redis             | Cache, rate-limit state, dan data sementara |
| Redis Client           | redis-py          | Komunikasi dengan Redis                     |
| HTTP Client            | HTTPX             | Integrasi API pihak ketiga                  |
| Password Hashing       | argon2-cffi       | Hash password Argon2id                      |
| Structured Logging     | structlog         | Logging terstruktur                         |
| Tracing                | OpenTelemetry     | Distributed tracing dan instrumentasi       |
| Metrics                | prometheus-client | Pengukuran metrik operasional               |
| QR Code                | Segno             | Pembuatan QR Code e-DO                      |
| Pengujian              | pytest            | Framework pengujian                         |
| Async Testing          | pytest-asyncio    | Pengujian fungsi asynchronous               |
| Coverage               | pytest-cov        | Cakupan pengujian                           |
| Property-Based Testing | Hypothesis        | Pengujian properti aturan bisnis            |
| Lint & Formatting      | Ruff              | Pemeriksaan gaya dan kualitas kode          |
| Static Type Checking   | Pyright           | Pemeriksaan tipe statis                     |
| Dependency Management  | uv                | Instalasi dan penguncian dependensi         |

Versi final dependency wajib dikunci dalam lockfile setelah pemeriksaan kompatibilitas.

Library tidak boleh otomatis menggunakan versi terbaru di production tanpa melalui pengujian.

## 3.2 Frontend Stack

| Komponen              | Teknologi/Library     | Fungsi                                 |
| --------------------- | --------------------- | -------------------------------------- |
| Bahasa                | TypeScript            | Type safety frontend                   |
| UI Framework          | React 19              | Pengembangan antarmuka                 |
| Build Tool            | Vite                  | Development server dan build           |
| Styling               | Tailwind CSS 4        | Sistem styling                         |
| UI Foundation         | shadcn/ui             | Komponen UI yang dapat dikustomisasi   |
| Accessible Primitives | Radix UI              | Komponen interaksi aksesibel           |
| Routing               | TanStack Router       | Routing dan navigasi bertipe           |
| Server State          | TanStack Query        | Fetching, cache, dan sinkronisasi data |
| Client State          | Zustand               | State antarmuka lintas komponen        |
| Forms                 | React Hook Form       | Pengelolaan formulir                   |
| Validation            | Zod                   | Validasi skema input                   |
| Form Resolver         | @hookform/resolvers   | Integrasi Zod dengan formulir          |
| Tables                | TanStack Table        | Tabel dengan filter dan pagination     |
| Charts                | Recharts              | Visualisasi data                       |
| Maps                  | MapLibre GL JS        | Visualisasi lokasi perusahaan          |
| Icons                 | Lucide React          | Ikon antarmuka                         |
| Date Utilities        | date-fns              | Pengelolaan tanggal                    |
| Notifications         | Sonner                | Toast dan notifikasi UI                |
| Unit Testing          | Vitest                | Pengujian unit                         |
| Component Testing     | React Testing Library | Pengujian komponen                     |
| Browser Testing       | Playwright            | End-to-end testing                     |
| Accessibility Testing | axe-core              | Pemeriksaan aksesibilitas              |
| Code Quality          | ESLint                | Pemeriksaan kode                       |
| Formatting            | Prettier              | Konsistensi format                     |

Library hanya digunakan sesuai kebutuhan. Tidak diperbolehkan memasang beberapa library yang menjalankan fungsi sama tanpa alasan teknis.

## 3.3 Infrastruktur

| Komponen             | Pilihan             | Prioritas                        |
| -------------------- | ------------------- | -------------------------------- |
| Container            | Docker              | Wajib                            |
| Local Orchestration  | Docker Compose      | Wajib                            |
| Reverse Proxy        | Caddy atau Nginx    | Wajib untuk deployment           |
| Cache Service        | Redis               | Wajib                            |
| Database Service     | PostgreSQL          | Wajib                            |
| Metrics              | Prometheus          | Dianjurkan                       |
| Monitoring Dashboard | Grafana             | Dianjurkan                       |
| Centralized Logs     | Grafana Loki        | Dianjurkan                       |
| Tracing Backend      | Tempo atau Jaeger   | Opsional                         |
| Object Storage       | S3-compatible/MinIO | Opsional sesuai kebutuhan berkas |
| CI                   | GitHub Actions      | Dianjurkan                       |

Observability tingkat lanjut dapat diaktifkan bertahap tanpa mengubah logika bisnis.

---

# 4. ARSITEKTUR SISTEM KESELURUHAN

## 4.1 Komponen Utama

Sistem terdiri dari:

**Client Layer**

- Browser pengguna publik.
- Browser petani.
- Browser koperasi.
- Browser staf Perumda.
- Browser petugas PKS.
- Browser Direksi.

**Frontend Application**

- Portal Publik.
- Portal Internal.
- Atomic Design Component System.
- API Client.
- State Management.
- Routing.

**Backend Application**

- Global middleware.
- Authentication and Authorization.
- API Router.
- Application Use Cases.
- Domain Business Rules.
- Repository Implementation.
- Integration Adapters.

**Data and Infrastructure**

- PostgreSQL.
- Redis.
- Penyimpanan dokumen jika diperlukan.
- Sistem logging dan monitoring.

## 4.2 Alur Komunikasi

Browser pengguna mengakses frontend melalui HTTPS.

Frontend mengirim request ke REST API.

Request melewati middleware keamanan dan observabilitas sebelum mencapai endpoint.

Endpoint meneruskan operasi kepada Application Layer.

Application Layer mengoordinasikan Domain Layer dan port repository/integrasi.

Infrastructure Layer menjalankan penyimpanan atau pemanggilan layanan eksternal.

Hasil diproses kembali menjadi response melalui API.

Aktivitas teknis yang relevan dicatat dalam logging dan tracing, sedangkan tindakan bisnis penting disimpan dalam audit trail.

## 4.3 Pola Deployment

Pada baseline, sistem dapat berjalan dengan komponen:

- Satu frontend web.
- Satu aplikasi backend FastAPI.
- Satu PostgreSQL.
- Satu Redis.
- Satu reverse proxy.

Observability services dapat ditambahkan sesuai lingkungan dan sumber daya.

Tidak diperlukan Kubernetes pada tahap tesis.

---

# 5. BACKEND MODULAR ARCHITECTURE

## 5.1 Ketentuan Utama

**Setiap modul backend wajib memiliki empat layer.**

Layer tersebut adalah:

1. Domain Layer.
2. Application Layer.
3. Infrastructure Layer.
4. Presentation Layer.

Tidak diperbolehkan menempatkan seluruh business logic dalam satu folder service global.

Tidak diperbolehkan menempatkan seluruh implementasi database dalam satu repository global yang mencampur semua domain.

## 5.2 Domain Layer

Domain Layer memuat aturan bisnis inti.

Komponen:

- Entities.
- Value Objects.
- Domain Services.
- Business Rules.
- Domain Events.
- Domain Exceptions.
- Repository Port/Interface.

Contoh tanggung jawab:

- Menghitung persentase selisih berat.
- Memastikan nilai timbangan valid.
- Menentukan apakah transaksi memerlukan pemeriksaan.
- Memastikan status bisnis dapat berubah sesuai aturan.

Domain Layer tidak boleh mengimpor FastAPI, SQLAlchemy ORM, Redis, atau komponen frontend.

Domain Layer harus dapat diuji menggunakan Python biasa.

## 5.3 Application Layer

Application Layer mengatur pelaksanaan use case.

Komponen:

- Commands.
- Queries.
- Use Case Handlers.
- Application Services.
- DTO.
- Transaction Orchestration.
- Application Ports.

Contoh:

- CreateTbsReceipt.
- PublishMillPrice.
- CreateDeliveryOrder.
- RegisterMillTicket.
- ReconcileWeighing.
- ApprovePayment.

Application Layer berfungsi sebagai penghubung antara HTTP/API dengan aturan bisnis.

Layer ini mengatur urutan pekerjaan, hak akses kontekstual, dan unit transaksi melalui abstraksi.

Application Layer tidak boleh menyusun SQL mentah atau bergantung langsung pada implementasi router FastAPI.

## 5.4 Infrastructure Layer

Infrastructure Layer mengimplementasikan kebutuhan teknis.

Komponen:

- ORM Models.
- Repository Implementations.
- Database Mappers.
- External API Clients.
- Cache Adapters.
- File Storage Adapters.
- Event Publishers.
- External Service Integrations.

Contoh:

- SqlAlchemyPriceRepository.
- PostgresWeighingRepository.
- RedisPublicPriceCache.
- MillApiClient.
- FileTicketStorage.

Infrastructure Layer boleh menggunakan SQLAlchemy, Redis, HTTPX, dan library teknis lainnya.

Infrastructure Layer mengimplementasikan interface yang didefinisikan pada layer dalam.

## 5.5 Presentation Layer

Presentation Layer bertanggung jawab terhadap komunikasi aplikasi dengan dunia luar.

Komponen:

- API Routes.
- Request Schemas.
- Response Schemas.
- HTTP Dependencies.
- Endpoint Validation.
- Response Mapping.

Contoh endpoint:

- GET /api/v1/public/prices
- GET /api/v1/public/mills
- POST /api/v1/receipts
- POST /api/v1/delivery-orders
- POST /api/v1/reconciliations

Presentation Layer tidak boleh menghitung aturan bisnis inti.

Endpoint harus tetap tipis dan hanya mengatur penerimaan request, pemanggilan use case, serta pengembalian response.

## 5.6 Aturan Dependency

Arah dependency logis:

- Presentation → Application.
- Application → Domain.
- Infrastructure → Domain/Application Ports.
- Domain → Tidak bergantung pada layer luar.

Implementasi konkret dihubungkan melalui Dependency Injection pada composition root.

Application Layer tidak boleh mengimpor Infrastructure Implementation secara langsung.

---

# 6. STRUKTUR FOLDER BACKEND

Struktur repositori yang direkomendasikan:

```text
backend/
├── app/
│   ├── main.py
│   ├── bootstrap/
│   │   ├── app_factory.py
│   │   ├── dependency_container.py
│   │   └── router_registry.py
│   │
│   ├── core/
│   │   ├── config/
│   │   ├── security/
│   │   ├── middleware/
│   │   ├── logging/
│   │   ├── observability/
│   │   ├── database/
│   │   ├── cache/
│   │   ├── errors/
│   │   └── shared/
│   │
│   ├── modules/
│   │   ├── identity_access/
│   │   ├── public_portal/
│   │   ├── master_data/
│   │   ├── pricing/
│   │   ├── tbs_receiving/
│   │   ├── contracts/
│   │   ├── logistics/
│   │   ├── mill_weighing/
│   │   ├── reconciliation/
│   │   ├── reporting/
│   │   └── audit/
│   │
│   └── integrations/
│       └── composition/
│
├── alembic/
│   └── versions/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── security/
│   ├── performance/
│   └── e2e/
├── scripts/
├── pyproject.toml
├── uv.lock
├── Dockerfile
└── .env.example
```

Seluruh folder di dalam `modules/` wajib mengikuti template empat layer.

Contoh modul `reconciliation`:

```text
reconciliation/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── rules/
│   ├── services/
│   ├── events/
│   ├── exceptions/
│   └── ports/
│
├── application/
│   ├── commands/
│   ├── queries/
│   ├── use_cases/
│   ├── dto/
│   └── interfaces/
│
├── infrastructure/
│   ├── persistence/
│   ├── repositories/
│   ├── cache/
│   ├── integrations/
│   └── mappers/
│
├── presentation/
│   ├── routes/
│   ├── schemas/
│   ├── dependencies/
│   └── presenters/
│
└── __init__.py
```

Struktur ini merupakan standar minimum pembagian tanggung jawab, bukan kewajiban membuat file kosong untuk setiap subfolder.

Subfolder yang tidak diperlukan tidak harus dibuat.

---

# 7. PEMETAAN MODUL BACKEND

| Modul           | Tanggung Jawab                                 |
| --------------- | ---------------------------------------------- |
| identity_access | Autentikasi, sesi, pengguna, hak akses         |
| public_portal   | Penyajian informasi publik dan konten          |
| master_data     | Petani, kebun, koperasi, PKS                   |
| pricing         | Harga Disbun, harga PKS, verifikasi, publikasi |
| tbs_receiving   | Penerimaan TBS, penimbangan, grading kebun     |
| contracts       | Kontrak, kuota, alokasi pasokan                |
| logistics       | Armada, muatan, e-DO, status pengiriman        |
| mill_weighing   | Penerimaan PKS, tiket timbang, grading PKS     |
| reconciliation  | Pencocokan berat, sengketa, faktur, pembayaran |
| reporting       | Dashboard, agregasi, pelaporan                 |
| audit           | Audit bisnis dan penelusuran perubahan penting |

Walaupun nama modul backend lebih banyak dari delapan modul PRD, cakupan bisnisnya tetap sama.

Pemisahan dilakukan berdasarkan batas tanggung jawab teknis.

## 7.1 Batas Kepemilikan Data

Setiap modul harus memiliki kepemilikan logis atas data dan aturan bisnisnya.

Contoh:

- Modul `pricing` memiliki aturan publikasi harga.
- Modul `contracts` memiliki aturan alokasi kuota.
- Modul `logistics` memiliki aturan surat jalan.
- Modul `mill_weighing` memiliki aturan tiket timbang PKS.
- Modul `reconciliation` memiliki aturan pencocokan dan status sengketa.

Modul tidak boleh secara bebas mengubah tabel milik modul lain.

Interaksi lintas modul menggunakan kontrak aplikasi atau antarmuka yang terdokumentasi.

Untuk alur yang membutuhkan konsistensi atomik, Application Layer mengoordinasikan pekerjaan dalam transaksi database yang sesuai.

---

# 8. STANDAR SOLID DAN CLEAN CODE

## 8.1 Single Responsibility Principle

Setiap class atau fungsi memiliki tanggung jawab yang terdefinisi dengan jelas.

Contoh pemisahan:

- PriceValidator memvalidasi data harga.
- PublishPriceUseCase mengoordinasikan publikasi.
- PriceRepository menyimpan dan mengambil data.
- PriceRouter menangani HTTP.

Satu class tidak boleh sekaligus menangani validasi HTTP, SQL, aturan harga, dan publikasi.

## 8.2 Open/Closed Principle

Aturan sistem harus dapat diperluas tanpa harus mengubah banyak implementasi lama.

Contoh:

Strategi perhitungan potongan grading dapat memiliki variasi berdasarkan ketentuan PKS.

Variasi tersebut diimplementasikan melalui strategi atau policy yang terpisah, bukan percabangan kondisi yang tersebar di banyak endpoint.

## 8.3 Liskov Substitution Principle

Implementasi repository atau adapter harus mematuhi kontrak yang disepakati.

Implementasi sementara berbasis memori dan implementasi PostgreSQL harus memberikan perilaku yang konsisten berdasarkan interface.

## 8.4 Interface Segregation Principle

Interface dibuat sesuai kebutuhan klien.

Contoh:

- PriceReader.
- PriceWriter.
- PricePublisher.

Komponen yang hanya membaca harga tidak perlu bergantung pada seluruh operasi penulisan dan publikasi.

## 8.5 Dependency Inversion Principle

Use case bergantung pada interface, bukan implementasi database.

Contoh:

ReconcileWeighingUseCase bergantung pada ReconciliationRepository Port.

Implementasi PostgreSQL disediakan dari Infrastructure Layer.

## 8.6 Standar Clean Code

Wajib diterapkan:

- Nama fungsi dan variabel menjelaskan maksud.
- Tidak ada fungsi yang terlalu besar tanpa alasan.
- Tidak ada business logic pada router.
- Tidak ada query database pada Domain Layer.
- Tidak ada nilai aturan bisnis penting yang di-hardcode sembarangan.
- Tidak menggunakan float untuk perhitungan uang.
- Tidak menggunakan mutable global state untuk transaksi.
- Tidak menggunakan bare except tanpa alasan.
- Tidak menggunakan logging print untuk production.
- Tidak menggunakan dependency tersembunyi.
- Tidak membuat abstraksi yang belum dibutuhkan.
- Tidak menduplikasi aturan bisnis lintas modul.

Prinsip KISS, DRY, dan YAGNI diterapkan bersama SOLID.

Tidak seluruh kode harus menggunakan Design Pattern. Pattern digunakan ketika memberikan manfaat yang jelas.

---

# 9. PERFORMANCE ENGINEERING BACKEND

## 9.1 Tujuan

Backend harus memberikan response yang efisien dengan penggunaan CPU, memori, dan koneksi database yang terkendali.

Optimasi harus berdasarkan hasil pengukuran, bukan asumsi.

## 9.2 Asynchronous I/O

Operasi I/O menggunakan pendekatan asynchronous ketika relevan.

Contoh:

- Query database.
- Akses Redis.
- Pemanggilan API PKS.
- Operasi jaringan.

Aturan:

- Tidak melakukan blocking I/O di jalur async.
- Tidak menggunakan operasi CPU berat secara langsung di event loop.
- Tidak membuat task asynchronous tanpa pengelolaan siklus hidup.
- Tidak membagikan satu AsyncSession ke beberapa concurrent task.

## 9.3 Database Connection Pool

Koneksi PostgreSQL dikelola menggunakan connection pooling.

Konfigurasi pool harus mempertimbangkan:

- Jumlah worker backend.
- Kapasitas PostgreSQL.
- Perkiraan concurrency.
- Waktu tunggu koneksi.
- Jumlah koneksi maksimum.
- Pengujian beban.

Ukuran pool tidak ditetapkan secara sembarangan. Nilai awal ditentukan melalui benchmarking.

## 9.4 Query Optimization

Wajib menghindari:

- N+1 query.
- Query tanpa filter pada data besar.
- Fetch seluruh kolom yang tidak diperlukan.
- Query berulang dalam satu request.
- Pagination menggunakan seluruh data sekaligus.
- Transaksi panjang yang menahan lock secara berlebihan.

Teknik yang digunakan:

- Explicit column selection.
- Selective eager loading.
- Pagination.
- Indexing.
- Query profiling.
- EXPLAIN ANALYZE.
- Database aggregation.
- Bulk operation ketika sesuai.

## 9.5 Pagination

Endpoint daftar harus mendukung pagination.

Untuk daftar sederhana digunakan pagination yang stabil.

Untuk dataset transaksi besar dengan urutan konsisten, keyset/cursor pagination diprioritaskan dibanding offset besar.

Setiap endpoint menentukan batas maksimal `page_size`.

## 9.6 Background Processing

Pekerjaan berat yang tidak harus selesai dalam response HTTP dapat diproses secara asynchronous melalui worker.

Contoh:

- Generasi laporan besar.
- Ekspor data.
- Pemrosesan dokumen.
- Pengiriman notifikasi.
- Perhitungan agregasi yang mahal.

Penggunaan job queue hanya diwajibkan ketika diperlukan.

Untuk tahap awal, proses sederhana dapat berjalan secara synchronous selama memenuhi target performa.

Jika diperlukan worker persisten, gunakan solusi yang kompatibel dengan Redis dan memiliki retry, status pekerjaan, serta mekanisme idempotency.

Pekerjaan keuangan kritis tidak boleh hanya mengandalkan background task tanpa penyimpanan status yang durable.

## 9.7 Resource Management

Sistem harus:

- Menutup session database.
- Mengatur timeout HTTP.
- Membatasi ukuran upload.
- Membatasi ukuran response.
- Menghindari memory leak.
- Tidak membuat object besar secara tidak perlu.
- Memproses file besar secara streaming apabila relevan.
- Menggunakan lazy loading frontend dan API secara tepat.

---

# 10. DATABASE ENGINEERING

## 10.1 Database Utama

Database utama menggunakan PostgreSQL.

Database relasional dipilih karena sistem memiliki hubungan transaksi yang kompleks dan memerlukan integritas data.

## 10.2 Prinsip Perancangan

- Normalisasi data hingga setidaknya 3NF untuk data transaksional yang relevan.
- Primary key dan foreign key.
- Unique constraint.
- Check constraint.
- Referential integrity.
- Transaction management.
- Index berdasarkan kebutuhan query.
- Auditability.
- Migration versioning.

## 10.3 Tipe Data Finansial

Perhitungan harga dan nilai uang tidak boleh menggunakan floating point biner.

Gunakan `Decimal` pada Python dan `NUMERIC` pada PostgreSQL.

Contoh rancangan awal:

- Harga TBS: NUMERIC(18,2).
- Nilai transaksi: NUMERIC(20,2).
- Berat TBS: NUMERIC(14,3).
- Persentase: NUMERIC dengan presisi sesuai kebutuhan.

Presisi final ditetapkan dalam DBD berdasarkan data dan aturan pembulatan Perumda.

## 10.4 Transaksi Database

Operasi yang mengubah beberapa data terkait harus menggunakan transaksi atomik.

Contoh pembuatan e-DO:

1. Memeriksa penerimaan yang tersedia.
2. Memeriksa kontrak dan kuota.
3. Mengalokasikan muatan.
4. Membuat e-DO.
5. Mengubah status muatan.
6. Menyimpan audit bisnis.

Operasi harus berhasil secara keseluruhan atau dibatalkan jika terjadi kegagalan.

## 10.5 Pencegahan Race Condition

Proses yang berpotensi menerima request bersamaan harus dikendalikan.

Contoh:

- Dua petugas mengalokasikan kuota yang sama.
- Dua proses membuat e-DO dari muatan yang sama.
- Dua request menyetujui pembayaran yang sama.
- Dua request merekonsiliasi tiket yang sama.

Teknik yang dapat digunakan:

- Row-level locking.
- Unique constraints.
- Optimistic locking.
- Database transactions.
- Idempotency keys.

Pemilihan teknik disesuaikan dengan proses bisnis.

## 10.6 Idempotency

Endpoint kritis harus dapat mencegah efek ganda akibat pengiriman request berulang.

Prioritas:

- Pembuatan e-DO.
- Pencatatan tiket timbang.
- Rekonsiliasi.
- Persetujuan pembayaran.
- Pencatatan pembayaran.

Idempotency key harus memiliki cakupan identitas, operasi, dan batas waktu atau kebijakan retensi yang terdefinisi.

## 10.7 Indexing

Indeks awal dipertimbangkan pada:

- Kode petani.
- Kode koperasi.
- Kode PKS.
- Nomor kontrak.
- Nomor e-DO.
- Nomor tiket timbang.
- Status transaksi.
- Tanggal transaksi.
- Kombinasi referensi dan status yang sering difilter.

Indeks final harus divalidasi menggunakan query plan.

Terlalu banyak indeks dapat memperlambat operasi penulisan.

## 10.8 Database Migration

Seluruh perubahan skema database menggunakan Alembic.

Ketentuan:

- Migrasi terdokumentasi.
- Migrasi diuji sebelum deployment.
- Tidak mengubah database production secara manual.
- Backup dilakukan sebelum migrasi berisiko.
- Migration history tidak dihapus sembarangan.
- Strategi rollback atau roll-forward disiapkan.

---

# 11. CACHING STRATEGY

## 11.1 Tujuan

Redis digunakan untuk mengurangi beban pembacaan berulang dan mempercepat respons endpoint yang sesuai.

Cache tidak menjadi sumber kebenaran utama transaksi bisnis.

PostgreSQL tetap menjadi source of truth untuk data permanen.

## 11.2 Data yang Layak Di-cache

| Data                     | Strategi                        | Contoh TTL Awal  |
| ------------------------ | ------------------------------- | ---------------- |
| Harga publik aktif       | Cache-aside                     | 30–60 detik     |
| Direktori PKS publik     | Cache-aside                     | 5–15 menit      |
| Profil perusahaan publik | Cache-aside                     | 15 menit         |
| Referensi dropdown       | Cache-aside                     | 5–15 menit      |
| Agregasi dashboard       | Cache berdasarkan cakupan akses | 15–60 detik     |
| Konfigurasi non-sensitif | Cache-aside                     | Sesuai perubahan |

Nilai TTL merupakan titik awal pengujian, bukan angka final.

## 11.3 Data yang Tidak Boleh Di-cache Secara Sembarangan

- Password.
- Token autentikasi dalam cache publik.
- Data rekening.
- Bukti pembayaran rahasia.
- Hasil otorisasi lintas pengguna tanpa scope.
- Keputusan pembayaran yang belum final.
- Data pribadi petani pada cache yang dapat diakses publik.

State sesi autentikasi dapat disimpan di Redis secara aman, tetapi tidak boleh tercampur dengan cache konten publik.

## 11.4 Cache Key Design

Cache key harus memiliki struktur yang konsisten.

Contoh:

- public:prices:v1:region:{region}
- public:mills:v1:region:{region}
- public:profile:v1
- dashboard:v1:scope:{scope_id}:period:{period}

Cache yang bergantung pada hak akses harus memasukkan scope dan identitas konteks yang relevan.

## 11.5 Cache Invalidation

Setelah harga baru dipublikasikan:

1. Transaksi database diselesaikan.
2. Perubahan dinyatakan berhasil.
3. Cache harga yang relevan diinvalidasi atau diperbarui.
4. Request selanjutnya memperoleh data terbaru.

Untuk proses kompleks, invalidasi dapat menggunakan mekanisme outbox yang durable.

Cache tidak boleh diinvalidasi sebelum database commit secara permanen.

## 11.6 Cache Stampede Protection

Untuk data dengan trafik tinggi, sistem dapat menggunakan:

- TTL jitter.
- Request coalescing.
- Lock terdistribusi yang dibatasi waktu.
- Stale-while-revalidate pada data publik yang aman.

Harga lama hanya boleh ditampilkan jika diberi keterangan jelas bahwa data belum diperbarui.

## 11.7 Redis Failure Handling

Jika Redis tidak tersedia:

- Endpoint informasi publik dapat menggunakan fallback PostgreSQL dengan pembatasan beban.
- Operasi bisnis penting harus tetap menjaga konsistensi database.
- Sistem autentikasi tidak boleh mengizinkan akses secara otomatis akibat kegagalan penyimpanan sesi.
- Rate limiting dan kontrol keamanan yang bergantung pada Redis harus menerapkan kebijakan kegagalan yang aman.
- Kegagalan Redis dicatat dalam monitoring.

---

# 12. AUTHENTICATION DAN AUTHORIZATION

## 12.1 Model Akses

Sistem terdiri dari:

- Public Access.
- Authenticated Access.
- Role-Based Access Control.
- Resource Ownership/Scope Validation.

Login digunakan untuk aktivitas internal.

Portal Publik tidak memerlukan login.

## 12.2 Session Management

Untuk aplikasi web, baseline autentikasi menggunakan session server-side dengan session identifier acak yang disimpan melalui cookie:

- HttpOnly.
- Secure pada HTTPS.
- SameSite sesuai kebutuhan.
- Session expiration.
- Session revocation.
- Session rotation setelah autentikasi.

Cookie sesi tidak boleh dapat dibaca JavaScript.

Sesi aktif disimpan dan divalidasi pada server.

## 12.3 Password Security

Password harus di-hash menggunakan Argon2id.

Ketentuan:

- Tidak menyimpan plaintext password.
- Menggunakan parameter hashing yang sesuai kemampuan server.
- Membatasi percobaan login.
- Tidak membocorkan apakah akun tertentu terdaftar.
- Mendukung logout dan pencabutan sesi.
- Mendukung reset password dengan token sekali pakai dan masa berlaku terbatas.

## 12.4 Role-Based Access Control

RBAC diterapkan berdasarkan peran.

Namun RBAC saja tidak cukup.

Sistem harus memeriksa scope dan kepemilikan data.

Contoh:

- Petani A tidak boleh membaca pembayaran Petani B.
- Koperasi A tidak boleh mengubah data Koperasi B.
- Petugas PKS A tidak boleh membuka tiket PKS B.
- Staf tanpa izin keuangan tidak boleh menyetujui pembayaran.
- Pengunjung publik tidak boleh mengakses API internal.

Pemeriksaan ini wajib dilakukan pada server.

## 12.5 Sensitive Operations

Operasi berisiko tinggi harus memiliki kontrol tambahan.

Contoh:

- Perubahan harga setelah verifikasi.
- Perubahan data timbang yang sudah disahkan.
- Penyelesaian dispute.
- Persetujuan pembayaran.
- Pengubahan hak akses.
- Penghapusan atau penonaktifan akun.

Kontrol dapat berupa re-authentication, konfirmasi eksplisit, dual approval, atau MFA berdasarkan risiko dan SOP yang disahkan.

---

# 13. SECURITY ENGINEERING

## 13.1 Standar Keamanan

Perancangan mengacu pada prinsip OWASP ASVS dan OWASP Cheat Sheet.

Target desain adalah kontrol keamanan yang relevan dengan aplikasi bisnis dan perlindungan data transaksi.

Target ini bukan klaim sertifikasi keamanan.

## 13.2 API Security

API harus menerapkan:

- Authentication.
- Authorization.
- Scope validation.
- Request validation.
- Rate limiting.
- Response filtering.
- Strict CORS.
- Security headers.
- Input size limits.
- Safe error responses.

## 13.3 CSRF Protection

Karena aplikasi menggunakan cookie sesi, request yang mengubah data wajib dilindungi terhadap CSRF.

Kontrol mencakup:

- CSRF token yang divalidasi server.
- Pemeriksaan Origin untuk request sensitif.
- Konfigurasi SameSite cookie.
- Tidak menggunakan GET untuk mengubah state.

## 13.4 XSS Protection

Frontend dan backend harus:

- Menghindari injeksi HTML tidak terpercaya.
- Tidak menggunakan rendering HTML mentah tanpa sanitasi.
- Menggunakan output encoding yang benar.
- Menerapkan Content Security Policy.
- Melakukan validasi data yang akan ditampilkan.

## 13.5 SQL Injection Prevention

Seluruh query menggunakan parameter binding.

Tidak diperbolehkan menggabungkan input pengguna langsung ke SQL.

## 13.6 File Upload Security

Jika sistem mendukung unggah tiket atau bukti pembayaran:

- Membatasi tipe berkas.
- Membatasi ukuran.
- Memvalidasi konten.
- Menggunakan nama berkas internal.
- Mencegah path traversal.
- Menyimpan berkas di luar direktori publik langsung.
- Menggunakan akses terotorisasi.
- Menyediakan pemeriksaan malware jika diperlukan.

## 13.7 Secrets Management

Rahasia tidak boleh disimpan dalam source code.

Contoh:

- Database password.
- Session signing/secret material.
- API credentials.
- Storage credentials.
- Monitoring credentials.

Gunakan environment variables atau secret manager.

File `.env` yang berisi rahasia tidak boleh masuk ke version control.

## 13.8 Data Protection

Informasi pribadi petani dan data pembayaran harus mengikuti kebijakan perlindungan data yang berlaku di Indonesia.

Pengumpulan, pemrosesan, publikasi, retensi, dan penghapusan data harus didasarkan pada kewenangan yang sah.

Data publik dan data internal harus memiliki aturan klasifikasi yang berbeda.

---

# 14. MIDDLEWARE OBSERVABILITY — CCTV SYSTEM

## 14.1 Konsep

Sistem menggunakan middleware sebagai lapisan pemantauan aktivitas teknis.

Konsep ini disebut **CCTV Digital**, yaitu mekanisme untuk mengetahui request yang masuk, endpoint yang digunakan, waktu pemrosesan, hasil response, serta kegagalan yang terjadi.

CCTV Digital bukan perekaman seluruh isi komunikasi atau data sensitif pengguna.

Tujuannya adalah membantu pemeliharaan, audit keamanan, dan investigasi error.

## 14.2 Middleware yang Diperlukan

| Middleware/Komponen     | Fungsi                                      |
| ----------------------- | ------------------------------------------- |
| Request ID              | Memberi identitas unik setiap request       |
| Correlation Context     | Menghubungkan aktivitas dalam satu alur     |
| Access Logging          | Mencatat request HTTP secara aman           |
| Timing                  | Mengukur durasi request                     |
| Authentication          | Memvalidasi sesi                            |
| Authorization Guard     | Memastikan hak akses                        |
| CSRF Protection         | Melindungi request perubahan data           |
| Rate Limiting           | Membatasi penyalahgunaan request            |
| Security Headers        | Menambahkan header keamanan                 |
| Exception Handling      | Menangani error terstandar                  |
| Metrics Instrumentation | Mengumpulkan metrik performa                |
| Tracing                 | Menelusuri tahapan eksekusi                 |
| Audit Hook              | Memicu pencatatan audit bisnis yang relevan |

Urutan eksekusi aktual mengikuti perilaku middleware framework dan harus diuji agar error, header keamanan, serta identitas request tetap konsisten.

## 14.3 Access Log

Setiap request yang relevan dicatat dengan informasi seperti:

- Timestamp UTC.
- Request ID.
- Trace ID.
- HTTP method.
- Route template.
- Response status.
- Duration.
- Actor ID apabila sudah terautentikasi.
- Role yang relevan.
- Request size.
- Response size.

Tidak boleh mencatat password, cookie sesi, token, nomor rekening, maupun seluruh request body secara default.

## 14.4 Contoh Structured Log

```json
{
  "timestamp": "2026-11-10T09:30:00Z",
  "level": "INFO",
  "event": "http_request_completed",
  "request_id": "req_example_001",
  "trace_id": "trace_example_001",
  "method": "POST",
  "route": "/api/v1/reconciliations",
  "status_code": 201,
  "duration_ms": 138,
  "actor_id": "internal_user_17",
  "module": "reconciliation"
}
```

Data di atas merupakan contoh ilustratif.

## 14.5 Error Logging

Jika terjadi kesalahan, sistem harus mencatat:

- Waktu kejadian.
- Error code.
- Error class.
- Modul.
- Operasi yang gagal.
- Request ID.
- Trace ID.
- Penyebab teknis yang aman disimpan.
- Stack trace pada lingkungan logging internal.
- Kategori severity.

## 14.6 Security Event Logging

Kejadian penting yang wajib dipantau meliputi:

- Login gagal.
- Percobaan akses tanpa izin.
- Perubahan hak akses.
- Percobaan melewati alur bisnis.
- Aktivitas administrator.
- Percobaan request berulang yang mencurigakan.
- Perubahan konfigurasi sensitif.
- Kegagalan validasi keamanan.

Log keamanan dipisahkan secara logis dari access log umum.

## 14.7 Business Audit Trail

Audit bisnis disimpan secara terstruktur dan berbeda dari logging HTTP.

Contoh:

- Harga TBS dipublikasikan.
- Data timbangan direvisi.
- e-DO diterbitkan.
- Status dispute diubah.
- Pembayaran disetujui.
- Bukti pembayaran diverifikasi.

Audit memuat:

- Event ID.
- Actor ID.
- Jenis tindakan.
- Resource type.
- Resource ID.
- Waktu.
- Perubahan status.
- Alasan bila diwajibkan.
- Request ID.
- Metadata yang diperbolehkan.

Data audit harus menggunakan mekanisme append-only pada jalur aplikasi.

Hak penulisan dan penghapusan audit dibatasi. Untuk kebutuhan integritas yang lebih kuat, perubahan audit dapat dilindungi melalui hash chain, penyimpanan terpisah, atau media immutable.

Audit penting harus berhasil tersimpan secara konsisten dengan perubahan transaksi bisnis.

## 14.8 Trace Correlation

Setiap error harus dapat ditelusuri menggunakan Request ID atau Trace ID.

Contoh:

Pengguna melaporkan:

"Rekonsiliasi gagal. Kode referensi: req_example_001."

Administrator dapat mencari referensi tersebut dalam sistem logging untuk menemukan operasi yang gagal.

## 14.9 Monitoring Dashboard

Dashboard teknis dapat menampilkan:

- Total request.
- Error rate.
- Response latency.
- Slow endpoints.
- Database connection usage.
- Redis availability.
- Cache hit ratio.
- Failed login attempts.
- Queue failures jika ada.
- Jumlah konflik transaksi.
- Health status aplikasi.

Dashboard observabilitas hanya dapat diakses administrator atau operator yang diberi kewenangan.

## 14.10 Log Retention dan Privasi

Retensi log harus didefinisikan berdasarkan kebutuhan operasional, hukum, dan klasifikasi informasi.

Tidak semua jenis log memiliki periode retensi yang sama.

Log tidak boleh disimpan tanpa batas.

Akses ke log, penghapusan, ekspor, dan perubahan kebijakan logging harus dikendalikan serta diaudit.

---

# 15. ERROR HANDLING DAN ERROR MANAGEMENT

## 15.1 Tujuan

Error harus mudah dikenali oleh pengguna dan mudah ditelusuri oleh pengembang tanpa mengekspos informasi internal.

## 15.2 Kategori Error

| Kategori                | Contoh                          | HTTP         |
| ----------------------- | ------------------------------- | ------------ |
| Validation Error        | Data timbangan tidak valid      | 422          |
| Authentication Error    | Belum login                     | 401          |
| Authorization Error     | Tidak memiliki izin             | 403          |
| Not Found               | Tiket tidak ditemukan           | 404          |
| Conflict                | Muatan sudah dialokasikan       | 409          |
| Rate Limit              | Terlalu banyak request          | 429          |
| Business Rule Violation | Transaksi belum dapat disetujui | 409 atau 422 |
| Internal Error          | Kesalahan tak terduga           | 500          |
| Service Unavailable     | Dependensi penting terganggu    | 503          |

Status HTTP final diselaraskan dalam kontrak API.

## 15.3 Standar Error Response

Response error harus memiliki struktur konsisten.

Contoh:

```json
{
  "success": false,
  "error": {
    "code": "REC_WEIGHT_DISPUTE",
    "message": "Selisih berat melebihi toleransi yang berlaku.",
    "details": {
      "reconciliation_status": "DISPUTE_HOLD"
    }
  },
  "request_id": "req_example_001"
}
```

Contoh tersebut merupakan response kesalahan aturan bisnis yang terkontrol, bukan stack trace internal.

## 15.4 Error Code Convention

Format:

`MODULE_CATEGORY_DESCRIPTION`

Contoh:

- AUTH_INVALID_CREDENTIALS
- AUTH_ACCESS_DENIED
- PRICE_INVALID_PERIOD
- PRICE_ALREADY_PUBLISHED
- TBS_INVALID_WEIGHT
- CONTRACT_QUOTA_EXCEEDED
- LOG_DELIVERY_ALREADY_ASSIGNED
- MILL_DUPLICATE_TICKET
- REC_WEIGHT_DISPUTE
- PAY_ALREADY_APPROVED
- SYS_DATABASE_UNAVAILABLE

Setiap kode harus memiliki dokumentasi dan perilaku yang konsisten.

## 15.5 User-Friendly Error Messages

Pesan pengguna harus menggunakan bahasa Indonesia yang jelas.

Contoh:

Tidak disarankan:

"IntegrityError duplicate key violates unique constraint."

Disarankan:

"Nomor tiket timbang sudah terdaftar. Periksa kembali nomor tiket sebelum menyimpan."

Pesan teknis lengkap hanya tersedia pada sistem logging yang terproteksi.

## 15.6 Retry Policy

Retry hanya diterapkan pada operasi yang aman untuk diulang.

Tidak semua kegagalan harus di-retry.

Operasi mutasi penting membutuhkan idempotency untuk mencegah duplikasi.

Gunakan timeout, exponential backoff, dan jitter untuk panggilan jaringan yang sesuai.

---

# 16. REST API DESIGN STANDARD

## 16.1 Versioning

API menggunakan prefix:

`/api/v1/`

API publik menggunakan:

`/api/v1/public/`

## 16.2 Endpoint Group

| Domain          | Prefix                  |
| --------------- | ----------------------- |
| Authentication  | /api/v1/auth            |
| Public          | /api/v1/public          |
| Farmers         | /api/v1/farmers         |
| Cooperatives    | /api/v1/cooperatives    |
| Mills           | /api/v1/mills           |
| Pricing         | /api/v1/prices          |
| Receipts        | /api/v1/receipts        |
| Contracts       | /api/v1/contracts       |
| Delivery Orders | /api/v1/delivery-orders |
| Mill Tickets    | /api/v1/mill-tickets    |
| Reconciliations | /api/v1/reconciliations |
| Payments        | /api/v1/payments        |
| Reports         | /api/v1/reports         |
| Administration  | /api/v1/admin           |

## 16.3 API Conventions

- Gunakan HTTP method sesuai tujuan.
- Gunakan JSON untuk request dan response standar.
- Gunakan status code konsisten.
- Terapkan pagination untuk daftar.
- Terapkan filtering dan sorting terkontrol.
- Gunakan request ID.
- Validasi seluruh input pada server.
- Gunakan schema response eksplisit.
- Jangan mengembalikan field ORM sensitif secara otomatis.

## 16.4 API Documentation

FastAPI OpenAPI digunakan sebagai dasar dokumentasi API.

Dokumentasi memuat:

- Endpoint.
- Request schema.
- Response schema.
- Authorization.
- Error code.
- Contoh payload.
- Aturan pagination.
- Idempotency.
- Versioning.

Dokumentasi API internal tidak harus dapat diakses publik pada lingkungan production.

## 16.5 API Contract Testing

Frontend dan backend harus menggunakan kontrak API yang terdokumentasi.

Perubahan API tidak boleh dilakukan tanpa pemeriksaan dampak.

Disarankan menghasilkan TypeScript types dari OpenAPI agar frontend dan backend memiliki definisi data yang selaras.

---

# 17. FRONTEND ARCHITECTURE

## 17.1 Pendekatan

Frontend menggunakan React dan TypeScript dengan dua prinsip utama:

1. Atomic Design untuk penyusunan komponen UI.
2. Feature-Based Organization untuk pengelompokan logika aplikasi berdasarkan domain.

Atomic Design tidak menggantikan pembagian fitur.

Atomic Design mengatur tingkat komponen visual, sedangkan struktur feature mengatur kepemilikan fungsi bisnis.

## 17.2 Lima Level Atomic Design

### Level 1 — Atoms

Atoms merupakan elemen UI paling kecil yang dapat digunakan ulang.

Contoh:

- Button.
- Icon.
- Text.
- Heading.
- Input.
- Label.
- Badge.
- Checkbox.
- Radio.
- Spinner.
- Skeleton.

Atoms tidak boleh memiliki logika transaksi bisnis.

### Level 2 — Molecules

Molecules merupakan kombinasi beberapa atoms untuk satu fungsi antarmuka.

Contoh:

- SearchField.
- PriceDisplay.
- FormField.
- PasswordInput.
- DateRangeFilter.
- StatusIndicator.
- PaginationControl.
- MillLocationLink.

### Level 3 — Organisms

Organisms merupakan bagian antarmuka yang lebih kompleks.

Contoh:

- PublicHeader.
- InternalSidebar.
- PriceComparisonTable.
- MillLocationPanel.
- TbsReceivingForm.
- DeliveryOrderSummary.
- ReconciliationSummary.
- PaymentApprovalPanel.
- ExecutiveKpiSection.

Organisms boleh menggunakan hook dan props untuk berinteraksi dengan data, tetapi aturan bisnis utama tetap berada di domain/backend.

### Level 4 — Templates

Templates menentukan struktur halaman.

Contoh:

- PublicWebsiteTemplate.
- AuthenticationTemplate.
- InternalDashboardTemplate.
- DataManagementTemplate.
- TransactionFormTemplate.
- ExecutiveDashboardTemplate.

Templates mengatur tata letak, navigasi, dan slot konten.

### Level 5 — Pages

Pages merupakan implementasi halaman sebenarnya.

Contoh:

- HomePage.
- PublicPricesPage.
- PublicMillsPage.
- LoginPage.
- FarmerDashboardPage.
- ReceivingPage.
- DeliveryOrdersPage.
- ReconciliationPage.
- PaymentsPage.
- ExecutiveDashboardPage.

---

# 18. STRUKTUR FOLDER FRONTEND

```text
frontend/
├── src/
│   ├── app/
│   │   ├── providers/
│   │   ├── router/
│   │   ├── layouts/
│   │   └── config/
│   │
│   ├── components/
│   │   ├── atoms/
│   │   ├── molecules/
│   │   ├── organisms/
│   │   └── templates/
│   │
│   ├── features/
│   │   ├── auth/
│   │   ├── public-pricing/
│   │   ├── public-mills/
│   │   ├── farmers/
│   │   ├── cooperatives/
│   │   ├── tbs-receiving/
│   │   ├── contracts/
│   │   ├── logistics/
│   │   ├── mill-weighing/
│   │   ├── reconciliation/
│   │   ├── payments/
│   │   └── reporting/
│   │
│   ├── pages/
│   │   ├── public/
│   │   ├── auth/
│   │   └── internal/
│   │
│   ├── hooks/
│   ├── lib/
│   │   ├── api/
│   │   ├── validation/
│   │   ├── formatting/
│   │   └── utils/
│   ├── styles/
│   ├── types/
│   ├── assets/
│   └── main.tsx
│
├── tests/
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

Feature folder dapat memiliki:

- api.
- components.
- hooks.
- schemas.
- types.
- utils.
- tests.

Komponen yang hanya dipakai dalam satu fitur disimpan pada folder fitur tersebut.

Komponen bersama yang benar-benar digunakan lintas fitur dapat ditempatkan pada Atomic Design components.

## 18.1 Aturan Struktur

- Atoms tidak boleh bergantung pada Pages.
- Molecules dapat mengimpor Atoms.
- Organisms dapat mengimpor Atoms dan Molecules.
- Templates dapat mengimpor komponen dari level di bawahnya.
- Pages menggunakan Templates dan komponen yang relevan.
- Logika API tidak ditulis langsung dalam seluruh komponen visual.
- Komponen UI bersama tidak boleh mengimpor seluruh feature.
- Hindari circular dependencies.
- Hindari satu file komponen yang terlalu besar.

---

# 19. FRONTEND STATE MANAGEMENT

## 19.1 Server State

TanStack Query digunakan untuk:

- Fetch API.
- Cache response.
- Loading state.
- Error state.
- Refetch.
- Invalidation.
- Mutation.
- Background synchronization.

Server state tidak perlu diduplikasi secara permanen dalam Zustand.

## 19.2 Client State

Zustand digunakan untuk state UI yang perlu dibagikan lintas komponen.

Contoh:

- Sidebar state.
- Preferensi tampilan.
- Filter UI tertentu.
- Dialog state kompleks.

Untuk state lokal sederhana, React useState tetap digunakan.

## 19.3 Form State

React Hook Form digunakan untuk formulir.

Zod digunakan untuk validasi frontend.

Validasi backend tetap wajib.

Frontend validation tidak dianggap sebagai pengganti security validation.

## 19.4 Authentication State

Frontend mendapatkan status sesi dari endpoint terproteksi.

Session identifier tidak disimpan pada localStorage.

Setelah logout:

- State pengguna dibersihkan.
- Query cache privat dibersihkan.
- Navigasi diarahkan ke halaman yang sesuai.
- Permintaan privat tidak boleh terus menggunakan identitas pengguna sebelumnya.

## 19.5 Data Fetching Strategy

- Query key harus konsisten.
- Query privat harus mempertimbangkan identitas dan scope.
- Perubahan data harus memicu invalidation yang tepat.
- Hindari pemanggilan API ganda.
- Gunakan pagination pada tabel besar.
- Gunakan prefetch hanya untuk data yang diperlukan.
- Hindari optimistic update pada proses keuangan yang memerlukan persetujuan final.

---

# 20. UI/UX DESIGN SYSTEM

## 20.1 Design Tokens

Frontend menggunakan design tokens untuk:

- Colors.
- Typography.
- Spacing.
- Radius.
- Shadows.
- Borders.
- Breakpoints.
- Component states.

Perubahan visual global harus dapat dilakukan melalui token.

## 20.2 Visual Direction

Aplikasi diarahkan pada gaya:

- Profesional.
- Bersih.
- Modern.
- Mudah digunakan.
- Berorientasi data.
- Tidak berlebihan secara dekoratif.
- Cocok untuk lingkungan pemerintahan/BUMD dan pengguna lapangan.

Hindari penggunaan gradient berlebihan, dekorasi yang tidak relevan, efek kaca yang mengganggu keterbacaan, dan animasi tanpa tujuan fungsional.

## 20.3 Responsive Layout

Portal Publik menggunakan mobile-first layout.

Portal Internal:

- Desktop memiliki sidebar navigasi.
- Sidebar dapat dibuat tetap pada ukuran desktop.
- Konten utama memiliki area scroll independen apabila diperlukan.
- Tabel lebar harus menggunakan teknik responsif yang tidak merusak informasi.
- Mobile menggunakan navigasi yang lebih ringkas.

## 20.4 Loading dan Error States

Setiap halaman berbasis API harus memiliki:

- Loading state.
- Empty state.
- Error state.
- Success state.
- Unauthorized state bila relevan.

Jangan menampilkan halaman kosong ketika API gagal.

## 20.5 Accessibility

Target pengembangan diarahkan pada WCAG 2.2 Level AA untuk fitur yang relevan.

Pengujian mencakup:

- Kontras warna.
- Focus state.
- Navigasi keyboard.
- Semantic markup.
- Label formulir.
- Error announcement.
- Dialog accessibility.
- Target sentuh yang memadai.

---

# 21. FRONTEND PERFORMANCE

## 21.1 Code Splitting

Gunakan route-level lazy loading untuk halaman besar.

Contoh:

- Executive Dashboard.
- Analytics.
- Peta lokasi.
- Laporan.

## 21.2 Bundle Optimization

- Hindari library berat yang tidak diperlukan.
- Gunakan tree shaking.
- Hindari import seluruh paket ikon jika tidak dibutuhkan.
- Gunakan dynamic import.
- Optimalkan aset visual.
- Hindari duplikasi dependency.

## 21.3 Render Optimization

- Gunakan komposisi komponen yang jelas.
- Hindari re-render tidak diperlukan.
- Gunakan memoization berdasarkan hasil profiling.
- Gunakan virtualisasi untuk daftar sangat besar.
- Terapkan debounce pada pencarian yang memerlukan API.

## 21.4 Map Performance

Peta lokasi PKS harus:

- Mengambil data koordinat yang diperlukan.
- Menghindari marker berlebihan tanpa kebutuhan.
- Menampilkan daftar lokasi sebagai alternatif.
- Memuat komponen peta secara lazy jika memungkinkan.
- Mematuhi lisensi dan ketentuan penyedia tile.

MapLibre merupakan library render peta, bukan penyedia data lokasi atau layanan navigasi secara otomatis.

## 21.5 Public Portal SEO

Karena baseline menggunakan React SPA, metadata halaman publik, sitemap, dan aksesibilitas crawler harus diperhatikan.

Jika kebutuhan indeks pencarian publik menjadi prioritas utama, prerendering atau SSR dapat dievaluasi sebagai pengembangan arsitektur.

---

# 22. INTEGRATION ARCHITECTURE

## 22.1 Integrasi Harga PKS

Baseline menggunakan input harga yang diverifikasi petugas.

Jika API pihak ketiga tersedia, integrasi menggunakan adapter.

Kontrak adapter harus mendukung:

- Source identification.
- Fetch timestamp.
- Effective date.
- Validation.
- Error handling.
- Retry policy.
- Normalization.

Perubahan API pihak ketiga tidak boleh mengubah aturan bisnis inti.

## 22.2 Integrasi Tiket Timbang

Sistem mendukung:

- Manual verified entry.
- Future external API adapter.

Kedua jalur harus menghasilkan data dengan format domain yang konsisten.

## 22.3 Integrasi Peta

MapLibre digunakan untuk rendering.

Sumber peta, geocoding, dan layanan navigasi dipilih serta dikonfigurasi secara terpisah.

Jika koordinat belum tersedia, sistem tidak boleh membuat koordinat palsu.

## 22.4 File Storage

Dokumen tiket, kontrak, dan bukti pembayaran dapat disimpan melalui storage adapter.

Metadata tetap disimpan dalam PostgreSQL.

Akses dokumen harus melalui pemeriksaan otorisasi.

---

# 23. TESTING STRATEGY

## 23.1 Unit Testing

Unit testing berfokus pada Domain Layer dan Application Layer.

Contoh:

- Perhitungan berat netto.
- Perhitungan grading.
- Validasi harga.
- Alokasi kuota.
- Perubahan status pengiriman.
- Perhitungan selisih.
- Penentuan status dispute.
- Kalkulasi pembayaran.

Pengujian Domain Layer tidak memerlukan database aktif.

## 23.2 Integration Testing

Pengujian integrasi mencakup:

- Repository PostgreSQL.
- Database transactions.
- Redis caching.
- Authentication session.
- Modul yang saling berinteraksi.
- API integration adapters.

## 23.3 API Contract Testing

Setiap endpoint diuji untuk:

- Valid request.
- Invalid request.
- Authentication.
- Authorization.
- Response schema.
- Error schema.
- Pagination.
- Idempotency.

## 23.4 Security Testing

Minimal:

- Broken access control.
- Cross-role access.
- Cross-tenant/scope data access.
- SQL injection attempts.
- XSS prevention.
- CSRF protection.
- Rate limiting.
- Session expiry.
- Unauthorized file access.
- Sensitive data leakage.
- Log redaction.

## 23.5 Database Testing

Pengujian meliputi:

- Unique constraints.
- Foreign keys.
- Transaction rollback.
- Concurrency.
- Idempotency.
- Migration.
- Index usage.
- Data consistency.

## 23.6 Frontend Testing

Vitest dan React Testing Library digunakan untuk pengujian unit dan komponen.

Playwright digunakan untuk pengujian browser.

Skenario:

- Portal Publik tanpa login.
- Perbandingan harga.
- Peta PKS.
- Login.
- Akses berdasarkan role.
- Penerimaan TBS.
- Pembuatan e-DO.
- Rekonsiliasi.
- Persetujuan pembayaran.
- Logout.

## 23.7 End-to-End Testing

Skenario utama:

1. Harga dibuat dan diverifikasi.
2. Harga dipublikasikan.
3. Petani dan koperasi tersedia dalam master data.
4. Penerimaan TBS dicatat.
5. Penimbangan dihitung.
6. Kontrak dan kuota dipilih.
7. e-DO dibuat.
8. PKS memverifikasi pengiriman.
9. Tiket timbang dicatat.
10. Rekonsiliasi dijalankan.
11. Transaksi diselesaikan atau ditahan.
12. Pembayaran diproses sesuai kewenangan.
13. Dashboard diperbarui.

Skenario alternatif harus menguji error dan dispute.

## 23.8 Quality Gate

Sebelum penggabungan perubahan kode:

- Formatting lulus.
- Linting lulus.
- Type checking lulus.
- Unit tests lulus.
- Relevant integration tests lulus.
- API contract tests lulus untuk perubahan API.
- Security checks lulus.
- Build frontend lulus.
- Tidak ada secret dalam repository.

Target cakupan pengujian awal dapat ditetapkan minimal 80% pada Domain dan Application Layer, dengan seluruh aturan bisnis kritis tercakup oleh skenario pengujian yang bermakna.

Coverage bukan satu-satunya indikator kualitas.

---

# 24. PERFORMANCE TESTING

## 24.1 Tujuan Pengujian

Mengukur kemampuan sistem dalam menangani beban operasional secara konsisten.

## 24.2 Alat

Locust dapat digunakan untuk load testing.

Pengujian database menggunakan query profiling dan EXPLAIN ANALYZE.

## 24.3 Skenario Pengujian

- Pembacaan harga publik bersamaan.
- Pencarian daftar PKS.
- Login pengguna.
- Pembuatan penerimaan TBS.
- Pembuatan e-DO.
- Pencatatan tiket timbang.
- Proses rekonsiliasi.
- Permintaan dashboard.
- Percobaan request ganda.

## 24.4 Target Awal

| Parameter                           | Sasaran Awal                  |
| ----------------------------------- | ----------------------------- |
| Waktu respons transaksi utama       | P95 ≤ 3 detik                |
| Pembacaan harga publik              | P95 ≤ 1,5 detik              |
| Error tak terduga pada beban normal | Diupayakan di bawah 1%        |
| Perhitungan uang dan berat          | Tepat sesuai aturan numerik   |
| Duplikasi transaksi akibat retry    | 0 pada skenario yang diuji    |
| Pelanggaran otorisasi               | 0 pada skenario yang diuji    |
| Cache invalidation                  | Sesuai kontrak kesegaran data |
| Database deadlock tak tertangani    | 0 pada skenario yang diuji    |

Target diukur pada lingkungan dan tingkat beban yang didefinisikan.

Sebagai baseline pengujian awal, dapat digunakan 25–50 virtual users, kemudian beban dinaikkan sesuai kapasitas perangkat dan hasil pengukuran.

Target tidak boleh diklaim tercapai sebelum benchmark dilakukan.

---

# 25. HEALTH CHECK DAN MONITORING

## 25.1 Health Endpoints

Sistem menyediakan endpoint internal:

- /health/live
- /health/ready

Liveness menunjukkan proses aplikasi berjalan.

Readiness memeriksa apakah aplikasi siap melayani operasi yang diperlukan.

Pemeriksaan readiness dapat mempertimbangkan PostgreSQL dan komponen penting lainnya.

## 25.2 Metrics

Metrik yang dianjurkan:

- HTTP request count.
- HTTP request duration.
- Error rate.
- Active database connections.
- Database query latency.
- Redis availability.
- Cache hit ratio.
- Background job failures.
- Application memory usage.
- Application CPU usage.

## 25.3 Alerting

Alert diprioritaskan untuk:

- Kegagalan database.
- Kegagalan autentikasi secara tidak wajar.
- Peningkatan error rate.
- Slow query berulang.
- Kegagalan proses pembayaran.
- Ketidaktersediaan Redis yang memengaruhi layanan.
- Kegagalan worker penting.

Alert tidak boleh dikirim untuk seluruh warning tanpa klasifikasi agar tidak menghasilkan alarm fatigue.

---

# 26. DEPLOYMENT DAN ENVIRONMENT

## 26.1 Environment

Minimal tersedia:

- Development.
- Testing.
- Production/Demo.

Data penelitian dan data sensitif tidak boleh langsung disalin ke lingkungan development tanpa otorisasi dan perlindungan.

## 26.2 Docker

Backend, frontend, PostgreSQL, dan Redis dapat dijalankan melalui Docker Compose.

Dockerfile harus:

- Menggunakan base image yang sesuai.
- Meminimalkan dependency.
- Menghindari proses sebagai root apabila memungkinkan.
- Tidak menyertakan secret.
- Mendukung health check.
- Menghasilkan build reproducible.

## 26.3 Reverse Proxy

Reverse proxy menangani:

- HTTPS.
- Request forwarding.
- Header keamanan.
- Pembatasan ukuran request.
- Logging yang relevan.
- Konfigurasi domain.

## 26.4 Database Backup

Sistem membutuhkan:

- Backup terjadwal.
- Kebijakan retensi.
- Penyimpanan backup yang terlindungi.
- Pengujian restore.
- Prosedur pemulihan.

Backup dianggap valid setelah diuji pemulihannya.

## 26.5 CI Pipeline

Pipeline minimal:

1. Dependency installation.
2. Static analysis.
3. Type checking.
4. Unit tests.
5. Integration tests yang relevan.
6. Frontend tests.
7. Production build.
8. Dependency/security scanning.
9. Artifact packaging.

Deployment dilakukan hanya setelah pemeriksaan yang ditetapkan berhasil.

---

# 27. CODE QUALITY DAN GOVERNANCE

## 27.1 Coding Conventions

Backend:

- Python type hints.
- Ruff.
- Pyright.
- Consistent naming.
- Explicit interfaces.
- Limited dependencies.

Frontend:

- TypeScript strict mode.
- ESLint.
- Prettier.
- Typed API contracts.
- Feature-based organization.
- Atomic Design.

## 27.2 Git Workflow

Gunakan branch atau perubahan terisolasi berdasarkan pekerjaan.

Setiap perubahan harus memiliki:

- Tujuan.
- Batas perubahan.
- Tes terkait.
- Ringkasan perubahan.
- Dampak terhadap kontrak.

## 27.3 Architecture Decision Records

Keputusan teknis penting dicatat dalam ADR.

Contoh:

- ADR-001 Modular Monolith.
- ADR-002 Four-Layer Backend Architecture.
- ADR-003 PostgreSQL as Source of Truth.
- ADR-004 Redis Cache Strategy.
- ADR-005 Server-Side Session Authentication.
- ADR-006 Atomic Design Frontend.
- ADR-007 Structured Logging and Audit Separation.

ADR membantu menjaga konsistensi keputusan ketika proyek berkembang.

## 27.4 Dependency Governance

- Gunakan lockfile.
- Audit dependency.
- Hindari paket tidak terpelihara.
- Hindari dependency dengan fungsi tumpang tindih.
- Evaluasi pembaruan keamanan.
- Uji kompatibilitas sebelum upgrade.

## 27.5 Dokumentasi Internal

Dokumentasi teknis minimal meliputi:

- README.
- Environment configuration.
- Architecture overview.
- Module ownership.
- API specification.
- Database migration guide.
- Testing guide.
- Deployment guide.
- Error catalog.
- Security and logging policy.

---

# 28. REQUIREMENT TRACEABILITY

Setiap kebutuhan teknis harus dapat ditelusuri kembali ke kebutuhan produk.

Contoh:

| ID TRD       | Kebutuhan Teknis                     | Referensi PRD          |
| ------------ | ------------------------------------ | ---------------------- |
| TR-PUB-001   | Endpoint publik tanpa autentikasi    | FR-PUB-001             |
| TR-PRICE-001 | Repository dan API harga multi-PKS   | FR-PUB-002, FR-PUB-003 |
| TR-MAP-001   | Integrasi MapLibre dan koordinat PKS | FR-PUB-005             |
| TR-AUTH-001  | Session authentication dan RBAC      | Bagian 4 PRD           |
| TR-MD-001    | Master data terpusat                 | FR-MD-001–005         |
| TR-TBS-001   | Validasi timbang dan grading         | FR-TBS-001–005        |
| TR-CON-001   | Kontrol kontrak dan kuota            | FR-KTR-001–004        |
| TR-LOG-001   | e-DO dan konsolidasi muatan          | FR-LOG-001–006        |
| TR-MILL-001  | Pencatatan tiket PKS                 | FR-PKS-001–005        |
| TR-REC-001   | Rekonsiliasi dan dispute             | FR-REC-001–005        |
| TR-PAY-001   | Kalkulasi dan pencatatan pembayaran  | FR-REC-006–010        |
| TR-DSH-001   | Dashboard dan laporan                | FR-DSH-001–007        |

Seluruh ID pada tabel merupakan penghubung awal.

Traceability matrix lengkap akan diperbarui sejalan dengan penyusunan AFD, DBD, BSD, dan IPD.

---

# 29. RISIKO TEKNIS DAN MITIGASI

| Risiko                                             | Mitigasi                                             |
| -------------------------------------------------- | ---------------------------------------------------- |
| Backend berubah menjadi monolith tanpa batas modul | Architecture tests dan module dependency rules       |
| Business logic bercampur dengan router             | Code review dan unit tests Domain Layer              |
| Query lambat                                       | Query profiling dan index berdasarkan bukti          |
| Redis menyajikan harga usang                       | TTL, invalidation, timestamp, dan kebijakan fallback |
| Data bocor lintas peran                            | RBAC, scope validation, security tests               |
| Request ganda menyebabkan transaksi dobel          | Idempotency dan database constraints                 |
| Race condition kuota                               | Transaction locking dan concurrency tests            |
| Logging membocorkan rahasia                        | Structured logging dan redaction                     |
| Error sulit ditelusuri                             | Request ID, trace ID, error catalog                  |
| Kompleksitas observability berlebihan              | Implementasi bertahap                                |
| Bundle frontend besar                              | Code splitting dan performance budget                |
| Banyak komponen UI duplikat                        | Atomic Design dan component review                   |
| Integrasi PKS tidak tersedia                       | Manual verified entry sebagai baseline               |
| Infrastruktur development terbatas                 | Docker Compose dan konfigurasi layanan minimal       |

---

# 30. KRITERIA PENERIMAAN TEKNIS

Implementasi dianggap memenuhi baseline TRD apabila:

1. Backend dipisahkan berdasarkan modul domain.
2. Setiap modul memiliki empat layer yang jelas.
3. Tidak ada dependency terlarang dari Domain Layer ke framework.
4. Logika bisnis utama dapat diuji secara mandiri.
5. API menggunakan kontrak yang terdokumentasi.
6. PostgreSQL menjadi sumber kebenaran transaksi.
7. Database migration dapat dijalankan.
8. Transaksi kritis terlindungi dari pencatatan ganda.
9. Race condition penting telah diuji.
10. Redis cache memiliki kebijakan TTL dan invalidation.
11. Kegagalan Redis tidak membuka akses tidak sah.
12. Portal Publik dapat digunakan tanpa login.
13. Portal Internal menerapkan autentikasi dan otorisasi.
14. Pembatasan data lintas role dan scope telah diuji.
15. Middleware menghasilkan request ID.
16. Error memiliki kode dan response konsisten.
17. Logging tidak memuat rahasia.
18. Audit bisnis penting tercatat.
19. Metrik performa utama dapat diukur.
20. Frontend menggunakan Atomic Design lima level.
21. Frontend menggunakan TypeScript strict mode.
22. Formulir memiliki validasi frontend dan backend.
23. Halaman memiliki loading, empty, dan error state.
24. Sistem responsif pada desktop dan mobile.
25. Unit tests dan integration tests lulus.
26. API contract tests lulus.
27. Security tests kritis lulus.
28. Production build berhasil.
29. Dokumentasi arsitektur diperbarui.
30. Skenario transaksi TBS end-to-end dapat didemonstrasikan.

---

# 31. KEPUTUSAN YANG MASIH MEMERLUKAN VALIDASI

Keputusan teknis berikut harus dipastikan sebelum implementasi production:

1. Infrastruktur hosting dan domain.
2. Spesifikasi server.
3. Jumlah pengguna aktif yang diperkirakan.
4. Ketersediaan akses API PKS.
5. Sumber data harga yang diizinkan.
6. Penyedia tile peta dan biaya penggunaan.
7. Kebijakan keamanan organisasi.
8. Kebijakan retensi data dan log.
9. Kebutuhan backup dan pemulihan.
10. SOP persetujuan pembayaran.
11. Kebutuhan layanan notifikasi.
12. Persyaratan publikasi data perusahaan dan mitra.

Untuk prototipe tesis, kebutuhan yang belum dikonfirmasi dapat menggunakan konfigurasi simulasi yang diberi label secara jelas.

---

# 32. KESIMPULAN

Technical Requirements Document ini menetapkan rancangan teknis pengembangan Sistem Informasi Terintegrasi Rantai Pasok TBS pada Perumda Tuah Sekata.

Backend menggunakan pendekatan Modular Monolith dengan Clean Architecture dan empat layer pada setiap modul, yaitu Domain, Application, Infrastructure, dan Presentation.

Prinsip SOLID menjadi dasar pengembangan agar kode mudah dipelihara, diuji, dan diperluas.

PostgreSQL digunakan untuk menjaga integritas transaksi, Redis untuk caching yang terkontrol, serta middleware observabilitas untuk membantu pemantauan request, performa, keamanan, dan kesalahan sistem.

Sistem logging dibedakan menjadi access logging, security logging, dan business audit trail agar aktivitas dapat ditelusuri tanpa membocorkan informasi sensitif.

Frontend menggunakan React dan TypeScript dengan pendekatan Atomic Design lima tingkat, dikombinasikan dengan pengelompokan fitur berdasarkan domain bisnis.

Perancangan mempertahankan dua lingkungan penggunaan, yaitu Portal Publik tanpa login dan Portal Internal dengan autentikasi serta otorisasi berdasarkan peran dan cakupan data.

Seluruh rancangan diarahkan untuk mendukung pengembangan prototipe yang terukur, aman, memiliki kinerja yang baik, dan dapat dievaluasi melalui metodologi DSRM pada penelitian tesis.

**Status Dokumen: TRD V1.1 — TECHNICAL ARCHITECTURE BASELINE**

**Dokumen Selanjutnya: Application Flow Document (AFD).**

---

## REFERENSI TEKNIS UTAMA

- FastAPI Documentation — https://fastapi.tiangolo.com/
- SQLAlchemy Documentation — https://docs.sqlalchemy.org/
- Alembic Documentation — https://alembic.sqlalchemy.org/
- PostgreSQL Documentation — https://www.postgresql.org/docs/
- Redis Documentation — https://redis.io/docs/
- React Documentation — https://react.dev/
- TypeScript Documentation — https://www.typescriptlang.org/docs/
- Vite Documentation — https://vite.dev/
- Tailwind CSS Documentation — https://tailwindcss.com/docs
- TanStack Query — https://tanstack.com/query
- TanStack Router — https://tanstack.com/router
- shadcn/ui — https://ui.shadcn.com/docs
- MapLibre — https://maplibre.org/
- OpenTelemetry — https://opentelemetry.io/docs/
- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/

**Akhir Dokumen — Technical Requirements Document V1.1**

# 33. SOLO DEVELOPER ARCHITECTURE PRINCIPLES V1.1

Bagian ini mengikat pilihan teknis. Jika daftar tool atau quality gate sebelumnya menyatakan komponen opsional sebagai wajib, klasifikasi di sini yang berlaku.

## 33.1 Prinsip Implementasi

- **Modular Monolith + Clean Architecture + SOLID** tetap wajib. Setiap modul bisnis memiliki `domain/`, `application/`, `infrastructure/`, dan `presentation/` di dalam modul tersebut.
- Terapkan SOLID secara pragmatis: tanggung jawab jelas, domain bebas HTTP/ORM, dependency inversion pada batas yang memberi manfaat pengujian atau variasi. Buat interface hanya bila dibutuhkan; hindari generic repository, inheritance, wrapper, factory, dan container tanpa tanggung jawab nyata.
- Struktur ringan: entities/rules pada Domain, use cases pada Application, ORM/repository pada Infrastructure, route/schema pada Presentation. Tambah file berdasarkan kebutuhan nyata, bukan folder kosong.
- Dependency mengarah Presentation → Application → Domain; Infrastructure mengimplementasikan port yang diperlukan. Wiring eksplisit pada composition root dan FastAPI dependencies cukup sebagai DI baseline.
- `core` hanya untuk konfigurasi, session database, security infrastructure, logging, middleware, error, cache utility, dan primitive lintas modul. Business logic tetap dimiliki modul.
- Pertahankan PostgreSQL, SQLAlchemy, Alembic, constraint, transaksi, pooling, dan migrasi incremental. Optimasi berdasarkan profiling: kebenaran query, indeks relevan, pagination, transaksi, concurrency, lalu cache.

Contoh ilustratif: `backend/app/modules/pricing/{domain,application,infrastructure,presentation}/`. Struktur ini tidak mewajibkan file atau folder kosong.

## 33.2 Security dan Observability Baseline

Tetap wajib: server-side session, cookie HttpOnly, CSRF protection, RBAC dan scope authorization, Argon2id, validasi input, rate limiting, least privilege, secure file handling, serta audit transaksi penting. Kegagalan cache tidak boleh melewati autentikasi atau mengubah hasil transaksi.

Middleware minimum: Request ID, HTTP access log terstruktur, durasi, status, module/error code, exception handler, health checks, security event log, dan business audit trail. Jangan log password, token, cookie, rekening, PII lengkap, atau payload sensitif. Request ID dapat digunakan pengguna untuk menelusuri error.

`structlog` atau logging terstruktur setara adalah baseline. Prometheus, Grafana, Loki, OpenTelemetry, dan tracing backend ditambahkan saat manfaat operasional terukur; bukan prasyarat prototipe lokal.

## 33.3 Klasifikasi Teknologi

| Status | Teknologi / kemampuan | Ketentuan |
| --- | --- | --- |
| Required | FastAPI, PostgreSQL, SQLAlchemy, Alembic, React, TypeScript, Vite, Atomic Design, OpenAPI | Stack baseline dan kontrak bersama |
| Required | Pydantic, pytest, Ruff, structured logging, session security, migrations | Terapkan seperlunya; konfigurasi dan lockfile minimal |
| Conditional | Redis, HTTPX, MapLibre, TanStack Table, satu chart library, object storage, background worker | Hanya bila use case tersedia; aplikasi dan tes dasar tetap berjalan tanpa cache Redis |
| Conditional | TanStack Query, React Hook Form, Zod, router pilihan, shadcn/ui, Lucide, Vitest, React Testing Library, Playwright, MSW | Pilih sesuai kebutuhan; hindari duplikasi fungsi |
| Conditional | Zustand | Hanya jika shared client state tidak nyaman ditangani lokal/server state |
| Deferred | Prometheus/Grafana/Loki/OpenTelemetry stack, HA kompleks, bank settlement otomatis | Tunda sampai kebutuhan terukur dan disetujui |

Jangan gunakan dua library chart atau state management untuk fungsi sama. Coverage 80% bukan gate universal; prioritaskan tes aturan kritis.

## 33.4 Redis dan Database

PostgreSQL adalah source of truth. Redis didukung sebagai optimasi opsional untuk kandidat seperti harga publik, direktori PKS, atau agregasi dashboard setelah manfaat diukur. Cache memiliki TTL, invalidation, timestamp, dan fallback aman. Kegagalan Redis tidak membuat transaksi hilang atau memperlonggar otorisasi.

## 33.5 Frontend dan UX

React + TypeScript menggunakan Feature-Based Organization dan Atomic Design lima level: Atoms (tanpa business logic), Molecules, Organisms, Templates, Pages. Komponen satu fitur tinggal di fitur tersebut; shared component hanya untuk penggunaan lintas fitur. Backend menjadi sumber kebenaran aturan bisnis.

Pertahankan 25 prinsip UX, golden ratio sebagai pedoman komposisi fleksibel, micro-interactions fungsional, mobile-first Portal Publik, dashboard internal responsif, accessibility, reduced motion, serta loading/empty/error/success state. Terapkan berdasarkan relevansi, bukan checklist mekanis setiap komponen.

## 33.6 Testing dan Quality Gates

Backend memprioritaskan domain unit, use case, database integration, API contract, auth/scope, concurrency pada operasi kritis, dan end-to-end. Frontend memprioritaskan typecheck, interaksi/form penting, MSW workflow, browser journey utama, responsive/accessibility, dan production build. Fokus risiko tinggi: harga, berat, grading, kontrak, kuota, e-DO, rekonsiliasi, settlement, pembayaran, dan akses. Hindari tes CRUD berulang yang menguji perilaku sama. Performance benchmark dijalankan pada milestone relevan, bukan blocker styling.

Setiap milestone memiliki objective, scope, acceptance criteria, tes relevan, evidence, PASS/FAIL, dan regression check. Kekuatan bukti menyesuaikan risiko.
