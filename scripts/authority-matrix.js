const fs = require('fs');
const path = require('path');
const { syncToGoogleSheets } = require('../_engine/SEO-Factory/seo-engine/google-sheets-sync');

/**
 * Authority Matrix Engine
 * Generates a Heatmap of Pillars vs. Cities to identify content gaps.
 */

const BASE_DIR = path.join(__dirname, '..');
const SEO_ENGINE_DIR = path.join(BASE_DIR, '_engine', 'SEO-Factory', 'seo-engine');
const CONFIG = JSON.parse(fs.readFileSync(path.join(SEO_ENGINE_DIR, 'local-engine', 'local-config.json'), 'utf8'));
const PILLARS = JSON.parse(fs.readFileSync(path.join(SEO_ENGINE_DIR, 'PILLARS.json'), 'utf8'));

async function generateMatrix() {
    console.log('--- Generating Authority Matrix ---');

    const SITE_ROOT = BASE_DIR;
    const cities = ['Lancaster', 'Palmdale', 'Quartz Hill', 'Tehachapi', 'Acton', 'Rosamond', 'Mojave', 'Littlerock', 'California City', 'Lake Los Angeles'];
    const pillars = PILLARS.pillars.map(p => p.name);

    const matrixData = [];

    for (const pillar of pillars) {
        const row = { Pillar: pillar };
        for (const city of cities) {
            row[city] = countPages(SITE_ROOT, pillar, city);
        }
        matrixData.push(row);
    }

    console.log(`[Matrix] Generated ${matrixData.length} pillar rows.`);
    await syncToGoogleSheets(CONFIG, matrixData, "Authority Matrix");
    console.log('--- Authority Matrix Complete ---');
}

function countPages(siteRoot, pillar, city) {
    let count = 0;
    const normalizedPillar = pillar.toLowerCase().replace(/\s+/g, '-');
    const normalizedCity = city.toLowerCase().replace(/\s+/g, '-');

    // Scan Blog, Locations, and Services
    const scanDirs = [
        path.join(siteRoot, 'blog'),
        path.join(siteRoot, 'locations'),
        path.join(siteRoot, 'services')
    ];

    scanDirs.forEach(dir => {
        if (fs.existsSync(dir)) {
            const files = getAllHtmlFiles(dir);
            files.forEach(file => {
                const content = fs.readFileSync(file, 'utf8').toLowerCase();
                if (content.includes(pillar.toLowerCase()) && content.includes(city.toLowerCase())) {
                    count++;
                }
            });
        }
    });

    return count;
}

function getAllHtmlFiles(dirPath, arrayOfFiles) {
    const files = fs.readdirSync(dirPath);
    arrayOfFiles = arrayOfFiles || [];
    files.forEach(function (file) {
        if (fs.statSync(dirPath + "/" + file).isDirectory()) {
            arrayOfFiles = getAllHtmlFiles(dirPath + "/" + file, arrayOfFiles);
        } else if (file === 'index.html') {
            arrayOfFiles.push(path.join(dirPath, "/", file));
        }
    });
    return arrayOfFiles;
}

if (require.main === module) {
    generateMatrix().catch(console.error);
}
