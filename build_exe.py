import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import logging

APP_NAME = "VT_Download"
ENTRY_SCRIPT = "video_downloader_pro.py"

LOGO_PNG = "logo.png"
LOGO_ICO = "logo.ico"
YTDLP_EXE = "yt-dlp.exe"
FFMPEG_EXE = "ffmpeg.exe"
FFPROBE_EXE = "ffprobe.exe"

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
BUILD = os.path.join(ROOT, "build")
SPEC = os.path.join(ROOT, f"{APP_NAME}.spec")
BUILD_LOG = os.path.join(ROOT, "build.log")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BUILD_LOG, mode="w", encoding="utf-8"),
    ],
)
log = logging.getLogger("builder")

def run(cmd):
    log.info("RUN: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)

def clean():
    for p in (DIST, BUILD):
        if os.path.isdir(p):
            log.info("Remove folder: %s", p)
            shutil.rmtree(p, ignore_errors=True)
    if os.path.exists(SPEC):
        log.info("Remove file: %s", SPEC)
        try:
            os.remove(SPEC)
        except Exception:
            pass

def download(url, out):
    log.info("Download: %s -> %s", url, out)
    urllib.request.urlretrieve(url, out)

def ensure_ytdlp():
    if os.path.exists(YTDLP_EXE):
        log.info("✓ %s exists", YTDLP_EXE)
        return
    download(
        "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        YTDLP_EXE,
    )

def ensure_ffmpeg():
    if os.path.exists(FFMPEG_EXE) and os.path.exists(FFPROBE_EXE):
        log.info("✓ %s and %s exist", FFMPEG_EXE, FFPROBE_EXE)
        return

    url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = os.path.join(ROOT, "_ffmpeg_temp.zip")
    download(url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            base = os.path.basename(member)
            if base in (FFMPEG_EXE, FFPROBE_EXE):
                with zf.open(member) as src, open(os.path.join(ROOT, base), "wb") as dst:
                    shutil.copyfileobj(src, dst)
                log.info("Extracted: %s", base)

    try:
        os.remove(zip_path)
    except Exception:
        pass

    if not os.path.exists(FFMPEG_EXE) or not os.path.exists(FFPROBE_EXE):
        raise RuntimeError("ffmpeg.exe/ffprobe.exe extraction failed.")

def ensure_icon():
    if os.path.exists(LOGO_ICO):
        return
    if not os.path.exists(LOGO_PNG):
        log.warning("logo.png not found -> skipping ico generation.")
        return
    try:
        from PIL import Image
        img = Image.open(LOGO_PNG)
        img.save(LOGO_ICO, format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
        log.info("Created %s", LOGO_ICO)
    except Exception as e:
        log.warning("Could not create logo.ico (install pillow): %s", e)

def build():
    os.chdir(ROOT)

    if not os.path.exists(ENTRY_SCRIPT):
        raise FileNotFoundError(f"Missing {ENTRY_SCRIPT} in project folder.")

    clean()
    ensure_icon()
    ensure_ytdlp()
    ensure_ffmpeg()

    # IMPORTANT: fixes missing playwright_stealth/js/* at runtime
    collect_all = [
        "--collect-all", "playwright_stealth",
        "--collect-all", "playwright",
    ]

    hidden = [
        "--hidden-import", "playwright.sync_api",
        "--hidden-import", "playwright_stealth",
        "--hidden-import", "playwright_stealth.stealth",
        "--hidden-import", "playwright_stealth.stealth_sync",
    ]

    add_data = []
    if os.path.exists(LOGO_PNG):
        add_data += ["--add-data", f"{LOGO_PNG};."]
    if os.path.exists(LOGO_ICO):
        add_data += ["--add-data", f"{LOGO_ICO};."]

    for tool in (YTDLP_EXE, FFMPEG_EXE, FFPROBE_EXE):
        if os.path.exists(tool):
            add_data += ["--add-data", f"{tool};."]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", APP_NAME,
    ]

    if os.path.exists(LOGO_ICO):
        cmd += ["--icon", LOGO_ICO]

    cmd += add_data + hidden + collect_all + [ENTRY_SCRIPT]
    run(cmd)

    # Copy tools next to exe for reliability
    out_dir = os.path.join(DIST, APP_NAME)
    for tool in (YTDLP_EXE, FFMPEG_EXE, FFPROBE_EXE):
        src = os.path.join(ROOT, tool)
        dst = os.path.join(out_dir, tool)
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                log.info("Copied: %s -> %s", tool, dst)
            except Exception as e:
                log.warning("Copy failed %s: %s", tool, e)

    log.info("DONE. Output: %s", os.path.join(out_dir, f"{APP_NAME}.exe"))
    log.info("Log: %s", BUILD_LOG)


if __name__ == "__main__":
    build()