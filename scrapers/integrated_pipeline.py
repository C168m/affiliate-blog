#!/usr/bin/env python3
"""
Integrated Pipeline: Amazon Products + DeepSeek -> SEO Articles with Affiliate Links
"""
import json, os, time, hashlib
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"D:\AI-Money-Machine")
DATA_DIR = PROJECT_ROOT / r"06-流量引擎\联盟营销\data"
ARTICLES_DIR = PROJECT_ROOT / r"05-SEO内容站群\articles"
ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

# Load scraped Amazon products
products_file = DATA_DIR / "amazon_products_latest.json"
with open(products_file, "r", encoding="utf-8") as f:
    amazon_data = json.load(f)

# Tracking ID - replace with real one after registering Amazon Associates
TRACKING_ID = os.getenv("AMAZON_TRACKING_ID_US", "YOUR-TRACKING-ID-20")

def make_affiliate_link(asin):
    return "https://www.amazon.com/dp/{}/?tag={}".format(asin, TRACKING_ID)

def call_deepseek(system_prompt, user_prompt, api_key=None, max_tokens=2500):
    import requests
    api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        return ""
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": "Bearer {}".format(api_key), "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=90
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        print("  DeepSeek err ({}): {}".format(resp.status_code, resp.text[:200]))
        return ""
    except Exception as e:
        print("  DeepSeek fail: {}".format(e))
        return ""

def generate_articles():
    print("=" * 60)
    print("Integrated Pipeline: Amazon + DeepSeek -> SEO Articles")
    print("=" * 60)

    articles = []
    total_links = 0

    for query, products in amazon_data.items():
        if len(products) < 2:
            continue

        # Build product data for article
        product_list = []
        for p in products[:3]:
            link = make_affiliate_link(p["asin"])
            rating = p.get("rating", "N/A")
            price = p.get("price", "N/A").replace("\n", "")
            product_list.append({
                "asin": p["asin"],
                "price": price,
                "rating": rating,
                "affiliate_link": link,
            })
            total_links += 1

        keyword = "best {} 2026".format(query)
        print("\n  [ARTICLE] {}".format(keyword))

        # Build system prompt with real product data
        products_str = json.dumps(product_list, indent=2)
        system_prompt = """You are a professional Amazon affiliate content writer. 
Write a "Best of" listicle with REAL product data provided below.
Include the affiliate links naturally in the text.
Structure: H1 title, engaging intro, 3 product reviews with H2 headings, comparison table, verdict, FAQ, CTA.
Each product section MUST include: the product name from data, price, rating, and an affiliate link embedded naturally.
Word count: 1500+ words.
Tone: helpful, expert, honest (mention cons too)."""

        user_prompt = """Write a "Best {} 2026" listicle article.

Use these REAL Amazon products (include the affiliate links naturally):

{}

For each product, write a mini-review mentioning the price, rating, and embedding the affiliate link in the review text.
End with a comparison table and a final recommendation CTA with links.""".format(query.title(), products_str)

        content = call_deepseek(system_prompt, user_prompt, max_tokens=3000)

        article = {
            "id": "AFL_{}_{:04d}".format(datetime.now().strftime("%Y%m%d"), hash(query) % 10000),
            "keyword": keyword,
            "title": "Best {} 2026 — Top Picks & Reviews".format(query.title()),
            "slug": keyword.replace(" ", "-").lower()[:60],
            "content": content,
            "word_count_actual": len(content.split()) if content else 0,
            "affiliate_products": product_list,
            "affiliate_links_count": total_links,
            "amazon_tracking_id": TRACKING_ID,
            "status": "ai_generated" if content else "failed",
            "created_at": datetime.now().isoformat(),
        }

        slug = article["slug"]
        art_path = ARTICLES_DIR / "{}.json".format(slug)
        with open(art_path, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

        articles.append(article)
        preview = content[:120].replace("\n", " ") if content else "(no content)"
        print("  OK: {} | {} words | {} links".format(slug, article["word_count_actual"], total_links))
        print("  Preview: {}...".format(preview))

    # Save summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_articles": len(articles),
        "total_affiliate_links": sum(a["affiliate_links_count"] for a in articles),
        "articles": [{"slug": a["slug"], "title": a["title"], "links": a["affiliate_links_count"]} for a in articles],
    }
    summary_path = ARTICLES_DIR / "affiliate_summary_{}.json".format(datetime.now().strftime("%Y%m%d_%H%M"))
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("Pipeline complete: {} articles, {} affiliate links".format(len(articles), summary["total_affiliate_links"]))
    print("Summary: {}".format(summary_path))
    return articles, summary

if __name__ == "__main__":
    from dotenv import load_dotenv; load_dotenv()
    generate_articles()
