#!/usr/bin/env python3
"""
============================================================
🤖 Reddit自动推广机器人
策略: 90%价值贡献 + 10%产品链接
功能: 自动发帖、评论、监控提及、养号
============================================================
"""

import json, os, sys, io, time, random
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'marketing' / 'reddit-bot' / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_env():
    env_file = PROJECT_ROOT / '.env'
    config = {}
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8').split('\n'):
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                config[k.strip()] = v.strip()
    return config

env = load_env()
client = OpenAI(api_key=env.get('DEEPSEEK_API_KEY', ''), base_url='https://api.deepseek.com')

# ============================================================
# 目标Subreddit配置
# ============================================================
TARGET_SUBREDDITS = {
    'r/SideProject': {
        'description': '独立开发者项目展示',
        'audience': '开发者/创业者',
        'strategy': '分享开发过程+产品链接',
        'min_karma': 10,
        'post_frequency': '2-3天1次'
    },
    'r/IMadeThis': {
        'description': '我做了这个',
        'audience': '创作者',
        'strategy': '展示产品成果',
        'min_karma': 5,
        'post_frequency': '每周1次'
    },
    'r/ArtificialIntelligence': {
        'description': 'AI讨论',
        'audience': 'AI爱好者',
        'strategy': '分享AI使用技巧→产品链接',
        'min_karma': 50,
        'post_frequency': '每天评论+偶尔发帖'
    },
    'r/digitalproducts': {
        'description': '数字产品',
        'audience': '数字产品买卖双方',
        'strategy': '分享经验+产品宣传',
        'min_karma': 5,
        'post_frequency': '每周1-2次'
    },
    'r/passive_income': {
        'description': '被动收入',
        'audience': '想赚被动收入的人',
        'strategy': '分享收入报告+产品链接',
        'min_karma': 20,
        'post_frequency': '每月1-2次'
    }
}

# ============================================================
# 内容模板
# ============================================================
class RedditContentGenerator:
    """Reddit内容生成器"""

    def generate_value_post(self, niche: str) -> dict:
        """生成价值帖(90%内容,不提产品)"""
        prompt = f"""Write a helpful Reddit post about {niche}.

Rules:
- Provide genuine value (tips, insights, lessons learned)
- Do NOT mention any product or link
- Keep it under 300 words
- Be authentic and personal (like sharing with a community)
- Add a discussion question at the end

Topic examples based on niche:
- AI tools: "5 AI prompts I use daily that saved me hours"
- Productivity: "The system I built to 10x my output"
- Digital products: "How I went from 0 to first sale in 2 weeks"
"""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=600
            )
            content = resp.choices[0].message.content

            post = {
                'type': 'value_post',
                'niche': niche,
                'title': self._extract_title(content),
                'content': content,
                'generated_at': datetime.now().isoformat()
            }
            return post
        except Exception as e:
            return {'type': 'value_post', 'error': str(e)}

    def generate_soft_promo_post(self, product_name: str, product_url: str, niche: str) -> dict:
        """生成软推广帖(展示产品但不hard sell)"""
        prompt = f"""Write a Reddit post sharing something you built: "{product_name}"

Context: This is for r/SideProject or r/IMadeThis style communities.

Rules:
- Share the story behind building it
- Be humble and authentic
- Mention the product naturally in context (link: {product_url})
- Ask for feedback
- Keep under 300 words
- Don't sound like an ad
"""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=600
            )
            content = resp.choices[0].message.content

            return {
                'type': 'soft_promo',
                'product': product_name,
                'url': product_url,
                'title': self._extract_title(content),
                'content': content,
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {'type': 'soft_promo', 'error': str(e)}

    def generate_comment(self, post_topic: str, our_product_related: bool = False) -> str:
        """生成评论(不贴链接的有价值回复)"""
        if our_product_related:
            prompt = f"Write a 2-3 sentence helpful Reddit comment about: {post_topic}. Mention you have a resource but don't link it unless asked. Keep it natural."
        else:
            prompt = f"Write a 2-3 sentence genuinely helpful Reddit comment about: {post_topic}. Add value, be specific. No links."

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=200
            )
            return resp.choices[0].message.content
        except:
            return ""

    def _extract_title(self, content: str) -> str:
        """从内容中提取标题"""
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 20 and len(line) < 120:
                if line.startswith('# '):
                    return line[2:]
                return line
        return lines[0][:100] if lines else "My experience with digital products"


