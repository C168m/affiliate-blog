# 05-SEO内容站群

## 🎯 职能
用AI批量生产高质量SEO文章，搭建WordPress站群，赚AdSense+联盟佣金。

---

## 🏗 内容站架构

```
主站 (AI工具评测)  ← 品牌站
├── 子站1 (AI写作工具对比)
├── 子站2 (AI绘图工具指南)
├── 子站3 (AI编程助手评测)
├── 子站4 (AI视频工具教程)
└── 子站5 (AI营销工具推荐)
```

---

## 📝 AI文章生产流水线

```
关键词研究(Ahrefs/Semrush) → DeepSeek生成大纲 → AI写正文
→ 人工策展检查 → WordPress自动发布 → 内链+外链
```

## 🔑 关键词策略

| 关键词类型 | 示例 | 难度 |
|-----------|------|------|
| 长尾信息词 | "best free AI writing tool for blog" | 低 |
| 产品对比词 | "ChatGPT vs Claude for coding" | 中 |
| 教程词 | "how to use AI to write emails" | 低 |
| 商业词 | "buy AI prompts for marketing" | 中高 |

---

## 💰 变现方式

| 方式 | 说明 | 收益 |
|------|------|------|
| Google AdSense | 自动广告展示 | $1-10 CPM |
| Amazon联盟 | 推荐AI书籍/工具 | 3-10%佣金 |
| SaaS联盟 | 推荐AI工具(Jasper等) | 20-30%佣金 |
| 自有产品 | 推荐自己的Gumroad产品 | 100% |

---

## 🚀 快速启动

```bash
# 搭建WordPress站
python wp_manager.py --action create --domain "aitoolreview.com"

# 生成文章
python seo_content.py --keyword "best ai writing tools 2026" --count 10

# 发布文章
python wp_manager.py --action publish --site "aitoolreview.com" --articles output/*.html
```
