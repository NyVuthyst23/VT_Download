# PyInstaller build script

import os
import shutil
import logging

logging.basicConfig(filename='build.log', level=logging.INFO)

# Clean previous builds
shutil.rmtree('dist', ignore_errors=True)
shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('spec', ignore_errors=True)

# Tool downloads
os.system('curl -L -o yt-dlp.exe https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe')
os.system('curl -L -o ffmpeg.exe https://ffmpeg.org/releases/ffmpeg-release-full.7z')
os.system('curl -L -o ffprobe.exe https://ffmpeg.org/releases/ffmpeg-release-full.7z')

# PyInstaller command
os.system('pyinstaller --collect-all playwright_stealth --hidden-import logging build_exe.py')

logging.info('Build complete.')