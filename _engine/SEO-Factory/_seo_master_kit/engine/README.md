# 🚀 Master SEO Engine v1.7

The **Master SEO Engine** is a high-performance automation suite designed for "Website Factory" brands. It orchestrates technical SEO hygiene, programmatic content growth, and authority-building internal link meshes.

This engine is built to be **AI-Native**, providing future explorers (Antigravity/Jules) with the data and protocols needed to scale search authority for property service niches.

## 🏗️ Project Architecture

```text
new-version-seo/seo-worker-engine/
├── config.json              # Site-specific IDs and Paths
├── service-account.json     # Google Cloud Identity (Service Account)
├── README.md                # This file (The Engine Manual)
└── core/
    ├── seo_factory.py       # Main Execution Engine (Python)
    ├── registries/          # Strategy Seeding Data
    │   ├── cornerstones.json
    │   ├── subpage_plan.json
    │   └── market_intel.json
    └── templates/           # (Optional) HTML/SEO Component Templates
```

## ⚙️ Configuration

### 1. `config.json`
Located at the engine root, this file defines the operational environment:
- `SPREADSHEET_ID`: The "SEO Brain" Sheet where all audits and growth plans live.
- `WEBSITE_DIR`: Path to the local website source files (relative to `core/`).
- `DOMAIN`: Canonical URL of the production site (e.g., `https://aipilots.site`).
- `GSC_SITE_URL`: Google Search Console property ID (e.g., `sc-domain:aipilots.site`).
- `SITEMAP_MAPPING`: Defines how URLs are categorized (Services, Blog, Locations, etc.).

### 2. Google Identity
Place a `service-account.json` in the engine root with `Sheets` and `Search Console` API access.

---

## ⚡ Setup Guide: GSC & Sheets Integration

To enable the "SEO Brain," you must link the physical site with the Google Cloud infrastructure.

### Step 1: Google Cloud Project Setup
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (e.g., `seo-factory-engine`).
3.  **Enable APIs**: 
    - Search for and enable the **Google Sheets API**.
    - Search for and enable the **Google Search Console API**.
4.  **Create Service Account**:
    - Navigate to **IAM & Admin > Service Accounts**.
    - Create a service account named `seo-worker`.
    - Create a JSON key for this account and save it as `service-account.json` in the engine root.
    - **Copy the service account email** (e.g., `seo-worker@your-project-id.iam.gserviceaccount.com`).

### Step 2: Google Sheet Preparation
1.  Create a fresh Google Sheet.
2.  **Share the Sheet**: Click "Share" and paste the `seo-worker` service account email. Give it **Editor** access.
3.  **Find the ID**: Copy the ID from the URL: `docs.google.com/spreadsheets/d/[THIS_PART_IS_THE_ID]/edit`.
4.  Paste this ID into `config.json` under `SPREADSHEET_ID`.

### Step 3: Google Search Console (GSC) Link
1.  Go to [Google Search Console](https://search.google.com/search-console).
2.  Select your property.
3.  Go to **Settings > Users and Permissions**.
4.  Add the `seo-worker` service account email as a **Viewer**.
5.  In `config.json`, set `GSC_SITE_URL` to match your property (e.g., `sc-domain:aipilots.site` or `https://aipilots.site/`).

---

## 🛠️ Operational Protocols

The engine is primarily operated via `core/seo_factory.py`.

### A. Full Synchronization (`sync`)
```bash
python3 core/seo_factory.py sync
```
*   **What it does**: 
    1. Crawls the local site and audits every page for SEO health (Title, Meta, H1).
    2. Fetches real performance data (Impressions, Clicks, Positions) from GSC.
    3. Calculates Internal Link gravity and authority clusters.
    4. Performs Gap Analysis against `cornerstones.json` and `subpage_plan.json`.
    5. Updates the Google Sheet with fresh metrics and growth recommendations.

### B. Sitemap Maintenance (`sitemap`)
```bash
python3 core/seo_factory.py sitemap
```
*   **What it does**: Regenerates the `sitemap.xml` based on the current local file structure, ensuring all `index.html` files are included.

## 📊 Sheet Architecture (The "SEO Brain")

The Google Sheet is the central command center for the engine. It is organized into specialized tabs that drive the "Website Factory" growth logic.

### 🧭 Strategy & Guidance
*   **📖 CLIENT GUIDE**: A glossary of terms and instructions for the client. Explains the value of each section of the sheet.
*   **📊 RESULTS DASHBOARD**: Executive summary of KPIs: Total Pages, Website Health Score, Monthly Traffic, and Sync Status.

### 🏥 Technical Hygiene
*   **🏥 WEBSITE WELLNESS**: The primary audit log. Tracks **URL**, **Health Score**, **Meta Title**, **Meta Description**, and **Status**. It flags technical debt that needs fixing.
*   **📂 SERVICE PAGES / ✍️ BLOG ARTICLES**: Filtered views of the wellness data specifically for core service offerings and content marketing.

### 🧱 Authority & Structure
*   **Sitemap Inventory**: The canonical list of every live page. Maps URLs to **Page Types** and **Parent Topics/Clusters**.
*   **Cornerstone_Map**: Tracks "Authority Pillars" (Cornerstones). Compares the **Ideal Page Count** for a topic against the **Current Live Count** to find gaps.
*   **Subpage_Plan**: A tactical roadmap of planned supporting pages for each cornerstone, tracking their implementation status.

### 🚀 Performance & Growth
*   **🔑 CONTENT PERFORMANCE**: Imports real data from Search Console. Shows **Keywords**, **Current Rank**, **Target Page**, and **Impressions**.
*   **🛡️ AUTHORITY RADAR**: Calculated cluster strength metrics. Shows **Gravity Score** (total authority) and **Opportunity Score** (potential for ROI).
*   **⚔️ CLUSTER MAP**: Visual summary of topics. Categorizes clusters as **Dominant** (Reinforce), **Growth** (Expand), or **Expansion Needed** (Build).
*   **🚀 EXPANSION ENGINE**: AI-generated page suggestions based on the Gaps found in the Cornerstone Analysis. Use this to guide your next content sprint.

### � Linking & Optimization
*   **Backlink_Audit**: Audits internal and external link counts for every page to ensure link juice is flowing correctly.
*   **Internal_Link_Queue**: Strategic suggestions for specific links to add (Source → Target) to boost underperforming clusters.
*   **Reinforcement_Queue**: A list of existing pages that need updates, title tweaks, or content expansion based on GSC performance data.

## 🤖 AI Protocol for Future Explorers

When starting work on a site powered by this engine, follow these steps:

1.  **Check the Health**: Run `sync` and check the **WELLNESS** tab. Fix any 🔴 "Needs Improvement" pages before building new content.
2.  **Verify the Strategy**: Read `core/registries/cornerstones.json` to understand the primary "Authority Pillars" of the brand.
3.  **Execute Growth**: Check the **EXPANSION ENGINE** tab. The engine identifies exactly which subpages are missing to complete a cluster.
4.  **Harden Links**: Use the **Backlink_Audit** results to identify "Under-linked" pages and inject internal links into relevant content.

---
*Built for the Dronesmiths Website Factory | 2026 Strategy Suite*
