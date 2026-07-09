# setup.ps1 - Create / repair the finesse_sim conda environment.
#
# Mirrors the robust approach used by run.ps1: all the fragile logic that used
# to live in a .bat (env detection, package detection, reinstall prompts, conda
# create/install) now runs in PowerShell, which does not suffer the .bat parsing
# quirks (CRLF/BOM, nested quotes from `conda info --base`, `if exist` pitfalls)
# that caused silent "flash-close" windows on some machines.
#
# Everything is logged to %TEMP%\finesse_setup.log for diagnostics.

$ErrorActionPreference = 'Stop'

$logFile = Join-Path $env:TEMP 'finesse_setup.log'
$script:condaBat = $null
$script:condaBase = $null

function Log($msg) {
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "$ts  $msg"
    try { Add-Content -Path $logFile -Value $line -Encoding ASCII } catch { }
    Write-Host $line
}

function Locate-Conda {
    # Try `conda info --base` first (needs conda on PATH), then scan standard bases.
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

    foreach ($base in $candidates) {
        if (-not $base) { continue }
        $cb = Join-Path $base 'condabin\conda.bat'
        Log "checking conda.bat: $cb"
        if (Test-Path $cb) {
            $script:condaBase = $base
            $script:condaBat = $cb
            return $true
        }
    }
    return $false
}

function Find-EnvPath($name) {
    # Authoritative env detection via `conda env list`. Covers named envs and
    # --prefix envs, and any location conda chooses - not just $condaBase\envs.
    # Returns the env's real path, or $null if not present.
    try {
        $list = & "$script:condaBat" env list 2>$null
    } catch {
        Log "conda env list failed: $_"
        return $null
    }
    $namePat = '^\s*' + [regex]::Escape($name) + '\b'
    foreach ($line in $list) {
        if ($line -match '^\s*#') { continue }   # skip comment header
        if ($line -match $namePat) {
            $tokens = ($line -split '\s+') | Where-Object { $_ -and $_ -ne '*' }
            if ($tokens.Count -ge 2) {
                return $tokens[-1].Trim()
            }
        }
    }
    return $null
}

function Get-MissingPackages($envDir) {
    $site = Join-Path $envDir 'Lib\site-packages'
    $pkgs = @('finesse', 'numpy', 'scipy', 'networkx', 'flask')
    $missing = @()
    foreach ($p in $pkgs) {
        if (-not (Test-Path (Join-Path $site $p))) {
            $missing += $p
        }
    }
    return $missing
}

function Remove-Env {
    Write-Host 'Removing existing finesse_sim environment ...'
    & $script:condaBat env remove -n finesse_sim -y
}

function Create-Env {
    Write-Host 'Creating conda environment: finesse_sim ...'
    & $script:condaBat create -n finesse_sim python=3.12 --solver=classic -y
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'ERROR: Failed to create conda environment.'
        exit 1
    }

    Write-Host 'Installing dependencies (conda-forge: finesse, numpy, scipy, networkx) ...'
    & $script:condaBat install -n finesse_sim -c conda-forge --solver=classic -y finesse numpy scipy networkx
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'ERROR: Failed to install scientific packages from conda-forge.'
        exit 1
    }

    Write-Host 'Installing Flask (pip) ...'
    & $script:condaBat run -n finesse_sim pip install flask
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'WARNING: Flask may not have installed correctly.'
        Write-Host 'Try manually:'
        Write-Host '  conda activate finesse_sim'
        Write-Host '  pip install flask'
    }
}

try {
    try { Set-Content -Path $logFile -Value '' -Encoding ASCII -NoNewline } catch { }
    Write-Host '========================================'
    Write-Host ' Finesse3 Optics Simulator - Setup'
    Write-Host '========================================'
    Write-Host ''

    if (-not (Locate-Conda)) {
        Write-Host 'ERROR: conda not found. Install Miniconda/Anaconda first:'
        Write-Host '  https://docs.conda.io/en/latest/miniconda.html'
        exit 1
    }
    Log "conda.bat: $script:condaBat"
    Log "conda base: $script:condaBase"

    $envDir = Find-EnvPath 'finesse_sim'
    $envExists = ($null -ne $envDir) -and (Test-Path (Join-Path $envDir 'python.exe'))
    if ($envExists) { Log "finesse_sim env path: $envDir" }

    if (-not $envExists) {
        Log 'finesse_sim env not found -> creating'
        Create-Env
    } else {
        Log 'finesse_sim env found -> checking packages'
        $missing = Get-MissingPackages $envDir
        if ($missing.Count -eq 0) {
            Write-Host 'Found existing environment: finesse_sim'
            Write-Host 'All required packages are already installed.'
            $ans = Read-Host 'Reinstall the environment anyway? [y/N]'
            if ($ans -match '^[yY]') {
                Remove-Env
                Create-Env
            } else {
                Write-Host 'Nothing to do - the environment is ready. You can run run.bat now.'
            }
        } else {
            Write-Host 'Found existing environment: finesse_sim'
            Write-Host "The environment exists but is missing: $($missing -join ', ')"
            $ans = Read-Host 'Reinstall the environment to fix it? [y/N]'
            if ($ans -match '^[yY]') {
                Remove-Env
                Create-Env
            } else {
                Write-Host 'Aborted. No changes made. Run setup again and choose Y to reinstall.'
                exit 0
            }
        }
    }

    Write-Host ''
    Write-Host '========================================'
    Write-Host ' Setup complete!'
    Write-Host ''
    Write-Host ' To launch:'
    Write-Host '   run.bat'
    Write-Host ''
    Write-Host ' Or manually:'
    Write-Host '   conda activate finesse_sim'
    Write-Host '   python launcher.py'
    Write-Host '========================================'
    Log 'setup done'
} catch {
    Log "UNEXPECTED ERROR: $_"
    Write-Host "Unexpected error: $_"
    exit 1
}
