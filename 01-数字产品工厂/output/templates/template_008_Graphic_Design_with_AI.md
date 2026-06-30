# Ultimate Graphic Design with AI Notion Template — All-in-One System

**Price:** $14.99

Here is a detailed Notion template for **Graphic Design with AI**.

---

### 1. Template Name & Purpose
**Name:** AI Design Studio Hub
**Purpose:** To manage the end-to-end workflow of creating visual assets using AI tools (Midjourney, DALL-E, Stable Diffusion, Photoshop Beta). It tracks prompts, asset versions, approval status, and final delivery, bridging the gap between concept generation and client handoff.

---

### 2. Database Tables (with Columns/Fields)

**Table A: Projects** (Main parent database)
- **Name** (Title)
- **Status** (Select: Brief Received / Ideation / Approved / Delivered / Archived)
- **Client** (Text)
- **Deadline** (Date)
- **Design Style** (Multi-Select: Minimalist, Cyberpunk, Vintage, Corporate, etc.)
- **Brief Notes** (Text block)
- **Deliverables** (Rollup of completed assets from Table B)
- **Total Assets** (Rollup Count of Table B)

**Table B: AI Assets** (Child database related to Projects)
- **Asset Name** (Title)
- **Project** (Relation to Table A)
- **AI Tool** (Select: Midjourney, DALL-E 3, Stable Diffusion, Photoshop AI, Leonardo)
- **Prompt Used** (Text – the exact prompt text)
- **Negative Prompt** (Text – optional)
- **Status** (Select: Draft / Revised / Final / Rejected)
- **Version #** (Number – auto-increment)
- **File Preview** (Files & Media – image upload)
- **Dimensions** (Select: 1:1, 16:9, 9:16, 4:3)
- **Style Reference** (URL – link to reference image or style code)
- **Generation Date** (Date/Time)
- **Notes** (Text – what was changed from previous version)

---

### 3. Views (Calendar, Kanban, Table, Gallery)

**Calendar View**
- **Filter:** Show only projects with a Deadline.
- **Use Case:** Visualize delivery dates for client work and schedule final handoffs. Undated generative experiments are hidden.

**Kanban View**  
- **Group by:** Asset Status (Draft → Revised → Final → Rejected).
- **Use Case:** Drag assets through the pipeline. A designer can see exactly which images need revision and which are ready to export.

**Table View** (Default)
- **Sort by:** Generation Date (newest first).
- **Use Case:** Bulk editing metadata (e.g., changing all “Draft” assets to “Revised” after a batch). Best for data entry and filtering by prompt keywords.

**Gallery View**
- **Group by:** AI Tool (Midjourney / DALL-E / Stable Diffusion).
- **Use Case:** Visual comparison. See which tool produces better results for a given style. Click any image to view its full prompt.

**Additional: Board by Project**
- **Group by:** Project Name.
- **Use Case:** See all assets for a single client project in one scrollable layout.

---

### 4. Automations & Formulas

**Formulas (inside Assets table)**
- `Prompt Length` = `len(prop("Prompt Used"))` – to track if prompts are too short/verbose.
- `Asset Age` = `dateBetween(now(), prop("Generation Date"), "days")` – shows how long an asset has been sitting without action.
- `Full Prompt Log` = `prop("AI Tool") + ": " + prop("Prompt Used")` – concatenation for quick copy-paste.

**Automations (Native Notify or manual scripting)**
- **When** `Asset.Status` changes to `Final` → **Send notification** to @Designer with link to asset + project name.
- **When** `Project.Deadline` is 2 days away and `Project.Status` is not `Approved` → **Send reminder** via email or Slack webhook.
- **Weekly digest**: Auto-create a database entry in a separate “Weekly Review” table summarizing total assets generated, top prompt lengths, and most-used AI tool.

---

### 5. How Users Benefit

| Pain Point | Solution from Template |
|------------|------------------------|
| Forgetting which prompt created the best result | Every asset stores its exact prompt and negative prompt. |
| Losing track of versions | Version # auto-increments; notes explain each revision. |
| No central repository for client assets | Gallery view + relation to project ensures one source of truth. |
| Wasting time on manual sorting | Kanban and Calendar views show status and deadlines at a glance. |
| Difficulty comparing AI tool performance | Gallery grouped by tool allows side-by-side visual comparison. |
| Deadline slippage | Automation alerts team 48 hours before project deadlines. |

**Real-world workflow example:**
1. Designer gets a brief → creates Project in Notion.
2. Runs 20 iterations in Midjourney → uploads to Assets table with exact prompts.
3. Drags best 3 into “Revised” on Kanban.
4. Client approves → status changed to “Final” → automation notifies the team.
5. Project status updated to “Delivered” → asset exported.

This template turns chaotic AI experimentation into a repeatable, client-ready design system.