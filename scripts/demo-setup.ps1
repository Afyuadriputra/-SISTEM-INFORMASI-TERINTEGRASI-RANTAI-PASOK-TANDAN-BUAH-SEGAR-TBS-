[CmdletBinding()]
param(
    [switch]$ResetDemo,
    [string]$ConfirmDatabase = "",
    [switch]$Yes
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_demo-common.ps1")

function New-RandomUrlSafeSecret {
    param([int]$NumBytes = 24)
    $bytes = New-Object byte[] $NumBytes
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($bytes)
    }
    finally {
        $rng.Dispose()
    }
    return ([System.BitConverter]::ToString($bytes).Replace("-", "").ToLowerInvariant())
}

function Test-DemoPgConnection {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PythonExe,
        [Parameter(Mandatory = $true)]
        [string]$DatabaseUrl
    )

    $psycopgUrl = $DatabaseUrl -replace "^postgresql\+psycopg://", "postgresql://"
    $pyCmd = "import os, sys, psycopg; conn = psycopg.connect(os.environ['DEMO_PROBE_DB_URL'], connect_timeout=3); row = conn.execute('SELECT current_database()').fetchone(); conn.close(); sys.exit(0 if row and row[0] == 'agroniaga_demo' else 1)"
    $exitCode = Invoke-WithChildEnv -EnvOverrides @{ DEMO_PROBE_DB_URL = $psycopgUrl } -Action {
        $prevPref = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            & $PythonExe -B -c $pyCmd *> $null
            return $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $prevPref
        }
    }
    return ($exitCode -eq 0)
}

function Ensure-DemoDatabaseAndRole {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PythonExe,
        [Parameter(Mandatory = $true)]
        [string]$DatabaseUrl,
        [Parameter(Mandatory = $true)]
        $PgInfo
    )

    if ($PgInfo.Database -ne "agroniaga_demo") {
        throw "Refusing database provisioning for non-demo DB '$($PgInfo.Database)'."
    }

    if (Test-DemoPgConnection -PythonExe $PythonExe -DatabaseUrl $DatabaseUrl) {
        Write-Host "[OK] Koneksi PostgreSQL ke agroniaga_demo terverifikasi." -ForegroundColor Green
        return
    }

    if ($PgInfo.Host -notin @("127.0.0.1", "localhost")) {
        throw "Tidak dapat terhubung ke $($PgInfo.Host):$($PgInfo.Port)/agroniaga_demo dan provisioning otomatis hanya mendukung host lokal."
    }

    $wslCmd = Get-Command wsl.exe -ErrorAction SilentlyContinue
    if ($null -eq $wslCmd) {
        throw "Gagal login ke agroniaga_demo dan wsl.exe tidak tersedia untuk membuat role/database agroniaga_demo."
    }

    Write-Host "[INFO] Membuat role dan database terisolasi agroniaga_demo di PostgreSQL port $($PgInfo.Port)..." -ForegroundColor Cyan
    if ($PgInfo.Username -ne "agroniaga_demo") {
        throw "Username demo di DATABASE_URL harus 'agroniaga_demo', bukan '$($PgInfo.Username)'."
    }
    if ($PgInfo.Password -notmatch "^[a-z0-9]+$") {
        throw "Password demo di DATABASE_URL untuk provisioning WSL hanya mengizinkan karakter [a-z0-9]."
    }

    $safePass = $PgInfo.Password
    $roleSql = "DO `$`$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agroniaga_demo') THEN CREATE ROLE agroniaga_demo WITH LOGIN PASSWORD '$safePass' NOSUPERUSER NOCREATEDB NOCREATEROLE; END IF; END `$`$;"
    $roleSql | & wsl.exe -u root -- su - postgres -c "psql -p $($PgInfo.Port) -v ON_ERROR_STOP=1"
    if ($LASTEXITCODE -ne 0) {
        throw "Gagal memastikan role agroniaga_demo di PostgreSQL port $($PgInfo.Port)."
    }

    $dbExists = ("SELECT 1 FROM pg_database WHERE datname = 'agroniaga_demo';" | & wsl.exe -u root -- su - postgres -c "psql -p $($PgInfo.Port) -tA" | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Gagal memeriksa daftar database di PostgreSQL port $($PgInfo.Port)."
    }
    if ($dbExists -ne "1") {
        "CREATE DATABASE agroniaga_demo OWNER agroniaga_demo ENCODING 'UTF8';" | & wsl.exe -u root -- su - postgres -c "psql -p $($PgInfo.Port) -v ON_ERROR_STOP=1"
        if ($LASTEXITCODE -ne 0) {
            throw "Gagal membuat database agroniaga_demo di PostgreSQL port $($PgInfo.Port)."
        }
    }

    $privSql = @"
