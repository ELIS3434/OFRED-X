@echo off
echo ========================================
echo   KOMPLETNY ANTI-BOT RESPONSE SYSTEM
echo   Dla OnlyFans i Reddit
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nie jest zainstalowany!
    echo Zainstaluj Python 3.8+ z https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Tworzenie virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Aktywacja virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo [INFO] Instalacja zależności...
pip install -r requirements.txt --quiet

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] Plik .env nie istnieje!
    echo Skopiuj .env.example do .env i wypełnij credentials
    echo.
)

REM Run application
echo [INFO] Uruchamianie aplikacji...
echo.
python COMPLETE_ANTIBOT_SYSTEM.py

pause
