@echo off
echo ==========================================
echo  Aegis Infrastructure Advisor Setup
echo ==========================================
echo.
echo Installing python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    exit /b %errorlevel%
)

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
)

echo.
echo Seeding database with telemetry data...
set PYTHONPATH=.
python scripts/seed_historical_data.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to seed database.
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo  Setup Completed Successfully!
echo ==========================================
pause
