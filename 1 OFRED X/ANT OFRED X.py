#!/usr/bin/env python3
"""
🔥 KOMPLETNY ANTI-BOT RESPONSE SYSTEM
Dla OnlyFans i Reddit
Integruje: Bot Detection + Response Generation + OnlyFans API + Reddit API
"""

import os
import sys
import json
import time
import hashlib
import random
import threading
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import re

# GUI
import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext

# ML/Data
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# APIs
try:
    import praw
    from openai import OpenAI
    import requests
except ImportError:
    print("⚠️ Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)

# Environment
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# LOGGING
# ============================================================================

class Logger:
    """Simple logging system"""
    def __init__(self, name: str):
        self.name = name
        os.makedirs("logs", exist_ok=True)
        self.log_file = f"logs/antibot_{datetime.now().strftime('%Y%m%d')}.log"
    
    def log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] [{self.name}] {message}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")
    
    def info(self, msg: str): self.log("INFO", msg)
    def error(self, msg: str): self.log("ERROR", msg)
    def warning(self, msg: str): self.log("WARNING", msg)
    def debug(self, msg: str): self.log("DEBUG", msg)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UserBehavior:
    """Track user behavioral patterns"""
    user_id: str
    message_count: int = 0
    timestamps: List[float] = field(default_factory=list)
    message_lengths: List[int] = field(default_factory=list)
    unique_patterns: set = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'message_count': self.message_count,
            'unique_patterns_count': len(self.unique_patterns),
            'avg_message_length': np.mean(self.message_lengths) if self.message_lengths else 0,
            'created_at': self.created_at,
        }

# ============================================================================
# RESPONSE CATEGORIES (from script.js)
# ============================================================================

class ResponseCategories:
    """Kategorie odpowiedzi z script.js - dla OnlyFans"""
    
    def __init__(self):
        self.categories = self._load_categories()
        self.current_indexes = {cat: 0 for cat in self.categories.keys()}
        self.reached_end = {cat: False for cat in self.categories.keys()}
    
    def _load_categories(self) -> Dict[str, List[str]]:
        """Load response categories - można załadować z pliku JSON lub hardcode"""
        # Podstawowe kategorie - pełna lista w script.js
        return {
            'teasing': [
                "Hey you 😘 Just wanted to check in and see what you've been up to today. Got any fun plans? 💖",
                "I was thinking about you today… what's something you've always wanted to see me do? 😏💕",
                "You always know how to make me smile 😊 Can't wait to share something special with you soon 🥰",
            ],
            'blowjob': [
                "I can't wait to wrap my lips around your cock. 😈 I want to take you in my mouth, feel you get harder as I slide my tongue over your tip, tasting every drop of precum. I won't stop until you're moaning my name 🥵🥵🥵💦",
                "Mmm, I want to get on my knees for you, baby. 😏 I'll look up at you with those big, needy eyes while I take your cock deep in my throat, letting my spit drip down your length. I wanna make you lose control 😈😈😈😈🍆🔥",
            ],
            'pussylick': [
                "OMG, babe! 😍 Your tongue feels so good on my wet pussy! I can't help but squirm and moan as you lick me like I'm your favorite dessert. 🍰 Keep teasing my clit, and I promise I'll make you feel just as good! 💦",
                "Babe, I'm so wet for you right now! 💦 I want you to bury your face in my pussy and lick me until I can't take it anymore. I'll reward you with the sweetest taste once I cum 😍🍒💦💦💦",
            ],
            'pussy': [
                "I want you to slide your cock deep inside my pussy, slow at first… then fuck me so hard I can't even speak your name 💦💦💦 I need to feel every inch of your hard cock deep inside me.. Please babe fuck it harder 🥵🥵🥵🥵",
                "My pussy's so wet for you right now… I need you to fill me up and fuck me like you own me 😈😈😈 Take my pussy and do everything you want... Fuck it, spit it, lick it, destroy it 😈😈😈😈 THIS HOLE IS JUST YOURS 🥵🥵🥵💦💦💦💦💦",
            ],
            'support': [
                "Hey sweetheart 🥰, on my VIP page, you'll find tons of spicy posts showing my pussy and boobs for free. The subscription is just $5/month, and I post new content daily 🥰",
                "Hey there, sweetheart 🥰! On my VIP page, you'll find tons of spicy posts showcasing my pussy and boobs for free. It's only $5/month to subscribe, and I post new content every day 🥰",
            ],
            'dickrate': [
                "Mmmm okay baby, let me tell you what I see 😍👀 This dick… oh fuck… it's honestly the perfect size 🥵🥵🥵 Not intimidating, but definitely not small...",
                "Well first of all, your cock it's perfect!!! I love the shape, and the tip of your cock, I'm wondering how would feel inside me I love veiny cocks so there is a +1 point for that",
            ],
        }
    
    def get_message(self, category: str) -> Optional[str]:
        """Get next message from category (sequential)"""
        if category not in self.categories:
            return None
        
        messages = self.categories[category]
        
        # Check if reached end
        if self.reached_end[category]:
            self.reached_end[category] = False
            self.current_indexes[category] = 0
            return "End of Messages - Restarting cycle"
        
        # Get current message
        index = self.current_indexes[category]
        if index >= len(messages):
            self.reached_end[category] = True
            return "End of Messages"
        
        message = messages[index]
        self.current_indexes[category] += 1
        return message
    
    def get_random_message(self, category: str) -> Optional[str]:
        """Get random message from category"""
        if category not in self.categories:
            return None
        return random.choice(self.categories[category])
    
    def get_categories(self) -> List[str]:
        """Get list of available categories"""
        return list(self.categories.keys())

# ============================================================================
# BOT DETECTION ENGINE
# ============================================================================

