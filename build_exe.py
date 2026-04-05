# ====================================================================
# build_exe.py — Build script សម្រាប់ VT_Download
# របៀបប្រើ: python build_exe.py
# លទ្ធផល:  dist/VT_Download.exe  (file តែមួយ)
# ====================================================================

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import logging

# ──────────────────────────────────────────────
# ការកំណត់ឈ្មោះ app និង file ចំបង
# ──────────────────────────────────────────────
APP_NAME    = "VT_Download"           # ឈ្មោះ EXE ដែល output
ENTRY_SCRIPT = "video_downloader_pro.py"  # script ចំបង (entry point)

LOGO_PNG  = "logo.png"       # logo ដើម (PNG)
LOGO_ICO  = "logo.ico"       # logo សម្រាប់ icon EXE (ICO)
YTDLP_EXE   = "yt-dlp.exe"  # tool ដោនឡូត video
FFMPEG_EXE  = "ffmpeg.exe"   # tool encode/decode video
FFPROBE_EXE = "ffprobe.exe"  # tool ពិនិត្យ media info

# ──────────────────────────────────────────────
# Path folder សំខាន់ៗ
# ──────────────────────────────────────────────
ROOT      = os.path.dirname(os.path.abspath(__file__))  # folder គម្រោង
DIST      = os.path.join(ROOT, "dist")                  # folder output
BUILD     = os.path.join(ROOT, "build")                 # folder build ชั่วคราว
SPEC      = os.path.join(ROOT, f"{APP_NAME}.spec")      # file spec របស់ PyInstaller
BUILD_LOG = os.path.join(ROOT, "build.log")             # log file

# ──────────────────────────────────────────────
# ការ log សម្រាប់ terminal និង file
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),                          # print ទៅ terminal
        logging.FileHandler(BUILD_LOG, mode="w", encoding="utf-8"), # save ទៅ build.log
    ],
)
log = logging.getLogger("builder")


# ──────────────────────────────────────────────
# run(): run command ហើយ check error
# ──────────────────────────────────────────────
def run(cmd):
    log.info("RUN: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)


# ──────────────────────────────────────────────
# clean(): លុប folder build/dist/spec ចាស់
#          ដើម្បី build ថ្មីស្អាត
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# download(): download file ពី URL ទៅ disk
# ──────────────────────────────────────────────
def download(url, out):
    log.info("Download: %s -> %s", url, out)
    urllib.request.urlretrieve(url, out)


# ──────────────────────────────────────────────
# ensure_ytdlp(): download yt-dlp.exe ប្រសិនបើ
#                 មិនទាន់មាន
# ──────────────────────────────────────────────
def ensure_ytdlp():
    if os.path.exists(YTDLP_EXE):
        log.info("✓ %s exists", YTDLP_EXE)
        return
    download(
        "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        YTDLP_EXE,
    )


# ──────────────────────────────────────────────
# ensure_ffmpeg(): download ffmpeg + ffprobe
#                  ពី zip ហើយ extract
# ──────────────────────────────────────────────
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
        os.remove(zip_path)  # លុប zip ចោលបន្ទាប់ extract
    except Exception:
        pass

    if not os.path.exists(FFMPEG_EXE) or not os.path.exists(FFPROBE_EXE):
        raise RuntimeError("ffmpeg.exe/ffprobe.exe extraction failed.")


# ──────────────────────────────────────────────
# ensure_icon(): បំប្លែង logo.png → logo.ico
#                ត្រូវការ:  pip install pillow
# ──────────────────────────────────────────────
def ensure_icon():
    if os.path.exists(LOGO_ICO):
        return  # មានរួចហើយ មិនបំប្លែងម្តងទៀត
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


# ──────────────────────────────────────────────
# build(): function ចំបង — build EXE file
#
#   លទ្ធផល: dist/VT_Download.exe  (file តែមួយ)
#   ملاحظة: --onefile បញ្ចូល tool ទាំងអស់ក្នុង
#           EXE តែមួយ → ចែករំលែកបានងាយ
# ──────────────────────────────────────────────
def build():
    os.chdir(ROOT)

    if not os.path.exists(ENTRY_SCRIPT):
        raise FileNotFoundError(f"Missing {ENTRY_SCRIPT} in project folder.")

    clean()         # លុបចោល folder build ចាស់
    ensure_icon()   # បំប្លែង logo.png → logo.ico
    ensure_ytdlp()  # download yt-dlp.exe
    ensure_ffmpeg() # download ffmpeg.exe + ffprobe.exe

    # ── Collect playwright និង playwright_stealth ទាំងអស់
    #    (ចាំបាច់ ព្រោះ playwright_stealth/js/* ត្រូវ bundle ផង)
    collect_all = [
        "--collect-all", "playwright_stealth",
        "--collect-all", "playwright",
    ]

    # ── Hidden imports ដែល PyInstaller រកមិនឃើញដោយស្វ័យប្រវត្តិ
    hidden = [
        "--hidden-import", "playwright.sync_api",
        "--hidden-import", "playwright_stealth",
        "--hidden-import", "playwright_stealth.stealth",
        "--hidden-import", "playwright_stealth.stealth_sync",
    ]

    # ── Data files បញ្ចូលក្នុង EXE (logo + tools)
    add_data = []
    if os.path.exists(LOGO_PNG):
        add_data += ["--add-data", f"{LOGO_PNG};."]
    if os.path.exists(LOGO_ICO):
        add_data += ["--add-data", f"{LOGO_ICO};."]

    for tool in (YTDLP_EXE, FFMPEG_EXE, FFPROBE_EXE):
        if os.path.exists(tool):
            add_data += ["--add-data", f"{tool};."]

    # ── PyInstaller command
    #    --onefile  = output ជា EXE file តែមួយ (ឃើញ file តិច)
    #    --windowed = មិនបង្ហាញ console/terminal window
    #    --noconfirm = overwrite dist ដោយមិន confirm
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",   # ← file តែមួយ (ងាយចែករំលែក)
        "--windowed",
        "--name", APP_NAME,
    ]

    if os.path.exists(LOGO_ICO):
        cmd += ["--icon", LOGO_ICO]  # ដាក់ icon ឱ្យ EXE

    cmd += add_data + hidden + collect_all + [ENTRY_SCRIPT]
    run(cmd)

    # ── Build រួចរាល់ — output path
    out_exe = os.path.join(DIST, f"{APP_NAME}.exe")
    log.info("DONE. Output: %s", out_exe)
    log.info("Log: %s", BUILD_LOG)


if __name__ == "__main__":
    build()