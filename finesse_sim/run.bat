@echo off
cd /d "%~dp0"
echo Optics Simulator starting...

REM Fix conda DLL loading on some environments
set CONDA_DLL_SEARCH_MODIFICATION_ENABLE=1

REM Auto-detect conda and activate finesse_sim env
if defined CONDA_PREFIX goto :skip_activate
set "CONDA_BASE=C:\ProgramData\anaconda3"
if exist "%CONDA_BASE%\Scripts\activate.bat" (
    call "%CONDA_BASE%\Scripts\activate.bat" finesse_sim
    goto :skip_activate
)
set "CONDA_BASE=%USERPROFILE%\.conda"
if exist "%CONDA_BASE%\Scripts\activate.bat" (
    call "%CONDA_BASE%\Scripts\activate.bat" finesse_sim
)

:skip_activate
if defined CONDA_PREFIX set "PATH=%CONDA_PREFIX%\Library\bin;%PATH%"

REM Auto-detect free port (start from 5000, try up to 5100)
for /f %%p in ('powershell -NoProfile -Command "$p=5000;$t=New-Object Net.Sockets.TcpClient;while($true){try{$t.Connect('localhost',$p);$t.Close();$t=New-Object Net.Sockets.TcpClient;$p++}catch{break}};$p"') do set "APP_PORT=%%p"
echo Using port: %APP_PORT%

echo.
python launcher.py --port %APP_PORT%
echo Server stopped.
pause
