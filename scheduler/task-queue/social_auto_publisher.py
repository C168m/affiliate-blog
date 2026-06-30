#!/usr/bin/env python3
"""
============================================================
📣 Social Media Auto Publisher — 社媒自动化发布系统
支持: Twitter/X | Reddit | LinkedIn | Facebook Page
============================================================
"""

import json, os, sys, io, time, random, hashlib
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'scheduler' / 'task-queue' / 'social_posts'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Config
# ============================================================
env = {}
env_file = PROJECT_ROOT / '.env'
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8').split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

API_KEY = env.get('DEEPSEEK_API_KEY', '')
if not API_KEY:
    print('ERROR: DEEPSEEK_API_KEY not found')
    sys.exit(1)

client = OpenAI(api_key=API_KEY, base_url='https://api.deepseek.com')

# ============================================================
# Product Links Pool
# ============================================================
PRODUCT_LINKS = [
    {'name': 'AI Marketing Automation Prompt Pack', 'url': 'https://payhip.com/b/cxgM9', 'price': '$9.99'},
    {'name': 'Email Marketing AI Prompt Pack', 'url': 'https://payhip.com/b/cxgM9', 'price': '$9.99'},
    {'name': 'ChatGPT Prompt Engineering Guide', 'url': 'https://howler06371.gumroad.com/l/fuowsw', 'price': '$19.98'},
    {'name': 'YouTube Automation Prompt Pack', 'url': 'https://howler06371.gumroad.com/l/pesoed', 'price': '$9.99'},
    {'name': 'Productivity Notion Templates', 'url': 'https://howler06371.gumroad.com/l/zmyrkl', 'price': '$9.99'},
]

# ============================================================
# Content Engine
# ============================================================
class SocialContentGenerator:
    """生成各平台内容"""

    def twitter_post(self, topic: str, include_link: bool = False) -> str:
        """生成推文(280字以内)"""
        link_hint = ''
        if include_link:
            p = random.choice(PRODUCT_LINKS)
            link_hint = f'Mention your product naturally: {p["name"]} ({p["url"]})'

        prompt = f"""Write ONE viral Twitter/X post about: {topic}
{link_hint}

Rules:
- Under 280 characters
- Start with emoji
- Include actionable insight
- Make people want to engage
- ONE hashtag max
- If product mentioned, make it feel like a genuine recommendation
- NO sales-y language
- Write in English"""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=150, temperature=0.9
            )
            return resp.choices[0].message.content.strip()
        except:
            return ''

    def reddit_post(self, subreddit: str) -> dict:
        """生成Reddit帖"""
        topics = {
            'r/SideProject': 'Recently built an AI tool for {niche}. Would love feedback from the community.',
            'r/ArtificialIntelligence': 'Interesting trend I noticed about {niche} — anyone else seeing this?',
            'r/digitalproducts': 'My experience creating and selling {niche} digital products — what worked and what didn\'t',
            'r/passive_income': 'How I\'m using AI to build passive income streams in 2026',
        }

        base_topic = topics.get(subreddit, topics['r/SideProject'])
        niche = random.choice(['AI prompts', 'productivity templates', 'AI marketing', 'digital content'])

        prompt = f"""Write a Reddit post for {subreddit}.
Topic: {base_topic.format(niche=niche)}

Rules:
- 90% value, 10% self-promo (only if natural)
- Authentic, personal voice
- 200-400 words
- Discussion question at the end
- Do NOT include links unless it feels 100% natural
"""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=600, temperature=0.8
            )
            content = resp.choices[0].message.content
            title = content.strip().split('\n')[0][:100]

            return {
                'subreddit': subreddit,
                'title': title.replace('# ', ''),
                'content': content,
                'type': 'value_post'
            }
        except:
            return {}

    def linkedin_post(self, topic: str) -> str:
        """生成LinkedIn帖"""
        prompt = f"""Write a LinkedIn post about: {topic}
Rules:
- Professional but conversational
- 3-5 short paragraphs
- Share insight/lesson learned
- End with a question to drive engagement
- NO links unless truly adding value
- 800-1200 characters"""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=400, temperature=0.8
            )
            return resp.choices[0].message.content.strip()
        except:
            return ''


