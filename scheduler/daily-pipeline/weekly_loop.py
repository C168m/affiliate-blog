#!/usr/bin/env python3
"""
============================================================
⏰ AI Money Machine — 全自动周循环调度引擎
每周: 生产内容 → 发布推广 → 数据报告 → 优化
============================================================

使用方法:
  python weekly_loop.py --mode once    # 运行一次周循环
  python weekly_loop.py --mode cron    # 持续运行(每30分钟检查)
  python weekly_loop.py --mode report  # 仅生成本周报告
"""

import json, os, sys, io, time, subprocess
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_DIR = PROJECT_ROOT / 'scheduler' / 'daily-pipeline' / 'logs'
REPORT_DIR = PROJECT_ROOT / 'analytics' / 'dashboard' / 'reports'
DATA_DIR = PROJECT_ROOT / 'scheduler' / 'task-queue'
for d in [LOG_DIR, REPORT_DIR, DATA_DIR]: d.mkdir(parents=True, exist_ok=True)

# ============================================================
# 周循环任务定义
# ============================================================
WEEKLY_PIPELINE = {
    'Monday': [
        {'time': '09:00', 'task': 'weekly_report', 'script': 'analytics/dashboard/reports/generate_report.py', 'desc': '上周数据报告'},
        {'time': '10:00', 'task': 'content_gen', 'script': 'marketing/seo-blogs/seo_blogs.py', 'desc': 'SEO博客文章'},
        {'time': '12:00', 'task': 'twitter_posts', 'script': 'scheduler/task-queue/social_auto_publisher.py', 'desc': '本周Twitter内容'},
        {'time': '14:00', 'task': 'gumroad_sync', 'desc': 'Gumroad产品状态同步'},
    ],
    'Tuesday': [
        {'time': '09:00', 'task': 'twitter_publish', 'desc': '发布Twitter内容'},
        {'time': '11:00', 'task': 'linkedin_publish', 'desc': '发布LinkedIn内容'},
        {'time': '14:00', 'task': 'pinterest_pins', 'script': 'scheduler/task-queue/pinterest_auto_pinner.py', 'desc': 'Pinterest Pin排期'},
    ],
    'Wednesday': [
        {'time': '09:00', 'task': 'reddit_post', 'desc': 'Reddit价值帖'},
        {'time': '11:00', 'task': 'twitter_publish', 'desc': '发布Twitter内容'},
        {'time': '14:00', 'task': 'medium_article', 'desc': 'Medium新文章'},
    ],
    'Thursday': [
        {'time': '09:00', 'task': 'twitter_publish', 'desc': '发布Twitter内容'},
        {'time': '11:00', 'task': 'youtube_shorts', 'script': 'scheduler/task-queue/youtube_shorts_generator.py', 'desc': 'YouTube Shorts脚本'},
        {'time': '14:00', 'task': 'linkedin_publish', 'desc': '发布LinkedIn内容'},
    ],
    'Friday': [
        {'time': '09:00', 'task': 'twitter_publish', 'desc': '发布Twitter内容'},
        {'time': '11:00', 'task': 'reddit_post', 'desc': 'Reddit推广帖'},
        {'time': '14:00', 'task': 'content_review', 'desc': '本周内容效果分析'},
        {'time': '16:00', 'task': 'weekly_data_snapshot', 'desc': '本周收益快照'},
    ],
    'Saturday': [
        {'time': '10:00', 'task': 'twitter_publish', 'desc': '发布Twitter内容'},
        {'time': '14:00', 'task': 'weekly_content_plan', 'desc': '下周内容计划'},
    ],
    'Sunday': [
        {'time': '10:00', 'task': 'weekly_full_report', 'desc': '生成完整周报'},
        {'time': '14:00', 'task': 'next_week_prep', 'desc': '预生成下周内容'},
        {'time': '16:00', 'task': 'optimization', 'desc': '价格/描述优化建议'},
    ],
}

