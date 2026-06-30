#!/usr/bin/env python3
"""
============================================================
📣 社交媒体矩阵自动导流
Twitter/X + Reddit + Pinterest + Medium
============================================================
"""

import json, os, sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SOCIAL_DATA = Path(__file__).parent
for sub in ["Twitter-X自动化", "Reddit自动化", "Pinterest自动化", "Medium博客"]:
    (SOCIAL_DATA / sub).mkdir(parents=True, exist_ok=True)

# ============================================================
# 内容模板库
# ============================================================

class ContentTemplates:
    """各平台内容模板"""

    @staticmethod
    def twitter_post(product: dict) -> str:
        """Twitter推广帖"""
        templates = [
            f"🔥 Just launched: {product['title_en']}\n\n💲 Only ${product['price_usd']}\n📥 Instant download\n🔗 Link in bio",
            f"I spent 50 hours creating this {product['title_en']}.\n\nYou can get it for just ${product['price_usd']}.\n\nWorth every penny. 👇",
            f"Tired of searching for good {product['niche']} resources?\n\nI made one: {product['title_en']}\n\n${product['price_usd']} — lifetime access.",
            f"New product alert 🚀\n\n{product['title_en']}\n✅ 50+ ready-to-use items\n✅ Lifetime updates\n✅ ${product['price_usd']} only\n\nGrab it here 👇",
        ]
        return templates[hash(product['id']) % len(templates)]

    @staticmethod
    def reddit_post(product: dict, subreddit: str) -> dict:
        """Reddit帖子(注意: 90%价值 + 10%推广)"""
        return {
            "title": f"[Resource] {product['title_en']} — Sharing something I built",
            "body": f"""Hey r/{subreddit}!

I've been working on {product['niche']} for a while and created this {product['title_en']}.

**What's included:**
- 50+ professionally curated items
- Ready to use immediately
- Lifetime access + updates

**Why I made this:**
I noticed there wasn't a good all-in-one resource for {product['niche']}, so I compiled everything I've learned and used.

**Price:** ${product['price_usd']} (trying to keep it accessible)

**Link:** [Gumroad](https://store.com/{product['id']})

Happy to answer any questions in the comments! 🙏""",
            "subreddit": subreddit
        }

    @staticmethod
    def pinterest_pin(product: dict) -> dict:
        """Pinterest Pin"""
        return {
            "title": product["title_en"],
            "description": f"${product['price_usd']} — {product['title_en']}. Instant download. #ai #digitalproduct #{product['niche'].replace(' ', '')}",
            "link": f"https://store.com/{product['id']}",
            "board": "Digital Products & Resources"
        }

    @staticmethod
    def medium_article(product: dict) -> dict:
        """Medium导流文章(教程/经验分享)"""
        return {
            "title": f"How I Created {product['title_en']} Using AI — And Why You Should Too",
            "subtitle": f"A step-by-step guide to creating digital products with AI, featuring my latest release: {product['title_en']}",
            "tags": ["AI", "Digital Products", "Side Hustle", "Maker", "Technology"],
            "cta": f"👇 Get {product['title_en']} here: https://store.com/{product['id']}"
        }

# ============================================================
# 社交媒体自动化管理器
# ============================================================