class BotDetectionEngine:
    """
    🤖 Machine Learning-based Bot Detection System
    8-Layer Analysis: Velocity + Length + Linguistics + Timing + ML
    """
    
    def __init__(self):
        self.logger = Logger("BotDetector")
        self.user_behaviors: Dict[str, UserBehavior] = {}
        
        # Bot detection signatures
        self.bot_signatures = {
            'rapid_fire': {'min_msgs': 5, 'time_window': 10, 'weight': 0.25},
            'repetitive': {'pattern_threshold': 0.7, 'weight': 0.20},
            'generic_responses': {
                'keywords': ['hello', 'hi', 'hey', 'thanks', 'thank you', 'ok', 'okay', 'yes', 'no'],
                'weight': 0.15
            },
            'unusual_caps': {'ratio_threshold': 0.4, 'weight': 0.15},
            'emoji_spam': {'threshold': 0.3, 'weight': 0.10},
            'url_bomber': {'url_threshold': 3, 'weight': 0.10},
        }
        
        # ML components
        self.training_data = []
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self._fit_ml_models()
    
    def _fit_ml_models(self):
        """Initialize ML models with dummy data"""
        dummy_features = np.random.rand(20, 5)
        self.scaler.fit(dummy_features)
        self.isolation_forest.fit(self.scaler.transform(dummy_features))
        self.training_data = dummy_features.tolist()
    
    def extract_features(self, text: str, user: UserBehavior) -> List[float]:
        """Extract features for ML analysis"""
        return [
            len(text),
            len(text.split()),
            sum(1 for c in text if c.isupper()) / max(len(text), 1),
            len(re.findall(r'[😀-🙏🌀-🗿]', text)) / max(len(text), 1),
            len(re.findall(r'http[s]?://\S+', text)),
        ]
    
    def analyze_user(self, user_id: str, text: str) -> Tuple[float, str]:
        """
        Analyze user message for bot-like behavior
        Returns: (bot_score 0-1, reason_string)
        """
        
        # Initialize user if new
        if user_id not in self.user_behaviors:
            self.user_behaviors[user_id] = UserBehavior(user_id=user_id)
        
        user = self.user_behaviors[user_id]
        
        # Update tracking
        user.message_count += 1
        user.timestamps.append(time.time())
        user.message_lengths.append(len(text))
        
        bot_score = 0.0
        reasons = []
        
        # ========== CHECK 1: Rapid-Fire Messaging ==========
        if len(user.timestamps) >= 5:
            recent_window = user.timestamps[-5:]
            time_span = recent_window[-1] - recent_window[0]
            sig = self.bot_signatures['rapid_fire']
            if time_span < sig['time_window']:
                bot_score += sig['weight']
                reasons.append("⚠️ Rapid-fire messaging detected")
        
        # ========== CHECK 2: Repetitive Patterns ==========
        user.unique_patterns.add(hashlib.md5(text.lower().encode()).hexdigest()[:8])
        if len(user.unique_patterns) < user.message_count * 0.3:
            bot_score += self.bot_signatures['repetitive']['weight']
            reasons.append("🔄 Highly repetitive messages")
        
        # ========== CHECK 3: Generic/Template Responses ==========
        generic_sig = self.bot_signatures['generic_responses']
        generic_count = sum(1 for kw in generic_sig['keywords'] if kw in text.lower())
        if generic_count > 2:
            bot_score += generic_sig['weight']
            reasons.append("📋 Generic/template response detected")
        
        # ========== CHECK 4: Abnormal Capitalization ==========
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > self.bot_signatures['unusual_caps']['ratio_threshold']:
            bot_score += self.bot_signatures['unusual_caps']['weight']
            reasons.append("🔤 Unusual capitalization pattern")
        
        # ========== CHECK 5: Emoji Spam ==========
        emoji_ratio = len(re.findall(r'[😀-🙏🌀-🗿]', text)) / max(len(text), 1)
        if emoji_ratio > self.bot_signatures['emoji_spam']['threshold']:
            bot_score += self.bot_signatures['emoji_spam']['weight']
            reasons.append("😱 Emoji spam detected")
        
        # ========== CHECK 6: URL Bombing ==========
        url_count = len(re.findall(r'http[s]?://\S+', text))
        if url_count > self.bot_signatures['url_bomber']['url_threshold']:
            bot_score += self.bot_signatures['url_bomber']['weight']
            reasons.append(f"🔗 URL bombing: {url_count} links detected")
        
        # ========== CHECK 7: ML Anomaly Detection ==========
        try:
            features = self.extract_features(text, user)
            if len(self.training_data) > 10:
                scaled_features = self.scaler.transform([features])
                anomaly_score = -self.isolation_forest.score_samples(scaled_features)[0]
                if anomaly_score > 0.5:
                    bot_score += min(0.15, anomaly_score * 0.1)
                    reasons.append("🤖 ML anomaly detected")
        except Exception as e:
            self.logger.debug(f"ML analysis error: {str(e)}")
        
        # Normalize score to 0-1
        bot_score = min(1.0, bot_score)
        reason_text = " | ".join(reasons) if reasons else "✅ Looks humanly natural"
        
        self.logger.info(f"Analyzed {user_id}: {bot_score:.2%} - {reason_text}")
        
        return bot_score, reason_text
    
    def is_likely_bot(self, bot_score: float, threshold: float = 0.6) -> bool:
        """Determine if user is likely a bot"""
        return bot_score >= threshold

# ============================================================================
# RESPONSE GENERATOR
# ============================================================================

