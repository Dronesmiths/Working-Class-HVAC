const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { runValidation } = require('./validate');
const { syncToGoogleSheets } = require('../google-sheets-sync');
const { syncWithMasterIndex } = require('../sitemap-utils');
const maps = require('../map-utils');
const weather = require('../weather-utils');
const pollen = require('../pollen-utils');

const BASE_DIR = __dirname;
const CONFIG = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'local-config.json'), 'utf8'));
const LOCATIONS = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'locations.json'), 'utf8'));
const SERVICES = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'services.json'), 'utf8'));
const GEO_DATA = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'geo-data.json'), 'utf8'));
const BUILD_MAP_PATH = path.join(BASE_DIR, 'build-map.json');
const BUILD_LOG_PATH = path.join(BASE_DIR, 'logs', 'local-build-log.json');
const SITEMAP_PATH = path.join(BASE_DIR, 'sitemap-local.xml');
const MASTER_SITEMAP_PATH = path.join(BASE_DIR, '..', '..', 'sitemap.xml');
const SEO_KW_MAP_PATH = path.join(BASE_DIR, '..', 'KW_MAP.json');
const TEMPLATE_PATH = path.join(BASE_DIR, '..', 'TEMPLATES', 'page-template.html');
const SITE_ROOT = path.join(BASE_DIR, '..', '..', '..', '..');
const LOCK_FILE = path.join(BASE_DIR, '.build-lock');
const SITEMAP_HASH_PATH = path.join(BASE_DIR, 'logs', 'sitemap-hash.txt');

const DRY_RUN = process.argv.includes('--dry-run');

// --- UTILS ---

function writeAtomic(filePath, content) {
    if (DRY_RUN) {
        console.log(`[DRY RUN] Would write to: ${filePath}`);
        return;
    }
    const tmpPath = filePath + '.tmp';
    fs.writeFileSync(tmpPath, content);
    fs.renameSync(tmpPath, filePath);
}

function generateSitemap(urls) {
    const lastmod = new Date().toISOString().split('T')[0];
    let xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n`;

    urls.forEach(url => {
        xml += `  <url>\n    <loc>${CONFIG.domain}${url}</loc>\n    <lastmod>${lastmod}</lastmod>\n  </url>\n`;
    });

    xml += `</urlset>`;
    return xml;
}

function getChecksum(content) {
    return crypto.createHash('md5').update(content).digest('hex');
}

function verifySitemapIntegrity(newContent) {
    if (!fs.existsSync(SITEMAP_PATH)) {
        console.log('Local sitemap missing. This run will regenerate it.');
        return true;
    }
    if (!fs.existsSync(SITEMAP_HASH_PATH)) {
        console.log('Checksum missing. This run will re-baseline it.');
        return true;
    }

    const oldHash = fs.readFileSync(SITEMAP_HASH_PATH, 'utf8').trim();
    const currentHash = getChecksum(fs.readFileSync(SITEMAP_PATH, 'utf8'));

    if (oldHash !== currentHash) {
        console.error('CRITICAL: Sitemap integrity failure! Hash mismatch. Manual intervention required.');
        return false;
    }
    return true;
}

function syncWithMasterSitemap() {
    if (!CONFIG.auto_sitemap_sync || !fs.existsSync(MASTER_SITEMAP_PATH)) return;

    let masterContent = fs.readFileSync(MASTER_SITEMAP_PATH, 'utf8');
    const localSitemapUrl = `${CONFIG.domain}/sitemap-local.xml`;

    if (masterContent.includes(localSitemapUrl)) {
        console.log('Master sitemap already synced.');
        return;
    }

    // Logic to append to sitemapindex or convert urlset
    if (masterContent.includes('</sitemapindex>')) {
        const replacement = `  <sitemap>\n    <loc>${localSitemapUrl}</loc>\n  </sitemap>\n</sitemapindex>`;
        masterContent = masterContent.replace('</sitemapindex>', replacement);
    } else if (masterContent.includes('</urlset>')) {
        // Convert urlset to sitemapindex for the root index
        console.log('Converting root sitemap to sitemapindex for safe scaling...');

        // Save the old core urls to sitemap-core.xml first to prevent loss
        const coreSitemapPath = path.join(SITE_ROOT, 'sitemap-core.xml');
        if (!fs.existsSync(coreSitemapPath)) {
            writeAtomic(coreSitemapPath, masterContent);
        }

        masterContent = `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
            `  <sitemap>\n    <loc>${CONFIG.domain}/sitemap-core.xml</loc>\n  </sitemap>\n` +
            `  <sitemap>\n    <loc>${localSitemapUrl}</loc>\n  </sitemap>\n` +
            `  <sitemap>\n    <loc>${CONFIG.domain}/sitemap-blog.xml</loc>\n  </sitemap>\n` +
            `</sitemapindex>`;
    }

    writeAtomic(MASTER_SITEMAP_PATH, masterContent);
    console.log('Synced with master sitemap.');
}

