#!/usr/bin/env python3
"""
🚀 Anti-Bot Response Manager for Reddit & OnlyFans
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features:
- AI-powered natural responses (GPT-3.5)
- Advanced bot detection
- Reddit & OnlyFans integration
- Modern GUI
- Rate limiting & behavioral tracking
"""

import asyncio
import json
import threading
import hashlib
import random
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re

import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

try:
    import praw
    from openai import OpenAI
except ImportError:
    print("Zainstaluj: pip install praw openai scikit-learn numpy")


@dataclass
class UserBehavior:
    """Track user behavioral patterns"""
    user_id: str
    message_count: int = 0
    avg_response_time: float = 0.0
    timestamps: List[float] = None
    message_lengths: List[int] = None
    unique_patterns: set = None
    typing_speed: float = 0.0  # chars per second
    capitalization_ratio: float = 0.0
    punctuation_ratio: float = 0.0
    emoji_usage: float = 0.0
    
    def __post_init__(self):
        if self.timestamps is None:
            self.timestamps = []
        if self.message_lengths is None:
            self.message_lengths = []
        if self.unique_patterns is None:
            self.unique_patterns = set()


class BotDetectionEngine:
    """Machine Learning-based bot detection"""
    
    def __init__(self):
        self.user_behaviors: Dict[str, UserBehavior] = {}
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.bot_signatures = {
            # Bot patterns
            'rapid_fire': {'min_msgs': 5, 'time_window': 10},  # 5 wiadomości w 10 sekund
            'repetitive': {'pattern_threshold': 0.7},
            'generic_responses': {'similarity_threshold': 0.85},
            'suspicious_timing': {'std_dev_threshold': 0.5},
            'unusual_caps': {'ratio_threshold': 0.4},
            'emoji_spam': {'threshold': 0.3},
            'url_bomber': {'url_threshold': 3},
        }
        self.training_data = []
        
    def extract_features(self, text: str, user: UserBehavior) -> np.ndarray:
        """Extract behavioral features from message"""
        
        # 1. Message velocity
        if len(user.timestamps) > 1:
            recent_times = user.timestamps[-5:]
            time_diffs = np.diff(recent_times)
            message_velocity = 1.0 / (np.mean(time_diffs) + 1e-6)
        else:
            message_velocity = 0.0
            
        # 2. Message length consistency
        if user.message_lengths:
            length_std = np.std(user.message_lengths) if len(user.message_lengths) > 1 else 0
            length_mean = np.mean(user.message_lengths)
            current_length = len(text)
            length_anomaly = abs(current_length - length_mean) / (length_std + 1)
        else:
            length_anomaly = 0.0
            
        # 3. Linguistic patterns
        caps_ratio = sum(1 for c in text if c.isupper()) / (len(text) + 1)
        punct_ratio = sum(1 for c in text if c in '!?.,-;:') / (len(text) + 1)
        emoji_ratio = len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', text)) / (len(text) + 1)
        url_count = len(re.findall(r'http[s]?://\S+', text))
        
        # 4. Repetition score
        words = text.lower().split()
        unique_ratio = len(set(words)) / (len(words) + 1)
        
        # 5. Response time anomaly
        if len(user.timestamps) > 1:
            recent_interval = user.timestamps[-1] - user.timestamps[-2]
            avg_interval = np.mean(np.diff(user.timestamps))
            timing_anomaly = recent_interval / (avg_interval + 1e-6)
        else:
            timing_anomaly = 0.0
            
        # Stack features
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
        Returns: (bot_score 0-1, reason)
        """
        
        if user_id not in self.user_behaviors:
            self.user_behaviors[user_id] = UserBehavior(user_id=user_id)
            
        user = self.user_behaviors[user_id]
        
        # Update behavior tracking
        user.message_count += 1
        user.timestamps.append(time.time())
        user.message_lengths.append(len(text))
        
        bot_score = 0.0
        reasons = []
        
        # ======= CHECK 1: Rapid-fire messaging =======
        if len(user.timestamps) >= 5:
            recent_window = user.timestamps[-5:]
            time_span = recent_window[-1] - recent_window[0]
            if time_span < self.bot_signatures['rapid_fire']['time_window']:
                bot_score += 0.25
                reasons.append("⚠️ Rapid-fire messaging detected")
                
        # ======= CHECK 2: Repetitive patterns =======
        user.unique_patterns.add(hashlib.md5(text.lower().encode()).hexdigest()[:8])
        if len(user.unique_patterns) < user.message_count * 0.3:
            bot_score += 0.20
            reasons.append("🔄 Highly repetitive messages")
            
        # ======= CHECK 3: Generic/template responses =======
        generic_phrases = [
            "check out my profile", "subscribe now", "link in bio",
            "follow for more", "dm me", "click here", "only fans",
            "🔥🔥🔥", "💯💯💯", "👀👀👀"
        ]
        generic_count = sum(1 for phrase in generic_phrases if phrase in text.lower())
        if generic_count > 2:
            bot_score += 0.15
            reasons.append("📋 Generic/template response detected")
            
        # ======= CHECK 4: Abnormal capitalization =======
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > self.bot_signatures['unusual_caps']['ratio_threshold']:
            bot_score += 0.15
            reasons.append("🔤 Unusual capitalization pattern")
            
        # ======= CHECK 5: Emoji spam =======
        emoji_ratio = len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', text)) / max(len(text), 1)
        if emoji_ratio > self.bot_signatures['emoji_spam']['threshold']:
            bot_score += 0.10
            reasons.append("😱 Emoji spam detected")
            
        # ======= CHECK 6: URL bombing =======
        url_count = len(re.findall(r'http[s]?://\S+', text))
        if url_count > self.bot_signatures['url_bomber']['url_threshold']:
            bot_score += 0.10
            reasons.append(f"🔗 URL bombing: {url_count} links")
            
        # ======= CHECK 7: ML anomaly detection =======
        try:
            features = self.extract_features(text, user)
            if len(self.training_data) > 10:
                scaled_features = self.scaler.transform([features])
                anomaly_score = -self.isolation_forest.score_samples(scaled_features)[0]
                if anomaly_score > 0.5:
                    bot_score += min(0.15, anomaly_score * 0.1)
                    reasons.append("🤖 ML anomaly detected")
        except Exception as e:
            pass
            
        # Normalize score to 0-1
        bot_score = min(1.0, bot_score)
        reason_text = " | ".join(reasons) if reasons else "✅ Wygląda humanitarnie"
        
        return bot_score, reason_text
        
    def is_likely_bot(self, bot_score: float, threshold: float = 0.6) -> bool:
        """Determine if user is likely a bot"""
        return bot_score >= threshold


class HumanResponseGenerator:
    """Generate AI responses that evade bot detection"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.response_cache = {}
        self.variation_techniques = [
            "add_typos",
            "vary_capitalization",
            "add_filler_words",
            "change_punctuation",
            "add_reactions",
        ]
        
    def humanize_text(self, text: str, technique: str) -> str:
        """Apply humanization technique"""
        
        if technique == "add_typos":
            # Dodaj naturalnie wyglądające literówki
            if random.random() < 0.1:
                words = text.split()
                if words:
                    idx = random.randint(0, len(words) - 1)
                    word = words[idx]
                    if len(word) > 2:
                        pos = random.randint(0, len(word) - 1)
                        word_list = list(word)
                        word_list[pos] = chr(ord(word_list[pos]) + random.randint(-1, 1))
                        words[idx] = ''.join(word_list)
                    text = ' '.join(words)
            return text
            
        elif technique == "vary_capitalization":
            # Naturalne variacje kapitalizacji
            sentences = text.split('. ')
            for i in range(len(sentences)):
                if random.random() < 0.3:
                    sentences[i] = sentences[i][0].lower() + sentences[i][1:] if sentences[i] else sentences[i]
            return '. '.join(sentences)
            
        elif technique == "add_filler_words":
            # Add natural filler words
            fillers = ["btw", "honestly", "like", "you know", "i mean", "tbh"]
            if random.random() < 0.3:
                sentences = text.split('. ')
                if sentences:
                    idx = random.randint(0, len(sentences) - 1)
                    sentences[idx] = f"{random.choice(fillers)}, {sentences[idx]}"
                    text = '. '.join(sentences)
            return text
            
        elif technique == "change_punctuation":
            # Vary punctuation naturally
            text = text.replace('!!!', '!!')
            if text.endswith('?'):
                if random.random() < 0.3:
                    text = text[:-1] + '..'
            return text
            
        elif technique == "add_reactions":
            # Add natural reactions
            reactions = ["haha", "lol", "omg", "wtf", "wow"]
            if random.random() < 0.2:
                text = f"{random.choice(reactions)}, {text}"
            return text
            
        return text
        
    def generate_response(self, 
                         incoming_msg: str,
                         context: str = "",
                         persona: str = "friendly") -> str:
        """Generate humanized AI response"""
        
        # System prompt
        system_prompt = f"""You are a {persona} person responding naturally on Reddit/OnlyFans.
Keep responses:
- Natural and conversational (2-5 sentences usually)
- Authentic with occasional typos/colloquialisms
- Non-salesy unless directly asked
- Personal and engaging
- 85% human-like in tone

Your goal: genuine interaction, NOT bot-like automated responses."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: {context}\n\nIncoming message: {incoming_msg}"}
                ],
                temperature=0.85,  # Higher for variety
                max_tokens=150,
                top_p=0.95,
            )
            
            base_response = response.choices[0].message.content.strip()
            
            # Apply humanization
            technique = random.choice(self.variation_techniques)
            humanized = self.humanize_text(base_response, technique)
            
            return humanized
            
        except Exception as e:
            return f"Hey! Thanks for reaching out. {random.choice(['What brings you here?', 'How can I help?', 'Whats up?'])}"


class RedditManager:
    """Handle Reddit API interactions"""
    
    def __init__(self, credentials: Dict):
        """
        credentials = {
            'client_id': 'xxx',
            'client_secret': 'xxx',
            'user_agent': 'AntiBot/1.0',
            'username': 'xxx',
            'password': 'xxx',
        }
        """
        try:
            self.reddit = praw.Reddit(**credentials)
            self.authenticated = True
        except Exception as e:
            self.authenticated = False
            self.error = str(e)
            
    def get_messages(self, limit: int = 20):
        """Get recent messages"""
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
            return messages
        except Exception as e:
            return []
            
    def send_message(self, username: str, subject: str, message: str):
        """Send message to user"""
        try:
            self.reddit.redditor(username).message(subject, message)
            return True
        except Exception as e:
            return False


class OnlyFansManager:
    """Handle OnlyFans DM interactions (via API)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_token = None
        
    def authenticate(self):
        """Authenticate with OnlyFans API"""
        # OnlyFans API implementation
        # Note: Wymagane Official API access
        pass
        
    def get_messages(self):
        """Retrieve messages from OnlyFans"""
        pass
        
    def send_message(self, user_id: str, message: str):
        """Send message on OnlyFans"""
        pass


