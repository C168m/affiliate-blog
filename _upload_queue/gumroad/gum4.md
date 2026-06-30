# Ultimate Personal Finance with AI Notion Template — All-in-One System

**Price:** $14.99

Here is a detailed, practical **Personal Finance with AI** Notion template designed for immediate use.

---

### 1. Template Name & Purpose

**Name:** The AI Finance OS

**Purpose:** To create a single source of truth for your financial life, leveraging AI (via Notion’s built-in AI or manual prompts) to categorize transactions, summarize spending trends, and generate actionable savings goals. It replaces spreadsheets with a visual, relational system.

---

### 2. Database Tables (with Columns/Fields)

You will create **three connected databases**.

#### A. `Transactions` (Main Ledger)
- **Name** (Text)
- **Amount** (Number, format: USD)
- **Date** (Date)
- **Type** (Select: Income / Expense / Transfer)
- **Category** (Select: Housing, Food, Transport, Utilities, Entertainment, Savings, Salary, Freelance, etc.)
- **Account** (Relation → `Accounts` table)
- **AI Summary** (Text – *AI Automation writes here*)
- **Recurring?** (Checkbox)
- **Notes** (Text)
- **Month** (Formula: `formatDate(prop("Date"), "MMM YYYY")`)

#### B. `Accounts` (Bank & Cash)
- **Name** (Text: e.g., "Checking", "Savings", "Credit Card A")
- **Type** (Select: Checking / Savings / Credit / Cash)
- **Current Balance** (Number)
- **Transactions** (Relation → `Transactions`)
- **Net Change** (Formula: `prop("Transactions").sum(prop("Amount"))`)

#### C. `Goals` (AI-Generated Target)
- **Name** (Text: e.g., "Emergency Fund", "Summer Trip")
- **Target Amount** (Number)
- **Current Amount** (Number)
- **Target Date** (Date)
- **Auto Suggestion** (Text – *AI writes a suggested monthly saving amount*)
- **Active?** (Checkbox)
- **Progress** (Formula: `round(prop("Current Amount") / prop("Target Amount") * 100) + "%"`)

---

### 3. Views (Tabbed Layout Inside the `Transactions` DB)

| **View** | **Configuration** | **Purpose** |
|---|---|---|
| **Table** (Main view) | Show all fields. Group by `Month`. Sort by `Date` descending. | Quick data entry and bulk editing. |
| **Calendar** | Filter: `Date` is within next 30 days. Show `Amount` and `Notes`. | Upcoming bills/subscriptions you marked as recurring. |
| **Kanban** | Group by `Category`. Cards show `Name`, `Amount`, `AI Summary`. | Spot which spending category (e.g., "Food") is dominating your budget. |
| **Gallery** | Filter: `Type` is Income. Group by `Account`. Show `AI Summary`. | A visual dashboard of your income streams per account. |

**Bonus Account View:** In the `Accounts` database, create a **Gallery** view showing a color-coded card for each account, displaying `Name`, `Balance`, and the `Net Change` formula.

---

### 4. Automations & Formulas (The "AI" Engine)

You will use **Notion Automations** and standard **Formulas**. *If you have Notion AI, use it for the text generation steps below; otherwise, manually copy/paste the prompt template.*

#### A. Automation: AI Transaction Categorization
- **Trigger:** When a new `Transaction` is added (or when "Category" is empty).
- **Action:** Use **Notion AI** to write in the `AI Summary` field.
- **AI Prompt used:**
  > "Based on the transaction name '[Name]' and amount $[Amount] on [Date], suggest a spending category and a one-sentence summary. Format: `Category: [Category] | Summary: [Sentence]`"
- **Result:** The `AI Summary` field auto-fills, and you can manually update the `Category` column accordingly.

#### B. Formula: Monthly Net Worth
Add this formula to the `Accounts` database (or a separate "Dashboard" database):
> `prop("Accounts").map(current.prop("Current Balance")).sum()`

#### C. Formula: Goal Auto-Progress (Already in `Goals` DB)
> `format(round(prop("Current Amount") / prop("Target Amount") * 100)) + "%"`

#### D. (Optional) Automation: Weekly Spending Alert
- **Trigger:** Weekly on Sunday.
- **Action:** Send an email to you (via Notion reminders) with a linked page to the `Transactions` database filtered by "This Week", showing the week's total spend.

---

### 5. How Users Benefit from It

1. **Zero Manual Tagging:** The AI automation removes the friction of categorizing every coffee or utility bill. You just enter the name and amount; the AI suggests the category.
2. **Proactive Goal Setting:** The `Goals` database’s `Auto Suggestion` field (fed by AI) translates your spending data into realistic saving targets (e.g., "Based on last month's spending, you can save $150 toward your Emergency Fund by reducing takeout").
3. **Visual Causal Links:** Relating `Transactions` to `Accounts` and `Goals` lets you see, in one click, how buying a new laptop affected your Savings account balance and delayed a vacation goal.
4. **Bill Forecasting:** The Calendar view of recurring transactions (rent, subscriptions) shows your next 30 days of expenses at a glance, preventing overdrafts.
5. **Actionable Insights from Kanban:** Grouping expenses by category in Kanban reveals which categories are chronically overspent, allowing you to set real-time budget caps.
6. **Privacy & Simplicity:** Unlike third-party budgeting apps that connect to your bank (posing security risks), this template is entirely manual but AI-assisted—you control the data entry and the AI suggestions stay inside Notion.

**To get started immediately:** Duplicate the three databases, add your accounts, then start logging one week of transactions. The AI will quickly "learn" your spending patterns.