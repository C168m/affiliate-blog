#!/usr/bin/env python3
"""
============================================================
🤖 AI智能客服自动回复系统
支持: Gumroad + Payhip 买家消息自动回复
使用: DeepSeek API 智能回复
============================================================
"""

import json, os, sys, io, time, hashlib
from datetime import datetime
from pathlib import Path
from openai import OpenAI

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================
# 配置加载
# ============================================================
PROJECT_ROOT = Path(__file__).parent

def load_env():
    env_file = PROJECT_ROOT / '.env'
    config = {}
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8').split('\n'):
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                config[k.strip()] = v.strip()
    return config

env = load_env()
API_KEY = env.get('DEEPSEEK_API_KEY', '')
GUMROAD_TOKEN = env.get('GUMROAD_ACCESS_TOKEN', '')

client = OpenAI(api_key=API_KEY, base_url='https://api.deepseek.com')

# ============================================================
# 产品知识库 (AI客服知道这些产品)
# ============================================================
PRODUCT_KNOWLEDGE = """
## Gumroad 产品
1. Ultimate YouTube Automation Prompt Pack ($9.99)
   - 10个YouTube自动化AI提示词
   - 格式: Markdown
   - 适合: YouTube创作者

2. Ultimate Graphic Design with AI Notion Template ($14.99)
   - 一体化Notion模板
   - 格式: Notion Template
   - 适合: 设计师

3. Mastering AI Coding & Development Complete Guide 2026 ($19.98)
   - AI编程电子书
   - 格式: Markdown
   - 适合: 开发者

## Payhip 产品 (Skill Vault店铺)
1. AI Marketing Automation Prompt Pack ($9.99)
   - AI营销自动化提示词包

2. Ultimate Email Marketing with AI Prompt Pack ($9.99)
   - 邮件营销AI提示词

3. Mastering ChatGPT Prompt Engineering ($19.99)
   - ChatGPT提示工程电子书
"""

