import asyncio, subprocess, time, json, os, urllib.request, random
from pathlib import Path

SCRIPT_DIR = Path(r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化")
REAL_PROFILE = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data"
CDP_PORT = 9227
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.isfile(EDGE):
    EDGE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

# Kill any lingering Edge
import subprocess as sp
sp.run(["taskkill", "/f", "/im", "msedge.exe"], capture_output=True)
time.sleep(2)

print("[LAUNCH] Starting Edge CDP...")
proc = subprocess.Popen([
    EDGE,
    f"--remote-debugging-port={CDP_PORT}",
    f"--user-data-dir={REAL_PROFILE}",
    "--no-first-run", "--no-default-browser-check",
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
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")

        # Use default context (has cookies)
        ctx = browser.contexts[0]
        cookies = await ctx.cookies()
        pc = [c for c in cookies if "pinterest" in c.get("domain", "")]
        auth = next((c for c in pc if c["name"] == "_auth"), None)
        print(f"[COOKIES] {len(pc)} Pinterest cookies, _auth={auth.get('value','?')[:20] if auth else 'NONE'}...")

        # Create a NEW page in the default context (inherits cookies)
        page = await ctx.new_page()
        
        # Inject stealth BEFORE navigation
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.chrome = { runtime: {}, loadTimes: function(){}, csi: function(){}, app: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'zh-CN'] });
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            const q = window.navigator.permissions.query;
            window.navigator.permissions.query = (p) => (p.name === 'notifications' ? Promise.resolve({state: Notification.permission}) : q(p));
        """)
        page.set_default_timeout(30000)

        # Navigate to Pinterest (should use cookies from the context)
        print("[CHECK] Navigating to Pinterest...")
        await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"], [data-test-id="addPinButton"]'
        logged_in = await page.query_selector(selectors)
        
        print(f"URL: {page.url}")
        title = await page.title()
        print(f"Title: {title}")
        print(f"Logged in: {logged_in is not None}")

        if not logged_in:
            await page.screenshot(path=str(SCRIPT_DIR / "cdp_direct_test.png"))
            print("[FAIL] Not logged in - may need manual login step in CDP window")
            await browser.close()
            proc.terminate()
            return 0

        print("[OK] LOGGED IN via CDP!")

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
        await browser.close()
        return posted

result = asyncio.run(main())

print("[CLOSE] Shutting down Edge...")
proc.terminate()
proc.wait(timeout=10)
print(f"[FINAL] Published: {result}")
