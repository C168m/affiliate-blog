#!/usr/bin/env python3
"""
============================================================
🏭 数字产品工厂 — AI批量生产可销售数字商品
============================================================
"""

import json, os, sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = Path(__file__).parent / "output"
for sub in ["pdfs", "templates", "ebooks", "assets", "catalogs"]:
    (OUTPUT_DIR / sub).mkdir(parents=True, exist_ok=True)

# ============================================================
# 产品模板
# ============================================================

PRODUCT_TEMPLATES = {
    "prompt_pack": {
        "name": "AI提示词包",
        "price_usd": 9.99,
        "format": "PDF",
        "categories": ["marketing", "coding", "writing", "design", "business", "education", "social media", "SEO", "email", "sales"],
        "prompt": """You are a professional prompt engineer. Create a premium prompt pack for the niche: {niche}.
Include 20 high-quality, ready-to-use prompts. Each prompt should have:
- Title
- Category
- The prompt itself
- Expected output description
- Tips for best results
Format as structured content ready for PDF export."""
    },
    "ebook": {
        "name": "AI教程电子书",
        "price_usd": 19.99,
        "format": "PDF",
        "categories": ["AI for Beginners", "ChatGPT Mastery", "AI Marketing", "AI Coding", "AI Design", "AI Business"],
        "prompt": """Write a comprehensive ebook chapter about: {niche}.
Target audience: Beginners to intermediate.
Length: ~2000 words.
Include: Introduction, 5 key concepts, practical examples, summary.
Tone: Professional but accessible."""
    },
    "notion_template": {
        "name": "Notion模板",
        "price_usd": 14.99,
        "format": "Notion Link",
        "categories": ["Project Management", "Habit Tracker", "Content Calendar", "Finance Tracker", "Goal Setting", "Meeting Notes"],
        "prompt": """Design a Notion template for: {niche}.
Include: Database structure, views, properties, formulas.
Describe the layout and functionality in detail."""
    },
    "asset_pack": {
        "name": "素材/代码包",
        "price_usd": 29.99,
        "format": "ZIP",
        "categories": ["Python Scripts", "Social Media Templates", "UI Components", "Icon Pack", "Email Templates", "Landing Page Kit"],
        "prompt": """Create a list of items for a {niche} asset pack.
List 20 items with descriptions and file formats.
Describe what each item does and its use case."""
    }
}

# ============================================================
# 产品工厂
# ============================================================

