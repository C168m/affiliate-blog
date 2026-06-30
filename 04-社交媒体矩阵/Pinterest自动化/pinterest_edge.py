#!/usr/bin/env python3
"""
Pinterest Edge CDP 自动化
使用专属 Edge 配置文件 + DevTools Protocol — 不干扰正常浏览器
"""

import json, os, sys, time, random, subprocess, shutil
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
QUEUE_FILE = SCRIPT_DIR / "publish_queue.json"
LOG_FILE = SCRIPT_DIR / "auto_pin.log"
EDGE_PROFILE = SCRIPT_DIR / "edge_pin_profile"
CDP_PORT = 9223

sys.stdout.reconfigure(encoding="utf-8")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def find_edge():
    paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in paths:
        if os.path.isfile(p):
            return p
    raise FileNotFoundError("Edge not found")


def launch_edge():
    """Launch Edge with dedicated profile and CDP, without killing existing Edge"""
    edge = find_edge()
    profile_dir = str(EDGE_PROFILE)
    
    log(f"[LAUNCH] Starting Edge with dedicated profile on port {CDP_PORT}...")
    
    cmd = [
        edge,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--new-window",
        "about:blank",
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for i in range(20):
        time.sleep(1.5)
        try:
            import urllib.request
            resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/version", timeout=3)
            data = json.loads(resp.read())
            if "Browser" in data:
                log(f"[LAUNCH] Edge ready: {data.get('Browser', '')[:60]}")
                return proc
        except:
            pass
    
    log("[ERROR] Edge failed to start")
    proc.kill()
    return None


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_queue():
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


async def ensure_login(page, config, dry_run=False):
    """Check login, prompt if needed"""
    await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    
    selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"], [data-test-id="addPinButton"]'
    
    logged_in = await page.query_selector(selectors)
    if logged_in:
        return True
    
    log("[LOGIN] Not logged in. Opening login page...")
    log(f"[LOGIN] Account: {config['pinterest_email']}")
    log("[LOGIN] Please log in manually in the Edge window that just opened.")
    log("[LOGIN] (This is real Edge - Pinterest won't block it)")
    log("[LOGIN] Auto-detecting login (checking every 5 sec, max 5 min)...")
    
    await page.goto("https://www.pinterest.com/login/", timeout=30000, wait_until="domcontentloaded")
    
    if not dry_run:
        for _ in range(60):
            await page.wait_for_timeout(5000)
            if await page.query_selector(selectors):
                log("[LOGIN] Login detected!")
                break
            log("[LOGIN] Waiting... (please log in the Edge window)")
    
    await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    logged_in = await page.query_selector(selectors)
    
    if logged_in:
        log("[OK] Login successful! Cookies saved in dedicated profile.")
        return True
    else:
        log("[WARN] Login may not have succeeded - will try anyway")
        return False


async def publish_via_edge(dry_run=False):
    from playwright.async_api import async_playwright
    
    config = load_config()
    queue = load_queue()
    
    if not queue:
        log("[SKIP] No pins to publish")
        return 0
    
    log(f"[PUBLISH] {len(queue)} pins queued")
    EDGE_PROFILE.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        log(f"[CDP] Connecting to Edge on port {CDP_PORT}...")
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        
        # Create fresh context/page (avoid detached frame)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Los_Angeles",
        )
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        # Check/fix login
        if not await ensure_login(page, config, dry_run):
            if dry_run:
                log("[DRY] Login required - skipping")
                return 0
            log("[WARN] Proceeding without confirmed login...")
        
        posted = 0
        failed = 0
        
        for i, pin in enumerate(queue):
            if dry_run:
                log(f"[DRY RUN] [{i+1}/{len(queue)}] {pin['title'][:60]}")
                continue
            
            log(f"[PIN] [{i+1}/{len(queue)}] {pin['title'][:50]}...")
            
            try:
                ok = await create_pin_edge(page, pin, config)
                if ok:
                    posted += 1
                    log(f"  [OK]")
                else:
                    failed += 1
                    log(f"  [FAIL]")
            except Exception as e:
                failed += 1
                log(f"  [ERROR] {e}")
            
            if i < len(queue) - 1:
                delay = random.randint(4000, 8000)
                log(f"  [WAIT] {delay//1000}s")
                await page.wait_for_timeout(delay)
        
        log(f"[DONE] Posted: {posted}, Failed: {failed}")
    
    if not dry_run and posted > 0:
        QUEUE_FILE.unlink(missing_ok=True)
        log("[CLEAN] Queue cleared")
    
    return posted


