#!/usr/bin/env python3
"""
============================================================
AI Money Machine — Blog Affiliate Automation
单一入口 | GitHub Pages部署 | 无需VPN切换

用法:
  python launch.py                    # 启动服务器 + 每日管道
  python launch.py --deploy           # 部署到GitHub Pages
  python launch.py --generate "产品名" # 生成新affiliate文章
  python launch.py --audit            # SEO审计
  python launch.py --set-id TRACK-ID  # 设置Amazon追踪ID并批量替换
============================================================
"""
import json, os, sys, re, shutil, subprocess, time, io
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
BLOG = ROOT / "blog"
CONFIG = ROOT / "blog_config.json"
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
(DATA / "social_posts").mkdir(exist_ok=True)
(DATA / "logs").mkdir(exist_ok=True)

PLACEHOLDER_TAG = "YOUR-TRACKING-ID-20"

# ============================================================
# 配置
# ============================================================
DEFAULTS = {
    "amazon_tracking_id": "",
    "blog_name": "TechGear Picks",
    "blog_tagline": "Expert Reviews & Buying Guides",
    "github_username": "",
    "github_repo": "",
    "domain": "",  # <username>.github.io/<repo> 或自定义域名
    "articles_count": 10,
    "last_deploy": None
}

def cfg():
    if CONFIG.exists():
        c = json.loads(CONFIG.read_text(encoding="utf-8"))
        return {**DEFAULTS, **c}
    return dict(DEFAULTS)

def save_cfg(c):
    CONFIG.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")

def ensure_cfg():
    if not CONFIG.exists():
        save_cfg(DEFAULTS)
    c = cfg()
    if not c.get("domain"):
        if c.get("github_username") and c.get("github_repo"):
            c["domain"] = f"{c['github_username']}.github.io/{c['github_repo']}"
            save_cfg(c)
    return c

# ============================================================
# 实用工具
# ============================================================
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    return line

def run(cmd, cwd=None, timeout=30):
    """运行命令,返回 (returncode, stdout, stderr)"""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          cwd=str(cwd) if cwd else None, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)

# ============================================================
# Blog 服务器
# ============================================================
class Server:
    def __init__(self, port=8080):
        self.port = port
        self.proc = None

    def start(self):
        self.stop()
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(self.port),
             "--directory", str(BLOG), "--bind", "0.0.0.0"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)

    def stop(self):
        if self.proc:
            try: self.proc.terminate()
            except: pass

    def ok(self):
        import urllib.request
        try:
            r = urllib.request.urlopen(f"http://127.0.0.1:{self.port}", timeout=2)
            return r.status == 200
        except: return False

# ============================================================
# Tracking ID 批量替换
# ============================================================
class TagPatcher:
    def __init__(self, tracking_id):
        self.tid = tracking_id

    def patch(self):
        """一键替换所有HTML中的占位符"""
        if not self.tid:
            return {"error": "tracking_id为空"}
        results = []
        for f in BLOG.glob("*.html"):
            c = f.read_text(encoding="utf-8")
            n = c.count(PLACEHOLDER_TAG)
            if n:
                f.write_text(c.replace(PLACEHOLDER_TAG, self.tid), encoding="utf-8")
                results.append({"file": f.name, "replacements": n})
        total = sum(r["replacements"] for r in results)
        return {"files": len(results), "total": total}

    def revert(self):
        """还原占位符"""
        for f in BLOG.glob("*.html"):
            c = f.read_text(encoding="utf-8")
            if self.tid in c:
                f.write_text(c.replace(self.tid, PLACEHOLDER_TAG), encoding="utf-8")
        return {"status": "reverted"}

