#!/usr/bin/env python3
"""
AI Money Machine - Master Automation Controller v2.0
Unified scheduler: Amazon scraping -> Product factory -> SEO articles -> Blog rebuild
"""
import json, os, sys, time, subprocess
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"D:\AI-Money-Machine")

class MasterController:
    def __init__(self):
        self.log_file = PROJECT_ROOT / "automation_log.jsonl"

    def log(self, task, status, detail=""):
        entry = {"time": datetime.now().isoformat(), "task": task, "status": status, "detail": detail}
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        icon = {"ok":"OK","fail":"FAIL","skip":"SKIP"}.get(status, "??")
        print("  [{}] {}: {}".format(icon, task, detail))

    def run_amazon_scraper(self):
        """Step 1: Scrape real Amazon products"""
        print("\n" + "="*50)
        print("Step 1: Amazon Product Scraping")
        print("="*50)
        script = PROJECT_ROOT / "scrapers/amazon_scraper.py"
        if not script.exists():
            self.log("amazon_scrape", "skip", "scraper script missing")
            return False
        try:
            result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=120, cwd=str(PROJECT_ROOT))
            if result.returncode == 0:
                self.log("amazon_scrape", "ok", "scraped successfully")
                return True
            else:
                self.log("amazon_scrape", "fail", result.stderr[-200:])
                return False
        except Exception as e:
            self.log("amazon_scrape", "fail", str(e)[:100])
            return False

    def run_product_factory(self, count=5):
        """Step 2: Generate digital products"""
        print("\n" + "="*50)
        print("Step 2: Product Factory - {} products".format(count))
        print("="*50)
        script = PROJECT_ROOT / "01-数字产品工厂/product_factory.py"
        if not script.exists():
            self.log("product_factory", "skip", "script missing")
            return False
        try:
            result = subprocess.run(
                [sys.executable, str(script), "--mode", "batch", "--count", str(count)],
                capture_output=True, text=True, timeout=180, cwd=str(script.parent)
            )
            if result.returncode == 0:
                self.log("product_factory", "ok", "{} products".format(count))
                return True
            else:
                self.log("product_factory", "fail", result.stderr[-200:])
                return False
        except Exception as e:
            self.log("product_factory", "fail", str(e)[:100])
            return False

    def run_seo_factory(self, count=5):
        """Step 3: Generate SEO articles with Amazon links"""
        print("\n" + "="*50)
        print("Step 3: SEO Articles + Amazon Links - {} articles".format(count))
        print("="*50)
        script = PROJECT_ROOT / "scrapers/integrated_pipeline.py"
        if not script.exists():
            self.log("seo_factory", "skip", "integrated pipeline missing")
            return False
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=600, cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0:
                self.log("seo_factory", "ok", "{} articles".format(count))
                return True
            else:
                self.log("seo_factory", "fail", result.stderr[-200:])
                return False
        except Exception as e:
            self.log("seo_factory", "fail", str(e)[:100])
            return False

    def run_blog_builder(self):
        """Step 4: Rebuild static blog"""
        print("\n" + "="*50)
        print("Step 4: Blog Rebuild")
        print("="*50)
        script = PROJECT_ROOT / "scrapers/blog_builder.py"
        if not script.exists():
            self.log("blog_build", "skip", "builder missing")
            return False
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0:
                self.log("blog_build", "ok", "blog rebuilt")
                return True
            else:
                self.log("blog_build", "fail", result.stderr[-200:])
                return False
        except Exception as e:
            self.log("blog_build", "fail", str(e)[:100])
            return False

    def full_cycle(self, products=5, articles=5):
        """Run complete automation cycle"""
        print("\n" + "#"*60)
        print("# AI Money Machine v2.0 — Full Automation Cycle")
        print("# Started: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("#"*60)

        start = time.time()
        results = {}

        # Step 1: Scrape Amazon
        results["amazon"] = self.run_amazon_scraper()

        # Step 2: Products
        results["products"] = self.run_product_factory(products)

        # Step 3: SEO Articles
        results["articles"] = self.run_seo_factory(articles)

        # Step 4: Blog
        results["blog"] = self.run_blog_builder()

        elapsed = time.time() - start
        print("\n" + "#"*60)
        print("# Cycle Complete in {:.0f}s".format(elapsed))
        print("# Results: {}".format(json.dumps(results)))
        print("#"*60)
        return results

def main():
    from dotenv import load_dotenv; load_dotenv()

    import argparse
    p = argparse.ArgumentParser(description="AI Money Machine Master Controller")
    p.add_argument("--mode", choices=["full","scrape","products","articles","blog","loop"], default="full")
    p.add_argument("--products", type=int, default=5)
    p.add_argument("--articles", type=int, default=5)
    p.add_argument("--interval", type=int, default=3600, help="Loop interval in seconds (default 1hr)")
    args = p.parse_args()

    ctrl = MasterController()

    if args.mode == "full":
        ctrl.full_cycle(args.products, args.articles)

    elif args.mode == "scrape":
        ctrl.run_amazon_scraper()

    elif args.mode == "products":
        ctrl.run_product_factory(args.products)

    elif args.mode == "articles":
        ctrl.run_seo_factory(args.articles)

    elif args.mode == "blog":
        ctrl.run_blog_builder()

    elif args.mode == "loop":
        print("="*50)
        print("AI Money Machine — Auto Loop Mode")
        print("Interval: {}s ({}min)".format(args.interval, args.interval/60))
        print("Ctrl+C to stop")
        print("="*50)
        cycle = 0
        while True:
            cycle += 1
            print("\n>>> Cycle #{} <<<".format(cycle))
            try:
                ctrl.full_cycle(args.products, args.articles)
            except Exception as e:
                print("Cycle error: {}".format(e))
                ctrl.log("cycle", "fail", str(e)[:100])
            print("Sleeping {}s...".format(args.interval))
            time.sleep(args.interval)

if __name__ == "__main__":
    main()
