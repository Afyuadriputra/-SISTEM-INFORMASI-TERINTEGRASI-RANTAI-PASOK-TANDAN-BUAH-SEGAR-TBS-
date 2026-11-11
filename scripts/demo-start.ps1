[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_demo-common.ps1")

function Wait-Http200 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,
        [int]$TimeoutSeconds = 30,
        [int]$WatchPid = 0
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if ($WatchPid -gt 0) {
            $alive = Get-Process -Id $WatchPid -ErrorAction SilentlyContinue
            if ($null -eq $alive) {
                return $false
            }
        }
        try {
            $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($resp.StatusCode -eq 200) {
                return $true
            }
        }
        catch {
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

$repoRoot = Get-DemoRepoRoot
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$envDemoFile = Join-Path $backendDir ".env.demo"
$pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"
$seedScript = Join-Path $backendDir "scripts\seed_demo.py"
$viteEntry = Join-Path $frontendDir "node_modules\vite\bin\vite.js"

if (-not (Test-Path -LiteralPath $envDemoFile)) {
    throw "backend/.env.demo belum ada. Jalankan .\scripts\demo-setup.ps1 terlebih dahulu."
}
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "Python .venv backend tidak ditemukan. Jalankan .\scripts\demo-setup.ps1."
}
if (-not (Test-Path -LiteralPath $viteEntry)) {
    throw "frontend/node_modules belum terpasang. Jalankan .\scripts\demo-setup.ps1."
}

$existingState = Read-DemoState
if ($null -ne $existingState) {
    $beAlive = $false
    $feAlive = $false
    if ($null -ne $existingState.backend) {
        $beProc = Get-VerifiedTrackedProcess -ProcessId ([int]$existingState.backend.pid) -ExpectedStartTimeUtc ([string]$existingState.backend.startTimeUtc)
        $beAlive = ($null -ne $beProc)
    }
    if ($null -ne $existingState.frontend) {
        $feProc = Get-VerifiedTrackedProcess -ProcessId ([int]$existingState.frontend.pid) -ExpectedStartTimeUtc ([string]$existingState.frontend.startTimeUtc)
        $feAlive = ($null -ne $feProc)
    }
    if ($beAlive -and $feAlive) {
        $activeFeUrl = if ($existingState.frontend.url) { $existingState.frontend.url } else { "http://localhost:5173" }
        $activeBeUrl = if ($existingState.backend.url) { $existingState.backend.url } else { "http://127.0.0.1:8000" }
        Write-Host "[OK] Sesi demo sudah berjalan." -ForegroundColor Green
        Write-Host "Aplikasi Frontend : $activeFeUrl"
        Write-Host "Backend Health    : $activeBeUrl/health/ready"
        Write-Host "Untuk menghentikan: .\scripts\demo-stop.ps1"
        exit 0
    }
    if ($beAlive -or $feAlive) {
        throw "Ditemukan sesi demo parsial yang masih aktif di .demo-state/pids.json. Jalankan .\scripts\demo-stop.ps1 lalu coba .\scripts\demo-start.ps1 lagi."
    }
    Remove-DemoState
}

$bePort = Find-AvailableDemoPort -PreferredPort 8000
if ($bePort -ne 8000) {
    Write-Host "[INFO] Port 8000 dipakai proses lain; backend demo menggunakan port alternatif $bePort tanpa mengganggu proses pengguna." -ForegroundColor Yellow
}

$fePort = Find-AvailableDemoPort -PreferredPort 5173
if ($fePort -ne 5173) {
    Write-Host "[INFO] Port 5173 dipakai proses lain; frontend demo menggunakan port alternatif $fePort tanpa mengganggu proses pengguna." -ForegroundColor Yellow
}

$demoVars = Read-DemoEnvFile -EnvFilePath $envDemoFile
$pgInfo = Parse-PgConnectionInfo -DatabaseUrl ([string]$demoVars["DATABASE_URL"])
$redisInfo = Parse-RedisConnectionInfo -RedisUrl ([string]$demoVars["REDIS_URL"])

if (-not (Test-TcpPort -HostName $pgInfo.Host -Port $pgInfo.Port)) {
    throw "PostgreSQL tidak aktif di $($pgInfo.Host):$($pgInfo.Port)."
}
if (-not (Test-RedisDbReady -HostName $redisInfo.Host -Port $redisInfo.Port -DbIndex $redisInfo.DbIndex)) {
    throw "Redis demo DB /$($redisInfo.DbIndex) tidak siap di $($redisInfo.Host):$($redisInfo.Port)."
}

Push-Location $backendDir
try {
    Invoke-WithChildEnv -EnvOverrides $demoVars -Action {
        & $pythonExe -B $seedScript --env-file $envDemoFile --verify-only
        if ($LASTEXITCODE -ne 0) {
            throw "Data demo belum lengkap atau gagal verifikasi. Jalankan .\scripts\demo-setup.ps1."
        }
    }
}
finally {
    Pop-Location
}

$nodeCmd = Get-Command node.exe -ErrorAction SilentlyContinue
if ($null -eq $nodeCmd) {
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
}
if ($null -eq $nodeCmd) {
    throw "Node.js tidak ditemukan di PATH."
}

$stateDir = Get-DemoStateDir
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

$beOutLog = Join-Path $stateDir "backend.out.log"
$beErrLog = Join-Path $stateDir "backend.err.log"
$feOutLog = Join-Path $stateDir "frontend.out.log"
$feErrLog = Join-Path $stateDir "frontend.err.log"

$beEnv = [ordered]@{}
foreach ($k in $demoVars.Keys) {
    $beEnv[$k] = $demoVars[$k]
}
$beEnv["PYTHONUNBUFFERED"] = "1"
if ($fePort -ne 5173) {
    $beEnv["CORS_ALLOWED_ORIGINS"] = "[`"http://localhost:$fePort`",`"http://127.0.0.1:$fePort`",`"http://localhost:5173`",`"http://127.0.0.1:5173`"]"
}

$beBaseUrl = "http://127.0.0.1:$bePort"
$feBaseUrl = "http://localhost:$fePort"

Write-Host "[INFO] Menyalakan FastAPI backend demo di port $bePort (agroniaga_demo + Redis /2)..." -ForegroundColor Cyan
$beProc = Invoke-WithChildEnv -EnvOverrides $beEnv -Action {
    Start-Process -FilePath $pythonExe `
        -ArgumentList @("-B", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$bePort", "--loop", "asyncio:SelectorEventLoop") `
        -WorkingDirectory $backendDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $beOutLog `
        -RedirectStandardError $beErrLog `
        -PassThru
}
$beStartUtc = $beProc.StartTime.ToUniversalTime().ToString("o")
$feProc = $null
$feStartUtc = ""

try {
    $beReady = Wait-Http200 -Url "$beBaseUrl/health/ready" -TimeoutSeconds 30 -WatchPid $beProc.Id
    if (-not $beReady) {
        $tail = if (Test-Path -LiteralPath $beErrLog) { (Get-Content -LiteralPath $beErrLog -Tail 20 | Out-String) } else { "" }
        throw "Backend FastAPI demo gagal mencapai /health/ready. Log terakhir:`n$tail"
    }

    $readyResp = Invoke-RestMethod -Uri "$beBaseUrl/health/ready" -TimeoutSec 3
    $healthOk = ($readyResp.success -eq $true) -and ($null -ne $readyResp.data) -and ($readyResp.data.status -in @("ok", "ready"))
    if (-not $healthOk) {
        throw "Backend readiness mengembalikan status tidak sehat: $($readyResp | ConvertTo-Json -Compress)"
    }
    Write-Host "[OK] Backend demo siap di $beBaseUrl/health/ready (PG: $($readyResp.data.dependencies.postgresql), Redis: $($readyResp.data.dependencies.redis))." -ForegroundColor Green

    $feEnv = [ordered]@{
        VITE_API_MODE         = "real"
        VITE_DEMO_BANNER      = "true"
        VITE_DEV_PROXY_TARGET = $beBaseUrl
    }

    Write-Host "[INFO] Menyalakan React Vite frontend (VITE_API_MODE=real) di port $fePort..." -ForegroundColor Cyan
    $feProc = Invoke-WithChildEnv -EnvOverrides $feEnv -RemoveKeys @() -Action {
        Start-Process -FilePath $nodeCmd.Source `
            -ArgumentList @("node_modules\vite\bin\vite.js", "--host", "localhost", "--port", "$fePort", "--strictPort") `
            -WorkingDirectory $frontendDir `
            -WindowStyle Hidden `
            -RedirectStandardOutput $feOutLog `
            -RedirectStandardError $feErrLog `
            -PassThru
    }
    $feStartUtc = $feProc.StartTime.ToUniversalTime().ToString("o")

    $feReady = Wait-Http200 -Url "$feBaseUrl/" -TimeoutSeconds 30 -WatchPid $feProc.Id
    if (-not $feReady) {
        $tail = if (Test-Path -LiteralPath $feErrLog) { (Get-Content -LiteralPath $feErrLog -Tail 20 | Out-String) } else { "" }
        throw "Frontend Vite gagal siap di $feBaseUrl/. Log terakhir:`n$tail"
    }

    $proxyOk = Wait-Http200 -Url "$feBaseUrl/api/v1/public/prices" -TimeoutSeconds 15 -WatchPid $feProc.Id
    if (-not $proxyOk) {
        throw "Proxy Vite /api/v1/public/prices gagal meneruskan request ke backend $beBaseUrl."
    }
}
catch {
    if ($null -ne $feProc -and -not [string]::IsNullOrWhiteSpace($feStartUtc)) {
        Stop-TrackedProcessTree -ProcessId $feProc.Id -ExpectedStartTimeUtc $feStartUtc | Out-Null
    }
    Stop-TrackedProcessTree -ProcessId $beProc.Id -ExpectedStartTimeUtc $beStartUtc | Out-Null
    throw
}

Write-DemoState -State @{
    startedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    backend      = @{
        pid          = $beProc.Id
        startTimeUtc = $beStartUtc
        port         = $bePort
        url          = $beBaseUrl
    }
    frontend     = @{
        pid          = $feProc.Id
        startTimeUtc = $feStartUtc
        port         = $fePort
        url          = $feBaseUrl
    }
}

$credPath = Join-Path $backendDir ".demo-credentials.local.txt"
Write-Host ""
Write-Host "=== Aplikasi Demo Lokal Siap ===" -ForegroundColor Green
Write-Host "URL Aplikasi      : $feBaseUrl"
Write-Host "URL Backend Health: $beBaseUrl/health/ready"
Write-Host "Mode Frontend     : VITE_API_MODE=real (tanpa MSW) + MODE DEMO banner"
Write-Host "Database & Redis  : agroniaga_demo ($($pgInfo.Port)) + Redis /$($redisInfo.DbIndex)"
Write-Host "Kredensial Demo   : $credPath"
Write-Host "Hentikan Demo     : .\scripts\demo-stop.ps1"
