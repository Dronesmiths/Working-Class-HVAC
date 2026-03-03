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
                'Format': src.endsWith('.webp') ? 'Premium (WebP)' : 'Standard (Legacy)',
                'Last Verified': new Date().toISOString()
            });
        });
    }

    console.log(`[Asset Audit] Audited ${assetReport.length} image instances.`);
    await syncToGoogleSheets(CONFIG, assetReport, "Asset Health");
    console.log('--- Asset Audit Complete ---');
}

function getAllHtmlFiles(dirPath, arrayOfFiles) {
    const files = fs.readdirSync(dirPath);
    arrayOfFiles = arrayOfFiles || [];
    files.forEach(function(file) {
        const fullPath = path.join(dirPath, file);
        if (fs.statSync(fullPath).isDirectory()) {
            if (file !== 'node_modules' && file !== '.git') {
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
