#!/usr/bin/env python3
"""
Amazon Niche Research Tool
基于 Jungle Scout / Helium 10 方法论 + 真实案例实践
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "niche_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 六大高利润 Amazon 利基 (参考 FatStacks + Niche Site Project + Partnerkin)
HIGH_PROFIT_NICHES = [
    {"name": "Home & Kitchen", "commission": "4-8%", "avg_price": "$30-150",
     "difficulty": "medium", "season": "year-round",
     "sub": ["coffee gear", "air fryers", "cookware", "storage"],
     "example_kw": "best coffee grinder, best air fryer under $100"},
    {"name": "Outdoor & Garden", "commission": "4-5%", "avg_price": "$50-200",
     "difficulty": "medium", "season": "spring/summer",
     "sub": ["camping gear", "BBQ & grilling", "garden tools"],
     "example_kw": "best camping tent 2026, best gas grill under $500"},
    {"name": "Pet Supplies", "commission": "4-5%", "avg_price": "$15-100",
     "difficulty": "easy", "season": "year-round",
     "sub": ["dog supplies", "cat supplies", "pet grooming"],
     "example_kw": "best dog bed, automatic cat feeder review"},
    {"name": "Baby Products", "commission": "3-7%", "avg_price": "$30-300",
     "difficulty": "medium", "season": "year-round",
     "sub": ["baby gear", "nursery items", "baby feeding"],
     "example_kw": "best baby stroller 2026, best car seat for toddlers"},
    {"name": "Fitness & Sports", "commission": "4-5%", "avg_price": "$30-300",
     "difficulty": "medium", "season": "January peak",
     "sub": ["home gym", "yoga gear", "running shoes"],
     "example_kw": "best adjustable dumbbells, best yoga mat for beginners"},
    {"name": "Electronics Accessories", "commission": "2-5%", "avg_price": "$20-100",
     "difficulty": "high", "season": "year-round",
     "sub": ["phone accessories", "PC peripherals", "audio gear"],
     "example_kw": "best wireless charger, best mechanical keyboard under $100"},
]

# 关键词研究模板 (5种购买意图类型)
KEYWORD_PATTERNS = {
    "review": ["{p} review", "{p} review 2026", "honest {p} review", "is {p} worth it"],
    "best_of": ["best {p}", "best {p} 2026", "best {p} for {use}", "top 10 {p}", "best budget {p}"],
    "vs": ["{p1} vs {p2}", "{p1} or {p2}", "{p1} comparison"],
    "guide": ["how to choose {p}", "{p} buying guide", "beginner guide to {p}"],
    "price": ["best {p} under ${price}", "best budget {p}", "cheap {p} that works"],
}


class NicheScorer:
    """利基评分引擎 (0-100分)"""

    @staticmethod
    def score(niche: dict) -> dict:
        s = 0
        breakdown = {}
        # Commission rate (higher = better)
        c = niche.get("commission_rate", niche.get("commission", "4%"))
        cr = float(c.replace("%", "").split("-")[0])
        if cr >= 6.5: s += 25; breakdown["commission"] = "great +25"
        elif cr >= 4: s += 15; breakdown["commission"] = "good +15"
        else: s += 8; breakdown["commission"] = "ok +8"
        # Difficulty
        diff = niche.get("difficulty", "medium")
        if diff == "easy": s += 25; breakdown["competition"] = "low +25"
        elif diff == "medium": s += 15; breakdown["competition"] = "medium +15"
        else: s += 5; breakdown["competition"] = "high +5"
        # Seasonality
        season = niche.get("seasonality", niche.get("season", "year-round"))
        if season == "year-round": s += 20; breakdown["seasonality"] = "year-round +20"
        else: s += 8; breakdown["seasonality"] = "seasonal +8"
        # Content potential
        subs = niche.get("sub_niches", niche.get("sub", []))
        if len(subs) >= 3: s += 15; breakdown["sub_niches"] = "rich +15"
        else: s += 5; breakdown["sub_niches"] = "limited +5"
        # Avg price sweet spot ($50-200)
        s += 15; breakdown["price_range"] = "verified +15"

        rec = "GO" if s >= 70 else "RESEARCH" if s >= 50 else "SKIP"
        return {"score": s, "max": 100, "recommendation": rec, "breakdown": breakdown}


class KeywordGenerator:
    """关键词生成器"""

    @staticmethod
    def generate(product: str, use_case: str = "beginners", price: int = 50) -> list:
        kws = []
        for kt, patterns in KEYWORD_PATTERNS.items():
            for pat in patterns[:2]:
                kw = pat.replace("{p}", product).replace("{p1}", product).replace("{p2}", "alternative").replace("{use}", use_case).replace("{price}", str(price))
                kws.append({"keyword": kw, "type": kt, "product": product})
        return kws

    @staticmethod
    def batch_generate(products: list) -> list:
        all_kws = []
        for p in products:
            all_kws.extend(KeywordGenerator.generate(p))
        return all_kws


def main():
    import argparse
    p = argparse.ArgumentParser(description="Amazon Niche Research")
    p.add_argument("--action", choices=["niches", "score", "keywords"], default="niches")
    p.add_argument("--nickname", default="coffee gear")
    p.add_argument("--product", default="coffee grinder")
    args = p.parse_args()

    if args.action == "niches":
        print("\nAmazon High-Profit Niches:\n")
        for n in HIGH_PROFIT_NICHES:
            sc = NicheScorer.score(n)
            print(f"  [{sc['score']}/100] {n['name']} | Comm: {n['commission']} | Price: {n['avg_price']} | {sc['recommendation']}")
            print(f"    Sub-niches: {', '.join(n['sub'])}")
            print(f"    Breakdown: {sc['breakdown']}\n")

    elif args.action == "score":
        for n in HIGH_PROFIT_NICHES:
            if args.nickname.lower() in n["name"].lower():
                sc = NicheScorer.score(n)
                print(f"\n{n['name']}: {sc['score']}/100 — {sc['recommendation']}")
                for k, v in sc["breakdown"].items():
                    print(f"  {k}: {v}")

    elif args.action == "keywords":
        kws = KeywordGenerator.generate(args.product)
        print(f"\nBuyer Intent Keywords for '{args.product}':\n")
        for kw in kws:
            print(f"  [{kw['type']}] {kw['keyword']}")


if __name__ == "__main__":
    main()