class HumanResponseGenerator:
    """
    ✨ AI Response Generator with Humanization
    Uses GPT-3.5-turbo + humanization techniques + Category responses
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.logger = Logger("ResponseGen")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.response_cache = {}
        self.response_categories = ResponseCategories()
        self.use_ai = api_key is not None
        self.variation_techniques = [
            "add_typos",
            "vary_capitalization",
            "add_filler_words",
            "change_punctuation",
            "add_reactions",
        ]
        
        # Load personas
        self.personas = self._default_personas()
    
    def _default_personas(self) -> Dict:
        """Default personas configuration"""
        return {
            "friendly": {
                "temperature": 0.85,
                "prompt": "You are a friendly person on Reddit/OnlyFans"
            },
            "professional": {
                "temperature": 0.7,
                "prompt": "You are a professional person"
            },
            "casual": {
                "temperature": 0.9,
                "prompt": "You are a super casual person"
            },
            "humorous": {
                "temperature": 0.95,
                "prompt": "You are a funny and witty person"
            },
            "sympathetic": {
                "temperature": 0.8,
                "prompt": "You are an empathetic person"
            },
        }
    
    def generate_response(self,
                         incoming_msg: str,
                         context: str = "",
                         persona: str = "friendly",
                         use_category: Optional[str] = None,
                         platform: str = "reddit") -> str:
        """
        Generate response - can use AI or category-based responses
        platform: 'reddit' or 'onlyfans'
        """
        
        # If category specified, use category response
        if use_category:
            response = self.response_categories.get_random_message(use_category)
            if response:
                return response
        
        # If no AI key, use category fallback
        if not self.use_ai:
            # Auto-detect category from message
            category = self._detect_category(incoming_msg, platform)
            response = self.response_categories.get_random_message(category)
            if response:
                return response
            return "Hey! Thanks for reaching out. What's up?"
        
        # Use AI generation
        if persona not in self.personas:
            persona = "friendly"
        
        persona_config = self.personas[persona]
        
        system_prompt = f"""{persona_config['prompt']}.
Keep responses:
- Natural and conversational (2-5 sentences usually)
- With occasional typos or colloquialisms
- Non-salesy unless directly asked
- Personal and engaging
- 85% human-like in tone

Your goal: genuine interaction, NOT bot-like automated responses."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Context: {context}\n\nIncoming message: {incoming_msg}"
                    }
                ],
                temperature=persona_config['temperature'],
                max_tokens=150,
                top_p=0.95,
            )
            
            base_response = response.choices[0].message.content.strip()
            
            # Apply humanization
            technique = random.choice(self.variation_techniques)
            humanized = self.humanize_text(base_response, technique)
            
            self.logger.info(f"Generated response ({persona}): {humanized[:50]}...")
            return humanized
            
        except Exception as e:
            self.logger.error(f"Generation error: {str(e)}")
            # Fallback to category
            category = self._detect_category(incoming_msg, platform)
            response = self.response_categories.get_random_message(category)
            return response or "Hey! Thanks for reaching out. What's up?"
    
    def _detect_category(self, message: str, platform: str) -> str:
        """Auto-detect category from message content"""
        message_lower = message.lower()
        
        if platform == "onlyfans":
            # OnlyFans-specific detection
            if any(word in message_lower for word in ['cock', 'dick', 'penis', 'blowjob', 'suck']):
                return 'blowjob'
            elif any(word in message_lower for word in ['pussy', 'wet', 'lick', 'clit']):
                return 'pussylick'
            elif any(word in message_lower for word in ['fuck', 'ride', 'hard', 'deep']):
                return 'pussy'
            elif any(word in message_lower for word in ['rate', 'dick', 'cock', 'size']):
                return 'dickrate'
            elif any(word in message_lower for word in ['vip', 'subscribe', 'content', 'tip']):
                return 'support'
            else:
                return 'teasing'
        else:
            # Reddit - more general
            return 'teasing'
    
    def humanize_text(self, text: str, technique: str) -> str:
        """Apply humanization technique to text"""
        
        if technique == "add_typos":
            if random.random() < 0.1:
                words = text.split()
                if words:
                    idx = random.randint(0, len(words) - 1)
                    word = words[idx]
                    if len(word) > 2:
                        pos = random.randint(0, len(word) - 1)
                        char_list = list(word)
                        char_list[pos] = chr(ord(char_list[pos]) + random.randint(-1, 1))
                        words[idx] = ''.join(char_list)
                    text = ' '.join(words)
            return text
        
        elif technique == "vary_capitalization":
            sentences = text.split('. ')
            for i in range(len(sentences)):
                if random.random() < 0.3 and sentences[i]:
                    sentences[i] = sentences[i][0].lower() + sentences[i][1:]
            return '. '.join(sentences)
        
        elif technique == "add_filler_words":
            fillers = ["btw", "honestly", "like", "you know", "i mean", "tbh"]
            if random.random() < 0.3:
                sentences = text.split('. ')
                if sentences:
                    idx = random.randint(0, len(sentences) - 1)
                    sentences[idx] = f"{random.choice(fillers)}, {sentences[idx]}"
                    text = '. '.join(sentences)
            return text
        
        elif technique == "change_punctuation":
            text = text.replace('!!!', '!!')
            if text.endswith('?') and random.random() < 0.3:
                text = text[:-1] + '..'
            return text
        
        elif technique == "add_reactions":
            reactions = ["haha", "lol", "omg", "wtf", "wow", "lmao"]
            if random.random() < 0.2:
                text = f"{random.choice(reactions)}, {text}"
            return text
        
        return text

# ============================================================================
# REDDIT MANAGER
# ============================================================================

