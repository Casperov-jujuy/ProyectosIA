@echo off
echo Starting CV Optimizer Project...

:: Start Backend
start "CV Optimizer Backend" cmd /k "cd backend && python -m uvicorn main:app --reload"

:: Start Frontend
start "CV Optimizer Frontend" cmd /k "cd frontend && npm run dev"

echo Servers are launching in new windows.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Please wait for "Application startup complete" in the Backend window.
pause
