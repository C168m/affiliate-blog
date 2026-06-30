#!/usr/bin/env python3
"""
Pinterest 自动化发布脚本
功能: 抓取 pickedtested.com 新文章 → 生成 Pin 图 → 自动发布到 Pinterest
"""

import json, os, sys, time, re, io, random, hashlib
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')
# ============================================================
# 配置
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
TRACKING_FILE = SCRIPT_DIR / "pinned_articles.json"
IMAGES_DIR = SCRIPT_DIR / "pin_images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_tracking():
    with open(TRACKING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tracking(data):
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ============================================================
# 文章抓取
# ============================================================
def fetch_html(url, timeout=15):
    """抓取页面 HTML"""
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] 抓取失败 {url}: {e}")
        return None

def parse_article_list(html):
    """从首页/Blog页解析文章列表"""
    articles = []
    pattern = re.compile(
        r'<h2><a href="([^"]+)">([^<]+)</a></h2>.*?<p>([^<]+)</p>',
        re.DOTALL
    )
    for m in pattern.finditer(html):
        href = m.group(1)
        title = m.group(2).replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&")
        excerpt = m.group(3).strip()
        if href.endswith(".html") and "privacy" not in href:
            articles.append({
                "url": f"https://pickedtested.com{href}" if href.startswith("/") else href,
                "title": title,
                "excerpt": excerpt
            })
    return articles

def parse_article_detail(html):
    """从文章详情页提取标题、描述"""
    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    title = h1_match.group(1).replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&") if h1_match else ""

    # 提取第一段实质内容作为描述
    p_matches = re.findall(r'<p[^>]*>([^<]{80,400})</p>', html)
    description = p_matches[0].strip() if p_matches else ""

    return {"title": title, "description": description}

