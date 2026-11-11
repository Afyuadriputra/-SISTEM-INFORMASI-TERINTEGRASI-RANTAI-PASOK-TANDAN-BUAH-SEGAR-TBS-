Set-StrictMode -Version Latest

function Get-DemoRepoRoot {
    return (Split-Path -Parent $PSScriptRoot)
}

function Get-DemoStateDir {
    $repoRoot = Get-DemoRepoRoot
    return (Join-Path $repoRoot ".demo-state")
}

function Get-DemoStatePath {
    return (Join-Path (Get-DemoStateDir) "pids.json")
}

function Read-DemoEnvFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$EnvFilePath
    )

    if (-not (Test-Path -LiteralPath $EnvFilePath)) {
        throw "File konfigurasi demo tidak ditemukan: $EnvFilePath. Jalankan .\scripts\demo-setup.ps1 terlebih dahulu."
    }

    $vars = [ordered]@{}
    $lines = Get-Content -LiteralPath $EnvFilePath -Encoding UTF8
    foreach ($rawLine in $lines) {
        $line = $rawLine.Trim()
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) {
            continue
        }
        $eqIdx = $line.IndexOf("=")
        if ($eqIdx -lt 1) {
            continue
        }
        $key = $line.Substring(0, $eqIdx).Trim()
        $val = $line.Substring($eqIdx + 1).Trim()
        $vars[$key] = $val
    }

    Assert-DemoEnvIsolated -Vars $vars
    return $vars
}

function Assert-DemoEnvIsolated {
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$Vars
    )

    if (-not $Vars.Contains("DATABASE_URL") -or [string]::IsNullOrWhiteSpace([string]$Vars["DATABASE_URL"])) {
        throw "DATABASE_URL wajib ada di backend/.env.demo."
    }
    if (-not $Vars.Contains("REDIS_URL") -or [string]::IsNullOrWhiteSpace([string]$Vars["REDIS_URL"])) {
        throw "REDIS_URL wajib ada di backend/.env.demo."
    }

    $dbUrl = [string]$Vars["DATABASE_URL"]
    $redisUrl = [string]$Vars["REDIS_URL"]

    if ($dbUrl -match "CHANGE_ME_LOCAL_DEMO_PASSWORD") {
        throw "DATABASE_URL di backend/.env.demo masih berisi placeholder. Jalankan .\scripts\demo-setup.ps1 atau ganti password lokal."
    }
    if ($Vars.Contains("SESSION_SECRET") -and ([string]$Vars["SESSION_SECRET"] -match "REPLACE_WITH_LOCAL_RANDOM")) {
        throw "SESSION_SECRET di backend/.env.demo masih berisi placeholder."
    }

    $pgInfo = Parse-PgConnectionInfo -DatabaseUrl $dbUrl
    if ($pgInfo.Database -ne "agroniaga_demo") {
        throw "DITOLAK: DATABASE_URL pada konfigurasi demo harus mengarah ke database 'agroniaga_demo', bukan '$($pgInfo.Database)'."
    }

    if ($redisUrl -notmatch "/2(\?|$)") {
        throw "DITOLAK: REDIS_URL pada konfigurasi demo harus mengarah ke Redis DB '/2', bukan '$redisUrl'."
    }
}

function Parse-PgConnectionInfo {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DatabaseUrl
    )

    $normalized = $DatabaseUrl -replace "^postgresql\+psycopg://", "postgresql://" -replace "^postgres://", "postgresql://"
    $uri = [System.Uri]$normalized
    $userInfoParts = $uri.UserInfo.Split(":", 2)
    $userName = [System.Uri]::UnescapeDataString($userInfoParts[0])
    $password = ""
    if ($userInfoParts.Length -gt 1) {
        $password = [System.Uri]::UnescapeDataString($userInfoParts[1])
    }
    $dbName = $uri.AbsolutePath.TrimStart("/")
    $port = if ($uri.Port -gt 0) { $uri.Port } else { 5432 }

    return [PSCustomObject]@{
        Host     = $uri.Host
        Port     = $port
        Username = $userName
        Password = $password
        Database = $dbName
    }
}

function Parse-RedisConnectionInfo {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RedisUrl
    )

    $uri = [System.Uri]$RedisUrl
    $port = if ($uri.Port -gt 0) { $uri.Port } else { 6379 }
    $dbStr = $uri.AbsolutePath.TrimStart("/")
    $dbIndex = 0
    if (-not [string]::IsNullOrWhiteSpace($dbStr)) {
        $dbIndex = [int]$dbStr
    }
    return [PSCustomObject]@{
        Host    = $uri.Host
        Port    = $port
        DbIndex = $dbIndex
    }
}

function Test-TcpPort {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HostName,
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [int]$TimeoutMs = 1500
    )

    $ipAddr = $null
    $client = $null
    try {
        if ([System.Net.IPAddress]::TryParse($HostName, [ref]$ipAddr)) {
            $client = New-Object System.Net.Sockets.TcpClient($ipAddr.AddressFamily)
        }
        else {
            $client = New-Object System.Net.Sockets.TcpClient
        }
        $iar = $client.BeginConnect($HostName, $Port, $null, $null)
        $connected = $iar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)
        if (-not $connected) {
            return $false
        }
        $client.EndConnect($iar)
        return $true
    }
    catch {
        return $false
    }
    finally {
        if ($null -ne $client) {
            $client.Close()
        }
    }
}

