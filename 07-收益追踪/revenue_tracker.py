#!/usr/bin/env python3
"""
============================================================
📊 统一收益追踪看板
追踪: Gumroad/Payhip/LemonSqueezy/YouTube AdSense/AdSense SEO/联盟佣金
"""

import json, os, sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = Path(__file__).parent / "data"
for sub in ["销售统计", "渠道归因", "可视化看板"]:
    (DATA_DIR / ".." / sub).mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 统一收益追踪
# ============================================================

class UnifiedRevenueTracker:
    """统一收益追踪"""

    def __init__(self):
        self.revenue_file = DATA_DIR / "revenue_history.json"
        self.load()

    def load(self):
        if self.revenue_file.exists():
            with open(self.revenue_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "daily_records": [],
                "totals": {
                    "gumroad": 0.0,
                    "payhip": 0.0,
                    "lemonsqueezy": 0.0,
                    "youtube_adsense": 0.0,
                    "seo_adsense": 0.0,
                    "affiliate": 0.0
                }
            }

    def save(self):
        with open(self.revenue_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def record_sale(self, platform: str, product: str, amount: float, currency: str = "USD"):
        """记录一笔销售"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "platform": platform,
            "product": product,
            "amount": amount,
            "currency": currency,
            "amount_cny": round(amount * 7.2, 2)  # 汇率
        }
        self.data["daily_records"].append(record)

        # 更新总计数
        key = platform.lower().replace(" ", "_")
        if key in self.data["totals"]:
            self.data["totals"][key] += amount
        else:
            # 归类到数字产品
            self.data["totals"]["gumroad"] += amount

        self.save()
        return record

    def get_daily_summary(self, date: str = None) -> dict:
        """每日汇总"""
        date = date or datetime.now().strftime("%Y-%m-%d")
        day_records = [r for r in self.data["daily_records"] if r["date"] == date]

        return {
            "date": date,
            "total_sales": len(day_records),
            "total_revenue_usd": round(sum(r["amount"] for r in day_records), 2),
            "total_revenue_cny": round(sum(r.get("amount_cny", r["amount"] * 7.2) for r in day_records), 2),
            "by_platform": self._group_by(day_records, "platform"),
            "by_product": self._group_by(day_records, "product"),
        }

    def get_monthly_summary(self) -> dict:
        """月度汇总"""
        month = datetime.now().strftime("%Y-%m")
        month_records = [r for r in self.data["daily_records"] if r["date"].startswith(month)]

        return {
            "month": month,
            "days_with_sales": len(set(r["date"] for r in month_records)),
            "total_sales": len(month_records),
            "total_revenue_usd": round(sum(r["amount"] for r in month_records), 2),
            "total_revenue_cny": round(sum(r.get("amount_cny", r["amount"] * 7.2) for r in month_records), 2),
            "avg_daily_revenue_usd": round(sum(r["amount"] for r in month_records) / max(len(set(r["date"] for r in month_records)), 1), 2),
            "lifetime_total_usd": round(sum(self.data["totals"].values()), 2),
        }

    def _group_by(self, records: list, key: str) -> dict:
        groups = {}
        for r in records:
            k = r.get(key, "unknown")
            if k not in groups:
                groups[k] = {"count": 0, "revenue": 0.0}
            groups[k]["count"] += 1
            groups[k]["revenue"] += r["amount"]
        return groups

    def project_annual(self) -> dict:
        """年收入预估"""
        monthly = self.get_monthly_summary()
        daily_avg = monthly["avg_daily_revenue_usd"]

        return {
            "current_month_estimate": round(daily_avg * 30, 2),
            "annual_projection": round(daily_avg * 365, 2),
            "based_on_days": monthly["days_with_sales"],
        }


# ============================================================
# 渠道归因
# ============================================================

class AttributionTracker:
    """流量渠道归因"""

    CHANNELS = ["YouTube", "SEO/Google", "Twitter/X", "Reddit", "Pinterest", "Medium", "Direct", "Email"]

    def __init__(self):
        self.attribution_file = DATA_DIR / "attribution_data.json"
        self.load()

    def load(self):
        if self.attribution_file.exists():
            with open(self.attribution_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"visits": [], "conversions": []}

    def track_visit(self, channel: str, page: str, product_id: str = None):
        self.data["visits"].append({
            "timestamp": datetime.now().isoformat(),
            "channel": channel,
            "page": page,
            "product_id": product_id
        })

    def track_conversion(self, channel: str, product_id: str, amount: float):
        self.data["conversions"].append({
            "timestamp": datetime.now().isoformat(),
            "channel": channel,
            "product_id": product_id,
            "amount": amount
        })

    def get_channel_roi(self) -> dict:
        """各渠道ROI分析"""
        if not self.data["visits"]:
            return {}

        channel_stats = {}
        for ch in self.CHANNELS:
            visits = len([v for v in self.data["visits"] if v["channel"] == ch])
            conversions = len([c for c in self.data["conversions"] if c["channel"] == ch])
            revenue = sum(c["amount"] for c in self.data["conversions"] if c["channel"] == ch)

            channel_stats[ch] = {
                "visits": visits,
                "conversions": conversions,
                "conversion_rate": f"{(conversions / max(visits, 1)) * 100:.1f}%",
                "revenue": round(revenue, 2),
                "revenue_per_visit": round(revenue / max(visits, 1), 4)
            }

        return channel_stats


# ============================================================
# Streamlit可视化看板
# ============================================================

def generate_dashboard():
    """生成Streamlit看板代码"""
    dashboard_code = '''import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from revenue_tracker import UnifiedRevenueTracker

st.set_page_config(page_title="AI Money Machine — Revenue Dashboard", layout="wide")
st.title("💰 AI Money Machine — 收益驾驶舱")

tracker = UnifiedRevenueTracker()
monthly = tracker.get_monthly_summary()
annual = tracker.project_annual()

# KPI卡片
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("💵 本月收入(USD)", f"${monthly['total_revenue_usd']:.2f}")
with col2:
    st.metric("🇨🇳 本月收入(CNY)", f"¥{monthly['total_revenue_cny']:.2f}")
with col3:
    st.metric("📦 本月销售", f"{monthly['total_sales']} 单")
with col4:
    st.metric("📈 日均收入", f"${monthly['avg_daily_revenue_usd']:.2f}")
with col5:
    st.metric("🔮 年预估", f"${annual['annual_projection']:.2f}")

# 收入趋势
st.subheader("📈 收入趋势")
dates = list(set(r["date"] for r in tracker.data["daily_records"]))
dates.sort()
daily_amounts = []
for d in dates[-30:]:
    day_records = [r for r in tracker.data["daily_records"] if r["date"] == d]
    daily_amounts.append({"date": d, "revenue": sum(r["amount"] for r in day_records)})
if daily_amounts:
    df = pd.DataFrame(daily_amounts)
    fig = px.bar(df, x="date", y="revenue", title="每日收入 (USD)")
    st.plotly_chart(fig, use_container_width=True)

# 平台分布
st.subheader("🏪 收入来源分布")
totals = tracker.data["totals"]
platform_names = list(totals.keys())
platform_values = list(totals.values())
fig2 = px.pie(values=platform_values, names=platform_names, title="各平台收入占比")
st.plotly_chart(fig2, use_container_width=True)

st.caption(f"AI Money Machine v2.0 | 数据更新: {datetime.now().strftime("%Y-%m-%d %H:%M")}")
'''
    dashboard_path = PROJECT_ROOT / "07-收益追踪" / "可视化看板" / "dashboard.py"
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(dashboard_code)
    print(f"✅ 看板已生成: {dashboard_path}")
    return dashboard_path


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="收益追踪")
    parser.add_argument("--action", choices=["summary", "record", "dashboard", "attribution"], default="summary")
    parser.add_argument("--platform", type=str, default="gumroad")
    parser.add_argument("--product", type=str, default="Test Product")
    parser.add_argument("--amount", type=float, default=9.99)

    args = parser.parse_args()

    if args.action == "summary":
        tracker = UnifiedRevenueTracker()
        daily = tracker.get_daily_summary()
        monthly = tracker.get_monthly_summary()
        annual = tracker.project_annual()

        print(f"\n{'='*40}")
        print(f"💰 AI Money Machine 收益报告")
        print(f"{'='*40}")
        print(f"\n📅 今日: ${daily['total_revenue_usd']:.2f} ({daily['total_sales']}单)")
        print(f"\n📆 本月: ${monthly['total_revenue_usd']:.2f} ({monthly['total_sales']}单)")
        print(f"   日均: ${monthly['avg_daily_revenue_usd']:.2f}")
        print(f"\n📊 累计平台收入:")
        for platform, amount in tracker.data["totals"].items():
            if amount > 0:
                print(f"   {platform}: ${amount:.2f}")
        print(f"\n🔮 年度预估: ${annual['annual_projection']:.2f}")

    elif args.action == "record":
        tracker = UnifiedRevenueTracker()
        tracker.record_sale(args.platform, args.product, args.amount)
        print(f"✅ 已记录: {args.platform} — {args.product} — ${args.amount:.2f}")

    elif args.action == "dashboard":
        generate_dashboard()
        print("\n启动看板: streamlit run 07-收益追踪/可视化看板/dashboard.py")

    elif args.action == "attribution":
        attr = AttributionTracker()
        print(f"📊 渠道数据: {len(attr.data['visits'])} 次访问, {len(attr.data['conversions'])} 次转化")

if __name__ == "__main__":
    main()
