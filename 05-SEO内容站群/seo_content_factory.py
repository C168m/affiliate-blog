#!/usr/bin/env python3
"""
============================================================
📝 SEO内容站群 — AI文章生产 + WordPress自动发布
============================================================
"""

import json, os, sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ARTICLES_DIR = Path(__file__).parent / "articles"
ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 高价值SEO关键词模板
# ============================================================

KEYWORD_TEMPLATES = {
    "best_of": {
        "pattern": "best {niche} tools 2026",
        "intent": "商业/购买",
        "difficulty": "medium",
        "article_type": "listicle"
    },
    "vs_comparison": {
        "pattern": "{product_a} vs {product_b} comparison",
        "intent": "比较",
        "difficulty": "low",
        "article_type": "comparison"
    },
    "how_to": {
        "pattern": "how to use {tool} for {task}",
        "intent": "教程",
        "difficulty": "low",
        "article_type": "tutorial"
    },
    "review": {
        "pattern": "{product} review 2026",
        "intent": "购买决策",
        "difficulty": "low-medium",
        "article_type": "review"
    },
    "alternatives": {
        "pattern": "{product} alternatives free",
        "intent": "替代方案",
        "difficulty": "low",
        "article_type": "listicle"
    }
}

# ============================================================
# 利基市场
# ============================================================

NICHE_MARKETS = [
    {
        "name": "AI Writing Tools",
        "keywords": [
            "best AI writing tools 2026",
            "ChatGPT alternatives for writing",
            "AI copywriting software comparison",
            "best free AI writer",
            "AI content generator review"
        ],
        "affiliate_programs": ["Jasper AI (30%)", "Copy.ai (25%)", "Writesonic (30%)", "Rytr (20%)"],
        "adsense_cpc": "$2-8"
    },
    {
        "name": "AI Image Generators",
        "keywords": [
            "best AI image generator 2026",
            "Midjourney vs DALL-E vs Stable Diffusion",
            "free AI art generator no signup",
            "AI photo editor online free",
            "best AI logo maker"
        ],
        "affiliate_programs": ["Leonardo AI", "Canva Pro", "Adobe Firefly"],
        "adsense_cpc": "$1-5"
    },
    {
        "name": "Productivity Tools",
        "keywords": [
            "best productivity apps 2026",
            "Notion vs Obsidian vs Roam",
            "best project management software",
            "AI meeting notes app",
            "best to-do list app"
        ],
        "affiliate_programs": ["Notion", "Monday.com", "ClickUp"],
        "adsense_cpc": "$3-10"
    },
    {
        "name": "Website Builders",
        "keywords": [
            "best website builder 2026",
            "Wix vs Squarespace vs WordPress",
            "best free website builder",
            "AI website builder review",
            "cheapest web hosting"
        ],
        "affiliate_programs": ["Hostinger (60%)", "Bluehost ($65/sale)", "Wix ($100/sale)", "Elementor"],
        "adsense_cpc": "$5-15"
    },
    {
        "name": "VPN & Security",
        "keywords": [
            "best VPN 2026",
            "NordVPN vs ExpressVPN",
            "best free VPN",
            "password manager comparison",
            "antivirus software review"
        ],
        "affiliate_programs": ["NordVPN (40%)", "ExpressVPN (35%)", "Surfshark (50%)"],
        "adsense_cpc": "$8-20"
    }
]

# ============================================================
# AI文章生产
# ============================================================