# ============================================================
# 自动化执行引擎
# ============================================================
class WeeklyLoop:
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.weekday = datetime.now().strftime('%A')
        self.log_file = LOG_DIR / f'weekly_{datetime.now().strftime("%Y%W")}.log'

    def log(self, level, msg):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f'[{ts}] [{level}] {msg}'
        print(line)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(line + '\n')

    def run_script(self, script_path):
        """运行指定Python脚本"""
        full_path = PROJECT_ROOT / script_path
        if not full_path.exists():
            self.log('SKIP', f'{script_path} not found')
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(full_path)],
                capture_output=True, text=True, timeout=600, cwd=str(PROJECT_ROOT),
                encoding='utf-8', errors='replace'
            )
            ok = result.returncode == 0
            self.log('OK' if ok else 'FAIL', f'{script_path} (exit={result.returncode})')
            if result.stdout:
                self.log('OUT', result.stdout[-200:].replace('\n', ' | '))
            return ok
        except Exception as e:
            self.log('ERROR', f'{script_path}: {e}')
            return False

    def run_today(self):
        """执行今日计划"""
        tasks = WEEKLY_PIPELINE.get(self.weekday, [])
        self.log('START', f'=== {self.weekday} {self.today} 今日任务: {len(tasks)} ===')

        success = failed = skipped = 0
        for task in tasks:
            self.log('TASK', f'{task["time"]} {task["task"]} — {task["desc"]}')
            if 'script' in task:
                if self.run_script(task['script']):
                    success += 1
                else:
                    failed += 1
            else:
                self.log('SKIP', f'{task["task"]} — 需手动或浏览器操作')
                skipped += 1

        self.log('END', f'今日完成: ✅{success} ❌{failed} ⏭{skipped}')
        return {'success': success, 'failed': failed, 'skipped': skipped}

    def run_full_week(self):
        """模拟运行整周（立即执行所有任务）"""
        self.log('START', f'=== 全周模拟运行 ===')
        total = {'success': 0, 'failed': 0, 'skipped': 0}
        for day, tasks in WEEKLY_PIPELINE.items():
            self.log('DAY', f'--- {day} ---')
            for task in tasks:
                if 'script' in task:
                    if self.run_script(task['script']):
                        total['success'] += 1
                    else:
                        total['failed'] += 1
                else:
                    total['skipped'] += 1
                time.sleep(1)
        self.log('END', f'全周完成: ✅{total["success"]} ❌{total["failed"]} ⏭{total["skipped"]}')
        return total

    def generate_weekly_report(self):
        """生成完整周报"""
        from openai import OpenAI
        env = {}
        for line in (PROJECT_ROOT / '.env').read_text(encoding='utf-8').split('\n'):
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                env[k.strip()] = v.strip()

        client = OpenAI(api_key=env.get('DEEPSEEK_API_KEY', ''), base_url='https://api.deepseek.com')

        # 产品摘要
        store_value = 154.86
        total_products = 10

        prompt = f"""Write a weekly business report for an AI digital products store.

Store: https://howler06371.gumroad.com
Products: {total_products} digital products (${store_value} total value)
Platform: Gumroad

Sections to include:
1. Weekly Summary (2-3 sentences)
2. Product Performance (best/worst performing categories)
3. Marketing Activity (what was posted/promoted this week)
4. Revenue Estimate (based on traffic data)
5. Recommendations for Next Week
6. Key Metrics Table

Keep it concise, data-driven. Format as a professional report."""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=800, temperature=0.3
            )
            report = resp.choices[0].message.content

            report_file = REPORT_DIR / f'weekly_report_{datetime.now().strftime("%Y%W")}.md'
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            self.log('REPORT', f'Generated: {report_file}')
            print(f'\n{report}')
            return report
        except Exception as e:
            self.log('ERROR', f'Report generation failed: {e}')
            return None

    def print_weekly_plan(self):
        """打印每周计划"""
        print('\n' + '=' * 70)
        print(f'  📅 AI Money Machine — 全自动周循环 ({self.weekday})')
        print('=' * 70)
        for day, tasks in WEEKLY_PIPELINE.items():
            marker = '▶' if day == self.weekday else ' '
            print(f'\n{marker} {day}:')
            for task in tasks:
                print(f'    {task["time"]} [{task["task"]}] {task["desc"]}')
        print('\n' + '=' * 70)


# ============================================================
# 主程序
# ============================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(description='AI Money Machine Weekly Loop')
    parser.add_argument('--mode', choices=['once', 'cron', 'full', 'report', 'plan'], default='plan')
    parser.add_argument('--interval', type=int, default=1800, help='Cron模式检查间隔(秒),默认1800')

    args = parser.parse_args()
    loop = WeeklyLoop()

    if args.mode == 'plan':
        loop.print_weekly_plan()

    elif args.mode == 'once':
        loop.print_weekly_plan()
        print(f'\n🚀 执行今日任务: {loop.weekday}\n')
        loop.run_today()

    elif args.mode == 'full':
        loop.print_weekly_plan()
        print('\n🚀 执行全周批量任务\n')
        loop.run_full_week()

    elif args.mode == 'report':
        print('📊 生成周报...')
        loop.generate_weekly_report()

    elif args.mode == 'cron':
        loop.print_weekly_plan()
        print(f'\n⏰ 启动Cron模式 (每{args.interval}秒检查)')
        print('按 Ctrl+C 停止\n')
        loop.log('CRON', f'Cron mode started, interval={args.interval}s')

        last_executed = {}
        try:
            while True:
                now = datetime.now()
                tasks = WEEKLY_PIPELINE.get(now.strftime('%A'), [])
                for task in tasks:
                    task_key = f'{now.strftime("%A")}-{task["time"]}'
                    task_time = datetime.strptime(f'{now.strftime("%Y-%m-%d")} {task["time"]}', '%Y-%m-%d %H:%M')
                    diff = (now - task_time).total_seconds()

                    if 0 <= diff < args.interval and task_key not in last_executed:
                        loop.log('CRON', f'触发: {task["time"]} {task["desc"]}')
                        if 'script' in task:
                            loop.run_script(task['script'])
                        last_executed[task_key] = now.isoformat()

                time.sleep(min(args.interval, 300))
        except KeyboardInterrupt:
            print('\n🛑 Cron模式已停止')


if __name__ == '__main__':
    main()