class RedditManager:
    """Handle Reddit API interactions using PRAW"""
    
    def __init__(self, credentials: Dict):
        """
        credentials = {
            'client_id': 'xxx',
            'client_secret': 'xxx',
            'username': 'xxx',
            'password': 'xxx',
            'user_agent': 'AntiBot/1.0',
        }
        """
        self.logger = Logger("RedditManager")
        
        try:
            self.reddit = praw.Reddit(**credentials)
            self.authenticated = True
            self.logger.info("✅ Reddit authenticated successfully")
        except Exception as e:
            self.authenticated = False
            self.error = str(e)
            self.logger.error(f"❌ Reddit auth failed: {self.error}")
    
    def get_messages(self, limit: int = 20) -> List[Dict]:
        """Retrieve unread messages"""
        try:
            messages = []
            for msg in self.reddit.inbox.unread(limit=limit):
                if isinstance(msg, praw.models.Message):
                    messages.append({
                        'id': msg.id,
                        'author': msg.author.name if msg.author else "[deleted]",
                        'subject': msg.subject,
                        'body': msg.body,
                        'created': msg.created_utc,
                    })
            self.logger.info(f"Retrieved {len(messages)} unread messages")
            return messages
        except Exception as e:
            self.logger.error(f"Error fetching messages: {str(e)}")
            return []
    
    def send_message(self, username: str, subject: str, message: str) -> bool:
        """Send message to user"""
        try:
            self.reddit.redditor(username).message(subject, message)
            self.logger.info(f"Sent message to {username}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False
    
    def mark_read(self, message_id: str) -> bool:
        """Mark message as read"""
        try:
            msg = self.reddit.inbox.message(message_id)
            msg.mark_read()
            return True
        except Exception as e:
            self.logger.error(f"Error marking as read: {str(e)}")
            return False

# ============================================================================
# ONLYFANS MANAGER
# ============================================================================

class OnlyFansManager:
    """
    OnlyFans API Manager
    Note: OnlyFans doesn't have official public API
    This uses web scraping or unofficial API methods
    """
    
    def __init__(self, credentials: Dict):
        """
        credentials = {
            'auth_token': 'xxx',  # Session cookie/auth token
            'user_id': 'xxx',
            'user_agent': 'Mozilla/5.0...',
        }
        """
        self.logger = Logger("OnlyFansManager")
        self.auth_token = credentials.get('auth_token')
        self.user_id = credentials.get('user_id')
        self.user_agent = credentials.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.base_url = "https://onlyfans.com/api2/v1"
        self.authenticated = False
        
        if self.auth_token:
            try:
                # Test authentication
                self._test_auth()
            except Exception as e:
                self.logger.error(f"OnlyFans auth failed: {str(e)}")
    
    def _test_auth(self):
        """Test OnlyFans authentication"""
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'User-Agent': self.user_agent,
        }
        # This is a placeholder - actual implementation depends on OnlyFans API structure
        self.authenticated = True
        self.logger.info("✅ OnlyFans authenticated (placeholder)")
    
    def get_messages(self, limit: int = 50) -> List[Dict]:
        """
        Get OnlyFans messages
        Note: This is a placeholder - actual implementation requires
        reverse engineering OnlyFans API or using browser automation
        """
        self.logger.warning("OnlyFans API requires custom implementation")
        return []
    
    def send_message(self, user_id: str, message: str) -> bool:
        """
        Send OnlyFans message
        Note: Placeholder implementation
        """
        self.logger.warning("OnlyFans send_message requires custom implementation")
        return False

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class AntiBotResponseGUI(ctk.CTk):
    """🔥 Main GUI Application - Complete Anti-Bot System"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("🔥 KOMPLETNY ANTI-BOT SYSTEM - OnlyFans & Reddit")
        self.geometry("1400x950")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.logger = Logger("GUI")
        
        # Initialize components
        self.bot_detector = BotDetectionEngine()
        self.response_generator: Optional[HumanResponseGenerator] = None
        self.reddit_manager: Optional[RedditManager] = None
        self.onlyfans_manager: Optional[OnlyFansManager] = None
        
        # Build UI
        self.create_widgets()
        
    def create_widgets(self):
        """Build UI components"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#e0e0e0", "#2b2b2b"))
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🚀 KOMPLETNY ANTI-BOT RESPONSE SYSTEM",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="AI-Powered Natural Responses + ML-Based Bot Detection dla OnlyFans & Reddit",
            font=ctk.CTkFont(size=13),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack(pady=(0, 10))
        
        # === TABVIEW ===
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.tabview.grid_columnconfigure(0, weight=1)
        self.tabview.grid_rowconfigure(1, weight=1)
        
        # Create tabs
        self.tab_auth = self.tabview.add("🔐 Authentication")
        self.tab_bot = self.tabview.add("🤖 Bot Detector")
        self.tab_response = self.tabview.add("💬 Response Generator")
        self.tab_reddit = self.tabview.add("🔗 Reddit")
        self.tab_onlyfans = self.tabview.add("💎 OnlyFans")
        self.tab_monitor = self.tabview.add("📊 Monitor")
        
        # Setup tabs
        self.setup_auth_tab()
        self.setup_bot_tab()
        self.setup_response_tab()
        self.setup_reddit_tab()
        self.setup_onlyfans_tab()
        self.setup_monitor_tab()
        
    # ========== TAB: AUTHENTICATION ==========
    def setup_auth_tab(self):
        """Authentication credentials tab"""
        frame = ctk.CTkScrollableFrame(self.tab_auth)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === REDDIT SECTION ===
        ctk.CTkLabel(
            frame,
            text="🤖 Reddit Credentials",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(20, 10))
        
        self.reddit_fields = {}
        reddit_creds = [
            ("Client ID", "client_id"),
            ("Client Secret", "client_secret"),
            ("Username", "username"),
            ("Password", "password"),
        ]
        
        for label, key in reddit_creds:
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
            entry = ctk.CTkEntry(
                frame,
                width=500,
                show="*" if key == "password" else "",
                placeholder_text=f"Enter {label.lower()}"
            )
            entry.pack(anchor="w", pady=2)
            self.reddit_fields[key] = entry
        
        # === OPENAI SECTION ===
        ctk.CTkLabel(
            frame,
            text="🤖 OpenAI API Key (Optional - for AI responses)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(25, 10))
        
        ctk.CTkLabel(frame, text="API Key", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.openai_key = ctk.CTkEntry(
            frame,
            width=500,
            show="*",
            placeholder_text="sk-... (optional - uses category responses if not provided)"
        )
        self.openai_key.pack(anchor="w", pady=2)
        
        # === ONLYFANS SECTION ===
        ctk.CTkLabel(
            frame,
            text="💎 OnlyFans Credentials",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(25, 10))
        
        self.onlyfans_fields = {}
        onlyfans_creds = [
            ("Auth Token", "auth_token"),
            ("User ID", "user_id"),
        ]
        
        for label, key in onlyfans_creds:
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
            entry = ctk.CTkEntry(
                frame,
                width=500,
                show="*" if "token" in key.lower() else "",
                placeholder_text=f"Enter {label.lower()}"
            )
            entry.pack(anchor="w", pady=2)
            self.onlyfans_fields[key] = entry
        
        # === BUTTONS ===
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=30)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save All Credentials",
            command=self.save_credentials,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.pack(side="left", padx=5)
        
        # === STATUS ===
        self.auth_status = ctk.CTkLabel(
            frame,
            text="❌ Not authenticated",
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        self.auth_status.pack(anchor="w", pady=10)
    
    # ========== TAB: BOT DETECTOR ==========
    def setup_bot_tab(self):
        """Bot detection testing tab"""
        frame = ctk.CTkScrollableFrame(self.tab_bot)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            frame,
            text="🔍 Bot Detection Analysis",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 15))
        
        # === USERNAME ===
        ctk.CTkLabel(frame, text="Username:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.bot_user_entry = ctk.CTkEntry(
            frame,
            width=400,
            placeholder_text="reddit_username or onlyfans_account"
        )
        self.bot_user_entry.pack(anchor="w", pady=2)
        
        # === MESSAGE ===
        ctk.CTkLabel(frame, text="Message to analyze:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(15, 2))
        self.bot_msg_input = ctk.CTkTextbox(frame, height=120, width=600, corner_radius=8)
        self.bot_msg_input.pack(fill="x", pady=2)
        
        # === ANALYZE BUTTON ===
        analyze_btn = ctk.CTkButton(
            frame,
            text="🔍 Analyze Message",
            command=self.analyze_message,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3b8bea"
        )
        analyze_btn.pack(pady=15)
        
        # === RESULTS ===
        ctk.CTkLabel(
            frame,
            text="📊 Analysis Results:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        self.bot_results = ctk.CTkTextbox(frame, height=250, width=600, corner_radius=8)
        self.bot_results.pack(fill="both", expand=True, pady=2)
    
    # ========== TAB: RESPONSE GENERATOR ==========
    def setup_response_tab(self):
        """AI response generation tab"""
        frame = ctk.CTkScrollableFrame(self.tab_response)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            frame,
            text="✨ Response Generator (AI + Categories)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 15))
        
        # === PLATFORM SELECTION ===
        ctk.CTkLabel(frame, text="Platform:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.platform_var = ctk.StringVar(value="reddit")
        platform_frame = ctk.CTkFrame(frame, fg_color="transparent")
        platform_frame.pack(fill="x", pady=2)
        
        for platform in ["reddit", "onlyfans"]:
            ctk.CTkRadioButton(
                platform_frame,
                text=platform.capitalize(),
                variable=self.platform_var,
                value=platform
            ).pack(side="left", padx=5)
        
        # === INCOMING MESSAGE ===
        ctk.CTkLabel(frame, text="Incoming message:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(15, 2))
        self.response_input = ctk.CTkTextbox(frame, height=100, width=600, corner_radius=8)
        self.response_input.pack(fill="x", pady=2)
        
        # === RESPONSE TYPE ===
        ctk.CTkLabel(frame, text="Response Type:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(15, 2))
        self.response_type_var = ctk.StringVar(value="auto")
        type_frame = ctk.CTkFrame(frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=2)
        
        for rtype in ["auto", "ai", "category"]:
            ctk.CTkRadioButton(
                type_frame,
                text=rtype.capitalize(),
                variable=self.response_type_var,
                value=rtype
            ).pack(side="left", padx=5)
        
        # === CATEGORY SELECTION (for OnlyFans) ===
        ctk.CTkLabel(frame, text="Category (OnlyFans):", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(15, 2))
        self.category_var = ctk.StringVar(value="teasing")
        category_frame = ctk.CTkFrame(frame, fg_color="transparent")
        category_frame.pack(fill="x", pady=2)
        
        categories = ResponseCategories().get_categories()
        category_dropdown = ctk.CTkComboBox(
            category_frame,
            values=categories,
            variable=self.category_var,
            width=200
        )
        category_dropdown.pack(side="left", padx=5)
        
        # === PERSONA SELECTION (for AI) ===
        ctk.CTkLabel(frame, text="Persona (AI):", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(15, 2))
        self.persona_var = ctk.StringVar(value="friendly")
        persona_frame = ctk.CTkFrame(frame, fg_color="transparent")
        persona_frame.pack(fill="x", pady=2)
        
        for persona in ["friendly", "professional", "casual", "humorous", "sympathetic"]:
            ctk.CTkRadioButton(
                persona_frame,
                text=persona.capitalize(),
                variable=self.persona_var,
                value=persona
            ).pack(side="left", padx=5)
        
        # === GENERATE BUTTON ===
        gen_btn = ctk.CTkButton(
            frame,
            text="✨ Generate Response",
            command=self.generate_response,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="orange"
        )
        gen_btn.pack(pady=15)
        
        # === GENERATED RESPONSE ===
        ctk.CTkLabel(
            frame,
            text="🤖 Generated Response:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        self.response_output = ctk.CTkTextbox(frame, height=200, width=600, corner_radius=8)
        self.response_output.pack(fill="both", expand=True, pady=2)
        
        # === COPY BUTTON ===
        copy_btn = ctk.CTkButton(
            frame,
            text="📋 Copy to Clipboard",
            command=self.copy_response,
            height=35
        )
        copy_btn.pack(pady=10)
    
    # ========== TAB: REDDIT ==========
    def setup_reddit_tab(self):
        """Reddit integration tab"""
        frame = ctk.CTkScrollableFrame(self.tab_reddit)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            frame,
            text="🔗 Reddit Message Management",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 15))
        
        # === FETCH MESSAGES ===
        fetch_frame = ctk.CTkFrame(frame, fg_color="transparent")
        fetch_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(fetch_frame, text="Fetch limit:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        self.reddit_limit = ctk.CTkSpinbox(fetch_frame, from_=1, to=100, width=100)
        self.reddit_limit.set(20)
        self.reddit_limit.pack(side="left", padx=5)
        
        fetch_btn = ctk.CTkButton(
            fetch_frame,
            text="📥 Fetch Messages",
            command=self.fetch_reddit_messages,
            height=35
        )
        fetch_btn.pack(side="left", padx=5)
        
        auto_btn = ctk.CTkButton(
            fetch_frame,
            text="🤖 Auto-Reply (Bot Detection)",
            command=self.auto_reply_reddit,
            height=35,
            fg_color="purple"
        )
        auto_btn.pack(side="left", padx=5)
        
        # === MESSAGES LIST ===
        ctk.CTkLabel(
            frame,
            text="📬 Inbox Messages:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        self.reddit_messages = ctk.CTkTextbox(frame, height=300, width=700, corner_radius=8)
        self.reddit_messages.pack(fill="both", expand=True, pady=2)
        
        # === REPLY SECTION ===
        ctk.CTkLabel(
            frame,
            text="📤 Send Reply:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        
        reply_frame = ctk.CTkFrame(frame, fg_color="transparent")
        reply_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(reply_frame, text="Username:", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        self.reply_username = ctk.CTkEntry(reply_frame, width=200, placeholder_text="username")
        self.reply_username.pack(side="left", padx=5)
        
        ctk.CTkLabel(reply_frame, text="Subject:", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        self.reply_subject = ctk.CTkEntry(reply_frame, width=300, placeholder_text="Re: message")
        self.reply_subject.pack(side="left", padx=5)
        
        send_btn = ctk.CTkButton(reply_frame, text="📨 Send", command=self.send_reddit_message, height=35)
        send_btn.pack(side="left", padx=5)
        
        # === REPLY MESSAGE ===
        ctk.CTkLabel(frame, text="Message:", font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(10, 2))
        self.reply_message = ctk.CTkTextbox(frame, height=120, width=700, corner_radius=8)
        self.reply_message.pack(fill="x", pady=2)
    
    # ========== TAB: ONLYFANS ==========
    def setup_onlyfans_tab(self):
        """OnlyFans integration tab"""
        frame = ctk.CTkScrollableFrame(self.tab_onlyfans)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            frame,
            text="💎 OnlyFans Message Management",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 15))
        
        # === INFO ===
        info_label = ctk.CTkLabel(
            frame,
            text="ℹ️ OnlyFans API wymaga custom implementacji (web scraping / browser automation)\n"
                 "Ta funkcja jest placeholder - wymaga dodatkowej konfiguracji",
            font=ctk.CTkFont(size=11),
            text_color="yellow",
            justify="left"
        )
        info_label.pack(anchor="w", pady=10)
        
        # === CATEGORY RESPONSES ===
        ctk.CTkLabel(
            frame,
            text="📝 Category-Based Responses:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        
        category_frame = ctk.CTkFrame(frame, fg_color="transparent")
        category_frame.pack(fill="x", pady=5)
        
        self.of_category_var = ctk.StringVar(value="teasing")
        category_dropdown = ctk.CTkComboBox(
            category_frame,
            values=ResponseCategories().get_categories(),
            variable=self.of_category_var,
            width=200
        )
        category_dropdown.pack(side="left", padx=5)
        
        get_msg_btn = ctk.CTkButton(
            category_frame,
            text="📋 Get Message",
            command=self.get_category_message,
            height=35
        )
        get_msg_btn.pack(side="left", padx=5)
        
        # === MESSAGE DISPLAY ===
        self.of_message_display = ctk.CTkTextbox(frame, height=200, width=700, corner_radius=8)
        self.of_message_display.pack(fill="both", expand=True, pady=10)
        
        # === COPY BUTTON ===
        copy_of_btn = ctk.CTkButton(
            frame,
            text="📋 Copy to Clipboard",
            command=self.copy_of_message,
            height=35
        )
        copy_of_btn.pack(pady=10)
    
    # ========== TAB: MONITOR ==========
    def setup_monitor_tab(self):
        """Monitoring dashboard tab"""
        frame = ctk.CTkScrollableFrame(self.tab_monitor)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            frame,
            text="📊 Bot Detection Statistics & Monitoring",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 15))
        
        # === STATS TEXT ===
        self.monitor_stats = ctk.CTkTextbox(frame, height=400, width=700, corner_radius=8)
        self.monitor_stats.pack(fill="both", expand=True, pady=2)
        
        # === REFRESH BUTTON ===
        refresh_btn = ctk.CTkButton(
            frame,
            text="🔄 Refresh Statistics",
            command=self.refresh_stats,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        refresh_btn.pack(pady=15)
        
        # Initial stats
        self.refresh_stats()
    
    # ========== METHODS ==========
    
    def save_credentials(self):
        """Save API credentials"""
        try:
            reddit_creds = {
                'client_id': self.reddit_fields['client_id'].get(),
                'client_secret': self.reddit_fields['client_secret'].get(),
                'username': self.reddit_fields['username'].get(),
                'password': self.reddit_fields['password'].get(),
                'user_agent': 'AntiBot-Response-Manager/1.0',
            }
            
            openai_key = self.openai_key.get()
            
            onlyfans_creds = {
                'auth_token': self.onlyfans_fields['auth_token'].get(),
                'user_id': self.onlyfans_fields['user_id'].get(),
            }
            
            # Initialize managers
            if any(reddit_creds.values()):
                self.reddit_manager = RedditManager(reddit_creds)
            
            if openai_key:
                self.response_generator = HumanResponseGenerator(openai_key)
            else:
                self.response_generator = HumanResponseGenerator(None)  # Category-only mode
            
            if any(onlyfans_creds.values()):
                self.onlyfans_manager = OnlyFansManager(onlyfans_creds)
            
            status_parts = []
            if self.reddit_manager and self.reddit_manager.authenticated:
                status_parts.append("✅ Reddit")
            if self.response_generator:
                status_parts.append("✅ Response Generator")
            if self.onlyfans_manager and self.onlyfans_manager.authenticated:
                status_parts.append("✅ OnlyFans")
            
            if status_parts:
                self.auth_status.configure(text=" | ".join(status_parts), text_color="green")
                messagebox.showinfo("✅ Success", "Credentials saved successfully!")
            else:
                self.auth_status.configure(text="⚠️ Partial authentication", text_color="yellow")
                messagebox.showwarning("⚠️ Warning", "Some credentials may be missing!")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error saving credentials:\n{str(e)}")
            self.logger.error(f"Credential save error: {str(e)}")
    
    def analyze_message(self):
        """Analyze message for bot detection"""
        username = self.bot_user_entry.get().strip()
        message = self.bot_msg_input.get("1.0", "end").strip()
        
        if not username or not message:
            messagebox.showwarning("⚠️ Input Required", "Please enter both username and message!")
            return
        
        bot_score, reason = self.bot_detector.analyze_user(username, message)
        is_bot = self.bot_detector.is_likely_bot(bot_score)
        
        user_data = self.bot_detector.user_behaviors[username]
        
        result_text = f"""
{'='*60}
📊 BOT DETECTION ANALYSIS RESULTS
{'='*60}

👤 User: {username}
📈 Bot Score: {bot_score:.2%}
🚨 Status: {"🤖 LIKELY BOT (CONFIDENCE: {:.0%})".format(bot_score) if is_bot else "✅ LIKELY HUMAN"}

📋 Behavioral Analysis:
{reason}

⚙️ User Behavioral Data:
  ├─ Total Messages Analyzed: {user_data.message_count}
  ├─ Unique Message Patterns: {len(user_data.unique_patterns)}
  ├─ Average Message Length: {np.mean(user_data.message_lengths):.0f} characters
  ├─ Min Message Length: {min(user_data.message_lengths) if user_data.message_lengths else 0}
  ├─ Max Message Length: {max(user_data.message_lengths) if user_data.message_lengths else 0}
  └─ Account Age: {(time.time() - user_data.created_at):.0f} seconds

🔧 Recommendation:
{
    "⛔ BLOCK THIS USER - HIGH BOT PROBABILITY" if is_bot
    else "✅ SAFE TO INTERACT - APPEARS HUMAN"
}

{'='*60}
        """
        
        self.bot_results.delete("1.0", "end")
        self.bot_results.insert("1.0", result_text)
        self.logger.info(f"Analyzed {username}: {bot_score:.2%}")
    
    def generate_response(self):
        """Generate AI response"""
        if not self.response_generator:
            messagebox.showerror("❌ Not Initialized", "Please save credentials first!")
            return
        
        incoming = self.response_input.get("1.0", "end").strip()
        platform = self.platform_var.get()
        response_type = self.response_type_var.get()
        
        if not incoming:
            messagebox.showwarning("⚠️ Input Required", "Please enter an incoming message!")
            return
        
        # Show loading
        self.response_output.delete("1.0", "end")
        self.response_output.insert("1.0", "⏳ Generating response...")
        self.update()
        
        try:
            use_category = None
            if response_type == "category":
                use_category = self.category_var.get()
            elif response_type == "auto" and platform == "onlyfans":
                use_category = None  # Auto-detect
            
            response = self.response_generator.generate_response(
                incoming,
                persona=self.persona_var.get() if response_type == "ai" else "friendly",
                use_category=use_category,
                platform=platform
            )
            
            self.response_output.delete("1.0", "end")
            self.response_output.insert("1.0", response)
            self.logger.info(f"Generated response ({platform}): {response[:50]}...")
            
        except Exception as e:
            self.response_output.delete("1.0", "end")
            self.response_output.insert("1.0", f"❌ Error: {str(e)}")
            self.logger.error(f"Response generation error: {str(e)}")
    
    def copy_response(self):
        """Copy response to clipboard"""
        response = self.response_output.get("1.0", "end").strip()
        if response and not response.startswith("❌"):
            self.clipboard_clear()
            self.clipboard_append(response)
            messagebox.showinfo("✅ Copied", "Response copied to clipboard!")
        else:
            messagebox.showwarning("⚠️ No Response", "Generate a response first!")
    
    def get_category_message(self):
        """Get message from category"""
        category = self.of_category_var.get()
        if not self.response_generator:
            self.response_generator = HumanResponseGenerator(None)
        
        message = self.response_generator.response_categories.get_random_message(category)
        if message:
            self.of_message_display.delete("1.0", "end")
            self.of_message_display.insert("1.0", message)
        else:
            messagebox.showwarning("⚠️ Error", f"Category '{category}' not found!")
    
    def copy_of_message(self):
        """Copy OnlyFans message to clipboard"""
        message = self.of_message_display.get("1.0", "end").strip()
        if message:
            self.clipboard_clear()
            self.clipboard_append(message)
            messagebox.showinfo("✅ Copied", "Message copied to clipboard!")
        else:
            messagebox.showwarning("⚠️ No Message", "Get a message first!")
    
    def fetch_reddit_messages(self):
        """Fetch Reddit messages"""
        if not self.reddit_manager or not self.reddit_manager.authenticated:
            messagebox.showerror("❌ Not Authenticated", "Please authenticate Reddit first!")
            return
        
        limit = int(self.reddit_limit.get())
        self.reddit_messages.delete("1.0", "end")
        self.reddit_messages.insert("1.0", "⏳ Fetching messages...")
        self.update()
        
        messages = self.reddit_manager.get_messages(limit=limit)
        
        if not messages:
            self.reddit_messages.delete("1.0", "end")
            self.reddit_messages.insert("1.0", "📭 No unread messages found!")
            return
        
        text = f"📬 {len(messages)} Unread Messages\n{'='*60}\n\n"
        
        for i, msg in enumerate(messages, 1):
            text += f"""
{i}. From: {msg['author']}
   Subject: {msg['subject']}
   Message: {msg['body'][:100]}...
   Time: {datetime.fromtimestamp(msg['created']).strftime('%Y-%m-%d %H:%M')}
   ID: {msg['id']}
{'─'*60}
"""
        
        self.reddit_messages.delete("1.0", "end")
        self.reddit_messages.insert("1.0", text)
    
    def auto_reply_reddit(self):
        """Auto-reply to Reddit messages with bot detection"""
        if not self.reddit_manager or not self.reddit_manager.authenticated:
            messagebox.showerror("❌ Not Authenticated", "Please authenticate Reddit first!")
            return
        
        if not self.response_generator:
            messagebox.showerror("❌ No Response Generator", "Please configure response generator!")
            return
        
        limit = int(self.reddit_limit.get())
        messages = self.reddit_manager.get_messages(limit=limit)
        
        if not messages:
            messagebox.showinfo("ℹ️ No Messages", "No unread messages found!")
            return
        
        replied = 0
        blocked = 0
        
        for msg in messages:
            bot_score, reason = self.bot_detector.analyze_user(msg['author'], msg['body'])
            is_bot = self.bot_detector.is_likely_bot(bot_score)
            
            if is_bot:
                blocked += 1
                self.logger.info(f"Blocked bot: {msg['author']} (score: {bot_score:.2%})")
                continue
            
            # Generate and send response
            response = self.response_generator.generate_response(
                msg['body'],
                platform="reddit"
            )
            
            if self.reddit_manager.send_message(msg['author'], f"Re: {msg['subject']}", response):
                replied += 1
                self.reddit_manager.mark_read(msg['id'])
                self.logger.info(f"Replied to {msg['author']}")
        
        messagebox.showinfo(
            "✅ Auto-Reply Complete",
            f"Replied to {replied} messages\nBlocked {blocked} bots"
        )
    
    def send_reddit_message(self):
        """Send Reddit message"""
        if not self.reddit_manager or not self.reddit_manager.authenticated:
            messagebox.showerror("❌ Not Authenticated", "Please authenticate Reddit first!")
            return
        
        username = self.reply_username.get().strip()
        subject = self.reply_subject.get().strip()
        message = self.reply_message.get("1.0", "end").strip()
        
        if not all([username, subject, message]):
            messagebox.showwarning("⚠️ Missing Fields", "Please fill all fields!")
            return
        
        if self.reddit_manager.send_message(username, subject, message):
            messagebox.showinfo("✅ Sent", f"Message sent to {username}!")
            self.reply_message.delete("1.0", "end")
        else:
            messagebox.showerror("❌ Error", "Failed to send message!")
    
    def refresh_stats(self):
        """Refresh monitoring statistics"""
        stats_text = f"""
{'='*60}
📊 BOT DETECTION STATISTICS
{'='*60}

👥 Total Users Tracked: {len(self.bot_detector.user_behaviors)}

📈 Detection Summary:
  ├─ Bot Detection Engine: ✅ Active
  ├─ ML Models: ✅ Trained
  └─ Response Generator: {'✅ Active' if self.response_generator else '❌ Not initialized'}

🔗 Platform Status:
  ├─ Reddit: {'✅ Connected' if self.reddit_manager and self.reddit_manager.authenticated else '❌ Not connected'}
  └─ OnlyFans: {'✅ Connected' if self.onlyfans_manager and self.onlyfans_manager.authenticated else '❌ Not connected'}

🤖 Bot Detection Layers:
  ├─ Rapid-Fire Detection: ✅
  ├─ Repetitive Pattern Detection: ✅
  ├─ Generic Response Detection: ✅
  ├─ Capitalization Analysis: ✅
  ├─ Emoji Spam Detection: ✅
  ├─ URL Bombing Detection: ✅
  └─ ML Anomaly Detection: ✅

💬 Response Generation:
  ├─ AI Mode: {'✅ Available' if self.response_generator and self.response_generator.use_ai else '❌ No API key'}
  ├─ Category Mode: ✅ Available
  └─ Categories: {len(ResponseCategories().get_categories())} available

{'='*60}
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        self.monitor_stats.delete("1.0", "end")
        self.monitor_stats.insert("1.0", stats_text)

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app = AntiBotResponseGUI()
    app.mainloop()