# ============================================================
# Post Scheduler
# ============================================================
class PostScheduler:
    """排期引擎"""

    WEEKLY_SCHEDULE = {
        'Monday': [
            {'time': '09:00', 'platform': 'twitter', 'type': 'quick_tip'},
            {'time': '12:00', 'platform': 'linkedin', 'type': 'thought_leadership'},
            {'time': '18:00', 'platform': 'twitter', 'type': 'engagement'},
            {'time': '20:00', 'platform': 'reddit', 'type': 'value_post'},
        ],
        'Tuesday': [
            {'time': '09:00', 'platform': 'twitter', 'type': 'product_mention'},
            {'time': '14:00', 'platform': 'linkedin', 'type': 'case_study'},
            {'time': '18:00', 'platform': 'twitter', 'type': 'thread'},
        ],
        'Wednesday': [
            {'time': '09:00', 'platform': 'twitter', 'type': 'quick_tip'},
            {'time': '12:00', 'platform': 'reddit', 'type': 'value_comment'},
            {'time': '16:00', 'platform': 'linkedin', 'type': 'educational'},
            {'time': '18:00', 'platform': 'twitter', 'type': 'engagement'},
        ],
        'Thursday': [
            {'time': '09:00', 'platform': 'twitter', 'type': 'product_mention'},
            {'time': '12:00', 'platform': 'linkedin', 'type': 'thought_leadership'},
            {'time': '18:00', 'platform': 'twitter', 'type': 'quick_tip'},
        ],
        'Friday': [
            {'time': '09:00', 'platform': 'twitter', 'type': 'case_study'},
            {'time': '14:00', 'platform': 'linkedin', 'type': 'behind_scenes'},
            {'time': '18:00', 'platform': 'twitter', 'type': 'engagement'},
            {'time': '20:00', 'platform': 'reddit', 'type': 'value_post'},
        ],
        'Saturday': [
            {'time': '12:00', 'platform': 'twitter', 'type': 'casual_tip'},
            {'time': '16:00', 'platform': 'reddit', 'type': 'discussion'},
        ],
        'Sunday': [
            {'time': '12:00', 'platform': 'twitter', 'type': 'reflection'},
            {'time': '18:00', 'platform': 'linkedin', 'type': 'weekly_roundup'},
        ],
    }

    def get_today_schedule(self) -> list:
        today = datetime.now().strftime('%A')
        return self.WEEKLY_SCHEDULE.get(today, [])

    def generate_weekly_batch(self):
        """生成一周的全部内容"""
        gen = SocialContentGenerator()
        all_posts = []

        for day, slots in self.WEEKLY_SCHEDULE.items():
            day_posts = []
            for slot in slots:
                post = {
                    'day': day,
                    'time': slot['time'],
                    'platform': slot['platform'],
                    'type': slot['type'],
                    'content': '',
                    'status': 'draft'
                }

                # Generate content based on platform and type
                topics_pool = [
                    'how AI is changing content creation',
                    'why digital products are the best side hustle',
                    '5 lessons from building AI tools',
                    'the future of work with AI',
                    'how to use ChatGPT for marketing',
                    'productivity hacks using Notion',
                ]
                topic = random.choice(topics_pool)

                if slot['platform'] == 'twitter':
                    include_link = slot['type'] in ['product_mention', 'case_study']
                    post['content'] = gen.twitter_post(topic, include_link)
                elif slot['platform'] == 'reddit':
                    sr = random.choice(['r/SideProject', 'r/digitalproducts', 'r/ArtificialIntelligence'])
                    post['content'] = gen.reddit_post(sr)
                elif slot['platform'] == 'linkedin':
                    post['content'] = gen.linkedin_post(topic)

                if post['content']:
                    day_posts.append(post)
                    print(f'  📅 {day} {slot["time"]} [{slot["platform"]}] {slot["type"]}')

            all_posts.extend(day_posts)

        # Save
        output_file = DATA_DIR / f'weekly_batch_{datetime.now().strftime("%Y%m%d")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=2)

        return all_posts


