@echo off
chcp 65001 >nul
title AI Money Machine — 全自动流水线
cd /d D:\AI-Money-Machine

:menu
cls
echo ============================================
echo    🤖 AI Money Machine 全自动搬砖流水线
echo    v4.0 | 2026-06-18
echo ============================================
echo.
echo   [1] 📅 显示每周计划
echo   [2] 🚀 运行今日任务
echo   [3] 🔄 运行全周任务(立即执行)
echo   [4] 📊 生成周报
echo   [5] ⏰ 启动Cron长期模式(持续运行)
echo   [6] 📈 生成数据分析报告
echo   [7] 📝 生成新Medium文章
echo   [8] 📣 生成社媒推广内容
echo   [0] 退出
echo.
echo ============================================
set /p choice="请选择 [0-8]: "

if "%choice%"=="1" goto plan
if "%choice%"=="2" goto today
if "%choice%"=="3" goto fullweek
if "%choice%"=="4" goto weeklyreport
if "%choice%"=="5" goto cron
if "%choice%"=="6" goto analytics
if "%choice%"=="7" goto medium
if "%choice%"=="8" goto social
if "%choice%"=="0" goto end
goto menu

:plan
echo.
python scheduler/daily-pipeline/weekly_loop.py --mode plan
pause
goto menu

:today
echo.
python scheduler/daily-pipeline/weekly_loop.py --mode once
pause
goto menu

:fullweek
echo.
python scheduler/daily-pipeline/weekly_loop.py --mode full
pause
goto menu

:weeklyreport
echo.
python scheduler/daily-pipeline/weekly_loop.py --mode report
pause
goto menu

:cron
echo.
echo ⏰ 启动Cron长期运行 (Ctrl+C 停止)
echo 每30分钟检查一次任务计划
echo.
python scheduler/daily-pipeline/weekly_loop.py --mode cron
pause
goto menu

:analytics
echo.
python analytics/dashboard/reports/generate_report.py
pause
goto menu

:medium
echo.
python marketing/seo-blogs/seo_blogs.py
pause
goto menu

:social
echo.
python scheduler/task-queue/social_auto_publisher.py
pause
goto menu

:end
echo 再见!
exit
