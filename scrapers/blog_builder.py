#!/usr/bin/env python3
"""
Static Blog Generator - SEO-optimized blog from AI-generated articles
Output: static HTML ready for Vercel deployment
"""
import json, os, shutil
from datetime import datetime
from pathlib import Path

ARTICLES_DIR = Path(r"D:\AI-Money-Machine\05-SEO内容站群\articles")
OUTPUT_DIR = Path(r"D:\AI-Money-Machine\blog")
SITE_NAME = "TechGear Picks"
SITE_TAGLINE = "Expert Reviews & Buying Guides"
AMAZON_DISCLOSURE = "As an Amazon Associate we earn from qualifying purchases."

# Clean output
if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True)

# CSS
CSS = """
:root { --bg: #fff; --text: #1a1a1a; --muted: #666; --accent: #e47911; --link: #0066c0; --border: #e5e5e5; }
* { box-sizing:border-box; margin:0; padding:0; }
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; color:var(--text); background:var(--bg); line-height:1.7; }
.container { max-width:800px; margin:0 auto; padding:0 20px; }
header { border-bottom:1px solid var(--border); padding:24px 0; margin-bottom:40px; }
header h1 { font-size:1.6rem; font-weight:700; }
header h1 a { color:var(--text); text-decoration:none; }
header p { color:var(--muted); font-size:.9rem; margin-top:4px; }
nav { margin-top:12px; display:flex; gap:20px; }
nav a { color:var(--link); text-decoration:none; font-size:.85rem; font-weight:500; }
nav a:hover { text-decoration:underline; }
.hero { margin-bottom:40px; }
.hero h2 { font-size:1.3rem; margin-bottom:8px; }
.hero p { color:var(--muted); }
.article-grid { display:grid; gap:24px; }
.article-card { border:1px solid var(--border); border-radius:8px; padding:20px; transition:box-shadow .2s; }
.article-card:hover { box-shadow:0 2px 12px rgba(0,0,0,.08); }
.article-card h3 { font-size:1.1rem; margin-bottom:6px; line-height:1.4; }
.article-card h3 a { color:var(--link); text-decoration:none; }
.article-card h3 a:hover { text-decoration:underline; color:#c45500; }
.article-card .meta { font-size:.8rem; color:var(--muted); margin-top:8px; }
.article-card .tag { display:inline-block; background:#f0f7ff; color:#0066c0; padding:2px 8px; border-radius:4px; font-size:.75rem; margin-right:6px; }
.disclosure { background:#fff8f0; border:1px solid #ffe0b2; border-radius:6px; padding:12px 16px; margin:20px 0; font-size:.8rem; color:#b26500; }
.article-content h1 { font-size:1.8rem; margin:0 0 16px 0; line-height:1.3; }
.article-content h2 { font-size:1.4rem; margin:32px 0 12px 0; padding-bottom:6px; border-bottom:1px solid var(--border); }
.article-content h3 { font-size:1.1rem; margin:20px 0 8px 0; }
.article-content p { margin:0 0 16px 0; }
.article-content ul, .article-content ol { margin:0 0 16px 24px; }
.article-content li { margin-bottom:6px; }
.article-content a { color:var(--link); }
.article-content table { width:100%; border-collapse:collapse; margin:16px 0; }
.article-content th, .article-content td { border:1px solid var(--border); padding:10px 12px; text-align:left; font-size:.9rem; }
.article-content th { background:#f8f9fa; font-weight:600; }
.article-content strong { color:#333; }
.btn-amazon { display:inline-block; background:linear-gradient(to bottom,#f7dfa5,#f0c14b); border:1px solid #a88734; border-radius:3px; padding:8px 16px; color:#111; font-weight:600; text-decoration:none; font-size:.9rem; margin:4px 4px 4px 0; }
.btn-amazon:hover { background:linear-gradient(to bottom,#f5d78e,#eeb933); }
footer { border-top:1px solid var(--border); margin-top:60px; padding:24px 0; text-align:center; color:var(--muted); font-size:.8rem; }
.breadcrumb { font-size:.8rem; color:var(--muted); margin-bottom:20px; }
.breadcrumb a { color:var(--link); text-decoration:none; }
@media(max-width:600px) { .container { padding:0 16px; } .article-content h1 { font-size:1.4rem; } .article-content h2 { font-size:1.2rem; } }
"""

