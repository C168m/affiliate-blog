---
name: DeepSeek对接包
description: DeepSeek API对接。用于AI内容批量生产：数字产品、SEO文章、YouTube脚本、社交媒体文案。
cost: ¥0-50/月 (有大量免费额度)
---

# 🤖 DeepSeek对接包

## 安装
```bash
pip install openai
```

## 快速使用
```python
from openai import OpenAI
client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com"
)
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "写一篇AI工具评测文章"}]
)
```

## 成本: ¥1/百万tokens — 一条视频脚本≈¥0.005

## 本项目的核心提示词模板
详见各模块的prompt定义:
- 数字产品工厂 → PRODUCT_TEMPLATES
- YouTube脚本 → SHORT_TEMPLATES / LONG_TEMPLATES
- SEO文章 → ARTICLE_TEMPLATES
- 社交媒体 → ContentTemplates