class SEOArticleFactory:
    """SEO文章批量生产"""

    ARTICLE_TEMPLATES = {
        "listicle": """Write a comprehensive listicle article: "Best {title}"
Target keyword: {keyword}
Word count: 2000
Structure:
- Engaging introduction (hook + problem + solution preview)
- {count} items with H2 headings
- Each item: Brief intro + key features + pros/cons + pricing
- Comparison table
- Verdict & recommendation
- FAQ section (5 questions)
- CTA with affiliate links
Tone: Helpful, expert, conversational
SEO: Include target keyword in H1, first paragraph, 2-3 H2s, and conclusion""",

        "comparison": """Write a detailed comparison article: "{title}"
Target keyword: {keyword}
Word count: 2500
Structure:
- Introduction: Why this comparison matters
- Quick overview table
- Deep dive: Feature by feature comparison
- Pricing comparison table
- Use case recommendations
- Verdict: Which is best for whom
- FAQ
Tone: Balanced, data-driven, unbiased""",

        "tutorial": """Write a step-by-step tutorial: "{title}"
Target keyword: {keyword}
Word count: 1800
Structure:
- Introduction: What you'll learn
- Prerequisites
- Step 1 through Step N (detailed, with screenshots described)
- Common problems & solutions
- Pro tips
- Conclusion & next steps
Tone: Clear, patient, encouraging for beginners""",

        "review": """Write an in-depth product review: "{title}"
Target keyword: {keyword}
Word count: 2200
Structure:
- Quick verdict (TL;DR box)
- Full introduction
- Features breakdown
- Performance & testing results
- Pricing & value analysis
- Pros & cons table
- Alternatives comparison
- Final recommendation
- FAQ
Tone: Honest, detailed, based on real usage"""
    }

    def _call_deepseek(self, system_prompt, user_prompt, max_tokens=2000):
        import requests
        if not getattr(self, 'api_key', None):
            self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        if not self.api_key:
            return ""
        try:
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "max_tokens": max_tokens, "temperature": 0.7},
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            print(f"  DeepSeek err ({resp.status_code}): {resp.text[:200]}")
            return ""
        except Exception as e:
            print(f"  DeepSeek fail: {e}")
            return ""

    def generate_article(self, keyword: str, article_type: str = "listicle") -> dict:
        """生成一篇SEO文章"""
        template = self.ARTICLE_TEMPLATES.get(article_type, self.ARTICLE_TEMPLATES["listicle"])
        title = keyword.replace("best ", "").replace("2026", "").strip().title()

        print(f"  📝 [{article_type}] {keyword[:60]}...")

        # Generate real content with DeepSeek
        template_content = template  # template is a string prompt
        system_msg = f"You are a professional SEO content writer. Write a {article_type} article about: {keyword}. Include engaging intro, 2000+ words, affiliate link placeholders, and conclusion with CTA."
        user_msg = f"Write a comprehensive {article_type} article. Title: {self._title_from_keyword(keyword, article_type)}. Include real examples and practical tips. Format with H2 subheadings."
        print(f"  AI: {keyword[:50]}...")
        ai_content = self._call_deepseek(system_msg, user_msg, max_tokens=2500)

        article = {
            "id": f"SEO_{datetime.now().strftime('%Y%m%d')}_{hash(keyword) % 10000:04d}",
            "keyword": keyword,
            "article_type": article_type,
            "title": self._title_from_keyword(keyword, article_type),
            "slug": keyword.replace(" ", "-").lower()[:60],
            "content": ai_content if ai_content else "",
            "meta_description": f"Complete guide to {keyword}. Expert review, comparison, and recommendations for 2026.",
            "word_count_target": 2000,
            "status": "ai_generated" if ai_content else "draft",
            "affiliate_links": [],
            "created_at": datetime.now().isoformat()
        }

        # 保存
        article_path = ARTICLES_DIR / f"{article['slug']}.json"
        with open(article_path, "w", encoding="utf-8") as f:
            json.dump(article, f, indent=2, ensure_ascii=False)

        return article

    def batch_generate(self, niches: list = None, count: int = 10) -> list:
        """批量生成文章"""
        niches = niches or NICHE_MARKETS[:3]
        articles = []

        print(f"\n{'='*50}")
        print(f"📝 SEO文章工厂启动 — 目标: {count} 篇")
        print(f"{'='*50}\n")

        article_types = list(self.ARTICLE_TEMPLATES.keys())

        for i in range(count):
            niche = niches[i % len(niches)]
            kw = niche["keywords"][i % len(niche["keywords"])]
            atype = article_types[i % len(article_types)]

            article = self.generate_article(kw, atype)
            articles.append(article)

        print(f"\n📊 产出: {len(articles)} 篇文章")
        return articles

    def _title_from_keyword(self, keyword: str, article_type: str) -> str:
        if article_type == "listicle":
            return f"{keyword.title()} — Top 10 Picks for 2026"
        elif article_type == "comparison":
            return f"{keyword.title()} — Honest Comparison 2026"
        elif article_type == "tutorial":
            return f"{keyword.title()} — Step-by-Step Guide 2026"
        elif article_type == "review":
            return f"{keyword.title()} — In-Depth Review 2026"
        return f"{keyword.title()} — Ultimate Guide 2026"

