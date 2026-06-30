#!/usr/bin/env python3
"""
============================================================
📌 Pinterest Auto-Pinner — 产品视觉推广自动Pin
为所有Gumroad产品自动生成Pin图片描述,排期发布
============================================================
"""

import json, sys, io, random, time
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'scheduler' / 'task-queue' / 'pinterest_pins'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Config
env = {}
for line in (PROJECT_ROOT / '.env').read_text(encoding='utf-8').split('\n'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

client = OpenAI(api_key=env.get('DEEPSEEK_API_KEY', ''), base_url='https://api.deepseek.com')

# Product data
PRODUCTS = [
    {'name': 'YouTube Automation Prompt Pack', 'url': 'https://howler06371.gumroad.com/l/pesoed', 'price': '$9.99', 'keywords': 'youtube,automation,ai prompts,content creation'},
    {'name': 'Graphic Design AI Notion Template', 'url': 'https://howler06371.gumroad.com/l/mvonqg', 'price': '$14.99', 'keywords': 'graphic design,notion template,ai design'},
    {'name': 'AI Coding & Development Guide', 'url': 'https://howler06371.gumroad.com/l/fuowsw', 'price': '$19.98', 'keywords': 'coding,ai development,programming guide'},
    {'name': 'Productivity Notion Templates Pack', 'url': 'https://howler06371.gumroad.com/l/zmyrkl', 'price': '$9.99', 'keywords': 'productivity,notion template,organization'},
    {'name': 'SEO Optimization with AI Guide', 'url': 'https://howler06371.gumroad.com/l/qubudd', 'price': '$19.99', 'keywords': 'seo,ai marketing,search optimization'},
    {'name': 'E-commerce AI Tools Guide', 'url': 'https://howler06371.gumroad.com/l/scooum', 'price': '$19.99', 'keywords': 'ecommerce,ai tools,online business'},
    {'name': 'AI for Real Estate Guide', 'url': 'https://howler06371.gumroad.com/l/cjemk', 'price': '$19.99', 'keywords': 'real estate,ai,property'},
    {'name': 'Personal Finance Notion Template', 'url': 'https://howler06371.gumroad.com/l/jdqsye', 'price': '$14.99', 'keywords': 'personal finance,budget,notion'},
    {'name': 'Customer Service AI Prompts', 'url': 'https://howler06371.gumroad.com/l/ewqobu', 'price': '$9.99', 'keywords': 'customer service,ai prompts,support'},
    {'name': 'Small Business AI Notion Template', 'url': 'https://howler06371.gumroad.com/l/xhxtrr', 'price': '$14.99', 'keywords': 'small business,ai,notion template'},
]

BOARDS = [
    'AI Tools & Resources',
    'Digital Products & Templates',
    'Productivity & Workflow',
    'Side Hustle Ideas',
]

def generate_pin(product, board):
    """为产品生成一个Pinterest Pin描述"""
    prompt = f"""Create a Pinterest pin description for this digital product:

Product: {product['name']}
Price: {product['price']}
Link: {product['url']}
Pinterest Board: {board}

Requirements:
- Title: Catchy, 40-60 chars, with emoji
- Description: 150-200 chars, keyword-rich
- Include 3-5 relevant hashtags
- Make people want to click and save

Format:
TITLE: [title]
DESC: [description]
TAGS: [#tag1 #tag2 #tag3]
"""

    try:
        resp = client.chat.completions.create(
            model='deepseek-chat',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=250, temperature=0.9
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"TITLE: {product['name']} 📌\nDESC: Premium {product['name']} - {product['price']}. Check it out!\nTAGS: #digitalproducts"

def generate_schedule():
    """生成30天Pin排期(每天3个Pin)"""
    pins = []
    start_date = datetime.now() + timedelta(days=1)

    for day in range(30):
        date = start_date + timedelta(days=day)
        # 每天3个Pin,不同时间
        for slot, hour in enumerate([9, 14, 20], 1):
            product = PRODUCTS[(day * 3 + slot) % len(PRODUCTS)]
            board = BOARDS[(day + slot) % len(BOARDS)]

            pin_content = generate_pin(product, board)

            pins.append({
                'date': date.strftime('%Y-%m-%d'),
                'time': f'{hour:02d}:00',
                'product': product['name'],
                'url': product['url'],
                'board': board,
                'content': pin_content,
                'status': 'scheduled'
            })

    return pins

def main():
    print('=' * 60)
    print('📌 Pinterest Auto-Pinner — 30天排期生成')
    print('=' * 60)

    print(f'\n🛒 Products: {len(PRODUCTS)}')
    print(f'📋 Boards: {len(BOARDS)}')

    pins = generate_schedule()

    # 保存
    output_file = DATA_DIR / f'pinterest_schedule_{datetime.now().strftime("%Y%m%d")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pins, f, ensure_ascii=False, indent=2)

    print(f'\n✅ 已生成 {len(pins)} 个Pin排期')
    print(f'📁 保存: {output_file}')

    # 统计
    per_day = {}
    for p in pins:
        d = p['date']
        per_day[d] = per_day.get(d, 0) + 1

    print(f'\n📊 统计:')
    print(f'   总Pin数: {len(pins)}')
    print(f'   天数: {len(per_day)}')
    print(f'   日均Pin: {len(pins)//len(per_day)}')
    print(f'   覆盖产品: {len(PRODUCTS)}')

    # 展示前3个Pin
    print(f'\n📌 示例Pin (前3个):')
    for p in pins[:3]:
        print(f'   [{p["date"]} {p["time"]}] {p["board"]}')
        print(f'   {p["content"][:100]}...')
        print()

    print(f'\n💡 Pinterest操作指南:')
    print(f'   1. 注册 pinterest.com (任意邮箱)')
    print(f'   2. 创建4个Board: {", ".join(BOARDS)}')
    print(f'   3. 每天手动Pin 3-5个(或API自动)')
    print(f'   4. 每个Pin用上方生成的内容')
    print(f'   5. 链接指向Gumroad产品页面')

if __name__ == '__main__':
    main()