# ============================================================
# 内容引擎
# ============================================================
ARTICLE_CSS = """:root{--bg:#fff;--text:#1a1a1a;--muted:#666;--accent:#e47911;--link:#0066c0;--border:#e5e5e5}*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:var(--text);background:var(--bg);line-height:1.7}.container{max-width:800px;margin:0 auto;padding:0 20px}header{border-bottom:1px solid var(--border);padding:24px 0;margin-bottom:40px}header h1{font-size:1.6rem;font-weight:700}header h1 a{color:var(--text);text-decoration:none}header p{color:var(--muted);font-size:.9rem;margin-top:4px}nav{margin-top:12px;display:flex;gap:20px}nav a{color:var(--link);text-decoration:none;font-size:.85rem}.btn-amazon{display:inline-block;background:linear-gradient(to bottom,#f7dfa5,#f0c14b);border:1px solid #a88734;border-radius:3px;padding:8px 16px;color:#111;font-weight:600;text-decoration:none;font-size:.9rem}.btn-amazon:hover{background:linear-gradient(to bottom,#f5d78e,#eeb933)}.product-table{width:100%;border-collapse:collapse;margin:20px 0}.product-table th,.product-table td{border:1px solid var(--border);padding:10px 12px;text-align:left}.product-table th{background:#f8f9fa}.pros-cons{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}.pros{color:#2d7d46}.cons{color:#c45500}footer{border-top:1px solid var(--border);margin-top:60px;padding:24px 0;text-align:center;color:var(--muted);font-size:.8rem}.disclosure{background:#fff8f0;border:1px solid #ffe0b2;border-radius:6px;padding:12px 16px;margin:20px 0;font-size:.8rem;color:#b26500}.article-content h1{font-size:1.8rem;margin:0 0 16px 0}.article-content h2{font-size:1.4rem;margin:32px 0 12px 0;padding-bottom:6px;border-bottom:1px solid var(--border)}.article-content h3{font-size:1.1rem;margin:20px 0 8px 0}.article-content p{margin:0 0 16px 0}.article-content ul,.article-content ol{margin:0 0 16px 24px}.article-content li{margin-bottom:6px}.breadcrumb{font-size:.8rem;color:var(--muted);margin-bottom:20px}.breadcrumb a{color:var(--link);text-decoration:none}@media(max-width:600px){.container{padding:0 16px}.pros-cons{grid-template-columns:1fr}}"""

ARTICLE_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} — {blog_name}</title><meta name="description" content="{meta_desc}"><style>{css}</style></head><body><div class="container"><header><h1><a href="/">{blog_name}</a></h1><p>{blog_tagline}</p><nav><a href="/">Home</a> <a href="/disclosure.html">Disclosure</a></nav></header><article class="article-content"><div class="breadcrumb"><a href="/">Home</a> &raquo; {category}</div><div class="disclosure">As an Amazon Associate we earn from qualifying purchases.</div>{body}</article><footer><p>{blog_name} &copy; 2026</p></footer></div></body></html>"""

INDEX_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{blog_name} — Best Tech Reviews 2026</title><meta name="description" content="Expert reviews and buying guides for tech products."><style>{css}</style></head><body><div class="container"><header><h1><a href="/">{blog_name}</a></h1><p>{blog_tagline}</p><nav><a href="/">Home</a> <a href="/disclosure.html">Disclosure</a></nav></header><main><div class="disclosure">As an Amazon Associate we earn from qualifying purchases.</div><div class="article-grid">{cards}</div></main><footer><p>{blog_name} &copy; 2026</p></footer></div></body></html>"""

INDEX_CSS = ":root{--bg:#fff;--text:#1a1a1a;--muted:#666;--accent:#e47911;--link:#0066c0;--border:#e5e5e5}*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:var(--text);background:var(--bg);line-height:1.7}.container{max-width:800px;margin:0 auto;padding:0 20px}header{border-bottom:1px solid var(--border);padding:24px 0;margin-bottom:40px}header h1{font-size:1.6rem;font-weight:700}header h1 a{color:var(--text);text-decoration:none}header p{color:var(--muted);font-size:.9rem;margin-top:4px}nav{margin-top:12px;display:flex;gap:20px}nav a{color:var(--link);text-decoration:none;font-size:.85rem}.hero{margin-bottom:40px}.hero h2{font-size:1.3rem;margin-bottom:8px}.hero p{color:var(--muted)}.article-grid{display:grid;gap:24px}.article-card{border:1px solid var(--border);border-radius:8px;padding:20px;transition:box-shadow .2s}.article-card:hover{box-shadow:0 2px 12px rgba(0,0,0,.08)}.article-card h3{font-size:1.1rem;margin-bottom:6px}.article-card h3 a{color:var(--link);text-decoration:none}.article-card h3 a:hover{text-decoration:underline;color:#c45500}.article-card .meta{font-size:.8rem;color:var(--muted);margin-top:8px}.article-card .tag{display:inline-block;background:#f0f7ff;color:#0066c0;padding:2px 8px;border-radius:4px;font-size:.75rem;margin-right:6px}.disclosure{background:#fff8f0;border:1px solid #ffe0b2;border-radius:6px;padding:12px 16px;margin:20px 0;font-size:.8rem;color:#b26500}footer{border-top:1px solid var(--border);margin-top:60px;padding:24px 0;text-align:center;color:var(--muted);font-size:.8rem}@media(max-width:600px){.container{padding:0 16px}}"

