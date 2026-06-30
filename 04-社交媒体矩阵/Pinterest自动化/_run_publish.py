import asyncio, subprocess, time, json, os, urllib.request, random
from pathlib import Path

SCRIPT_DIR = Path(r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化")
EDGE_PROFILE = str(SCRIPT_DIR / "edge_pin_profile")
CDP_PORT = 9225
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.isfile(EDGE):
    EDGE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

print("[LAUNCH] Starting Edge CDP...")
proc = subprocess.Popen([
    EDGE,
    f"--remote-debugging-port={CDP_PORT}",
    f"--user-data-dir={EDGE_PROFILE}",
    "--no-first-run", "--no-default-browser-check",
    "--new-window", "about:blank",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for i in range(20):
    time.sleep(1.5)
    try:
        resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/version", timeout=3)
        data = json.loads(resp.read())
        print(f"[LAUNCH] Edge ready: {data.get('Browser', '')[:60]}")
        break
    except:
        pass

async def main():
    from playwright.async_api import async_playwright
    import sys
    sys.path.insert(0, str(SCRIPT_DIR))
    from publish_now import load_config, load_queue, create_pin, log

    async with async_playwright() as p:
        # Extract cookies from Edge CDP
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        ctx = browser.contexts[0]
        all_cookies = await ctx.cookies()
        pc = [c for c in all_cookies if "pinterest" in c.get("domain", "")]
        await browser.close()

        # Check _auth freshness
        auth = next((c for c in pc if c["name"] == "_auth"), None)
        auth_val = auth.get("value", "") if auth else "NOT FOUND"
        print(f"\n[CHECK] _auth cookie value: {auth_val[:80]}...")
        if auth_val in ("0", "", "NOT FOUND"):
            print("[ERROR] _auth is empty/expired - cookies still stale!")
            proc.terminate()
            return 0

        print("[OK] _auth looks fresh!")

        # Launch Firefox with cookies
        browser_ff = await p.firefox.launch(
            headless=False,
            firefox_user_prefs={"dom.webdriver.enabled": False, "useAutomationExtension": False}
        )
        ctx_ff = await browser_ff.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Los_Angeles",
        )
        await ctx_ff.add_cookies(pc)
        print(f"[FIREFOX] Injected {len(pc)} cookies")

        page = await ctx_ff.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.chrome = { runtime: {} };
        """)

        await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"]'
        logged_in = await page.query_selector(selectors)

        if not logged_in:
            print("[FAIL] Still not logged in with fresh cookies")
            await page.screenshot(path=str(SCRIPT_DIR / "ff_fresh_test.png"))
            await browser_ff.close()
            proc.terminate()
            return 0

        print("[OK] LOGGED IN!")

        # Publish
        config = load_config()
        queue = load_queue()
        log(f"[PUBLISH] {len(queue)} pins")

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
            except Exception as e:
                failed += 1
                log(f"  [ERROR] {e}")
            if i < len(queue) - 1:
                delay = random.randint(4000, 8000)
                log(f"  [WAIT] {delay//1000}s")
                await page.wait_for_timeout(delay)

        log(f"[DONE] Posted: {posted}, Failed: {failed}")
        await browser_ff.close()
        return posted

result = asyncio.run(main())

print("[CLOSE] Shutting down Edge...")
proc.terminate()
proc.wait(timeout=10)
print(f"[FINAL] Published: {result}")
