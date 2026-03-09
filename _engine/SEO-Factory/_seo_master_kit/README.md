# 🛠️ Master SEO Engine Kit - Portable Edition

This kit contains the full Dronesmiths SEO Strategy Engine and specialized worker scripts. It is designed to be dropped into any new website project to instantly enable automated SEO auditing, sitemap management, and Search Console integration.

## 📁 Kit Structure

- `/engine`: The core `seo-worker-engine` (Python logic).
- `/workers`: Specialized scripts for Schema, OG Images, and health checks.
- `/config`: Template files for project setup.

## 🚀 Deployment Instructions

### 1. Initial Setup
1.  Copy the `_seo_master_kit` directory into your new project's root.
2.  Navigate to `_seo_master_kit/config/`.
3.  Duplicate `config.json.template` as `../engine/config.json`.
4.  Follow the **Setup Guide** below to provision your Google API keys.

### 2. Google Sheets & GSC Integration
Refer to the detailed guide in `/engine/README.md` to:
1.  Create a Google Cloud Project.
2.  Enable Search Console and Sheets APIs.
3.  Create a Service Account and save it as `/engine/service-account.json`.
4.  Link your Google Sheet and Search Console property.

### 3. Running the Engine
From your project root (outside the kit):

**To Sync everything to the Sheet:**
```bash
python3 _seo_master_kit/engine/core/seo_factory.py sync
```

**To Update the Sitemap:**
```bash
python3 _seo_master_kit/engine/core/seo_factory.py sitemap
```

**To Run Workers (Schema, OG Images):**
```bash
python3 _seo_master_kit/workers/add_schema_markup.py
python3 _seo_master_kit/workers/add_og_images.py
```

## 🤖 AI Exploration Protocol
When an AI agent (Antigravity/Jules) enters a project with this kit:
1.  It should read `/engine/README.md` to understand the sheet architecture.
2.  It should check `engine/config.json` to ensure the project IDs are correct.
3.  It can use the commands above to maintain the site's SEO authority.

---
*Dronesmiths | Website Factory Standards 2026*
