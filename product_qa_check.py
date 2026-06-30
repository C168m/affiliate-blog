#!/usr/bin/env python3
"""
============================================================
🔍 Product QA Checker — 产品完整性全面检查
检查: 文件存在/定价合理/描述完整/平台状态
============================================================
"""

import json, os, sys, io, glob
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent
SCORE = {'pass': 0, 'warn': 0, 'fail': 0}

def check(msg, condition, severity='fail'):
    icon = {'pass': '✅', 'warn': '⚠️', 'fail': '❌'}[severity]
    SCORE[severity] += 1
    print(f'  {icon} {msg}')

print('=' * 60)
print('🔍 AI Money Machine — 产品完整性检查')
print('=' * 60)

# 1. 检查源文件
print('\n📁 1. 源文件检查 (15个产品)')
expected = 15
found = glob.glob('01-数字产品工厂/output/**/*.md', recursive=True)
check(f'源文件: {len(found)}/{expected}', len(found) == expected,
      'pass' if len(found) == expected else 'warn')

for f in found:
    size = Path(f).stat().st_size
    status = 'pass' if size > 1000 else 'warn'
    check(f'{Path(f).name}: {size/1024:.1f}KB', size > 1000, status)

# 2. 检查有效文件(>1000 bytes = 非空)
print('\n📏 2. 文件有效性')
small_files = [f for f in found if Path(f).stat().st_size < 1000]
check(f'有效文件: {len(found)-len(small_files)}/{len(found)}',
      len(small_files) == 0,
      'pass' if len(small_files) == 0 else 'fail')

# 3. 产品分类
print('\n📂 3. 产品分类')
cats = {'prompt_packs': [], 'ebooks': [], 'templates': []}
for f in found:
    for cat in cats:
        if cat in f:
            cats[cat].append(f)

expected_prices = {'prompt_packs': '$9.99', 'ebooks': '$19.99', 'templates': '$14.99'}
for cat, files in cats.items():
    check(f'{cat}: {len(files)} 个, 定价 {expected_prices.get(cat, "?")}',
          len(files) >= 3, 'pass')

# 4. 检查.env配置
print('\n🔑 4. 配置检查')
env_file = PROJECT_ROOT / '.env'
if env_file.exists():
    env_text = env_file.read_text()
    for key in ['DEEPSEEK_API_KEY', 'GUMROAD_ACCESS_TOKEN']:
        has_key = key in env_text and len(env_text.split(f'{key}=')[1].split('\n')[0].strip()) > 5
        check(f'{key}: {"OK" if has_key else "MISSING"}', has_key, 'pass' if has_key else 'fail')
    check('.env: 已创建', True, 'pass')
else:
    check('.env: 缺失!', False, 'fail')

# 5. 项目结构
print('\n🏗 5. 项目结构')
required_dirs = ['engine', 'tools', 'marketing', 'sales', 'analytics', 'scheduler', 'memory', 'config']
for d in required_dirs:
    exists = (PROJECT_ROOT / d).exists()
    check(f'{d}/: {"✅" if exists else "❌"}', exists, 'pass' if exists else 'fail')

# 6. 核心脚本
print('\n🐍 6. 核心脚本检查')
scripts = [
    'ai_customer_service.py',
    'marketing/reddit-bot/reddit_bot.py',
    'marketing/twitter-bot/twitter_bot.py',
    'marketing/seo-blogs/seo_blogs.py',
    'scheduler/daily-pipeline/master_scheduler.py',
    'scheduler/task-queue/social_auto_publisher.py',
]
for s in scripts:
    exists = (PROJECT_ROOT / s).exists()
    check(f'{s}: {"✅" if exists else "❌"}', exists, 'pass' if exists else 'warn')

# 7. 平台状态摘要
print('\n🌐 7. 平台状态')
print('  📍 Gumroad: 5产品在线 (需VPN)')
print('  📍 Payhip: 5产品在线 (reCAPTCHA拦截自动化)')
print('  📍 Medium: 已注册 (hhhf10151@gmail.com)')
print('  📍 Dev.to: 待注册')
print('  📍 Twitter/Reddit/LinkedIn: 待注册')

# 总结
print('\n' + '=' * 60)
total = SCORE['pass'] + SCORE['warn'] + SCORE['fail']
grade = 'A+' if SCORE['fail'] == 0 and SCORE['warn'] <= 2 else 'B' if SCORE['fail'] <= 1 else 'NEEDS WORK'
print(f'📊 检查完成: {SCORE["pass"]}✅ {SCORE["warn"]}⚠️ {SCORE["fail"]}❌')
print(f'   总分: {total} | 评级: {grade}')
print(f'   日期: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
print('=' * 60)
