# 🚀 AI Money Machine v3.0 — 架构总览

## 7层架构

```
D:\AI-Money-Machine\
│
├── 🧠 engine/           引擎层 — AI生产核心
│   ├── product-engine/   产品生产(DeepSeek批量生成数字产品)
│   ├── content-engine/   内容工厂(脚本→图片→TTS→视频)
│   └── ai-copilot/       AI副驾驶(DeepSeek整合+客服)
│
├── 🔧 tools/            工具层 — 自动化操作
│   ├── browser-automation/  Playwright浏览器自动化
│   ├── api-connectors/      Gumroad/Payhip API
│   └── file-processor/      文件处理(格式转换/压缩)
│
├── 📣 marketing/        推广层 — 流量获取
│   ├── reddit-bot/         Reddit自动推广
│   ├── twitter-bot/        Twitter/X自动发帖
│   ├── seo-blogs/          Medium/Dev.to SEO博客
│   ├── pinterest-bot/      Pinterest自动Pin
│   └── youtube-channel/    YouTube无人频道
│
├── 💰 sales/            销售层 — 变现
│   ├── gumroad-store/      Gumroad店铺
│   ├── payhip-store/       Payhip店铺
│   └── affiliate-network/  联盟营销
│
├── 📊 analytics/        数据层 — 分析
│   ├── revenue-tracker/    收益追踪
│   ├── traffic-analytics/  流量分析
│   └── dashboard/          可视化看板
│
├── ⏰ scheduler/        调度层 — 自动化
│   ├── daily-pipeline/     每日流水线
│   ├── task-queue/         任务队列
│   └── monitor/            监控告警
│
├── 🧿 memory/           记忆层 — 上下文
│   ├── knowledge-base/     项目知识库
│   ├── session-logs/       会话日志
│   └── decision-records/   决策记录
│
└── ⚙️ config/           配置层
    ├── env-templates/      环境模板
    ├── prompt-library/     提示词库
    └── product-templates/  产品模板
```

## 数据流

```
config/prompt-library  →  engine/product-engine  →  tools/file-processor
                                    ↓
                              sales/gumroad-store  →  💰 收款
                              sales/payhip-store   →  💰 收款
                                    ↓
marketing/reddit-bot  ─┐
marketing/twitter-bot   ├→  traffic  →  sales  →  analytics
marketing/seo-blogs    ─┤
marketing/pinterest-bot ┘
```

## 每日自动化流水线

```
08:00  scheduler 触发
08:05  engine 生产3个新产品
08:15  tools 自动上架到 Gumroad + Payhip
09:00  marketing/reddit-bot 在相关Subreddit发价值帖
10:00  marketing/twitter-bot 发3条推广推文
11:00  marketing/seo-blogs 发布1篇Medium文章
12:00  marketing/pinterest-bot Pin产品图片
14:00  tools/browser-automation 检查所有店铺状态
18:00  marketing 第二轮社交媒体推广
23:00  analytics 采集全天数据 → 生成日报
```
