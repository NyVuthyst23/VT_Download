"""
╔══════════════════════════════════════════════════════════════╗
║          VT_Download — Video Transformer Module              ║
║                                                              ║
║  Batch-process videos to remove copyright fingerprints       ║
║  and create visually distinct versions for content creators. ║
║                                                              ║
║  Transformations applied:                                    ║
║    • Horizontal Flip (hflip)                                 ║
║    • Auto-Crop & Zoom (scale 110% + center crop)             ║
║    • Speed 1.05x (setpts + atempo; pitch stable during       ║
║      speed change, then separately shifted +2 semitones)     ║
║    • Audio Pitch +2 semitones (asetrate + aresample)         ║
║    • Color Correction (brightness/contrast/saturation)       ║
║    • Metadata Removal (strip all EXIF/original metadata)     ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import threading
import subprocess
import time
import logging
from tkinter import filedialog, StringVar

import customtkinter as ctk

# ─── Color Palette (matches main app) ────────────────────────────────────────
COLORS = {
    "bg_dark":        "#0a0e17",
    "bg_card":        "#131a27",
    "bg_card_inner":  "#0d1220",
    "bg_card_glass":  "#161d2e",
    "bg_input":       "#080c14",
    "border":         "#1e2d3d",
    "border_glow":    "#58a6ff",
    "border_glass":   "#2a3a4f",
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
    "gray_btn":       "#1e293b",
    "gray_btn_hover": "#334155",
    "progress_bg":    "#1e293b",
    "progress_fill":  "#3b82f6",
}

# Supported video formats for batch processing
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".wmv", ".m4v", ".ts"}

# Encoding quality settings
VIDEO_CRF = "18"        # CRF 18 = high quality (lower = better; 18 is near-lossless)
AUDIO_BITRATE = "192k"  # Audio bitrate for AAC output

logger = logging.getLogger("video_transformer")


def _find_ffmpeg():
    """Find ffmpeg executable: prefer bundled, then local, then PATH."""
    is_frozen = getattr(sys, "frozen", False)
    if is_frozen:
        exe_dir = os.path.dirname(sys.executable)
        bundled = os.path.join(exe_dir, "ffmpeg.exe")
        if os.path.exists(bundled):
            return bundled
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            mei = os.path.join(meipass, "ffmpeg.exe")
            if os.path.exists(mei):
                return mei

    # Look next to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local = os.path.join(script_dir, "ffmpeg.exe")
    if os.path.exists(local):
        return local

    # Fall back to system PATH
    import shutil
    path_ffmpeg = shutil.which("ffmpeg")
    if path_ffmpeg:
        return path_ffmpeg

    return "ffmpeg"


def build_ffmpeg_filter(speed: float = 1.05) -> tuple[str, str]:
    """
    Build FFmpeg video and audio filter strings for all transformations.

    Video chain:
      hflip  →  scale 110%  →  crop to original size (center)  →  setpts for speed  →  eq (color)

    Audio chain:
      atempo (speed, pitch unchanged during speed)  →  asetrate (pitch +2 semitones)  →  aresample

    Returns (vf_string, af_string).
    """
    # ── Video filters ──────────────────────────────────────────────────────────
    # 1. Horizontal flip
    vf_parts = ["hflip"]

    # 2. Scale to 110% of original dimensions (iw/ih = input width/height)
    vf_parts.append("scale=iw*1.1:ih*1.1")

    # 3. Center-crop back to original dimensions
    vf_parts.append("crop=iw/1.1:ih/1.1")

    # 4. Speed adjustment (setpts: presentation timestamps)
    pts_factor = round(1.0 / speed, 6)
    vf_parts.append(f"setpts={pts_factor}*PTS")

    # 5. Color correction: brightness +5%, contrast +10%, saturation +10%
    #    eq filter: brightness range [-1,1], contrast range [0,2], saturation range [0,3]
    vf_parts.append("eq=brightness=0.05:contrast=1.10:saturation=1.10")

    vf = ",".join(vf_parts)

    # ── Audio filters ──────────────────────────────────────────────────────────
    af_parts = []

    # 1. Speed adjustment with atempo (keeps pitch stable, range 0.5–2.0)
    af_parts.append(f"atempo={speed}")

    # 2. Pitch shift +2 semitones via sample rate manipulation
    #    2 semitones = factor of 2^(2/12) ≈ 1.12246
    pitch_factor = round(2 ** (2 / 12), 6)
    af_parts.append(f"asetrate=44100*{pitch_factor}")

    # 3. Resample back to standard 44100 Hz so downstream stays compatible
    af_parts.append("aresample=44100")

    af = ",".join(af_parts)

    return vf, af


class VideoTransformerWindow(ctk.CTkToplevel):
    """
    Batch Video Transformer window.

    Applies a fixed set of FFmpeg transformations to remove copyright
    fingerprints and create unique visual versions of videos.
    """

    def __init__(self, master=None, lang: str = "en"):
        super().__init__(master)
        self._lang = lang
        self.title("🎬 Video Transformer — Remove Copyright Fingerprint")
        self.geometry("700x620")
        self.minsize(660, 580)
        self.configure(fg_color=COLORS["bg_dark"])
        if master:
            self.transient(master)
        self.grab_set()

        # ── State variables ────────────────────────────────────────
        self.input_folder = StringVar()
        self.output_folder = StringVar()
        self._is_processing = False
        self._cancel_event = threading.Event()
        self._ffmpeg = _find_ffmpeg()

        self._build_ui()

    # ═══════════════════════════════════════════════════════════════
    # UI CONSTRUCTION
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(14, 4))

        ctk.CTkLabel(
            hdr,
            text="🎬 Video Transformer",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["neon_blue"],
        ).pack(side="left")

        ctk.CTkButton(
            hdr, text="✕", width=32, height=32,
            fg_color="transparent", hover_color=COLORS["accent_red"],
            font=ctk.CTkFont(size=16), corner_radius=16,
            command=self._on_close,
        ).pack(side="right")

        # Subtitle
        ctk.CTkLabel(
            self,
            text="Remove Copyright Fingerprints — Batch Process Videos",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=24, pady=(0, 10))

        # ── Transformations info card ─────────────────────────────
        info_card = ctk.CTkFrame(
            self, fg_color=COLORS["bg_card_glass"],
            corner_radius=14, border_width=1, border_color=COLORS["border_glass"]
        )
        info_card.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            info_card,
            text="✅  Transformations Applied Automatically:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["neon_cyan"],
        ).pack(anchor="w", padx=16, pady=(12, 4))

        transforms = [
            ("↔️", "Horizontal Flip (hflip)"),
            ("🔲", "Auto-Crop & Zoom  (scale 110% → center crop)"),
            ("⚡", "Speed ×1.05  (setpts + atempo, pitch stable during speed change)"),
            ("🎵", "Audio Pitch +2 semitones  (asetrate + aresample, applied after speed)"),
            ("🎨", "Color Correction  (brightness +5%, contrast +10%, saturation +10%)"),
            ("🗑️", "Metadata Removal  (strip all EXIF / original metadata)"),
        ]
        grid = ctk.CTkFrame(info_card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 12))
        for i, (icon, desc) in enumerate(transforms):
            row_frame = ctk.CTkFrame(grid, fg_color="transparent")
            row_frame.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 20), pady=2)
            ctk.CTkLabel(
                row_frame, text=icon,
                font=ctk.CTkFont(size=14), width=22,
            ).pack(side="left")
            ctk.CTkLabel(
                row_frame, text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS["text_secondary"],
            ).pack(side="left", padx=(4, 0))

        # ── Folder Selection ──────────────────────────────────────
        folder_card = ctk.CTkFrame(
            self, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1, border_color=COLORS["border"]
        )
        folder_card.pack(fill="x", padx=20, pady=(0, 10))

        # Input folder row
        in_row = ctk.CTkFrame(folder_card, fg_color="transparent")
        in_row.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(
            in_row, text="📁 Input Folder:", width=110, anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")
        ctk.CTkEntry(
            in_row, textvariable=self.input_folder, state="readonly",
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            corner_radius=10, height=36, text_color=COLORS["text_primary"],
        ).pack(side="left", fill="x", expand=True, padx=8)
        ctk.CTkButton(
            in_row, text="Browse", width=80, height=36,
            fg_color=COLORS["neon_blue"], hover_color="#2563eb",
            corner_radius=10, command=self._browse_input,
        ).pack(side="right")

        # Output folder row
        out_row = ctk.CTkFrame(folder_card, fg_color="transparent")
        out_row.pack(fill="x", padx=16, pady=(0, 14))
        ctk.CTkLabel(
            out_row, text="📂 Output Folder:", width=110, anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")
        ctk.CTkEntry(
            out_row, textvariable=self.output_folder, state="readonly",
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            corner_radius=10, height=36, text_color=COLORS["text_primary"],
        ).pack(side="left", fill="x", expand=True, padx=8)
        ctk.CTkButton(
            out_row, text="Browse", width=80, height=36,
            fg_color=COLORS["neon_orange"], hover_color="#ea580c",
            corner_radius=10, command=self._browse_output,
        ).pack(side="right")

        # ── Progress area ─────────────────────────────────────────
        prog_card = ctk.CTkFrame(
            self, fg_color=COLORS["bg_card"],
            corner_radius=14, border_width=1, border_color=COLORS["border"]
        )
        prog_card.pack(fill="x", padx=20, pady=(0, 10))

        self._status_label = ctk.CTkLabel(
            prog_card,
            text="Ready — select folders and press Start",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_muted"],
        )
        self._status_label.pack(anchor="w", padx=16, pady=(12, 6))

        self._progress_bar = ctk.CTkProgressBar(
            prog_card, mode="determinate",
            fg_color=COLORS["progress_bg"], progress_color=COLORS["progress_fill"],
            corner_radius=6, height=14,
        )
        self._progress_bar.set(0)
        self._progress_bar.pack(fill="x", padx=16, pady=(0, 6))

        self._eta_label = ctk.CTkLabel(
            prog_card,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"],
        )
        self._eta_label.pack(anchor="e", padx=16, pady=(0, 12))

        # ── Log box ───────────────────────────────────────────────
        self._log_box = ctk.CTkTextbox(
            self,
            fg_color=COLORS["bg_card_inner"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=COLORS["text_secondary"],
            state="disabled",
            height=110,
        )
        self._log_box.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # ── Action buttons ────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        self._start_btn = ctk.CTkButton(
            btn_row,
            text="▶  Start Batch Transform",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=COLORS["neon_green"], hover_color="#16a34a",
            text_color="#0a0e17",
            corner_radius=12, height=48,
            command=self._start_processing,
        )
        self._start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._cancel_btn = ctk.CTkButton(
            btn_row,
            text="✕  Cancel",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=COLORS["gray_btn"], hover_color=COLORS["accent_red"],
            corner_radius=12, height=48, state="disabled",
            command=self._cancel_processing,
        )
        self._cancel_btn.pack(side="left", width=130)

    # ═══════════════════════════════════════════════════════════════
    # FOLDER BROWSE
    # ═══════════════════════════════════════════════════════════════

    def _browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder with Videos")
        if folder:
            self.input_folder.set(folder)
            # Auto-set output folder if not set yet
            if not self.output_folder.get():
                self.output_folder.set(os.path.join(folder, "transformed"))

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder for Transformed Videos")
        if folder:
            self.output_folder.set(folder)

    # ═══════════════════════════════════════════════════════════════
    # PROCESSING
    # ═══════════════════════════════════════════════════════════════

    def _start_processing(self):
        if self._is_processing:
            return

        in_dir = self.input_folder.get().strip()
        out_dir = self.output_folder.get().strip()

        if not in_dir or not os.path.isdir(in_dir):
            self._log("❌ Please select a valid input folder.", error=True)
            return
        if not out_dir:
            self._log("❌ Please select an output folder.", error=True)
            return

        # Collect video files
        video_files = [
            f for f in sorted(os.listdir(in_dir))
            if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS
        ]
        if not video_files:
            self._log("⚠️  No supported video files found in the input folder.", error=True)
            return

        os.makedirs(out_dir, exist_ok=True)

        self._is_processing = True
        self._cancel_event.clear()
        self._start_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._progress_bar.set(0)
        self._clear_log()

        thread = threading.Thread(
            target=self._process_batch,
            args=(in_dir, out_dir, video_files),
            daemon=True,
        )
        thread.start()

    def _process_batch(self, in_dir: str, out_dir: str, video_files: list[str]):
        total = len(video_files)
        start_time = time.time()
        succeeded = 0
        failed = 0

        self._log(f"🚀 Starting batch transform — {total} file(s)")
        self._log(f"   Input:  {in_dir}")
        self._log(f"   Output: {out_dir}")
        self._log("─" * 60)

        for idx, filename in enumerate(video_files):
            if self._cancel_event.is_set():
                self._log("⚠️  Cancelled by user.")
                break

            in_path = os.path.join(in_dir, filename)
            base, ext = os.path.splitext(filename)
            out_filename = f"{base}_transformed{ext}"
            out_path = os.path.join(out_dir, out_filename)

            self._update_status(f"Processing {idx + 1}/{total}: {filename}")
            self._log(f"[{idx + 1}/{total}] {filename}")

            try:
                self._transform_video(in_path, out_path)
                succeeded += 1
                self._log(f"  ✅ Done → {out_filename}")
            except subprocess.CalledProcessError as exc:
                failed += 1
                self._log(f"  ❌ FFmpeg error (code {exc.returncode}): {filename}", error=True)
            except Exception as exc:
                failed += 1
                self._log(f"  ❌ Error: {exc}", error=True)

            # Update progress bar and ETA
            progress = (idx + 1) / total
            elapsed = time.time() - start_time
            if idx + 1 < total:
                eta_secs = (elapsed / (idx + 1)) * (total - idx - 1)
                eta_str = self._format_duration(eta_secs)
                self._update_eta(f"ETA: {eta_str}  |  {idx + 1}/{total} done")
            else:
                self._update_eta(f"All {total} file(s) processed")
            self._update_progress(progress)

        elapsed_total = time.time() - start_time
        self._log("─" * 60)
        self._log(
            f"✅ Completed in {self._format_duration(elapsed_total)}  "
            f"— {succeeded} succeeded, {failed} failed"
        )
        self._update_status(
            f"✅ Done — {succeeded}/{total} succeeded" if not self._cancel_event.is_set()
            else "⚠️  Cancelled"
        )
        self._finish_processing()

    def _transform_video(self, in_path: str, out_path: str):
        """
        Run FFmpeg to apply all transformations to a single video file.

        Transformations:
          Video: hflip → scale 110% → center crop → setpts (speed) → eq (color)
          Audio: atempo (speed) → asetrate (pitch) → aresample (normalize rate)
          Metadata: all metadata stripped via -map_metadata -1
        """
        vf, af = build_ffmpeg_filter(speed=1.05)

        cmd = [
            self._ffmpeg,
            "-y",                          # overwrite output without asking
            "-i", in_path,                 # input file
            "-vf", vf,                     # video filter chain
            "-af", af,                     # audio filter chain
            "-map_metadata", "-1",         # strip all metadata
            "-c:v", "libx264",             # re-encode video (required for filters)
            "-preset", "fast",             # encoding speed/quality trade-off
            "-crf", VIDEO_CRF,             # high quality (lower = better, 18 is near-lossless)
            "-c:a", "aac",                 # re-encode audio
            "-b:a", AUDIO_BITRATE,        # audio bitrate
            "-movflags", "+faststart",    # web-optimized MP4
            out_path,
        ]

        logger.debug("FFmpeg command: %s", " ".join(cmd))

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return result

    # ═══════════════════════════════════════════════════════════════
    # CANCEL / CLOSE
    # ═══════════════════════════════════════════════════════════════

    def _cancel_processing(self):
        if self._is_processing:
            self._cancel_event.set()
            self._log("⚠️  Cancelling… (current file will finish)")

    def _on_close(self):
        if self._is_processing:
            self._cancel_event.set()
        self.destroy()

    def _finish_processing(self):
        self._is_processing = False
        self.after(0, lambda: self._start_btn.configure(state="normal"))
        self.after(0, lambda: self._cancel_btn.configure(state="disabled"))

    # ═══════════════════════════════════════════════════════════════
    # UI HELPERS (thread-safe)
    # ═══════════════════════════════════════════════════════════════

    def _update_status(self, text: str):
        self.after(0, lambda: self._status_label.configure(text=text))

    def _update_progress(self, value: float):
        self.after(0, lambda: self._progress_bar.set(value))

    def _update_eta(self, text: str):
        self.after(0, lambda: self._eta_label.configure(text=text))

    def _log(self, message: str, error: bool = False):
        """Append a message to the log box (thread-safe)."""
        def _append():
            self._log_box.configure(state="normal")
            self._log_box.insert("end", message + "\n")
            self._log_box.see("end")
            self._log_box.configure(state="disabled")
        self.after(0, _append)

    def _clear_log(self):
        def _do_clear():
            self._log_box.configure(state="normal")
            self._log_box.delete("1.0", "end")
            self._log_box.configure(state="disabled")
        self.after(0, _do_clear)

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format seconds into mm:ss or hh:mm:ss string."""
        seconds = int(seconds)
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"


# ─── Standalone entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.withdraw()
    win = VideoTransformerWindow(master=root)
    win.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
