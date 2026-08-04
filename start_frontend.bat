@echo off
echo ===================================================
echo  Starting Aegis Angular Frontend Application (Port 4200)
echo ===================================================
echo.
set PATH=C:\Program Files\nodejs;%PATH%
cd /d "%~dp0frontend"

if not exist node_modules (
    echo Installing Angular dependencies...
    call npm install
)

echo Launching Angular dev server on http://localhost:4200 ...
call npm start
if %errorlevel% neq 0 (
    echo [ERROR] Angular dev server failed to start.
    pause
)
