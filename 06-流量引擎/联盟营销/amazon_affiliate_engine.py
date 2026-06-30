#!/usr/bin/env python3
"""
Amazon Affiliate Engine - Blog to Amazon Traffic Core
Based on: FatStacks $2K/mo, Partnerkin $19K/mo, Niche Site Project
"""

import json, os, sys, re, hashlib
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = Path(__file__).parent
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Amazon Niche Database - based on real case studies
# ============================================================

AMAZON_NICHES = {
    "home_kitchen": {
        "name": "Home & Kitchen", "commission_rate": "4-8%", "avg_price": "$30-150",
        "buyer_intent": "high",
        "case_reference": "XSquareSEO Case Study - best off-site SEO",
        "sub_niches": [
            {"name": "Coffee & Espresso", "products": ["espresso machine", "coffee grinder", "milk frother", "pour over kit", "coffee scale"], "seasonality": "year-round"},
            {"name": "Air Fryers & Small Appliances", "products": ["air fryer", "instant pot", "stand mixer", "blender", "food processor"], "seasonality": "Q4 peak"},
            {"name": "Cookware Sets", "products": ["stainless steel cookware", "cast iron skillet", "non-stick pan set", "dutch oven", "knife set"], "seasonality": "Q4 peak"},
            {"name": "Home Organization", "products": ["closet organizer", "storage bins", "shelf liner", "pantry organizer", "under bed storage"], "seasonality": "year-round"},
        ]
    },
    "outdoor_garden": {
        "name": "Outdoor & Garden", "commission_rate": "4-5%", "avg_price": "$50-200",
        "buyer_intent": "high",
        "case_reference": "Niche Site Project - Spencer outdoor niche",
        "sub_niches": [
            {"name": "Camping Gear", "products": ["camping tent", "sleeping bag", "camping stove", "hiking backpack", "headlamp"], "seasonality": "spring/summer"},
            {"name": "Grilling & BBQ", "products": ["gas grill", "charcoal grill", "smoker", "grill tools set", "meat thermometer"], "seasonality": "summer peak"},
            {"name": "Garden Tools", "products": ["electric lawn mower", "string trimmer", "pruning shears", "garden hose", "sprinkler"], "seasonality": "spring/summer"},
        ]
    },
    "pets": {
        "name": "Pet Supplies", "commission_rate": "4-5%", "avg_price": "$15-100",
        "buyer_intent": "high",
        "case_reference": "wanghuiblog - niche down for easier success",
        "sub_niches": [
            {"name": "Dog Supplies", "products": ["dog bed", "dog harness", "dog toys", "dog food container", "dog nail clippers"], "seasonality": "year-round"},
            {"name": "Cat Supplies", "products": ["cat tree", "cat litter box", "cat scratching post", "automatic cat feeder", "cat water fountain"], "seasonality": "year-round"},
        ]
    },
    "baby": {
        "name": "Baby Products", "commission_rate": "3-7%", "avg_price": "$30-300",
        "buyer_intent": "very_high",
        "case_reference": "FatStacks - high conversion, high ticket",
        "sub_niches": [
            {"name": "Baby Gear", "products": ["baby stroller", "car seat", "baby carrier", "high chair", "baby monitor"], "seasonality": "year-round"},
            {"name": "Nursery", "products": ["crib mattress", "changing pad", "baby sound machine", "blackout curtains", "nursery humidifier"], "seasonality": "year-round"},
        ]
    },
    "fitness": {
        "name": "Fitness & Sports", "commission_rate": "4-5%", "avg_price": "$30-300",
        "buyer_intent": "high",
        "case_reference": "Great for Pinterest visual shareability",
        "sub_niches": [
            {"name": "Home Gym", "products": ["adjustable dumbbells", "resistance bands", "yoga mat", "exercise bike", "pull up bar"], "seasonality": "January peak"},
            {"name": "Running Gear", "products": ["running shoes", "running watch", "hydration vest", "compression socks", "running belt"], "seasonality": "spring/fall"},
        ]
    },
    "electronics": {
        "name": "Electronics Accessories", "commission_rate": "2-5%", "avg_price": "$20-100",
        "buyer_intent": "medium_high",
        "case_reference": "",
        "sub_niches": [
            {"name": "Phone Accessories", "products": ["wireless charger", "phone case", "screen protector", "power bank", "bluetooth earbuds"], "seasonality": "year-round"},
            {"name": "Computer Peripherals", "products": ["mechanical keyboard", "wireless mouse", "webcam", "USB hub", "monitor stand"], "seasonality": "year-round"},
        ]
    },
}

