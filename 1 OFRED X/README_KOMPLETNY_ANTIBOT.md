# 🔥 KOMPLETNY ANTI-BOT RESPONSE SYSTEM
## Dla OnlyFans i Reddit

Kompletny system anty-bot z wykrywaniem botów, generowaniem odpowiedzi i integracją z Reddit i OnlyFans.

---

## 🎯 FEATURES

### 🤖 Bot Detection (8-Layer ML System)
- ✅ Rapid-fire messaging detection
- ✅ Repetitive pattern analysis
- ✅ Generic/template response detection
- ✅ Abnormal capitalization analysis
- ✅ Emoji spam detection
- ✅ URL bombing detection
- ✅ ML anomaly detection (Isolation Forest)

### 💬 Response Generation
- ✅ **AI Mode**: GPT-3.5 Turbo z humanization techniques
- ✅ **Category Mode**: Pre-defined kategorie odpowiedzi z script.js
- ✅ **Auto Mode**: Automatyczne wykrywanie kategorii
- ✅ 5 personas: friendly, professional, casual, humorous, sympathetic

### 🔗 Platform Integration
- ✅ **Reddit**: Pełna integracja przez PRAW API
- ✅ **OnlyFans**: Placeholder (wymaga custom implementacji)
- ✅ Auto-reply z bot detection
- ✅ Message management

### 📊 Monitoring
- ✅ Real-time statistics
- ✅ User behavior tracking
- ✅ Bot score history
- ✅ System status dashboard

---

## 🚀 INSTALACJA

### Krok 1: Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### Krok 2: Skonfiguruj API keys

Skopiuj `.env.example` do `.env` i wypełnij:

```bash
cp .env.example .env
```

Edytuj `.env`:
- **Reddit**: https://www.reddit.com/prefs/apps
- **OpenAI** (opcjonalnie): https://platform.openai.com/api-keys
- **OnlyFans**: Wymaga custom implementacji

### Krok 3: Uruchom aplikację

```bash
python COMPLETE_ANTIBOT_SYSTEM.py
```

---

## 📖 UŻYCIE

### 🔐 Authentication Tab
1. Wpisz Reddit credentials
2. (Opcjonalnie) Wpisz OpenAI API key
3. (Opcjonalnie) Wpisz OnlyFans credentials
4. Kliknij "💾 Save All Credentials"

### 🤖 Bot Detector Tab
1. Wpisz username
2. Wklej wiadomość do analizy
3. Kliknij "🔍 Analyze Message"
4. Przeczytaj wynik (bot score + powody)

### 💬 Response Generator Tab
1. Wybierz platformę (Reddit/OnlyFans)
2. Wybierz typ odpowiedzi:
   - **Auto**: Automatyczne wykrywanie
   - **AI**: Użyj GPT-3.5 (wymaga API key)
   - **Category**: Wybierz konkretną kategorię
3. Wpisz incoming message
4. Kliknij "✨ Generate Response"
5. Skopiuj odpowiedź

### 🔗 Reddit Tab
1. **Fetch Messages**: Pobierz wiadomości
2. **Auto-Reply**: Automatyczna odpowiedź z bot detection
3. **Manual Reply**: Ręczna odpowiedź

### 💎 OnlyFans Tab
1. Wybierz kategorię odpowiedzi
2. Kliknij "📋 Get Message"
3. Skopiuj wiadomość do schowka

### 📊 Monitor Tab
- Real-time statistics
- System status
- Bot detection metrics

---

## 🎨 KATEGORIE ODPOWIEDZI (OnlyFans)

System zawiera następujące kategorie odpowiedzi:

- `teasing` - Teasing messages
- `blowjob` - Blowjob-related
- `pussylick` - Pussy licking
- `pussy` - Pussy fucking
- `squirt` - Squirting
- `asshole` - Anal play
- `ass` - Ass fucking
- `cum` - Cum-related
- `joi` - Jerk off instructions
- `dominant` - Dominant messages
- `cuckold` - Cuckold content
- `balls` - Ball-related
- `massive` - Massive content
- `bundle` - Bundle offers
- `support` - Support/VIP messages
- `ivyvip` - Ivy VIP
- `ambervip` - Amber VIP
- `vrajeli` - Vrajeli messages
- `dickrate` - Dick rating

---

## ⚙️ KONFIGURACJA

### Bot Detection Threshold

Domyślny próg wykrywania botów: **0.6** (60%)

Możesz zmienić w kodzie:
```python
is_bot = self.bot_detector.is_likely_bot(bot_score, threshold=0.6)
```

