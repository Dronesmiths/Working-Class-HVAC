const { GoogleSpreadsheet } = require('google-spreadsheet');
const { JWT } = require('google-auth-library');
const fs = require('fs');
const path = require('path');

const CREDENTIALS_PATH = path.join(__dirname, '..', 'GOOGLE KEYS', 'endless-terra-488018-c4-2f632c3b19ef.json');
const SPREADSHEET_ID = '1Ipagk7rJmuqCooYkGcQfbs81fqHmuyvyj_MDkTRoSZk';

const NEW_TABS = [
    { title: '📖 CLIENT GUIDE', headers: ['Term', 'Definition', 'Purpose'] },
    { title: '📊 RESULTS DASHBOARD', headers: ['KPI', 'Current Value', 'Previous Value', 'Change %'] },
    { title: '🏥 WEBSITE WELLNESS', headers: ['URL', 'Health Score', 'Meta Title', 'Meta Description', 'H1', 'Status'] },
    { title: '📂 SERVICE PAGES', headers: ['URL', 'Service Name', 'Health Score', 'Last Updated'] },
    { title: '📍 LOCATION PAGES', headers: ['URL', 'Location Name', 'Health Score', 'Last Updated'] },
    { title: '✍️ BLOG ARTICLES', headers: ['URL', 'Article Title', 'Health Score', 'Last Updated'] },
    { title: 'Sitemap Inventory', headers: ['URL', 'Page Type', 'Parent Topic', 'Last Synced'] },
    { title: 'Cornerstone_Map', headers: ['Topic', 'Ideal Count', 'Current Count', 'Gap', 'Priority'] },
    { title: 'Subpage_Plan', headers: ['Parent Topic', 'Subpage Title', 'Status', 'Launch Date'] },
    { title: '🔑 CONTENT PERFORMANCE', headers: ['Keyword', 'Clicks', 'Impressions', 'CTR', 'Position', 'Target Page'] },
    { title: '🛡️ AUTHORITY RADAR', headers: ['Cluster', 'Gravity Score', 'Opportunity Score', 'Next Action'] },
    { title: '⚔️ CLUSTER MAP', headers: ['Cluster Name', 'Strategy', 'Status'] },
    { title: '🚀 EXPANSION ENGINE', headers: ['Suggested Slug', 'Focus Keyword', 'Category', 'Reason'] },
    { title: 'Backlink_Audit', headers: ['URL', 'Internal In', 'Internal Out', 'External Out', 'Status'] },
    { title: 'Internal_Link_Queue', headers: ['Source URL', 'Target URL', 'Anchor Text', 'Applied'] },
    { title: 'Reinforcement_Queue', headers: ['URL', 'Metric Issue', 'Resolution Strategy', 'Status'] }
];

async function updateSheet() {
    try {
        const creds = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
        const auth = new JWT({
            email: creds.client_email,
            key: creds.private_key,
            scopes: [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.file'
            ],
        });

        const doc = new GoogleSpreadsheet(SPREADSHEET_ID, auth);
        await doc.loadInfo();
        console.log(`Connected to: "${doc.title}"`);

        for (const tab of NEW_TABS) {
            if (!doc.sheetsByTitle[tab.title]) {
                console.log(`Adding tab: ${tab.title}`);
                await doc.addSheet({
                    title: tab.title,
                    headerValues: tab.headers
                });
            } else {
                console.log(`Tab already exists: ${tab.title} (Enforcing headers)`);
                const sheet = doc.sheetsByTitle[tab.title];
                await sheet.setHeaderRow(tab.headers);
            }
        }
        console.log('✅ Sheet architecture updated successfully.');
    } catch (err) {
        console.error('❌ Error updating sheet:', err.message);
    }
}

updateSheet();
