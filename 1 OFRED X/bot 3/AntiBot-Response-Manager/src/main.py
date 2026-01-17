#!/usr/bin/env python3
"""
🔥 AntiBot-Response-Manager
Complete Anti-Bot Response System for Reddit & OnlyFans
Version: 1.0.0
Author: Your Name
License: GPL-3.0
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
# BOT DETECTION ENGINE
# ============================================================================

class BotDetectionEngine:
    """
    🤖 Machine Learning-based Bot Detection System
    8-Layer Analysis: Velocity + Length + Linguistics + Timing + ML
    """
    
    def __init__(self, config_path: str = None):
        self.logger = Logger("BotDetector")
        
        # Load bot signatures
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.bot_signatures = json.load(f)
        else:
            self.bot_signatures = self._default_signatures()
        
        # Initialize ML models
        self.user_behaviors: Dict[str, UserBehavior] = {}
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.training_data = []
        
    def _default_signatures(self) -> Dict:
        """Default bot signatures"""
        return {
            "rapid_fire": {"min_msgs": 5, "time_window": 10, "weight": 0.25},
            "repetitive": {"pattern_threshold": 0.7, "weight": 0.20},
            "generic_responses": {
                "keywords": [
                    "check out my profile", "subscribe now", "link in bio",
                    "follow for more", "dm me", "click here", "only fans",
                    "🔥🔥🔥", "💯💯💯", "👀👀👀"
                ],
                "weight": 0.15
            },
            "suspicious_timing": {"std_dev_threshold": 0.5, "weight": 0.10},
            "unusual_caps": {"ratio_threshold": 0.4, "weight": 0.15},
            "emoji_spam": {"threshold": 0.3, "weight": 0.10},
            "url_bomber": {"url_threshold": 3, "weight": 0.10}
        }
    
    def extract_features(self, text: str, user: UserBehavior) -> np.ndarray:
        """Extract 8 behavioral features"""
        
        # 1. Message velocity (msg/second)
        if len(user.timestamps) > 1:
            recent_times = user.timestamps[-5:]
            time_diffs = np.diff(recent_times)
            message_velocity = 1.0 / (np.mean(time_diffs) + 1e-6)
        else:
            message_velocity = 0.0
        
        # 2. Message length anomaly
        if user.message_lengths:
            length_std = np.std(user.message_lengths) if len(user.message_lengths) > 1 else 0
            length_mean = np.mean(user.message_lengths)
            current_length = len(text)
            length_anomaly = abs(current_length - length_mean) / (length_std + 1)
        else:
            length_anomaly = 0.0
        
        # 3. Capitalization ratio
        caps_ratio = sum(1 for c in text if c.isupper()) / (len(text) + 1)
        
        # 4. Punctuation ratio
        punct_ratio = sum(1 for c in text if c in '!?.,-;:') / (len(text) + 1)
        
        # 5. Emoji ratio
        emoji_ratio = len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', text)) / (len(text) + 1)
        
        # 6. URL count
        url_count = len(re.findall(r'http[s]?://\S+', text))
        
        # 7. Word uniqueness
        words = text.lower().split()
        unique_ratio = len(set(words)) / (len(words) + 1)
        
        # 8. Response timing anomaly
        if len(user.timestamps) > 1:
            recent_interval = user.timestamps[-1] - user.timestamps[-2]
            avg_interval = np.mean(np.diff(user.timestamps))
            timing_anomaly = recent_interval / (avg_interval + 1e-6)
        else:
            timing_anomaly = 0.0
        
        features = np.array([
            message_velocity,
            length_anomaly,
            caps_ratio,
            punct_ratio,
            emoji_ratio,
            url_count,
            unique_ratio,
            timing_anomaly,
        ])
        
        return features
    
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
    Uses GPT-3.5-turbo + humanization techniques
    """
    
    def __init__(self, api_key: str):
        self.logger = Logger("ResponseGen")
        self.client = OpenAI(api_key=api_key)
        self.response_cache = {}
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
    
    def generate_response(self,
                         incoming_msg: str,
                         context: str = "",
                         persona: str = "friendly") -> str:
        """Generate AI response with humanization"""
        
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
            default = f"Hey! Thanks for reaching out. {random.choice(['What brings you here?', 'How can I help?', 'What\'s up?'])}"
            return default

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
# MAIN GUI APPLICATION
# ============================================================================

