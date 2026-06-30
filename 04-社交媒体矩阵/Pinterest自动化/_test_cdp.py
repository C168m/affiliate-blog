import asyncio, subprocess, time, json, os, urllib.request
from pathlib import Path

EDGE_PROFILE = r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\edge_pin_profile"
CDP_PORT = 9223
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.isfile(EDGE):
    EDGE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

print("[LAUNCH] Starting Edge CDP...")
proc = subprocess.Popen([
    EDGE,
    f"--remote-debugging-port={CDP_PORT}",
    f"--user-data-dir={EDGE_PROFILE}",
    "--no-first-run",
    "--no-default-browser-check",
    "--new-window",
    "about:blank",
])

for i in range(20):
    time.sleep(1.5)
    try:
        resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/version", timeout=3)
        data = json.loads(resp.read())
        print(f"[LAUNCH] Edge ready: {data.get('Browser', '')[:60]}")
        break
    except:
        pass

async def test():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        
        # KEY: use default context (has profile cookies), NOT new_context()
        contexts = browser.contexts
        print(f"Existing contexts: {len(contexts)}")
        if contexts:
            ctx = contexts[0]
            print(f"Using default context: {ctx}")
        else:
            ctx = await browser.new_context()
        
        pages = ctx.pages
        if pages:
            page = pages[0]
        else:
            page = await ctx.new_page()
        
        await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        title = await page.title()
        url = page.url
        print(f"URL: {url}")
        print(f"Title: {title}")
        
        selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"], [data-test-id="addPinButton"]'
        logged_in = await page.query_selector(selectors)
        print(f"Logged in: {logged_in is not None}")
        
        if not logged_in:
            await page.screenshot(path=r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\cdp_test.png")
        
        # Also check cookies directly
        cookies = await ctx.cookies("https://www.pinterest.com")
        pinterest_cookies = [c for c in cookies if "pinterest" in c.get("domain", "")]
        print(f"Pinterest cookies in context: {len(pinterest_cookies)}")
        for c in pinterest_cookies[:3]:
            print(f"  {c['name']} = {c.get('value', '')[:30]}...")
        
        await browser.close()

asyncio.run(test())
print("[CLOSE] Shutting down Edge...")
proc.terminate()
proc.wait(timeout=10)
print("[DONE]")
