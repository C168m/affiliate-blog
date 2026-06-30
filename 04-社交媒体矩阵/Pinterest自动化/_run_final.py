import asyncio, subprocess, time, json, os, urllib.request, random
from pathlib import Path

SCRIPT_DIR = Path(r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化")
REAL_PROFILE = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data"
CDP_PORT = 9226
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.isfile(EDGE):
    EDGE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

print("[LAUNCH] Starting Edge CDP with REAL profile...")
proc = subprocess.Popen([
    EDGE,
    f"--remote-debugging-port={CDP_PORT}",
    f"--user-data-dir={REAL_PROFILE}",
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
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(SCRIPT_DIR))
    from publish_now import load_config, load_queue, create_pin, log

    async with async_playwright() as p:
        # Read cookies from real profile
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        ctx = browser.contexts[0]
        all_cookies = await ctx.cookies()
        pc = [c for c in all_cookies if "pinterest" in c.get("domain", "")]
        print(f"\n[COOKIES] Got {len(pc)} Pinterest cookies from real profile")
        for c in pc:
            print(f"  {c['name']} = {str(c.get('value',''))[:50]}...")

        await browser.close()
        print("[CDP] Edge CDP connection closed")

        if not pc:
            print("[ERROR] No Pinterest cookies - is user logged in?")
            proc.terminate()
            return 0

        auth = next((c for c in pc if c["name"] == "_auth"), None)
        if not auth or auth.get("value", "") in ("0", ""):
            print("[ERROR] _auth is empty!")
            proc.terminate()
            return 0

        print(f"[OK] _auth looks valid: {auth['value'][:30]}...")

        # Launch Firefox with cookies
        print("\n[FIREFOX] Launching Firefox...")
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

        page = await ctx_ff.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.chrome = { runtime: {} };
        """)

        await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"]'
        logged_in = await page.query_selector(selectors)
        print(f"URL: {page.url}")
        print(f"Logged in: {logged_in is not None}")

        if not logged_in:
            await page.screenshot(path=str(SCRIPT_DIR / "ff_real_test.png"))
            print("[FAIL] Not logged in via Firefox")
            await browser_ff.close()
            proc.terminate()
            return 0

        print("[OK] LOGGED IN! Starting publish...")

        config = load_config()
        queue = load_queue()
        log(f"[PUBLISH] {len(queue)} pins queued")

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
