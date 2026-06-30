import os, sys, json, re

PROJECT = r"D:\AI-Money-Machine"

# ===== Fix product_factory.py =====
fp = os.path.join(PROJECT, "01-数字产品工厂", "product_factory.py")
with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

# Fix indentation (lines shifted 2 spaces to left)
# Find and fix the _call_deepseek + create_product + batch_create methods
# The _call_deepseek has wrong indentation
content = re.sub(r"\n   def __init__", "\n    def __init__", content)
content = re.sub(r"\n       self\.api_key", "\n        self.api_key", content)
content = re.sub(r"\n    def _call_deepseek", "\n    def _call_deepseek", content)

# Add ai_content to dict
old_dict_line = '"description": self._gen_description(product_type, niche),\n            "tags":'
new_dict_line = '"description": self._gen_description(product_type, niche),\n            "ai_content": ai_content if ai_content else "",\n            "tags":'
if old_dict_line in content:
    content = content.replace(old_dict_line, new_dict_line)
    print("  [OK] ai_content field added to product dict")

# Fix status
content = content.replace('"status": "draft"', '"status": "ai_generated" if ai_content else "draft"')

with open(fp, "w", encoding="utf-8") as f:
    f.write(content)
print("  [OK] product_factory.py fixed")

# ===== Fix seo_content_factory.py =====
fp2 = os.path.join(PROJECT, "05-SEO内容站群", "seo_content_factory.py")
with open(fp2, "r", encoding="utf-8") as f:
    content2 = f.read()

if "_call_deepseek" not in content2:
    method = """    def _call_deepseek(self, system_prompt, user_prompt, max_tokens=2000):
        import requests
        if not self.api_key:
            return ""
        try:
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "max_tokens": max_tokens, "temperature": 0.7},
                timeout=60
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            print(f"  DeepSeek err ({resp.status_code}): {resp.text[:200]}")
            return ""
        except Exception as e:
            print(f"  DeepSeek fail: {e}")
            return ""
"""
    # Insert before generate_article
    marker = "    def generate_article(self, keyword"
    if marker in content2:
        content2 = content2.replace(marker, method + "\n" + marker)
        print("  [OK] _call_deepseek added to seo_content_factory.py")
else:
    print("  seo_content_factory already has _call_deepseek")

with open(fp2, "w", encoding="utf-8") as f:
    f.write(content2)

print("\nAll fixes applied.")
