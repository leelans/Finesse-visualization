# run.ps1 - Launch the Finesse3 Optics Simulator web app (single-window mode).
#
# Design:
#  * run.bat is a thin entry point that calls this script and only pauses on error.
#  * All locating / port logic is robust PowerShell (cmd.exe quoting is fragile).
#  * We then hand off to a small helper .bat that activates the conda env and
#    starts Flask IN THE SAME CONSOLE WINDOW (cmd /c, no new window), so the
#    user sees exactly ONE window: the server window. It auto-closes when the
#    server stops. A detached PowerShell poller opens the browser once the port
#    is ready, so it never blocks the main window.

$ErrorActionPreference = 'Stop'

$logFile = Join-Path $env:TEMP 'finesse_run.log'

function Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "$ts  $msg"
    try { Add-Content -Path $logFile -Value $line -Encoding ASCII } catch { }
    Write-Host $line
}

try {
    # Initialise the log file.
    try { Set-Content -Path $logFile -Value '' -Encoding ASCII -NoNewline } catch { }
    Log 'run.ps1 started'

    # ----------------------------------------------------------------------
    # Locate the finesse_sim conda env.
    # Try `conda info --base` first (needs conda on PATH), then fall back to
    # scanning well-known base directories for envs\finesse_sim\python.exe.
    # The filesystem scan is what makes this work even when double-clicking the
    # .bat (where conda may NOT be on PATH).
    # ----------------------------------------------------------------------
    $candidates = @()
    try {
        $b = (& conda info --base 2>$null)
        if ($b) {
            $b = $b.Trim().Trim('"')
            if ($b) { $candidates += $b }
        }
    } catch {
        Log "conda info --base unavailable: $_"
    }
    $candidates += "$env:USERPROFILE\.conda"
    $candidates += "$env:USERPROFILE\Miniconda3"
    $candidates += 'C:\ProgramData\anaconda3'
    $candidates += 'C:\ProgramData\Miniconda3'

    $envPython = $null
    $condaBase = $null
    foreach ($base in $candidates) {
        if (-not $base) { continue }
        $py = Join-Path $base 'envs\finesse_sim\python.exe'
        Log "checking $py"
        if (Test-Path $py) {
            $envPython = $py
            $condaBase = $base
            break
        }
    }

    if (-not $envPython) {
        Write-Host ''
        Write-Host "ERROR: the 'finesse_sim' conda environment was not found."
        Write-Host 'Run setup.bat to create it (finesse 3.x + flask).'
        Write-Host ''
        exit 1
    }
    Log "env python found: $envPython"
    Log "conda base: $condaBase"

    $condaBat = Join-Path $condaBase 'condabin\conda.bat'
    $launcher = Join-Path $PSScriptRoot 'launcher.py'
    Log "conda.bat: $condaBat"
    Log "launcher: $launcher"

    # ----------------------------------------------------------------------
    # Pick a free port starting from 5000.
    # ----------------------------------------------------------------------
    $port = 5000
    while ($port -le 5100) {
        $busy = $false
        try {
            $c = New-Object System.Net.Sockets.TcpClient
            $c.Connect('127.0.0.1', $port)
            $c.Close()
            $busy = $true
        } catch {
            $busy = $false
        }
        if (-not $busy) { break }
        $port++
    }
    Log "selected port: $port"

    # ----------------------------------------------------------------------
    # Write a tiny browser-poller .ps1 (waits for the port, then opens it).
    # Kept separate so we avoid nested quoting inside the .bat.
    # ----------------------------------------------------------------------
    $browserPs1 = Join-Path $env:TEMP 'finesse_open_browser.ps1'
    $browserPs1Content = @'
param([int]$port)
for ($i = 0; $i -lt 90; $i++) {
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $c.Connect('127.0.0.1', $port)
        $c.Close()
        Start-Process "http://localhost:$port"
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
'@
    [System.IO.File]::WriteAllText($browserPs1, $browserPs1Content, [System.Text.Encoding]::ASCII)
    Log "wrote browser poller: $browserPs1"

    # ----------------------------------------------------------------------
    # Write the helper .bat that activates the env and starts the server in the
    # SAME window. Paths are baked in at write time to dodge quoting pitfalls.
    # `cmd /c` (not /k) => the window auto-closes once the server stops.
    # ----------------------------------------------------------------------
    $lines = @(
        '@echo off'
        "echo Launching Finesse3 Optics Simulator on port $port ..."
        "echo Server URL: http://localhost:$port"
        "echo (First import of Finesse can take ~20-30s. Keep this window open; close it to stop the server.)"
        'echo.'
        "call `"$condaBat`" activate finesse_sim"
        "start `"`" /b powershell -NoProfile -ExecutionPolicy Bypass -File `"$browserPs1`" -port $port"
        "python `"$launcher`" --no-browser --port $port"
    )
    $tempBat = Join-Path $env:TEMP 'finesse_start.bat'
    [System.IO.File]::WriteAllText($tempBat, ($lines -join "`r`n"), [System.Text.Encoding]::ASCII)
    Log "wrote helper bat: $tempBat"

    # Hand off to cmd in the SAME console window. PowerShell waits here until the
    # server (and thus this window) ends.
    Log 'handing off to server window (single window)'
    & cmd.exe /c $tempBat
    Log 'run.ps1 done'
} catch {
    Log "UNEXPECTED ERROR: $_"
    Write-Host "Unexpected error: $_"
    exit 1
}