def markdown_to_html(text):
    """Simple Markdown to HTML converter for article content"""
    import re
    lines = text.split('\n')
    html = []
    in_list = False
    list_type = None
    in_table = False

    for line in lines:
        line = line.rstrip()
        if in_table:
            if line.startswith('|'):
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if all(c.startswith('---') for c in cells):
                    continue
                tag = 'th' if not in_table else 'td'
                html.append('<tr>')
                for c in cells:
                    html.append('<{}>{}</{}>'.format(tag, c, tag))
                html.append('</tr>')
                in_table = True
                continue
            else:
                html.append('</tbody></table>')
                in_table = False

        if not line:
            if in_list:
                html.append('</{}>'.format(list_type))
                in_list = False
                list_type = None
            continue

        if line.startswith('# '):
            if in_list:
                html.append('</{}>'.format(list_type)); in_list = False; list_type = None
            html.append('<h1>{}</h1>'.format(line[2:]))
        elif line.startswith('## '):
            if in_list:
                html.append('</{}>'.format(list_type)); in_list = False; list_type = None
            html.append('<h2>{}</h2>'.format(line[3:]))
        elif line.startswith('### '):
            if in_list:
                html.append('</{}>'.format(list_type)); in_list = False; list_type = None
            html.append('<h3>{}</h3>'.format(line[4:]))
        elif line.startswith('|'):
            if in_list:
                html.append('</{}>'.format(list_type)); in_list = False; list_type = None
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if all(c.startswith('---') for c in cells):
                continue
            html.append('<table><thead><tr>')
            for c in cells:
                html.append('<th>{}</th>'.format(c))
            html.append('</tr></thead><tbody>')
            in_table = True
        elif re.match(r'^\d+\.', line):
            if not in_list or list_type != 'ol':
                if in_list:
                    html.append('</{}>'.format(list_type))
                html.append('<ol>')
                in_list = True
                list_type = 'ol'
            content = re.sub(r'^\d+\.\s*', '', line)
            html.append('<li>{}</li>'.format(content))
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list or list_type != 'ul':
                if in_list:
                    html.append('</{}>'.format(list_type))
                html.append('<ul>')
                in_list = True
                list_type = 'ul'
            content = re.sub(r'^[-*]\s+', '', line)
            html.append('<li>{}</li>'.format(content))
        else:
            if in_list:
                html.append('</{}>'.format(list_type))
                in_list = False
                list_type = None
            line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" rel="nofollow sponsored">\1</a>', line)
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            html.append('<p>{}</p>'.format(line))

    if in_list:
        html.append('</{}>'.format(list_type))
    if in_table:
        html.append('</tbody></table>')

    return '\n'.join(html)

def build_page(title, body, meta_desc="", is_home=False):
    """Build complete HTML page"""
    nav_html = '<nav><a href="/">Home</a> <a href="/about.html">About</a> <a href="/disclosure.html">Disclosure</a></nav>'
    breadcrumb = '' if is_home else '<div class="breadcrumb"><a href="/">Home</a> &raquo; {}</div>'.format(title)
    desc_meta = '<meta name="description" content="{}">'.format(meta_desc or title)
    body_cls = 'class="article-content"' if not is_home else ''
    disclosure = '' if is_home else '<div class="disclosure">{}</div>'.format(AMAZON_DISCLOSURE)

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{} — {}</title>
{}
<style>{}</style>
</head>
<body>
<div class="container">
<header>
  <h1><a href="/">{}</a></h1>
  <p>{}</p>
  {}
</header>
{}
{}
<div {}>
{}
</div>
<footer><p>{} &copy; 2026 — {}</p></footer>
</div>
</body>
</html>""".format(title, SITE_NAME, desc_meta, CSS, SITE_NAME, SITE_TAGLINE, nav_html, breadcrumb, disclosure, body_cls, body, SITE_NAME, AMAZON_DISCLOSURE)


# Load articles
articles = []
for f in sorted(ARTICLES_DIR.glob("best-*.json")):
    with open(f, "r", encoding="utf-8") as fp:
        a = json.load(fp)
        if a.get("status") == "ai_generated" and a.get("content"):
            articles.append(a)

print("Found {} articles".format(len(articles)))

# Build article pages
article_pages = []
for a in articles:
    slug = a.get("slug", "article")
    html_content = markdown_to_html(a["content"])
    page = build_page(a["title"], html_content, a.get("meta_description", ""))
    out_path = OUTPUT_DIR / "{}.html".format(slug)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    article_pages.append({"title": a["title"], "slug": slug, "word_count": a.get("word_count_actual", 0)})
    print("  Built: {}.html".format(slug))

# Build homepage
cards = []
for ap in article_pages:
    cards.append("""<div class="article-card">
  <h3><a href="{}.html">{}</a></h3>
  <div class="meta"><span class="tag">Review</span> {} words &middot; Expert guide with real product comparisons</div>
</div>""".format(ap["slug"], ap["title"], ap["word_count"]))

home_body = """<div class="hero">
<h2>Expert Tech Reviews & Buying Guides</h2>
<p>Honest, in-depth reviews of the best tech gear. We test products, compare features, and help you make smarter buying decisions. Updated for 2026.</p>
</div>
<div class="article-grid">
{}
</div>""".format('\n'.join(cards))

home_page = build_page("Best Tech Reviews 2026", home_body, "Expert reviews and buying guides for mechanical keyboards, wireless mice, webcams, USB hubs, monitor stands, bluetooth earbuds, and more.", is_home=True)
with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write(home_page)

# Build disclosure page
disc_body = """<div class="article-content">
<h1>Affiliate Disclosure</h1>
<p>TechGear Picks is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com.</p>
<p>When you click on links to Amazon.com on this site and make a purchase, we may earn a small commission at no additional cost to you. This helps support our work in testing and reviewing products.</p>
<h2>Our Promise</h2>
<p>We only recommend products we believe offer genuine value. Our reviews are based on research, testing, and real user feedback. Affiliate commissions do not influence our recommendations.</p>
</div>"""
disc_page = build_page("Affiliate Disclosure", disc_body, "Affiliate disclosure for TechGear Picks")
with open(OUTPUT_DIR / "disclosure.html", "w", encoding="utf-8") as f:
    f.write(disc_page)

print("\nBlog built: {} pages in {}".format(len(article_pages) + 2, OUTPUT_DIR))
print("Open: file:///{}/index.html".format(OUTPUT_DIR.as_posix()))
