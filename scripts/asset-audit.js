const fs = require('fs');
const path = require('path');
const { syncToGoogleSheets } = require('../_engine/SEO-Factory/seo-engine/google-sheets-sync');

/**
 * Asset Audit Engine
 * Scans for images, checks alt text, and verifies format.
 */

const BASE_DIR = path.join(__dirname, '..');
const SEO_ENGINE_DIR = path.join(BASE_DIR, '_engine', 'SEO-Factory', 'seo-engine');
const CONFIG = JSON.parse(fs.readFileSync(path.join(SEO_ENGINE_DIR, 'local-engine', 'local-config.json'), 'utf8'));

async function auditAssets() {
    console.log('--- Starting Asset & Image Audit ---');
    const SITE_ROOT = BASE_DIR;
    const assetReport = [];

    const htmlFiles = getAllHtmlFiles(SITE_ROOT);
    console.log(`[Asset Audit] Found ${htmlFiles.length} HTML files to audit.`);

    for (const file of htmlFiles) {
        if (file.includes('node_modules')) continue;

        const content = fs.readFileSync(file, 'utf8');
        const imgTags = content.match(/<img [^>]*src="([^"]+)"[^>]*>/g) || [];

        imgTags.forEach(tag => {
            const src = tag.match(/src="([^"]+)"/)?.[1];
            const alt = tag.match(/alt="([^"]*)"/)?.[1];
            const relativePage = path.relative(SITE_ROOT, file);

            assetReport.push({
                'Page Path': relativePage,
                'Image Source': src,
                'Alt Text Status': alt ? '✅ Present' : '❌ MISSING (SEO Risk)',
                'Format': src ? (src.endsWith('.webp') ? 'Premium (WebP)' : 'Standard (Legacy)') : 'Unknown',
                'Last Verified': new Date().toISOString()
            });
        });
    }

    console.log(`[Asset Audit] Generated report with ${assetReport.length} image instances.`);
    await syncToGoogleSheets(CONFIG, assetReport, "Asset Health");
    console.log('--- Asset Audit Complete ---');
}

function getAllHtmlFiles(dirPath, arrayOfFiles) {
    const files = fs.readdirSync(dirPath);
    arrayOfFiles = arrayOfFiles || [];
    files.forEach(function (file) {
        const fullPath = path.join(dirPath, file);
        if (fs.statSync(fullPath).isDirectory()) {
            const exclude = ['node_modules', '.git', '_engine', 'scripts', 'GOOGLE KEYS'];
            if (!exclude.includes(file)) {
                arrayOfFiles = getAllHtmlFiles(fullPath, arrayOfFiles);
            }
        } else if (file === 'index.html') {
            arrayOfFiles.push(fullPath);
        }
    });
    return arrayOfFiles;
}

if (require.main === module) {
    auditAssets().catch(console.error);
}