class AntiBot ResponseGUI(ctk.CTk):
    """🔥 Main GUI Application"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("🔥 AntiBot-Response-Manager v1.0")
        self.geometry("1300x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.logger = Logger("GUI")
        
        # Initialize components
        self.bot_detector = BotDetectionEngine()
        self.response_generator: Optional[HumanResponseGenerator] = None
        self.reddit_manager: Optional[RedditManager] = None
        
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
            text="🚀 AntiBot-Response-Manager - Advanced Anti-Bot System",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="AI-Powered Natural Responses + ML-Based Bot Detection for Reddit & OnlyFans",
            font=ctk.CTkFont(size=12),
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
        self.tab_monitor = self.tabview.add("📊 Monitor")
        
        # Setup tabs
        self.setup_auth_tab()
        self.setup_bot_tab()
        self.setup_response_tab()
        self.setup_reddit_tab()
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
            text="🤖 OpenAI API Key",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(25, 10))
        
        ctk.CTkLabel(frame, text="API Key", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.openai_key = ctk.CTkEntry(
            frame,
            width=500,
            show="*",
            placeholder_text="sk-..."
        )
        self.openai_key.pack(anchor="w", pady=2)
        
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
        
        test_btn = ctk.CTkButton(
            button_frame,
            text="🧪 Test Credentials",
            command=self.test_credentials,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        test_btn.pack(side="left", padx=5)
        
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
            placeholder_text="reddit_username or account_name"
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
            text="✨ AI Response Generator",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 15))
        
        # === INCOMING MESSAGE ===
        ctk.CTkLabel(frame, text="Incoming message:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        self.response_input = ctk.CTkTextbox(frame, height=100, width=600, corner_radius=8)
        self.response_input.pack(fill="x", pady=2)
        
        # === PERSONA SELECTION ===
        ctk.CTkLabel(frame, text="Persona:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(15, 2))
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
            
            if not all(reddit_creds.values()) or not openai_key:
                messagebox.showwarning("⚠️ Missing Fields", "Please fill all required fields!")
                return
            
            # Initialize managers
            self.reddit_manager = RedditManager(reddit_creds)
            self.response_generator = HumanResponseGenerator(openai_key)
            
            if self.reddit_manager.authenticated:
                self.auth_status.configure(text="✅ All systems authenticated!", text_color="green")
                messagebox.showinfo("✅ Success", "Credentials saved and authenticated successfully!")
                self.logger.info("Credentials saved successfully")
            else:
                self.auth_status.configure(text=f"❌ {self.reddit_manager.error}", text_color="red")
                messagebox.showerror("❌ Auth Error", f"Reddit authentication failed:\n{self.reddit_manager.error}")
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error saving credentials:\n{str(e)}")
            self.logger.error(f"Credential save error: {str(e)}")
    
    def test_credentials(self):
        """Test credentials"""
        messagebox.showinfo("ℹ️ Test", "Fill credentials first, then click 'Save All Credentials' to test automatically!")
    
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
            messagebox.showerror("❌ Not Authenticated", "Please authenticate OpenAI API first!")
            return
        
        incoming = self.response_input.get("1.0", "end").strip()
        persona = self.persona_var.get()
        
        if not incoming:
            messagebox.showwarning("⚠️ Input Required", "Please enter an incoming message!")
            return
        
        # Show loading
        self.response_output.delete("1.0", "end")
        self.response_output.insert("1.0", "⏳ Generating response... (this may take a few seconds)")
        self.update()
        
        try:
            response = self.response_generator.generate_response(incoming, persona=persona)
            
            self.response_output.delete("1.0", "end")
            self.response_output.insert("1.0", response)
            self.logger.info(f"Generated response ({persona}): {response[:50]}...")
            
        except Exception as e:
            self.response_output.delete("1.0", "end")
            self.response_output.insert("1.0", f"❌ Error: {str(e)}\n\nMake sure your OpenAI API key is valid!")
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
   Date: {datetime.fromtimestamp(msg['created']).strftime('%Y-%m-%d %H:%M:%S')}
   ID: {msg['id']}
{'-'*60}
"""
        
        self.reddit_messages.delete("1.0", "end")
        self.reddit_messages.insert("1.0", text)
    
    def send_reddit_message(self):
        """Send Reddit message"""
        if not self.reddit_manager or not self.reddit_manager.authenticated:
            messagebox.showerror("❌ Not Authenticated", "Please authenticate Reddit first!")
            return
        
        username = self.reply_username.get().strip()
        subject = self.reply_subject.get().strip()
        message = self.reply_message.get("1.0", "end").strip()
        
        if not all([username, subject, message]):
            messagebox.showwarning("⚠️ Missing Fields", "Fill username, subject, and message!")
            return
        
        if self.reddit_manager.send_message(username, subject, message):
            messagebox.showinfo("✅ Sent", f"Message sent to {username}!")
            self.reply_username.delete(0, "end")
            self.reply_subject.delete(0, "end")
            self.reply_message.delete("1.0", "end")
            self.logger.info(f"Sent message to {username}")
        else:
            messagebox.showerror("❌ Error", "Failed to send message!")
    
    def refresh_stats(self):
        """Refresh statistics display"""
        stats_text = """
╔════════════════════════════════════════════════════════════════════════╗
║               📊 BOT DETECTION ENGINE STATISTICS                       ║
╚════════════════════════════════════════════════════════════════════════╝

📈 OVERALL STATISTICS:
  ├─ Total Unique Users Analyzed: {total_users}
  ├─ Total Messages Analyzed: {total_messages}
  ├─ Training Data Points: {training_points}
  └─ ML Model Status: {"Ready" if self.bot_detector.training_data else "Warming Up"}

👥 USER PROFILES (Last 10):
{user_stats}

🤖 BOT SIGNATURES LOADED:
  ├─ Rapid-Fire Detection: {"✅ Enabled" if "rapid_fire" in self.bot_detector.bot_signatures else "❌ Disabled"}
  ├─ Repetition Analysis: {"✅ Enabled" if "repetitive" in self.bot_detector.bot_signatures else "❌ Disabled"}
  ├─ Generic Response Detection: {"✅ Enabled" if "generic_responses" in self.bot_detector.bot_signatures else "❌ Disabled"}
  ├─ Capitalization Anomaly: {"✅ Enabled" if "unusual_caps" in self.bot_detector.bot_signatures else "❌ Disabled"}
  ├─ Emoji Spam Detection: {"✅ Enabled" if "emoji_spam" in self.bot_detector.bot_signatures else "❌ Disabled"}
  ├─ URL Bombing Detection: {"✅ Enabled" if "url_bomber" in self.bot_detector.bot_signatures else "❌ Disabled"}
  └─ ML Anomaly Detection: {"✅ Enabled" if self.bot_detector.isolation_forest else "❌ Disabled"}

✨ RESPONSE GENERATOR STATUS:
  └─ {
    "🤖 OpenAI API Connected" if self.response_generator else "⚠️ Not Authenticated"
  }

🔗 REDDIT INTEGRATION:
  └─ {
    "✅ Connected & Authenticated" if self.reddit_manager and self.reddit_manager.authenticated else "⚠️ Not Authenticated"
  }
        """.format(
            total_users=len(self.bot_detector.user_behaviors),
            total_messages=sum(u.message_count for u in self.bot_detector.user_behaviors.values()),
            training_points=len(self.bot_detector.training_data),
            user_stats="\n".join([
                f"  {i+1}. {uid}: {u.message_count} msgs, {len(u.unique_patterns)} patterns"
                for i, (uid, u) in enumerate(list(self.bot_detector.user_behaviors.items())[:10])
            ]) if self.bot_detector.user_behaviors else "  (No users analyzed yet)"
        )
        
        self.monitor_stats.delete("1.0", "end")
        self.monitor_stats.insert("1.0", stats_text)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Launch application"""
    app = AntiBot ResponseGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
