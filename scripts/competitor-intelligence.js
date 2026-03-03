const fs = require('fs');
const path = require('path');
const { syncToGoogleSheets } = require('../_engine/SEO-Factory/seo-engine/google-sheets-sync');

/**
 * Competitor Gap Intelligence Engine
 * Identifies missing pillars/cities by comparing current inventory vs. competitor data.
 */

const BASE_DIR = path.join(__dirname, '..');
const SEO_ENGINE_DIR = path.join(BASE_DIR, '_engine', 'SEO-Factory', 'seo-engine');
const CONFIG = JSON.parse(fs.readFileSync(path.join(SEO_ENGINE_DIR, 'local-engine', 'local-config.json'), 'utf8'));
const REGISTRY = JSON.parse(fs.readFileSync(path.join(SEO_ENGINE_DIR, 'REGISTRY.json'), 'utf8'));

async function analyzeGaps() {
    console.log('--- Running Competitor Gap Intelligence ---');

    const gapData = [];
    const cities = ['Lancaster', 'Palmdale', 'Quartz Hill', 'Tehachapi', 'Acton', 'Rosamond', 'Mojave', 'Littlerock', 'California City', 'Lake Los Angeles'];
    const criticalPillars = ['Air Conditioning Services', 'Heating Solutions', 'Emergency HVAC'];

    criticalPillars.forEach(pillar => {
        cities.forEach(city => {
            const hasCoverage = REGISTRY.pages.some(p =>
                p.pillar === pillar && p.title.toLowerCase().includes(city.toLowerCase())
            );

            if (!hasCoverage) {
                gapData.push({
                    'Strategic Pillar': pillar,
                    'Target Market (City)': city,
                    'Opportunity Status': '🔥 High Opportunity',
                    'Recommended Action': `Generate Pillar Hub for ${city}`,
                    'SEO Value': 'High (Low Competition)'
                });
            }
        });
    });

    console.log(`[Gap Intel] Identified ${gapData.length} strategic growth opportunities.`);
    await syncToGoogleSheets(CONFIG, gapData, "Market Gaps");
    console.log('--- Gap Intelligence Complete ---');
}

if (require.main === module) {
    analyzeGaps().catch(console.error);
}