# ============================================================
# WordPress自动发布
# ============================================================

class WordPressPublisher:
    """WordPress自动发布"""

    def __init__(self):
        self.sites_file = Path(__file__).parent / "sites.json"
        self.load_sites()

    def load_sites(self):
        if self.sites_file.exists():
            with open(self.sites_file, "r", encoding="utf-8") as f:
                self.sites = json.load(f)
        else:
            self.sites = []

    def add_site(self, domain: str, wp_user: str, wp_app_password: str) -> dict:
        """添加WordPress站点"""
        site = {
            "id": len(self.sites) + 1,
            "domain": domain,
            "api_url": f"https://{domain}/wp-json/wp/v2",
            "user": wp_user,
            "app_password": wp_app_password,  # WordPress → Users → Application Passwords
            "added_at": datetime.now().isoformat()
        }
        self.sites.append(site)
        with open(self.sites_file, "w", encoding="utf-8") as f:
            json.dump(self.sites, f, indent=2)
        return site

    def publish_article(self, site_id: int, article: dict) -> dict:
        """发布文章到WordPress"""
        site = self.sites[site_id - 1] if site_id <= len(self.sites) else None
        if not site:
            print(f"  ❌ 站点{site_id}不存在")
            return {"status": "failed"}

        print(f"  📤 发布到 {site['domain']}: {article['title'][:50]}...")

        # TODO: WordPress REST API
        # POST {api_url}/posts
        # Authorization: Basic {base64(user:app_password)}
        # Body: {title, content, slug, status: "publish", categories, tags}

        result = {
            "site": site["domain"],
            "article_id": article["id"],
            "url": f"https://{site['domain']}/{article['slug']}",
            "status": "published",
            "published_at": datetime.now().isoformat()
        }

        return result


# ============================================================
# 关键词研究工具
# ============================================================

class KeywordResearch:
    """关键词研究"""

    @staticmethod
    def generate_keyword_ideas(niche: str) -> list:
        """生成关键词思路"""
        ideas = []
        for template_name, template in KEYWORD_TEMPLATES.items():
            kw = template["pattern"].replace("{niche}", niche)
            ideas.append({
                "keyword": kw,
                "type": template_name,
                "intent": template["intent"],
                "difficulty": template["difficulty"]
            })
        return ideas

    @staticmethod
    def analyze_keywords(keywords: list) -> dict:
        """分析关键词(整合第三方数据)"""
        # TODO: 对接Ahrefs/Semrush/DataForSEO API
        return {
            "total_keywords": len(keywords),
            "avg_difficulty": "low-medium",
            "total_search_volume_estimate": "10K-50K/month",
            "top_opportunity": keywords[0] if keywords else None
        }


# ============================================================
# CLI
# ============================================================

def main():
    from dotenv import load_dotenv; load_dotenv()
    import argparse
    parser = argparse.ArgumentParser(description="SEO内容站群")
    parser.add_argument("--action", choices=["produce", "keywords", "publish", "niches"], default="niches")
    parser.add_argument("--niche", type=str, default="AI Writing Tools")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--keyword", type=str)

    args = parser.parse_args()

    if args.action == "niches":
        print("\n💰 高价值SEO利基市场:\n")
        for n in NICHE_MARKETS:
            print(f"  📍 {n['name']}")
            print(f"     AdSense CPC: {n['adsense_cpc']}")
            print(f"     联盟: {', '.join(n['affiliate_programs'][:2])}")
            print(f"     关键词示例: {n['keywords'][0]}\n")

    elif args.action == "keywords":
        kw_research = KeywordResearch()
        ideas = kw_research.generate_keyword_ideas(args.niche)
        print(f"\n🔑 {args.niche} 关键词思路:\n")
        for idea in ideas:
            print(f"  [{idea['intent']}] {idea['keyword']} (难度: {idea['difficulty']})")

    elif args.action == "produce":
        factory = SEOArticleFactory()
        niches = [n for n in NICHE_MARKETS if n["name"] == args.niche] or NICHE_MARKETS[:1]
        factory.batch_generate(niches, args.count)

    elif args.action == "publish":
        wp = WordPressPublisher()
        print(f"\n📋 已配置站点: {len(wp.sites)}")
        for s in wp.sites:
            print(f"  {s['domain']}")

if __name__ == "__main__":
    main()