function normalizeSlug(slug) {
    return slug.toLowerCase()
        .trim()
        .replace(/[^a-z0-9]/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
}

function hasGeoIntent(keyword) {
    if (CONFIG.mode === 'manual') return true;
    const tokens = keyword.toLowerCase().split(/\s+/);
    const intentMarkers = CONFIG.geo_intent_keywords || [];
    return intentMarkers.some(marker => tokens.includes(marker));
}

function getKeywordHits(keyword, kwMap) {
    let hits = 0;
    const searchLow = keyword.toLowerCase();
    for (const key in kwMap) {
        if (key.toLowerCase().includes(searchLow)) hits++;
        if (Array.isArray(kwMap[key])) {
            kwMap[key].forEach(val => {
                if (val.toLowerCase().includes(searchLow)) hits++;
            });
        }
    }
    return hits;
}

const ANALYTICS_DIR = path.join(BASE_DIR, '..', 'ANALYTICS');
const GSC_PULL_PATH = path.join(ANALYTICS_DIR, 'GSC_PULL.json');

// --- GSC STRENGTHENING ---

function strengthenWithGSC() {
    console.log('--- Analyzing GSC Data for Strengthening Opportunities ---');
    if (!fs.existsSync(GSC_PULL_PATH)) {
        console.log('No GSC data found. Skipping.');
        return [];
    }

    const gscData = JSON.parse(fs.readFileSync(GSC_PULL_PATH, 'utf8'));
    const newOpportunities = [];

    // Analyze top and rising queries for geo-intent
    const queries = [...(gscData.top_queries || []), ...(gscData.rising_queries || [])];

    queries.forEach(q => {
        const query = typeof q === 'string' ? q : q.query;
        if (!query) return;

        if (hasGeoIntent(query)) {
            // Extract city name (basic heuristic: last word or words after 'in'/'at')
            let potentialCity = '';
            if (query.includes(' in ')) potentialCity = query.split(' in ')[1];
            else if (query.includes(' at ')) potentialCity = query.split(' at ')[1];
            else potentialCity = query.split(' ').pop();

            if (potentialCity && potentialCity.length > 3) {
                const slug = normalizeSlug(potentialCity);
                newOpportunities.push({
                    city: potentialCity.charAt(0).toUpperCase() + potentialCity.slice(1),
                    state: 'CA', // Default for now
                    slug: slug,
                    reason: `GSC Opportunity: ${query}`
                });
            }
        }
    });

    return newOpportunities;
}

async function generateProLocationPage(dir, url, title, h1, locationString, cityData, weatherData, pollenData) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    const filePath = path.join(dir, 'index.html');

    // For this Pro Upgrade, we want to allow overwriting to apply the new styling
    // to existing pages. We'll log it instead of skipping.
    if (fs.existsSync(filePath)) {
        console.log(`Updating existing page with pro styling: ${filePath}`);
    } else {
        console.log(`Generating new pro page: ${filePath}`);
    }

    let template = fs.readFileSync(TEMPLATE_PATH, 'utf8');

    // --- GEO SIGNALS ---
    const cityInfo = GEO_DATA.cities[cityData.city] || {};
    const zipString = cityInfo.zip_codes ? `Serving: ${cityInfo.zip_codes.join(', ')}` : '';
    const landmarkHtml = cityInfo.landmarks ? `
        <div class="local-landmarks">
            <h5>Local Landmarks & Service Areas</h5>
            <ul>
                ${cityInfo.landmarks.map(l => `<li>${l}</li>`).join('')}
            </ul>
        </div>` : '';

    // --- MAP COMPONENTS ---
    let mapHtml = '';
    const apiKey = CONFIG.google_maps_api_key;
    const flags = CONFIG.maps_feature_flags || {};

    if (apiKey) {
        if (flags.show_live_map) mapHtml += maps.generateMapEmbed(apiKey, locationString);
        if (flags.show_static_map) mapHtml += maps.generateStaticMap(apiKey, locationString);
        if (flags.show_street_view) mapHtml += maps.generateStreetView(apiKey, locationString);
        if (flags.show_directions) mapHtml += maps.generateDirectionsLink(locationString, CONFIG.business_address);
        if (flags.show_reviews && CONFIG.google_place_id) mapHtml += maps.generatePlaceReview(apiKey, CONFIG.google_place_id);
    }

    // --- ENVIRONMENTAL COMPONENTS ---
    const weatherHtml = weather.generateWeatherSnippet(cityData.city, cityData.state, weatherData);
    const pollenHtml = pollen.generatePollenSnippet(pollenData);

    const bodySections = `
<!-- FACTORY:BODY_START -->
<div class="pro-location-content">
    <div class="hero-subline">Premium HVAC Solutions for ${locationString}</div>
    <div class="zip-coverage">${zipString}</div>
    
    <div class="environmental-dashboard">
        ${weatherHtml}
        ${pollenHtml}
    </div>

    <div class="content-block main-narrative">
        <p>Working Class HVAC is dedicated to providing the residents of ${cityData.city} with reliable, high-performance heating and cooling solutions. Given the <strong>${cityInfo.climate_type || 'local climate'}</strong>, maintaining system efficiency is critical for both comfort and cost-savings.</p>
        <p>Our technicians are experts in ${h1}, ensuring your home or business remains optimized regardless of the high desert's extreme shifts.</p>
    </div>

    ${landmarkHtml}
    
    <div class="map-container">
        ${mapHtml}
    </div>
</div>
<!-- FACTORY:BODY_END -->
    `;

    template = template.replace('{{TITLE}}', title)
        .replace('{{H1}}', h1)
        .replace('{{CANONICAL_URL}}', `${CONFIG.domain}${url}`)
        .replace('{{META_DESCRIPTION}}', `Professional ${h1} in ${locationString}. Live weather, pollen alerts, and expert HVAC care for ${cityData.city} residents.`)
        .replace('{{INTRO}}', `Optimizing indoor comfort for ${cityData.city}. Check local weather and environmental alerts below.`)
        .replace('{{BODY_SECTIONS}}', bodySections)
        .replace('{{FAQ_BLOCK}}', '<!-- FACTORY:FAQ_START -->\n<!-- FACTORY:FAQ_END -->')
        .replace('{{CTA_HEADING}}', `Schedule Service in ${cityData.city}`)
        .replace('{{CTA_TEXT}}', `Join hundreds of satisfied homeowners in ${cityData.city} who trust Working Class HVAC.`)
        .replace('{{CTA_LABEL}}', 'Call Now')
        .replace('{{CTA_URL}}', 'tel:661-235-0000');

    writeAtomic(filePath, template);
}

