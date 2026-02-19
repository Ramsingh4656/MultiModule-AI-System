@echo off
echo ========================================
echo   AI Productivity Suite - Startup
echo ========================================
echo.

echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "venv\Scripts\activate && python main.py"
cd ..

echo Waiting for backend to initialize...
timeout /t 10 /nobreak > nul

echo Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Servers Starting...
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/api/docs
echo.
echo Press any key to exit...
pause > nul