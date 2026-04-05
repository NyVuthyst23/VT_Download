"""
╔══════════════════════════════════════════════════════════════╗
║          VT_Download — Video Downloader Pro v3.0             ║
║                                                              ║
║  Copyright © 2026 Ny Vuthy. All Rights Reserved.             ║
║                                                              ║
║  This software is protected by copyright law.                ║
║  Unauthorized copying, modification, or distribution         ║
║  of this software is strictly prohibited.                    ║
║                                                              ║
║  Contact: Telegram @ny_vuthy_7 | Facebook /vuthyny7777       ║
╚══════════════════════════════════════════════════════════════╝
"""

__version__ = "3.0.0"
__author__ = "Ny Vuthy"
__copyright__ = "Copyright © 2026 Ny Vuthy. All Rights Reserved."

import customtkinter as ctk
from tkinter import filedialog, StringVar, IntVar
import os
import sys
import math
import threading
import subprocess
import re
import shutil
import webbrowser
import json
import urllib.request
import io
try:
    import browser_engine
except ImportError:
    browser_engine = None
try:
    import winsound
except ImportError:
    winsound = None
from PIL import Image, ImageTk

# ─── Theme Configuration ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ─── Config Persistence ──────────────────────────────────────────────
CONFIG_DIR = os.path.expanduser("~\\.vt_download")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

# ─── Multi-Language System ────────────────────────────────────────────
LANG = {
    "app_title": {"en": "VT_Download", "km": "VT_Download"},
    "app_subtitle": {
        "en": "YouTube (Shorts) • FB (Reels/Page) • TikTok (No Logo) • IG • 1000+ Sites",
        "km": "YouTube (Shorts) • FB (Reels/Page) • TikTok (គ្មានឡូហ្គោ) • IG • 1000+ គេហទំព័រ"
    },
    "select_platform": {"en": "Select Platform", "km": "ជ្រើសរើសវេទិកា"},
    "video_url": {"en": "Video URL", "km": "តំណវីដេអូ"},
    "paste_url_hint": {"en": "Paste video URL here...", "km": "បិទភ្ជាប់តំណវីដេអូនៅទីនេះ..."},
    "paste": {"en": "Paste", "km": "បិទភ្ជាប់"},
    "download_format": {"en": "Download Format", "km": "ទម្រង់ទាញយក"},
    "video_mp4": {"en": "  Video (MP4)", "km": "  វីដេអូ (MP4)"},
    "audio_mp3": {"en": "  Audio (MP3)", "km": "  សំឡេង (MP3)"},
    "quality": {"en": "Quality:", "km": "គុណភាព:"},
    "best_quality": {"en": "Best Quality", "km": "គុណភាពល្អបំផុត"},
    "audio_only": {"en": "Audio Only", "km": "សំឡេងតែប៉ុណ្ណោះ"},
    "save_location": {"en": "Save Location", "km": "ទីតាំងរក្សាទុក"},
    "browse": {"en": "Browse", "km": "រកមើល"},
    "login_required": {
        "en": "Login Required (Use Browser Cookies to access private videos)",
        "km": "ត្រូវការចូល (ប្រើ Cookies ដើម្បីចូលមើលវីដេអូឯកជន)"
    },
    "options": {"en": "Options", "km": "ជម្រើស"},
    "batch_download": {
        "en": "📑 Batch Download (Playlist/Profile - No Logo)",
        "km": "📑 ទាញយកច្រើន (Playlist/Profile - គ្មានឡូហ្គោ)"
    },
    "sound_alert": {"en": "🔔 Sound Alert", "km": "🔔 សំឡេងជូនដំណឹង"},
    "proxy": {"en": "🌐 Proxy:", "km": "🌐 ប្រូកស៊ី:"},
    "download": {"en": "Download", "km": "ទាញយក"},
    "cancel": {"en": "Cancel", "km": "បោះបង់"},
    "update_core": {"en": "Update Core", "km": "អាប់ដេត"},
    "splitter": {"en": "Splitter", "km": "កាត់វីដេអូ"},
    "download_progress": {"en": "Download Progress", "km": "វឌ្ឍនភាពទាញយក"},
    "open_folder": {"en": "📂  Open Folder", "km": "📂  បើកថត"},
    "open_file": {"en": "▶  Open File", "km": "▶  បើកឯកសារ"},
    "support_contact": {"en": "Support Contact:", "km": "ទំនាក់ទំនងជំនួយ:"},
    "about": {"en": "About VT_Download", "km": "អំពី VT_Download"},
    "toggle_theme": {"en": "Toggle Dark/Light Theme", "km": "ប្ដូររូបរាងងងឹត/ភ្លឺ"},
    "fetching_info": {"en": "🔍 Fetching video info...", "km": "🔍 កំពុងទាញយកព័ត៌មានវីដេអូ..."},
    "starting_download": {"en": "Starting download...", "km": "កំពុងចាប់ផ្ដើមទាញយក..."},
    "download_complete": {"en": "✅ Download Complete!", "km": "✅ ទាញយកបានសម្រេច!"},
    "cancelled": {"en": "❌ Cancelled", "km": "❌ បានបោះបង់"},
    "processing": {"en": "⚙ Processing...", "km": "⚙ កំពុងដំណើរការ..."},
    "paste_url_first": {"en": "Please paste a video URL first.", "km": "សូមបិទភ្ជាប់តំណវីដេអូជាមុនសិន។"},
    "save_not_exist": {"en": "Save location does not exist.", "km": "ទីតាំងរក្សាទុកមិនមាន។"},
    "download_success": {"en": "Video downloaded successfully!", "km": "វីដេអូបានទាញយកដោយជោគជ័យ!"},
    "checking_updates": {"en": "Checking for updates... (yt-dlp)", "km": "កំពុងពិនិត្យការអាប់ដេត... (yt-dlp)"},
    "update_complete": {"en": "✅ Update Complete!", "km": "✅ អាប់ដេតបានសម្រេច!"},
    "update_failed": {"en": "❌ Update Failed", "km": "❌ អាប់ដេតបរាជ័យ"},
    "shortcuts": {
        "en": "Enter: Download  │  Esc: Cancel  │  Ctrl+V: Paste",
        "km": "Enter: ទាញយក  │  Esc: បោះបង់  │  Ctrl+V: បិទភ្ជាប់"
    },
    "file_size": {"en": "📦 Size:", "km": "📦 ទំហំ:"},
    "video_cutter": {"en": "✂️ Fast Video Splitter", "km": "✂️ កាត់វីដេអូលឿន"},
    "original_video": {"en": "Original Video:", "km": "វីដេអូដើម:"},
    "save_to": {"en": "Save To:", "km": "រក្សាទុកទៅ:"},
    "start_time": {"en": "Start Time:", "km": "ពេលចាប់ផ្ដើម:"},
    "end_time": {"en": "End Time:", "km": "ពេលបញ្ចប់:"},
    "cut_now": {"en": "✂️ Cut Now", "km": "✂️ កាត់ឥឡូវ"},
    "close": {"en": "Close", "km": "បិទ"},
    "waiting": {"en": "Waiting...", "km": "កំពុងរង់ចាំ..."},
    "cutting_video": {"en": "Cutting video (Fast Mode)...", "km": "កំពុងកាត់វីដេអូ (របៀបលឿន)..."},
    "select_valid_video": {"en": "❌ Select a valid input video.", "km": "❌ សូមជ្រើសរើសវីដេអូត្រឹមត្រូវ។"},
    "ffmpeg_not_found": {"en": "❌ FFmpeg not found on system.", "km": "❌ រកមិនឃើញ FFmpeg នៅក្នុងប្រព័ន្ធ។"},
    "time_format_hint": {
        "en": "Format: HH:MM:SS. Example: 00:01:30 to cut from 1 min 30 sec.",
        "km": "ទម្រង់: HH:MM:SS។ ឧទាហរណ៍: 00:01:30 ដើម្បីកាត់ពី 1 នាទី 30 វិនាទី។"
    },
    "about_desc": {
        "en": "Professional Video Downloader\nYouTube • Facebook • TikTok • Kuaishou",
        "km": "កម្មវិធីទាញយកវីដេអូប្រកបដោយវិជ្ជាជីវៈ\nYouTube • Facebook • TikTok • Kuaishou"
    },
    "licensed_software": {
        "en": "Licensed Commercial Software\nUnauthorized copying or distribution is prohibited.",
        "km": "កម្មវិធីពាណិជ្ជកម្មដែលមានអាជ្ញាប័ណ្ណ\nការចម្លង ឬចែកចាយដោយគ្មានការអនុញ្ញាតត្រូវបានហាមឃាត់។"
    },
    "trademark_notice": {
        "en": "VT_Download™ is a trademark of Ny Vuthy",
        "km": "VT_Download™ ជាពាណិជ្ជសញ្ញារបស់ Ny Vuthy"
    },
    "purchase_support": {"en": "📩 Purchase & Support", "km": "📩 ទិញ & ជំនួយ"},
    "wait_download_finish": {
        "en": "Please wait until the current download finishes.",
        "km": "សូមរង់ចាំរហូតដល់ការទាញយកបច្ចុប្បន្នបញ្ចប់។"
    },
    "video_info": {"en": "📐 Video Info", "km": "📐 ព័ត៌មានវីដេអូ"},
    "duration_label": {"en": "⏱ Duration:", "km": "⏱ រយៈពេល:"},
    "resolution_label": {"en": "📺 Resolution:", "km": "📺 គុណភាពបង្ហាញ:"},
    "filesize_label": {"en": "📦 File Size:", "km": "📦 ទំហំឯកសារ:"},
    "cut_mode": {"en": "Cut Mode:", "km": "របៀបកាត់:"},
    "fast_copy": {"en": "⚡ Fast (Stream Copy)", "km": "⚡ លឿន (Stream Copy)"},
    "precise_reencode": {"en": "🎯 Precise (Re-encode)", "km": "🎯 ប្រាកដ (Re-encode)"},
    "output_filename": {"en": "Output Name:", "km": "ឈ្មោះទិន្នផល:"},
    "analyzing_video": {"en": "🔍 Analyzing video...", "km": "🔍 កំពុងវិភាគវីដេអូ..."},
    "open_result": {"en": "📂 Open Result", "km": "📂 បើកលទ្ធផល"},
    "cut_another": {"en": "🔄 Cut Another", "km": "🔄 កាត់ផ្សេងទៀត"},
    "no_video_info": {"en": "Select a video file to see info", "km": "ជ្រើសរើសវីដេអូដើម្បីមើលព័ត៌មាន"},
    "downloading_core": {"en": "Downloading yt-dlp core... (Please wait)", "km": "កំពុងទាញយក yt-dlp core... (សូមរង់ចាំ)"},
    "core_not_found": {"en": "yt-dlp core not found. Downloading the latest version...", "km": "រកមិនឃើញ yt-dlp core។ កំពុងទាញយកកំណែចុងក្រោយ..."},
    "core_installed": {"en": "✅ Core installed successfully!", "km": "✅ បានដំឡើង Core ដោយជោគជ័យ!"},
    "core_download_failed": {"en": "❌ Core Download Failed", "km": "❌ ការទាញយក Core បានបរាជ័យ"},
    "core_installed_toast": {"en": "yt-dlp core installed successfully!", "km": "បានដំឡើង yt-dlp core ដោយជោគជ័យ!"},
    "folder_not_found": {"en": "Folder not found.", "km": "រកមិនឃើញថតឯកសារ។"},
    "failed_attempts": {"en": "⚠ Failed after {n} attempts", "km": "⚠ បរាជ័យបន្ទាប់ពីព្យាយាម {n} ដង"},
    "ytdlp_updated": {"en": "yt-dlp updated successfully!", "km": "បានធ្វើបច្ចុប្បន្នភាព yt-dlp ដោយជោគជ័យ!"},
    "tooltip_download": {"en": "Start download (Enter)", "km": "ចាប់ផ្ដើមទាញយក (Enter)"},
    "tooltip_cancel": {"en": "Cancel download (Esc)", "km": "បោះបង់ការទាញយក (Esc)"},
    "tooltip_update": {"en": "Update yt-dlp to latest version", "km": "ធ្វើបច្ចុប្បន្នភាព yt-dlp ទៅកំណែចុងក្រោយ"},
    "tooltip_splitter": {"en": "Open Fast Video Splitter tool", "km": "បើកឧបករណ៍កាត់វីដេអូលឿន"},
    "mode_single_cut": {"en": "✂️ Single Cut", "km": "✂️ កាត់តែមួយ"},
    "mode_multi_split": {"en": "📊 Multi-Split", "km": "📊 កាត់ច្រើនភាគ"},
    "min_per_part": {"en": "Minutes per Part:", "km": "នាទីក្នុងមួយភាគ:"},
    "total_parts_calc": {"en": "= {n} parts", "km": "= {n} ភាគ"},
    "splitting_video": {"en": "Splitting video into {n} parts...", "km": "កំពុងកាត់វីដេអូជា {n} ភាគ..."},
    "split_progress": {"en": "Cutting part {i}/{n}...", "km": "កំពុងកាត់ភាគ {i}/{n}..."},
    "split_complete": {"en": "✅ Split into {n} parts successfully!", "km": "✅ បានកាត់ជា {n} ភាគដោយជោគជ័យ!"},
    "need_video_duration": {"en": "❌ Cannot detect video duration. Select a valid video.", "km": "❌ មិនអាចរកឃើញរយៈពេលវីដេអូ។ សូមជ្រើសវីដេអូត្រឹមត្រូវ។"},
    "open_output_folder": {"en": "📂 Open Folder", "km": "📂 បើកថតឯកសារ"},
    "app_update_available": {"en": "🆕 New version {v} available!", "km": "🆕 កំណែថ្មី {v} មានហើយ!"},
    "app_update_btn": {"en": "⬆️ Update App", "km": "⬆️ អាប់ដេតកម្មវិធី"},
    "app_up_to_date": {"en": "✅ App is up to date (v{v})", "km": "✅ កម្មវិធីទាន់សម័យហើយ (v{v})"},
    "app_downloading_update": {"en": "⬇️ Downloading update...", "km": "⬇️ កំពុងទាញយកការអាប់ដេត..."},
    "app_update_restart": {"en": "✅ Update downloaded! Restart the app to apply.", "km": "✅ បានទាញយកការអាប់ដេត! សូមបិទបើកកម្មវិធីឡើងវិញ។"},
    "app_update_failed": {"en": "❌ Update failed", "km": "❌ ការអាប់ដេតបានបរាជ័យ"},
    "check_update": {"en": "Check for Updates", "km": "ពិនិត្យការអាប់ដេត"},
}

