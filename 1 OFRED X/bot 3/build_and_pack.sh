#!/bin/bash
# 🔥 AntiBot-Response-Manager - Build & Pack Script
# This script packages everything for GitHub/distribution

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║    🔥 AntiBot-Response-Manager - Build & Pack v1.0                 ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p AntiBot-Response-Manager/{src,tests,config,docs,.github/workflows,data,logs}

# Copy/create main files
echo "📄 Creating configuration files..."

# .env.example
cat > AntiBot-Response-Manager/.env.example << 'EOF'
# 🔐 REDDIT CREDENTIALS
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=AntiBot-Response-Manager/1.0

# 🤖 OPENAI API
OPENAI_API_KEY=sk-your-api-key-here

# 👾 ONLYFANS (OPTIONAL)
ONLYFANS_API_KEY=your_onlyfans_api_key
ONLYFANS_SESSION_TOKEN=your_session_token

# 💾 DATABASE
DATABASE_PATH=data/antibot.db
DATABASE_BACKUP_PATH=data/backups/

# 📊 LOGGING
LOG_LEVEL=INFO
LOG_FILE=logs/antibot.log

# 🔧 CONFIGURATION
BOT_SCORE_THRESHOLD=0.6
MAX_RETRIES=3
TIMEOUT=30
ENABLE_MONITORING=true

# 🌍 ENVIRONMENT
DEBUG=false
ENV=production
EOF

# .gitignore
cat > AntiBot-Response-Manager/.gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.env.local
.env.*.local
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
data/
logs/
*.db
*.sqlite
*.sqlite3
.pytest_cache/
.coverage
htmlcov/
.tox/
Thumbs.db
EOF

# requirements.txt
cp requirements.txt AntiBot-Response-Manager/

# setup.py
cat > AntiBot-Response-Manager/setup.py << 'EOF'
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="antibot-response-manager",
    version="1.0.0",
    author="Your Name",
    description="Advanced Anti-Bot Response System for Reddit & OnlyFans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AntiBot-Response-Manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    python_requires=">=3.10",
    install_requires=[
        "customtkinter>=5.2.0",
        "praw>=7.8.0",
        "openai>=1.3.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
    ],
)
EOF

# LICENSE (GPL-3.0)
cat > AntiBot-Response-Manager/LICENSE << 'EOF'
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2026 Your Name

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

[Full GPL-3.0 text at: https://www.gnu.org/licenses/gpl-3.0.html]
EOF

# README.md
cat > AntiBot-Response-Manager/README.md << 'EOF'
# 🔥 AntiBot-Response-Manager

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue?logo=docker)](https://www.docker.com/)

> 🚀 **Advanced Anti-Bot Response System for Reddit & OnlyFans**
> 
> AI-powered natural responses + ML-based bot detection + Behavioral analysis

## 🎯 Features

- ✅ **AI Response Generator** - GPT-3.5 Turbo z humanization techniques
- ✅ **8-Layer Bot Detection** - ML + behavioral + signature analysis
- ✅ **Reddit Integration** - PRAW API dla messaging
- ✅ **Modern GUI** - CustomTkinter interface
- ✅ **Real-time Monitoring** - Live statistics dashboard
- ✅ **Anti-Detection** - Randomization + evasion techniques

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/yourusername/AntiBot-Response-Manager.git
cd AntiBot-Response-Manager

# Install
pip install -r requirements.txt

# Setup
cp .env.example .env
nano .env  # Edit API keys

# Run
python src/main.py
```

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Setup Guide](docs/SETUP.md)
- [Bot Detection Guide](docs/BOT_DETECTION.md)

## 📄 License

GPL-3.0 - See [LICENSE](LICENSE)

---

**Made with ❤️ - 2026**
EOF

# Dockerfile
cat > AntiBot-Response-Manager/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY config/ /app/config/
COPY .env.example /app/.env

RUN mkdir -p /app/{data,logs}

CMD ["python", "src/main.py"]
EOF

# docker-compose.yml
cat > AntiBot-Response-Manager/docker-compose.yml << 'EOF'
version: '3.8'

services:
  antibot:
    build: .
    container_name: antibot-response-manager
    environment:
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
      - REDDIT_USERNAME=${REDDIT_USERNAME}
      - REDDIT_PASSWORD=${REDDIT_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
EOF

# Create __init__.py files
echo "📦 Creating package files..."
touch AntiBot-Response-Manager/src/__init__.py
touch AntiBot-Response-Manager/tests/__init__.py

# config files
cat > AntiBot-Response-Manager/config/bot_signatures.json << 'EOF'
{
  "rapid_fire": {"min_msgs": 5, "time_window": 10, "weight": 0.25},
  "repetitive": {"pattern_threshold": 0.7, "weight": 0.20},
  "generic_responses": {
    "keywords": ["check out my profile", "subscribe now", "link in bio", "follow for more"],
    "weight": 0.15
  },
  "unusual_caps": {"ratio_threshold": 0.4, "weight": 0.15},
  "emoji_spam": {"threshold": 0.3, "weight": 0.10},
  "url_bomber": {"url_threshold": 3, "weight": 0.10}
}
EOF

cat > AntiBot-Response-Manager/config/personas.json << 'EOF'
{
  "friendly": {"temperature": 0.85, "tone": "casual and warm"},
  "professional": {"temperature": 0.7, "tone": "formal and helpful"},
  "casual": {"temperature": 0.9, "tone": "super relaxed"},
  "humorous": {"temperature": 0.95, "tone": "funny and witty"},
  "sympathetic": {"temperature": 0.8, "tone": "empathetic"}
}
EOF

# Copy main application file
echo "🔧 Copying application files..."
cp complete_antibot_full.py AntiBot-Response-Manager/src/main.py

# docs
cat > AntiBot-Response-Manager/docs/INSTALLATION.md << 'EOF'
# 📦 Installation Guide

## Requirements
- Python 3.10+
- pip or poetry

## Steps

1. **Clone repository**
```bash
git clone https://github.com/yourusername/AntiBot-Response-Manager.git
cd AntiBot-Response-Manager
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run**
```bash
python src/main.py
```

## Docker

```bash
docker-compose up
```
EOF

# Create ZIP
echo ""
echo "📦 Creating ZIP package..."
zip -r AntiBot-Response-Manager-v1.0.zip AntiBot-Response-Manager/

echo ""
echo "✅ Build complete!"
echo ""
echo "📦 Package created: AntiBot-Response-Manager-v1.0.zip"
echo ""
echo "📁 Contents:"
echo "   ├─ src/main.py (Full application)"
echo "   ├─ config/ (Configuration files)"
echo "   ├─ docs/ (Documentation)"
echo "   ├─ .env.example (Environment template)"
echo "   ├─ requirements.txt (Dependencies)"
echo "   ├─ Dockerfile & docker-compose.yml"
echo "   └─ README.md & LICENSE"
echo ""
echo "🚀 Next steps:"
echo "   1. Extract: unzip AntiBot-Response-Manager-v1.0.zip"
echo "   2. Install: pip install -r requirements.txt"
echo "   3. Configure: cp .env.example .env && nano .env"
echo "   4. Run: python src/main.py"
echo ""
echo "🎉 Ready to upload to GitHub!"
