#!/usr/bin/env python3
"""Pinterest Pin Publisher - Cookie injection version. Uses Edge profile copy with existing Pinterest login."""

import json, os, sys, time, random
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
QUEUE_FILE = SCRIPT_DIR / "publish_queue.json"
LOG_FILE = SCRIPT_DIR / "auto_pin.log"
EDGE_PROFILE = SCRIPT_DIR / "edge_pin_profile"

sys.stdout.reconfigure(encoding="utf-8")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
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

STEALTH = """
Object.defineProperty(navigator, 'webdriver', { get: () => false });
window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
const q = window.navigator.permissions.query;
window.navigator.permissions.query = (p) => (p.name === 'notifications' ? Promise.resolve({state: Notification.permission}) : q(p));
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'zh-CN'] });
"""

async def publish_all():
    config = load_config()
    queue = load_queue()

    if not queue:
        log("[SKIP] No pins in queue")
        return 0

    log(f"[START] Publishing {len(queue)} pins")
    EDGE_PROFILE.mkdir(parents=True, exist_ok=True)

    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        log("[BROWSER] Launching Edge with cookie profile...")
        browser = await p.chromium.launch_persistent_context(
            str(EDGE_PROFILE),
            channel="msedge",
            headless=False,
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Los_Angeles",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.add_init_script(STEALTH)
        page.set_default_timeout(30000)

        log("[CHECK] Checking Pinterest login via cookies...")
        try:
            await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        except Exception as e:
            log(f"[ERROR] Cannot reach Pinterest: {e}")
            await browser.close()
            return 0

        await page.wait_for_timeout(3000)

        selectors = (
            '[data-test-id="header-create-menu-button"], '
            '[aria-label="Create"], '
            'button[aria-label="Create Pin"], '
            '[data-test-id="addPinButton"]'
        )
        logged_in = await page.query_selector(selectors)

        if not logged_in:
            log("[ERROR] Cookie login FAILED! Cookies may be expired.")
            log("[FIX] Open pinterest.com in normal Edge, verify logged in, then re-copy cookies.")
            await page.screenshot(path=str(SCRIPT_DIR / "login_failed.png"))
            await browser.close()
            return 0

        log("[OK] Cookie login successful!")

        posted = 0
        failed = 0

        for i, pin in enumerate(queue):
            log(f"[PIN] [{i+1}/{len(queue)}] {pin['title'][:50]}...")

            try:
                ok = await create_pin(page, pin, config)
                if ok:
                    posted += 1
                    log("  [OK]")
                else:
                    failed += 1
                    log("  [FAIL]")
                    await page.screenshot(path=str(SCRIPT_DIR / "pin_failed.png"))
            except Exception as e:
                failed += 1
                log(f"  [ERROR] {e}")

            if i < len(queue) - 1:
                delay = random.randint(4000, 8000)
                log(f"  [WAIT] {delay//1000}s")
                await page.wait_for_timeout(delay)

        await browser.close()

    log(f"[DONE] Posted: {posted}, Failed: {failed}, Total: {len(queue)}")

    if posted > 0:
        QUEUE_FILE.unlink(missing_ok=True)
        log("[CLEAN] Queue cleared")

    return posted


async def create_pin(page, pin, config):
    # 1. Click Create
    await page.goto("https://www.pinterest.com/", timeout=20000, wait_until="domcontentloaded")
    await page.wait_for_timeout(random.randint(2000, 3500))

    create_btn = await page.query_selector(
        '[data-test-id="addPinButton"], '
        '[data-test-id="header-create-menu-button"], '
        'button[aria-label="Create Pin"], '
        'button:has-text("Create")'
    )
    if not create_btn:
        log("  [WARN] Create button not found")
        return False

    await create_btn.click()
    await page.wait_for_timeout(1500)

    pin_menu = await page.query_selector(
        '[data-test-id="create-pin"], '
        'div[role="menuitem"]:has-text("Pin"), '
        'span:has-text("Create Pin")'
    )
    if pin_menu:
        await pin_menu.click()
    await page.wait_for_timeout(2500)

    # 2. Upload image
    file_input = await page.query_selector('input[type="file"]')
    if not file_input:
        dropzone = await page.query_selector('[data-test-id="pin-builder-image-dropzone"]')
        if dropzone:
            await dropzone.click()
            await page.wait_for_timeout(2000)

    file_input = await page.query_selector('input[type="file"]')
    if file_input:
        await file_input.set_input_files(pin["image_path"])
        await page.wait_for_timeout(random.randint(3000, 5000))
        log(f"  [IMG] {Path(pin['image_path']).name}")
    else:
        log("  [WARN] File input not found")
        return False

    # 3. Title
    title_el = await page.query_selector(
        '[data-test-id="pin-title"], '
        '#pin-title, '
        '[contenteditable="true"][role="textbox"]'
    )
    if not title_el:
        title_el = await page.query_selector('[contenteditable="true"]')
    if title_el:
        await title_el.click()
        await title_el.fill("")
        await title_el.type(pin["title"][:100], delay=50)
        await page.wait_for_timeout(800)

    # 4. Description
    desc_el = await page.query_selector(
        '[data-test-id="pin-description"], '
        '#pin-description, '
        '[placeholder*="description"], '
        '[placeholder*="Describe"]'
    )
    if desc_el:
        desc_text = pin.get("description", "")[:400] + config["pin_template"]["description_suffix"]
        await desc_el.click()
        await desc_el.fill(desc_text)
        await page.wait_for_timeout(800)

    # 5. Link
    link_el = await page.query_selector(
        '[data-test-id="pin-link"], '
        '#pin-link, '
        'input[placeholder*="link"], '
        'input[placeholder*="URL"], '
        'input[placeholder*="website"]'
    )
    if link_el:
        await link_el.click()
        await link_el.fill(pin["url"])
        await page.wait_for_timeout(800)

    # 6. Board selector
    try:
        board_btn = await page.query_selector(
            '[data-test-id="board-selector"], '
            'button:has-text("Board")'
        )
        if board_btn:
            await board_btn.click()
            await page.wait_for_timeout(2000)
            board_opt = await page.query_selector(
                f'div:has-text("{config["pinterest_board"]}"), '
                f'span:has-text("{config["pinterest_board"]}")'
            )
            if board_opt:
                await board_opt.click()
                await page.wait_for_timeout(1500)
                log(f"  [BOARD] {config['pinterest_board']}")
    except Exception as e:
        log(f"  [WARN] Board skipped: {e}")

    # 7. Publish
    await page.wait_for_timeout(2000)
    save_btn = await page.query_selector(
        'button:has-text("Save"), '
        'button:has-text("Publish"), '
        '[data-test-id="board-dropdown-save-button"], '
        '[data-test-id="pin-builder-save"], '
        '[data-test-id="create-pin-done"]'
    )
    if save_btn:
        await save_btn.click()
        await page.wait_for_timeout(4000)
        return True
    else:
        log("  [WARN] Publish button not found")
        return False


if __name__ == "__main__":
    import asyncio
    n = asyncio.run(publish_all())
    print(f"\nDONE: {n} pins published")
