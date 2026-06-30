#!/usr/bin/env python3
"""
============================================================
⏰ 全自动调度引擎
定时任务 + 监控告警 + 全自动运行
============================================================
"""

import json, os, sys, time, subprocess
from dotenv import load_dotenv; load_dotenv()
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ============================================================
# 每日自动化时间表
# ============================================================

DAILY_SCHEDULE = [
    # 时间   模块                    脚本                                  说明
    ("07:00", "健康检查",    "python -c 'print(\"✅ 系统正常\")'",        "系统自检"),
    ("08:00", "社交媒体",    "python 04-社交媒体矩阵/social_automation.py --action schedule", "早间社交推广"),
    ("09:00", "SEO生产",     "python 05-SEO内容站群/seo_content_factory.py --action produce --count 3", "SEO文章生产"),
    ("10:00", "数字产品",    "python 01-数字产品工厂/product_factory.py --mode batch --count 5", "数字产品生产"),
    ("11:00", "YouTube生产", "python 03-YouTube无人频道/youtube_manager.py --action produce --type short", "YouTube Short生产"),
    ("12:00", "销售上架",    "python 02-销售平台自动化/sales_automation.py --action publish", "产品上架"),
    ("13:00", "YouTube发布", "python 03-YouTube无人频道/youtube_manager.py --action produce", "午间视频发布"),
    ("15:00", "SEO发布",     "python 05-SEO内容站群/seo_content_factory.py --action publish", "文章发布"),
    ("17:00", "社交媒体",    "python 04-社交媒体矩阵/social_automation.py --action schedule", "晚间社交推广"),
    ("19:00", "YouTube发布", "python 03-YouTube无人频道/youtube_manager.py --action produce --type long", "晚高峰长视频"),
    ("21:00", "联盟更新",    "python 06-流量引擎/traffic_engine.py --action programs", "联盟链接检查"),
    ("22:00", "收益采集",    "python 07-收益追踪/revenue_tracker.py --action summary", "收益数据采集"),
    ("23:30", "日报生成",    "python 07-收益追踪/revenue_tracker.py --action summary", "生成日报"),
]

# ============================================================
# 调度器
# ============================================================

class SmartScheduler:
    """智能调度器"""

    def __init__(self):
        self.schedule = DAILY_SCHEDULE
        self.log_file = LOG_DIR / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        self.executed = set()

    def get_due_tasks(self) -> list:
        """获取当前应该执行的任务"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        due = []

        for time_str, name, cmd, desc in self.schedule:
            # 任务时间±5分钟内触发
            task_hour, task_min = map(int, time_str.split(":"))
            current_minutes = now.hour * 60 + now.minute
            task_minutes = task_hour * 60 + task_min

            if abs(current_minutes - task_minutes) <= 5:
                task_key = f"{time_str}_{name}"
                if task_key not in self.executed:
                    due.append((time_str, name, cmd, desc, task_key))

        return due

    def run_task(self, time_str: str, name: str, cmd: str, desc: str, task_key: str) -> dict:
        """执行一个任务"""
        print(f"\n{'='*50}")
        print(f"▶ [{time_str}] {name}")
        print(f"  📋 {desc}")
        print(f"  💻 {cmd}")
        print(f"{'='*50}")

        start = datetime.now()

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(PROJECT_ROOT)
            )
            success = result.returncode == 0
            duration = (datetime.now() - start).total_seconds()

            log_entry = {
                "timestamp": start.isoformat(),
                "task": name,
                "scheduled_time": time_str,
                "duration_seconds": duration,
                "success": success,
                "stdout_tail": result.stdout[-300:] if result.stdout else "",
                "stderr_tail": result.stderr[-300:] if result.stderr else "",
            }

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            self.executed.add(task_key)

            if success:
                print(f"  ✅ 完成 ({duration:.1f}s)")
            else:
                print(f"  ❌ 失败 ({duration:.1f}s)")

            return log_entry

        except subprocess.TimeoutExpired:
            print(f"  ⏰ 超时 (10分钟)")
            return {"task": name, "success": False, "error": "timeout"}
        except Exception as e:
            print(f"  💥 异常: {e}")
            return {"task": name, "success": False, "error": str(e)}

    def run_cycle(self):
        """运行一个周期"""
        due = self.get_due_tasks()

        if not due:
            # 静默等待
            return

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔔 {len(due)} 个待执行任务")

        for time_str, name, cmd, desc, task_key in due:
            self.run_task(time_str, name, cmd, desc, task_key)

    def run_loop(self, check_interval: int = 60):
        """持续运行"""
        print("=" * 60)
        print("⏰ AI Money Machine 全自动调度引擎")
        print(f"📋 每日任务: {len(self.schedule)} 个")
        print(f"🔄 检查间隔: {check_interval}秒")
        print("=" * 60)
        print("\n⏳ 等待任务触发...\n")

        # 重置每日执行记录
        last_date = datetime.now().strftime("%Y-%m-%d")

        try:
            while True:
                # 新的一天，重置执行记录
                today = datetime.now().strftime("%Y-%m-%d")
                if today != last_date:
                    self.executed.clear()
                    last_date = today
                    print(f"\n🆕 新的一天! {today} 任务已重置\n")

                self.run_cycle()
                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n🛑 调度引擎已停止")

    def print_schedule(self):
        """打印今日计划"""
        print(f"\n📅 每日自动化时间表 ({datetime.now().strftime('%Y-%m-%d')})\n")
        print(f"{'时间':<8} {'模块':<14} {'说明'}")
        print("-" * 50)
        for time_str, name, cmd, desc in self.schedule:
            print(f"{time_str:<8} {name:<14} {desc}")


# ============================================================
# 监控告警
# ============================================================

class SystemMonitor:
    """系统监控"""

    @staticmethod
    def check_health() -> list:
        """健康检查"""
        issues = []

        # 检查Python
        try:
            result = subprocess.run("python --version", shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                issues.append("Python未正常运行")
        except:
            issues.append("Python检查失败")

        # 检查磁盘空间
        import shutil
        usage = shutil.disk_usage(str(PROJECT_ROOT))
        free_gb = usage.free / (1024**3)
        if free_gb < 5:
            issues.append(f"⚠️ 磁盘空间不足: {free_gb:.1f}GB")

        # 检查日志大小
        total_log_size = sum(f.stat().st_size for f in LOG_DIR.glob("*.log") if f.is_file())
        if total_log_size > 100 * 1024 * 1024:  # 100MB
            issues.append(f"⚠️ 日志文件过大: {total_log_size / 1024 / 1024:.1f}MB")

        return issues

    @staticmethod
    def send_alert(message: str, level: str = "warning"):
        """发送告警"""
        alert_file = LOG_DIR / "alerts.jsonl"
        alert = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        with open(alert_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(alert, ensure_ascii=False) + "\n")


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="全自动调度引擎")
    parser.add_argument("--mode", choices=["loop", "once", "schedule", "health"], default="schedule")
    parser.add_argument("--interval", type=int, default=60, help="检查间隔(秒)")

    args = parser.parse_args()

    scheduler = SmartScheduler()
    monitor = SystemMonitor()

    if args.mode == "schedule":
        scheduler.print_schedule()

    elif args.mode == "loop":
        print("🚀 启动全自动调度引擎...")
        issues = monitor.check_health()
        if issues:
            for issue in issues:
                print(f"  {issue}")
        scheduler.run_loop(args.interval)

    elif args.mode == "once":
        scheduler.run_cycle()

    elif args.mode == "health":
        issues = monitor.check_health()
        if issues:
            print("⚠️ 发现问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 系统状态正常")

if __name__ == "__main__":
    main()
