@echo off
setlocal
cd /d %~dp0

start "mini-rag-backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --port 8000"
start "mini-rag-frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev -- --port 5173"

echo Started backend (8000) and frontend (5173) in separate windows.
endlocal
