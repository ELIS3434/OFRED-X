# 🚀 QUICK START - KOMPLETNY ANTI-BOT SYSTEM

## Szybka Instalacja (Windows)

### Krok 1: Uruchom instalator
```bash
start_antibot.bat
```

Skrypt automatycznie:
- ✅ Sprawdzi Python
- ✅ Utworzy virtual environment
- ✅ Zainstaluje zależności
- ✅ Uruchomi aplikację

### Krok 2: Konfiguracja API

1. **Reddit API** (wymagane):
   - Idź na: https://www.reddit.com/prefs/apps
   - Kliknij "Create App"
   - Skopiuj `client_id` i `client_secret`
   - Wpisz w aplikacji (zakładka Authentication)

2. **OpenAI API** (opcjonalne):
   - Idź na: https://platform.openai.com/api-keys
   - Utwórz nowy klucz
   - Wpisz w aplikacji (zakładka Authentication)

3. **OnlyFans** (placeholder):
   - Wymaga custom implementacji
   - Możesz używać kategorii odpowiedzi bez API

### Krok 3: Użycie

#### Bot Detection
1. Otwórz zakładkę "🤖 Bot Detector"
2. Wpisz username i wiadomość
3. Kliknij "🔍 Analyze Message"
4. Przeczytaj wynik

#### Response Generation
1. Otwórz zakładkę "💬 Response Generator"
2. Wybierz platformę (Reddit/OnlyFans)
3. Wybierz typ odpowiedzi (Auto/AI/Category)
4. Wpisz incoming message
5. Kliknij "✨ Generate Response"
6. Skopiuj odpowiedź

#### Reddit Auto-Reply
1. Otwórz zakładkę "🔗 Reddit"
2. Kliknij "🤖 Auto-Reply (Bot Detection)"
3. System automatycznie:
   - Pobierze wiadomości
   - Wykryje boty
   - Wygeneruje odpowiedzi
   - Wyśle odpowiedzi

#### OnlyFans Categories
1. Otwórz zakładkę "💎 OnlyFans"
2. Wybierz kategorię
3. Kliknij "📋 Get Message"
4. Skopiuj wiadomość

---

## 🔧 Manual Installation (Linux/Mac)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env
cp .env.example .env
nano .env  # Edit with your credentials

# 3. Run application
python COMPLETE_ANTIBOT_SYSTEM.py
```

---

## ⚠️ TROUBLESHOOTING

### Problem: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Problem: "Reddit authentication failed"
- Sprawdź credentials na https://www.reddit.com/prefs/apps
- Upewnij się, że user_agent jest unikalny

### Problem: GUI nie ładuje się
```bash
pip uninstall customtkinter -y
pip install customtkinter==5.2.0
```

---

## 📚 DALSZA DOKUMENTACJA

Zobacz `README_KOMPLETNY_ANTIBOT.md` dla pełnej dokumentacji.

---

**Gotowe! 🎉**
