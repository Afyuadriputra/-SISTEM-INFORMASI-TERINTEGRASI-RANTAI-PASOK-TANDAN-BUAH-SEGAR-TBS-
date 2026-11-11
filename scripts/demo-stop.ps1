[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_demo-common.ps1")

$state = Read-DemoState
if ($null -eq $state) {
    Write-Host "[INFO] Tidak ada sesi demo tercatat di .demo-state/pids.json. PostgreSQL, Redis, dan proses lain tidak disentuh." -ForegroundColor Yellow
    exit 0
}

$stoppedAny = $false

foreach ($svc in @("frontend", "backend")) {
    $entry = $state.$svc
    if ($null -eq $entry) {
        continue
    }
    $pidVal = [int]$entry.pid
    $startUtc = [string]$entry.startTimeUtc
    $stopped = Stop-TrackedProcessTree -ProcessId $pidVal -ExpectedStartTimeUtc $startUtc
    if ($stopped) {
        Write-Host "[OK] Proses $svc demo (PID $pidVal) berhasil dihentikan." -ForegroundColor Green
        $stoppedAny = $true
    }
    else {
        Write-Host "[INFO] Proses $svc demo (PID $pidVal) sudah berhenti atau bukan proses sesi ini; dilewati aman." -ForegroundColor Yellow
    }
}

Remove-DemoState
if ($stoppedAny) {
    Write-Host "[OK] Sesi demo dihentikan bersih. Data agroniaga_demo, PostgreSQL, dan Redis tetap terjaga." -ForegroundColor Green
}
else {
    Write-Host "[OK] State demo dibersihkan. Tidak ada proses lain yang disentuh." -ForegroundColor Green
}
