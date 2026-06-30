#!/usr/bin/env python3
"""
============================================================
⏰ 统一调度器 — AI Money Machine 全自动运营中枢
每日: 生产产品 → 上架 → 推广 → 数据追踪
============================================================
"""

import json, os, sys, io, time, subprocess
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_DIR = PROJECT_ROOT / 'scheduler' / 'daily-pipeline' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 每日流水线定义
# ============================================================
DAILY_PIPELINE = [
    {
        'time': '08:00',
        'name': '系统自检',
        'module': 'monitor',
        'command': 'python engine/ai-copilot/health_check.py',
        'desc': '检查API/网络/店铺状态'
    },
    {
        'time': '08:15',
        'name': '产品生产',
        'module': 'product-engine',
        'command': 'python engine/product-engine/produce.py --count 3',
        'desc': 'DeepSeek批量生产3个数字产品'
    },
    {
        'time': '08:30',
        'name': '文件处理',
        'module': 'file-processor',
        'command': 'python tools/file-processor/process.py',
        'desc': '格式化产品文件→PDF/Markdown'
    },
    {
        'time': '09:00',
        'name': 'Gumroad上架',
        'module': 'gumroad-store',
        'command': 'python sales/gumroad-store/publish.py',
        'desc': '新产品自动上架Gumroad'
    },
    {
        'time': '09:10',
        'name': 'Payhip上架',
        'module': 'payhip-store',
        'command': 'python sales/payhip-store/publish.py',
        'desc': '新产品自动上架Payhip'
    },
    {
        'time': '10:00',
        'name': 'Twitter推广',
        'module': 'twitter-bot',
        'command': 'python marketing/twitter-bot/twitter_bot.py',
        'desc': '发布AI生成推文'
    },
    {
        'time': '11:00',
        'name': 'Reddit推广',
        'module': 'reddit-bot',
        'command': 'python marketing/reddit-bot/reddit_bot.py',
        'desc': '发布/评论Reddit'
    },
    {
        'time': '12:00',
        'name': 'SEO博客',
        'module': 'seo-blogs',
        'command': 'python marketing/seo-blogs/seo_blogs.py',
        'desc': '生成并发布博客文章'
    },
    {
        'time': '14:00',
        'name': 'Pinterest推广',
        'module': 'pinterest-bot',
        'command': 'python marketing/pinterest-bot/pin.py',
        'desc': 'Pin产品图片'
    },
    {
        'time': '16:00',
        'name': 'YouTube Shorts',
        'module': 'youtube-channel',
        'command': 'python marketing/youtube-channel/youtube_manager.py --action produce --type short',
        'desc': '生产YouTube Shorts'
    },
    {
        'time': '18:00',
        'name': '第二轮社交推广',
        'module': 'twitter-bot',
        'command': 'python marketing/twitter-bot/twitter_bot.py --mode engage',
        'desc': '晚间互动推广'
    },
    {
        'time': '23:00',
        'name': '收益采集',
        'module': 'revenue-tracker',
        'command': 'python analytics/revenue-tracker/collect.py',
        'desc': '全平台收益数据采集'
    },
    {
        'time': '23:10',
        'name': '日报生成',
        'module': 'dashboard',
        'command': 'python analytics/dashboard/generate_report.py',
        'desc': '生成每日报告'
    },
    {
        'time': '23:30',
        'name': 'AI记忆更新',
        'module': 'knowledge-base',
        'command': 'python memory/knowledge-base/update.py',
        'desc': '更新知识库和学习记录'
    },
]