function validateCategory() {
    const company = JSON.parse(fs.readFileSync(path.join(BASE_DIR, '..', 'COMPANY.json'), 'utf8'));
    const categoryKeywords = ['HVAC', 'Air Conditioning', 'Heating', 'Cooling', 'AC Repair'];
    const legacyKeywords = ['Special Education', 'Assessment', 'IEE', 'CAS Evals'];

    const companyName = company.company_name || "";
    const isHVAC = categoryKeywords.some(kw => companyName.includes(kw));
    const isLegacy = legacyKeywords.some(kw => companyName.includes(kw));

    if (!isHVAC || isLegacy) {
        console.error(`CRITICAL: Category mismatch. Detected: "${companyName}". Expected: HVAC. ABORTING.`);
        process.exit(1);
    }
    console.log(`✅ Category Verified: HVAC Project (${companyName})`);
}

async function build() {
    validateCategory();
    if (DRY_RUN) console.log('*** DRY RUN MODE: No files will be written ***');

    if (!DRY_RUN && fs.existsSync(LOCK_FILE)) {
        const lockTime = parseInt(fs.readFileSync(LOCK_FILE, 'utf8'));
        const ageInMinutes = (Date.now() - lockTime) / (1000 * 60);
        const ttl = CONFIG.lock_ttl_minutes || 30;

        if (ageInMinutes < ttl) {
            console.error(`Error: Build lock active (age: ${ageInMinutes.toFixed(1)}m, TTL: ${ttl}m).`);
            process.exit(1);
        } else {
            console.warn(`Stale lock detected (age: ${ageInMinutes.toFixed(1)}m). Resetting for fresh run.`);
            fs.unlinkSync(LOCK_FILE);
        }
    }

    if (!DRY_RUN) fs.writeFileSync(LOCK_FILE, Date.now().toString());

    const summary = {
        date: new Date().toISOString().split('T')[0],
        new_cities: 0,
        new_services: 0,
        skipped_duplicates: 0,
        skipped_low_intent: [],
        skipped_collisions: [],
        errors: []
    };

    // --- STEP 0: GSC STRENGTHENING ---
    if (CONFIG.mode !== 'manual') {
        const opportunities = strengthenWithGSC();
        opportunities.forEach(opp => {
            if (!LOCATIONS.find(l => normalizeSlug(l.slug) === opp.slug)) {
                console.log(`[GSC] Found new opportunity: ${opp.city} (${opp.reason})`);
                LOCATIONS.push(opp);
            }
        });
    }

    try {
        runValidation();

        const buildLog = JSON.parse(fs.readFileSync(BUILD_LOG_PATH, 'utf8'));
        const existingUrls = new Set(buildLog.builds.map(b => b.url));
        const newUrls = [];
        const kwMap = fs.existsSync(SEO_KW_MAP_PATH) ? JSON.parse(fs.readFileSync(SEO_KW_MAP_PATH, 'utf8')) : {};

        let totalPagesBuiltInRun = 0;
        const maxTotalPages = CONFIG.max_total_new_pages_per_run || 25;
        let locationsInRun = 0;
        const maxLocations = CONFIG.max_new_locations_per_run || 3;

        const seenSlugs = new Set();
        const maxServices = CONFIG.max_services_per_location || 5;

        for (const loc of LOCATIONS) {
            let newServicesCount = 0;
            if (totalPagesBuiltInRun >= maxTotalPages) break;
            if (locationsInRun >= maxLocations) break;

            const nCitySlug = normalizeSlug(loc.slug);
            if (seenSlugs.has(nCitySlug)) {
                console.warn(`Collision detected: Slug ${nCitySlug} already processed this run. Check locations.json.`);
                summary.skipped_collisions.push(nCitySlug);
                continue;
            }
            seenSlugs.add(nCitySlug);
            if (nCitySlug !== loc.slug) {
                console.warn(`Normalized slug: ${loc.slug} -> ${nCitySlug}`);
            }

            const cityKeyword = `${loc.city}`;
            const hits = getKeywordHits(cityKeyword, kwMap);
            const minHits = CONFIG.assisted_min_keyword_hits || 0;

            if (CONFIG.mode !== 'manual' && hits < minHits) {
                console.log(`Skipping ${loc.city}: Low keyword hits (${hits}/${minHits})`);
                summary.skipped_low_intent.push(`${loc.city} (${hits}/${minHits})`);
                continue;
            }

            // Fetch environmental data once per city
            const weatherData = await weather.getWeatherData(loc.city, loc.state, CONFIG.google_maps_api_key);
            const pollenData = await pollen.getPollenData(null, null, CONFIG.google_maps_api_key);

            // 1. City main page: /locations/city/
            const cityUrl = `/locations/${nCitySlug}/`;
            let cityWasNew = false;

            if (totalPagesBuiltInRun < maxTotalPages) {
                console.log(`${DRY_RUN ? '[DRY RUN] Would build/update' : 'Processing'}: ${cityUrl}`);
                const locationString = `${loc.city}, ${loc.state}`;
                const targetDir = path.join(SITE_ROOT, 'locations', nCitySlug);
                await generateProLocationPage(targetDir, cityUrl, locationString, `${loc.city} Local HVAC Services`, locationString, loc, weatherData, pollenData);

                if (!existingUrls.has(cityUrl)) {
                    buildLog.builds.push({ url: cityUrl, type: 'location', timestamp: new Date().toISOString() });
                    newUrls.push(cityUrl);
                    summary.new_cities++;
                }

                totalPagesBuiltInRun++;
                locationsInRun++;
                cityWasNew = true;
            }

            // 2. City + Service pages: /locations/city/service/
            for (const svc of SERVICES) {
                if (totalPagesBuiltInRun >= maxTotalPages) break;
                if (newServicesCount >= maxServices) {
                    console.log(`Service threshold reached for ${loc.city}: ${maxServices} services max.`);
                    break;
                }

                const nSvcSlug = normalizeSlug(svc.slug);
                const cityServiceUrl = `/locations/${nCitySlug}/${nSvcSlug}/`;

                console.log(`${DRY_RUN ? '[DRY RUN] Would build/update' : 'Processing'}: ${cityServiceUrl}`);
                const locationString = `${loc.city}, ${loc.state}`;
                const targetDir = path.join(SITE_ROOT, 'locations', nCitySlug, nSvcSlug);
                await generateProLocationPage(targetDir, cityServiceUrl, `${svc.name} in ${locationString}`, `${svc.name} - ${loc.city}`, locationString, loc, weatherData, pollenData);

                if (!existingUrls.has(cityServiceUrl)) {
                    buildLog.builds.push({ url: cityServiceUrl, type: 'city-service', timestamp: new Date().toISOString() });
                    newUrls.push(cityServiceUrl);
                    summary.new_services++;
                }

                totalPagesBuiltInRun++;
                newServicesCount++;
                if (!cityWasNew) {
                    cityWasNew = true;
                    locationsInRun++;
                }
            }
        }

        if (newUrls.length > 0) {
            const sitemapContent = generateSitemap(buildLog.builds.map(b => b.url));

            if (!verifySitemapIntegrity(sitemapContent)) {
                throw new Error('Sitemap integrity mismatch.');
            }

            writeAtomic(BUILD_LOG_PATH, JSON.stringify(buildLog, null, 2));
            writeAtomic(SITEMAP_PATH, sitemapContent);
            writeAtomic(SITEMAP_HASH_PATH, getChecksum(sitemapContent));
            syncWithMasterIndex(SITE_ROOT, CONFIG.domain, 'sitemap-local.xml');

            // Sync Locations
            const locId = await syncToGoogleSheets(CONFIG, SITE_ROOT, "Locations");

            // Sync Services
            const svcId = await syncToGoogleSheets(CONFIG, SITE_ROOT, "Services");

            const finalId = locId || svcId;
            if (finalId && finalId !== CONFIG.google_sheet_id) {
                CONFIG.google_sheet_id = finalId;
                fs.writeFileSync(path.join(BASE_DIR, 'local-config.json'), JSON.stringify(CONFIG, null, 4));
                console.log(`[Local] Updated local-config.json with new Sheet ID: ${finalId}`);
            }
        }

        const summaryPath = path.join(BASE_DIR, 'logs', `run-summary-${summary.date}.json`);
        writeAtomic(summaryPath, JSON.stringify(summary, null, 2));
        console.log(`Run complete. Built ${newUrls.length} pages.`);

    } catch (err) {
        console.error('Build failed:', err.message);
        summary.errors.push(err.message);
    } finally {
        if (!DRY_RUN && fs.existsSync(LOCK_FILE)) {
            fs.unlinkSync(LOCK_FILE);
        }
    }
}

(async () => {
    await build();
})();
