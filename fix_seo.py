import os

fp = os.path.join(r"D:\AI-Money-Machine", "05-SEO内容站群", "seo_content_factory.py")
with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

# template is a string, not a dict. Fix the two .get() calls.
old1 = 'template_content = template.get("content", keyword)'
new1 = 'template_content = template  # template is a string prompt'
if old1 in content:
    content = content.replace(old1, new1)
    print("[OK] Fixed template.get(content)")

old2 = 'system_msg = f"You are a professional SEO content writer. Write a {article_type} article about: {keyword}. Include engaging intro, {template.get(\'word_count\', 2000)} words, affiliate link placeholders, and conclusion with CTA."'
new2 = 'system_msg = f"You are a professional SEO content writer. Write a {article_type} article about: {keyword}. Include engaging intro, 2000+ words, affiliate link placeholders, and conclusion with CTA."'
if old2 in content:
    content = content.replace(old2, new2)
    print("[OK] Fixed template.get(word_count)")
else:
    print("old2 not found, searching...")
    if 'template.get' in content:
        idx = content.index('template.get')
        print("Found at:", content[idx-30:idx+30])

with open(fp, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
