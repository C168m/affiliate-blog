import asyncio, sys
from pathlib import Path
sys.path.insert(0, r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化")
from playwright.async_api import async_playwright

EDGE_PROFILE = Path(r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\edge_pin_profile")

async def quick_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            str(EDGE_PROFILE),
            channel="msedge",
            headless=False,
            viewport={"width": 1920, "height": 1080},
            args=["--disable-blink-features=AutomationControlled", "--no-first-run"],
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"], [data-test-id="addPinButton"]'
        logged_in = await page.query_selector(selectors)
        
        title = await page.title()
        url = page.url
        print(f"URL: {url}")
        print(f"Title: {title}")
        print(f"Logged in: {logged_in is not None}")
        
        if logged_in:
            print("COOKIE LOGIN WORKED!")
        else:
            print("NOT LOGGED IN - cookies invalid or expired")
            await page.screenshot(path=r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\cookie_test.png")
        
        await browser.close()

asyncio.run(quick_test())
