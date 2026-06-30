# AI Money Machine — 研究发现

## 平台可行性 (已验证)

### Gumroad ✅ 主力
- 支持中国卖家, 邮箱+PayPal即可
- 手续费: 10% (免费方案) / 0% ($10/月)
- API可用但文件上传不可靠 → 浏览器编辑页面有效
- 需VPN访问
- Store: https://howler06371.gumroad.com

### Payhip ✅ 第二渠道
- 支持中国卖家, 5%手续费(更低)
- PayPal已连接
- Cloudflare验证 + React表单导致Playwright无法完成最后一步
- **关键发现**: Payhip产品页使用React受控组件, setInputFiles不被React state识别

### LemonSqueezy ❌ 永久放弃
- 明确不支持中国商户

## Playwright自动化限制 (关键发现)
1. React受控组件: setInputFiles不触发React onChange → 解决方案: JS直接提交form (Payhip可行)
2. Payhip产品页表单id="addproduct", action="https://payhip.com/product/addit"
3. 多modal叠加 → Escape逐层关闭即可

## 反自动化检测 (2026-06-12 新发现)
1. **Gumroad React空列表**: Playwright浏览器中/products页面显示空白引导页, 产品表格不渲染。API正常但GUI被反自动化检测阻止。
2. **Gumroad API文件上传**: PUT multipart返回200但file_info始终为空。文件上传必须通过浏览器Content tab。
3. **Google登录reCAPTCHA**: Playwright浏览器被标记为不寻常设备, 触发额外人机验证。
4. **Payhip Cloudflare**: 持续reCAPTCHA拦截。

## 根本结论
这些平台都有成熟的反自动化机制。自动化能做到90%(API创建产品+内容生产), 但最后10%(浏览器上传+发布)必须真人操作。这是所有这类项目的边界。

## 2026年最佳数字产品赛道
1. AI提示词包 — 月搜索量50K+, $5-15
2. AI教程电子书 — 月搜索量20K+, $10-30
3. Notion模板 — 月搜索量30K+, $10-20

## 成本分析
- DeepSeek: 15个产品 ≈ $0.03 (极高ROI)
- 平台费: Gumroad 10% / Payhip 5%
- 总投入: <$10 (含API+平台费)
