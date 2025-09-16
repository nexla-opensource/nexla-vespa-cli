@echo off
REM Vespa Nexla Plugin CLI - Windows Version
echo Starting Vespa Nexla Plugin...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    echo Please download and install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "main.py" (
    echo Error: main.py not found. Please run this script from the plugin directory.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install/upgrade pip
echo Updating pip...
python -m pip install --upgrade pip

REM Install requirements
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    echo Warning: requirements.txt not found. Some dependencies may be missing.
)

REM Run the main application
echo.
echo ===========================================
echo    Welcome to Vespa Nexla Plugin CLI
echo ===========================================
echo.
python main.py

REM Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)

REM Deactivate virtual environment
call deactivate 2>nul