# ============================================================
# Channel Configuration
# ============================================================
class ChannelSetup:
    """各渠道配置指南"""

    @staticmethod
    def setup_guide():
        print("""
╔══════════════════════════════════════════════════════════╗
║        📣 社媒渠道注册/配置指南 (全部零实名)            ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  1️⃣  Twitter/X (twitter.com)                            ║
║     注册: 任意邮箱 → 设置头像+Bio                       ║
║     API: developer.twitter.com → Free Tier              ║
║     Bio放: Gumroad/Payhip链接                           ║
║     频率: 3-5条/天, 价值:推广=8:2                       ║
║                                                          ║
║  2️⃣  Reddit (reddit.com)                                ║
║     注册: 任意邮箱 → 先养号7天                          ║
║     前7天: 只浏览+点赞+评论(不贴链接)                   ║
║     第8天起: 90%价值帖+10%产品提及                      ║
║     目标Sub: r/SideProject r/IMadeThis r/digitalproducts ║
║                                                          ║
║  3️⃣  LinkedIn (linkedin.com)                            ║
║     注册: 任意邮箱 → 填职业信息                         ║
║     频率: 1-2篇高质量帖/天                              ║
║     内容: 行业洞察+案例+趋势                            ║
║                                                          ║
║  4️⃣  Medium (medium.com) — ✅ 已注册                    ║
║     账号: hhhf10151@gmail.com                            ║
║     频率: 2-3篇/周                                       ║
║     CTA: 文末链接到产品                                  ║
║                                                          ║
║  5️⃣  Dev.to (dev.to)                                     ║
║     注册: Google账号 → 技术向内容                       ║
║     频率: 1篇/周 (可从Medium交叉发布)                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """)

    @staticmethod
    def daily_routine():
        return """
📅 每日社媒操作流程 (自动化或手动):

08:00 — 检查所有账号状态
09:00 — Twitter: 发1条价值推文
10:00 — LinkedIn: 发1条行业洞察
12:00 — Twitter: 互动(点赞+评论同领域内容)
14:00 — Reddit: 1条有价值评论
16:00 — LinkedIn: 互动
18:00 — Twitter: 发1条产品相关推文
20:00 — Reddit: 发1个价值帖(可选含产品链接)
22:00 — 检查所有平台互动数据

周频率: Twitter 20帖 + LinkedIn 5帖 + Reddit 5帖 + Medium 2篇
"""


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 60)
    print("📣 Social Media Auto Publisher")
    print("=" * 60)

    # Show setup guide
    ChannelSetup.setup_guide()
    print(ChannelSetup.daily_routine())

    # Generate week's content
    print("=" * 60)
    print("📝 生成本周全部社媒内容...")
    print("=" * 60)

    scheduler = PostScheduler()
    print(f'\n📅 {datetime.now().strftime("%A")} schedule:')
    today = scheduler.get_today_schedule()
    for slot in today:
        print(f'  {slot["time"]} [{slot["platform"]}] {slot["type"]}')

    print('\n🔄 生成全部28帖/周...')
    all_posts = scheduler.generate_weekly_batch()
    print(f'\n✅ 本周内容: {len(all_posts)} 帖')
    print(f'   保存于: {DATA_DIR}')

    # Stats
    platforms = {}
    for p in all_posts:
        platforms[p['platform']] = platforms.get(p['platform'], 0) + 1
    print('\n📊 本周分布:')
    for platform, count in platforms.items():
        print(f'   {platform}: {count} 帖')


if __name__ == '__main__':
    main()