class ContentEngine:
    def __init__(self, config):
        self.c = config
        self.tid = config.get("amazon_tracking_id", "")

    def generate(self, product, category="Electronics", products=None):
        if products is None:
            products = [{"name": f"{product.title()} Pro", "asin": "B0XXXXXXX",
                         "price": "$49.99", "rating": "4.5/5",
                         "pros": ["Excellent quality", "Great value"], "cons": ["Limited options"],
                         "desc": f"Our top recommendation for most people looking for a {product}."}]

        slug = product.lower().replace(" ", "-")
        filename = f"best-{slug}-2026.html"
        title = f"Best {product.title()} 2026 — Top Picks & Buying Guide"
        meta = f"Best {product} 2026 buying guide. Compare top picks, read reviews, and find the right {product} for your needs."
        tid = self.tid

        rows = []
        reviews = []
        for i, p in enumerate(products, 1):
            amz = f"https://www.amazon.com/dp/{p['asin']}/?tag={tid}" if tid else "#"
            rows.append(f'<tr><td>#{i}</td><td><a href="{amz}" rel="nofollow sponsored">{p["name"]}</a></td><td>{p.get("price","N/A")}</td><td>{p.get("rating","N/A")}</td><td><a href="{amz}" class="btn-amazon" rel="nofollow sponsored">Check Price</a></td></tr>')
            pros = "".join(f"<li>{x}</li>" for x in p.get("pros", []))
            cons = "".join(f"<li>{x}</li>" for x in p.get("cons", []))
            reviews.append(f'<h2>{p["name"]}</h2><p>{p.get("desc","")}</p><div class="pros-cons"><div class="pros"><strong>Pros:</strong><ul>{pros}</ul></div><div class="cons"><strong>Cons:</strong><ul>{cons}</ul></div></div><a href="{amz}" class="btn-amazon" rel="nofollow sponsored">Check Price on Amazon</a>')

        body = f"""<h1>Best {product.title()} 2026 — Complete Buying Guide</h1>
<p>Looking for the best {product}? We tested and compared the top options available right now.</p>
<h2>Our Top Picks at a Glance</h2>
<table class="product-table"><thead><tr><th>Rank</th><th>Product</th><th>Price</th><th>Rating</th><th></th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<h2>Detailed Reviews</h2>{"".join(reviews)}
<h2>How to Choose the Best {product.title()}</h2>
<ul><li><strong>Quality:</strong> Look for durable materials and solid construction.</li><li><strong>Value:</strong> Compare features against price for the best deal.</li><li><strong>Reviews:</strong> Check real user feedback for long-term reliability.</li></ul>"""

        html = ARTICLE_HTML.format(title=title, blog_name=self.c["blog_name"],
                                   blog_tagline=self.c["blog_tagline"], meta_desc=meta,
                                   category=category.title(), body=body, css=ARTICLE_CSS)
        filepath = BLOG / filename
        filepath.write_text(html, encoding="utf-8")
        self.rebuild_index()
        self.update_sitemap()
        return filename

    def rebuild_index(self):
        articles = sorted([f for f in BLOG.glob("best-*.html")],
                         key=lambda f: f.stat().st_mtime, reverse=True)
        cards = ""
        for f in articles[:20]:
            name = f.stem.replace("best-","").replace("-2026","").replace("-"," ").title()
            cards += f'<div class="article-card"><span class="tag">Review</span><h3><a href="/{f.name}">{name}</a></h3><p>Buying guide and top picks for {name.lower()}.</p><div class="meta">Updated 2026</div></div>\n'
        html = INDEX_HTML.format(blog_name=self.c["blog_name"],
                                blog_tagline=self.c["blog_tagline"],
                                cards=cards, css=INDEX_CSS)
        (BLOG / "index.html").write_text(html, encoding="utf-8")
        return len(articles)

    def update_sitemap(self):
        domain = self.c.get("domain", "localhost")
        now = datetime.now().strftime("%Y-%m-%d")
        urls = []
        for f in sorted(BLOG.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
            prio = "1.0" if f.name == "index.html" else "0.3" if f.name == "disclosure.html" else "0.8"
            urls.append(f"  <url><loc>https://{domain}/{f.name}</loc><lastmod>{now}</lastmod><priority>{prio}</priority></url>")
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'
        (BLOG / "sitemap.xml").write_text(sitemap, encoding="utf-8")
        (BLOG / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: https://{domain}/sitemap.xml\n", encoding="utf-8")
        return len(urls)

# ============================================================
# SEO 审计
# ============================================================
class SEOAudit:
    def run(self):
        results = []
        for f in BLOG.glob("best-*.html"):
            c = f.read_text(encoding="utf-8")
            issues = []
            tm = re.search(r'<title>(.*?)</title>', c)
            t = tm.group(1) if tm else ""
            if len(t) < 20 or len(t) > 70: issues.append(f"Title {len(t)} chars (ideal 30-60)")
            if PLACEHOLDER_TAG in c: issues.append("CRITICAL: Placeholder tracking ID!")
            amz = len(re.findall(r'amazon\.com', c, re.I))
            if amz < 3: issues.append(f"Only {amz} Amazon links (5-15 recommended)")
            score = max(0, 100 - len(issues) * 20)
            results.append({"file": f.name, "title": t[:80], "amazon_links": amz, "issues": issues, "score": score})
        return results

# ============================================================
# GitHub Pages 部署器
# ============================================================
class Deployer:
    def __init__(self, config):
        self.c = config

    def check(self):
        """检查是否满足部署条件"""
        issues = []
        if not self.c.get("github_username"):
            issues.append("github_username 未设置")
        if not self.c.get("github_repo"):
            issues.append("github_repo 未设置")
        ret, out, err = run("git remote get-url origin")
        if ret != 0:
            issues.append("git remote origin 未配置")
        else:
            log(f"Git remote: {out}")
        return len(issues) == 0, issues

    def deploy(self):
        """部署blog到GitHub Pages (gh-pages分支)"""
        log("=" * 50)
        log("Deploying to GitHub Pages...")

        # 确保sitemap和robots是最新的
        engine = ContentEngine(self.c)
        n = engine.update_sitemap()
        log(f"Sitemap updated: {n} URLs")

        # 使用 git subtree 推送到 gh-pages
        blog_path = str(BLOG)

        # Check if we're in a git repo
        ret, _, _ = run("git rev-parse --show-toplevel")
        if ret != 0:
            return {"error": "Not a git repo. Run: git init" if ret != 0 else "ok"}

        # Add blog changes
        run("git add blog/")

        # Commit (only if there are changes)
        ret, out, _ = run("git diff --cached --quiet blog/")
        if ret == 0 and False:  # no changes
            log("No changes to deploy.")
        else:
            ts = datetime.now().strftime("%Y%m%d-%H%M")
            run(f'git commit -m "blog: auto-deploy {ts}"')

        # Push to gh-pages using subtree
        # Strategy: split blog/ into gh-pages branch
        ret, out, err = run("git subtree split --prefix blog -b gh-pages-temp")
        if ret != 0:
            # Fallback: direct approach
            ret, out, err = run("git push origin --delete gh-pages")
            ret, out, err = run("git subtree push --prefix blog origin gh-pages")
        else:
            run("git push origin gh-pages-temp:gh-pages --force")
            run("git branch -D gh-pages-temp")

        if ret == 0:
            self.c["last_deploy"] = datetime.now().isoformat()
            save_cfg(self.c)
            url = f"https://{self.c['domain']}"
            log(f"Deployed! Visit: {url}")
            log("(It may take 1-2 minutes for GitHub Pages to update)")
            return {"status": "ok", "url": url}
        else:
            return {"error": err}

    def status(self):
        """检查GitHub Pages可访问性"""
        import urllib.request
        url = f"https://{self.c['domain']}"
        try:
            r = urllib.request.urlopen(url, timeout=10)
            return r.status == 200
        except: return False

# ============================================================
# 社交推广
# ============================================================
class SocialQueue:
    def __init__(self, config):
        self.c = config
        (DATA / "social_posts").mkdir(parents=True, exist_ok=True)

    def generate(self, article_file, product_name):
        domain = self.c.get("domain", "localhost")
        url = f"https://{domain}/{article_file}"
        posts = {
            "twitter": [
                f"Best {product_name} 2026 — Complete Buyer's Guide 🔥",
                f"We tested the top {product_name} picks. Here are our honest findings:",
                f"Full comparison & buying guide: {url}"
            ],
            "reddit": {
                "title": f"I spent weeks researching the best {product_name} — here are my honest findings",
                "body": f"Full breakdown with pros/cons for each pick: {url}",
                "subreddits": ["BuyItForLife", "GoodValue", "AmazonBudgetFinds"]
            },
            "pinterest": {
                "title": f"Best {product_name} 2026 — Top Picks & Buying Guide",
                "description": f"Compare the best {product_name} options for 2026. Expert reviews and recommendations.",
                "url": url, "board": f"{product_name.title()} Reviews"
            }
        }
        path = DATA / "social_posts" / f"social_{datetime.now().strftime('%Y%m%d_%H%M')}_{article_file.replace('.html','')}.json"
        path.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
class Pipeline:
    def __init__(self, config):
        self.c = config
        self.logs = []

    def step(self, msg, status="OK"):
        line = f"[{status}] {msg}"
        self.logs.append(line)
        print(line)

    def run(self):
        print("=" * 55)
        print(f"  AI Money Machine — Blog Automation")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 55)

        # 1. Tracking ID check
        tid = self.c.get("amazon_tracking_id", "")
        if tid:
            self.step(f"Tracking ID: {tid}")
        else:
            self.step("Tracking ID: NOT SET (links will use placeholder)", "WARN")

        # 2. Server
        srv = Server()
        srv.start()
        self.step("Blog server" if srv.ok() else "Server FAILED", "OK" if srv.ok() else "ERR")

        # 3. SEO Audit
        results = SEOAudit().run()
        avg = sum(r["score"] for r in results) / max(len(results), 1)
        critical = sum(1 for r in results if any("CRITICAL" in i for i in r["issues"]))
        self.step(f"SEO Audit: {len(results)} articles, avg {avg:.0f}/100" + (f", {critical} critical" if critical else ""))
        for r in results:
            for iss in r["issues"]:
                self.step(f"  {r['file']}: {iss}", "WARN")

        # 4. Sitemap
        engine = ContentEngine(self.c)
        n = engine.update_sitemap()
        self.step(f"Sitemap: {n} URLs")

        # 5. Rebuild index
        n = engine.rebuild_index()
        self.step(f"Homepage: {n} articles listed")

        # 6. Social queue
        articles = sorted(BLOG.glob("best-*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
        sq = SocialQueue(self.c)
        for f in articles[:2]:
            name = f.stem.replace("best-","").replace("-2026","").replace("-"," ")
            p = sq.generate(f.name, name)
            self.step(f"Social queued: {name.title()}")

        # 7. Deploy check
        deployer = Deployer(self.c)
        ready, issues = deployer.check()
        if ready:
            self.step("GitHub Pages: ready to deploy (--deploy)")
        else:
            for i in issues:
                self.step(f"Deploy config: {i}", "WARN")

        # Write log
        logfile = DATA / "logs" / f"daily_{datetime.now().strftime('%Y%m%d')}.json"
        logfile.write_text(json.dumps({
            "date": datetime.now().isoformat(),
            "steps": self.logs,
            "audit": results
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        print("=" * 55)
        print(f"  Done. Log: {logfile.name}")
        print("=" * 55)
        return self.logs

# ============================================================
# Setup 向导
# ============================================================
def interactive_setup():
    """首次设置向导"""
    print("\n" + "=" * 50)
    print("  AI Money Machine — 首次设置")
    print("=" * 50)
    print("\n这个向导会收集必要的配置信息。")
    print("(需要 GitHub 账号和 Amazon Associates 账号，都是 Gmail 即可注册)\n")

    c = ensure_cfg()

    # GitHub username
    gh_user = input(f"GitHub 用户名 [{c.get('github_username','')}]: ").strip()
    if gh_user: c["github_username"] = gh_user
    else: gh_user = c.get("github_username","")

    # GitHub repo
    gh_repo = input(f"GitHub 仓库名 [{c.get('github_repo','')}]: ").strip()
    if gh_repo: c["github_repo"] = gh_repo
    else: gh_repo = c.get("github_repo","")

    if gh_user and gh_repo:
        c["domain"] = f"{gh_user}.github.io/{gh_repo}"

    # Amazon tracking ID
    tid = input(f"Amazon Tracking ID [{c.get('amazon_tracking_id','')}]: ").strip()
    if tid:
        c["amazon_tracking_id"] = tid
        # 立即替换
        result = TagPatcher(tid).patch()
        print(f"\n  [OK] 已替换 {result['total']} 个链接 ({result['files']} 个文件)")

    save_cfg(c)

    # Git setup
    print("\n--- Git 仓库设置 ---")
    ret, out, err = run("git rev-parse --show-toplevel")
    if ret != 0:
        run("git init")
        print("  [OK] git init")
        with open(ROOT / ".gitignore", "w", encoding="utf-8") as f:
            f.write("# AI Money Machine\nlogs/\n*.pyc\n__pycache__/\n.env\ncf_*.txt\ncf_*.json\ndata/logs/\n")
        print("  [OK] .gitignore created")

    ret, out, err = run("git remote get-url origin")
    if ret != 0 and gh_user and gh_repo:
        url = f"https://github.com/{gh_user}/{gh_repo}.git"
        ret, out, err = run(f"git remote add origin {url}")
        if ret == 0:
            print(f"  [OK] Remote added: {url}")
        else:
            print(f"  [WARN] 无法添加remote: {err}")
    elif ret == 0:
        print(f"  [OK] Remote: {out}")

    print("\n" + "=" * 50)
    print("  设置完成！")
    print(f"  Blog URL: https://{c.get('domain','N/A')}")
    print(f"  本地预览: http://localhost:8080")
    print("=" * 50)
    print("\n下一步:")
    print("  1. 在 GitHub 上创建仓库: github.com/new")
    print(f"     仓库名: {c['github_repo']}")
    print("  2. 推送到 GitHub:")
    print(f"     git add . && git commit -m 'init' && git push -u origin main")
    print("  3. 在仓库 Settings > Pages 中启用 GitHub Pages")
    print("     Source: Deploy from a branch → gh-pages (之后自动推送)")
    print("  4. 运行: python launch.py --deploy")

# ============================================================
# CLI
# ============================================================
def main():
    import argparse
    p = argparse.ArgumentParser(description="AI Money Machine — Blog Affiliate Automation")
    p.add_argument("--setup", action="store_true", help="首次设置向导")
    p.add_argument("--deploy", action="store_true", help="部署到GitHub Pages")
    p.add_argument("--audit", action="store_true", help="SEO审计")
    p.add_argument("--generate", type=str, default=None, metavar="PRODUCT", help="生成新文章")
    p.add_argument("--category", type=str, default="Electronics", help="文章分类")
    p.add_argument("--set-id", type=str, default=None, metavar="TRACKING_ID", help="设置Amazon追踪ID")
    p.add_argument("--domain", type=str, default=None, metavar="DOMAIN", help="设置域名")
    p.add_argument("--server", action="store_true", help="仅启动服务器")
    args = p.parse_args()

    c = ensure_cfg()

    if args.setup:
        interactive_setup()
        return

    if args.set_id:
        c["amazon_tracking_id"] = args.set_id
        save_cfg(c)
        result = TagPatcher(args.set_id).patch()
        print(f"[OK] Tracking ID set. Patched {result['total']} links in {result['files']} files.")
        return

    if args.domain:
        c["domain"] = args.domain
        save_cfg(c)
        ContentEngine(c).update_sitemap()
        print(f"[OK] Domain set: {args.domain}")
        return

    if args.deploy:
        deployer = Deployer(c)
        ok, issues = deployer.check()
        if not ok:
            print("部署条件未满足:")
            for i in issues: print(f"  - {i}")
            print("\n运行 --setup 进行配置")
            return
        result = deployer.deploy()
        if "error" in result:
            print(f"Deploy failed: {result['error']}")
        else:
            print(f"Deployed: {result['url']}")
        return

    if args.audit:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        for r in SEOAudit().run():
            s = "[OK]" if r["score"] >= 80 else "[WARN]" if r["score"] >= 60 else "[ERR]"
            print(f"{s} {r['file']} — {r['score']}/100")
            for i in r["issues"]: print(f"  {i}")
        return

    if args.generate:
        engine = ContentEngine(c)
        filename = engine.generate(args.generate, args.category)
        print(f"[OK] Generated: {filename}")
        print(f"  http://localhost:8080/{filename}")
        return

    if args.server:
        srv = Server()
        srv.start()
        print(f"Server: http://localhost:8080")
        print("Press Ctrl+C to stop.")
        try:
            while True: time.sleep(5)
        except KeyboardInterrupt:
            srv.stop()
            print("Stopped.")
        return

    # Default: run daily pipeline
    Pipeline(c).run()

if __name__ == "__main__":
    main()
