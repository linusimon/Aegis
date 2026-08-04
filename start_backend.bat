@echo off
echo ===================================================
echo  Starting Aegis FastAPI Backend Service (Port 8000)
echo ===================================================
echo.
set PYTHONPATH=.
set PYTHON_EXE="C:\Users\MY PC\AppData\Local\Programs\Python\Python312\python.exe"

if exist %PYTHON_EXE% (
    %PYTHON_EXE% -m app.main
) else (
    python -m app.main
)

if %errorlevel% neq 0 (
    echo [ERROR] FastAPI Backend Service crashed.
    pause
)