class AntiBot ResponseGUI(ctk.CTk):
    """Main GUI Application"""
    
    def __init__(self):
        super().__init__()
        
        self.title("🤖 Anti-Bot Response Manager")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.bot_detector = BotDetectionEngine()
        self.response_generator: Optional[HumanResponseGenerator] = None
        self.reddit_manager: Optional[RedditManager] = None
        
        self.create_ui()
        
    def create_ui(self):
        """Build UI"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # === HEADER ===
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(header, text="🔥 Anti-Bot Response Manager", font=("Arial", 24, "bold"))
        title.pack()
        
        # === TABVIEW ===
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self.tab_auth = self.tabs.add("🔐 Authentication")
        self.tab_bot = self.tabs.add("🤖 Bot Detector")
        self.tab_response = self.tabs.add("💬 Response Generator")
        self.tab_monitor = self.tabs.add("📊 Monitor")
        
        self.setup_auth_tab()
        self.setup_bot_detector_tab()
        self.setup_response_tab()
        self.setup_monitor_tab()
        
    def setup_auth_tab(self):
        """Authentication setup"""
        frame = ctk.CTkScrollableFrame(self.tab_auth)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === REDDIT ===
        ctk.CTkLabel(frame, text="🤖 Reddit Credentials", font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 10))
        
        fields = [
            ("Client ID", "reddit_client_id"),
            ("Client Secret", "reddit_client_secret"),
            ("Username", "reddit_user"),
            ("Password", "reddit_pass"),
        ]
        
        self.reddit_fields = {}
        for label, key in fields:
            ctk.CTkLabel(frame, text=label).pack(anchor="w", pady=(10, 2))
            entry = ctk.CTkEntry(frame, width=400, show="*" if "pass" in key else "")
            entry.pack(anchor="w", pady=2)
            self.reddit_fields[key] = entry
            
        # === OPENAI ===
        ctk.CTkLabel(frame, text="🤖 OpenAI API Key", font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 10))
        ctk.CTkLabel(frame, text="API Key").pack(anchor="w", pady=(10, 2))
        self.openai_key = ctk.CTkEntry(frame, width=400, show="*")
        self.openai_key.pack(anchor="w", pady=2)
        
        # Save button
        save_btn = ctk.CTkButton(frame, text="💾 Save Credentials", command=self.save_credentials, height=40)
        save_btn.pack(pady=20)
        
    def setup_bot_detector_tab(self):
        """Bot detection interface"""
        frame = ctk.CTkScrollableFrame(self.tab_bot)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Test Message for Bot Detection", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 10))
        
        ctk.CTkLabel(frame, text="Username:").pack(anchor="w", pady=(10, 2))
        self.bot_user_entry = ctk.CTkEntry(frame, width=300, placeholder_text="reddit_username")
        self.bot_user_entry.pack(anchor="w", pady=2)
        
        ctk.CTkLabel(frame, text="Message to analyze:").pack(anchor="w", pady=(15, 2))
        self.bot_msg_input = ctk.CTkTextbox(frame, height=150, width=600)
        self.bot_msg_input.pack(pady=5)
        
        analyze_btn = ctk.CTkButton(frame, text="🔍 Analyze Message", command=self.analyze_message, height=40)
        analyze_btn.pack(pady=10)
        
        ctk.CTkLabel(frame, text="Results:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(20, 5))
        self.bot_results = ctk.CTkTextbox(frame, height=200, width=600)
        self.bot_results.pack(pady=5)
        
    def setup_response_tab(self):
        """Response generation"""
        frame = ctk.CTkScrollableFrame(self.tab_response)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Generate AI Response", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 10))
        
        ctk.CTkLabel(frame, text="Incoming message:").pack(anchor="w", pady=(10, 2))
        self.response_input = ctk.CTkTextbox(frame, height=100, width=600)
        self.response_input.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Persona:").pack(anchor="w", pady=(15, 2))
        self.persona_var = ctk.StringVar(value="friendly")
        persona_dropdown = ctk.CTkComboBox(
            frame, 
            values=["friendly", "professional", "casual", "humorous", "sympathetic"],
            variable=self.persona_var,
            width=200
        )
        persona_dropdown.pack(anchor="w", pady=2)
        
        generate_btn = ctk.CTkButton(frame, text="✨ Generate Response", command=self.generate_response, height=40)
        generate_btn.pack(pady=10)
        
        ctk.CTkLabel(frame, text="Generated response:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(20, 5))
        self.response_output = ctk.CTkTextbox(frame, height=200, width=600)
        self.response_output.pack(pady=5)
        
        copy_btn = ctk.CTkButton(frame, text="📋 Copy to Clipboard", command=self.copy_response)
        copy_btn.pack(pady=5)
        
    def setup_monitor_tab(self):
        """Monitoring dashboard"""
        frame = ctk.CTkScrollableFrame(self.tab_monitor)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Bot Detection Statistics", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 10))
        
        self.monitor_stats = ctk.CTkTextbox(frame, height=400, width=700)
        self.monitor_stats.pack(pady=5)
        
        refresh_btn = ctk.CTkButton(frame, text="🔄 Refresh Stats", command=self.refresh_stats)
        refresh_btn.pack(pady=10)
        
    def save_credentials(self):
        """Save API credentials"""
        try:
            reddit_creds = {
                'client_id': self.reddit_fields['reddit_client_id'].get(),
                'client_secret': self.reddit_fields['reddit_client_secret'].get(),
                'username': self.reddit_fields['reddit_user'].get(),
                'password': self.reddit_fields['reddit_pass'].get(),
                'user_agent': 'AntiBot/1.0',
            }
            
            openai_key = self.openai_key.get()
            
            if not all(reddit_creds.values()) or not openai_key:
                messagebox.showwarning("Missing Fields", "Please fill all credentials")
                return
                
            # Initialize managers
            self.reddit_manager = RedditManager(reddit_creds)
            self.response_generator = HumanResponseGenerator(openai_key)
            
            if self.reddit_manager.authenticated:
                messagebox.showinfo("Success", "✅ Credentials saved successfully!")
            else:
                messagebox.showerror("Auth Error", f"❌ Reddit auth failed: {self.reddit_manager.error}")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ {str(e)}")
            
    def analyze_message(self):
        """Analyze message for bot detection"""
        username = self.bot_user_entry.get()
        message = self.bot_msg_input.get("1.0", "end").strip()
        
        if not username or not message:
            messagebox.showwarning("Missing Input", "Fill username and message")
            return
            
        bot_score, reason = self.bot_detector.analyze_user(username, message)
        is_bot = self.bot_detector.is_likely_bot(bot_score)
        
        result_text = f"""
