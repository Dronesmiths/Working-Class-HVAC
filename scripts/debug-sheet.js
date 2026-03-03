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

async function verify() {
    const doc = new GoogleSpreadsheet(CONFIG.google_sheet_id, auth);
    await doc.loadInfo();
    console.log(`Document Title: ${doc.title}`);

    for (const sheet of doc.sheetsByIndex) {
        console.log(`Sheet: ${sheet.title}`);
        console.log(`  Headers: ${sheet.headerValues.join(', ')}`);
    }
}

verify();
