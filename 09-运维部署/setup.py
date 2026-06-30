#!/usr/bin/env python3
"""
============================================================
🔧 AI Money Machine 一键环境安装
============================================================
"""

import subprocess, sys, os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def run(cmd: str, desc: str = "") -> bool:
    print(f"  ⏳ {desc}...")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
        ok = r.returncode == 0
        print(f"  {'✅' if ok else '⚠️'} {desc} {'- 成功' if ok else '- 警告'}")
        return ok
    except Exception as e:
        print(f"  ❌ {desc} - 失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🔧 AI Money Machine 一键环境安装")
    print("=" * 50)

    # 1. pip升级
    run(f"{sys.executable} -m pip install --upgrade pip", "pip升级")

    # 2. 核心依赖
    print("\n📦 Python核心依赖...")
    pkgs = [
        "requests", "playwright", "beautifulsoup4",
        "schedule", "pandas", "plotly", "openai",
        "moviepy", "edge-tts", "python-dotenv", "rich",
        "streamlit", "tweepy", "praw"
    ]
    for pkg in pkgs:
        run(f"{sys.executable} -m pip install {pkg} --quiet", pkg)

    # 3. Playwright浏览器
    print("\n🌐 Playwright Chromium...")
    run("playwright install chromium", "Chromium")

    # 4. FFmpeg检查
    print("\n🎬 FFmpeg检查...")
    r = subprocess.run("ffmpeg -version", shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print("  ⚠️ FFmpeg未安装: https://ffmpeg.org/download.html")

    # 5. 创建必要目录
    print("\n📁 创建目录...")
    for d in ["logs", "output", "data", "auth", "temp"]:
        (PROJECT_ROOT / d).mkdir(exist_ok=True)

    # 6. .env模板
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        env_file.write_text("""# AI Money Machine 环境配置
DEEPSEEK_API_KEY=sk-your-key-here
GUMROAD_TOKEN=
PAYHIP_API_KEY=
LEMONSQUEEZY_API_KEY=
""", encoding="utf-8")

    print("\n" + "=" * 50)
    print("🎉 安装完成!")
    print("=" * 50)
    print("""
下一步:
  1. 编辑 .env 填入API Key
  2. 注册 DeepSeek: platform.deepseek.com
  3. 注册 Gumroad: gumroad.com/signup
  4. 运行: python 00-总控中心/main_pipeline.py --mode full
    """)

if __name__ == "__main__":
    main()
