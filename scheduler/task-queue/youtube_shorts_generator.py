#!/usr/bin/env python3
"""
============================================================
🎬 YouTube Shorts Auto-Generator
从产品内容自动生成YouTube Shorts脚本+素材描述
============================================================
"""

import json, sys, io, os, glob, random
from datetime import datetime
from pathlib import Path
from openai import OpenAI

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'scheduler' / 'task-queue' / 'youtube_shorts'
DATA_DIR.mkdir(parents=True, exist_ok=True)

env = {}
for line in (PROJECT_ROOT / '.env').read_text(encoding='utf-8').split('\n'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip()

client = OpenAI(api_key=env.get('DEEPSEEK_API_KEY', ''), base_url='https://api.deepseek.com')

# Find product files to use as source material
PRODUCT_DIR = PROJECT_ROOT / '01-数字产品工厂' / 'output'
content_files = glob.glob(str(PRODUCT_DIR / '**' / '*.md'), recursive=True)

print(f'Found {len(content_files)} product files for Shorts content')

SHORTS_TEMPLATES = [
    {
        'style': 'top5',
        'title': 'Top 5 AI Prompts That Will Blow Your Mind 🤯',
        'duration': 45,
        'hook': 'Stop wasting hours on {topic}. Here are 5 AI prompts that do the work for you.',
    },
    {
        'style': 'before_after',
        'title': 'How AI Changed My Workflow in 60 Seconds ⚡',
        'duration': 55,
        'hook': 'Before AI: 3 hours. After AI: 3 minutes. Here\'s how.',
    },
    {
        'style': 'quick_tip',
        'title': 'One AI Trick That Saves Me 10 Hours/Week ⌛',
        'duration': 30,
        'hook': 'Most people don\'t know about this AI feature. It saves me 10 hours every week.',
    },
    {
        'style': 'tutorial',
        'title': 'How to Use {topic} — Complete Beginner Guide 🎓',
        'duration': 58,
        'hook': 'Never used {topic} before? Watch this 60-second crash course.',
    },
    {
        'style': 'comparison',
        'title': 'Free vs Paid AI Tools — Which Actually Works? 💰',
        'duration': 50,
        'hook': 'You don\'t need to pay for expensive AI tools. Here\'s what actually works.',
    },
]

def generate_shorts(category, source_file):
    """从产品内容生成Shorts脚本"""
    # 读取源文件前500字
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()[:800]
    except:
        source_content = 'AI digital products and automation'

    template = random.choice(SHORTS_TEMPLATES)
    topic = Path(source_file).stem.replace('_', ' ')[:50]

    prompt = f"""Create a YouTube Shorts script based on this template:

STYLE: {template['style']}
DURATION: {template['duration']} seconds
HOOK: {template['hook'].format(topic=topic)}

Source content excerpt:
{source_content}

Requirements:
- Engaging hook in first 3 seconds
- Fast-paced, punchy language
- Each scene: timestamp, voiceover text, visual description
- End with: 'Follow for more AI tips' + Channel name hint
- Total 5-7 scenes

Output as JSON with fields: title, scenes (array of {{timeStart, timeEnd, voiceover, visual}}), tags"""

    try:
        resp = client.chat.completions.create(
            model='deepseek-chat',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=800, temperature=0.9
        )
        return resp.choices[0].message.content
    except Exception as e:
        return json.dumps({'error': str(e)})

def main():
    print('=' * 60)
    print('🎬 YouTube Shorts Generator')
    print('=' * 60)

    # Product URL mapping
    product_links = {
        'prompt': 'https://howler06371.gumroad.com/l/pesoed',
        'coding': 'https://howler06371.gumroad.com/l/fuowsw',
        'design': 'https://howler06371.gumroad.com/l/mvonqg',
        'productivity': 'https://howler06371.gumroad.com/l/zmyrkl',
        'seo': 'https://howler06371.gumroad.com/l/qubudd',
        'ecommerce': 'https://howler06371.gumroad.com/l/scooum',
        'real estate': 'https://howler06371.gumroad.com/l/cjemk',
        'finance': 'https://howler06371.gumroad.com/l/jdqsye',
        'customer': 'https://howler06371.gumroad.com/l/ewqobu',
        'business': 'https://howler06371.gumroad.com/l/xhxtrr',
    }

    all_shorts = []

    # Generate 5 Shorts from different product files
    selected_files = content_files[:5] if len(content_files) >= 5 else content_files
    categories = ['AI prompts', 'productivity', 'AI coding', 'marketing', 'design']

    for i, (filepath, cat) in enumerate(zip(selected_files, categories)):
        print(f'\n🎬 Short #{i+1}: {cat}')
        script = generate_shorts(cat, filepath)

        # Match product link
        link = next((v for k, v in product_links.items() if k in filepath.lower()), product_links['prompt'])

        short = {
            'id': f'SHORT_{datetime.now().strftime("%Y%m%d")}_{i}',
            'category': cat,
            'script': script,
            'product_link': link,
            'call_to_action': f'Link in bio → {link}',
            'generated_at': datetime.now().isoformat()
        }
        all_shorts.append(short)

        preview = script[:200] if isinstance(script, str) else str(script)[:200]
        print(f'   {preview}...')

    # Save
    output_file = DATA_DIR / f'shorts_batch_{datetime.now().strftime("%Y%m%d")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_shorts, f, ensure_ascii=False, indent=2)

    print(f'\n✅ {len(all_shorts)} Shorts scripts generated')
    print(f'📁 Saved: {output_file}')

    print(f'\n💡 YouTube Shorts策略:')
    print(f'   - 频道名: AI Tools Hub')
    print(f'   - 每个Short末尾引导到Gumroad产品')
    print(f'   - 用Edge-TTS免费配音 + FFmpeg合成')
    print(f'   - 每天发1-2个Shorts → 积累订阅')
    print(f'   - 达到1K订阅 + 10M Shorts观看 → 开启AdSense')

if __name__ == '__main__':
    main()
