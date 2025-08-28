@echo off
echo ========================================
echo   Stock Transaction Manager - Local Dev
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist .venv (
    echo [1/4] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment already exists ✓
)

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Install/update dependencies
echo [3/4] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

REM Check MySQL connection
echo [4/4] Checking MySQL connection...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: MySQL not found in PATH. Make sure MySQL is running.
    echo You can start MySQL service with: net start mysql80
)

echo.
echo ========================================
echo   🚀 STARTING APPLICATION
echo ========================================
echo.
echo → Local URL: http://localhost:5000
echo → Dashboard: http://localhost:5000/dashboard
echo → Press Ctrl+C to stop the server
echo → Database will be created automatically
echo.

python app.py

echo.
echo Application stopped. Press any key to exit...
pause >nul