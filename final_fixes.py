import re, os, sys
PROJECT = r"D:\AI-Money-Machine"

# Fix 1: SEO factory - add content + status
fp = os.path.join(PROJECT, "05-SEO内容站群", "seo_content_factory.py")
with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

before = '"slug": keyword.replace(" ", "-").lower()[:60],\n            "meta_description"'
after = '"slug": keyword.replace(" ", "-").lower()[:60],\n            "content": ai_content if ai_content else "",\n            "meta_description"'
if before in content:
    content = content.replace(before, after)
    print("[OK] SEO: content field added")

before2 = '"word_count_target": 2000,\n            "status": "draft",'
after2 = '"word_count_target": 2000,\n            "status": "ai_generated" if ai_content else "draft",'
if before2 in content:
    content = content.replace(before2, after2)
    print("[OK] SEO: status conditional")

before3 = "def main():\n    import argparse"
after3 = "def main():\n    from dotenv import load_dotenv; load_dotenv()\n    import argparse"
if before3 in content:
    content = content.replace(before3, after3)
    print("[OK] SEO: .env loading added to main()")

with open(fp, "w", encoding="utf-8") as f:
    f.write(content)

# Fix 2: Scheduler .env
fp2 = os.path.join(PROJECT, "08-全自动调度", "scheduler.py")
with open(fp2, "r", encoding="utf-8") as f:
    c2 = f.read()
if "load_dotenv" not in c2:
    c2 = c2.replace(
        "import json, os, sys, time, subprocess",
        "import json, os, sys, time, subprocess\nfrom dotenv import load_dotenv; load_dotenv()"
    )
    with open(fp2, "w", encoding="utf-8") as f:
        f.write(c2)
    print("[OK] Scheduler: .env added")

# Fix 3: Sales automation .env
fp3 = os.path.join(PROJECT, "02-销售平台自动化", "sales_automation.py")
with open(fp3, "r", encoding="utf-8") as f:
    c3 = f.read()
if "load_dotenv" not in c3:
    c3 = c3.replace(
        "import json, os, sys",
        "import json, os, sys\nfrom dotenv import load_dotenv; load_dotenv()"
    )
    with open(fp3, "w", encoding="utf-8") as f:
        f.write(c3)
    print("[OK] Sales: .env added")

print("\nAll final fixes applied.")
