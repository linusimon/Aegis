@echo off
echo ===================================================
echo  Starting Standalone MCP SQLite Database Server (Port 8001)
echo ===================================================
echo.
set PYTHONPATH=.
set PYTHON_EXE="C:\Users\MY PC\AppData\Local\Programs\Python\Python312\python.exe"

if exist %PYTHON_EXE% (
    %PYTHON_EXE% mcp_db_server.py --transport sse --port 8001
) else (
    python mcp_db_server.py --transport sse --port 8001
)

if %errorlevel% neq 0 (
    echo [ERROR] MCP Database Server crashed.
    pause
)