REVOKE ALL ON DATABASE agroniaga_dev FROM agroniaga_demo;
REVOKE ALL ON DATABASE agroniaga_test FROM agroniaga_demo;
GRANT ALL PRIVILEGES ON DATABASE agroniaga_demo TO agroniaga_demo;
"@
    $privSql | & wsl.exe -u root -- su - postgres -c "psql -p $($PgInfo.Port) -v ON_ERROR_STOP=1"
    if ($LASTEXITCODE -ne 0) {
        throw "Gagal mengatur hak akses database agroniaga_demo."
    }

    "GRANT ALL ON SCHEMA public TO agroniaga_demo;" | & wsl.exe -u root -- su - postgres -c "psql -p $($PgInfo.Port) -d agroniaga_demo -v ON_ERROR_STOP=1"
    if ($LASTEXITCODE -ne 0) {
        throw "Gagal memberi hak schema public pada database agroniaga_demo."
    }

    if (-not (Test-DemoPgConnection -PythonExe $PythonExe -DatabaseUrl $DatabaseUrl)) {
        throw "Database agroniaga_demo sudah dibuat, tetapi koneksi dengan password di backend/.env.demo gagal. Periksa apakah role agroniaga_demo sebelumnya dibuat dengan password berbeda."
    }
    Write-Host "[OK] Database agroniaga_demo berhasil disiapkan secara terisolasi." -ForegroundColor Green
}

$repoRoot = Get-DemoRepoRoot
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"
$uvExe = Join-Path $backendDir ".venv\Scripts\uv.exe"
$alembicExe = Join-Path $backendDir ".venv\Scripts\alembic.exe"
$envDemoExample = Join-Path $backendDir ".env.demo.example"
$envDemoFile = Join-Path $backendDir ".env.demo"
$seedScript = Join-Path $backendDir "scripts\seed_demo.py"

Write-Host "=== Setup Lingkungan Demo Lokal AgroNiaga TBS ===" -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "Python .venv backend tidak ditemukan di $pythonExe. Jalankan 'cd backend; uv sync --dev' terlebih dahulu."
}
Write-Host "[OK] Python .venv ditemukan." -ForegroundColor Green

$nodeCmd = Get-Command node.exe -ErrorAction SilentlyContinue
if ($null -eq $nodeCmd) {
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
}
$npmCmd = Get-Command npm.cmd -ErrorAction SilentlyContinue
if ($null -eq $nodeCmd -or $null -eq $npmCmd) {
    throw "Node.js / npm belum terpasang atau tidak ada di PATH."
}
Write-Host "[OK] Node.js & npm ditemukan." -ForegroundColor Green

if (-not (Test-Path -LiteralPath $envDemoFile)) {
    if (-not (Test-Path -LiteralPath $envDemoExample)) {
        throw "Template $envDemoExample tidak ditemukan."
    }
    Write-Host "[INFO] Membuat backend/.env.demo dari template dengan secret lokal acak..." -ForegroundColor Cyan
    $demoDbPass = New-RandomUrlSafeSecret -NumBytes 16
    $demoSessionSecret = New-RandomUrlSafeSecret -NumBytes 32
    $templateText = Get-Content -LiteralPath $envDemoExample -Raw -Encoding UTF8
    $generatedText = $templateText.Replace("CHANGE_ME_LOCAL_DEMO_PASSWORD", $demoDbPass).Replace(
        "REPLACE_WITH_LOCAL_RANDOM_48BYTE_SESSION_SECRET_DO_NOT_USE_IN_PROD", $demoSessionSecret
    )
    Set-Content -LiteralPath $envDemoFile -Value $generatedText -Encoding UTF8
}

$demoVars = Read-DemoEnvFile -EnvFilePath $envDemoFile
$pgInfo = Parse-PgConnectionInfo -DatabaseUrl ([string]$demoVars["DATABASE_URL"])
$redisInfo = Parse-RedisConnectionInfo -RedisUrl ([string]$demoVars["REDIS_URL"])

