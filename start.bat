@echo off
echo ===================================================
echo  Aegis Infrastructure Advisor - Unified Start Script
echo ===================================================
echo.
echo Launching 3-Tier Distributed System:
echo 1. MCP Database Server   -> Port 8001 (SSE Background Service)
echo 2. FastAPI Backend API   -> Port 8000 (REST & Multi-Agent API)
echo 3. Angular SPA Frontend  -> Port 4200 (Dashboard UI)
echo.

start "MCP Server (Port 8001)" cmd /k "%~dp0start_mcp.bat"
timeout /t 3 /nobreak >nul

start "FastAPI Backend (Port 8000)" cmd /k "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul

start "Angular Frontend (Port 4200)" cmd /k "%~dp0start_frontend.bat"

echo ===================================================
echo All 3 services have been started in separate windows!
echo - Angular Dashboard: http://localhost:4200
echo - FastAPI Backend:   http://localhost:8000
echo - MCP SSE Server:    http://127.0.0.1:8001/sse
echo ===================================================
pause