def t(key, lang="en"):
    """Get translated text for a key."""
    entry = LANG.get(key, {})
    return entry.get(lang, entry.get("en", key))

# ─── Color Palette (Enhanced v3.0) ────────────────────────────────────
COLORS = {
    "bg_dark":        "#0a0e17",  # Deeper dark background
    "bg_card":        "#131a27",  # Rich dark card with blue tint
    "bg_card_inner":  "#0d1220",
    "bg_card_glass":  "#161d2e",  # Glassmorphism card
    "bg_input":       "#080c14",
    "border":         "#1e2d3d",  # Subtle blue-tinted border
    "border_glow":    "#58a6ff",  # Soft blue glow
    "border_glass":   "#2a3a4f",  # Glassmorphism border
    "neon_blue":      "#58a6ff",
    "neon_cyan":      "#39d5e0",
    "neon_pink":      "#ff7b72",
    "neon_orange":    "#f0a030",
    "neon_green":     "#56d364",
    "neon_purple":    "#bc8cff",
    "text_primary":   "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted":     "#475569",
    "accent_red":     "#f85149",
    "accent_blue":    "#58a6ff",
    "accent_dark":    "#1e293b",
    "accent_orange":  "#f0a030",
    "gradient_start": "#3b82f6",  # Vibrant gradient start
    "gradient_end":   "#8b5cf6",  # Purple gradient end
    "gradient_pink1": "#388bfd",
    "gradient_pink2": "#1f6feb",
    "gray_btn":       "#1e293b",
    "gray_btn_hover": "#334155",
    "progress_bg":    "#1e293b",
    "progress_fill":  "#3b82f6",
    "scrollbar":      "#334155",
    "glow_shadow":    "#3b82f620",  # For glow effects
}

# ─── Icon Symbols (Unicode) ──────────────────────────────────────────
ICONS = {
    "youtube":   "▶",
    "facebook":  "f",
    "tiktok":    "♪",
    "kuaishou":  "⚡",
    "paste":     "📋",
    "browse":    "📁",
    "download":  "⬇",
    "cancel":    "✕",
    "video":     "🎬",
    "audio":     "🎵",
    "import":    "📥",
    "detect":    "🔍",
    "export":    "📤",
    "save":      "💾",
    "reset":     "🔄",
    "generate":  "⚙",
    "platform":  "🌐",
    "url":       "🔗",
    "format":    "📀",
    "folder":    "📂",
    "progress":  "📊",
    "list":      "📋",
    "tools":     "🛠",
}


