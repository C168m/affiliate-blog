#!/usr/bin/env python3
"""
Pinterest CDP 自动化 - 通过 Chrome DevTools Protocol 连接真实 Chrome
使用 Chrome Profile 6 的已有 Pinterest 登录态，无需重新登录
"""

import json, os, sys, time, random, subprocess, signal
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
QUEUE_FILE = SCRIPT_DIR / "publish_queue.json"
LOG_FILE = SCRIPT_DIR / "auto_pin.log"
CDP_PORT = 9222

sys.stdout.reconfigure(encoding="utf-8")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def find_chrome():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in paths:
        if os.path.isfile(p):
            return p
    raise FileNotFoundError("Chrome not found")


def kill_chrome():
    log("[KILL] Closing existing Chrome instances...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True, timeout=10)
        time.sleep(3)
    except:
        pass


def launch_chrome(chrome_path, profile="Profile 6"):
    log(f"[LAUNCH] Starting Chrome with Profile: {profile} on port {CDP_PORT}...")
    
    user_data = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    
    cmd = [
        chrome_path,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data}",
        f"--profile-directory={profile}",
        "--no-first-run",
        "--no-default-browser-check",
        "about:blank",
    ]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    
    # Wait for Chrome to start
    for i in range(15):
        time.sleep(1.5)
        try:
            import urllib.request
            resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/version", timeout=3)
            data = json.loads(resp.read())
            if "Browser" in data:
                log(f"[LAUNCH] Chrome ready: {data.get('Browser', '')[:60]}")
                return proc
        except:
            pass
    
    log("[ERROR] Chrome failed to start within timeout")
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


async def publish_via_cdp(dry_run=False):
    from playwright.async_api import async_playwright
    
    config = load_config()
    queue = load_queue()
    
    if not queue:
        log("[SKIP] No pins in queue")
        return 0
    
    log(f"[PUBLISH] {len(queue)} pins to publish")
    
    async with async_playwright() as p:
        log(f"[CDP] Connecting to Chrome on port {CDP_PORT}...")
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        
        # The CDP connection gives us existing contexts (with user's login)
        contexts = browser.contexts
        if contexts:
            context = contexts[0]
            pages = context.pages
            page = pages[0] if pages else await context.new_page()
        else:
            page = await browser.new_page()
        
        # Navigate to Pinterest to verify login
        log("[CHECK] Verifying Pinterest login...")
        await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Check if logged in
        logged_in = await page.query_selector(
            '[data-test-id="header-create-menu-button"], '
            '[aria-label="Create"], '
            'button[aria-label="Create Pin"], '
            '[data-test-id="addPinButton"]'
        )
        
        if not logged_in:
            log("[WARN] Not logged into Pinterest in this Chrome profile")
            log("[WARN] Please log in manually in the Chrome window, then press Enter...")
            if not dry_run:
                input()
            await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            logged_in = await page.query_selector('[data-test-id="header-create-menu-button"]')
        
        if not logged_in:
            log("[ERROR] Still not logged in after manual attempt")
            return 0
        
        log("[OK] Pinterest login verified")
        
        posted = 0
        failed = 0
        
        for i, pin in enumerate(queue):
            if dry_run:
                log(f"[DRY RUN] [{i+1}/{len(queue)}] {pin['title'][:60]}")
                continue
            
            log(f"[PIN] [{i+1}/{len(queue)}] {pin['title'][:50]}...")
            
            try:
                success = await create_pin_cdp(page, pin, config)
                if success:
                    posted += 1
                    log(f"  [OK] Published")
                else:
                    failed += 1
                    log(f"  [FAIL] Failed")
            except Exception as e:
                failed += 1
                log(f"  [ERROR] {e}")
            
            if i < len(queue) - 1:
                delay = random.randint(4000, 8000)
                log(f"  [WAIT] {delay//1000}s...")
                await page.wait_for_timeout(delay)
        
        log(f"[DONE] Posted: {posted}, Failed: {failed}")

    if not dry_run and posted > 0:
        QUEUE_FILE.unlink(missing_ok=True)
        log("[CLEAN] Queue cleared")
    
    return posted


async def create_pin_cdp(page, pin, config):
    try:
        await page.goto("https://www.pinterest.com/", timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(random.randint(2000, 3500))
        
        # Click Create button
        create_btn = await page.query_selector(
            '[data-test-id="addPinButton"], '
            '[data-test-id="header-create-menu-button"], '
            'button[aria-label="Create Pin"], '
            'button:has-text("Create")'
        )
        if not create_btn:
            log("  [WARN] No Create button found")
            return False
        
        await create_btn.click()
        await page.wait_for_timeout(1500)
        
        # Click "Create Pin" in dropdown
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
            # Try different approach - maybe the create flow is different
            dropzone = await page.query_selector('[data-test-id="pin-builder-image-dropzone"]')
            if dropzone:
                await dropzone.click()
                await page.wait_for_timeout(2000)
        
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(pin["image_path"])
            await page.wait_for_timeout(random.randint(3000, 5000))
            log(f"  [IMG] Uploaded {Path(pin['image_path']).name}")
        else:
            log("  [WARN] Cannot find file upload")
            await page.screenshot(path=str(SCRIPT_DIR / "cdp_debug.png"))
            return False
        
        # Title
        title_el = await page.query_selector(
            '[data-test-id="pin-title"], '
            '#pin-title, '
            '[id*="title"][contenteditable="true"], '
            '[contenteditable="true"][role="textbox"]'
        )
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
            desc = (pin.get("description", "")[:400] +
                    config["pin_template"]["description_suffix"])
            await desc_el.click()
            await desc_el.fill(desc)
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
        
        # Board
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
            log(f"  [WARN] Board selection: {e}")
        
        # Save
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
            log("  [WARN] No Save button")
            await page.screenshot(path=str(SCRIPT_DIR / "cdp_debug.png"))
            return False
            
    except Exception as e:
        log(f"  [ERROR] {e}")
        try:
            await page.screenshot(path=str(SCRIPT_DIR / "cdp_debug.png"))
        except:
            pass
        return False


if __name__ == "__main__":
    import asyncio, argparse
    
    parser = argparse.ArgumentParser(description="Pinterest CDP Automation")
    parser.add_argument("--mode", choices=["publish", "dry-run"], default="publish")
    parser.add_argument("--profile", default="Profile 6", help="Chrome profile name")
    args = parser.parse_args()
    
    # 1. Kill existing Chrome
    kill_chrome()
    
    # 2. Find Chrome
    chrome_path = find_chrome()
    
    # 3. Launch Chrome with CDP
    proc = launch_chrome(chrome_path, args.profile)
    if not proc:
        log("[FATAL] Cannot start Chrome")
        sys.exit(1)
    
    try:
        # 4. Publish pins
        dry = (args.mode == "dry-run")
        n = asyncio.run(publish_via_cdp(dry_run=dry))
        log(f"[FINAL] Published {n} pins")
    finally:
        # 5. Close our Chrome instance
        log("[CLOSE] Shutting down Chrome...")
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except:
            proc.kill()
        log("[CLOSE] Done")
