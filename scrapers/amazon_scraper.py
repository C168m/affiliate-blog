#!/usr/bin/env python3
"""
Amazon Product Scraper - 从 Amazon.com 采集真实商品数据
使用 Playwright 真实浏览器，绕过基础反爬
"""
import json, time, re, random
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

DATA_DIR = Path(r"D:\AI-Money-Machine\06-流量引擎\联盟营销\data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

PRODUCTS_TO_SCRAPE = [
    "mechanical keyboard",
    "wireless mouse",
    "webcam 1080p",
    "USB hub",
    "monitor stand",
    "bluetooth earbuds",
    "wireless charger",
    "phone case iPhone",
]

class AmazonScraper:
    def __init__(self):
        self.results = []

    def scrape_product(self, context, query, max_results=5):
        """Search Amazon for a product and extract ASIN+price+rating"""
        page = context.new_page()
        results = []
        try:
            url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
            print(f"  [SEARCH] {query}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 4))

            items = page.query_selector_all('div[data-component-type="s-search-result"]')
            print(f"    Found {len(items)} results")

            count = 0
            for item in items:
                if count >= max_results:
                    break
                try:
                    asin = item.get_attribute("data-asin")
                    if not asin or asin == "":
                        continue

                    title_el = item.query_selector("h2 a span")
                    title = title_el.inner_text().strip() if title_el else "N/A"

                    price_whole = item.query_selector(".a-price-whole")
                    price_fraction = item.query_selector(".a-price-fraction")
                    price = "N/A"
                    if price_whole:
                        pw = price_whole.inner_text().strip()
                        pf = price_fraction.inner_text().strip() if price_fraction else "00"
                        price = "${}.{}".format(pw, pf)

                    rating_el = item.query_selector(".a-icon-star-small .a-icon-alt, .a-icon-alt")
                    rating = rating_el.inner_text().split(" ")[0] if rating_el else "N/A"

                    reviews_el = item.query_selector("span.a-size-base.s-underline-text")
                    reviews = reviews_el.inner_text().strip() if reviews_el else "N/A"

                    img_el = item.query_selector("img.s-image")
                    img = img_el.get_attribute("src") if img_el else "N/A"

                    result = {
                        "asin": asin,
                        "title": title[:120],
                        "price": price,
                        "rating": rating,
                        "reviews": reviews,
                        "image": img,
                        "query": query,
                        "scraped_at": datetime.now().isoformat(),
                    }
                    results.append(result)
                    print("    OK [{}] {}... | {} | stars={} reviews={}".format(asin, title[:50], price, rating, reviews))
                    count += 1
                except Exception as e:
                    print("    SKIP parse err: {}".format(e))
                    continue
        except Exception as e:
            print("    FAIL search: {}".format(e))
        finally:
            page.close()
        return results

    def scrape_all(self):
        """Scrape all target products"""
        all_data = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )

            for query in PRODUCTS_TO_SCRAPE:
                results = self.scrape_product(context, query, max_results=5)
                all_data[query] = results
                time.sleep(random.uniform(3, 6))

            browser.close()

        total = sum(len(v) for v in all_data.values())
        out_path = DATA_DIR / "amazon_products_{}.json".format(datetime.now().strftime('%Y%m%d_%H%M'))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        latest_path = DATA_DIR / "amazon_products_latest.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print("\n" + "="*50)
        print("OK: Scraped {} products across {} categories".format(total, len(all_data)))
        print("Saved: {}".format(out_path))
        return all_data

if __name__ == "__main__":
    scraper = AmazonScraper()
    scraper.scrape_all()