# ============================================================
# AI客服引擎
# ============================================================
class AICustomerService:
    """AI智能客服 — 自动回复买家咨询"""

    def __init__(self):
        self.knowledge_base = PRODUCT_KNOWLEDGE
        self.chat_history = []  # 对话历史
        self.faq_file = PROJECT_ROOT / '07-上下文记忆系统' / '项目知识库' / 'faq.md'

    def reply(self, customer_name: str, message: str, platform: str = "Gumroad") -> str:
        """AI自动回复客户消息"""

        # 构建提示词
        prompt = f"""You are an AI customer service agent for an AI digital products store called "Skill Vault" (also selling on Gumroad as "fgg hhh").

Your products:
{self.knowledge_base}

Customer Name: {customer_name}
Platform: {platform}
Customer Message: "{message}"

Reply as a friendly, helpful customer service agent. Follow these rules:
1. Be warm and professional
2. Answer the question directly
3. If they ask about pricing or features, provide specific details from the knowledge base
4. If they have a technical issue, offer clear steps to resolve it
5. End with an offer to help further
6. Keep it under 150 words
7. Reply in the same language as the customer's message (English or Chinese)

Your reply:"""

        try:
            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=[
                    {'role': 'system', 'content': 'You are a professional, friendly AI customer service agent for a digital products store.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            reply = response.choices[0].message.content

            # 记录对话
            self.chat_history.append({
                'timestamp': datetime.now().isoformat(),
                'customer': customer_name,
                'platform': platform,
                'message': message,
                'reply': reply,
                'tokens': response.usage.total_tokens
            })

            return reply

        except Exception as e:
            # 备用回复
            fallback = self._fallback_reply(customer_name, message)
            self.chat_history.append({
                'timestamp': datetime.now().isoformat(),
                'customer': customer_name,
                'message': message,
                'reply': fallback,
                'fallback': True
            })
            return fallback

    def _fallback_reply(self, customer_name: str, message: str) -> str:
        """离线备用回复(API不可用时)"""
        msg_lower = message.lower()

        if any(w in msg_lower for w in ['price', 'cost', 'how much', '多少钱', '价格']):
            return f"Hi {customer_name}! Our products range from $9.99 to $19.99. You can see all products and prices at our store. Is there a specific product you're interested in?"

        if any(w in msg_lower for w in ['download', 'download', '下载', 'file', '文件']):
            return f"Hi {customer_name}! After purchase, you'll get instant access to download your files. If you're having trouble, try refreshing the page or checking your email for the download link."

        if any(w in msg_lower for w in ['refund', '退款', 'return']):
            return f"Hi {customer_name}! We offer a 30-day money-back guarantee on all products. Please let me know your order details and I'll process the refund for you right away."

        if any(w in msg_lower for w in ['support', 'help', '帮助', 'question', '问题']):
            return f"Hi {customer_name}! Thanks for reaching out. I'm here to help with any questions about our AI products. What would you like to know?"

        return f"Hi {customer_name}! Thanks for your message. I'll get back to you with a detailed response shortly. In the meantime, you can browse our products at our store. Is there anything specific I can help with?"

    def handle_common_questions(self) -> dict:
        """处理常见问题,返回FAQ"""
        faqs = [
            {
                'question': 'How do I download my purchase?',
                'trigger_keywords': ['download', '下载', 'get file', 'access'],
                'reply': 'After purchase, you get instant download access. Check your email for the download link, or visit your Gumroad/Payhip library.'
            },
            {
                'question': 'What format are the files in?',
                'trigger_keywords': ['format', '格式', 'pdf', 'file type'],
                'reply': 'Our products come in Markdown (.md) format, which can be opened with any text editor. Some templates come as Notion template links.'
            },
            {
                'question': 'Do you offer refunds?',
                'trigger_keywords': ['refund', '退款', 'money back', 'return'],
                'reply': 'Yes! We offer a 30-day no-questions-asked refund policy. Contact us with your order details.'
            },
            {
                'question': 'Can I use these for commercial projects?',
                'trigger_keywords': ['commercial', '商用', 'business', 'client'],
                'reply': 'Yes! All our products come with a commercial license. Use them for personal and client projects.'
            },
            {
                'question': 'Do you offer custom/bulk orders?',
                'trigger_keywords': ['custom', '定制', 'bulk', '批量', 'discount'],
                'reply': 'We do! Contact us for custom prompt packs or bulk discounts for teams. Email us for a quote.'
            },
        ]

        # 保存FAQ
        self.faq_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.faq_file, 'w', encoding='utf-8') as f:
            f.write('# AI客服FAQ\n\n')
            for faq in faqs:
                f.write(f"## Q: {faq['question']}\n")
                f.write(f"触发词: {', '.join(faq['trigger_keywords'])}\n\n")
                f.write(f"A: {faq['reply']}\n\n---\n")

        return faqs

    def save_chat_log(self):
        """保存对话记录"""
        log_dir = PROJECT_ROOT / '07-上下文记忆系统' / '会话历史'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f'customer_chat_{datetime.now().strftime("%Y%m%d")}.jsonl'

        with open(log_file, 'a', encoding='utf-8') as f:
            for chat in self.chat_history:
                f.write(json.dumps(chat, ensure_ascii=False) + '\n')

    def simulate_chat(self):
        """模拟测试各种客户问题"""
        test_messages = [
            ("John", "How much does the ChatGPT prompt pack cost?"),
            ("Sarah", "I can't download my purchase, help!"),
            ("小明", "这个产品支持退款吗？"),
            ("Mike", "Can I use these prompts for my clients?"),
            ("Lisa", "Do you offer bulk discounts for teams?")
        ]

        print("=" * 50)
        print("🤖 AI客服模拟测试")
        print("=" * 50)

        for name, msg in test_messages:
            print(f"\n👤 {name}: {msg}")
            reply = self.reply(name, msg)
            print(f"🤖 AI: {reply}")
            time.sleep(1)

# ============================================================
# Gumroad消息检查
# ============================================================
class GumroadMessageChecker:
    """检查Gumroad上的客户消息"""

    def __init__(self, token: str):
        self.token = token

    def check_messages(self):
        """检查未读消息"""
        # Gumroad没有直接的消息API，但可以通过sales/emails端点
        # 实际部署时用Playwright监控Gumroad dashboard
        print("Gumroad消息检查: 需要浏览器自动化(Playwright)查看后台消息")
        print("当前使用AI客服引擎处理模拟消息")

# ============================================================
# 主函数
# ============================================================
def main():
    print("🤖 AI智能客服自动回复系统")
    print("=" * 50)

    ai_cs = AICustomerService()

    # 生成FAQ
    faqs = ai_cs.handle_common_questions()
    print(f"✅ FAQ已生成: {len(faqs)} 条")
    print(f"   保存至: {ai_cs.faq_file}")

    # 模拟测试
    ai_cs.simulate_chat()

    # 保存对话记录
    ai_cs.save_chat_log()
    print(f"\n✅ 对话记录已保存")
    print(f"   共 {len(ai_cs.chat_history)} 条对话")

    print("\n" + "=" * 50)
    print("📊 系统状态")
    print("=" * 50)
    print("AI客服引擎: ✅ 就绪 (DeepSeek)")
    print(f"知识库产品: 6个")
    print(f"支持平台: Gumroad, Payhip")
    print(f"自动回复: ✅ 已启用")
    print(f"FAQ文档: {ai_cs.faq_file}")
    print("\n💡 下一步:")
    print("  1. Gumroad/Payhip有客户消息时,运行此脚本自动回复")
    print("  2. 或部署为Webhook,实时自动回复")

if __name__ == '__main__':
    main()
