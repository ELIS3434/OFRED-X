@echo off
REM 🔥 AntiBot-Response-Manager - Build & Pack for Windows
REM Complete packaging script for GitHub distribution

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║    🔥 AntiBot-Response-Manager - Build ^& Pack v1.0 (WINDOWS)       ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

echo 📁 Creating directory structure...
if not exist "AntiBot-Response-Manager" mkdir AntiBot-Response-Manager
cd AntiBot-Response-Manager
if not exist "src" mkdir src
if not exist "tests" mkdir tests
if not exist "config" mkdir config
if not exist "docs" mkdir docs
if not exist ".github\workflows" mkdir .github\workflows
if not exist "data" mkdir data
if not exist "logs" mkdir logs

cd ..

echo 📄 Creating configuration files...

REM .env.example
(
echo # 🔐 REDDIT CREDENTIALS
echo REDDIT_CLIENT_ID=your_client_id_here
echo REDDIT_CLIENT_SECRET=your_client_secret_here
echo REDDIT_USERNAME=your_reddit_username
echo REDDIT_PASSWORD=your_reddit_password
echo REDDIT_USER_AGENT=AntiBot-Response-Manager/1.0
echo.
echo # 🤖 OPENAI API
echo OPENAI_API_KEY=sk-your-api-key-here
echo.
echo # 💾 DATABASE
echo DATABASE_PATH=data/antibot.db
echo LOG_FILE=logs/antibot.log
echo.
echo # 🔧 CONFIGURATION
echo BOT_SCORE_THRESHOLD=0.6
echo TIMEOUT=30
echo.
echo # 🌍 ENVIRONMENT
echo DEBUG=false
echo ENV=production
) > AntiBot-Response-Manager\.env.example

REM .gitignore
(
echo __pycache__/
echo *.py[cod]
echo .env
echo .vscode/
echo .idea/
echo data/
echo logs/
echo *.db
echo .pytest_cache/
) > AntiBot-Response-Manager\.gitignore

REM requirements.txt
copy requirements.txt AntiBot-Response-Manager\ >nul

REM README.md
(
echo # 🔥 AntiBot-Response-Manager
echo.
echo [Python 3.10+] ^| [License: GPL-3.0]
echo.
echo 🚀 Advanced Anti-Bot Response System for Reddit ^& OnlyFans
echo.
echo ## 🎯 Features
echo.
echo - ✅ AI Response Generator - GPT-3.5 Turbo
echo - ✅ 8-Layer Bot Detection - ML + behavioral analysis
echo - ✅ Reddit Integration - PRAW API
echo - ✅ Modern GUI - CustomTkinter
echo - ✅ Real-time Monitoring - Statistics dashboard
echo.
echo ## 🚀 Quick Start
echo.
echo ```bash
echo git clone https://github.com/yourusername/AntiBot-Response-Manager.git
echo cd AntiBot-Response-Manager
echo pip install -r requirements.txt
echo cp .env.example .env
echo python src/main.py
echo ```
echo.
echo ## 📄 License
echo.
echo GPL-3.0 - See LICENSE file
) > AntiBot-Response-Manager\README.md

REM LICENSE
(
echo GNU GENERAL PUBLIC LICENSE
echo Version 3, 29 June 2007
echo.
echo Copyright (C) 2026 Your Name
echo.
echo This program is free software: you can redistribute it and/or modify
echo it under the terms of the GNU General Public License as published by
echo the Free Software Foundation, either version 3 of the License, or
echo (at your option) any later version.
echo.
echo For full GPL-3.0 text, visit: https://www.gnu.org/licenses/gpl-3.0.html
) > AntiBot-Response-Manager\LICENSE

REM Dockerfile
(
echo FROM python:3.11-slim
echo WORKDIR /app
echo COPY requirements.txt .
echo RUN pip install --no-cache-dir -r requirements.txt
echo COPY src/ /app/src/
echo COPY config/ /app/config/
echo RUN mkdir -p /app/{data,logs}
echo CMD ["python", "src/main.py"]
) > AntiBot-Response-Manager\Dockerfile

REM config/bot_signatures.json
(
echo {
echo   "rapid_fire": {"min_msgs": 5, "time_window": 10, "weight": 0.25},
echo   "repetitive": {"pattern_threshold": 0.7, "weight": 0.20},
echo   "generic_responses": {"weight": 0.15},
echo   "unusual_caps": {"ratio_threshold": 0.4, "weight": 0.15},
echo   "emoji_spam": {"threshold": 0.3, "weight": 0.10},
echo   "url_bomber": {"url_threshold": 3, "weight": 0.10}
echo }
) > AntiBot-Response-Manager\config\bot_signatures.json

REM config/personas.json
(
echo {
echo   "friendly": {"temperature": 0.85},
echo   "professional": {"temperature": 0.7},
echo   "casual": {"temperature": 0.9},
echo   "humorous": {"temperature": 0.95},
echo   "sympathetic": {"temperature": 0.8}
echo }
) > AntiBot-Response-Manager\config\personas.json

REM Copy main application
echo 🔧 Copying application files...
copy complete_antibot_full.py AntiBot-Response-Manager\src\main.py >nul

REM Create __init__.py
type nul > AntiBot-Response-Manager\src\__init__.py
type nul > AntiBot-Response-Manager\tests\__init__.py

echo.
echo ✅ All files created successfully!
echo.
echo 📦 Creating ZIP package...

REM PowerShell ZIP command (Windows 7+)
powershell -nologo -noprofile -command "& { Add-Type -A System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::CreateFromDirectory('AntiBot-Response-Manager', 'AntiBot-Response-Manager-v1.0.zip'); }"

echo.
echo ✅ Package created: AntiBot-Response-Manager-v1.0.zip
echo.
echo 📁 Contents:
echo    ├─ src/main.py ^(Full application^)
echo    ├─ config/ ^(Configuration files^)
echo    ├─ docs/ ^(Documentation^)
echo    ├─ .env.example ^(Environment template^)
echo    ├─ requirements.txt ^(Dependencies^)
echo    ├─ Dockerfile
echo    ├─ README.md
echo    └─ LICENSE
echo.
echo 🚀 Next steps:
echo    1. Extract ZIP file
echo    2. Run: pip install -r requirements.txt
echo    3. Configure: cp .env.example .env ^(edit with your API keys^)
echo    4. Run: python src/main.py
echo.
echo 🎉 Ready to upload to GitHub!
echo.
pause