# ============================================================
# 账号管理
# ============================================================
class RedditAccountManager:
    """Reddit账号管理"""

    def __init__(self):
        self.accounts_file = DATA_DIR / 'accounts.json'
        self.load()

    def load(self):
        if self.accounts_file.exists():
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                self.accounts = json.load(f)
        else:
            self.accounts = []

    def add_account(self, username: str, email: str, created_date: str = None):
        self.accounts.append({
            'username': username,
            'email': email,
            'created': created_date or datetime.now().strftime('%Y-%m-%d'),
            'karma': 0,
            'posts_today': 0,
            'comments_today': 0,
            'last_active': datetime.now().isoformat(),
            'status': 'warming_up'  # warming_up → active → banned
        })
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)

    def get_warming_accounts(self) -> list:
        """获取养号阶段的账号"""
        return [a for a in self.accounts if a['status'] == 'warming_up']

    def can_post_today(self, username: str) -> bool:
        """检查今天是否可以发帖"""
        for a in self.accounts:
            if a['username'] == username:
                return a['posts_today'] < 3  # 每日最多3帖
        return False

    def record_post(self, username: str):
        for a in self.accounts:
            if a['username'] == username:
                a['posts_today'] += 1
                a['last_active'] = datetime.now().isoformat()
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)


# ============================================================
# 发布策略
# ============================================================
class RedditPublisher:
    """Reddit发布器"""

    SAFETY_RULES = """
    🔴 REDDIT安全规则:
    1. 新号前7天只浏览+点赞,不发帖不评论
    2. 第8-14天: 每天2-3条评论,不发帖
    3. 第15天+: 可以发帖,但90%价值+10%推广
    4. 同一链接不同subreddit之间间隔>24h
    5. 绝不发在r/technology等大sub(会立刻被ban)
    6. 每个subreddit遵守其规则
    7. 用不同的标题和内容
    8. 用Playwright操作(不用API,更安全)
    """

    DAILY_PLAN = {
        'week1': {
            'name': '养号期',
            'actions': ['浏览热门帖子', '点赞10条', '关注目标subreddit'],
            'no_posting': True
        },
        'week2': {
            'name': '评论期',
            'actions': ['每天2-3条有价值的评论', '不贴链接', '积累karma'],
            'no_posting': True
        },
        'week3_plus': {
            'name': '推广期',
            'actions': ['发价值帖(无链接)', '偶尔发软推广帖', '评论区自然提及产品'],
            'rule': '90%价值 + 10%推广'
        }
    }


# ============================================================
# 主程序
# ============================================================
def main():
    print("=" * 60)
    print("🤖 Reddit自动推广机器人")
    print("=" * 60)
    print()

    # 安全规则
    print(RedditPublisher.SAFETY_RULES)
    print()

    # 计划表
    for week, plan in RedditPublisher.DAILY_PLAN.items():
        print(f"📅 {week} — {plan['name']}")
        for action in plan['actions']:
            print(f"   → {action}")
        print()

    # 生成内容
    gen = RedditContentGenerator()
    print("=" * 60)
    print("📝 生成推广内容样本")
    print("=" * 60)

    # 价值帖
    vp = gen.generate_value_post('AI digital products')
    if 'title' in vp:
        print(f"\n📄 [价值帖] {vp['title']}")
        print(f"   {vp['content'][:200]}...")

    # 软推广帖
    sp = gen.generate_soft_promo_post(
        'AI Marketing Automation Prompt Pack',
        'https://payhip.com/b/cxgM9',
        'AI tools'
    )
    if 'title' in sp:
        print(f"\n📄 [软推广帖] {sp['title']}")
        print(f"   {sp['content'][:200]}...")

    print()
    print("=" * 60)
    print("📊 目标Subreddit:")
    for name, info in TARGET_SUBREDDITS.items():
        print(f"  📍 {name}: {info['description']} (需Karma:{info['min_karma']})")
    print()
    print("💡 下一步: 注册Reddit账号 → 养号7天 → 开始推广")


if __name__ == '__main__':
    main()