class NeonFrame(ctk.CTkFrame):
    """A frame with a neon-glowing border effect."""
    def __init__(self, master, glow_color=COLORS["border_glow"], **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_card"])
        kwargs.setdefault("corner_radius", 18)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", glow_color)
        super().__init__(master, **kwargs)


class GlassFrame(ctk.CTkFrame):
    """Glassmorphism-style frame with layered appearance."""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_card_glass"])
        kwargs.setdefault("corner_radius", 16)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border_glass"])
        super().__init__(master, **kwargs)


class GlowButton(ctk.CTkButton):
    """A stylish button with hover glow."""
    def __init__(self, master, glow_color=None, **kwargs):
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("height", 40)
        kwargs.setdefault("font", ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        super().__init__(master, **kwargs)


class SectionTitle(ctk.CTkFrame):
    """Section header with icon and label."""
    def __init__(self, master, icon, text, color=COLORS["neon_cyan"], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        icon_label = ctk.CTkLabel(
            self, text=icon, font=ctk.CTkFont(size=16),
            text_color=color, width=24
        )
        icon_label.pack(side="left", padx=(0, 8))
        title_label = ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.pack(side="left")


class ToastNotification(ctk.CTkFrame):
    """Modern toast notification overlay."""
    STYLES = {
        "success": {"bg": "#0d2818", "border": "#3fb950", "icon": "✅", "text": "#3fb950"},
        "error":   {"bg": "#2d0b0b", "border": "#f85149", "icon": "❌", "text": "#f85149"},
        "info":    {"bg": "#0c1929", "border": "#58a6ff", "icon": "ℹ️", "text": "#58a6ff"},
        "warning": {"bg": "#2a1e00", "border": "#d29922", "icon": "⚠️", "text": "#d29922"},
    }

    def __init__(self, master, message, toast_type="success", duration=4000):
        style = self.STYLES.get(toast_type, self.STYLES["info"])
        super().__init__(master, fg_color=style["bg"], corner_radius=14,
                         border_width=2, border_color=style["border"])

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(padx=16, pady=10)

        ctk.CTkLabel(row, text=style["icon"], font=ctk.CTkFont(size=18),
                     text_color=style["text"]).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(row, text=message, font=ctk.CTkFont(family="Segoe UI", size=13),
                     text_color=COLORS["text_primary"], wraplength=400).pack(side="left")
        ctk.CTkButton(row, text="✕", width=28, height=28, fg_color="transparent",
                      hover_color=style["border"], text_color=COLORS["text_muted"],
                      command=self._dismiss).pack(side="left", padx=(12, 0))

        self.place(relx=0.5, rely=0.0, anchor="n", y=-80)
        self._animate_in()
        self._dismiss_id = self.after(duration, self._dismiss)

    def _animate_in(self, y=-80):
        if y < 10:
            self.place_configure(y=y)
            self.after(12, self._animate_in, y + 6)
        else:
            self.place_configure(y=10)

    def _dismiss(self):
        if hasattr(self, '_dismiss_id'):
            self.after_cancel(self._dismiss_id)
        try:
            self.destroy()
        except Exception:
            pass


class ToolTip:
    """Hover tooltip for widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self.tip_window:
            return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
            import tkinter as tk
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            tw.attributes("-topmost", True)
            tw.configure(bg="#1e1e2e")
            lbl = tk.Label(tw, text=self.text,
                           font=("Segoe UI", 10),
                           bg="#1e1e2e", fg="#e4e4e7",
                           padx=10, pady=5)
            lbl.pack()
        except Exception:
            pass

    def _hide(self, event=None):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None

class PlatformButton(ctk.CTkFrame):
    """Platform selection button with icon, label, and active state."""
    def __init__(self, master, icon_text, label, accent_color, callback=None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_card_inner"],
                         corner_radius=14, border_width=2,
                         border_color=COLORS["border"], cursor="hand2", **kwargs)
        self.accent_color = accent_color
        self.is_active = False
        self.callback = callback
        self.configure(width=130, height=70)
        self.pack_propagate(False)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(expand=True)

        self.icon_lbl = ctk.CTkLabel(
            inner, text=icon_text,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=accent_color
        )
        self.icon_lbl.pack(pady=(6, 2))

        self.name_lbl = ctk.CTkLabel(
            inner, text=label,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        self.name_lbl.pack(pady=(0, 4))

        # Bind clicks on all children
        for widget in [self, inner, self.icon_lbl, self.name_lbl]:
            widget.bind("<Button-1>", self._on_click)

    def _on_click(self, event=None):
        if self.callback:
            self.callback(self)

    def set_active(self, active: bool):
        self.is_active = active
        if active:
            self.configure(border_color=self.accent_color,
                           fg_color=self._darken(self.accent_color, 0.15))
            self.name_lbl.configure(text_color=self.accent_color)
        else:
            self.configure(border_color=COLORS["border"],
                           fg_color=COLORS["bg_card_inner"])
            self.name_lbl.configure(text_color=COLORS["text_secondary"])

    @staticmethod
    def _darken(hex_color, factor):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

class VideoCutterWindow(ctk.CTkToplevel):
    def __init__(self, master=None, lang="en"):
        super().__init__(master)
        self._lang = lang
        self.title(t("video_cutter", lang))
        self.geometry("660x680")
        self.minsize(620, 640)
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(master)
        self.grab_set()

        self.input_file = StringVar()
        self.output_folder = StringVar(value=os.path.expanduser("~\\Downloads"))
        self.start_time = StringVar(value="00:00:00")
        self.end_time = StringVar(value="00:05:00")
        self.output_name = StringVar(value="")
        self.cut_mode = StringVar(value="fast")
        self.min_per_part = StringVar(value="3")
        self._active_tab = "single"
        self.is_cutting = False
        self._last_output = ""
        self._last_output_dir = ""
        self._video_duration = 0

        self._build_ui()

    def _build_ui(self):
        L = self._lang
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(12, 6))
        ctk.CTkLabel(header, text=t("video_cutter", L),
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLORS["neon_blue"]).pack(side="left")
        ctk.CTkButton(header, text="✕", width=32, height=32,
                      fg_color="transparent", hover_color=COLORS["accent_red"],
                      font=ctk.CTkFont(size=16), corner_radius=16,
                      command=self.destroy).pack(side="right")

        # Mode Tabs
        tab_row = ctk.CTkFrame(self, fg_color="transparent")
        tab_row.pack(fill="x", padx=20, pady=(0, 4))
        self._tab_single = ctk.CTkButton(
            tab_row, text=t("mode_single_cut", L),
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["neon_blue"], hover_color="#2563eb",
            corner_radius=10, height=34, width=150,
            command=lambda: self._switch_tab("single"))
        self._tab_single.pack(side="left", padx=(0, 6))
        self._tab_multi = ctk.CTkButton(
            tab_row, text=t("mode_multi_split", L),
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["gray_btn"], hover_color=COLORS["gray_btn_hover"],
            corner_radius=10, height=34, width=150,
            command=lambda: self._switch_tab("multi"))
        self._tab_multi.pack(side="left")

        # Main Card
        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card_glass"],
                            corner_radius=16, border_width=1,
                            border_color=COLORS["border_glass"])
        card.pack(fill="both", expand=True, padx=20, pady=6)
        self._card = card

        # Input File
        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(row1, text=t("original_video", L), width=100, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkEntry(row1, textvariable=self.input_file, state="readonly",
                     fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                     corner_radius=10, height=36).pack(side="left", fill="x", expand=True, padx=8)
        ctk.CTkButton(row1, text=t("browse", L), width=80, height=36,
                      fg_color=COLORS["neon_blue"], hover_color="#2563eb",
                      corner_radius=10, command=self._browse_input).pack(side="right")

        # Video Info
        info_f = ctk.CTkFrame(card, fg_color=COLORS["bg_card_inner"],
                              corner_radius=12, border_width=1, border_color=COLORS["border"])
        info_f.pack(fill="x", padx=16, pady=6)
        info_inner = ctk.CTkFrame(info_f, fg_color="transparent")
        info_inner.pack(fill="x", padx=12, pady=8)
        self.info_duration = ctk.CTkLabel(info_inner, text=t("no_video_info", L),
                                           font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.info_duration.pack(side="left", padx=(0, 16))
        self.info_resolution = ctk.CTkLabel(info_inner, text="", font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.info_resolution.pack(side="left", padx=(0, 16))
        self.info_filesize = ctk.CTkLabel(info_inner, text="", font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"])
        self.info_filesize.pack(side="left")

        # Output Folder
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(row2, text=t("save_to", L), width=100, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkEntry(row2, textvariable=self.output_folder, state="readonly",
                     fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                     corner_radius=10, height=36).pack(side="left", fill="x", expand=True, padx=8)
        ctk.CTkButton(row2, text=t("browse", L), width=80, height=36,
                      fg_color=COLORS["neon_orange"], hover_color="#ea580c",
                      corner_radius=10, command=self._browse_output).pack(side="right")

        # ══ Tab Content Container ══
        self._tab_container = ctk.CTkFrame(card, fg_color="transparent")
        self._tab_container.pack(fill="x")

        # ══ SINGLE CUT PANEL ══
        self._single_panel = ctk.CTkFrame(self._tab_container, fg_color="transparent")
        rn = ctk.CTkFrame(self._single_panel, fg_color="transparent")
        rn.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(rn, text=t("output_filename", L), width=100, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkEntry(rn, textvariable=self.output_name, placeholder_text="auto-generated",
                     fg_color=COLORS["bg_input"], border_color=COLORS["border"],
                     corner_radius=10, height=36, text_color=COLORS["text_primary"],
                     placeholder_text_color=COLORS["text_muted"]).pack(side="left", fill="x", expand=True, padx=8)
        tf = ctk.CTkFrame(self._single_panel, fg_color=COLORS["bg_card_inner"],
                          corner_radius=12, border_width=1, border_color=COLORS["border"])
        tf.pack(fill="x", padx=16, pady=6)
        r3 = ctk.CTkFrame(tf, fg_color="transparent")
        r3.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(r3, text=t("start_time", L), width=80, anchor="w",
                     font=ctk.CTkFont(size=13), text_color=COLORS["neon_green"]).pack(side="left")
        ctk.CTkEntry(r3, textvariable=self.start_time, width=110, fg_color=COLORS["bg_input"],
                     border_color=COLORS["neon_green"], border_width=2, corner_radius=10, height=36,
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(r3, text=t("end_time", L), width=80, anchor="e",
                     font=ctk.CTkFont(size=13), text_color=COLORS["neon_pink"]).pack(side="left", padx=(24, 0))
        ctk.CTkEntry(r3, textvariable=self.end_time, width=110, fg_color=COLORS["bg_input"],
                     border_color=COLORS["neon_pink"], border_width=2, corner_radius=10, height=36,
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(tf, text=t("time_format_hint", L), text_color=COLORS["text_muted"],
                     font=ctk.CTkFont(size=11)).pack(pady=(0, 8))

        # ══ MULTI-SPLIT PANEL ══
        self._multi_panel = ctk.CTkFrame(self._tab_container, fg_color="transparent")
        sf = ctk.CTkFrame(self._multi_panel, fg_color=COLORS["bg_card_inner"],
                          corner_radius=12, border_width=1, border_color=COLORS["border"])
        sf.pack(fill="x", padx=16, pady=6)
        sr = ctk.CTkFrame(sf, fg_color="transparent")
        sr.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(sr, text=t("min_per_part", L), width=140, anchor="w",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["neon_cyan"]).pack(side="left")
        ctk.CTkEntry(sr, textvariable=self.min_per_part, width=80, fg_color=COLORS["bg_input"],
                     border_color=COLORS["neon_cyan"], border_width=2, corner_radius=10, height=40,
                     font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_primary"],
                     justify="center").pack(side="left", padx=(0, 20))
        self._per_part_label = ctk.CTkLabel(sr, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["neon_green"])
        self._per_part_label.pack(side="left")
        self.min_per_part.trace_add("write", self._update_per_part_display)
        hint_text = "ឧទាហរណ៍: បញ្ចូល 3 → វីដេអូ 30min ÷ 3 = 10 ភាគ" if L == "km" else "Example: Enter 3 → 30min video ÷ 3min = 10 parts"
        ctk.CTkLabel(sf, text=hint_text, text_color=COLORS["text_muted"], font=ctk.CTkFont(size=11)).pack(pady=(0, 10))

        # Cut Mode (shared)
        mr = ctk.CTkFrame(card, fg_color="transparent")
        mr.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(mr, text=t("cut_mode", L), width=100, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkRadioButton(mr, text=t("fast_copy", L), variable=self.cut_mode, value="fast",
                           font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"],
                           fg_color=COLORS["neon_green"], border_color=COLORS["neon_green"]).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(mr, text=t("precise_reencode", L), variable=self.cut_mode, value="precise",
                           font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"],
                           fg_color=COLORS["neon_cyan"], border_color=COLORS["neon_cyan"]).pack(side="left")

        # Progress / Status
        self.status_lbl = ctk.CTkLabel(card, text=t("waiting", L), text_color=COLORS["text_secondary"],
                                        font=ctk.CTkFont(size=13))
        self.status_lbl.pack(pady=(8, 0))
        self.progress_bar = ctk.CTkProgressBar(card, fg_color=COLORS["progress_bg"],
                                                progress_color=COLORS["progress_fill"], corner_radius=8, height=12)
        self.progress_bar.pack(fill="x", padx=24, pady=(6, 10))
        self.progress_bar.set(0)

        # Action Buttons
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="x", padx=20, pady=(4, 14))
        self.cut_btn = ctk.CTkButton(bot, text=t("cut_now", L), font=ctk.CTkFont(size=14, weight="bold"),
                                      fg_color=COLORS["gradient_pink1"], hover_color=COLORS["gradient_pink2"],
                                      corner_radius=12, width=140, height=42, command=self._start_action)
        self.cut_btn.pack(side="right", padx=(10, 0))
        ctk.CTkButton(bot, text=t("close", L), fg_color=COLORS["gray_btn"],
                      hover_color=COLORS["gray_btn_hover"], corner_radius=12,
                      width=90, height=42, command=self.destroy).pack(side="right")

        self._result_row = ctk.CTkFrame(bot, fg_color="transparent")
        ctk.CTkButton(self._result_row, text=t("open_output_folder", L), fg_color=COLORS["neon_green"],
                      hover_color="#16a34a", corner_radius=10, width=140, height=38,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._open_result_folder).pack(side="left", padx=(0, 8))
        ctk.CTkButton(self._result_row, text=t("cut_another", L), fg_color=COLORS["neon_blue"],
                      hover_color="#2563eb", corner_radius=10, width=130, height=38,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._reset_for_another).pack(side="left")

        self._switch_tab("single")

    def _switch_tab(self, tab):
        self._active_tab = tab
        self._single_panel.pack_forget()
        self._multi_panel.pack_forget()
        if tab == "single":
            self._single_panel.pack(fill="x")
            self._tab_single.configure(fg_color=COLORS["neon_blue"])
            self._tab_multi.configure(fg_color=COLORS["gray_btn"])
        else:
            self._multi_panel.pack(fill="x")
            self._tab_multi.configure(fg_color=COLORS["neon_cyan"])
            self._tab_single.configure(fg_color=COLORS["gray_btn"])
            self._update_per_part_display()

    def _update_per_part_display(self, *args):
        if self._video_duration <= 0:
            self._per_part_label.configure(text=""); return
        try:
            mins = float(self.min_per_part.get())
            if mins <= 0: self._per_part_label.configure(text=""); return
        except ValueError:
            self._per_part_label.configure(text=""); return
        import math
        n = math.ceil(self._video_duration / (mins * 60))
        self._per_part_label.configure(text=t("total_parts_calc", self._lang).replace("{n}", str(n)))

    def _browse_input(self):
        f = filedialog.askopenfilename(filetypes=[
            ("Video Files", "*.mp4 *.mkv *.webm *.avi *.mov *.ts *.flv *.m4v *.3gp *.mpg *.mpeg *.wmv *.vob *.m2ts *.mts"),
            ("All Files", "*.*")])
        if f:
            self.input_file.set(f)
            name, ext = os.path.splitext(os.path.basename(f))
            self.output_name.set(f"{name}_cut{ext}")
            self._analyze_video(f)

    def _browse_output(self):
        d = filedialog.askdirectory()
        if d: self.output_folder.set(d)

    def _analyze_video(self, filepath):
        self.status_lbl.configure(text=t("analyzing_video", self._lang))
        def _probe():
            ffmpeg_cmd = self._find_ffmpeg()
            if not ffmpeg_cmd:
                self.after(0, lambda: self.status_lbl.configure(text=t("waiting", self._lang))); return
            probe_cmd = ffmpeg_cmd.replace("ffmpeg", "ffprobe") if "ffmpeg" in ffmpeg_cmd else ffmpeg_cmd
            if not os.path.exists(probe_cmd) and probe_cmd != ffmpeg_cmd: probe_cmd = ffmpeg_cmd
            try:
                cmd = [probe_cmd, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filepath]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                if result.returncode == 0 and result.stdout.strip():
                    info = json.loads(result.stdout)
                    dur = float(info.get("format", {}).get("duration", 0))
                    sz = int(info.get("format", {}).get("size", 0))
                    w, h = 0, 0
                    for s in info.get("streams", []):
                        if s.get("codec_type") == "video": w = s.get("width", 0); h = s.get("height", 0); break
                    self._video_duration = dur
                    self.after(0, lambda: self._show_video_info(dur, w, h, sz))
                else:
                    r2 = subprocess.run([ffmpeg_cmd, "-i", filepath], capture_output=True, text=True, timeout=10,
                                         creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    stderr = r2.stderr or ""
                    dm = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', stderr)
                    rm = re.search(r'(\d{2,5})x(\d{2,5})', stderr)
                    dur = int(dm.group(1))*3600 + int(dm.group(2))*60 + float(dm.group(3)) if dm else 0
                    w, h = (int(rm.group(1)), int(rm.group(2))) if rm else (0, 0)
                    sz = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    self._video_duration = dur
                    self.after(0, lambda: self._show_video_info(dur, w, h, sz))
            except Exception:
                sz = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                self.after(0, lambda: self._show_video_info(0, 0, 0, sz))
            self.after(0, lambda: self.status_lbl.configure(text=t("waiting", self._lang)))
        threading.Thread(target=_probe, daemon=True).start()

    def _show_video_info(self, duration, width, height, size_bytes):
        L = self._lang
        if duration > 0:
            h, rem = divmod(int(duration), 3600); m, s = divmod(rem, 60)
            self.info_duration.configure(text=f"{t('duration_label', L)} {h:02d}:{m:02d}:{s:02d}", text_color=COLORS["neon_green"])
            self.end_time.set(f"{h:02d}:{m:02d}:{s:02d}")
            self._update_per_part_display()
        if width > 0 and height > 0:
            self.info_resolution.configure(text=f"{t('resolution_label', L)} {width}×{height}", text_color=COLORS["neon_cyan"])
        if size_bytes > 0:
            sz_str = f"{size_bytes/1_073_741_824:.1f} GB" if size_bytes > 1_073_741_824 else f"{size_bytes/1_048_576:.1f} MB"
            self.info_filesize.configure(text=f"{t('filesize_label', L)} {sz_str}", text_color=COLORS["neon_orange"])

    def _find_ffmpeg(self):
        import shutil
        if shutil.which("ffmpeg"): return "ffmpeg"
        base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        local = os.path.join(base, "ffmpeg.exe")
        return local if os.path.exists(local) else None

    def _start_action(self):
        if self._active_tab == "single": self._start_cut()
        else: self._start_multi_split()

    def _start_cut(self):
        if self.is_cutting: return
        inp = self.input_file.get()
        if not inp or not os.path.isfile(inp):
            self.status_lbl.configure(text=t("select_valid_video", self._lang)); return
        ffmpeg_cmd = self._find_ffmpeg()
        if not ffmpeg_cmd:
            self.status_lbl.configure(text=t("ffmpeg_not_found", self._lang)); return
        out_dir = self.output_folder.get()
        cn = self.output_name.get().strip()
        if cn: out_file = os.path.join(out_dir, cn)
        else:
            import time as _t; bn = os.path.basename(inp); nm, ext = os.path.splitext(bn)
            out_file = os.path.join(out_dir, f"{nm}_cut_{int(_t.time())}{ext}")
        self.is_cutting = True; self.cut_btn.configure(state="disabled")
        self.progress_bar.configure(mode="indeterminate"); self.progress_bar.start()
        self._result_row.pack_forget()
        self.status_lbl.configure(text=t("cutting_video", self._lang))
        mode = self.cut_mode.get()
        def _run():
            if mode == "fast":
                cmd = [ffmpeg_cmd, "-y", "-ss", self.start_time.get().strip(), "-i", inp,
                       "-to", self.end_time.get().strip(), "-c", "copy", "-avoid_negative_ts", "make_zero", out_file]
            else:
                cmd = [ffmpeg_cmd, "-y", "-i", inp, "-ss", self.start_time.get().strip(),
                       "-to", self.end_time.get().strip(), "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                       "-c:a", "aac", "-b:a", "192k", out_file]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                if proc.returncode == 0: self.after(0, lambda: self._on_success(out_file))
                else: self.after(0, lambda: self._on_error(f"FFmpeg: {proc.stderr[:120]}"))
            except Exception as e: self.after(0, lambda err=str(e): self._on_error(err))
        threading.Thread(target=_run, daemon=True).start()

    def _start_multi_split(self):
        if self.is_cutting: return
        inp = self.input_file.get()
        if not inp or not os.path.isfile(inp):
            self.status_lbl.configure(text=t("select_valid_video", self._lang)); return
        if self._video_duration <= 0:
            self.status_lbl.configure(text=t("need_video_duration", self._lang)); return
        ffmpeg_cmd = self._find_ffmpeg()
        if not ffmpeg_cmd:
            self.status_lbl.configure(text=t("ffmpeg_not_found", self._lang)); return
        import math
        try:
            mins = float(self.min_per_part.get())
            if mins <= 0: mins = 3
        except ValueError: mins = 3
        per_part = mins * 60  # seconds per part
        n = math.ceil(self._video_duration / per_part)
        out_dir = self.output_folder.get()
        nm, ext = os.path.splitext(os.path.basename(inp))
        self.is_cutting = True; self.cut_btn.configure(state="disabled")
        self._result_row.pack_forget()
        self.progress_bar.configure(mode="determinate"); self.progress_bar.set(0)
        self._last_output_dir = out_dir
        mode = self.cut_mode.get()
        def _split():
            for i in range(n):
                ss = per_part * i; es = min(per_part * (i + 1), self._video_duration)
                sh, srem = divmod(int(ss), 3600); sm, ssc = divmod(srem, 60)
                eh, erem = divmod(int(es), 3600); em, esc = divmod(erem, 60)
                s_str = f"{sh:02d}:{sm:02d}:{ssc:02d}"; e_str = f"{eh:02d}:{em:02d}:{esc:02d}"
                pn = f"{i+1:02d}" if n >= 10 else str(i+1)
                of = os.path.join(out_dir, f"{nm}_Part{pn}{ext}")
                self.after(0, lambda idx=i: self.status_lbl.configure(
                    text=t("split_progress", self._lang).replace("{i}", str(idx+1)).replace("{n}", str(n))))
                self.after(0, lambda idx=i: self.progress_bar.set(idx / n))
                if mode == "fast":
                    cmd = [ffmpeg_cmd, "-y", "-ss", s_str, "-i", inp, "-to", e_str,
                           "-c", "copy", "-avoid_negative_ts", "make_zero", of]
                else:
                    cmd = [ffmpeg_cmd, "-y", "-i", inp, "-ss", s_str, "-to", e_str,
                           "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                           "-c:a", "aac", "-b:a", "192k", of]
                try:
                    proc = subprocess.run(cmd, capture_output=True, text=True,
                                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    if proc.returncode != 0:
                        self.after(0, lambda: self._on_error(f"Part {i+1}: {proc.stderr[:100]}")); return
                except Exception as e:
                    self.after(0, lambda err=str(e): self._on_error(err)); return
            self.after(0, lambda: self._on_split_complete(n))
        threading.Thread(target=_split, daemon=True).start()

    def _on_split_complete(self, n):
        self.is_cutting = False; self.cut_btn.configure(state="normal")
        self.progress_bar.set(1); self.progress_bar.configure(progress_color=COLORS["neon_green"])
        self.status_lbl.configure(text=t("split_complete", self._lang).replace("{n}", str(n)),
                                   text_color=COLORS["neon_green"])
        self._result_row.pack(side="left", padx=(0, 10))
        self._open_result_folder()

    def _on_success(self, file_path):
        self.is_cutting = False; self._last_output = file_path
        self._last_output_dir = os.path.dirname(file_path)
        self.cut_btn.configure(state="normal"); self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate"); self.progress_bar.set(1)
        self.progress_bar.configure(progress_color=COLORS["neon_green"])
        try:
            sz = os.path.getsize(file_path)
            sz_str = f"{sz/1_048_576:.1f} MB" if sz > 1_048_576 else f"{sz/1024:.0f} KB"
        except Exception: sz_str = ""
        self.status_lbl.configure(text=f"✅ {os.path.basename(file_path)} ({sz_str})", text_color=COLORS["neon_green"])
        self._result_row.pack(side="left", padx=(0, 10))

    def _on_error(self, err):
        self.is_cutting = False; self.cut_btn.configure(state="normal")
        self.progress_bar.stop(); self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0); self.progress_bar.configure(progress_color=COLORS["accent_red"])
        self.status_lbl.configure(text=f"❌ {err[:80]}", text_color=COLORS["accent_red"])

    def _open_result_folder(self):
        folder = self._last_output_dir or self.output_folder.get()
        if os.path.isdir(folder):
            if os.name == 'nt': os.startfile(folder)
            else: subprocess.Popen(['xdg-open', folder])

    def _reset_for_another(self):
        self.progress_bar.set(0); self.progress_bar.configure(progress_color=COLORS["progress_fill"])
        self.status_lbl.configure(text=t("waiting", self._lang), text_color=COLORS["text_secondary"])
        self._result_row.pack_forget()
        self.start_time.set("00:00:00"); self.end_time.set("00:05:00")
        self.output_name.set(""); self.input_file.set("")
        self.info_duration.configure(text=t("no_video_info", self._lang), text_color=COLORS["text_muted"])
        self.info_resolution.configure(text=""); self.info_filesize.configure(text="")





class VideoDownloaderPro(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # ─── Load Config ──────────────────────────────────────
        self._config = load_config()
        self._lang = self._config.get("language", "en")

        # ─── Window Setup ─────────────────────────────────────
        self.title(f"VT_Download — Video Downloader Pro v{__version__}")
        self.geometry("780x880")
        self.minsize(700, 750)
        self.configure(fg_color=COLORS["bg_dark"])

        # Try to set window icon if logo exists
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Try to load app icon
        icon_path = resource_path("logo.png")
        if os.path.exists(icon_path):
            try:
                # Use wm_iconphoto to support .png as window and taskbar icon
                img = ImageTk.PhotoImage(Image.open(icon_path))
                self.wm_iconphoto(True, img)
            except Exception:
                pass # fallback gracefully

        # Variables
        self.selected_platform = StringVar(value="")
        self.url_var = StringVar(value="")
        self.format_var = StringVar(value=self._config.get("format", "mp4"))
        self.quality_var = StringVar(value=self._config.get("quality", "Best Quality"))
        self.save_path_var = StringVar(value=self._config.get("save_path", os.path.expanduser("~\\Downloads")))
        self.progress_var = IntVar(value=0)
        self.use_cookies_var = ctk.BooleanVar(value=self._config.get("use_cookies", False))
        self.cookie_browser_var = StringVar(value=self._config.get("cookie_browser", "chrome"))
        self.platform_buttons = []
        self._cancel_flag = False
        self._download_process = None
        self._retry_count = 0
        self._max_retries = 3
        self._download_params = {}

        self._last_fetched_url = ""
        self._thumb_after_id = None
        self._last_downloaded_file = ""
        self.playlist_var = ctk.BooleanVar(value=False)
        self.proxy_var = StringVar(value="")
        self.sound_alert_var = ctk.BooleanVar(value=self._config.get("sound_alert", True))

        # ─── Collect UI refs for language refresh ──────────────
        self._ui_refs = {}

        # ─── Build UI ─────────────────────────────────────────
        self._build_header()
        self._build_main_container()
        self._build_status_bar()

        # ─── Keyboard Shortcuts ───────────────────────────────
        self.bind("<Return>", lambda e: self._start_download())
        self.bind("<Escape>", lambda e: self._cancel_download())
        self.bind("<Control-v>", lambda e: self.after(50, self._paste_url))

        # ─── URL Auto-Detect ──────────────────────────────────
        self.url_var.trace_add("write", self._on_url_changed)

        # ─── Auto-Update yt-dlp on Startup ────────────────────
        self.after(2000, self._auto_check_update)

        # ─── Start Title Animation ───────────────────────────
        self._title_color_idx = 0
        self.after(3000, self._animate_title)

    # ═══════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=64)
        header.pack(fill="x", padx=30, pady=(14, 6))
        header.pack_propagate(False)

        # Container for logo and text
        inner_head = ctk.CTkFrame(header, fg_color="transparent")
        inner_head.pack(expand=True)

        icon_path = resource_path("logo.png")
        if os.path.exists(icon_path):
            try:
                img = ctk.CTkImage(light_image=Image.open(icon_path), size=(40, 40))
                logo_lbl = ctk.CTkLabel(inner_head, image=img, text="")
                logo_lbl.pack(side="left", padx=(0, 12))
            except Exception:
                pass

        # Title with animated gradient
        self._title_label = ctk.CTkLabel(
            inner_head, text=t("app_title", self._lang),
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=COLORS["neon_blue"]
        )
        self._title_label.pack(side="left")

        # Version badge
        ver_badge = ctk.CTkLabel(
            inner_head, text=f"v{__version__}",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLORS["neon_purple"],
            fg_color=COLORS["accent_dark"],
            corner_radius=8, width=44, height=20
        )
        ver_badge.pack(side="left", padx=(8, 0), pady=(0, 8))

        # Language toggle button  🇰🇭 / 🇬🇧
        self._lang_btn = ctk.CTkButton(
            inner_head,
            text="🇰🇭 KH" if self._lang == "en" else "🇬🇧 EN",
            width=60, height=32,
            fg_color=COLORS["accent_dark"],
            hover_color=COLORS["gray_btn_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10,
            command=self._toggle_language
        )
        self._lang_btn.pack(side="right", padx=(8, 0))
        ToolTip(self._lang_btn, "ប្ដូរភាសា / Switch Language")

        # Theme toggle button
        self._theme_btn = ctk.CTkButton(
            inner_head, text="🌙", width=36, height=36,
            fg_color="transparent", hover_color=COLORS["border"],
            font=ctk.CTkFont(size=18), corner_radius=18,
            command=self._toggle_theme
        )
        self._theme_btn.pack(side="right", padx=(8, 0))
        ToolTip(self._theme_btn, t("toggle_theme", self._lang))

         # About button
        about_btn = ctk.CTkButton(
            inner_head, text="ℹ️", width=36, height=36,
            fg_color="transparent", hover_color=COLORS["border"],
            font=ctk.CTkFont(size=18), corner_radius=18,
            command=self._show_about
        )
        about_btn.pack(side="right", padx=(8, 0))
        ToolTip(about_btn, t("about", self._lang))

        # Check for App Updates button
        update_btn = ctk.CTkButton(
            inner_head, text="🔄", width=36, height=36,
            fg_color="transparent", hover_color=COLORS["border"],
            font=ctk.CTkFont(size=18), corner_radius=18,
            command=self._check_app_update
        )
        update_btn.pack(side="right", padx=(8, 0))
        ToolTip(update_btn, t("check_update", self._lang))

        # Subtitle — supported platforms
        self._subtitle_label = ctk.CTkLabel(
            header,
            text=t("app_subtitle", self._lang),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"]
        )
        self._subtitle_label.pack()

    # ═══════════════════════════════════════════════════════════
    # MAIN CONTAINER
    # ═══════════════════════════════════════════════════════════
    def _build_main_container(self):
        # ═══════════════════════════════════════════════════
        # ACTION + PROGRESS — packed FIRST at bottom, always visible
        # ═══════════════════════════════════════════════════
        bottom_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                    corner_radius=16, border_width=1,
                                    border_color=COLORS["border"])
        bottom_frame.pack(fill="x", side="bottom", padx=30, pady=(4, 4))

        self._section_actions(bottom_frame)
        self._section_progress(bottom_frame)

        # ═══════════════════════════════════════════════════
        # SETTINGS CARD — fills remaining space
        # ═══════════════════════════════════════════════════
        center_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        center_wrapper.pack(fill="both", expand=True)

        card = NeonFrame(center_wrapper, glow_color=COLORS["border"], fg_color=COLORS["bg_card"],
                         border_color=COLORS["border"], corner_radius=20)
        card.pack(fill="both", expand=True, padx=30, pady=(0, 4))

        self._section_platform(card)
        self._divider(card)
        self._section_url(card)
        self._build_thumbnail_area(card)
        self._divider(card)
        self._section_format(card)
        self._divider(card)
        self._section_save(card)
        self._divider(card)
        self._section_auth(card)
        self._divider(card)
        self._section_options(card)

        # ─── Footer: Support Contacts ───
        self._divider(card)
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", pady=(0, 2))

        inner_footer = ctk.CTkFrame(footer, fg_color="transparent")
        inner_footer.pack(expand=True)

        support_lbl = ctk.CTkLabel(
            inner_footer, text=t("support_contact", self._lang), 
            font=ctk.CTkFont(family="Segoe UI", size=12), 
            text_color=COLORS["text_secondary"]
        )
        support_lbl.pack(side="left", padx=5)

        tele_btn = ctk.CTkButton(
            inner_footer, text="📱 Telegram", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
            width=80, height=24, fg_color="transparent", 
            hover_color=COLORS["border"], text_color=COLORS["neon_blue"], 
            command=lambda: webbrowser.open("https://t.me/ny_vuthy_7")
        )
        tele_btn.pack(side="left", padx=5)

        fb_btn = ctk.CTkButton(
            inner_footer, text="📘 Facebook", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
            width=80, height=24, fg_color="transparent", 
            hover_color=COLORS["border"], text_color=COLORS["accent_blue"], 
            command=lambda: webbrowser.open("https://www.facebook.com/vuthyny7777/")
        )
        fb_btn.pack(side="left", padx=5)

        # Copyright line
        copyright_row = ctk.CTkFrame(card, fg_color="transparent")
        copyright_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(
            copyright_row, text=f"© 2026 Ny Vuthy • v{__version__} • All Rights Reserved",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_muted"]
        ).pack()

    # ─── Section Helpers ──────────────────────────────────────
    def _divider(self, parent):
        div = ctk.CTkFrame(parent, fg_color=COLORS["border"], height=1)
        div.pack(fill="x", padx=20, pady=3)

    # ═══════════════════════════════════════════════════════════
    # 1. PLATFORM SELECTION
    # ═══════════════════════════════════════════════════════════
    def _section_platform(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(8, 4))

        self._ui_refs['platform_title'] = SectionTitle(container, ICONS["platform"], t("select_platform", self._lang),
                     COLORS["neon_cyan"])
        self._ui_refs['platform_title'].pack(anchor="w", pady=(0, 6))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(fill="x")

        platforms = [
            (ICONS["youtube"],  "YouTube",   COLORS["accent_red"]),
            (ICONS["facebook"], "Facebook",  COLORS["accent_blue"]),
            (ICONS["tiktok"],   "TikTok",    COLORS["neon_pink"]),
            ("📷",              "Instagram", "#E1306C"),
            (ICONS["kuaishou"], "Kuaishou",  COLORS["accent_orange"]),
        ]

        for icon, name, color in platforms:
            pb = PlatformButton(btn_row, icon, name, color,
                                callback=self._on_platform_select)
            pb.pack(side="left", padx=(0, 6), fill="y")
            self.platform_buttons.append(pb)

        # Activate YouTube by default
        self.platform_buttons[0].set_active(True)
        self.selected_platform.set("YouTube")

    def _on_platform_select(self, btn):
        for pb in self.platform_buttons:
            pb.set_active(pb is btn)
        self.selected_platform.set(btn.name_lbl.cget("text"))

    # ═══════════════════════════════════════════════════════════
    # 2. VIDEO URL
    # ═══════════════════════════════════════════════════════════
    def _section_url(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=4)

        SectionTitle(container, ICONS["url"], t("video_url", self._lang),
                     COLORS["neon_blue"]).pack(anchor="w", pady=(0, 6))

        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x")

        self.url_entry = ctk.CTkEntry(
            row, textvariable=self.url_var,
            placeholder_text=t("paste_url_hint", self._lang),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["neon_blue"],
            border_width=2,
            corner_radius=12,
            height=44,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"]
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        paste_btn = GlowButton(
            row, text=f"{ICONS['paste']}  {t('paste', self._lang)}",
            fg_color=COLORS["neon_blue"],
            hover_color="#2563eb",
            width=90, height=44,
            command=self._paste_url
        )
        paste_btn.pack(side="right")

    def _paste_url(self):
        try:
            clipboard = self.clipboard_get()
            self.url_var.set(clipboard)
        except Exception:
            pass

    def _clean_url(self, url):
        """Clean and normalize the URL for reliable downloading."""
        url = url.strip().strip('"').strip("'")
        url = re.sub(r'[&?](fbclid|utm_\w+|si|feature|ref|source)[=][^&]*', '', url)
        url = url.replace('??', '?').rstrip('?&')
        return url

    # ─── Auto-Detect Platform ────────────────────────────────
    def _detect_platform(self, url):
        """Detect platform from URL string."""
        u = url.lower()
        if 'youtube.com' in u or 'youtu.be' in u:
            return 'YouTube'
        elif 'facebook.com' in u or 'fb.watch' in u or 'fb.com' in u:
            return 'Facebook'
        elif 'tiktok.com' in u:
            return 'TikTok'
        elif 'instagram.com' in u or 'instagr.am' in u:
            return 'Instagram'
        elif 'kuaishou.com' in u or 'kwai.com' in u:
            return 'Kuaishou'
        return None

    def _on_url_changed(self, *args):
        """Called when URL field changes — auto-detect platform and fetch thumbnail."""
        url = self.url_var.get().strip()
        # Auto-detect platform
        platform = self._detect_platform(url)
        if platform:
            for pb in self.platform_buttons:
                if pb.name_lbl.cget("text") == platform:
                    self._on_platform_select(pb)
                    break
        # Debounce thumbnail fetch (wait 1.2s after last keystroke)
        if self._thumb_after_id:
            self.after_cancel(self._thumb_after_id)
        if url and len(url) > 15 and url != self._last_fetched_url:
            self._thumb_after_id = self.after(1200, self._fetch_video_info_async, url)
        elif not url:
            self._hide_thumbnail()

    # ─── Thumbnail Preview ───────────────────────────────────
    def _build_thumbnail_area(self, parent):
        """Create thumbnail preview area (hidden until video info is fetched)."""
        self.thumb_container = ctk.CTkFrame(parent, fg_color="transparent", height=0)
        self.thumb_container.pack(fill="x")
        self.thumb_container.pack_propagate(False)

        inner = ctk.CTkFrame(self.thumb_container, fg_color=COLORS["bg_card_inner"],
                             corner_radius=12, border_width=1, border_color=COLORS["border"])
        inner.pack(fill="x", padx=24, pady=(8, 4))

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=10)

        self.thumb_image_label = ctk.CTkLabel(
            row, text="🎬", width=140, height=80,
            fg_color=COLORS["bg_input"], corner_radius=8,
            font=ctk.CTkFont(size=28)
        )
        self.thumb_image_label.pack(side="left", padx=(0, 12))

        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)

        self.thumb_title_label = ctk.CTkLabel(
            info_frame, text="",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_primary"], anchor="w", wraplength=350
        )
        self.thumb_title_label.pack(fill="x", anchor="w")

        detail_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        detail_row.pack(fill="x", anchor="w", pady=(6, 0))

        self.thumb_duration_label = ctk.CTkLabel(
            detail_row, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]
        )
        self.thumb_duration_label.pack(side="left", padx=(0, 16))

        self.thumb_platform_label = ctk.CTkLabel(
            detail_row, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["neon_blue"]
        )
        self.thumb_platform_label.pack(side="left")

    def _fetch_video_info_async(self, url):
        """Trigger background video info fetch."""
        self._last_fetched_url = url
        # Show loading state
        self.thumb_title_label.configure(text=t("fetching_info", self._lang))
        self.thumb_duration_label.configure(text="")
        self.thumb_platform_label.configure(text="")
        self.thumb_image_label.configure(text="⏳", image=None if not hasattr(self.thumb_image_label, '_ctk_image') else None)
        self.thumb_container.pack_propagate(True)
        thread = threading.Thread(target=self._fetch_video_info, args=(url,), daemon=True)
        thread.start()

    def _fetch_video_info(self, url):
        """Background: get video metadata via yt-dlp --dump-json."""
        ytdlp = self._find_ytdlp()
        if not ytdlp:
            return
        try:
            cmd = list(ytdlp) + [
                "--dump-json", "--no-download", "--no-warnings",
                "--socket-timeout", "10", "--no-check-certificates",
            ]
            if self.use_cookies_var.get():
                cmd += ["--cookies-from-browser", self.cookie_browser_var.get()]
            cmd.append(url)

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=20,
                encoding="utf-8", errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )

            if result.returncode == 0 and result.stdout.strip():
                info = json.loads(result.stdout.strip().split('\n')[0])
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', '')
                thumbnail_url = info.get('thumbnail', '')

                # Download thumbnail
                thumb_data = None
                if thumbnail_url:
                    try:
                        req = urllib.request.Request(thumbnail_url,
                            headers={'User-Agent': 'Mozilla/5.0'})
                        resp = urllib.request.urlopen(req, timeout=8)
                        thumb_data = resp.read()
                    except Exception:
                        pass

                self.after(0, self._display_video_info, title, duration, uploader, thumb_data)
            else:
                self.after(0, self._hide_thumbnail)
        except Exception:
            self.after(0, self._hide_thumbnail)

    def _display_video_info(self, title, duration, uploader, thumb_data):
        """Display video info and thumbnail in the UI."""
        # Format duration
        if duration:
            mins, secs = divmod(int(duration), 60)
            hours, mins = divmod(mins, 60)
            dur_str = f"{hours}:{mins:02d}:{secs:02d}" if hours else f"{mins}:{secs:02d}"
        else:
            dur_str = ""

        self.thumb_title_label.configure(text=title[:70] + ("..." if len(str(title)) > 70 else ""))
        self.thumb_duration_label.configure(text=f"⏱ {dur_str}" if dur_str else "")

        platform = self._detect_platform(self.url_var.get()) or ""
        self.thumb_platform_label.configure(
            text=f"📺 {platform}" + (f"  •  {uploader}" if uploader else ""))

        if thumb_data:
            try:
                img = Image.open(io.BytesIO(thumb_data))
                img = img.resize((140, 80), Image.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(140, 80))
                self.thumb_image_label.configure(image=ctk_img, text="")
                self.thumb_image_label._ctk_img_ref = ctk_img
            except Exception:
                self.thumb_image_label.configure(text="🎬", image=None)
        else:
            self.thumb_image_label.configure(text="🎬", image=None)

        # Show the container
        self.thumb_container.pack_propagate(True)

    def _hide_thumbnail(self):
        """Hide the thumbnail preview area."""
        self.thumb_container.pack_propagate(False)
        self.thumb_container.configure(height=0)
        self._last_fetched_url = ""

    # ─── Toast Helper ────────────────────────────────────────
    def _show_toast(self, message, toast_type="success", duration=4000):
        """Show a toast notification overlay."""
        ToastNotification(self, message, toast_type, duration)

    # ─── Auto-Update yt-dlp on Startup ───────────────────────
    def _auto_check_update(self):
        """Silently check and update yt-dlp on startup."""
        def _check():
            ytdlp = self._find_ytdlp()
            if not ytdlp:
                return
            try:
                is_frozen = getattr(sys, 'frozen', False)
                if not is_frozen and sys.executable in str(ytdlp):
                    cmd = [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"]
                else:
                    cmd = list(ytdlp) + ["-U"]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=60,
                    encoding="utf-8", errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                )
                if result.returncode == 0:
                    out = result.stdout.lower()
                    if "up to date" not in out and "already" not in out:
                        self.after(0, lambda: self._show_toast(
                            "yt-dlp has been updated to the latest version!", "success"))
            except Exception:
                pass
        thread = threading.Thread(target=_check, daemon=True)
        thread.start()

    # ─── App Self-Update System ──────────────────────────────
    # Configure this URL to your GitHub repo for releases
    APP_UPDATE_URL = "https://api.github.com/repos/vuthyny/VT_Download/releases/latest"
    APP_DOWNLOAD_KEY = "browser_download_url"  # Key in GitHub release assets

    def _check_app_update(self):
        """Check if a newer version of VT_Download is available on GitHub."""
        self.progress_label.configure(text=t("check_update", self._lang) + "...")
        self.progress_bar.set(0)

        def _check():
            try:
                req = urllib.request.Request(
                    self.APP_UPDATE_URL,
                    headers={"User-Agent": "VT_Download", "Accept": "application/vnd.github.v3+json"})
                resp = urllib.request.urlopen(req, timeout=15)
                data = json.loads(resp.read().decode("utf-8"))

                remote_version = data.get("tag_name", "").lstrip("vV").strip()
                current = __version__

                if remote_version and self._is_newer_version(remote_version, current):
                    # Find the download URL for windows zip
                    download_url = None
                    for asset in data.get("assets", []):
                        name = asset.get("name", "").lower()
                        if "win" in name and name.endswith(".zip"):
                            download_url = asset.get(self.APP_DOWNLOAD_KEY)
                            break
                    # Fallback: first zip asset
                    if not download_url:
                        for asset in data.get("assets", []):
                            if asset.get("name", "").endswith(".zip"):
                                download_url = asset.get(self.APP_DOWNLOAD_KEY)
                                break

                    self.after(0, lambda: self._show_app_update_available(
                        remote_version, download_url, data.get("body", "")))
                else:
                    self.after(0, lambda: self._show_toast(
                        t("app_up_to_date", self._lang).replace("{v}", current), "success"))
                    self.after(0, lambda: self.progress_label.configure(
                        text=t("app_up_to_date", self._lang).replace("{v}", current)))
            except Exception as e:
                self.after(0, lambda: self._show_toast(
                    f"Update check failed: {str(e)[:60]}", "error"))
                self.after(0, lambda: self.progress_label.configure(text=""))

        threading.Thread(target=_check, daemon=True).start()

    @staticmethod
    def _is_newer_version(remote, current):
        """Compare version strings like '3.1.0' > '3.0.0'."""
        try:
            r_parts = [int(x) for x in remote.split(".")]
            c_parts = [int(x) for x in current.split(".")]
            # Pad shorter list with zeros
            while len(r_parts) < len(c_parts): r_parts.append(0)
            while len(c_parts) < len(r_parts): c_parts.append(0)
            return r_parts > c_parts
        except (ValueError, AttributeError):
            return False

    def _show_app_update_available(self, version, download_url, release_notes):
        """Show update notification with download button."""
        msg = t("app_update_available", self._lang).replace("{v}", version)
        self._show_toast(msg, "success", 10000)
        self.progress_label.configure(text=msg)

        if download_url:
            self._pending_update_url = download_url
            self._pending_update_version = version
            # Show update button in progress area
            if hasattr(self, '_app_update_btn'):
                self._app_update_btn.destroy()
            self._app_update_btn = ctk.CTkButton(
                self.progress_bar.master,
                text=t("app_update_btn", self._lang),
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                fg_color=COLORS["neon_green"], hover_color="#16a34a",
                corner_radius=10, width=160, height=36,
                command=self._download_app_update)
            self._app_update_btn.pack(pady=(6, 0))

    def _download_app_update(self):
        """Download and apply app update."""
        if not hasattr(self, '_pending_update_url') or not self._pending_update_url:
            return

        url = self._pending_update_url
        version = self._pending_update_version
        if hasattr(self, '_app_update_btn'):
            self._app_update_btn.configure(state="disabled",
                text=t("app_downloading_update", self._lang))

        self.progress_label.configure(text=t("app_downloading_update", self._lang))
        self.progress_bar.set(0)

        def _do_update():
            import zipfile
            import shutil
            try:
                is_frozen = getattr(sys, 'frozen', False)
                if is_frozen:
                    app_dir = os.path.dirname(sys.executable)
                else:
                    app_dir = os.path.dirname(os.path.abspath(__file__))

                # Download zip to temp
                zip_path = os.path.join(app_dir, f"_update_{version}.zip")

                def _report(count, block_size, total):
                    if total > 0:
                        pct = min(count * block_size / total, 1.0)
                        self.after(0, lambda p=pct: self.progress_bar.set(p))

                urllib.request.urlretrieve(url, zip_path, reporthook=_report)

                # Extract to temp folder
                update_dir = os.path.join(app_dir, f"_update_temp")
                if os.path.exists(update_dir):
                    shutil.rmtree(update_dir, ignore_errors=True)

                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(update_dir)

                # Find the inner folder (GitHub zips often have one top-level folder)
                contents = os.listdir(update_dir)
                source_dir = update_dir
                if len(contents) == 1 and os.path.isdir(os.path.join(update_dir, contents[0])):
                    source_dir = os.path.join(update_dir, contents[0])

                # Create batch script to replace files after app closes
                bat_path = os.path.join(app_dir, "_apply_update.bat")
                exe_name = os.path.basename(sys.executable) if is_frozen else ""

                if is_frozen and exe_name:
                    bat_content = f'''@echo off
echo Applying VT_Download update to v{version}...
timeout /t 2 /nobreak > nul
xcopy /s /y /q "{source_dir}\\*" "{app_dir}\\"
rmdir /s /q "{update_dir}"
del "{zip_path}" 2>nul
echo Update complete! Starting app...
start "" "{os.path.join(app_dir, exe_name)}"
del "%~f0"
'''
                    with open(bat_path, 'w') as f:
                        f.write(bat_content)

                    self.after(0, lambda: self._show_toast(
                        t("app_update_restart", self._lang), "success", 8000))
                    self.after(0, lambda: self.progress_label.configure(
                        text=t("app_update_restart", self._lang)))
                    self.after(0, lambda: self.progress_bar.set(1.0))

                    if hasattr(self, '_app_update_btn'):
                        # Change button to restart
                        def _restart():
                            subprocess.Popen(
                                ["cmd", "/c", bat_path],
                                creationflags=subprocess.CREATE_NO_WINDOW)
                            self.destroy()
                            sys.exit(0)
                        self.after(0, lambda: self._app_update_btn.configure(
                            state="normal", text="🔄 Restart Now",
                            fg_color=COLORS["neon_blue"], command=_restart))
                else:
                    # Dev mode: just copy files over
                    for item in os.listdir(source_dir):
                        s = os.path.join(source_dir, item)
                        d = os.path.join(app_dir, item)
                        try:
                            if os.path.isdir(s):
                                if os.path.exists(d):
                                    shutil.rmtree(d, ignore_errors=True)
                                shutil.copytree(s, d)
                            else:
                                shutil.copy2(s, d)
                        except Exception:
                            pass
                    shutil.rmtree(update_dir, ignore_errors=True)
                    os.remove(zip_path) if os.path.exists(zip_path) else None

                    self.after(0, lambda: self._show_toast(
                        t("app_update_restart", self._lang), "success", 8000))
                    self.after(0, lambda: self.progress_label.configure(
                        text=t("app_update_restart", self._lang)))
                    self.after(0, lambda: self.progress_bar.set(1.0))

            except Exception as e:
                self.after(0, lambda: self._show_toast(
                    f"{t('app_update_failed', self._lang)}: {str(e)[:60]}", "error"))
                self.after(0, lambda: self.progress_label.configure(
                    text=t("app_update_failed", self._lang)))
                if hasattr(self, '_app_update_btn'):
                    self.after(0, lambda: self._app_update_btn.configure(
                        state="normal", text=t("app_update_btn", self._lang)))

        threading.Thread(target=_do_update, daemon=True).start()

    # ═══════════════════════════════════════════════════════════
    # 3. DOWNLOAD FORMAT
    # ═══════════════════════════════════════════════════════════
    def _section_format(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=4)

        SectionTitle(container, ICONS["format"], t("download_format", self._lang),
                     COLORS["neon_pink"]).pack(anchor="w", pady=(0, 6))

        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x")

        # Radio: Video (MP4)
        mp4_radio = ctk.CTkRadioButton(
            row, text=t("video_mp4", self._lang),
            variable=self.format_var, value="mp4",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"],
            fg_color=COLORS["neon_pink"],
            border_color=COLORS["neon_pink"],
            hover_color="#db2777",
            radiobutton_width=20, radiobutton_height=20
        )
        mp4_radio.pack(side="left", padx=(0, 24))

        # Radio: Audio (MP3)
        mp3_radio = ctk.CTkRadioButton(
            row, text=t("audio_mp3", self._lang),
            variable=self.format_var, value="mp3",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"],
            fg_color=COLORS["neon_cyan"],
            border_color=COLORS["neon_cyan"],
            hover_color="#0891b2",
            radiobutton_width=20, radiobutton_height=20
        )
        mp3_radio.pack(side="left", padx=(0, 32))

        # Spacer
        spacer = ctk.CTkFrame(row, fg_color="transparent", width=20)
        spacer.pack(side="left")

        # Quality label
        qual_label = ctk.CTkLabel(
            row, text=t("quality", self._lang),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        )
        qual_label.pack(side="left", padx=(0, 8))

        # Quality dropdown
        qualities = ["Best Quality", "1080p", "720p", "480p", "360p", "Audio Only"]
        quality_dropdown = ctk.CTkOptionMenu(
            row, variable=self.quality_var,
            values=qualities,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS["bg_input"],
            button_color=COLORS["neon_blue"],
            button_hover_color="#2563eb",
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["border_glow"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            corner_radius=10,
            width=160, height=38
        )
        quality_dropdown.pack(side="left")

    # ═══════════════════════════════════════════════════════════
    # 4. SAVE LOCATION
    # ═══════════════════════════════════════════════════════════
    def _section_save(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=4)

        SectionTitle(container, ICONS["folder"], t("save_location", self._lang),
                     COLORS["neon_orange"]).pack(anchor="w", pady=(0, 6))

        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x")

        self.save_entry = ctk.CTkEntry(
            row, textvariable=self.save_path_var,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["neon_orange"],
            border_width=2,
            corner_radius=12,
            height=44,
            text_color=COLORS["text_primary"]
        )
        self.save_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = GlowButton(
            row, text=f"{ICONS['browse']}  {t('browse', self._lang)}",
            fg_color=COLORS["neon_orange"],
            hover_color="#ea580c",
            width=100, height=44,
            command=self._browse_folder
        )
        browse_btn.pack(side="right")

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_path_var.get())
        if folder:
            self.save_path_var.set(folder)

    # ═══════════════════════════════════════════════════════════
    # 5. AUTHENTICATION & LOGIN REQUIRED
    # ═══════════════════════════════════════════════════════════
    def _section_auth(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=2)

        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x")

        cookie_switch = ctk.CTkSwitch(
            row, text=t("login_required", self._lang),
            variable=self.use_cookies_var,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"],
            progress_color=COLORS["neon_blue"]
        )
        cookie_switch.pack(side="left")

        browser_dropdown = ctk.CTkOptionMenu(
            row, variable=self.cookie_browser_var,
            values=["chrome", "edge", "firefox", "brave", "opera", "safari"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS["bg_input"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["border_glow"],
            dropdown_fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            width=100, height=28
        )
        browser_dropdown.pack(side="right")

    # ═══════════════════════════════════════════════════════════
    # 5b. OPTIONS — Playlist, Proxy, Sound
    # ═══════════════════════════════════════════════════════════
    def _section_options(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=2)

        SectionTitle(container, ICONS["tools"], t("options", self._lang),
                     COLORS["text_secondary"]).pack(anchor="w", pady=(0, 4))

        row1 = ctk.CTkFrame(container, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 6))

        # Playlist switch
        playlist_switch = ctk.CTkSwitch(
            row1, text=t("batch_download", self._lang),
            variable=self.playlist_var,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"],
            progress_color=COLORS["neon_orange"]
        )
        playlist_switch.pack(side="left")

        # Sound alert switch
        sound_switch = ctk.CTkSwitch(
            row1, text=t("sound_alert", self._lang),
            variable=self.sound_alert_var,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"],
            progress_color=COLORS["neon_green"]
        )
        sound_switch.pack(side="right")

        row2 = ctk.CTkFrame(container, fg_color="transparent")
        row2.pack(fill="x")

        # Proxy input
        proxy_label = ctk.CTkLabel(
            row2, text=t("proxy", self._lang),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        )
        proxy_label.pack(side="left", padx=(0, 8))

        proxy_entry = ctk.CTkEntry(
            row2, textvariable=self.proxy_var,
            placeholder_text="http://host:port or socks5://host:port",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=10,
            height=32,
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_muted"]
        )
        proxy_entry.pack(side="left", fill="x", expand=True)

    # ═══════════════════════════════════════════════════════════
    # 6. ACTION BUTTONS
    # ═══════════════════════════════════════════════════════════
    def _section_actions(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(6, 2))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack()

        download_btn = ctk.CTkButton(
            btn_row,
            text=f"{ICONS['download']}   {t('download', self._lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=COLORS["gradient_pink1"],
            hover_color=COLORS["gradient_pink2"],
            corner_radius=14,
            width=180, height=50,
            command=self._start_download
        )
        download_btn.pack(side="left", padx=(0, 16))
        ToolTip(download_btn, t("tooltip_download", self._lang))

        cancel_btn = ctk.CTkButton(
            btn_row,
            text=f"{ICONS['cancel']}   {t('cancel', self._lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=COLORS["gray_btn"],
            hover_color=COLORS["gray_btn_hover"],
            corner_radius=14,
            width=120, height=50,
            command=self._cancel_download
        )
        cancel_btn.pack(side="left", padx=(0, 16))
        ToolTip(cancel_btn, t("tooltip_cancel", self._lang))

        update_btn = ctk.CTkButton(
            btn_row,
            text=f"{ICONS['reset']}   {t('update_core', self._lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            corner_radius=14,
            width=140, height=50,
            command=self._update_tool
        )
        update_btn.pack(side="left", padx=(0, 16))
        ToolTip(update_btn, t("tooltip_update", self._lang))

        split_btn = ctk.CTkButton(
            btn_row,
            text=f"✂️ {t('splitter', self._lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            corner_radius=14,
            width=120, height=50,
            command=self._open_cutter
        )
        split_btn.pack(side="left")
        ToolTip(split_btn, t("tooltip_splitter", self._lang))

    def _open_cutter(self):
        VideoCutterWindow(self, lang=self._lang)



    @staticmethod
    def _find_ytdlp():
        """Find yt-dlp: prefer bundled, then local, then path."""
        is_frozen = getattr(sys, 'frozen', False)
        
        if is_frozen:
            exe_dir = os.path.dirname(sys.executable)
            local_ytdlp = os.path.join(exe_dir, "yt-dlp.exe")
            
            # Extract yt-dlp, ffmpeg, ffprobe from _MEIPASS if not already next to exe
            import shutil
            for tool_name in ["yt-dlp.exe", "ffmpeg.exe", "ffprobe.exe"]:
                local_tool = os.path.join(exe_dir, tool_name)
                if not os.path.exists(local_tool):
                    bundled_tool = os.path.join(sys._MEIPASS, tool_name)
                    if os.path.exists(bundled_tool):
                        try:
                            shutil.copy2(bundled_tool, local_tool)
                        except Exception:
                            pass  # May fail if dir is read-only
                        
            if os.path.exists(local_ytdlp):
                return [local_ytdlp]
            # Fallback: run from _MEIPASS temp folder
            bundled = os.path.join(sys._MEIPASS, "yt-dlp.exe")
            if os.path.exists(bundled):
                return [bundled]
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            local_ytdlp = os.path.join(base_dir, "yt-dlp.exe")
            if os.path.exists(local_ytdlp):
                return [local_ytdlp]
            
        # Check global PATH
        import shutil
        if shutil.which("yt-dlp"):
            return ["yt-dlp"]
            
        # Try as Python module (dev mode only)
        if not is_frozen:
            try:
                subprocess.run(
                    [sys.executable, "-m", "yt_dlp", "--version"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    timeout=5
                )
                return [sys.executable, "-m", "yt_dlp"]
            except Exception:
                pass
                
        return None

    def _download_missing_ytdlp(self, callback=None):
        """Download yt-dlp.exe from GitHub if missing."""
        is_frozen = getattr(sys, 'frozen', False)
        base_dir = os.path.dirname(sys.executable) if is_frozen else os.path.dirname(os.path.abspath(__file__))
        target_path = os.path.join(base_dir, "yt-dlp.exe" if os.name == 'nt' else "yt-dlp")
        
        self.progress_var.set(0)
        self.progress_bar.set(0)
        self.progress_label.configure(text=t("downloading_core", self._lang))
        self._show_toast(t("core_not_found", self._lang), "warning", 5000)
        
        def _reporthook(count, block_size, total_size):
            if total_size > 0:
                pct = int(min((count * block_size * 100) / total_size, 100))
                self.after(0, lambda p=pct: self.progress_var.set(p))
                self.after(0, lambda p=pct: self.progress_bar.set(p / 100.0))
                self.after(0, lambda p=pct: self.progress_label.configure(text=f"Downloading core... {p}%"))

        def _download_task():
            try:
                # yt-dlp windows executable url
                url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
                if os.name != 'nt':
                    url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
                
                urllib.request.urlretrieve(url, target_path, reporthook=_reporthook)
                
                if os.name != 'nt':
                    os.chmod(target_path, 0o755)
                    
                self.after(0, lambda: self.progress_label.configure(text=t("core_installed", self._lang)))
                self.after(0, lambda: self._show_toast(t("core_installed_toast", self._lang), "success", 5000))
                
                if callback:
                    self.after(1000, callback)
            except Exception as e:
                self.after(0, lambda: self.progress_label.configure(text=t("core_download_failed", self._lang)))
                self.after(0, lambda err=str(e): self._show_toast(f"Error downloading yt-dlp: {err[:80]}", "error", 8000))

        threading.Thread(target=_download_task, daemon=True).start()

    def _start_download(self):
        """Start downloading the video using yt-dlp."""
        url = self.url_var.get().strip()
        if not url:
            self._show_toast(t("paste_url_first", self._lang), "warning")
            return

        self._ytdlp_cmd = self._find_ytdlp()
        if not self._ytdlp_cmd:
            self._download_missing_ytdlp(self._start_download)
            return

        save_path = self.save_path_var.get().strip()
        if not os.path.isdir(save_path):
            self._show_toast(t("save_not_exist", self._lang), "warning")
            return

        # Clean URL for reliability
        url = self._clean_url(url)

        # Store params for retry
        self._download_params = {
            'url': url,
            'save_path': save_path,
            'fmt': self.format_var.get(),
            'quality': self.quality_var.get(),
            'use_cookies': self.use_cookies_var.get(),
            'cookie_browser': self.cookie_browser_var.get(),
            'playlist': self.playlist_var.get(),
            'proxy': self.proxy_var.get().strip(),
        }

        # Reset state
        self._cancel_flag = False
        self._download_process = None
        self._retry_count = 0
        self.progress_var.set(0)
        self.progress_bar.set(0)
        self.speed_label.configure(text="")
        self.eta_label.configure(text="")
        self.progress_label.configure(text=t("starting_download", self._lang))
        self._last_downloaded_file = ""
        self._hide_open_buttons()
        self.progress_bar.configure(progress_color=COLORS["progress_fill"])

        self._attempt_download()

    def _build_download_cmd(self, retry_level=0):
        """Build yt-dlp command. retry_level controls fallback strategy."""
        params = self._download_params

        # Find ffmpeg location for merging video+audio
        is_frozen = getattr(sys, 'frozen', False)
        base_dir = os.path.dirname(sys.executable) if is_frozen else os.path.dirname(os.path.abspath(__file__))
        ffmpeg_dir = base_dir  # ffmpeg.exe should be in the same folder

        cmd = list(self._ytdlp_cmd) + [
            "--newline",
            "--no-colors",
            "--restrict-filenames",
            "--concurrent-fragments", "4",
            "--retries", "10",
            "--fragment-retries", "10",
            "--extractor-retries", "5",
            "--file-access-retries", "3",
            "--retry-sleep", "exp=1:30:2",
            "--socket-timeout", "30",
            "--no-mtime",
            "--ffmpeg-location", ffmpeg_dir,  # Always point to our bundled ffmpeg
        ]

        fmt = params['fmt']
        quality = params['quality']

        if fmt == "mp3":
            # ── Audio: MP3 + embedded thumbnail ──
            cmd += [
                "-x", "--audio-format", "mp3", "--audio-quality", "0",
                "--embed-thumbnail",  # Cover art for music players
            ]
        else:
            # ── Video: ensure universal MP4 (H.264 + AAC) ──
            if retry_level == 0:
                # Attempt 1: Specific quality format
                quality_map = {
                    "Best Quality": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
                    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                    "720p":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]",
                    "480p":  "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]",
                    "360p":  "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best[height<=360]",
                    "Audio Only": "bestaudio[ext=m4a]/bestaudio/best",
                }
                fmt_str = quality_map.get(quality, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best")
                cmd += ["-f", fmt_str]
            elif retry_level == 1:
                # Attempt 2: Pre-merged best — no merge needed
                cmd += ["-f", "b"]
            else:
                # Attempt 3: No format flag — full auto
                pass

            if quality != "Audio Only":
                # Force MP4 container (compatible with all devices/players)
                cmd += ["--merge-output-format", "mp4"]
                # Recode to H.264+AAC if source is WebM/VP9 (ensures phone/TV/player support)
                cmd += ["--remux-video", "mp4"]
                # Embed subtitles if available (as soft subs in MP4)
                cmd += ["--embed-subs", "--sub-langs", "all"]
                # Embed thumbnail as MP4 cover art
                cmd += ["--embed-thumbnail"]
            else:
                # Audio-only: extract to M4A for universal support
                cmd += ["-x", "--audio-format", "m4a", "--audio-quality", "0"]

        # Output template
        output_template = os.path.join(params['save_path'], "%(title)s.%(ext)s")
        cmd += ["-o", output_template]

        # Add cookies if selected
        if params['use_cookies']:
            cmd += ["--cookies-from-browser", params['cookie_browser']]

        # Playlist handling
        if params.get('playlist'):
            cmd += ["--yes-playlist"]
        else:
            cmd += ["--no-playlist"]

        # Proxy support
        proxy = params.get('proxy', '')
        if proxy:
            cmd += ["--proxy", proxy]
        else:
            cmd += ["--proxy", ""]

        # Extra resilience on retries
        if retry_level >= 1:
            cmd += ["--no-check-certificates"]
        if retry_level >= 2:
            cmd += ["--legacy-server-connect"]

        if params.get('_cookie_file') and not params.get('use_cookies'):
            cmd += ["--cookies", params['_cookie_file']]
        if params.get('_user_agent'):
            cmd += ["--user-agent", params['_user_agent']]

        cmd.append(params.get('_direct_url') or params['url'])
        return cmd

    def _attempt_download(self):
        """Attempt download with current retry level."""
        self._retry_count += 1
        retry_level = self._retry_count - 1

        if retry_level > 0:
            self.progress_bar.set(0)
            self.progress_var.set(0)
            self.speed_label.configure(text="")
            self.eta_label.configure(text="")
            strategy = ["Specific format", "Simplified format", "Auto format"][min(retry_level, 2)]
            self.progress_label.configure(
                text=f"⟳ Retry {self._retry_count}/{self._max_retries} — {strategy}..."
            )

        def _preflight_and_run():
            params = self._download_params
            url = params.get('url', '')
            
            # Stealth Bypass Logic on first attempt
            if retry_level == 0 and browser_engine and browser_engine.is_playwright_installed():
                def _prog(msg):
                    self.after(0, lambda m=msg: self.progress_label.configure(text=m))
                
                try:
                    # Setup headless browser engine (downloads Chromium once to AppData if missing)
                    success, msg = browser_engine.setup_playwright_browsers(_prog)
                    if not success:
                        print(f"Playwright setup error: {msg}")

                    direct_url, cookie_file, ua = browser_engine.sniff_video_context(url, _prog)
                    if direct_url:
                        params['_direct_url'] = direct_url
                    if cookie_file:
                        params['_cookie_file'] = cookie_file
                    if ua:
                        params['_user_agent'] = ua
                except Exception as e:
                    print(f"Stealth bypass failed: {e}")

            cmd = self._build_download_cmd(retry_level)
            self._run_download(cmd)

        thread = threading.Thread(target=_preflight_and_run, daemon=True)
        thread.start()

    def _run_download(self, cmd):
        """Execute yt-dlp in a subprocess with retry support."""
        try:
            self._download_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            # Enhanced regex: capture percentage, speed, and ETA
            progress_re = re.compile(
                r'\[download\]\s+(\d+\.?\d*)%\s+of\s+~?\s*\S+'
                r'(?:\s+at\s+(\S+))?'
                r'(?:\s+ETA\s+(\S+))?'
            )

            error_lines = []

            for line in self._download_process.stdout:
                if self._cancel_flag:
                    self._download_process.terminate()
                    self.after(0, self._on_download_cancelled)
                    return

                line = line.strip()
                if not line:
                    continue

                if "ERROR:" in line:
                    error_lines.append(line)

                match = progress_re.search(line)
                if match:
                    pct = float(match.group(1))
                    speed = match.group(2) or ""
                    eta = match.group(3) or ""
                    self.after(0, self._update_progress, pct, speed, eta)
                elif "[download] Destination:" in line:
                    filename = line.split("Destination:", 1)[-1].strip()
                    short = os.path.basename(filename)
                    self.after(0, self.progress_label.configure,
                               {"text": f"⬇ {short[:50]}..."})
                    self.after(0, self._set_last_file, os.path.join(
                        self._download_params.get('save_path', ''), short))
                elif "[Merger]" in line or "[ExtractAudio]" in line:
                    self.after(0, self.progress_label.configure,
                               {"text": "⚙ Processing..."})
                elif "[download]" not in line and "%" not in line:
                    error_lines.append(line)

            self._download_process.wait()
            rc = self._download_process.returncode

            if self._cancel_flag:
                self.after(0, self._on_download_cancelled)
            elif rc == 0:
                self.after(0, self._on_download_complete)
            else:
                # Auto-retry with fallback strategy
                if self._retry_count < self._max_retries:
                    self.after(800, self._attempt_download)
                else:
                    real_errors = [l for l in error_lines if "ERROR:" in l]
                    if real_errors:
                        detail = "\n".join(real_errors[-5:])
                    elif error_lines:
                        detail = "\n".join(error_lines[-8:])
                    else:
                        detail = f"yt-dlp exited with code {rc}"
                    self.after(0, self._on_download_error, detail)

        except Exception as e:
            if self._retry_count < self._max_retries:
                self.after(800, self._attempt_download)
            else:
                self.after(0, self._on_download_error, str(e))

    def _update_progress(self, pct, speed="", eta=""):
        """Update progress bar, speed, and ETA from the main thread."""
        self.progress_var.set(int(pct))
        self.progress_bar.set(pct / 100)
        self.progress_label.configure(text=f"{pct:.1f}%")
        if speed:
            self.speed_label.configure(text=f"🚀 {speed}")
        if eta:
            self.eta_label.configure(text=f"⏱ ETA {eta}")

    def _on_download_complete(self):
        self.progress_bar.configure(progress_color=COLORS["neon_green"])
        self.progress_bar.set(1.0)
        self.progress_var.set(100)
        self.progress_label.configure(text=t("download_complete", self._lang))
        self.speed_label.configure(text="")
        self.eta_label.configure(text="")
        self.url_var.set("")
        self._show_toast(t("download_success", self._lang), "success", 5000)
        self._show_open_buttons()
        # Sound alert
        if self.sound_alert_var.get():
            self._play_sound_alert()

    def _on_download_cancelled(self):
        self.progress_bar.set(0)
        self.progress_var.set(0)
        self.progress_label.configure(text=t("cancelled", self._lang))
        self.speed_label.configure(text="")
        self.eta_label.configure(text="")

    def _on_download_error(self, error_msg):
        self.progress_bar.configure(progress_color=COLORS["accent_red"])
        self.progress_label.configure(text=t("failed_attempts", self._lang).replace("{n}", str(self._retry_count)))
        self.speed_label.configure(text="")
        self.eta_label.configure(text="")

        suggestions = "\n\n💡 Suggestions:"
        err_lower = error_msg.lower()
        if "login" in err_lower or "private" in err_lower or "sign in" in err_lower:
            suggestions += "\n• Enable 'Login Required' and select your browser"
        if "format" in err_lower or "requested format" in err_lower:
            suggestions += "\n• Try 'Best Quality' or a different quality setting"
        suggestions += "\n• Click '🔄 Update Core' to update yt-dlp"
        suggestions += "\n• Check if the video URL is correct and accessible"

        self._show_toast(
            f"Download failed: {error_msg[:120]}", "error", 8000)

    def _cancel_download(self):
        self._cancel_flag = True
        self._retry_count = self._max_retries  # Prevent auto-retry
        if hasattr(self, '_download_process') and self._download_process:
            try:
                self._download_process.terminate()
            except Exception:
                pass
        self.progress_var.set(0)
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        self.speed_label.configure(text="")
        self.eta_label.configure(text="")

    def _update_tool(self):
        """Update yt-dlp core engine to the latest version."""
        if hasattr(self, '_download_process') and self._download_process:
            self._show_toast(t("wait_download_finish", self._lang), "warning")
            return

        self._ytdlp_cmd = self._find_ytdlp()
        if not self._ytdlp_cmd:
            self._download_missing_ytdlp(self._update_tool)
            return

        self.progress_var.set(0)
        self.progress_bar.set(0)
        self.progress_label.configure(text=t("checking_updates", self._lang))

        # Decide update command
        is_frozen = getattr(sys, 'frozen', False)
        if not is_frozen and sys.executable in self._ytdlp_cmd:
            # Installed via python -m pip
            cmd = [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"]
        else:
            # Standalone binary
            cmd = list(self._ytdlp_cmd) + ["-U"]

        thread = threading.Thread(target=self._run_update, args=(cmd,), daemon=True)
        thread.start()

    def _run_update(self, cmd):
        """Execute the yt-dlp update process in background."""
        try:
            self._download_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            output_log = []
            for line in self._download_process.stdout:
                line = line.strip()
                if not line:
                    continue
                output_log.append(line)
                self.after(0, self.progress_label.configure, {"text": f"Updating: {line[:60]}..."})

            self._download_process.wait()
            rc = self._download_process.returncode
            self._download_process = None

            if rc == 0:
                self.after(0, lambda: self.progress_bar.set(1.0))
                self.after(0, lambda: self.progress_label.configure(text=t("update_complete", self._lang)))
                self.after(0, lambda: self._show_toast(t("ytdlp_updated", self._lang), "success", 5000))
            else:
                err_msg = "\n".join(output_log[-8:]) if output_log else "Unknown error."
                self.after(0, lambda: self.progress_label.configure(text=t("update_failed", self._lang)))
                self.after(0, lambda: self._show_toast(f"Update failed: {err_msg[:80]}", "error", 6000))

        except Exception as e:
            self._download_process = None
            self.after(0, lambda: self.progress_label.configure(text=t("update_failed", self._lang)))
            self.after(0, lambda: self._show_toast(f"Update error: {str(e)[:80]}", "error", 6000))

    # ═══════════════════════════════════════════════════════════
    # 6. PROGRESS BAR
    # ═══════════════════════════════════════════════════════════
    def _section_progress(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=(4, 8))

        SectionTitle(container, ICONS["progress"], t("download_progress", self._lang),
                     COLORS["neon_green"]).pack(anchor="w", pady=(0, 6))

        self.progress_bar = ctk.CTkProgressBar(
            container,
            fg_color=COLORS["progress_bg"],
            progress_color=COLORS["progress_fill"],
            corner_radius=8,
            height=14
        )
        self.progress_bar.pack(fill="x", pady=(0, 6))
        self.progress_bar.set(0)

        info_row = ctk.CTkFrame(container, fg_color="transparent")
        info_row.pack(fill="x")

        self.progress_label = ctk.CTkLabel(
            info_row, text="0%",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["neon_cyan"]
        )
        self.progress_label.pack(side="left")

        self.speed_label = ctk.CTkLabel(
            info_row, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]
        )
        self.speed_label.pack(side="right")

        self.eta_label = ctk.CTkLabel(
            info_row, text="",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"]
        )
        self.eta_label.pack(side="right", padx=(0, 16))

        # Open folder/file buttons (hidden initially)
        self.open_btn_row = ctk.CTkFrame(container, fg_color="transparent")
        # NOT packed initially — shown after download completes

        self.open_folder_btn = ctk.CTkButton(
            self.open_btn_row, text=t("open_folder", self._lang),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLORS["neon_orange"], hover_color="#ea580c",
            corner_radius=10, width=130, height=34,
            command=self._open_download_folder
        )
        self.open_folder_btn.pack(side="left", padx=(0, 10))

        self.open_file_btn = ctk.CTkButton(
            self.open_btn_row, text=t("open_file", self._lang),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLORS["neon_green"], hover_color="#16a34a",
            corner_radius=10, width=130, height=34,
            command=self._open_downloaded_file
        )
        self.open_file_btn.pack(side="left")

    def _set_last_file(self, filepath):
        """Track the last downloaded file path."""
        self._last_downloaded_file = filepath

    def _show_open_buttons(self):
        """Show Open Folder/File buttons after download."""
        self.open_btn_row.pack(fill="x", pady=(8, 0))

    def _hide_open_buttons(self):
        """Hide Open Folder/File buttons."""
        self.open_btn_row.pack_forget()

    def _open_download_folder(self):
        """Open the download folder in file explorer."""
        folder = self.save_path_var.get().strip()
        if os.path.isdir(folder):
            if os.name == 'nt':
                os.startfile(folder)
            else:
                subprocess.Popen(['xdg-open', folder])
        else:
            self._show_toast(t("folder_not_found", self._lang), "warning")

    def _open_downloaded_file(self):
        """Open the last downloaded file."""
        if self._last_downloaded_file and os.path.isfile(self._last_downloaded_file):
            if os.name == 'nt':
                os.startfile(self._last_downloaded_file)
            else:
                subprocess.Popen(['xdg-open', self._last_downloaded_file])
        else:
            # Fallback: open folder
            self._open_download_folder()

    def _play_sound_alert(self):
        """Play a notification sound when download finishes."""
        try:
            if winsound:
                winsound.MessageBeep(winsound.MB_OK)
            else:
                self.bell()
        except Exception:
            self.bell()

    # ─── Status Bar ───────────────────────────────────────
    def _build_status_bar(self):
        """Status bar at the bottom showing yt-dlp version."""
        bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=28, corner_radius=0)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_label = ctk.CTkLabel(
            bar, text="⚙ Checking yt-dlp...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"]
        )
        self._status_label.pack(side="left", padx=16)

        self._shortcut_label = ctk.CTkLabel(
            bar, text=t("shortcuts", self._lang),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"]
        )
        self._shortcut_label.pack(side="right", padx=16)

        # Fetch yt-dlp version in background
        def _get_ver():
            ytdlp = self._find_ytdlp()
            if ytdlp:
                try:
                    result = subprocess.run(
                        list(ytdlp) + ["--version"],
                        capture_output=True, text=True, timeout=10,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                    )
                    ver = result.stdout.strip()
                    self.after(0, lambda: self._status_label.configure(
                        text=f"⚙ yt-dlp v{ver}"))
                except Exception:
                    self.after(0, lambda: self._status_label.configure(
                        text="⚙ yt-dlp (version unknown)"))
            else:
                self.after(0, lambda: self._status_label.configure(
                    text="⚠ yt-dlp not found", text_color=COLORS["accent_red"]))
        threading.Thread(target=_get_ver, daemon=True).start()

    # ─── Animated Title ───────────────────────────────────
    def _animate_title(self):
        """Cycle the title color through a gradient palette."""
        colors = ["#58a6ff", "#39c5cf", "#3fb950", "#d29922", "#ff7b72", "#bc8cff"]
        self._title_label.configure(text_color=colors[self._title_color_idx % len(colors)])
        self._title_color_idx += 1
        self.after(2500, self._animate_title)

    # ─── Theme Toggle ─────────────────────────────────────
    def _toggle_theme(self):
        """Toggle between dark and light appearance mode."""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self._theme_btn.configure(text="☀")
        else:
            ctk.set_appearance_mode("dark")
            self._theme_btn.configure(text="🌙")

    # ─── Language Toggle ──────────────────────────────────
    def _toggle_language(self):
        """Toggle between English and Khmer, then rebuild the entire UI."""
        self._lang = "km" if self._lang == "en" else "en"
        self._save_preferences()

        # Destroy all children and rebuild
        for widget in self.winfo_children():
            widget.destroy()

        self.platform_buttons = []
        self._ui_refs = {}
        self._build_header()
        self._build_main_container()
        self._build_status_bar()

        # Re-bind shortcuts
        self.bind("<Return>", lambda e: self._start_download())
        self.bind("<Escape>", lambda e: self._cancel_download())
        self.bind("<Control-v>", lambda e: self.after(50, self._paste_url))
        self.url_var.trace_add("write", self._on_url_changed)

        self._show_toast(
            "ភាសាបានប្ដូរទៅ ខ្មែរ" if self._lang == "km" else "Language changed to English",
            "info", 2000
        )

    # ─── Save Preferences ─────────────────────────────────
    def _save_preferences(self):
        """Save user preferences to config file."""
        cfg = {
            "language": self._lang,
            "format": self.format_var.get(),
            "quality": self.quality_var.get(),
            "save_path": self.save_path_var.get(),
            "use_cookies": self.use_cookies_var.get(),
            "cookie_browser": self.cookie_browser_var.get(),
            "sound_alert": self.sound_alert_var.get(),
        }
        save_config(cfg)

    # ─── About Dialog ─────────────────────────────────────
    def _show_about(self):
        """Show About dialog with copyright and version info."""
        L = self._lang
        about = ctk.CTkToplevel(self)
        about.title(t("about", L))
        about.geometry("440x450")
        about.resizable(False, False)
        about.attributes("-topmost", True)
        about.configure(fg_color=COLORS["bg_dark"])

        # Center on parent
        about.transient(self)
        about.grab_set()

        # Logo/Title
        ctk.CTkLabel(
            about, text="🎬 VT_Download",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=COLORS["neon_blue"]
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            about, text=f"Version {__version__}",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS["neon_purple"]
        ).pack()

        # Divider
        ctk.CTkFrame(about, fg_color=COLORS["border_glass"], height=1).pack(
            fill="x", padx=40, pady=12)

        # Description
        ctk.CTkLabel(
            about, text=t("about_desc", L),
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"], justify="center"
        ).pack()

        # Copyright
        ctk.CTkFrame(about, fg_color=COLORS["border_glass"], height=1).pack(
            fill="x", padx=40, pady=12)

        ctk.CTkLabel(
            about, text=__copyright__,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["neon_orange"]
        ).pack()

        ctk.CTkLabel(
            about, text=t("licensed_software", L),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"], justify="center"
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            about, text=t("trademark_notice", L),
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_muted"]
        ).pack(pady=(2, 0))

        # Contact & Purchase
        ctk.CTkFrame(about, fg_color=COLORS["border_glass"], height=1).pack(
            fill="x", padx=40, pady=10)

        ctk.CTkLabel(
            about, text=t("purchase_support", L),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(0, 6))

        contact_row = ctk.CTkFrame(about, fg_color="transparent")
        contact_row.pack()

        ctk.CTkButton(
            contact_row, text="📱 Telegram", width=100, height=30,
            fg_color=COLORS["neon_blue"], hover_color="#2563eb",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=lambda: webbrowser.open("https://t.me/ny_vuthy_7")
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            contact_row, text="📘 Facebook", width=100, height=30,
            fg_color=COLORS["accent_blue"], hover_color="#1d4ed8",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=lambda: webbrowser.open("https://www.facebook.com/vuthyny7777/")
        ).pack(side="left", padx=6)

        # Close button
        ctk.CTkButton(
            about, text=t("close", L), width=100, height=34,
            fg_color=COLORS["gray_btn"], hover_color=COLORS["gray_btn_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=10, command=about.destroy
        ).pack(pady=(12, 14))


# ─── Entry Point ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    app = VideoDownloaderPro()
    app.mainloop()
