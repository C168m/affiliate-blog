import re

f = r"D:\AI-Money-Machine\04-社交媒体矩阵\Pinterest自动化\pinterest_edge.py"
with open(f, "r", encoding="utf-8") as fh:
    content = fh.read()

# Fix 1: selectors tuple -> single string
old_sel = """    selectors = (
        '[data-test-id="header-create-menu-button"], '
        '[aria-label="Create"], '
        'button[aria-label="Create Pin"], '
        '[data-test-id="addPinButton"]'
    )"""
new_sel = """    selectors = '[data-test-id="header-create-menu-button"], [aria-label="Create"], button[aria-label="Create Pin"], [data-test-id="addPinButton"]'"""

if old_sel in content:
    content = content.replace(old_sel, new_sel)
    print("[OK] selectors fixed to single string")
else:
    print("[WARN] selectors pattern not found")

# Fix 2: CDP page handling
old_cdp = """        contexts = browser.contexts
        if contexts:
            page = contexts[0].pages[0] if contexts[0].pages else await contexts[0].new_page()
        else:
            page = await browser.new_page()
        
        # Check/fix login"""
new_cdp = """        # Create fresh context/page (avoid detached frame)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/Los_Angeles",
        )
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        # Check/fix login"""

if old_cdp in content:
    content = content.replace(old_cdp, new_cdp)
    print("[OK] CDP page handling fixed")
else:
    print("[WARN] CDP pattern not found")

with open(f, "w", encoding="utf-8") as fh:
    fh.write(content)

print("[DONE] File updated")
