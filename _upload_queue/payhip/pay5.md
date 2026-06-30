# Ultimate AI Data Analysis Notion Template — All-in-One System

**Price:** $14.99

Here is a detailed Notion template design for **AI Data Analysis**, optimized for practical, daily use by data analysts, product managers, and researchers.

### 1. Template Name & Purpose
**Name:** AI Data Analysis Hub  
**Purpose:** A central workspace to log, track, and execute AI-powered data queries (using tools like ChatGPT, Copilot, or custom APIs). It connects raw questions, AI outputs, validation steps, and actionable insights. The goal is to move from "I asked AI a question" to "I have a verified, reusable analysis."

---

### 2. Database Tables Needed

**A. `AI Queries` (Main Database)**

| Column Name | Type | Description |
| :--- | :--- | :--- |
| **Query Title** | Title | Concise summary (e.g., "Q3 Churn Drivers") |
| **Date** | Date | When the query was run |
| **Prompt** | Text (Long) | Exact input text given to AI |
| **AI Response** | Text (Long) | Full raw output (Pasted from AI tool) |
| **Data Source** | Select | Options: `SQL DB`, `CSV Upload`, `Google Sheets`, `API` |
| **Status** | Select | `Draft`, `Validating`, `Verified`, `Invalid`, `Archived` |
| **Confidence** | Select | `High`, `Medium`, `Low` (User-rated after validation) |
| **AI Tool Used** | Select | `ChatGPT-4`, `Claude`, `Copilot`, `Custom Model` |
| **Tags** | Multi-select | e.g., `Regression`, `Trending`, `Forecasting`, `Anomaly` |
| **Owner** | Person | Person responsible for validation |
| **Validation Notes** | Text | Steps taken to verify (SQL checks, manual calc, etc.) |
| **Actionable Insight** | Text | Final takeaway (1-2 sentences) |

**B. `Data Sources` (Linked Database)**

| Column Name | Type | Description |
| :--- | :--- | :--- |
| **Source Name** | Title | e.g., "Sales 2024" |
| **File/Connection** | URL/Text | Link to CSV, or DB connection string |
| **Last Updated** | Date | When data was refreshed |
| **Data Rows** | Number | Approximate row count |
| **Related Queries** | Relation | Links back to `AI Queries` |

**C. `Validation Checklist` (Wiki/Database)**

| Column Name | Type | Description |
| :--- | :--- | :--- |
| **Check Item** | Title | e.g., "Re-run same prompt with 3% random sample" |
| **Category** | Select | `Logic`, `Numbers`, `Assumptions`, `Privacy` |
| **Severity** | Select | `Critical`, `Minor`, `Suggestion` |

---

### 3. Views

**- Table View (Default):** Full list of all queries. Sort by `Date` descending. Use filters (e.g., `Status != Invalid`) to keep it clean.  
**- Kanban View:** Group by `Status`. Move cards from `Draft` → `Validating` → `Verified`. Visual workflow for pipeline management.  
**- Calendar View:** Group by `Date`. Useful for seeing analysis activity by week.  
**- Gallery View:** Show `Query Title` + a custom card preview (use `Status` as a colored badge + `Confidence` emoji). Great for weekly review meetings.

---

### 4. Automations & Formulas

**Formula: `Validation Score` (Rollup)**
- *Logic:* If `Validation Notes` has text AND `Confidence` is not empty, then "Complete" else "Needs Review".
- *Intended use:* Flags queries that haven't been properly verified.

**Automation 1: “New Query Alert”**
- *Trigger:* When a new item is added to `AI Queries`.
- *Action:* Send a notification to the `Owner` person with a link to the new query.

**Automation 2: “Expired Validation”**
- *Trigger:* When `Status` is `Validating` AND `Date` is older than 3 days.
- *Action:* Change `Confidence` to `Low` and notify the `Owner`.

**Automation 3: “Move to Archive”**
- *Trigger:* When `Status` is changed to `Verified` AND `Date` is older than 60 days.
- *Action:* Move the item to an `Archive` database (or change status to `Archived`).

**Button (In-Database): “Run Validation”**  
- *Action:* Opens a Notion page pre-populated with the `Validation Checklist` items. User ticks off checks.

---

### 5. How Users Benefit

**For an Analyst:**
- **Eliminates "AI Brain Dump":** Every output is logged. No more losing a great insight in a chat window.
- **Forces Validation:** The workflow (`Draft` → `Validating` → `Verified`) creates a culture of facts, not assumptions.
- **Reusable Prompts:** You can sort by `Tags` or `Data Source` to find a prompt that worked before (e.g., "SQL query for monthly retention"). Saves hours of re-prompting.

**For a Manager:**
- **Audit Trail:** See exactly what the AI was asked, what it returned, and if it was checked. Builds trust in AI outputs over time.
- **Confidence Heatmap:** Filter by `Confidence = Low` to find risky analyses that need a human second look.
- **Resource Planning:** The Calendar view shows when analysis was done—helpful for capacity planning.

**For the Team:**
- **Shared Context:** A new hire can look at the `AI Queries` table for the last 3 months and understand *how* the team uses AI, not just *what* the answers were.
- **Validation as a Service:** The linked `Validation Checklist` provides a standard operating procedure for AI oversight.

**Bottom line:** This template transforms AI from a black box to a transparent, auditable, and reusable analytical tool. It’s ready to use.