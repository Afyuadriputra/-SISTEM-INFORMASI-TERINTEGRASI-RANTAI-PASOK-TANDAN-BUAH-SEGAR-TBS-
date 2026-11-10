# ADR-006: Arsitektur Frontend Atomic Design 5 Level + Feature Organization

- **Status:** Accepted
- **Tanggal:** 2026-11-10
- **Referensi:** `TRD §17–18`, `DBD §31`, `IPD §24`, FigCraft D5 (`d5-design-gap-closure-signoff.md`)

## Konteks
UI mencakup 26 rute (`AFD §36`) lintas 8 konteks aktor (`PUBLIC` + 7 peran login) dan harus dapat dikembangkan dengan MSW serta menghasilkan React + TypeScript strict yang bebas duplikasi komponen.

## Keputusan
1. Visual komponen dibagi dalam **5 level Atomic Design** selaras perpustakaan FigCraft D5 (`Atoms -> Molecules -> Organisms -> Templates -> Pages`) di atas token `tokens.tailwind.css` (`@theme static`).
2. Kepemilikan alur bisnis dan fetch API dikelompokkan berdasarkan **Feature-Based Organization** (`features/auth`, `public-pricing`, `public-mills`, `master-data`, `receiving`, `contracts`, `logistics`, `mill-weighing`, `reconciliation`, `payments`, `reporting`, `admin`).
3. Server state dikelola oleh **TanStack Query**; UI form oleh **React Hook Form + Zod**; routing oleh **TanStack Router**; shared UI client state minimal oleh **Zustand**. Aturan bisnis akhir, penghitungan finansial, dan otorisasi tetap dieksekusi di backend.

## Konsekuensi
- **Positif:** Sinkronisasi 1:1 antara komponen FigCraft D5 (`Organism/InternalSidebar #275`, `Molecule/WeightInputGroup #227`, dll.) dan kontrak OpenAPI melalui `openapi-typescript`.
