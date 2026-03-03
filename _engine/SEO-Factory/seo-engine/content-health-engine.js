const fs = require('fs');
const path = require('path');
const { syncToGoogleSheets } = require('./google-sheets-sync');

/**
 * Content Health Engine
 * Scans generated HTML files, checks word count, and reports to Google Sheets.
 */

const BASE_DIR = __dirname;
const SITE_ROOT = path.join(BASE_DIR, '..', '..', '..');
const CONFIG = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'local-engine', 'local-config.json'), 'utf8'));

async function auditContent() {
    console.log('--- Starting Content Health Audit ---');
    const healthReport = [];

    // Areas to scan
    const scanPaths = [
        { dir: path.join(SITE_ROOT, 'blog'), pillar: 'Blog' },
        { dir: path.join(SITE_ROOT, 'newsletter'), pillar: 'Newsletter' },
        { dir: path.join(SITE_ROOT, 'services'), pillar: 'Services' },
        { dir: path.join(SITE_ROOT, 'locations'), pillar: 'Locations' }
    ];

    for (const scan of scanPaths) {
        if (!fs.existsSync(scan.dir)) continue;

        const files = getAllHtmlFiles(scan.dir);
        for (const file of files) {
            const content = fs.readFileSync(file, 'utf8');
            const wordCount = countWords(content);
            const relativePath = path.relative(SITE_ROOT, file);
            const slug = path.dirname(relativePath).split(path.sep).pop() || 'root';

            healthReport.push({
                Slug: slug,
                URL: `https://workingclasshvac.com/${relativePath.replace('index.html', '')}`,
                'Word Count': wordCount,
                Status: wordCount < 200 ? 'Thin' : (wordCount < 500 ? 'Needs Expansion' : 'Healthy'),
                Pillar: scan.pillar,
                LastChecked: new Date().toISOString()
            });
        }
    }

    console.log(`[Health Engine] Audited ${healthReport.length} pages.`);

    // Sync to Google Sheets
    await syncToGoogleSheets(CONFIG, healthReport, "Content Health");
    console.log('--- Content Health Audit Complete ---');
}

function getAllHtmlFiles(dirPath, arrayOfFiles) {
    const files = fs.readdirSync(dirPath);
    arrayOfFiles = arrayOfFiles || [];

    files.forEach(function (file) {
        if (fs.statSync(dirPath + "/" + file).isDirectory()) {
            arrayOfFiles = getAllHtmlFiles(dirPath + "/" + file, arrayOfFiles);
        } else {
            if (file === 'index.html') {
                arrayOfFiles.push(path.join(dirPath, "/", file));
            }
        }
    });

    return arrayOfFiles;
}

function countWords(html) {
    // Strip HTML tags and extra whitespace
    const text = html.replace(/<[^>]*>?/gm, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    return text.split(' ').length;
}

if (require.main === module) {
    auditContent().catch(console.error);
}

module.exports = { auditContent };
