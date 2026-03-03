const { GoogleSpreadsheet } = require('google-spreadsheet');
const { JWT } = require('google-auth-library');
const fs = require('fs');
const path = require('path');

const BASE_DIR = path.join(__dirname, '_engine', 'SEO-Factory', 'seo-engine');
const CONFIG_PATH = path.join(BASE_DIR, 'local-engine', 'local-config.json');
const CONFIG = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

const creds = JSON.parse(fs.readFileSync(path.join(BASE_DIR, '..', 'GOOGLE KEYS', 'endless-terra-488018-c4-2f632c3b19ef.json'), 'utf8'));

const auth = new JWT({
    email: creds.client_email,
    key: creds.private_key,
    scopes: [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ],
});

async function runAnalysis() {
    console.log('--- Pushing Competitor Intelligence to Master Sheet ---');
    const doc = new GoogleSpreadsheet(CONFIG.google_sheet_id, auth);
    await doc.loadInfo();

    const sheet = doc.sheetsByTitle['Competitors'];
    if (!sheet) {
        console.error('Competitors sheet not found. Run init-competitors.js first.');
        return;
    }

    const competitorData = [
        {
            'Competitor Name': 'All Heart Heating & Cooling',
            'Website URL': 'https://callallheart.com',
            'Top Keywords': 'ac repair lancaster ca, energy saving hvac, heating and cooling lancaster',
            'Estimated Traffic': 'High (Active local ads)',
            'Last Audit': new Date().toISOString()
        },
        {
            'Competitor Name': 'Arctic Air',
            'Website URL': 'https://arcticairav.com',
            'Top Keywords': 'ac replacement lancaster, ductless mini split lancaster, hvac maintenance av',
            'Estimated Traffic': 'Moderate (High reputation)',
            'Last Audit': new Date().toISOString()
        },
        {
            'Competitor Name': 'Preciado Air Conditioning',
            'Website URL': 'https://preciadoairconditioning.com',
            'Top Keywords': 'ac repair palmdale, hvac contractor palmdale, furnace repair palmdale',
            'Estimated Traffic': 'High (Regional leader)',
            'Last Audit': new Date().toISOString()
        },
        {
            'Competitor Name': 'Econo West Heating & Air',
            'Website URL': 'https://econowest.com',
            'Top Keywords': 'emergency ac repair lancaster, plumbing and hvac palmdale, hvac financing ca',
            'Estimated Traffic': 'High (Multichannel presence)',
            'Last Audit': new Date().toISOString()
        }
    ];

    console.log(`Pushing ${competitorData.length} competitors...`);
    await sheet.addRows(competitorData);
    console.log('✅ Success! Competitor data is now live.');
}

runAnalysis();
