# One-time setup: register run-desk:// for Cockpit Run Desk.
#
# Usage (from Cockpit root):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\register_run_desk_protocol.ps1

param(
    [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Launcher = Join-Path $Root "start_run_desk.ps1"
$Protocol = "run-desk"
$Hive = "HKCU:\Software\Classes\$Protocol"

if (-not (Test-Path $Launcher)) {
    Write-Error "Missing $Launcher"
}

if ($Unregister) {
    if (Test-Path $Hive) {
        Remove-Item -Path $Hive -Recurse -Force
        Write-Host "[OK] Unregistered ${Protocol}://"
    } else {
        Write-Host "[INFO] Protocol not registered."
    }
    exit 0
}

$command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Launcher`""

New-Item -Path $Hive -Force | Out-Null
Set-ItemProperty -Path $Hive -Name "(default)" -Value "URL:Cockpit Run Desk"
Set-ItemProperty -Path $Hive -Name "URL Protocol" -Value ""

$iconKey = Join-Path $Hive "DefaultIcon"
New-Item -Path $iconKey -Force | Out-Null
Set-ItemProperty -Path $iconKey -Name "(default)" -Value "$Launcher,0"

$shellKey = Join-Path $Hive "shell\open\command"
New-Item -Path $shellKey -Force | Out-Null
Set-ItemProperty -Path $shellKey -Name "(default)" -Value $command

Write-Host "[OK] Registered ${Protocol}:// -> Cockpit start_run_desk.ps1"
Write-Host ""
Write-Host "Chrome bookmark:"
Write-Host "  Name: Run Desk"
Write-Host "  URL:  run-desk://open"
