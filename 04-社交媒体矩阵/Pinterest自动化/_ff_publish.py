import asyncio, subprocess, time, json, os, urllib.request
from pathlib import Path

EDGE_PROFILE = r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\edge_pin_profile"
CDP_PORT = 9224
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

async def extract_and_publish():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        # Step 1: Connect to Edge CDP and read cookies
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        ctx = browser.contexts[0]
        all_cookies = await ctx.cookies()

        # Filter Pinterest cookies
        pc = [c for c in all_cookies if "pinterest" in c.get("domain", "")]
        print(f"\n[COOKIES] Extracted {len(pc)} Pinterest cookies from Edge CDP:")
        for c in pc:
            val = c.get("value", "")[:50]
            print(f"  {c['domain']:30s} | {c['name']:25s} = {val}...")

        await browser.close()

        if not pc:
            print("[ERROR] No Pinterest cookies found")
            return 0

        # Step 2: Launch Firefox and inject cookies
        print("\n[FIREFOX] Launching Firefox...")
        browser_ff = await p.firefox.launch(
            headless=False,
            firefox_user_prefs={
                "dom.webdriver.enabled": False,
                "useAutomationExtension": False,
            }
        )
        ctx_ff = await browser_ff.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Los_Angeles",
        )

        # Inject cookies
        await ctx_ff.add_cookies(pc)
        print(f"[FIREFOX] Injected {len(pc)} cookies")

        page = await ctx_ff.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.chrome = { runtime: {} };
        """)

        print("[CHECK] Testing Pinterest login in Firefox...")
        await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"]'
        logged_in = await page.query_selector(selectors)

        print(f"URL: {page.url}")
        print(f"Logged in: {logged_in is not None}")

        if not logged_in:
            await page.screenshot(path=r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\ff_test.png")
            print("[FAIL] Not logged in via Firefox either - cookies likely expired")
            await browser_ff.close()
            return 0

        print("[OK] Logged in via Firefox!")

        # Step 3: Publish queue
        import sys
        sys.path.insert(0, r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化")
        from publish_now import load_config, load_queue, create_pin, log

        config = load_config()
        queue = load_queue()

        log(f"[PUBLISH] {len(queue)} pins ready")

        posted = 0
        failed = 0
        import random

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

result = asyncio.run(extract_and_publish())

print("[CLOSE] Shutting down Edge...")
proc.terminate()
proc.wait(timeout=10)
print(f"[FINAL] {result} pins published")
