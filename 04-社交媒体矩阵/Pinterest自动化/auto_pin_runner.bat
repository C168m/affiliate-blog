@echo off
chcp 65001 >nul
REM Pinterest Auto-Pin Runner - Every 2 days via Task Scheduler
cd /d "D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化"

echo ===== %date% %time% ===== >> auto_pin.log

REM Phase 1: Scrape articles + generate Pin images (no VPN needed, no browser needed)
echo [SCRAPE] Checking for new articles... >> auto_pin.log
python pinterest_auto.py --mode scrape >> auto_pin.log 2>&1

REM Phase 2: Publish via Edge CDP (dedicated profile, doesn't kill your regular Edge)
if exist publish_queue.json (
    echo [PUBLISH] Queue found, publishing via Edge CDP... >> auto_pin.log
    python pinterest_browser.py --mode publish >> auto_pin.log 2>&1
) else (
    echo [SKIP] No new pins to publish >> auto_pin.log
)

echo [DONE] %date% %time% >> auto_pin.log
echo. >> auto_pin.log
