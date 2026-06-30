# 02-销售平台自动化

## 🎯 职能
将数字产品自动上架到Gumroad/Payhip/LemonSqueezy/闲鱼，多渠道覆盖全球市场。

---

## 🌐 四大销售平台

| 平台 | 受众 | 收款方式 | 手续费 | 实名？ |
|------|------|----------|--------|--------|
| **Gumroad** | 全球英语用户 | PayPal | 10%免费/0%付费版 | ❌ |
| **Payhip** | 全球用户 | PayPal/Stripe | 5% | ❌ |
| **LemonSqueezy** | 全球用户 | PayPal/Payoneer | 5%+$0.50 | ❌ |
| **闲鱼** | 中国用户 | 支付宝 | 0% | ⚠️选配 |

---

## 🤖 自动化上架流程

```python
# 一键上架到Gumroad
python gumroad_publisher.py --product "./output/prompt_pack_marketing.pdf" \
    --title "100 ChatGPT Marketing Prompts Bundle" \
    --price 9.99 \
    --tags "AI,ChatGPT,Marketing"

# 一键上架到Payhip
python payhip_publisher.py --product "./output/notion_template.zip" \
    --title "Ultimate Productivity Notion Template" \
    --price 14.99
```

## 🔑 平台注册指南

1. **Gumroad**: gumroad.com → Sign Up → PayPal绑定
2. **Payhip**: payhip.com → Create Account → Stripe/PayPal
3. **LemonSqueezy**: lemonsqueezy.com → 企业注册(填个人即可) → Payoneer
