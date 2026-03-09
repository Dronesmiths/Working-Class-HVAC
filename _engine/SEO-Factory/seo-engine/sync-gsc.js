const { JWT } = require('google-auth-library');
const fs = require('fs');
const path = require('path');

const BASE_DIR = __dirname;
const CREDENTIALS_PATH = path.join(BASE_DIR, '..', 'GOOGLE KEYS', 'endless-terra-488018-c4-2f632c3b19ef.json');
const ANALYTICS_DIR = path.join(BASE_DIR, 'ANALYTICS');
const GSC_PULL_PATH = path.join(ANALYTICS_DIR, 'GSC_PULL.json');
const DOMAIN = 'sc-domain:workingclasshvac.com';

async function syncGSC() {
    console.log('--- Starting Google Search Console Sync ---');
    
    if (!fs.existsSync(ANALYTICS_DIR)) {
        fs.mkdirSync(ANALYTICS_DIR, { recursive: true });
    }

    try {
        const creds = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
        const auth = new JWT({
            email: creds.client_email,
            key: creds.private_key,
            scopes: ['https://www.googleapis.com/auth/webmasters.readonly'],
        });

        console.log(`Service Account: ${creds.client_email}`);
        console.log(`Property: ${DOMAIN}`);

        const today = new Date();
        const ninetyDaysAgo = new Date(today);
        ninetyDaysAgo.setDate(today.getDate() - 90);
        
        const startDate = ninetyDaysAgo.toISOString().split('T')[0];
        const endDate = today.toISOString().split('T')[0];

        console.log(`Fetching query data from ${startDate} to ${endDate}...`);
        
        const res = await auth.request({
            url: `https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(DOMAIN)}/searchAnalytics/query`,
            method: 'POST',
            data: {
                startDate,
                endDate,
                dimensions: ['query'],
                rowLimit: 500
            }
        });

        const rows = res.data.rows || [];
        console.log(`Fetched ${rows.length} queries.`);

        const pullData = {
            last_sync: new Date().toISOString(),
            domain: DOMAIN,
            date_range: { startDate, endDate },
            top_queries: rows.map(r => ({
                query: r.keys[0],
                clicks: r.clicks,
                impressions: r.impressions,
                ctr: r.ctr,
                position: r.position
            }))
        };

        fs.writeFileSync(GSC_PULL_PATH, JSON.stringify(pullData, null, 2));
        console.log(`✅ SUCCESS: Data saved to ${GSC_PULL_PATH}`);

    } catch (err) {
        console.error('❌ ERROR: GSC Sync failed.');
        console.error(err.response ? JSON.stringify(err.response.data, null, 2) : err.message);
        process.exit(1);
    }
}

syncGSC();
