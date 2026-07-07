@echo off
echo ========================================
echo  Finesse3 Optics Simulator — Setup
echo ========================================
echo.

REM Check conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: conda not found. Install Miniconda first:
    echo   https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

REM Create environment
echo Creating conda environment: finesse_sim ...
call conda create -n finesse_sim python=3.12 -y 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to create conda environment.
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo Installing dependencies ...
call conda run -n finesse_sim pip install finesse numpy scipy networkx flask 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Some packages may not have installed correctly.
    echo Try manually:
    echo   conda activate finesse_sim
    echo   pip install finesse numpy scipy networkx flask
)

echo.
echo ========================================
echo  Setup complete!
echo.
echo  To launch:
echo    run.bat
echo.
echo  Or manually:
echo    conda activate finesse_sim
echo    python launcher.py
echo ========================================
pause
