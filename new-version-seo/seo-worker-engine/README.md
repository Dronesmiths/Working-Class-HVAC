# 🚀 Master SEO Engine v1.7 - Working Class HVAC

The **Master SEO Engine** is a high-performance automation suite designed for "Website Factory" brands. It orchestrates technical SEO hygiene, programmatic content growth, and authority-building internal link meshes for **workingclasshvac.com**.

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
- `SPREADSHEET_ID`: `1Ipagk7rJmuqCooYkGcQfbs81fqHmuyvyj_MDkTRoSZk` (SEO Brain)
- `WEBSITE_DIR`: `../../` (Root of Working Class HVAC)
- `DOMAIN`: `https://workingclasshvac.com`
- `GSC_SITE_URL`: `sc-domain:workingclasshvac.com`

## ⚡ Setup Guide: GSC & Sheets Integration

The engine is already linked to the project's Google Cloud infrastructure via `service-account.json`.

## 🛠️ Operational Protocols

The engine is primarily operated via `scripts/seo_factory.py` (Wrapper).

### A. Full Synchronization (`sync`)
```bash
python3 scripts/seo_factory.py sync
```

### B. Sitemap Maintenance (`sitemap`)
```bash
python3 scripts/seo_factory.py sitemap
```

### C. Autopilot (Full Cycle) (`autopilot`)
```bash
python3 scripts/seo_factory.py autopilot
```

---
*Built for the Dronesmiths Website Factory | 2026 Strategy Suite*