class SocialMediaAutomation:
    """社交媒体矩阵自动运营"""

    def __init__(self):
        self.templates = ContentTemplates()
        self.schedule_file = SOCIAL_DATA / "post_schedule.json"

    def create_content_batch(self, products: list) -> dict:
        """为一个产品创建全平台推广内容"""
        batch = {}

        for product in products[:3]:  # 每次处理最多3个产品
            product_content = {
                "product_id": product["id"],
                "twitter": self.templates.twitter_post(product),
                "reddit": self.templates.reddit_post(product, "SideProject"),
                "pinterest": self.templates.pinterest_pin(product),
                "medium": self.templates.medium_article(product),
                "created_at": datetime.now().isoformat()
            }
            batch[product["id"]] = product_content

        return batch

    def schedule_posts(self, content_batch: dict, platforms: list = None):
        """安排发布计划"""
        platforms = platforms or ["twitter", "reddit", "pinterest"]

        schedule = []
        now = datetime.now()

        for i, (product_id, content) in enumerate(content_batch.items()):
            for platform in platforms:
                # 错开发布时间,避免同时发布
                delay_hours = i * 2 + platforms.index(platform) * 0.5
                scheduled_time = now + timedelta(hours=delay_hours)

                post = {
                    "product_id": product_id,
                    "platform": platform,
                    "scheduled_time": scheduled_time.isoformat(),
                    "content": content.get(platform, ""),
                    "status": "scheduled"
                }
                schedule.append(post)
                print(f"  📅 计划: [{platform}] {scheduled_time.strftime('%H:%M')} — {product_id}")

        # 保存排期
        with open(self.schedule_file, "w", encoding="utf-8") as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

        return schedule

    def get_recommended_subreddits(self, niche: str) -> list:
        """根据niche推荐Subreddit"""
        recommendations = {
            "AI tools": ["r/ArtificialIntelligence", "r/SideProject", "r/SaaS", "r/InternetIsBeautiful"],
            "productivity": ["r/productivity", "r/GetMotivated", "r/selfimprovement", "r/Notion"],
            "marketing": ["r/marketing", "r/SEO", "r/content_marketing", "r/socialmedia"],
            "coding": ["r/programming", "r/learnprogramming", "r/webdev", "r/Python"],
            "design": ["r/graphic_design", "r/UI_Design", "r/Design", "r/FigmaDesign"],
        }
        return recommendations.get(niche, ["r/SideProject", "r/IMadeThis"])

# ============================================================
# 平台安全规则
# ============================================================

class PlatformSafety:
    """各平台风控规则"""

    RULES = {
        "reddit": {
            "max_posts_per_day": 3,
            "min_karma_to_post": 10,
            "self_promo_ratio": "10:1 (90% value, 10% promo)",
            "warning": "先养号，多评论贡献价值，再偶尔放链接",
            "ban_risk": "高 — 务必遵守10:1规则"
        },
        "twitter": {
            "max_posts_per_day": 10,
            "min_account_age": "3 days",
            "warning": "新号前3天不要放链接",
            "ban_risk": "中 — 不要批量重复内容"
        },
        "pinterest": {
            "max_pins_per_day": 25,
            "warning": "使用Rich Pin增加点击率",
            "ban_risk": "低"
        },
        "medium": {
            "max_posts_per_day": 3,
            "warning": "文章需要有实质内容，不能纯广告",
            "ban_risk": "中 — Medium严格打击纯广告"
        }
    }

    @staticmethod
    def check_safety(platform: str) -> dict:
        return PlatformSafety.RULES.get(platform, {})


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="社交媒体矩阵")
    parser.add_argument("--action", choices=["create", "schedule", "rules"], default="rules")
    parser.add_argument("--platform", type=str)

    args = parser.parse_args()

    if args.action == "rules":
        print("\n🛡 各平台安全规则:\n")
        for platform, rules in PlatformSafety.RULES.items():
            print(f"  📍 {platform.upper()}")
            for key, val in rules.items():
                print(f"     {key}: {val}")
            print()

    elif args.action == "create":
        auto = SocialMediaAutomation()
        # 示例产品
        demo_product = {
            "id": "DEMO_001",
            "title_en": "Ultimate AI Marketing Prompts Bundle",
            "price_usd": 9.99,
            "niche": "AI marketing"
        }
        batch = auto.create_content_batch([demo_product])
        print(f"\n✅ 已为 {len(batch)} 个产品创建全平台推广内容")
        for pid, content in batch.items():
            print(f"\n  📦 {pid}:")
            print(f"    Twitter: {content['twitter'][:80]}...")
            print(f"    Reddit: {content['reddit']['title']}")
            print(f"    Pinterest: {content['pinterest']['title']}")

    elif args.action == "schedule":
        auto = SocialMediaAutomation()
        auto.schedule_posts({"DEMO_001": {}})

if __name__ == "__main__":
    main()