function Test-RedisDbReady {
    param(
        [Parameter(Mandatory = $true)]
        [string]$HostName,
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [Parameter(Mandatory = $true)]
        [int]$DbIndex
    )

    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect($HostName, $Port, $null, $null)
        if (-not $iar.AsyncWaitHandle.WaitOne(2000, $false)) {
            return $false
        }
        $client.EndConnect($iar)
        $client.ReceiveTimeout = 2000
        $client.SendTimeout = 2000

        $stream = $client.GetStream()
        $dbText = [string]$DbIndex
        $cmd = "*1`r`n`$4`r`nPING`r`n*2`r`n`$6`r`nSELECT`r`n`$$($dbText.Length)`r`n$dbText`r`n"
        $bytes = [System.Text.Encoding]::ASCII.GetBytes($cmd)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()

        $buffer = New-Object byte[] 256
        $totalRead = 0
        $attempts = 0
        while ($totalRead -lt 10 -and $attempts -lt 5) {
            $read = $stream.Read($buffer, $totalRead, $buffer.Length - $totalRead)
            if ($read -le 0) {
                break
            }
            $totalRead += $read
            $attempts++
            $replyNow = [System.Text.Encoding]::ASCII.GetString($buffer, 0, $totalRead)
            if ($replyNow.Contains("+PONG") -and $replyNow.Contains("+OK")) {
                return $true
            }
        }
        $reply = [System.Text.Encoding]::ASCII.GetString($buffer, 0, $totalRead)
        return ($reply.Contains("+PONG") -and $reply.Contains("+OK"))
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

function Invoke-WithChildEnv {
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$EnvOverrides,
        [string[]]$RemoveKeys = @("TEST_DATABASE_URL", "TEST_REDIS_URL"),
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    $backup = @{}
    $allKeys = @($EnvOverrides.Keys) + $RemoveKeys
    foreach ($key in $allKeys) {
        if (-not $backup.ContainsKey($key)) {
            $backup[$key] = [Environment]::GetEnvironmentVariable($key, "Process")
        }
    }

    try {
        foreach ($rKey in $RemoveKeys) {
            [Environment]::SetEnvironmentVariable($rKey, $null, "Process")
        }
        foreach ($k in $EnvOverrides.Keys) {
            [Environment]::SetEnvironmentVariable([string]$k, [string]$EnvOverrides[$k], "Process")
        }
        return (& $Action)
    }
    finally {
        foreach ($k in $backup.Keys) {
            [Environment]::SetEnvironmentVariable($k, $backup[$k], "Process")
        }
    }
}

function Get-ListeningPortPids {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $pids = New-Object System.Collections.Generic.List[int]
    try {
        $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            if ($c.OwningProcess -gt 0 -and -not $pids.Contains([int]$c.OwningProcess)) {
                $pids.Add([int]$c.OwningProcess)
            }
        }
    }
    catch {
    }
    if ($pids.Count -eq 0) {
        if ((Test-TcpPort -HostName "127.0.0.1" -Port $Port -TimeoutMs 300) -or (Test-TcpPort -HostName "::1" -Port $Port -TimeoutMs 300)) {
            $pids.Add(-1)
        }
    }
    return $pids.ToArray()
}

function Find-AvailableDemoPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$PreferredPort,
        [int]$MaxOffset = 10
    )

    for ($offset = 0; $offset -le $MaxOffset; $offset++) {
        $candidate = $PreferredPort + $offset
        $busyPids = @(Get-ListeningPortPids -Port $candidate)
        if ($busyPids.Count -eq 0) {
            return $candidate
        }
    }
    throw "Tidak ada port bebas pada rentang $PreferredPort..$($PreferredPort + $MaxOffset)."
}

function Get-VerifiedTrackedProcess {
    param(
        [Parameter(Mandatory = $true)]
        [int]$ProcessId,
        [Parameter(Mandatory = $true)]
        [string]$ExpectedStartTimeUtc
    )

    $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($null -eq $proc) {
        return $null
    }
    try {
        $actualUtc = $proc.StartTime.ToUniversalTime().ToString("o")
        if ($actualUtc -eq $ExpectedStartTimeUtc) {
            return $proc
        }
    }
    catch {
        return $null
    }
    return $null
}

function Stop-DescendantsAndSelf {
    param([int]$TargetPid)
    try {
        $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $TargetPid" -ErrorAction SilentlyContinue
        foreach ($child in $children) {
            Stop-DescendantsAndSelf -TargetPid ([int]$child.ProcessId)
        }
    }
    catch {
    }
    Stop-Process -Id $TargetPid -Force -ErrorAction SilentlyContinue
}

function Stop-TrackedProcessTree {
    param(
        [Parameter(Mandatory = $true)]
        [int]$ProcessId,
        [Parameter(Mandatory = $true)]
        [string]$ExpectedStartTimeUtc
    )

    $proc = Get-VerifiedTrackedProcess -ProcessId $ProcessId -ExpectedStartTimeUtc $ExpectedStartTimeUtc
    if ($null -eq $proc) {
        return $false
    }

    Stop-DescendantsAndSelf -TargetPid $ProcessId
    try {
        $proc.WaitForExit(3000) | Out-Null
    }
    catch {
    }
    return $true
}

function Read-DemoState {
    $statePath = Get-DemoStatePath
    if (-not (Test-Path -LiteralPath $statePath)) {
        return $null
    }
    $raw = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }
    return ($raw | ConvertFrom-Json)
}

function Write-DemoState {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$State
    )

    $stateDir = Get-DemoStateDir
    if (-not (Test-Path -LiteralPath $stateDir)) {
        New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
    }
    $statePath = Get-DemoStatePath
    $json = $State | ConvertTo-Json -Depth 5
    Set-Content -LiteralPath $statePath -Value $json -Encoding UTF8
}

function Remove-DemoState {
    $statePath = Get-DemoStatePath
    if (Test-Path -LiteralPath $statePath) {
        Remove-Item -LiteralPath $statePath -Force -ErrorAction SilentlyContinue
    }
}
