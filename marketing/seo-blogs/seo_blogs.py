#!/usr/bin/env python3
"""
============================================================
📝 SEO博客推广引擎
平台: Medium + Dev.to + Hashnode
策略: 长文引流→CT→产品链接
============================================================
"""

import json, os, sys, io, time, re
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent.parent.parent  # Fix: go up to project root
DATA_DIR = PROJECT_ROOT / 'marketing' / 'seo-blogs' / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load .env from project root
env_file = PROJECT_ROOT / '.env'
env = {}
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8').split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

api_key = env.get('DEEPSEEK_API_KEY', '')
print(f'DEEPSEEK key: {api_key[:15]}...')
if not api_key:
    print('ERROR: No API key found in .env')
    sys.exit(1)

from openai import OpenAI
client = OpenAI(api_key=api_key, base_url='https://api.deepseek.com')

# ============================================================
# 高流量SEO关键词 (长尾低竞争)
# ============================================================
SEO_TOPICS = [
    {
        'keyword': 'best AI tools for content creation 2026',
        'volume': '2.5K/mo',
        'difficulty': 'easy',
        'article_type': 'listicle',
        'product_to_link': 'AI Marketing Automation Prompt Pack'
    },
    {
        'keyword': 'how to write better ChatGPT prompts',
        'volume': '8K/mo',
        'difficulty': 'medium',
        'article_type': 'tutorial',
        'product_to_link': 'ChatGPT Prompt Engineering Guide'
    },
    {
        'keyword': 'AI automation for small business owners',
        'volume': '3K/mo',
        'difficulty': 'easy',
        'article_type': 'guide',
        'product_to_link': 'Email Marketing AI Prompt Pack'
    },
    {
        'keyword': 'digital products that sell fast 2026',
        'volume': '4K/mo',
        'difficulty': 'easy',
        'article_type': 'listicle',
        'product_to_link': '(all products)'
    },
    {
        'keyword': 'make money with AI side hustle',
        'volume': '10K/mo',
        'difficulty': 'medium',
        'article_type': 'case_study',
        'product_to_link': '(all products)'
    },
]

# ============================================================
# 文章生成
# ============================================================
class SEOArticleGenerator:
    """SEO文章生成器"""

    def generate_medium_article(self, topic: dict) -> dict:
        """生成Medium文章(1500-2000字, SEO优化)"""
        prompt = f"""Write a high-quality Medium article.

Title: {topic['keyword'].replace('best ', 'Top 10 ').replace('how to ', 'How to ').title()} (2026 Guide)

Requirements:
- 1500-2000 words
- Engaging hook in first paragraph
- H2 subheadings for each major section
- 3-5 actionable tips with examples
- Natural mention of digital resources (our products fit here naturally)
- Friendly, conversational tone
- End with a soft CTA: "If you found this helpful, I've created [resources/tools] to help you get started faster"
- Include target keyword naturally (3-5 times)
- Meta description (under 160 chars)

Format as:
# [Title]

**Meta:** [meta description]

[Article content]
"""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=2500
            )
            content = resp.choices[0].message.content

            article = {
                'id': f"SEO_{datetime.now().strftime('%Y%m%d%H%M')}",
                'keyword': topic['keyword'],
                'difficulty': topic['difficulty'],
                'platform': 'Medium',
                'content': content,
                'word_count': len(content.split()),
                'generated_at': datetime.now().isoformat()
            }

            # 保存
            article_file = DATA_DIR / f"article_{article['id']}.md"
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return article
        except Exception as e:
            return {'error': str(e)}

    def generate_devto_article(self, topic: dict) -> dict:
        """生成Dev.to文章(技术向, 开发者受众)"""
        prompt = f"""Write a Dev.to article for developers.

Topic: {topic['keyword']}

Requirements:
- Technical, developer-focused tone
- Include code examples or practical workflows
- 1000-1500 words
- Use proper markdown (code blocks, headers)
- Title with numbers (e.g. "5 Ways to...")
- Add tags: ai, productivity, tutorial, automation
- End with links to resources

The article should teach something practical that developers can use immediately."""

        try:
            resp = client.chat.completions.create(
                model='deepseek-chat',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=2000
            )
            content = resp.choices[0].message.content

            article = {
                'id': f"DEV_{datetime.now().strftime('%Y%m%d%H%M')}",
                'keyword': topic['keyword'],
                'platform': 'Dev.to',
                'content': content,
                'generated_at': datetime.now().isoformat()
            }

            article_file = DATA_DIR / f"devto_{article['id']}.md"
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return article
        except Exception as e:
            return {'error': str(e)}


