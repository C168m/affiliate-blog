#!/usr/bin/env python3
"""
============================================================
🐦 Twitter/X自动推广机器人
策略: AI生成行业干货→自动发帖→互动增长
============================================================
"""

import json, os, sys, io, time, random
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'marketing' / 'twitter-bot' / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

env_file = PROJECT_ROOT / '.env'
env = {}
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8').split('\n'):
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

client = OpenAI(api_key=env.get('DEEPSEEK_API_KEY', ''), base_url='https://api.deepseek.com')

# ============================================================
# Twitter内容策略
# ============================================================
class TwitterContentEngine:
    """Twitter内容引擎"""

    TWEET_TYPES = {
        'value_thread': '干货线程(5-7条)',
        'quick_tip': '快速技巧(1条)',
        'case_study': '案例分享',
        'product_launch': '产品发布',
        'engagement': '互动帖(投票/问答)',
        'behind_scenes': '幕后分享',
    }

    OUR_PRODUCTS = [
        {'name': 'AI Marketing Automation Prompt Pack', 'url': 'https://payhip.com/b/cxgM9', 'price': '$9.99'},
        {'name': 'ChatGPT Prompt Engineering Guide', 'url': 'https://howler06371.gumroad.com/l/fuowsw', 'price': '$19.98'},
        {'name': 'Email Marketing AI Prompt Pack', 'url': 'https://payhip.com/b/cxgM9', 'price': '$9.99'},
    ]

    def generate_thread(self, topic: str) -> dict:
        """生成5条推文线程"""
        prompt = f"""Write a viral Twitter/X thread about: {topic}

Format: 5 tweets (THREAD 🧵)
Each tweet must be under 280 characters
Style: punchy, actionable, value-packed

Tweet 1: HOOK - grab attention with a bold claim or question
Tweet 2: The PROBLEM most people face
Tweet 3: The SOLUTION (with specific steps)
Tweet 4: Real EXAMPLE or personal experience
Tweet 5: CTA + link hint (use [link] as placeholder)

Make it feel like a friend sharing secrets, not a marketer."""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=600
            )
            content = resp.choices[0].message.content
            tweets = [t.strip() for t in content.split('\n\n') if t.strip() and len(t.strip()) > 20]
            return {
                'type': 'thread',
                'topic': topic,
                'tweets': tweets[:7],
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'type': 'thread', 'error': str(e)}

    def generate_tip_tweet(self) -> dict:
        """生成单条技巧推文"""
        topics = [
            'AI productivity hack', 'prompt engineering tip',
            'digital product creation', 'side hustle idea',
            'marketing automation', 'content creation with AI'
        ]
        topic = random.choice(topics)

        prompt = f"""Write one viral Twitter/X tweet about: {topic}

Rules:
- Under 280 characters
- Start with an emoji
- Include a counterintuitive insight
- Make it shareable
- Don't use hashtags (keep it clean)
- If mentioning a resource, use [link] as placeholder"""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=150
            )
            return {
                'type': 'tip',
                'topic': topic,
                'tweet': resp.choices[0].message.content.strip(),
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'type': 'tip', 'error': str(e)}

    def generate_product_tweet(self, product: dict) -> str:
        """生成产品推广帖"""
        prompt = f"""Write a natural Twitter/X post about launching this product:
Name: {product['name']}
Price: {product['price']}

Rules:
- Don't sound like an ad
- Share the story/why behind it
- Be humble
- Under 280 chars
- Pop in [link] as placeholder"""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=150
            )
            return resp.choices[0].message.content.strip()
        except:
            return f"Just launched: {product['name']}. Check it out: [link]"


# ============================================================
# 发布计划
# ============================================================
class TwitterScheduler:
    """Twitter发布调度"""

    DAILY_SCHEDULE = [
        {'time': '09:00', 'type': 'quick_tip', 'desc': '早上技巧帖'},
        {'time': '12:00', 'type': 'engagement', 'desc': '中午互动帖'},
        {'time': '15:00', 'type': 'value_thread', 'desc': '下午干货线程'},
        {'time': '18:00', 'type': 'quick_tip', 'desc': '晚上技巧帖'},
        {'time': '21:00', 'type': 'engagement', 'desc': '晚间互动'},
    ]

    WEEKLY_PLAN = {
        'Monday': ['value_thread', 'quick_tip', 'quick_tip'],
        'Tuesday': ['quick_tip', 'engagement', 'quick_tip'],
        'Wednesday': ['value_thread', 'product_launch', 'quick_tip'],
        'Thursday': ['quick_tip', 'engagement', 'value_thread'],
        'Friday': ['quick_tip', 'quick_tip', 'case_study'],
        'Saturday': ['engagement', 'quick_tip'],
        'Sunday': ['behind_scenes', 'engagement'],
    }

    def get_today_plan(self) -> list:
        today = datetime.now().strftime('%A')
        return self.WEEKLY_PLAN.get(today, ['quick_tip', 'quick_tip'])


# ============================================================
# 主程序
# ============================================================
def main():
    print("=" * 60)
    print("🐦 Twitter/X自动推广机器人")
    print("=" * 60)

    engine = TwitterContentEngine()
    scheduler = TwitterScheduler()

    # 今日计划
    today_plan = scheduler.get_today_plan()
    print(f"\n📅 今日发布计划 ({datetime.now().strftime('%A')}):")
    for t in today_plan:
        emoji = {'value_thread': '🧵', 'quick_tip': '💡', 'engagement': '💬',
                 'product_launch': '🚀', 'case_study': '📊', 'behind_scenes': '🎬'}
        print(f"  {emoji.get(t, '📝')} {t}")

    # 生成内容
    print(f"\n📝 生成今日内容...")

    # 1个线程
    print("\n🧵 干货线程:")
    thread = engine.generate_thread('how to use AI to 10x your productivity')
    if 'tweets' in thread:
        for i, t in enumerate(thread['tweets'], 1):
            print(f"  Tweet {i}: {t[:80]}...")

    # 2个技巧
    print("\n💡 技巧帖:")
    for i in range(2):
        tip = engine.generate_tip_tweet()
        if 'tweet' in tip:
            print(f"  Tip {i+1}: {tip['tweet'][:100]}")

    # 1个产品帖
    print("\n🚀 产品帖:")
    prod = engine.generate_product_tweet(engine.OUR_PRODUCTS[0])
    print(f"  {prod}")

    # 保存内容库
    content_lib = DATA_DIR / 'content_library.json'
    content = {
        'generated_at': datetime.now().isoformat(),
        'thread': thread,
        'product_tweet': prod
    }
    with open(content_lib, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 内容已保存: {content_lib}")
    print("\n" + "=" * 60)
    print("📊 Twitter推广策略:")
    print("  1. 每天3-5条推文 (价值+互动+产品)")
    print("  2. 在AI/产品/创业相关话题下互动")
    print("  3. 简介放 Gumroad/Payhip 链接")
    print("  4. Twitter API or Playwright 自动发布")
    print("  5. 目标: 1个月积累500+粉丝开始变现")
    print("=" * 60)


if __name__ == '__main__':
    main()