# ============================================================
# 调度器
# ============================================================
class MasterScheduler:
    """总调度器"""

    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.log_file = LOG_DIR / f'scheduler_{self.today}.log'
        self.executed = {}  # task_name → datetime

    def log(self, level: str, msg: str):
        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{ts}] [{level}] {msg}"
        print(line)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

    def print_schedule(self):
        print("=" * 70)
        print(f"  📅 AI Money Machine — 每日自动流水线 ({self.today})")
        print("=" * 70)
        for task in DAILY_PIPELINE:
            print(f"  {task['time']}  {task['name']:<14}  {task['desc']}")
        print("=" * 70)

    def run_task(self, task: dict) -> bool:
        """执行单个任务"""
        self.log('INFO', f"▶ {task['name']} — {task['desc']}")

        start = datetime.now()
        try:
            # 模拟运行(实际部署时用subprocess)
            result = subprocess.run(
                task['command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(PROJECT_ROOT)
            )
            duration = (datetime.now() - start).total_seconds()
            ok = result.returncode == 0

            if ok:
                self.log('OK', f"  ✅ {task['name']} ({duration:.1f}s)")
            else:
                err = result.stderr[-200:] if result.stderr else 'unknown'
                self.log('FAIL', f"  ❌ {task['name']} — {err[:100]}")

            self.executed[task['name']] = datetime.now().isoformat()
            return ok

        except subprocess.TimeoutExpired:
            self.log('FAIL', f"  ⏰ {task['name']} — timeout")
            return False
        except Exception as e:
            self.log('FAIL', f"  💥 {task['name']} — {e}")
            return False

    def run_full_day(self):
        """运行全天的流水线"""
        self.print_schedule()
        self.log('INFO', '=' * 60)
        self.log('INFO', f'🚀 每日流水线启动 ({self.today})')
        self.log('INFO', '=' * 60)

        success = 0
        failed = 0

        for task in DAILY_PIPELINE:
            ok = self.run_task(task)
            if ok:
                success += 1
            else:
                failed += 1
            time.sleep(2)

        # 日报
        self.log('INFO', '=' * 60)
        self.log('INFO', f'🏁 流水线完成: ✅{success} ❌{failed} / {len(DAILY_PIPELINE)}')
        self.log('INFO', '=' * 60)

        # 推算收入
        self._estimate_revenue()

    def _estimate_revenue(self):
        """收入预估"""
        products = 10
        avg_price = 12  # $12 average
        daily_visits_est = 50  # estimated from marketing activities
        conversion_rate = 0.02  # 2%
        estimated_sales = daily_visits_est * conversion_rate
        estimated_revenue = estimated_sales * avg_price

        self.log('ESTIMATE', f'预估访问: {daily_visits_est}/天')
        self.log('ESTIMATE', f'预估销售: {estimated_sales:.1f}单/天')
        self.log('ESTIMATE', f'预估收入: ${estimated_revenue:.2f}/天')
        self.log('ESTIMATE', f'预估月收入: ${estimated_revenue * 30:.2f}')


# ============================================================
# 主程序
# ============================================================
def main():
    scheduler = MasterScheduler()

    print("""
╔══════════════════════════════════════════════╗
║    ⏰ AI Money Machine 全自动调度中枢       ║
║    每日14个自动任务 | 7层架构 | 全程无人    ║
╚══════════════════════════════════════════════╝
    """)

    scheduler.print_schedule()

    print(f"\n🔄 运行模式:")
    print(f"  python scheduler.py --mode once   → 运行一次")
    print(f"  python scheduler.py --mode loop   → 持续运行(每60s检查)")
    print(f"  python scheduler.py --mode report → 显示计划")
    print(f"\n💡 将本脚本加入Windows计划任务即可全自动运行")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['once', 'loop', 'report'], default='report')
    args = parser.parse_args()

    scheduler = MasterScheduler()

    if args.mode == 'report':
        scheduler.print_schedule()
    elif args.mode == 'once':
        scheduler.run_full_day()
    elif args.mode == 'loop':
        scheduler.print_schedule()
        print("🔄 持续运行中... (Ctrl+C to stop)")
        try:
            while True:
                now = datetime.now()
                for task in DAILY_PIPELINE:
                    task_time = datetime.strptime(f"{now.strftime('%Y-%m-%d')} {task['time']}", '%Y-%m-%d %H:%M')
                    diff = abs((now - task_time).total_seconds())
                    if diff < 60 and task['name'] not in scheduler.executed:
                        scheduler.run_task(task)
                        scheduler.executed[task['name']] = now.isoformat()
                time.sleep(30)
                # Reset daily at midnight
                if now.hour == 0 and now.minute < 1:
                    scheduler.executed = {}
        except KeyboardInterrupt:
            print("\n🛑 调度器停止")
