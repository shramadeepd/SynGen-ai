@echo off
setlocal enabledelayedexpansion

REM SynGen AI - Windows Startup Script
REM This script starts both the backend and frontend services

echo 🚀 Starting SynGen AI Application...

REM Check if required directories exist
if not exist "Backend" (
    echo [ERROR] Backend directory not found!
    pause
    exit /b 1
)

if not exist "Frontend\ai-agent-ui" (
    echo [ERROR] Frontend directory not found!
    pause
    exit /b 1
)

REM Function to check if a port is in use
:check_port
netstat -an | find ":%1 " | find "LISTENING" >nul
if %errorlevel% == 0 (
    exit /b 0
) else (
    exit /b 1
)

REM Start Backend
echo [INFO] Starting Backend API Server...
cd Backend

REM Check if virtual environment exists
if not exist ".venv" if not exist "venv" (
    echo [WARNING] Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    REM Activate virtual environment
    if exist ".venv" (
        call .venv\Scripts\activate.bat
    ) else (
        call venv\Scripts\activate.bat
    )
)

REM Check if port 8000 is available
call :check_port 8000
if %errorlevel% == 0 (
    echo [WARNING] Port 8000 is already in use. Backend may already be running.
) else (
    echo [INFO] Starting FastAPI server on port 8000...
    start "SynGen AI Backend" cmd /k "python main_app.py"
    echo [SUCCESS] Backend started
)

cd ..

REM Start Frontend
echo [INFO] Starting Frontend Development Server...
cd Frontend\ai-agent-ui

REM Check if node_modules exists
if not exist "node_modules" (
    echo [WARNING] Node modules not found. Installing dependencies...
    npm install
)

REM Check if port 3000 is available
call :check_port 3000
if %errorlevel% == 0 (
    echo [WARNING] Port 3000 is already in use. Frontend may already be running.
) else (
    echo [INFO] Starting Vite development server on port 3000...
    start "SynGen AI Frontend" cmd /k "npm run dev"
    echo [SUCCESS] Frontend started
)

cd ..\..

REM Wait a moment for services to start
timeout /t 5 /nobreak >nul

echo.
echo [SUCCESS] Application started successfully!
echo [INFO] Backend API: http://localhost:8000
echo [INFO] Frontend UI: http://localhost:3000
echo [INFO] API Documentation: http://localhost:8000/docs
echo.
echo Press any key to open the application in your browser...
pause >nul

REM Open browser
start http://localhost:3000

echo.
echo Application is running. Close the terminal windows to stop the services.
pause 