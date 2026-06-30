#!/usr/bin/env python3
"""
Pinterest 浏览器自动化 - API v5 备选方案
使用 Playwright Chromium 持久化上下文，支持一次登录后自动复用 Cookie
"""

import json, os, sys, time, random, re
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
QUEUE_FILE = SCRIPT_DIR / "publish_queue.json"
CHROME_PROFILE = SCRIPT_DIR / "pw_chrome_profile"
LOG_FILE = SCRIPT_DIR / "auto_pin.log"

sys.stdout.reconfigure(encoding="utf-8")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_queue():
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================
# 反爬保护 - 隐藏自动化特征
# ============================================================
STEALTH_SCRIPT = """
// 移除 webdriver 标记
Object.defineProperty(navigator, 'webdriver', { get: () => false });
// 伪造 chrome 对象
window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
// 伪造插件数量（正常浏览器通常有3-5个）
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
// 伪造权限
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({state: Notification.permission}) :
        originalQuery(parameters)
);
// 隐藏 headless 特征
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'zh-CN'] });
Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
"""

def random_delay(min_ms=500, max_ms=2000):
    time.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

# ============================================================
# Pinterest 自动化发布
# ============================================================
async def publish_pins(headless=False, dry_run=False):
    """主发布函数"""
    config = load_config()
    queue = load_queue()

    if not queue:
        log("[SKIP] 发布队列为空，无需操作")
        return 0

    log(f"[START] 准备发布 {len(queue)} 个 Pin")

    from playwright.async_api import async_playwright

    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        log("[BROWSER] 启动 Chromium...")
        browser = await p.chromium.launch_persistent_context(
            str(CHROME_PROFILE),
            channel="msedge",
            headless=headless,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Los_Angeles",
            # 附加启动参数提升反爬
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()

        # 注入反爬脚本（每次导航前生效）
        await page.add_init_script(STEALTH_SCRIPT)
        page.set_default_timeout(30000)

        # ====== 检查登录状态 ======
        log("[CHECK] 检查 Pinterest 登录状态...")
        await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        random_delay(2000, 4000)

        logged_in = await page.query_selector(
            '[data-test-id="header-create-menu-button"], '
            '[aria-label="Create"], '
            'button[aria-label="Create Pin"], '
            '[data-test-id="addPinButton"]'
        )

        if not logged_in:
            log("[LOGIN] 未检测到登录状态")
            if headless:
                log("[ERROR] Headless 模式下无法登录，请先运行 --mode login")
                await browser.close()
                return 0

            log("[LOGIN] === 请在浏览器窗口中手动登录 Pinterest ===")
            log(f"[LOGIN] 邮箱: {config['pinterest_email']}")
            log("[LOGIN] 登录方式建议:")
            log("[LOGIN]   1. 点 Log in → 输入邮箱和密码")
            log("[LOGIN]   2. 如果出现 Google 登录按钮，用邮箱登录而非 Google")
            log("[LOGIN]   3. 如果需要验证，按页面提示完成")
            log("[LOGIN] ")
            log("[LOGIN] 自动检测登录状态（每5秒检查一次，最长5分钟）...")

            if not dry_run:
                for attempt in range(60):
                    await page.wait_for_timeout(5000)
                    try:
                        await page.goto("https://www.pinterest.com/", timeout=15000, wait_until="domcontentloaded")
                        random_delay(2000, 3000)
                        logged_in = await page.query_selector(
                            '[data-test-id="header-create-menu-button"], '
                            '[aria-label="Create"], '
                            'button[aria-label="Create Pin"], '
                            '[data-test-id="addPinButton"]'
                        )
                        if logged_in:
                            log("[OK] 登录成功！Cookie 已自动保存")
                            break
                        log(f"[LOGIN] 等待中... (第{attempt+1}次检查)")
                    except Exception as e:
                        log(f"[LOGIN] 检查出错（可能正在登录中）: {e}")
                else:
                    log("[WARN] 超时未检测到登录，继续尝试发布...")

        # ====== 逐个发布 ======
        posted = 0
        failed = 0

        for i, pin in enumerate(queue):
            if dry_run:
                log(f"[DRY RUN] [{i+1}/{len(queue)}] {pin['title'][:60]}")
                continue

            log(f"[PIN] [{i+1}/{len(queue)}] 正在发布: {pin['title'][:50]}...")

            try:
                success = await create_one_pin(page, pin, config)
                if success:
                    posted += 1
                    log(f"  [OK] 发布成功 ✓")
                else:
                    failed += 1
                    log(f"  [FAIL] 发布失败")
            except Exception as e:
                failed += 1
                log(f"  [ERROR] {e}")

            # 间隔避免被限流
            if i < len(queue) - 1:
                delay = random.randint(4000, 8000)
                log(f"  [WAIT] 等待 {delay//1000}s...")
                await page.wait_for_timeout(delay)

        await browser.close()

    log(f"[DONE] 完成！成功: {posted}, 失败: {failed}, 总计: {len(queue)}")

    if not dry_run and posted > 0:
        QUEUE_FILE.unlink(missing_ok=True)
        log(f"[CLEAN] 发布队列已清空")

    return posted


async def create_one_pin(page, pin, config):
    """发布单个 Pin"""
    try:
        # 1. 点首页 "+" → "Create Pin"
        await page.goto("https://www.pinterest.com/", timeout=20000, wait_until="domcontentloaded")
        random_delay(2000, 3000)

        # 点击 Create 按钮
        create_btn = await page.query_selector(
            '[data-test-id="addPinButton"], '
            '[data-test-id="header-create-menu-button"], '
            'button[aria-label="Create Pin"], '
            'button:has-text("Create")'
        )
        if not create_btn:
            log("  [WARN] 找不到 Create 按钮")
            return False

        await create_btn.click()
        random_delay(1000, 2000)

        # 点 "Create Pin" 菜单项
        pin_option = await page.query_selector(
            'text="Create Pin", '
            '[data-test-id="create-pin"], '
            'div[role="menuitem"]:has-text("Pin"), '
            'div[role="menuitem"]:has-text("Create Pin"), '
            'span:has-text("Create Pin")'
        )
        if pin_option:
            await pin_option.click()
        else:
            # 可能已经直接打开了创建页面
            pass

        random_delay(2000, 3000)

        # 2. 上传图片
        file_input = await page.query_selector('input[type="file"]')
        if not file_input:
            # 有可能需要先触发上传区域
            upload_area = await page.query_selector(
                '[data-test-id="pin-builder-image-dropzone"], '
                '[role="button"]:has-text("Upload"), '
                'div:has-text("Drag and drop")'
            )
            if upload_area:
                await upload_area.click()
                random_delay(1000, 2000)

        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(pin["image_path"])
            random_delay(3000, 5000)
            log(f"  [IMG] 上传: {Path(pin['image_path']).name}")
        else:
            log("  [WARN] 找不到文件上传控件")
            return False

        # 3. 填写标题
        title_el = await page.query_selector(
            '[data-test-id="pin-title"], '
            '#pin-title, '
            '[id*="title"], '
            '[contenteditable="true"][role="textbox"]'
        )
        if title_el:
            await title_el.click()
            await title_el.fill("")
            await title_el.type(pin["title"][:100], delay=50)
            random_delay(500, 1000)
            log(f"  [TITLE] {pin['title'][:50]}")

        # 4. 填写描述
        desc_el = await page.query_selector(
            '[data-test-id="pin-description"], '
            '#pin-description, '
            '[id*="description"], '
            '[placeholder*="description"], '
            '[placeholder*="Describe"]'
        )
        if desc_el:
            await desc_el.click()
            desc = pin.get("description", "")[:400]
            desc += config["pin_template"]["description_suffix"]
            await desc_el.fill(desc)
            random_delay(500, 1000)
            log(f"  [DESC] 描述已填写")

        # 5. 填写链接
        link_el = await page.query_selector(
            '[data-test-id="pin-link"], '
            '#pin-link, '
            '[id*="link"], '
            'input[placeholder*="link"], '
            'input[placeholder*="URL"], '
            'input[placeholder*="website"]'
        )
        if link_el:
            await link_el.click()
            await link_el.fill(pin["url"])
            random_delay(500, 1000)
            log(f"  [LINK] {pin['url']}")

        # 6. 选择 Board
        try:
            board_btn = await page.query_selector(
                '[data-test-id="board-selector"], '
                'button:has-text("Board"), '
                '[id*="board"], '
                'div[role="button"]:has-text("Board")'
            )
            if board_btn:
                await board_btn.click()
                random_delay(1500, 2500)

                board_option = await page.query_selector(
                    f'text="{config["pinterest_board"]}", '
                    f'div:has-text("{config["pinterest_board"]}"), '
                    f'span:has-text("{config["pinterest_board"]}")'
                )
                if board_option:
                    await board_option.click()
                    random_delay(1000, 1500)
                    log(f"  [BOARD] → {config['pinterest_board']}")
                else:
                    log(f"  [BOARD] 未找到板面 '{config['pinterest_board']}'，使用默认")
        except Exception as e:
            log(f"  [WARN] Board 选择跳过: {e}")

        # 7. 点保存/发布
        random_delay(1500, 2500)
        save_btn = await page.query_selector(
            'button:has-text("Save"), '
            'button:has-text("Publish"), '
            '[data-test-id="board-dropdown-save-button"], '
            '[data-test-id="pin-builder-save"], '
            '[data-test-id="create-pin-done"], '
            'button[type="submit"]'
        )
        if save_btn:
            await save_btn.click()
            random_delay(3000, 5000)
            return True
        else:
            log("  [WARN] 找不到发布按钮")
            # 保存截图用于调试
            await page.screenshot(path=str(SCRIPT_DIR / "debug_screenshot.png"))
            log("  [DEBUG] 已保存截图到 debug_screenshot.png")
            return False

    except Exception as e:
        log(f"  [ERROR] 发布异常: {e}")
        try:
            await page.screenshot(path=str(SCRIPT_DIR / "debug_screenshot.png"))
            log("  [DEBUG] 已保存错误截图")
        except:
            pass
        return False


# ============================================================
# 仅登录模式 - 让用户手动登录一次
# ============================================================
async def login_only():
    """只打开浏览器让用户手动登录，不做发布"""
    from playwright.async_api import async_playwright

    config = load_config()
    CHROME_PROFILE.mkdir(parents=True, exist_ok=True)

    log("[LOGIN] 正在打开浏览器...")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            str(CHROME_PROFILE),
            channel="msedge",
            headless=False,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Los_Angeles",
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.add_init_script(STEALTH_SCRIPT)

        await page.goto("https://www.pinterest.com/login/", timeout=30000, wait_until="domcontentloaded")
        log(f"[LOGIN] 页面: {page.url}")
        log(f"[LOGIN] 请在打开的浏览器中用以下账号登录:")
        log(f"[LOGIN]   邮箱: {config['pinterest_email']}")
        log(f"[LOGIN] ")
        log(f"[LOGIN] 自动检测登录状态（每5秒检查一次，最长5分钟）...")

        selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"], [data-test-id="addPinButton"]'
        for attempt in range(60):
            await page.wait_for_timeout(5000)
            try:
                await page.goto("https://www.pinterest.com/", timeout=15000, wait_until="domcontentloaded")
                logged_in = await page.query_selector(selectors)
                if logged_in:
                    log("[OK] 登录成功！Cookie 已保存到持久化 profile")
                    break
                log(f"[LOGIN] 等待中... (第{attempt+1}次检查)")
            except Exception as e:
                log(f"[LOGIN] 检查出错（可能正在登录中）: {e}")
        else:
            log("[WARN] 超时未检测到登录，请检查是否登录成功")
            await page.screenshot(path=str(SCRIPT_DIR / "login_check.png"))
            log("[DEBUG] 已保存截图 login_check.png")

        await browser.close()


# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(description="Pinterest 浏览器自动化发布")
    parser.add_argument("--mode", choices=["login", "publish", "dry-run"], default="publish",
                        help="login: 仅登录 | publish: 发布队列 | dry-run: 预览")
    parser.add_argument("--headless", action="store_true", help="无头模式（需要已登录）")
    args = parser.parse_args()

    if args.mode == "login":
        asyncio.run(login_only())
    elif args.mode == "dry-run":
        asyncio.run(publish_pins(headless=False, dry_run=True))
    else:
        asyncio.run(publish_pins(headless=args.headless))
