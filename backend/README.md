# AgroNiaga TBS Supply Chain Backend

Backend API FastAPI (Modular Monolith + Clean Architecture 4 Layer) untuk Sistem Informasi Terintegrasi Rantai Pasok TBS Perumda Tuah Sekata — Unit Agro Niaga.

## Prasyarat

- Python `3.12` (virtual environment terisolasi pada `backend/.venv`)
- PostgreSQL `17` (atau `16+`) dan Redis `7+`
- Kontrak kanonis M0.1 di `contracts/openapi.v1.yaml`

## Setup Lokal

1. Pastikan berada di direktori `backend/` dan gunakan `.venv` yang tersedia:
   ```powershell
   cd backend
   Copy-Item .env.example .env
   ```
2. Sinkronisasi paket dari `uv.lock`:
   ```powershell
   .venv\Scripts\uv.exe sync --inexact --active
   ```
3. Jalankan PostgreSQL & Redis menggunakan Docker Compose jika Docker tersedia:
   ```powershell
   docker compose -f ..\infra\docker-compose.yml up -d
   ```
   Jika menggunakan service PostgreSQL/Redis lokal atau WSL2, sesuaikan `DATABASE_URL`, `TEST_DATABASE_URL`, `REDIS_URL`, dan `TEST_REDIS_URL` pada `backend/.env`.
4. Jalankan migrasi Alembic ke database pengembangan:
   ```powershell
   .venv\Scripts\python.exe -m alembic upgrade head
   ```
5. Jalankan server pengembangan:
   ```powershell
   .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

## Pemeriksaan Kualitas & Pengujian

```powershell
.venv\Scripts\python.exe -m ruff format --check .
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m pyright
.venv\Scripts\python.exe -m pytest -q
```
