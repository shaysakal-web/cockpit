# Start Cockpit Run Desk (webui/server.py) and open the browser.
# Double-click start_run_desk.bat or run:  .\start_run_desk.ps1

param(
    [switch]$NewInstance,
    [switch]$NoBrowser,
    [int]$StartAfterPort = 0
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$ExpectedProjectId = "cockpit"
$PreferredPort = if ($env:ANALYSIS_WEB_PORT) { [int]$env:ANALYSIS_WEB_PORT } else { 8765 }

if ($NewInstance) {
    $StartPort = if ($StartAfterPort -gt 0) { $StartAfterPort + 1 } else { $PreferredPort }
    $PortsToTry = @($StartPort..($StartPort + 20))
} else {
    $PortsToTry = @($PreferredPort, 8770, 8771, 8772, 8773) | Select-Object -Unique
}

function Test-RunDeskPort([int]$Port) {
    $ping = "http://127.0.0.1:$Port/api/analyses"
    try {
        $resp = Invoke-WebRequest -Uri $ping -UseBasicParsing -TimeoutSec 2
        $j = $resp.Content | ConvertFrom-Json
        if ($j.registry_version -lt 1) {
            Write-Host "Run Desk on port $Port is outdated (registry v$($j.registry_version)); will restart."
            return $false
        }
        if ($j.project_id -ne $ExpectedProjectId) {
            Write-Host "Run Desk on port $Port is another project ($($j.project_id)); will start Cockpit desk."
            return $false
        }
        return $true
    } catch {
        return $false
    }
}

function Stop-RunDeskOnPort([int]$Port) {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) { return }
    $conns.OwningProcess | Sort-Object -Unique | ForEach-Object {
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Milliseconds 600
}

function Emit-RunDeskReady([int]$Port) {
    $script:LastRunDeskUrl = "http://127.0.0.1:$Port/"
    Write-Host "Run Desk ready: $script:LastRunDeskUrl"
}

function Open-RunDesk([int]$Port) {
    Emit-RunDeskReady $Port
    if (-not $NoBrowser) {
        Start-Process $script:LastRunDeskUrl
    }
}

Set-Location $Root

if (-not $NewInstance) {
    foreach ($p in $PortsToTry) {
        if (Test-RunDeskPort $p) {
            Write-Host "Cockpit Run Desk already running on port $p"
            Open-RunDesk $p
            exit 0
        }
    }
}

foreach ($p in $PortsToTry) {
    Stop-RunDeskOnPort $p
    Write-Host "Starting Cockpit Run Desk on port $p ..."
    $serverCmd = "Set-Location '$Root'; `$env:ANALYSIS_WEB_PORT='$p'; python webui\server.py"
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $serverCmd) -WindowStyle Minimized

    $deadline = (Get-Date).AddSeconds(15)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 400
        if (Test-RunDeskPort $p) {
            Open-RunDesk $p
            exit 0
        }
    }
    Write-Host "Port $p did not become ready; trying next port ..."
}

Write-Error "Could not start Cockpit Run Desk on any tried port. Check Python and webui/server.py."
exit 1
