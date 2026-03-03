const { GoogleSpreadsheet } = require('google-spreadsheet');
const { JWT } = require('google-auth-library');
const fs = require('fs');
const path = require('path');

/**
 * Syncs pages from sitemaps to a specific tab in a Google Sheet.
 * If config.google_sheet_id is missing, it creates a new Sheet and returns the ID.
 */
async function syncToGoogleSheets(config, siteRootOrData, tabName = "Inventory") {
    const isRawData = Array.isArray(siteRootOrData);
    const siteRoot = isRawData ? null : siteRootOrData;
    const rawData = isRawData ? siteRootOrData : null;
    const BASE_DIR = __dirname;
    const COMPANY_PATH = path.join(BASE_DIR, 'COMPANY.json');
    let companyName = "SEO Engine";

    if (fs.existsSync(COMPANY_PATH)) {
        try {
            const companyData = JSON.parse(fs.readFileSync(COMPANY_PATH, 'utf8'));
            companyName = companyData.company_name || "SEO Engine";
        } catch (e) {
            console.error('Error reading COMPANY.json:', e.message);
        }
    }

    try {
        const creds = JSON.parse(fs.readFileSync(path.join(BASE_DIR, '..', 'GOOGLE KEYS', 'endless-terra-488018-c4-2f632c3b19ef.json'), 'utf8'));

        const auth = new JWT({
            email: creds.client_email,
            key: creds.private_key,
            scopes: [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ],
        });

        let sheetId = config.google_sheet_id;
        const SHARED_ID_PATH = path.join(BASE_DIR, 'MASTER_SHEET_ID.json');

        // --- AUTO-DISCOVER OR CREATE SHEET ---
        // If sheetId is empty or the "demo" sheet ID, try to find a shared project ID
        const isDemoId = sheetId === '1oqN0tKGId4mchnWJTR72EHxeK-ZOVYUVVg3qnDvp-Ik';

        if (!sheetId || isDemoId) {
            if (fs.existsSync(SHARED_ID_PATH)) {
                try {
                    const sharedData = JSON.parse(fs.readFileSync(SHARED_ID_PATH, 'utf8'));
                    sheetId = sharedData.google_sheet_id;
                    console.log(`[Google Sheets] Found shared project sheet: ${sheetId}`);
                } catch (e) {
                    console.warn('[Google Sheets] Shared ID file corrupted.');
                }
            }

            // Still no valid ID? Create it.
            if (!sheetId || isDemoId) {
                const spreadsheetName = `${companyName} Master SEO`;
                console.log(`[Google Sheets] Zero-Config: Creating Master Spreadsheet "${spreadsheetName}"...`);

                const res = await auth.request({
                    url: 'https://www.googleapis.com/drive/v3/files',
                    method: 'POST',
                    data: {
                        name: spreadsheetName,
                        mimeType: 'application/vnd.google-apps.spreadsheet'
                    }
                });

                sheetId = res.data.id;
                console.log(`[Google Sheets] Created Master Sheet: ${sheetId}`);

                // Save it locally so ALL engines in this project find it
                fs.writeFileSync(SHARED_ID_PATH, JSON.stringify({
                    google_sheet_id: sheetId,
                    created_at: new Date().toISOString()
                }, null, 4));
            }
        }

        const doc = new GoogleSpreadsheet(sheetId, auth);
        await doc.loadInfo();
        console.log(`[Google Sheets] Connected to: "${doc.title}" (${sheetId})`);

        const sheetTitle = tabName;
        let sheet = doc.sheetsByTitle[sheetTitle];

        let headers = ['Slug', 'URL', 'Type', 'Page Role', 'Pillar/Parent', 'LastUpdated'];
        if (sheetTitle === 'Competitors') {
            headers = ['Competitor Name', 'Website URL', 'Top Keywords', 'Estimated Traffic', 'Last Audit'];
        } else if (rawData && rawData.length > 0) {
            headers = Object.keys(rawData[0]);
        }

        if (!sheet) {
            console.log(`Creating tab: ${sheetTitle}`);
            sheet = await doc.addSheet({
                title: sheetTitle,
                headerValues: headers
            });
        } else {
            console.log(`[${sheetTitle}] Enforcing headers: ${headers.join(', ')}`);
            await sheet.setHeaderRow(headers);
            await sheet.loadHeaderRow();
            console.log(`[${sheetTitle}] Verified headers: ${sheet.headerValues.join(', ')}`);
        }

        // --- COLLECT PAGES FROM SITEMAPS ---
        // Map tab names to sitemap sources for filtering
        const sourceMap = {
            'Locations': 'location',
            'Services': 'city-service',
            'Blogs': 'blog',
            'Newsletters': 'newsletter',
            'Competitors': 'competitor',
            'Core': 'core'
        };

        const targetSource = sourceMap[tabName];
        const allPages = [];

        const maps = [
            { path: 'sitemap.xml', source: 'all' },
            { path: 'sitemap-core.xml', source: 'core' },
            { path: 'sitemap-local.xml', source: 'local' },
            { path: 'sitemap-blog.xml', source: 'blog' },
            { path: 'sitemap-newsletter.xml', source: 'newsletter' }
        ];

        if (!rawData) {
            for (const map of maps) {
                const fullPath = path.join(siteRoot, map.path);
                if (fs.existsSync(fullPath)) {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    const urls = content.match(/<loc>(.*?)<\/loc>/g) || [];
                    urls.forEach(u => {
                        const url = u.replace(/<\/?loc>/g, '');

                        // Categorize based on URL pattern if source is 'all'
                        let effectiveSource = map.source;
                        if (effectiveSource === 'all') {
                            if (url.includes('/blog/')) effectiveSource = 'blog';
                            else if (url.includes('/locations/')) effectiveSource = 'location';
                            else if (url.includes('/services/')) effectiveSource = 'city-service';
                            else effectiveSource = 'core';
                        }

                        // If we have a target source, only collect matching ones
                        if (targetSource && effectiveSource !== targetSource) return;

                        allPages.push({
                            url,
                            source: effectiveSource,
                            pillar: 'Cornerstone',
                            focus: 'General'
                        });
                    });
                }
            }
        }

        // --- ENRICH FROM REGISTRY ---
        const registryPath = path.join(BASE_DIR, 'REGISTRY.json');
        const legacyRegistryPath = path.join(BASE_DIR, '..', 'REGISTRY.json');
        const finalRegistryPath = fs.existsSync(registryPath) ? registryPath : legacyRegistryPath;

        const registryMap = {};
        if (fs.existsSync(finalRegistryPath)) {
            try {
                const registryData = JSON.parse(fs.readFileSync(finalRegistryPath, 'utf8'));
                if (registryData && registryData.pages) {
                    registryData.pages.forEach(p => {
                        registryMap[p.slug] = p;
                    });
                }
            } catch (e) {
                console.error('[Google Sheets] Error reading REGISTRY.json:', e.message);
            }
        }

        // --- SYNC TO SHEET ---
        // Force clear to ensure new column structure is applied
        const forceClear = true;
        if (config.clear_before_sync || forceClear) {
            console.log(`[${tabName}] Clearing existing rows before re-sync...`);
            await sheet.clearRows();
        }

        const rows = await sheet.getRows();

        if (rawData) {
            console.log(`[${tabName}] Syncing ${rawData.length} raw data entries to Google Sheets...`);
            await sheet.addRows(rawData);
        } else {
            const existingUrls = new Set(rows.map(r => r.get('URL')));
            const newRows = allPages
                .filter(p => !existingUrls.has(p.url))
                .map(p => {
                    const slug = p.url.split('/').filter(Boolean).pop() || '/';
                    const regEntry = registryMap[slug] || {};

                    return {
                        Slug: slug,
                        URL: p.url,
                        Type: p.source,
                        'Page Role': regEntry.type === 'cornerstone' ? 'Cornerstone Page' : 'Sub Page',
                        'Pillar/Parent': regEntry.pillar || (p.source === 'location' ? 'Regional Coverage' : 'Root'),
                        LastUpdated: new Date().toISOString()
                    };
                });

            if (newRows.length > 0) {
                console.log(`[${tabName}] Syncing ${newRows.length} new entries to Google Sheets...`);
                await sheet.addRows(newRows);
            } else {
                console.log(`[${tabName}] Tab is up to date.`);
            }
        }

        return sheetId;

    } catch (err) {
        console.error('Google Sheets Sync Failed:', err.message);
        return null;
    }
}

module.exports = { syncToGoogleSheets };
