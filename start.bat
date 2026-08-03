@echo off
echo ==========================================
echo  Starting Aegis Capacity Planning Advisor
echo ==========================================
echo.
set PYTHONPATH=.
python -m app.main
if %errorlevel% neq 0 (
    echo [ERROR] Application crashed or stopped.
    pause
)
