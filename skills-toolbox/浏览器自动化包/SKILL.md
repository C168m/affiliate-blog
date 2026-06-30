---
name: 浏览器自动化包
description: Playwright浏览器自动化。用于国际平台(Gumroad/Payhip/YouTube/Reddit/Twitter)的自动操作，无需实名。
platforms: ["Gumroad", "Payhip", "YouTube", "Reddit", "Twitter/X", "Pinterest"]
---

# 🌐 浏览器自动化包

## 核心能力
- 国际平台自动注册/登录 (Gmail + 密码管理器)
- Gumroad/Payhip产品自动上架
- YouTube视频上传 (通过YouTube Studio)
- Reddit/Twitter/Pinterest自动发帖
- Cookie持久化 + 代理IP轮换

## 安装
```bash
pip install playwright
playwright install chromium
```

## 关键反检测配置
```python
# 隐藏自动化特征
browser = await pw.chromium.launch(
    headless=False,  # 不用headless
    args=['--disable-blink-features=AutomationControlled']
)
context = await browser.new_context(
    user_agent='随机真实UA',
    viewport={'width': 1920, 'height': 1080},
    locale='en-US'
)
```