class DigitalProductFactory:
    """数字产品批量生产"""

    def __init__(self, deepseek_api_key: str = ""):
        self.api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY", "")

    def _call_deepseek(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """Call DeepSeek API to generate real content"""
        import requests
        if not self.api_key:
            return ""
        try:
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                print(f"  DeepSeek API error ({resp.status_code}): {resp.text[:200]}")
                return ""
        except Exception as e:
            print(f"  DeepSeek call failed: {e}")
            return ""

    def create_product(self, product_type: str, niche: str) -> dict:
        """创建一个数字产品"""

        if product_type not in PRODUCT_TEMPLATES:
            raise ValueError(f"未知产品类型: {product_type}")

        template = PRODUCT_TEMPLATES[product_type]

        # Call DeepSeek to generate real product content
        system_msg = "You are a professional digital product creator. Create high-quality, marketable content ready to sell."
        user_msg = template["prompt"].replace("{niche}", niche)
        print(f"  AI: {product_type}/{niche}...")
        ai_content = self._call_deepseek(system_msg, user_msg, max_tokens=1500)

        # 构建产品数据
        product = {
            "id": f"DP_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": product_type,
            "name": template["name"],
            "niche": niche,
            "price_usd": template["price_usd"],
            "format": template["format"],
            "title_en": self._gen_english_title(product_type, niche),
            "title_cn": self._gen_chinese_title(product_type, niche),
            "description": self._gen_description(product_type, niche),
            "ai_content": ai_content if ai_content else "",
            "tags": self._gen_tags(product_type, niche),
            "created_at": datetime.now().isoformat(),
            "status": "ai_generated" if ai_content else "draft"
        }

        # 保存产品数据
        self._save_product(product)
        return product

    def batch_create(self, niches: list, count: int = 20) -> list:
        """批量生产 — 多个赛道×多个类型"""

        products = []
        types = list(PRODUCT_TEMPLATES.keys())

        print(f"\n{'='*50}")
        print(f"🏭 数字产品工厂启动")
        print(f"📦 目标产出: {count} 个产品")
        print(f"🎯 赛道: {', '.join(niches[:5])}")
        print(f"{'='*50}\n")

        for i in range(count):
            niche = niches[i % len(niches)]
            ptype = types[i % len(types)]
            product = self.create_product(ptype, niche)
            products.append(product)
            print(f"  ✅ [{i+1}/{count}] ${product['price_usd']:.2f} — {product['title_en']}")

        # 保存产品目录
        catalog = {
            "generated_at": datetime.now().isoformat(),
            "total_products": len(products),
            "total_value_usd": round(sum(p["price_usd"] for p in products), 2),
            "products": products
        }
        catalog_path = OUTPUT_DIR / "catalogs" / f"catalog_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)

        print(f"\n📊 生产报告:")
        print(f"  产品总数: {len(products)}")
        print(f"  总价值: ${catalog['total_value_usd']:.2f}")
        print(f"  目录文件: {catalog_path}")

        return products

    # ===== 辅助函数 =====

    def _gen_english_title(self, ptype: str, niche: str) -> str:
        titles = {
            "prompt_pack": f"100+ {niche.title()} ChatGPT Prompts — Ultimate Bundle 2026",
            "ebook": f"Mastering {niche.title()} with AI — Complete Guide 2026",
            "notion_template": f"Ultimate {niche.title()} Notion Template — All-in-One System",
            "asset_pack": f"Premium {niche.title()} Asset Pack — 50+ Files Ready to Use",
        }
        return titles.get(ptype, f"{niche.title()} Digital Product")

    def _gen_chinese_title(self, ptype: str, niche: str) -> str:
        titles = {
            "prompt_pack": f"终极{niche}AI提示词大全—100+精选模板",
            "ebook": f"用AI搞定{niche}—零基础到精通",
            "notion_template": f"最强{niche}Notion模板—一站式管理系统",
            "asset_pack": f"专业{niche}素材包—50+即用资源",
        }
        return titles.get(ptype, f"{niche}数字产品")

    def _gen_description(self, ptype: str, niche: str) -> str:
        return f"""Professionally crafted {PRODUCT_TEMPLATES[ptype]['name'].lower()} for {niche}.

✅ AI-generated, human-curated
✅ Ready to use — no setup required
✅ Lifetime access + free updates
✅ 30-day money-back guarantee

Perfect for: {niche} professionals, beginners, and enthusiasts.

Format: {PRODUCT_TEMPLATES[ptype]['format']}
Instant download after purchase."""

    def _gen_tags(self, ptype: str, niche: str) -> list:
        return [
            niche.lower().replace(" ", "-"),
            PRODUCT_TEMPLATES[ptype]['name'].lower().replace(" ", "-"),
            "ai",
            "digital-product",
            "2026",
            "template" if ptype == "notion_template" else "guide"
        ]

    def _save_product(self, product: dict):
        """保存产品JSON"""
        product_dir = OUTPUT_DIR / product["type"]
        product_dir.mkdir(exist_ok=True)
        filepath = product_dir / f"{product['id']}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(product, f, ensure_ascii=False, indent=2)


# ============================================================
# CLI
# ============================================================

def main():
    from dotenv import load_dotenv; load_dotenv()
    import argparse
    parser = argparse.ArgumentParser(description="数字产品工厂")
    parser.add_argument("--type", choices=list(PRODUCT_TEMPLATES.keys()), default="prompt_pack")
    parser.add_argument("--niche", type=str, default="AI marketing")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--mode", choices=["single", "batch"], default="batch")

    args = parser.parse_args()

    factory = DigitalProductFactory()

    if args.mode == "single":
        product = factory.create_product(args.type, args.niche)
        print(json.dumps(product, indent=2, ensure_ascii=False))
    else:
        niches = [
            "AI marketing", "coding automation", "social media content",
            "email marketing", "SEO optimization", "graphic design",
            "video production", "data analysis", "customer service",
            "project management", "personal productivity", "online education",
            "e-commerce automation", "financial planning", "health & fitness",
            "real estate marketing", "travel planning", "recipe creation",
            "language learning", "music production"
        ]
        factory.batch_create(niches, args.count)

if __name__ == "__main__":
    main()
