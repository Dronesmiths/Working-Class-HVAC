const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { syncToGoogleSheets } = require('../google-sheets-sync');
const { syncWithMasterIndex } = require('../sitemap-utils');
const { getEnrichedContent } = require('../content-ai');

const BASE_DIR = __dirname;
const CONFIG = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'blog-config.json'), 'utf8'));
const PILLARS_PATH = path.join(BASE_DIR, '..', 'PILLARS.json');
const REGISTRY_PATH = path.join(BASE_DIR, '..', 'REGISTRY.json');
const TEMPLATE_PATH = path.join(BASE_DIR, '..', 'TEMPLATES', 'blog-base.html');
const SITE_ROOT = path.join(BASE_DIR, '..', '..', '..', '..');
const SITEMAP_PATH = path.join(SITE_ROOT, 'sitemap-blog.xml');
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

function getChecksum(content) {
    return crypto.createHash('md5').update(content).digest('hex');
}

function normalizeSlug(slug) {
    return slug.toLowerCase().trim().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

async function writePlaceholder(dir, url, title, pillar, isCornerstone) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    const filePath = path.join(dir, 'index.html');
    if (fs.existsSync(filePath)) return;

    let template = fs.readFileSync(TEMPLATE_PATH, 'utf8');

    let footerGuidance = '';
    if (isCornerstone) {
        const guidanceUrl = `/newsletter/${normalizeSlug(title)}-guidance/`;
        footerGuidance = `\n<div class="guidance-box">\n  <p>Need more practical guidance on this? <a href="${guidanceUrl}">Read our Client Newsletter for ${title}</a>.</p>\n</div>`;
    }

    const mapsApiConfig = {
        apiKey: CONFIG.google_maps_api_key,
        placeId: CONFIG.google_place_id,
        flags: CONFIG.maps_feature_flags || {},
        businessAddress: CONFIG.business_address || ""
    };

    const bodyContent = await getEnrichedContent(title, pillar, "Lancaster, CA", mapsApiConfig);

    template = template.replace(/{{title}}/g, title)
        .replace(/{{subtitle}}/g, `Expert insights on ${pillar}`)
        .replace(/{{canonical_url}}/g, `${CONFIG.domain}${url}`)
        .replace(/{{meta_description}}/g, `Read our latest guide on ${title} within the ${pillar} pillar.`)
        .replace(/{{content_blocks}}/g, `${bodyContent}${footerGuidance}`)
        .replace(/{{cta_label}}/g, 'Get a Free Quote')
        .replace(/{{cta_url}}/g, '/contact/')
        .replace(/{{container_class}}/g, 'container')
        .replace(/{{button_class}}/g, 'btn btn-primary')
        .replace(/{{hero_section_class}}/g, 'blog-hero')
        .replace(/{{content_class}}/g, 'blog-content')
        .replace(/{{wrapper_class}}/g, 'blog-footer-cta');

    writeAtomic(filePath, template);
}

function generateSitemap(urls) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
    urls.forEach(url => {
        xml += `  <url>\n    <loc>${CONFIG.domain}${url}</loc>\n    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>\n  </url>\n`;
    });
    xml += '</urlset>';
    return xml;
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
        if (ageInMinutes < (CONFIG.lock_ttl_minutes || 30)) {
            console.error('Error: Build lock active.');
            process.exit(1);
        }
    }
    if (!DRY_RUN) fs.writeFileSync(LOCK_FILE, Date.now().toString());

    try {
        const registry = JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8'));
        const pillars = JSON.parse(fs.readFileSync(PILLARS_PATH, 'utf8'));

        let newPostsCount = 0;
        const maxNew = CONFIG.max_new_posts_per_run || 5;

        // Simplified logic for template: Ensure all registry entries exist
        for (const page of registry.pages) {
            const nSlug = normalizeSlug(page.slug);
            const url = `${CONFIG.base_path}/${nSlug}/`;
            const dir = path.join(SITE_ROOT, 'blog', nSlug);

            if (!fs.existsSync(path.join(dir, 'index.html'))) {
                if (newPostsCount < maxNew) {
                    console.log(`${DRY_RUN ? '[DRY RUN] Would build' : 'Building'}: ${url}`);
                    const isCornerstone = page.type === 'cornerstone';
                    await writePlaceholder(dir, url, page.title, page.pillar, isCornerstone);
                    newPostsCount++;
                }
            }
        }

        // Generate Blog Sitemap
        const allUrls = registry.pages.map(p => `${CONFIG.base_path}/${normalizeSlug(p.slug)}/`);
        const sitemapContent = generateSitemap(allUrls);
        writeAtomic(SITEMAP_PATH, sitemapContent);
        writeAtomic(SITEMAP_HASH_PATH, getChecksum(sitemapContent));

        // Sync with Master Sitemap Index
        syncWithMasterIndex(SITE_ROOT, CONFIG.domain, 'sitemap-blog.xml');

        // Sync with Google Sheets
        const newId = await syncToGoogleSheets(CONFIG, SITE_ROOT, "Blogs");
        if (newId && newId !== CONFIG.google_sheet_id) {
            CONFIG.google_sheet_id = newId;
            fs.writeFileSync(path.join(BASE_DIR, 'blog-config.json'), JSON.stringify(CONFIG, null, 4));
            console.log(`[Blog] Updated blog-config.json with new Sheet ID: ${newId}`);
        }

        console.log(`Run complete. Processed ${newPostsCount} new posts.`);

    } catch (err) {
        console.error('Blog Build failed:', err.message);
    } finally {
        if (!DRY_RUN && fs.existsSync(LOCK_FILE)) fs.unlinkSync(LOCK_FILE);
    }
}

(async () => {
    await build();
})();
