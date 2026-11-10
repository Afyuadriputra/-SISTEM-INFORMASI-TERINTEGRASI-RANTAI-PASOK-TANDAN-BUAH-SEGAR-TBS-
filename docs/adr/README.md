# Architecture Decision Records (ADR) — Indeks M0

Direktori ini mencatat keputusan arsitektur inti dan keputusan kontrak API yang ditetapkan pada **Milestone M0** mengacu pada [TRD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/TRD.md) (§27.3), [DBD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/DBD.md), [IPD.md](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/IPD.md), dan hasil verifikasi FigCraft D5.

| ID | Judul Keputusan | Status | Sumber Utama |
| :--- | :--- | :--- | :--- |
| [ADR-001](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-001-modular-monolith.md) | Arsitektur Backend Modular Monolith | Accepted | `TRD §2.2, §7` |
| [ADR-002](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-002-four-layer-clean-architecture.md) | Clean Architecture Empat Layer per Modul & SOLID Pragmatis | Accepted | `TRD §5, §8`, `IPD §9` |
| [ADR-003](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-003-postgresql-source-of-truth.md) | PostgreSQL sebagai Single Source of Truth | Accepted | `TRD §10`, `DBD §1.3` |
| [ADR-004](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-004-redis-cache-strategy.md) | Strategi Caching Redis Cache-Aside & Fail-Closed Security | Accepted | `TRD §11`, `DBD §24` |
| [ADR-005](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-005-session-csrf-rbac-scope.md) | Server-Side Session Cookie, CSRF, RBAC & Scope Isolation | Accepted | `TRD §12–13`, `DBD §6` |
| [ADR-006](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-006-atomic-design-frontend.md) | Arsitektur Frontend Atomic Design 5 Level + Feature Organization | Accepted | `TRD §17–18`, FigCraft D5 |
| [ADR-007](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-007-structured-logging-and-audit-separation.md) | Pemisahan Structured Access/Security Logs & Business Audit Trail | Accepted | `TRD §14`, `BSD §28` |
| [ADR-008](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-008-openapi-envelope-pagination.md) | Standar Kontrak OpenAPI 3.1.0, Envelope Response & Pagination | Accepted | `IPD §4`, `TRD §16` |
| [ADR-009](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-009-decimal-precision-uuid-timezone.md) | Transport Desimal String, Identifier UUID & Konvensi UTC/WIB | Accepted | `DBD §3`, `IPD §4.4` |
| [ADR-010](file:///d:/Kuliah/joki/radit/projek%20thesis%20bg%20givo/docs/adr/ADR-010-idempotency-concurrency-pending-sop.md) | Idempotency-Key, Concurrency Locking & Pending SOP Guards | Accepted | `BSD §27`, `DBD §21`, `AFD §41` |
