@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title AI Money Machine - Blog Affiliate System
echo.
echo ================================================
echo   AI Money Machine v2.0
echo   Blog Affiliate Automation (GitHub Pages)
echo ================================================
echo   1. Full Pipeline (Server + Audit + Social)
echo   2. Generate New Article
echo   3. SEO Audit Only
echo   4. Deploy to GitHub Pages
echo   5. Setup Wizard (First Time)
echo   6. Set Amazon Tracking ID
echo   7. Blog Server Only (localhost:8080)
echo ================================================
echo.
set /p mode="Select [1-7]: "

if "%mode%"=="1" (
    python launch.py
    pause
    exit /b
)
if "%mode%"=="2" (
    set /p product="Product name (e.g. wireless keyboard): "
    python launch.py --generate "%product%"
    pause
    exit /b
)
if "%mode%"=="3" (
    python launch.py --audit
    pause
    exit /b
)
if "%mode%"=="4" (
    python launch.py --deploy
    pause
    exit /b
)
if "%mode%"=="5" (
    python launch.py --setup
    pause
    exit /b
)
if "%mode%"=="6" (
    set /p tid="Amazon Tracking ID: "
    python launch.py --set-id %tid%
    pause
    exit /b
)
if "%mode%"=="7" (
    python launch.py --server
    exit /b
)
echo Invalid option.
pause
exit /b
