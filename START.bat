@echo off
chcp 65001 >nul
title AI Money Machine v2.0
cd /d D:\AI-Money-Machine

:menu
cls
echo ==============================================
echo     💰 AI Money Machine v2.0
echo     零实名·全自动·全球变现
echo ==============================================
echo.
echo   [1] 🚀 运行完整流水线
echo   [2] 📦 仅生产数字产品
echo   [3] 🎬 YouTube视频生产
echo   [4] 📝 SEO文章生产
echo   [5] 📣 社交媒体推广
echo   [6] 📊 查看收益报告
echo   [7] ⏰ 启动全自动调度
echo   [8] 📈 启动数据看板
echo   [9] 🔧 环境安装
echo   [S] 📋 平台注册指南
echo   [0] 退出
echo.
echo ==============================================

set /p choice="请输入选项: "

if "%choice%"=="1" goto full
if "%choice%"=="2" goto product
if "%choice%"=="3" goto youtube
if "%choice%"=="4" goto seo
if "%choice%"=="5" goto social
if "%choice%"=="6" goto report
if "%choice%"=="7" goto scheduler
if "%choice%"=="8" goto dashboard
if "%choice%"=="9" goto setup
if /i "%choice%"=="S" goto guide
if "%choice%"=="0" goto end
goto menu

:full
python "00-总控中心\main_pipeline.py" --mode full
pause && goto menu

:product
set /p count="生产数量 (默认10): "
if "%count%"=="" set count=10
python "00-总控中心\main_pipeline.py" --mode product --count %count%
pause && goto menu

:youtube
set /p topic="视频主题 (默认AI Writing Tools): "
if "%topic%"=="" set topic=AI Writing Tools
python "00-总控中心\main_pipeline.py" --mode youtube --niche "%topic%"
pause && goto menu

:seo
python "00-总控中心\main_pipeline.py" --mode seo --count 5
pause && goto menu

:social
python "00-总控中心\main_pipeline.py" --mode social
pause && goto menu

:report
python "07-收益追踪\revenue_tracker.py" --action summary
pause && goto menu

:scheduler
echo ⏰ 启动全自动调度引擎 (Ctrl+C 停止)...
python "08-全自动调度\scheduler.py" --mode loop --interval 300
pause && goto menu

:dashboard
echo 📈 启动数据看板: http://localhost:8501
streamlit run "07-收益追踪\可视化看板\dashboard.py"
pause && goto menu

:setup
python "09-运维部署\setup.py"
pause && goto menu

:guide
python "02-销售平台自动化\sales_automation.py" --action setup
pause && goto menu

:end
echo 再见!
exit
