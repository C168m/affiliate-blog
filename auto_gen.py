"""Auto-generate one article from product catalog - imported by launch.py"""
import json, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from launch import ContentEngine, cfg, save_cfg, log, ARTICLE_CSS, ARTICLE_HTML

CATALOG_PATH = ROOT / 'product_catalog.json'
TOPICS_PATH = ROOT / 'topics_queue.json'

def load_catalog():
    return json.loads(CATALOG_PATH.read_text(encoding='utf-8'))

def load_topics():
    if TOPICS_PATH.exists():
        return json.loads(TOPICS_PATH.read_text(encoding='utf-8'))
    return {'done': [], 'queue': []}

def save_topics(topics):
    TOPICS_PATH.write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding='utf-8')

def build_queue():
    catalog = load_catalog()
    topics = load_topics()
    existing = set(topics['done'])
    for category, items in catalog.items():
        for item in items:
            slug = 'best-' + item['keyword'].replace(' ', '-') + '-2026'
            if slug not in existing and slug not in [t[0] for t in topics['queue']]:
                topics['queue'].append([slug, item['keyword'], category])
    save_topics(topics)
    return topics

def run():
    c = cfg()
    log('Auto-generate: building topic queue...')
    topics = build_queue()
    if not topics['queue']:
        log('No topics left in queue! Add more to product_catalog.json')
        return None
    slug, keyword, category = topics['queue'].pop(0)
    log('Generating article: ' + slug)
    catalog = load_catalog()
    products = None
    for cat_items in catalog.values():
        for item in cat_items:
            if item['keyword'] == keyword:
                products = item['products']
                break
        if products:
            break
    if not products:
        log('No products for: ' + keyword)
        topics['done'].append(slug)
        save_topics(topics)
        return None
    tid = c.get('amazon_tracking_id', '')
    ga_id = c.get('google_analytics_id', '')
    blog_name = c.get('blog_name', 'TechGear Picks')
    blog_tagline = c.get('blog_tagline', 'Expert Reviews & Buying Guides')
    rows = []
    for i, p in enumerate(products, 1):
        asin = p.get('asin', 'B0XXXXXXX')
        amz = 'https://www.amazon.com/dp/' + asin + '/?tag=' + tid if tid else '#'
        rows.append('<tr><td>#' + str(i) + '</td><td><a href="' + amz + '" rel="nofollow sponsored">' + p['name'] + '</a></td><td>' + p.get('price','N/A') + '</td><td>' + p.get('rating','N/A') + '</td><td><a href="' + amz + '" class="btn-amazon" rel="nofollow sponsored">Check Price</a></td></tr>')
    reviews = []
    for p in products:
        asin = p.get('asin', 'B0XXXXXXX')
        amz = 'https://www.amazon.com/dp/' + asin + '/?tag=' + tid if tid else '#'
        pros_html = ''.join('<li>' + x + '</li>' for x in p.get('pros', []))
        cons_html = ''.join('<li>' + x + '</li>' for x in p.get('cons', []))
        reviews.append('<h2>' + p['name'] + '</h2><p>' + p.get('desc','') + '</p><div class="pros-cons"><div class="pros"><strong>Pros:</strong><ul>' + pros_html + '</ul></div><div class="cons"><strong>Cons:</strong><ul>' + cons_html + '</ul></div></div><a href="' + amz + '" class="btn-amazon" rel="nofollow sponsored">Check Price on Amazon</a>')
    title_word = keyword.replace('-', ' ').title()
    title = 'Best ' + title_word + ' 2026 - Top Picks & Buying Guide'
    meta = 'Best ' + keyword + ' 2026 buying guide. Compare top picks, read reviews, and find the right ' + keyword + ' for your needs.'
    body = '<h1>Best ' + title_word + ' 2026 - Complete Buying Guide</h1>\n<p>Looking for the best ' + keyword + '? We tested and compared the top options available right now to help you make the right choice.</p>\n<h2>Our Top Picks at a Glance</h2>\n<table class="product-table"><thead><tr><th>Rank</th><th>Product</th><th>Price</th><th>Rating</th><th></th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>\n<h2>Detailed Reviews</h2>\n' + ''.join(reviews) + '\n<h2>How to Choose the Best ' + title_word + '</h2>\n<ul><li><strong>Quality:</strong> Look for durable materials, solid build, and reliable performance over flashy features.</li><li><strong>Value:</strong> Compare features against price - the most expensive is not always the best fit.</li><li><strong>Reviews:</strong> Check what real users say about long-term reliability before buying.</li></ul>'
    ga_snippet = ''
    if ga_id and ga_id != 'G-YOUR-GA-ID':
        ga_snippet = '<script async src="https://www.googletagmanager.com/gtag/js?id=' + ga_id + '"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag("js",new Date());gtag("config","' + ga_id + '")</script>'
   html = ARTICLE_HTML.format(title=title, blog_name=blog_name, blog_tagline=blog_tagline, meta_desc=meta, category=category, body=body, css=ARTICLE_CSS, ga_snippet=ga_snippet)
   filename = slug + '.html'
    filepath = ROOT / 'blog' / filename
    filepath.write_text(html, encoding='utf-8')
    link_count = html.count('amazon.com/dp/')
    log('Generated: ' + filename + ' (' + str(link_count) + ' Amazon links, ' + '{:,}'.format(len(html)) + ' bytes)')
    engine = ContentEngine(c)
    n_idx = engine.rebuild_index()
    n_sm = engine.update_sitemap()
    log('Index rebuilt: ' + str(n_idx) + ' articles, sitemap: ' + str(n_sm) + ' URLs')
    topics['done'].append(slug)
    c['articles_count'] = n_idx
    save_cfg(c)
    save_topics(topics)
    return filename

if __name__ == '__main__':
    result = run()
    if result:
        print('[OK] ' + result)
    else:
        print('[DONE] No new articles generated')