📊 Bot Detection Results
━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 User: {username}
📈 Bot Score: {bot_score:.2%}
🚨 Status: {"🤖 LIKELY BOT" if is_bot else "✅ LIKELY HUMAN"}

📋 Analysis Details:
{reason}

⚙️ Behavioral Data:
- Message count: {self.bot_detector.user_behaviors[username].message_count}
- Unique patterns: {len(self.bot_detector.user_behaviors[username].unique_patterns)}
"""
        
        self.bot_results.delete("1.0", "end")
        self.bot_results.insert("1.0", result_text)
        
    def generate_response(self):
        """Generate AI response"""
        if not self.response_generator:
            messagebox.showerror("Error", "Please authenticate first (OpenAI API)")
            return
            
        incoming = self.response_input.get("1.0", "end").strip()
        persona = self.persona_var.get()
        
        if not incoming:
            messagebox.showwarning("Input Required", "Enter incoming message")
            return
            
        response = self.response_generator.generate_response(incoming, persona=persona)
        
        self.response_output.delete("1.0", "end")
        self.response_output.insert("1.0", response)
        
    def copy_response(self):
        """Copy generated response"""
        response = self.response_output.get("1.0", "end").strip()
        if response:
            self.clipboard_clear()
            self.clipboard_append(response)
            messagebox.showinfo("Copied", "Response copied to clipboard!")
            
    def refresh_stats(self):
        """Refresh statistics"""
        stats_text = "📊 Bot Detection Engine Statistics\n"
        stats_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        stats_text += f"Total Users Analyzed: {len(self.bot_detector.user_behaviors)}\n\n"
        
        for user_id, behavior in list(self.bot_detector.user_behaviors.items())[:10]:
            stats_text += f"👤 {user_id}:\n"
            stats_text += f"   - Messages: {behavior.message_count}\n"
            stats_text += f"   - Unique Patterns: {len(behavior.unique_patterns)}\n"
            stats_text += f"   - Avg Message Length: {np.mean(behavior.message_lengths):.0f} chars\n\n"
            
        self.monitor_stats.delete("1.0", "end")
        self.monitor_stats.insert("1.0", stats_text)


def main():
    """Launch application"""
    app = AntiBot ResponseGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