# ============================================================
# Buyer Intent Keywords Matrix
# ============================================================

BUYER_KEYWORDS = {
    "review": {
        "patterns": ["{product} review", "{product} review 2026", "honest {product} review", "is {product} worth it"],
        "intent": "purchase decision", "amazon_ctr": "5-15%", "article_type": "review",
    },
    "best_of": {
        "patterns": ["best {product}", "best {product} 2026", "best {product} for {use_case}", "top 10 {product}", "best budget {product}"],
        "intent": "buying intent", "amazon_ctr": "10-25%", "article_type": "listicle",
    },
    "vs": {
        "patterns": ["{product_a} vs {product_b}", "{product_a} or {product_b}", "{product_a} comparison"],
        "intent": "comparison", "amazon_ctr": "15-30%", "article_type": "comparison",
    },
    "guide": {
        "patterns": ["how to choose {product}", "{product} buying guide", "what to look for in {product}", "beginner guide to {product}"],
        "intent": "research", "amazon_ctr": "8-15%", "article_type": "guide",
    },
    "under_price": {
        "patterns": ["best {product} under ${price}", "best budget {product}", "cheap {product} that works"],
        "intent": "price-sensitive buyer", "amazon_ctr": "15-25%", "article_type": "listicle",
    },
}


# ============================================================
# Amazon Link Manager
# ============================================================

