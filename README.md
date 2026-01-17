# OFRED-X
ANTI-BOT RESPONSE pro ONLYFANS REDDIT 


# 🔥 Anti-Bot Response System

> **Advanced AI-Powered Bot Detection & Response Generation System for Reddit & OnlyFans**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey)](https://github.com)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com)

A comprehensive anti-bot system that combines **Machine Learning-based bot detection** with **AI-powered response generation** for managing messages on Reddit and OnlyFans platforms. Features an intuitive GUI, 8-layer bot detection engine, and multiple response generation modes.

---

<img width="162" height="112" alt="image" src="https://github.com/user-attachments/assets/354faa2d-c453-4528-b6dc-83f865a7a451" />


## ✨ Features

### 🤖 **8-Layer Bot Detection Engine**
- ✅ **Rapid-fire messaging detection** - Identifies suspicious message patterns
- ✅ **Repetitive pattern analysis** - Detects copy-paste behavior
- ✅ **Generic/template response detection** - Flags bot-like responses
- ✅ **Abnormal capitalization analysis** - Identifies unusual text patterns
- ✅ **Emoji spam detection** - Catches excessive emoji usage
- ✅ **URL bombing detection** - Flags suspicious link patterns
- ✅ **ML anomaly detection** - Uses Isolation Forest for advanced detection
- ✅ **Behavioral tracking** - Monitors user patterns over time

### 💬 **Response Generation**
- ✅ **AI Mode** - GPT-3.5 Turbo with humanization techniques
- ✅ **Category Mode** - 19 pre-defined response categories (OnlyFans)
- ✅ **Auto Mode** - Automatic category detection from message content
- ✅ **5 Personas** - friendly, professional, casual, humorous, sympathetic
- ✅ **Humanization** - Adds typos, filler words, and natural variations

### 🔗 **Platform Integration**
- ✅ **Reddit** - Full integration via PRAW API
  - Message fetching
  - Auto-reply with bot detection
  - Manual message management
- ✅ **OnlyFans** - Category-based response system
  - 19 response categories
  - Sequential/random message selection
  - Custom message management

### 📊 **Monitoring & Analytics**
- ✅ Real-time statistics dashboard
- ✅ User behavior tracking
- ✅ Bot score history
- ✅ System status monitoring
- ✅ Detailed logging system

### 🎨 **Modern GUI**
- ✅ Dark mode interface (CustomTkinter)
- ✅ Tabbed interface for easy navigation
- ✅ Real-time updates
- ✅ Clipboard integration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (3.12+ recommended)
- pip package manager
- Reddit API credentials (optional but recommended)
- OpenAI API key (optional, for AI responses)

### Installation

#### Windows (Automated)

```bash
# Run the automated installer
start_antibot.bat
```

The script will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Launch the application

#### Linux/Mac (Manual)

```bash
# 1. Clone the repository
git clone <repository-url>
cd "1 OFRED X"

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python "ANT OFRED X.py"
```

### Configuration

1. **Reddit API** (Required for Reddit features):
   - Go to: https://www.reddit.com/prefs/apps
   - Click "Create App"
   - Copy `client_id` and `client_secret`
   - Enter in the application (Authentication tab)

2. **OpenAI API** (Optional, for AI responses):
   - Go to: https://platform.openai.com/api-keys
   - Create a new API key
   - Enter in the application (Authentication tab)

3. **OnlyFans** (Optional):
   - Currently uses category-based responses
   - No API key required for basic functionality

---

## 📖 Usage

### 🔐 Authentication

1. Open the **Authentication** tab
2. Enter your Reddit credentials
3. (Optional) Enter OpenAI API key
4. Click **"💾 Save All Credentials"**

### 🤖 Bot Detection

1. Open the **Bot Detector** tab
2. Enter username and message to analyze
3. Click **"🔍 Analyze Message"**
4. Review the bot score and analysis results

**Bot Score Threshold**: 0.6 (60%) - Configurable in code

### 💬 Response Generation

1. Open the **Response Generator** tab
2. Select platform (Reddit/OnlyFans)
3. Choose response type:
   - **Auto**: Automatic category detection
   - **AI**: GPT-3.5 generation (requires API key)
   - **Category**: Select specific category
4. Enter incoming message
5. Click **"✨ Generate Response"**
6. Copy the generated response

### 🔗 Reddit Integration

1. Open the **Reddit** tab
2. **Fetch Messages**: Retrieve unread messages
3. **Auto-Reply**: Automatically reply with bot detection
   - Analyzes each message
   - Blocks bots (score > 0.6)
   - Generates and sends responses
4. **Manual Reply**: Send custom messages

### 💎 OnlyFans Categories

1. Open the **OnlyFans** tab
2. Select a category from dropdown
3. Click **"📋 Get Message"**
4. Copy message to clipboard

**Available Categories** (19 total):
- `teasing`, `blowjob`, `pussylick`, `pussy`, `squirt`
- `asshole`, `ass`, `cum`, `joi`, `dominant`
- `cuckold`, `balls`, `massive`, `bundle`, `support`
- `ivyvip`, `ambervip`, `vrajeli`, `dickrate`

### 📊 Monitoring

1. Open the **Monitor** tab
2. View real-time statistics:
   - Total users tracked
   - Bot detection engine status
   - Platform connection status
   - Response generation status
3. Click **"🔄 Refresh Statistics"** to update

---

## 📁 Project Structure

```
1 OFRED X/
├── ANT OFRED X.py          # Main application file
├── ANTOFRED.py             # Alternative implementation
├── requirements.txt        # Python dependencies
├── start_antibot.bat       # Windows installer script
├── README.md               # This file
├── README_KOMPLETNY_ANTIBOT.md  # Detailed documentation (PL)
├── QUICK_START.md         # Quick start guide
├── INSTALL_FIX.md         # Installation troubleshooting
├── OFresponse.js           # Response categories (JavaScript)
│
├── bot/                    # Chatbot module
│   ├── main.py
│   ├── prompt_analyzer.py
│   └── ...
│
├── bot 2/                  # Additional modules
│   └── readme.md
│
└── bot 3/                  # AntiBot components
    ├── complete_antibot_full.py
    ├── script.js
    └── ...
```

---

## 🔧 Configuration

### Bot Detection Threshold

Default threshold: **0.6** (60%)

To modify, edit `ANT OFRED X.py`:
```python
is_bot = self.bot_detector.is_likely_bot(bot_score, threshold=0.6)
```

### Response Generation

**Without OpenAI API Key:**
- System uses category-based responses only
- Automatic category detection from message content

**With OpenAI API Key:**
- AI generation with humanization
- Fallback to categories on error
- 5 persona options available

---

## 🛠️ Troubleshooting

### Installation Issues

**Problem**: `numpy` installation fails on Python 3.12
```bash
# Solution: Use updated requirements.txt
pip install -r requirements.txt
# numpy>=1.26.0 is required for Python 3.12+
```

**Problem**: `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

**Problem**: GUI doesn't load
```bash
pip uninstall customtkinter -y
pip install customtkinter>=5.2.0
```

### Runtime Issues

**Problem**: Reddit authentication failed
- Verify credentials at: https://www.reddit.com/prefs/apps
- Ensure user_agent is unique
- Check client_id and client_secret

**Problem**: OpenAI API key invalid
- Verify key at: https://platform.openai.com/api-keys
- Ensure key starts with "sk-"
- Check if key is active (not revoked)

**Problem**: OnlyFans features not working
- OnlyFans API requires custom implementation
- Currently supports category-based responses only
- See documentation for custom API integration

---

## 📊 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Bot Analysis | ~100ms | ML inference |
| AI Response Gen | ~2-3s | GPT API call |
| Category Response | ~10ms | Instant |
| Message Send | ~500ms | API call |
| DB Query | ~10ms | SQLite (if used) |

---

## 🔒 Security & Privacy

⚠️ **Important Security Notes:**

1. **Never commit `.env` file** - Contains API keys
2. **Use HTTPS** for all API calls
3. **Rate limiting** - Don't spam messages
4. **Respect ToS** - Reddit/OnlyFans don't officially support bots
5. **VPN recommended** - For privacy
6. **Store credentials securely** - Use environment variables

---

## 📝 Logging

Logs are saved in `logs/antibot_YYYYMMDD.log`

Format:
```
[2026-01-17 09:00:00] [INFO] [GUI] Credentials saved successfully
[2026-01-17 09:01:30] [INFO] [BotDetector] Analyzed user123: 35.00% - ✅ Looks humanly natural
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd "1 OFRED X"

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black pylint

# Run tests (if available)
pytest tests/

# Format code
black "ANT OFRED X.py"
```

---

## 📄 License

This project is licensed under the **GPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **PRAW** - Reddit API wrapper
- **OpenAI** - GPT-3.5 API
- **CustomTkinter** - Modern GUI framework
- **scikit-learn** - Machine learning library
- **numpy** - Numerical computing

---

## 📚 Additional Documentation

- [README_KOMPLETNY_ANTIBOT.md](README_KOMPLETNY_ANTIBOT.md) - Detailed documentation (Polish)
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [INSTALL_FIX.md](INSTALL_FIX.md) - Installation troubleshooting

---

## ⚠️ Disclaimer

This software is provided for educational and research purposes. Users are responsible for:

- Complying with platform Terms of Service (Reddit, OnlyFans)
- Respecting user privacy and consent
- Following applicable laws and regulations
- Using the software ethically and responsibly

The authors are not responsible for any misuse of this software.

---

## 📞 Support

For issues, questions, or contributions:

- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

## 🎯 Roadmap

- [ ] Full OnlyFans API integration
- [ ] Additional bot detection methods
- [ ] Multi-language support
- [ ] Database integration for history
- [ ] Web dashboard
- [ ] Docker containerization
- [ ] API server mode

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ - 2026**

---

<div align="center">

**🔥 Anti-Bot Response System - Advanced Bot Detection & Response Generation**

[⬆ Back to Top](#-anti-bot-response-system)

</div>