# ============================================================
# 发布策略
# ============================================================
class SEOPublisher:
    """SEO文章发布策略"""

    PUBLISHING_SCHEDULE = {
        'Medium': {
            'frequency': '3 articles/week',
            'best_time': 'Tuesday & Thursday 9am EST',
            'note': 'Use tags: AI, Technology, Entrepreneurship, Side Hustle'
        },
        'Dev.to': {
            'frequency': '2 articles/week',
            'best_time': 'Monday & Wednesday',
            'note': 'Tags: ai, productivity, tutorial, webdev'
        },
        'Hashnode': {
            'frequency': '1 article/week (republish Medium content)',
            'note': 'Auto-cross-post from Medium'
        }
    }

    CTA_TEMPLATES = [
        "\n\n---\n*If you found this helpful, I've put together a [resource pack](https://payhip.com/b/cxgM9) with ready-to-use AI prompts for marketing automation.*",
        "\n\n---\n*Want to dive deeper? Check out my [ChatGPT Prompt Engineering Guide](https://howler06371.gumroad.com/l/fuowsw) — packed with advanced techniques.*",
        "\n\n---\n*I created a [productivity toolkit](https://howler06371.gumroad.com/l/zmyrkl) that includes all the templates I use daily.*",
    ]


# ============================================================
# 主程序
# ============================================================
def main():
    print("=" * 60)
    print("📝 SEO博客推广引擎")
    print("=" * 60)

    generator = SEOArticleGenerator()

    # 生成2篇文章
    print(f"\n📝 生成SEO文章...")

    # Medium篇
    topic1 = SEO_TOPICS[0]
    print(f"\n📄 Medium文章: {topic1['keyword']}")
    article = generator.generate_medium_article(topic1)
    if 'content' in article:
        print(f"  ✅ {article['word_count']} words")
        print(f"  📁 {DATA_DIR}/article_{article['id']}.md")
        print(f"  CTA: {random.choice(SEOPublisher.CTA_TEMPLATES)[:80]}...")

    # Dev.to篇
    topic2 = SEO_TOPICS[2]
    print(f"\n📄 Dev.to文章: {topic2['keyword']}")
    article2 = generator.generate_devto_article(topic2)
    if 'content' in article2:
        print(f"  ✅ generated")

    print(f"\n" + "=" * 60)
    print("📊 SEO推广策略:")
    print("=" * 60)
    for platform, schedule in SEOPublisher.PUBLISHING_SCHEDULE.items():
        print(f"  📍 {platform}: {schedule['frequency']}")
        print(f"     时间: {schedule['best_time']}")
        print(f"     提示: {schedule['note']}")

    print(f"\n📊 SEO关键词库 ({len(SEO_TOPICS)} topics):")
    for t in SEO_TOPICS:
        print(f"  [{t['difficulty']}] {t['keyword']} ({t['volume']})")

    print(f"\n💡 下一步:")
    print("  1. 手动注册 Medium (medium.com) 和 Dev.to (dev.to)")
    print("  2. 复制生成的文章→手动发布到Medium/Dev.to")
    print("  3. 在文末添加CTA链接到Gumroad/Payhip")
    print("  4. 每周3篇 → 3个月后SEO流量开始涌入")


if __name__ == '__main__':
    import random
    main()