if (-not (Test-TcpPort -HostName $pgInfo.Host -Port $pgInfo.Port)) {
    throw "PostgreSQL tidak aktif di $($pgInfo.Host):$($pgInfo.Port). Jalankan service PostgreSQL lokal terlebih dahulu."
}
Write-Host "[OK] PostgreSQL aktif di $($pgInfo.Host):$($pgInfo.Port)." -ForegroundColor Green

if (-not (Test-RedisDbReady -HostName $redisInfo.Host -Port $redisInfo.Port -DbIndex $redisInfo.DbIndex)) {
    throw "Redis tidak merespons atau gagal memilih DB /$($redisInfo.DbIndex) di $($redisInfo.Host):$($redisInfo.Port)."
}
Write-Host "[OK] Redis aktif dan DB /$($redisInfo.DbIndex) siap." -ForegroundColor Green

Push-Location $backendDir
try {
    & $pythonExe -B -c "import faker" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[INFO] Menginstal dependensi backend (termasuk Faker) via uv..." -ForegroundColor Cyan
        if (Test-Path -LiteralPath $uvExe) {
            & $uvExe sync --dev
        }
        else {
            uv sync --dev
        }
        if ($LASTEXITCODE -ne 0) {
            throw "Gagal menjalankan uv sync --dev di backend/."
        }
    }
    Write-Host "[OK] Dependensi Python & Faker siap." -ForegroundColor Green
}
finally {
    Pop-Location
}

$viteEntry = Join-Path $frontendDir "node_modules\vite\bin\vite.js"
if (-not (Test-Path -LiteralPath $viteEntry)) {
    Write-Host "[INFO] Menginstal dependensi frontend (npm ci)..." -ForegroundColor Cyan
    Push-Location $frontendDir
    try {
        & $npmCmd.Source ci
        if ($LASTEXITCODE -ne 0) {
            throw "Gagal menjalankan npm ci di frontend/."
        }
    }
    finally {
        Pop-Location
    }
}
Write-Host "[OK] Dependensi frontend siap." -ForegroundColor Green

Ensure-DemoDatabaseAndRole -PythonExe $pythonExe -DatabaseUrl ([string]$demoVars["DATABASE_URL"]) -PgInfo $pgInfo

Write-Host "[INFO] Menjalankan migrasi Alembic ke HEAD pada agroniaga_demo..." -ForegroundColor Cyan
Push-Location $backendDir
try {
    Invoke-WithChildEnv -EnvOverrides $demoVars -Action {
        & $alembicExe upgrade head
        if ($LASTEXITCODE -ne 0) {
            throw "Migrasi Alembic ke agroniaga_demo gagal."
        }
        $currentRev = (& $alembicExe current | Out-String).Trim()
        if ($LASTEXITCODE -ne 0 -or -not $currentRev.Contains("0011_b10_reporting_indexes")) {
            throw "Revisi Alembic agroniaga_demo tidak berada di HEAD 0011_b10_reporting_indexes. Output: $currentRev"
        }
        Write-Host "[OK] Alembic berada di HEAD: $currentRev" -ForegroundColor Green
    }

    Write-Host "[INFO] Menjalankan Faker seeder idempotent ke agroniaga_demo..." -ForegroundColor Cyan
    $seedArgs = @("-B", $seedScript, "--env-file", $envDemoFile)
    if ($ResetDemo) {
        if ($ConfirmDatabase -ne "agroniaga_demo") {
            throw "Untuk reset demo, wajib menyertakan: -ResetDemo -ConfirmDatabase agroniaga_demo"
        }
        $seedArgs += @("--reset-demo", "--confirm-reset", "agroniaga_demo")
        if ($Yes) {
            $seedArgs += "--yes"
        }
    }

    Invoke-WithChildEnv -EnvOverrides $demoVars -Action {
        & $pythonExe @seedArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Seeding demo gagal dengan kode keluar $LASTEXITCODE."
        }
    }
}
finally {
    Pop-Location
}

$credPath = Join-Path $backendDir ".demo-credentials.local.txt"
Write-Host ""
Write-Host "=== Setup Demo Selesai ===" -ForegroundColor Green
Write-Host "Database Demo : $($pgInfo.Database) ($($pgInfo.Host):$($pgInfo.Port))"
Write-Host "Redis Demo    : $($redisInfo.Host):$($redisInfo.Port)/$($redisInfo.DbIndex)"
Write-Host "Kredensial    : $credPath (jangan di-commit ke Git)"
Write-Host "Langkah lanjut: .\scripts\demo-start.ps1"
