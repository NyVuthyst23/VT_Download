@echo off
REM Build Installer Script for NSIS

REM Check if NSIS is installed
where makensis >nul 2>nul
if %errorlevel% neq 0 (
    echo NSIS not found. Please install NSIS to build the installer.
    exit /b 1
)

REM Set the output file name
set OUTPUT_FILE=Installer.exe

REM Build the installer
makensis.exe /DOUTPUT_FILE=%OUTPUT_FILE% "installer_script.nsi"
if %errorlevel% neq 0 (
    echo An error occurred during the build process.
    exit /b 1
)

echo Installer built successfully: %OUTPUT_FILE%