async def create_pin_edge(page, pin, config):
    try:
        await page.goto("https://www.pinterest.com/", timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 3500))
        
        # Create button
        create_btn = await page.query_selector(
            '[data-test-id="addPinButton"], '
            '[data-test-id="header-create-menu-button"], '
            'button[aria-label="Create Pin"], '
            'button:has-text("Create")'
        )
        if not create_btn:
            log("  [WARN] No Create button")
            return False
        
        await create_btn.click()
        await page.wait_for_timeout(1500)
        
        # "Create Pin" menu
        pin_menu = await page.query_selector(
            '[data-test-id="create-pin"], '
            'div[role="menuitem"]:has-text("Pin"), '
            'span:has-text("Create Pin")'
        )
        if pin_menu:
            await pin_menu.click()
        await page.wait_for_timeout(2500)
        
        # Upload image
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
            log("  [WARN] No file input")
            await page.screenshot(path=str(SCRIPT_DIR / "edge_debug.png"))
            return False
        
        # Title
        title_el = await page.query_selector(
            'h1[contenteditable], '
            '[data-test-id="pin-title"], '
            '#pin-title, '
            '[contenteditable="true"][role="textbox"]'
        )
        if not title_el:
            # Pinterest v5 sometimes uses a different layout
            title_el = await page.query_selector('[contenteditable="true"]')
        if title_el:
            await title_el.click()
            await title_el.fill("")
            await title_el.type(pin["title"][:100], delay=50)
            await page.wait_for_timeout(800)
        
        # Description
        desc_el = await page.query_selector(
            '[data-test-id="pin-description"], '
            '#pin-description, '
            '[id*="description"]'
        )
        if desc_el:
            desc_text = pin.get("description", "")[:400] + config["pin_template"]["description_suffix"]
            await desc_el.click()
            await desc_el.fill(desc_text)
            await page.wait_for_timeout(800)
        
        # Link
        link_el = await page.query_selector(
            '[data-test-id="pin-link"], '
            '#pin-link, '
            '[id*="link"], '
            'input[placeholder*="link"], '
            'input[placeholder*="URL"]'
        )
        if link_el:
            await link_el.click()
            await link_el.fill(pin["url"])
            await page.wait_for_timeout(800)
        
        # Board selector
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
        except:
            pass
        
        # Save/Publish button
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
            log("  [WARN] No Save button found")
            await page.screenshot(path=str(SCRIPT_DIR / "edge_debug.png"))
            return False
            
    except Exception as e:
        log(f"  [ERROR] {e}")
        await page.screenshot(path=str(SCRIPT_DIR / "edge_debug.png"))
        return False


if __name__ == "__main__":
    import asyncio, argparse
    
    parser = argparse.ArgumentParser(description="Pinterest Edge CDP Automation")
    parser.add_argument("--mode", choices=["publish", "dry-run"], default="publish")
    args = parser.parse_args()
    
    edge_proc = launch_edge()
    if not edge_proc:
        log("[FATAL] Cannot start Edge")
        sys.exit(1)
    
    try:
        dry = (args.mode == "dry-run")
        n = asyncio.run(publish_via_edge(dry_run=dry))
        log(f"[FINAL] {n} pins published")
    finally:
        log("[CLOSE] Shutting down Edge...")
        try:
            edge_proc.terminate()
            edge_proc.wait(timeout=10)
        except:
            edge_proc.kill()
        log("[CLOSE] Done")