class AmazonLinkManager:
    """Amazon Associates affiliate link generation & tracking"""

    LOCALES = {
        "com": {"domain": "amazon.com", "env": "AMAZON_TRACKING_ID_US"},
        "co.uk": {"domain": "amazon.co.uk", "env": "AMAZON_TRACKING_ID_UK"},
        "de": {"domain": "amazon.de", "env": "AMAZON_TRACKING_ID_DE"},
        "ca": {"domain": "amazon.ca", "env": "AMAZON_TRACKING_ID_CA"},
    }

    def __init__(self, tracking_id=None, locale="com"):
        self.locale = locale
        self.domain = self.LOCALES[locale]["domain"]
        self.tracking_id = tracking_id or os.getenv(self.LOCALES[locale]["env"], "YOUR-TRACKING-ID-20")
        self.links_db = DATA_DIR / "amazon_links.json"
        self.clicks_db = DATA_DIR / "amazon_clicks.jsonl"
        self.load_db()

    def load_db(self):
        if self.links_db.exists():
            with open(self.links_db, "r", encoding="utf-8") as f:
                self.links = json.load(f)
        else:
            self.links = {}

    def save_db(self):
        with open(self.links_db, "w", encoding="utf-8") as f:
            json.dump(self.links, f, ensure_ascii=False, indent=2)

    def generate_link(self, asin, link_text=None, sub_id=None):
        """Generate tracked Amazon affiliate link"""
        base = f"https://www.{self.domain}/dp/{asin}"
        params = f"?tag={self.tracking_id}"
        if sub_id:
            params += f"&linkCode=ll1&linkId={sub_id}"
        full_url = f"{base}{params}"
        raw = f"{asin}:{sub_id or ''}:{datetime.now().isoformat()}"
        link_id = hashlib.md5(raw.encode()).hexdigest()[:12]

        link_data = {
            "id": link_id, "asin": asin, "locale": self.locale,
            "url": full_url, "link_text": link_text, "sub_id": sub_id,
            "created_at": datetime.now().isoformat(),
            "stats": {"clicks": 0, "conversions_est": 0, "earnings_est": 0.0},
        }
        self.links[link_id] = link_data
        self.save_db()
        return link_data

    def site_stripe_link(self, asin):
        """Generate SiteStripe-style short link"""
        return f"https://www.{self.domain}/dp/{asin}/?tag={self.tracking_id}"

    def image_link(self, asin, size="medium"):
        """Get Amazon product image URL for blog embedding"""
        base = "https://ws-na.amazon-adsystem.com/widgets/q"
        return (f"{base}?_encoding=UTF8&ASIN={asin}"
                f"&Format=_{size}&ID=AsinImage&MarketPlace=US"
                f"&ServiceVersion=20070822&WS=1&tag={self.tracking_id}")

    def log_click(self, link_id, source_page=None, source_domain=None):
        """Log a click event"""
        if link_id in self.links:
            self.links[link_id]["stats"]["clicks"] += 1
            self.save_db()
        entry = {"timestamp": datetime.now().isoformat(), "link_id": link_id,
                 "source_page": source_page, "source_domain": source_domain}
        with open(self.clicks_db, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def bulk_generate(self, products, article_slug):
        """Generate all Amazon links for one article"""
        results = []
        for i, p in enumerate(products):
            sid = hashlib.md5(f"{article_slug}:pos{i}".encode()).hexdigest()[:8]
            results.append(self.generate_link(p["asin"], p["name"], sid))
        return results

# ============================================================
# Amazon Product Research Engine
# ============================================================

class AmazonProductResearch:
    """Amazon niche product research (Jungle Scout / Helium 10 style)"""

    SCORING = {
        "price_50_200": 30, "price_20_50": 15, "price_200_plus": 10,
        "reviews_500_plus": 25, "reviews_100_500": 15,
        "non_seasonal": 15,
        "seo_low_comp": 20, "seo_med_comp": 10,
        "pinterest": 5, "content_opp": 10,
    }

    def evaluate(self, niche_name, sub_niche):
        """Score a niche 0-100. >=60 recommended."""
        score = 0
        br = {}

        avg_price = sub_niche.get("avg_price_est", 70)
        if 50 <= avg_price <= 200:
            score += self.SCORING["price_50_200"]; br["price"] = "good +30"
        elif 20 <= avg_price < 50:
            score += self.SCORING["price_20_50"]; br["price"] = "ok +15"
        else:
            score += self.SCORING["price_200_plus"]; br["price"] = "acceptable +10"

        season = sub_niche.get("seasonality", "year-round")
        if season == "year-round":
            score += self.SCORING["non_seasonal"]; br["seasonality"] = "year-round +15"
        else:
            br["seasonality"] = f"seasonal ({season})"

        score += self.SCORING["seo_low_comp"]; br["seo"] = "assumed low +20"
        score += self.SCORING["content_opp"]; br["content"] = "good +10"

        visual = ["fitness", "home_kitchen", "outdoor", "pets"]
        if any(c in niche_name.lower() for c in visual):
            score += self.SCORING["pinterest"]; br["pinterest"] = "high +5"

        rec = "GO" if score >= 60 else "RESEARCH" if score >= 45 else "SKIP"
        return {"niche": niche_name, "sub_niche": sub_niche["name"],
                "score": score, "recommendation": rec, "breakdown": br,
                "revenue_est": self._rev_est(score)}

    def _rev_est(self, score):
        if score >= 70: r = "$500-$5,000+/mo (6-12mo)"
        elif score >= 55: r = "$200-$2,000/mo (6-12mo)"
        else: r = "$50-$500/mo"
        return {"range": r, "basis": "100 articles, 5K-50K traffic, CTR 2%, CVR 1%, avg $50"}

    def keyword_ideas(self, product, count=10):
        """Generate buyer-intent keywords for a product"""
        kws = []
        for kt, kd in BUYER_KEYWORDS.items():
            for pat in kd["patterns"][:2]:
                kw = pat.replace("{product}", product).replace("{price}", "50").replace("{use_case}", "beginners")
                kws.append({"keyword": kw, "type": kt, "intent": kd["intent"],
                           "amazon_ctr": kd["amazon_ctr"], "article_type": kd["article_type"]})
        return kws[:count]


# ============================================================
# Content Strategy Engine
# ============================================================

class ContentStrategyEngine:
    """Amazon niche site content strategy (FatStacks + Partnerkin best practices)"""

    MIX = {"info": 0.40, "commercial": 0.50, "link_bait": 0.10}

    TIMELINE = [
        (1, 10, "info articles + long-tail keywords", 0),
        (2, 15, "start commercial + continue info", 0),
        (3, 20, "scale commercial + begin backlinks", 5),
        (4, 25, "fill content gaps + guest posts", 10),
        (5, 25, "update + strengthen backlinks", 10),
        (6, 15, "refresh old content + maintain", 5),
    ]

    BEST_PRACTICES = {
        "links_per_article": "5-15",
        "disclosure": "As an Amazon Associate I earn from qualifying purchases.",
        "placement": ["first 300 words (1-2 links)", "natural mentions", "summary CTA (2-3 links)"],
        "table_links": "Every product in comparison table gets an affiliate link",
    }

    def content_plan(self, niche, sub_niche, months=6):
        """Generate 6-month content plan"""
        plan = {"niche": niche["name"], "sub_niche": sub_niche["name"],
                "products": sub_niche["products"], "timeline": [],
                "total_articles": 0, "total_links": 0}
        for m, arts, focus, links in self.TIMELINE:
            month_kw = []
            for p in sub_niche["products"][:3]:
                if "refresh" not in focus:
                    month_kw.append(f"best {p} 2026")
                    month_kw.append(f"{p} review")
            plan["timeline"].append({"month": m, "articles": arts,
                "focus": focus, "links": links, "keywords": month_kw[:arts]})
            plan["total_articles"] += arts
            plan["total_links"] += links
        plan["projection"] = {"m3": "$100-500", "m6": "$500-2,000", "m12": "$1,000-4,000"}
        return plan

# ============================================================
# Pinterest to Amazon Traffic Strategy
# ============================================================

class PinterestAmazonStrategy:
    """Pinterest traffic to Amazon (Christy case: 20% traffic, $5K/mo)"""

    PIN_TYPES = {
        "review": ("The Best {product} of 2026", "Looking for the best {product}? See our top picks ->"),
        "listicle": ("10 Best {product} That Work in 2026", "Don't buy until you see this list! ->"),
        "guide": ("{product} Buying Guide", "Confused about {product}? Our guide breaks it down."),
    }

    def pin_strategy(self, article_url, product, count=5):
        """Generate Pinterest pin strategy for an article"""
        pins = []
        for pt, (tpl, dtpl) in self.PIN_TYPES.items():
            for i in range(min(2, count // 3 + 1)):
                pins.append({"type": pt,
                    "title": tpl.replace("{product}", product),
                    "desc": dtpl.replace("{product}", product),
                    "url": article_url,
                    "board": f"{product.title()} Reviews"})
        return pins[:count]


# ============================================================
# Unified Amazon Affiliate Engine
# ============================================================

class AmazonAffiliateEngine:
    """Unified Amazon affiliate engine"""

    def __init__(self, tracking_id=None):
        self.links = AmazonLinkManager(tracking_id)
        self.research = AmazonProductResearch()
        self.strategy = ContentStrategyEngine()
        self.pinterest = PinterestAmazonStrategy()

    def explore_niches(self):
        """Score all niches and rank them"""
        results = []
        for nk, nd in AMAZON_NICHES.items():
            for sub in nd["sub_niches"]:
                results.append(self.research.evaluate(nk, sub))
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def build_plan(self, niche_key, sub_idx=0):
        """Build full operation plan for a niche"""
        if niche_key not in AMAZON_NICHES:
            return {'error': f'Niche {niche_key!r} not found'}
        nd = AMAZON_NICHES[niche_key]
        sn = nd["sub_niches"][sub_idx]

        plan = {
            "overview": {"category": nd["name"], "sub": sn["name"],
                "commission": nd["commission_rate"], "avg_price": nd["avg_price"]},
            "evaluation": self.research.evaluate(niche_key, sn),
            "content": self.strategy.content_plan(nd, sn),
            "products": [],
            "keywords": self.research.keyword_ideas(sn["products"][0], 8),
        }
        for p in sn["products"]:
            link = self.links.generate_link("B0XXXXXXX", p)
            plan["products"].append({"name": p, "link_tpl": link["url"]})

        slug = sn["products"][0].replace(" ", "-")
        article_url = f"https://yourblog.com/best-{slug}-2026"
        plan["pinterest"] = self.pinterest.pin_strategy(article_url, sn["products"][0])
        return plan


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    p = argparse.ArgumentParser(description="Amazon Affiliate Engine")
    p.add_argument("--action", choices=["niches","plan","keywords","links","test"], default="niches")
    p.add_argument("--niche", default="home_kitchen")
    p.add_argument("--sub", type=int, default=0)
    p.add_argument("--tracking-id", default=None)
    p.add_argument("--product", default="espresso machine")
    args = p.parse_args()
    engine = AmazonAffiliateEngine(args.tracking_id)

    if args.action == "niches":
        print("\n" + "="*60)
        print("Amazon Niche Evaluation (based on FatStacks + Partnerkin case studies)")
        print("="*60)
        for n in engine.explore_niches():
            print(f"  [{n['score']}/100] {n['sub_niche']} ({n['niche']}) -- {n['recommendation']} | {n['revenue_est']['range']}")

    elif args.action == "plan":
        pl = engine.build_plan(args.niche, args.sub)
        if "error" in pl:
            print(f"ERR: {pl['error']}")
            return
        print(f"\n{pl['overview']['category']} > {pl['overview']['sub']}")
        print(f"Commission: {pl['overview']['commission']} | Avg Price: {pl['overview']['avg_price']}")
        print(f"Score: {pl['evaluation']['score']}/100 -- {pl['evaluation']['recommendation']}")
        print(f"\n{pl['content']['total_articles']} articles over 6 months:")
        for t in pl["content"]["timeline"]:
            print(f"  M{t['month']}: {t['articles']} articles | {t['focus']} | {t['links']} backlinks")
        print(f"\nRevenue Projection:")
        for k, v in pl["content"]["projection"].items():
            print(f"  {k}: {v}")

    elif args.action == "keywords":
        print(f"\nBuyer-Intent Keywords for: {args.product}\n")
        for kw in engine.research.keyword_ideas(args.product):
            print(f"  [{kw['type']:12}] {kw['keyword']} | Amazon CTR ~{kw['amazon_ctr']}")

    elif args.action == "links":
        print(f"\nTracking ID: {engine.links.tracking_id}")
        print(f"Stored links: {len(engine.links.links)}")
        for lid, ld in list(engine.links.links.items())[:5]:
            print(f"  [{ld['asin']}] {ld['link_text'] or 'N/A'} -- {ld['stats']['clicks']} clicks")

    elif args.action == "test":
        lm = engine.links
        link = lm.generate_link("B09J1QPFZN", "Sample Coffee Grinder", "test_pos1")
        print(f"Link: {link['url'][:70]}...")
        print(f"SiteStripe: {lm.site_stripe_link('B09J1QPFZN')}")
        print(f"Image: {lm.image_link('B09J1QPFZN')}")
        print(f"\nProduct Keywords for espresso machine:")
        for kw in engine.research.keyword_ideas("espresso machine", 5):
            print(f"  {kw['keyword']}")


if __name__ == "__main__":
    main()