### Response Generation

**Bez OpenAI API Key:**
- System używa tylko kategorii odpowiedzi
- Automatyczne wykrywanie kategorii z wiadomości

**Z OpenAI API Key:**
- AI generation z humanization
- Fallback do kategorii w przypadku błędu

---

## 🔒 BEZPIECZEŃSTWO

⚠️ **WAŻNE:**

1. **NIGDY nie commit'uj `.env`** - zawiera klucze API
2. **Use HTTPS** dla wszystkich API calls
3. **Rate limiting** - nie spam'uj wiadomościami
4. **Respect ToS** - Reddit/OnlyFans nie wspierają botów oficjalnie
5. **VPN recommended** - dla prywatności

---

## 🐛 TROUBLESHOOTING

### Problem: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Problem: "Reddit authentication failed"

1. Sprawdź credentials na: https://www.reddit.com/prefs/apps
2. Upewnij się, że user_agent jest unikalny
3. Sprawdź czy client_id i client_secret są poprawne

### Problem: "OpenAI API Key invalid"

1. Sprawdź klucz na: https://platform.openai.com/api-keys
2. Upewnij się, że klucz zaczyna się od "sk-"
3. Sprawdź czy klucz nie został zrevokowany

### Problem: GUI nie ładuje się

```bash
pip uninstall customtkinter -y
pip install customtkinter==5.2.0
```

---

## 📊 PERFORMANCE

| Operacja | Czas | Notatki |
|----------|------|---------|
| Bot Analysis | ~100ms | ML inference |
| AI Response Gen | ~2-3s | GPT API call |
| Category Response | ~10ms | Instant |
| Message Send | ~500ms | API call |

---

## 📝 LOGGING

Logi zapisywane w `logs/antibot_YYYYMMDD.log`

Format:
```
[2026-01-17 09:00:00] [INFO] [GUI] Credentials saved successfully
[2026-01-17 09:01:30] [INFO] [BotDetector] Analyzed user123: 35.00% - ✅ Looks humanly natural
```

---

## 🎬 WORKFLOW

```
┌─────────────────────────────────┐
│  GUI Application Started        │
└────────────┬────────────────────┘
             │
      ┌──────▼──────┐
      │ Authenticate│
      │ (API keys)  │
      └──────┬──────┘
             │
    ┌────────▼────────┐
    │ Fetch Messages  │
    │ (Reddit/OF API) │
    └────────┬────────┘
             │
    ┌────────▼────────────────┐
    │ Analyze Each Message    │
    │ (Bot Detection Engine)  │
    └────────┬────────────────┘
             │
    ┌────────▼─────────────┐
    │ Is Bot? (score > 0.6)│
    └────┬────────────┬────┘
         │ YES        │ NO
         │            │
    ┌────▼──┐   ┌────▼──────────┐
    │ Flag  │   │ Generate Reply │
    │       │   │ (AI/Category)  │
    └────┬──┘   └────┬──────────┘
         │           │
         └─────┬─────┘
               │
         ┌─────▼────────┐
         │ Send Message │
         │ (API)        │
         └─────┬────────┘
               │
         ┌─────▼────────┐
         │ Log Results  │
         │ Monitor      │
         └──────────────┘
```

---

## 📚 DODATKOWE ZASOBY

- [PRAW Documentation](https://praw.readthedocs.io/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [CustomTkinter Docs](https://customtkinter.tomschiffer.com/)
- [Scikit-learn ML](https://scikit-learn.org/)

---

## ⚠️ UWAGI

### OnlyFans API

OnlyFans nie ma oficjalnego publicznego API. Obecna implementacja to placeholder. Aby dodać pełną funkcjonalność, potrzebujesz:

1. **Web Scraping**: Selenium/Playwright do automatyzacji przeglądarki
2. **Unofficial API**: Reverse engineering OnlyFans API
3. **Browser Automation**: Automatyzacja logowania i wysyłania wiadomości

### Reddit API

Reddit ma oficjalne API przez PRAW. Wszystkie funkcje są w pełni zaimplementowane.

---

## 📄 LICENSE

GPL-3.0 - Free and open source

---

## 🎉 GOTOWE!

System zawiera:
- ✅ Pełny kod aplikacji
- ✅ Bot detection engine (8-layer ML)
- ✅ AI response generator (GPT-3.5)
- ✅ Category-based responses
- ✅ Reddit integration
- ✅ OnlyFans placeholder
- ✅ Modern GUI
- ✅ Full documentation

**Made with ❤️ - 2026**