# ============================================================
# Pin 图片生成
# ============================================================
def generate_pin_image(article, index):
    """生成 Pinterest 风格的 Pin 图片 (2:3 比例)"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("  [WARN] Pillow 未安装，跳过图片生成")
        return None

    width, height = 1000, 1500

    # 品牌配色方案 (5种风格轮换)
    color_schemes = [
        {"bg": (26, 26, 46), "accent": (231, 76, 60), "text": (255, 255, 255), "sub": (200, 200, 210)},
        {"bg": (18, 52, 86), "accent": (241, 196, 15), "text": (255, 255, 255), "sub": (180, 210, 240)},
        {"bg": (39, 55, 70), "accent": (46, 204, 113), "text": (255, 255, 255), "sub": (190, 210, 200)},
        {"bg": (58, 28, 44), "accent": (255, 152, 0), "text": (255, 255, 255), "sub": (220, 190, 200)},
        {"bg": (20, 40, 30), "accent": (52, 152, 219), "text": (255, 255, 255), "sub": (180, 200, 210)},
    ]
    scheme = color_schemes[index % len(color_schemes)]

    img = Image.new("RGB", (width, height), scheme["bg"])
    draw = ImageDraw.Draw(img)

    # 顶部品牌条
    draw.rectangle([(0, 0), (width, 80)], fill=scheme["accent"])

    # 品牌名
    try:
        font_brand = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 36)
        font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 42)
        font_desc = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    except:
        font_brand = ImageFont.load_default()
        font_title = font_desc = font_tag = font_brand

    draw.text((60, 18), "PICKEDTESTED", fill=(255, 255, 255), font=font_brand)
    draw.text((width - 180, 22), "★ REVIEW", fill=(255, 255, 255), font=font_tag)

    # 标题区域
    title = article.get("title", "Product Review")
    # 自动换行标题
    words = title.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font_title)
        if bbox[2] - bbox[0] < width - 120:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word
    if current_line:
        lines.append(current_line.strip())

    y_start = 200
    for i, line in enumerate(lines[:5]):  # 最多5行
        draw.text((60, y_start + i * 60), line, fill=scheme["text"], font=font_title)

    # 分类标签
    tag_text = "PRODUCT REVIEW"
    bbox_tag = draw.textbbox((0, 0), tag_text, font=font_tag)
    tag_w = bbox_tag[2] - bbox_tag[0] + 30
    tag_y = 600
    draw.rounded_rectangle([(60, tag_y), (60 + tag_w, tag_y + 44)], radius=22, fill=scheme["accent"])
    draw.text((75, tag_y + 8), tag_text, fill=(255, 255, 255), font=font_tag)

    # 底部描述区
    desc_y = 750
    draw.rectangle([(40, desc_y), (width - 40, desc_y + 2)], fill=scheme["accent"])

    desc_lines = ["Honest, hands-on review with pros & cons.", "Find the best price on Amazon →"]
    for i, line in enumerate(desc_lines):
        draw.text((60, desc_y + 30 + i * 40), line, fill=scheme["sub"], font=font_desc)

    # 底部 CTA
    cta_y = 1300
    draw.rounded_rectangle([(200, cta_y), (800, cta_y + 60)], radius=30, fill=scheme["accent"])
    draw.text((260, cta_y + 12), "READ FULL REVIEW →", fill=(255, 255, 255), font=font_brand)

    # URL 水印
    draw.text((60, 1450), "pickedtested.com", fill=scheme["sub"], font=font_desc)

    # 保存
    safe_name = re.sub(r'[^\w\s-]', '', article.get("title", "pin"))[:60].strip().replace(" ", "_")
    img_path = IMAGES_DIR / f"pin_{index}_{safe_name}.png"
    img.save(img_path, "PNG")
    print(f"  [ART] 生成 Pin 图: {img_path.name}")
    return str(img_path)

# ============================================================
# Pinterest 发布
# ============================================================
async def post_to_pinterest(page, article, image_path, config):
    """使用 Playwright 发布一个 Pin"""
    try:
        # Step 1: 打开 Pinterest 首页
        print(f"  [NAV] 打开 Pinterest...")
        await page.goto("https://www.pinterest.com/", timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Step 2: 点击右上角 "+" 按钮
        create_btn = await page.query_selector('[data-test-id="addPinButton"], [aria-label="Create"], button:has-text("Create")')
        if not create_btn:
            # 备用选择器
            create_btn = await page.query_selector('button[aria-label="Create Pin"]')
        if not create_btn:
            create_btn = await page.query_selector('[data-test-id="header-create-menu-button"]')

        if create_btn:
            await create_btn.click()
            await page.wait_for_timeout(1000)
        else:
            print("  [WARN] 找不到 Create 按钮，可能未登录")
            return False

        # Step 3: 点击 "Create Pin" 选项
        pin_option = await page.query_selector('text="Create Pin", [data-test-id="create-pin"]')
        if pin_option:
            await pin_option.click()
            await page.wait_for_timeout(2000)

        # Step 4: 上传图片
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(image_path)
            await page.wait_for_timeout(3000)
            print(f"  [UPLOAD] 上传图片: {Path(image_path).name}")
        else:
            print("  [WARN] 找不到文件上传输入框")
            return False

        # Step 5: 填写标题
        title_input = await page.query_selector('[data-test-id="pin-title"], #pin-title, [id*="title"]')
        if not title_input:
            title_input = await page.query_selector('[contenteditable="true"]')
        if title_input:
            await title_input.click()
            await title_input.fill(article["title"][:100])
            print(f"  [EDIT] 标题: {article['title'][:60]}...")

        # Step 6: 填写描述
        desc_input = await page.query_selector('[data-test-id="pin-description"], #pin-description, [id*="description"]')
        if desc_input:
            desc = article.get("description", "")[:400]
            desc += config["pin_template"]["description_suffix"]
            await desc_input.click()
            await desc_input.fill(desc)
            print(f"  [NOTE] 描述已填写")

        # Step 7: 填写链接
        link_input = await page.query_selector('[data-test-id="pin-link"], #pin-link, [id*="link"], input[placeholder*="link"], input[placeholder*="URL"]')
        if link_input:
            await link_input.click()
            await link_input.fill(article["url"])
            print(f"  [LINK] 链接: {article['url']}")

        # Step 8: 选择 Board (可选)
        board_btn = await page.query_selector('[data-test-id="board-selector"], button:has-text("Board")')
        if board_btn:
            await board_btn.click()
            await page.wait_for_timeout(1000)
            board_option = await page.query_selector(f'text="{config["pinterest_board"]}"')
            if board_option:
                await board_option.click()

        # Step 9: 点击发布
        await page.wait_for_timeout(1000)
        publish_btn = await page.query_selector('button:has-text("Save"), button:has-text("Publish"), [data-test-id="board-dropdown-save-button"], [data-test-id="pin-builder-save"], [data-test-id="create-pin-done"]')
        if publish_btn:
            await publish_btn.click()
            await page.wait_for_timeout(3000)
            print(f"  [OK] Pin 发布成功!")
            return True
        else:
            print("  [WARN] 找不到发布按钮")
            return False

    except Exception as e:
        print(f"  [ERROR] 发布异常: {e}")
        return False

# ============================================================
# 主流程
# ============================================================
def main_sync():
    """同步部分：抓取 + 生成图片"""
    print("=" * 60)
    print(f"[PIN] Pinterest 自动化 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    config = load_config()
    tracking = load_tracking()
    pinned_urls = set(tracking.get("pinned", []))

    # 1. 抓取文章列表
    print("\n[SEARCH] 抓取 pickedtested.com 文章列表...")
    html = fetch_html(f"{config['site_url']}/blog")
    if not html:
        html = fetch_html(config["site_url"])
    if not html:
        print("[ERROR] 无法访问网站")
        return []

    articles = parse_article_list(html)
    print(f"  [INFO] 发现 {len(articles)} 篇文章")

    # 2. 过滤已发布
    new_articles = [a for a in articles if a["url"] not in pinned_urls]
    print(f"  [NEW] 未发布: {len(new_articles)} 篇")

    if not new_articles:
        print("  [OK] 没有新文章，无需操作")
        tracking["last_run"] = datetime.now().isoformat()
        save_tracking(tracking)
        return []

    # 3. 抓取每篇文章详情
    print("\n[READ] 抓取文章详情...")
    for article in new_articles:
        detail_html = fetch_html(article["url"])
        if detail_html:
            detail = parse_article_detail(detail_html)
            article["title"] = detail["title"] or article["title"]
            article["description"] = detail["description"] or article["excerpt"]
        time.sleep(1)

    # 4. 生成 Pin 图片
    print("\n[ART] 生成 Pin 图片...")
    for i, article in enumerate(new_articles[:config["pin_batch_size"]]):
        img_path = generate_pin_image(article, i)
        article["image_path"] = img_path

    # 5. 不在此处标记已发布（发布成功后再标记）
    # 保存待发布列表供发布使用
    queue_file = SCRIPT_DIR / "publish_queue.json"
    queue = [a for a in new_articles[:config["pin_batch_size"]] if a.get("image_path")]
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    print(f"\n[STATS] 准备发布: {len(queue)} 个 Pin")
    return queue

# ============================================================
# 异步发布部分
# ============================================================
async def publish_all(headless=False):
    """使用 Playwright 发布所有待发 Pin"""
    queue_file = SCRIPT_DIR / "publish_queue.json"
    if not queue_file.exists():
        print("[LIST] 没有待发布的 Pin")
        return

    with open(queue_file, "r", encoding="utf-8") as f:
        queue = json.load(f)

    if not queue:
        print("[LIST] 发布队列为空")
        return

    print(f"\n{'=' * 60}")
    print(f"[PUBLISH] 开始发布 {len(queue)} 个 Pin 到 Pinterest")
    print(f"{'=' * 60}")

    config = load_config()

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[ERROR] 请安装 playwright: pip install playwright")
        return

    # 使用 Playwright Chromium 专属 profile（不跟 Edge 抢锁）
    edge_profile = os.path.join(str(SCRIPT_DIR), "edge_work_profile")
    os.makedirs(edge_profile, exist_ok=True)

    async with async_playwright() as p:
        # 用 Edge 持久化上下文 — 登录一次后 Cookie 永久保存
        browser = await p.chromium.launch_persistent_context(
            edge_profile,
            channel="msedge",
            headless=headless,
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        # 检查登录状态
        print("[BROWSER] 正在打开 Pinterest（首次加载可能需要 10-30 秒）...")
        try:
            await page.goto("https://www.pinterest.com/", timeout=30000, wait_until="domcontentloaded")
            print(f"[BROWSER] 页面加载成功: {page.url}")
        except Exception as e:
            print(f"[ERROR] 页面加载失败: {e}")
            print("[ERROR] 请检查网络连接，确保能访问 pinterest.com")
            print("[ERROR] 浏览器窗口将保持打开，请手动检查")
            input("按 Enter 关闭浏览器...")
            await browser.close()
            return

        await page.wait_for_timeout(3000)

        logged_in = await page.query_selector('[data-test-id="header-create-menu-button"], [aria-label="Create"], button:has-text("Create")')
        if not logged_in:
            print("\n[WARN] 未检测到登录状态。")
            print("   （如果是第一次运行，这是正常的，需要手动登录一次）")
            print("   请在打开的浏览器中手动登录 Pinterest")
            print("   账号: hhhf10151@gmail.com")
            print("   登录方式: 直接用邮箱密码登录（不要用 Google 登录避免弹窗问题）")
            print("   登录完成后按 Enter 继续...")
            input()
            print("[INFO] 重新检查登录状态...")
            await page.goto("https://www.pinterest.com/", timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            logged_in = await page.query_selector('[data-test-id="header-create-menu-button"], [aria-label="Create"], button:has-text("Create")')
            if logged_in:
                print("[OK] 登录成功！Cookie 已保存，下次自动登录")
            else:
                print("[WARN] 仍然未检测到登录，但继续尝试发布...")

        # 逐个发布
        posted = 0
        for i, article in enumerate(queue):
            print(f"\n[PIN] [{i+1}/{len(queue)}] {article['title'][:60]}...")
            success = await post_to_pinterest(page, article, article["image_path"], config)
            if success:
                posted += 1
            # 间隔避免被限流
            await page.wait_for_timeout(random.randint(3000, 6000))

        await browser.close()
        print(f"\n{'=' * 60}")
        print(f"[OK] 完成! 成功发布 {posted}/{len(queue)} 个 Pin")
        print(f"{'=' * 60}")

    # 清理队列
    queue_file.unlink(missing_ok=True)

# ============================================================
# CLI 入口
# ============================================================
if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(description="Pinterest 自动化发布")
    parser.add_argument("--mode", choices=["scrape", "publish", "full"], default="full",
                        help="scrape: 抓取+生成图片 | publish: 发布已有图片 | full: 完整流程")
    parser.add_argument("--headless", action="store_true", help="无头模式")

    args = parser.parse_args()

    if args.mode == "scrape":
        queue = main_sync()
        print(f"\n[OK] 抓取完成，{len(queue)} 个 Pin 已就绪")
        print("运行 --mode publish 来发布")

    elif args.mode == "publish":
        asyncio.run(publish_all(headless=args.headless))

    elif args.mode == "full":
        queue = main_sync()
        if queue:
            asyncio.run(publish_all(headless=args.headless))
        else:
            print("[OK] 没有新内容需要发布")
