import os
import sys
import argparse
import xml.etree.ElementTree as ET
import json
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import re

def get_slug(name):
    """Robust slugifier that handles non-breaking spaces and hidden whitespace."""
    if not name: return "-"
    return '-'.join(str(name).lower().split()).replace('_', '-')

# --- Configuration Loader ---
def load_config():
    """Loads site-specific configuration from config.json."""
    # The config is in the parent folder of 'core'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.json')
    if not os.path.exists(config_path):
        print(f"ERROR: config.json not found at {config_path}")
        sys.exit(1)
    with open(config_path, 'r') as f:
        return json.load(f)

CONFIG = load_config()
ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Resolve ROOT_DIR relative to ENGINE_ROOT
WEBSITE_REL_PATH = CONFIG.get('WEBSITE_DIR', '../website')
ROOT_DIR = os.path.abspath(os.path.join(ENGINE_ROOT, WEBSITE_REL_PATH))

SITEMAP_PATH = os.path.join(ROOT_DIR, CONFIG.get('SITEMAP_FILENAME', 'sitemap.xml'))
SPREADSHEET_ID = CONFIG.get('SPREADSHEET_ID')
SERVICE_ACCOUNT_FILE = os.path.join(ENGINE_ROOT, CONFIG.get('SERVICE_ACCOUNT_FILE', 'service-account.json'))
GSC_SITE_URL = CONFIG.get('GSC_SITE_URL')
DOMAIN = CONFIG.get('DOMAIN', 'https://example.com').rstrip('/')

SITEMAP_MAPPING = CONFIG.get('SITEMAP_MAPPING', {
    '📂 SERVICE PAGES': ['/services/', '/features/'],
    '✍️ BLOG ARTICLES': ['/blog/'],
    '📍 LOCATIONS': ['/locations/'],
    '🏗️ INDUSTRIES': ['/industries/'],
    'Funnel Pages': ['/pricing/', '/contact/', '/portfolio/'],
})

# Tab Definitions for Sync (Client-Friendly)
SEO_GROWTH_TABS = {
    '📖 CLIENT GUIDE': [['Section', 'Description', 'Value to You']],
    '📊 RESULTS DASHBOARD': [['Metric', 'Value', 'Goal', 'Status']],
    '🏥 WEBSITE WELLNESS': [['URL', 'Health Score', 'Meta Title', 'Meta Description', 'Status (Action Required)']],
    '🔑 CONTENT PERFORMANCE': [['Target Keyword', 'Difficulty', 'Current Rank', 'Target Page', 'Monthly Reach (Impressions)']],
    '🚀 GROWTH OPPORTUNITIES': [['New Topic', 'Buying Intent', 'Priority', 'Status']],
    '⚔️ COMPETITOR WATCH': [['Competitor', 'Website URL', 'Their Strength', 'Our Opportunity']],
    'Backlink_Audit': [['URL', 'External Backlinks', 'Internal Links', 'Authority Score', 'Status', 'Action']],
    '📂 SERVICE PAGES': [['URL', 'Last Modified', 'Status', 'Service Name', 'SEO Page Title']],
    '✍️ BLOG ARTICLES': [['URL', 'Last Modified', 'Status', 'Article Category', 'SEO Page Title']],
    'Sitemap Inventory': [['URL', 'Page Type', 'Parent Topic', 'Primary Keyword', 'Internal Links', 'Last Updated']],
    'Cornerstone_Map': [['Cornerstone', 'URL', 'Target Keyword', 'Ideal Supporting Pages', 'Current Supporting Pages', 'Missing Pages', 'Priority']],
    'Subpage_Plan': [['Parent Cornerstone', 'Subpage Topic', 'Page Type', 'Target Keyword', 'Status']],
    'Expansion_Engine': [['Cluster', 'Suggested Page', 'Target Keyword', 'Impressions', 'Opportunity Type']],
    'Reinforcement_Queue': [['URL', 'Action', 'Reason', 'Priority']],
    'Internal_Link_Queue': [['Source Page', 'Target Page', 'Suggested Anchor', 'Cluster', 'Reason']],
    'Authority_Radar': [['Cluster', 'Total Pages', 'Internal Links', 'External Backlinks', 'Total Impressions', 'Average Position', 'Gravity Score', 'Opportunity Score', 'Priority']],
    'Cluster_Map': [['Cluster', 'URL', 'Pages', 'Gravity Score', 'Opportunity Score', 'Priority', 'Recommended Action']]
}

# --- Data Registry Loader ---
def load_registry(name):
    """Loads default data lists from the registries folder."""
    registry_path = os.path.join(ENGINE_ROOT, 'core', 'registries', f"{name}.json")
    if os.path.exists(registry_path):
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load registry {name}: {e}")
    return []

CORNERSTONE_FILE = os.path.join(ENGINE_ROOT, 'core', 'registries', 'cornerstones.json')
CORNERSTONE_MAP_EXAMPLES = load_registry('cornerstones')
SUBPAGE_PLAN_EXAMPLES = load_registry('subpage_plan')
EXPANSION_ENGINE_EXAMPLES = load_registry('expansion_engine')
MARKET_INTEL_RAW = load_registry('market_intel')

# Standardize Market Intel format if it's a dict
MARKET_INTEL = MARKET_INTEL_RAW if isinstance(MARKET_INTEL_RAW, dict) else {
    '🚀 GROWTH OPPORTUNITIES': [],
    '⚔️ COMPETITOR WATCH': [],
    'Backlink_Audit': []
}

CLIENT_GUIDE_DATA = [
    ['DASHBOARD', 'A bird\'s-eye view of your total SEO success and growth progress.', 'Shows your ROI and overall site authority.'],
    ['WELLNESS', 'A technical "medical checkup" of your website pages.', 'Ensures Google can read your site perfectly.'],
    ['PERFORMANCE', 'Tracking exactly which keywords are driving people to your site.', 'Shows you what your customers are actually searching for.'],
    ['GROWTH', 'A roadmap of new content we should build to capture more traffic.', 'Plan for future customer acquisition.'],
    ['COMPETITORS', 'Monitoring who else is competing for your customers online.', 'Helps us stay one step ahead of the market.'],
    ['TRUST SIGNALS', 'Websites that are linking to you, which builds your authority.', 'The #1 factor for ranking higher on Google.']
]

# --- Core Logic ---

def get_ns():
    return {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

def categorize_url(url):
    for category, patterns in SITEMAP_MAPPING.items():
        for pattern in patterns:
            if pattern in url:
                return category
    return 'Page Health'

def get_sitemap_urls():
    if not os.path.exists(SITEMAP_PATH):
        return []
    tree = ET.parse(SITEMAP_PATH)
    root = tree.getroot()
    urls = []
    for url_tag in root.findall('ns:url', get_ns()):
        loc = url_tag.find('ns:loc', get_ns()).text
        lastmod = url_tag.find('ns:lastmod', get_ns()).text if url_tag.find('ns:lastmod', get_ns()) is not None else ''
        urls.append({'loc': loc, 'lastmod': lastmod})
    return urls

def cmd_sitemap():
    """Generates a fresh sitemap.xml by crawling the local directory."""
    print("Regenerating sitemap from local files...")
    domain = CONFIG.get('DOMAIN', 'https://aipilots.site')
    sitemap_path = os.path.join(ROOT_DIR, 'sitemap.xml')
    
    # Standard patterns to include or just recursive search
    import glob
    found_pages = []
    
    # Hero search for all index.html
    matches = glob.glob(os.path.join(ROOT_DIR, '**/index.html'), recursive=True)
    for m in matches:
        if 'node_modules' in m or '.git' in m: continue
        rel = os.path.relpath(m, ROOT_DIR)
        url_path = '/' + rel.replace('index.html', '')
        found_pages.append(url_path)
            
    # Deduplicate and build XML
    found_pages = sorted(list(set(found_pages)))
    
    # Use the same namespace logic as existing sitemap
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for p in found_pages:
        url_tag = ET.SubElement(root, "url")
        loc = ET.SubElement(url_tag, "loc")
        loc.text = f"{domain}{p}"
        lastmod = ET.SubElement(url_tag, "lastmod")
        lastmod.text = datetime.now().strftime('%Y-%m-%d')

    tree = ET.ElementTree(root)
    tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)
    print(f"SUCCESS: Updated sitemap with {len(found_pages)} pages.")

def update_sitemap(new_url):
    tree = ET.parse(SITEMAP_PATH)
    root = tree.getroot()
    
    # Check if exists
    for url_tag in root.findall('ns:url', get_ns()):
        if url_tag.find('ns:loc', get_ns()).text == new_url:
            print(f"URL {new_url} already in sitemap.")
            return

    url_tag = ET.SubElement(root, '{http://www.sitemaps.org/schemas/sitemap/0.9}url')
    loc_tag = ET.SubElement(url_tag, '{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    loc_tag.text = new_url
    lastmod_tag = ET.SubElement(url_tag, '{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
    lastmod_tag.text = datetime.now().strftime('%Y-%m-%d')
    
    # Prettify and save
    ET.indent(tree, space="  ", level=0)
    tree.write(SITEMAP_PATH, encoding='utf-8', xml_declaration=True)
    print(f"Updated sitemap.xml with {new_url}")

def analyze_page(url_path):
    """Analyzes a local HTML file for SEO health."""
    # Convert URL to local path
    rel_path = url_path.replace(DOMAIN, '').strip('/')
    if not rel_path:
        local_path = os.path.join(ROOT_DIR, 'index.html')
    else:
        local_path = os.path.join(ROOT_DIR, rel_path, 'index.html')

    if not os.path.exists(local_path):
        return None

    try:
        with open(local_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        title = soup.title.string if soup.title else ""
        meta_desc = ""
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            meta_desc = desc_tag.get('content', '')

        h1 = soup.find('h1')
        h1_text = h1.get_text().strip() if h1 else "MISSING"

        # Simple Health Scoring
        score = 100
        issues = []
        if not title or len(title) < 30: 
            score -= 20
            issues.append("Short/Missing Title")
        if not meta_desc or len(meta_desc) < 100:
            score -= 20
            issues.append("Short/Missing Desc")
        if h1_text == "MISSING":
            score -= 20
            issues.append("No H1")

        # Internal Link Collection
        internal_outbound = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Normalize and identify internal links
            if href.startswith('/') or DOMAIN in href:
                # Remove query params and fragments
                clean_href = href.split('?')[0].split('#')[0]
                if clean_href.startswith(DOMAIN):
                    clean_href = clean_href.replace(DOMAIN, '')
                if not clean_href.startswith('/'):
                    clean_href = '/' + clean_href
                internal_outbound.add(clean_href)

        return {
            'url': url_path,
            'title': title,
            'title_len': len(title),
            'desc_len': len(meta_desc),
            'h1': h1_text,
            'score': score,
            'status': "Healthy" if score > 70 else "Needs Improvement",
            'issues': ", ".join(issues),
            'outbound': list(internal_outbound),
            'strategic_links': len(re.findall(r'<li.*?>.*?</li>', str(soup.find('div', class_='seo-authority-block')), re.DOTALL)) if soup.find('div', class_='seo-authority-block') else 0
        }
    except Exception as e:
        print(f"Audit Error for {local_path}: {e}")
        return None

def get_gsc_data():
    """Fetches impression/click data from Search Console."""
    print("Fetching Search Console data...")
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
        service = build('searchconsole', 'v1', credentials=creds)
        
        request = {
            'startDate': '2025-01-01', # Using a broad range for demo/initial data
            'endDate': datetime.now().strftime('%Y-%m-%d'),
            'dimensions': ['query', 'page'],
            'rowLimit': 100
        }
        response = service.searchanalytics().query(siteUrl=GSC_SITE_URL, body=request).execute()
        return response.get('rows', [])
    except Exception as e:
        print(f"GSC Error: {e}")
        return []
def get_sheet_values(service, spreadsheet_id, range_name):
    """Helper to fetch values from a specific sheet range."""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    return result.get('values', [])

def calculate_cornerstone_gaps(service, spreadsheet_id, all_urls):
    """Analyzes Cornerstone_Map and Subpage_Plan against live sitemap."""
    cornerstone_rows = get_sheet_values(service, spreadsheet_id, "'Cornerstone_Map'!A2:F")
    subpage_rows = get_sheet_values(service, spreadsheet_id, "'Subpage_Plan'!A2:E")
    
    # 1. Map existing URLs to topics
    url_set = {u['loc'] for u in all_urls}
    
    # 2. Update Cornerstone Map
    updated_cornerstones = []
    for row in cornerstone_rows:
        if not row: continue
        name = row[0]
        ideal = int(row[2]) if len(row) > 2 and str(row[2]).isdigit() else 20
        # Check for matches in sitemap
        current = 0
        for loc in url_set:
            if f"/{name}/" in loc or f"-{name}/" in loc:
                current += 1
        
        missing = max(0, ideal - current)
        priority = row[5] if len(row) > 5 else 'Medium'
        updated_cornerstones.append([name, row[1] if len(row) > 1 else '', ideal, current, missing, priority])

    # 3. Update Subpage Plan Status
    updated_subpages = []
    for row in subpage_rows:
        if not row: continue
        parent = row[0]
        topic = row[1]
        slug = get_slug(topic)
        
        status = 'planned'
        # Check if topic slug exists in any live URL
        for loc in url_set:
            if slug in loc:
                status = 'exists'
                break
        
        updated_subpages.append([parent, topic, row[2] if len(row) > 2 else '', row[3] if len(row) > 3 else '', status])

    return updated_cornerstones, updated_subpages


def apply_formatting(service, spreadsheet_id, sheet_id, col_count, priority_colors=None):
    requests = [
        {
            'updateSheetProperties': {
                'properties': {'sheetId': sheet_id, 'gridProperties': {'frozenRowCount': 1}},
                'fields': 'gridProperties.frozenRowCount'
            }
        },
        {
            'autoResizeDimensions': {
                'dimensions': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': col_count}
            }
        },
        {
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 1.0},
                        'textFormat': {'bold': True}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }
    ]
    
    # Conditional Row Formatting for Cluster_Map
    if priority_colors:
        for i, prio in enumerate(priority_colors):
            color = {'red': 0.85, 'green': 0.92, 'blue': 0.83} if prio == "Dominant" else \
                    {'red': 1.0, 'green': 0.95, 'blue': 0.8} if prio == "Growth" else \
                    {'red': 0.96, 'green': 0.8, 'blue': 0.8} # Red for Expansion
            
            requests.append({
                'repeatCell': {
                    'range': {'sheetId': sheet_id, 'startRowIndex': i + 1, 'endRowIndex': i + 2},
                    'cell': {'userEnteredFormat': {'backgroundColor': color}},
                    'fields': 'userEnteredFormat(backgroundColor)'
                }
            })

    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': requests}).execute()

# --- Commands ---

def cmd_sync():
    print("Extracting current sitemap and auditing pages...")
    all_urls = get_sitemap_urls()
    audit_results = {}
    for u in all_urls:
        res = analyze_page(u['loc'])
        if res:
            audit_results[u['loc']] = res

    gsc_rows = get_gsc_data()
    
    urls_by_category = {cat: [] for cat in SEO_GROWTH_TABS.keys()}
    urls_by_category['📖 CLIENT GUIDE'] = CLIENT_GUIDE_DATA
    
    # Dashboard Aggregation
    total_pages = len(all_urls)
    total_audit = len(audit_results)
    avg_score = sum(r['score'] for r in audit_results.values()) / total_audit if total_audit > 0 else 0
    total_clicks = sum(r.get('clicks', 0) for r in gsc_rows)
    
    urls_by_category['📊 RESULTS DASHBOARD'] = [
        ['Metric', 'Current Value', 'Target Goal', 'Wellness Status'],
        ['Total Indexed Pages', total_pages, '100+', 'On Track' if total_pages > 50 else 'Lagging'],
        ['Website Health Score', f"{avg_score:.1f}%", '90%+', 'Excellent' if avg_score > 80 else 'Audit Required'],
        ['Monthly Search Traffic', int(total_clicks), '500+', 'Active'],
        ['Last Manual Sync', datetime.now().strftime('%Y-%m-%d %H:%M'), '-', 'Updated']
    ]

    for u in all_urls:
        loc, lastmod = u['loc'], u['lastmod']
        category = categorize_url(loc)
        audit = audit_results.get(loc, {})
        
        # Extraction of human-readable name from URL slug
        path_parts = loc.rstrip('/').split('/')
        readable_name = path_parts[-1].replace('-', ' ').title() if len(path_parts) > 3 else "Main Page"

        if category == '📂 SERVICE PAGES':
            urls_by_category[category].append([loc, lastmod, audit.get('status', 'Unknown'), readable_name, audit.get('title', '')])
        elif category == '✍️ BLOG ARTICLES':
            urls_by_category[category].append([loc, lastmod, audit.get('status', 'Unknown'), readable_name, audit.get('title', '')])
        elif category == '🏥 WEBSITE WELLNESS':
            urls_by_category[category].append([
                loc, 
                f"{audit.get('score', 0)}/100",
                audit.get('title', ''), 
                audit.get('issues', 'Healthy'), 
                audit.get('status', 'Unknown')
            ])
        elif category == 'Page Health': # Mapping generic to Wellness
             urls_by_category['🏥 WEBSITE WELLNESS'].append([
                loc, 
                f"{audit.get('score', 0)}/100",
                audit.get('title', ''), 
                audit.get('issues', 'Healthy'), 
                audit.get('status', 'Unknown')
            ])

    # Keyword Tracker from GSC
    kw_data = []
    for row in gsc_rows:
        query = row['keys'][0]
        page = row['keys'][1]
        kw_data.append([query, 'Growing', f"Pos: {row['position']:.1f}", page, int(row['impressions'])])
    urls_by_category['🔑 CONTENT PERFORMANCE'] = kw_data

    print("Authenticating with Google Sheets...")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=creds)

    # Pre-fetch existing Sitemap Inventory to preserve Clusters/Keywords
    print("Reading existing sitemap inventory...")
    try:
        existing_inventory = get_sheet_values(service, SPREADSHEET_ID, "'Sitemap Inventory'!A2:E")
    except Exception as e:
        print(f"Note: Could not read existing inventory (sheet may be new): {e}")
        existing_inventory = []
    inventory_map = {row[0]: (row[1], row[2], row[3]) for row in existing_inventory if len(row) >= 4}

    # Build a lookup map from the strategic roadmap
    roadmap_lookup = {get_slug(s[1]): s[0] for s in SUBPAGE_PLAN_EXAMPLES}

    # Populate Sitemap Inventory with merged data
    for u in all_urls:
        loc, lastmod = u['loc'], u['lastmod']
        category = categorize_url(loc)
        page_type = category.replace('📂 ', '').replace('✍️ ', '').split(' ')[0].rstrip('s')
        
        slug = loc.rstrip('/').split('/')[-1]
        roadmap_parent = roadmap_lookup.get(slug, '-')
        
        # Merge existing data if available
        existing = inventory_map.get(loc, (page_type, '-', '-'))
        
        # Priority: Roadmap > Existing Sheet > Path Fallback
        parent_topic = roadmap_parent if roadmap_parent != '-' else existing[1]
        
        if parent_topic == '-':
            if '/locations/' in loc: parent_topic = 'local-seo-av'
            elif '/industries/' in loc: parent_topic = 'website-build-roadmap'
            elif '/portfolio/' in loc: parent_topic = 'ai-authority-content'
            elif '/services/' in loc: parent_topic = 'managed-hosting'
            elif '/blog/' in loc: parent_topic = 'blog-general'
            elif '/website-care/' in loc: parent_topic = 'website-care'
            elif '/local-seo-av/' in loc: parent_topic = 'local-seo-av'
            elif '/nonprofit-digital/' in loc: parent_topic = 'nonprofit-digital'
            elif '/daycare-bundle/' in loc: parent_topic = 'daycare-bundle'
        
        strategic_count = audit.get('strategic_links', 0)
        urls_by_category['Sitemap Inventory'].append([loc, existing[0], parent_topic, existing[2], strategic_count, lastmod])

    # Market Intelligence Tabs (Previously curated, merge if not overlapping)
    for intel_tab, intel_data in MARKET_INTEL.items():
        if intel_tab in urls_by_category and not urls_by_category[intel_tab]:
            urls_by_category[intel_tab] = intel_data

    # 1.5 Backlink & Internal Link Audit Calculation

    # 1.5 Backlink & Internal Link Audit Calculation
    inverted_links = {}
    for url, res in audit_results.items():
        outbound = res.get('outbound', [])
        for link in outbound:
            # Normalize link to absolute URL for matching
            abs_link = link
            if abs_link.startswith('/'):
                abs_link = DOMAIN.rstrip('/') + abs_link
            
            if abs_link not in inverted_links:
                inverted_links[abs_link] = []
            inverted_links[abs_link].append(url)
    
    backlink_audit_rows = []
    for u in all_urls:
        url = u['loc']
        inbound_count = len(inverted_links.get(url, []))
        # Schema: URL, External Backlinks (Mocked for now), Internal Links, Authority Score, Status, Action
        score = min(inbound_count * 20, 100)
        status = "Healthy" if inbound_count >= 3 else "Under-linked"
        action = "-" if status == "Healthy" else "Build Internal Links"
        backlink_audit_rows.append([url, "0", inbound_count, score, status, action])
    
    urls_by_category['Backlink_Audit'] = backlink_audit_rows

    # Authority Radar Aggregation
    print("Calculating Authority Radar metrics...")
    radar_inventory = urls_by_category.get('Sitemap Inventory', [])
    try:
        radar_backlinks = get_sheet_values(service, SPREADSHEET_ID, "'Backlink_Audit'!A2:D")
    except Exception:
        radar_backlinks = []
    
    try:
        radar_performance = get_sheet_values(service, SPREADSHEET_ID, "'🔑 CONTENT PERFORMANCE'!A2:E")
    except Exception:
        radar_performance = []
    
    cluster_stats = {}
    for row in radar_inventory:
        if len(row) < 3: continue
        url, parent = row[0], row[2]
        if parent == '-': continue
        if parent not in cluster_stats:
            cluster_stats[parent] = {'pages': 0, 'internal': 0, 'external': 0, 'impressions': 0, 'positions': []}
        cluster_stats[parent]['pages'] += 1
        
        # Link to external backlinks from Backlink_Audit
        for bl in radar_backlinks:
            if len(bl) >= 4 and bl[0] == url:
                try: cluster_stats[parent]['external'] += int(bl[1]) if str(bl[1]).isdigit() else 0
                except: pass
                try: cluster_stats[parent]['internal'] += int(bl[2]) if str(bl[2]).isdigit() else 0
                except: pass
        
        # Link search performance
        for perf in radar_performance:
            if len(perf) >= 5 and perf[3] == url:
                try: cluster_stats[parent]['impressions'] += int(perf[4])
                except: pass
                try: 
                    pos_str = perf[2].replace('Pos: ', '')
                    cluster_stats[parent]['positions'].append(float(pos_str))
                except: pass

    # 2. Strategic Cornerstone & Expansion Analysis
    print("Performing unified strategic gap analysis...")
    try:
        cornerstone_data = get_sheet_values(service, SPREADSHEET_ID, "'Cornerstone_Map'!A2:D")
    except Exception:
        cornerstone_data = []
    
    # Merge seed data with sheet data with slug-normalization to prevent duplicates
    # Master Schema: [Cornerstone, URL, Target Keyword, Ideal, Current, Missing, Priority]
    all_cornerstones = {}
    for row in CORNERSTONE_MAP_EXAMPLES:
        slug = get_slug(row[0])
        all_cornerstones[slug] = [slug] + row[1:] # Force slug as Col A

    for row in cornerstone_data:
        if not row: continue
        slug = get_slug(row[0])
        if slug not in all_cornerstones:
            all_cornerstones[slug] = [slug, '-', '-', '15', '0', '15', 'High']
        
        # Schema Detection: If row[1] is a URL, it's the NEW schema
        is_new_schema = len(row) > 1 and (str(row[1]).startswith('http') or str(row[1]) == '-')
        
        if is_new_schema:
            # New Schema: [Slug, URL, Keyword, Ideal]
            if len(row) > 1: all_cornerstones[slug][1] = row[1]
            if len(row) > 2: all_cornerstones[slug][2] = row[2]
            if len(row) > 3: all_cornerstones[slug][3] = row[3]
        else:
            # Old Schema: [Slug, Keyword, Ideal]
            # row[1] was the keyword, row[2] was the ideal count
            if len(row) > 1: all_cornerstones[slug][2] = row[1] 
            if len(row) > 2: all_cornerstones[slug][3] = row[2]
        
        all_cornerstones[slug][0] = slug # FORCE 100% slug consistency

    updated_cornerstones = []
    expansion_suggestions = []
    total_expansion_count = 0
    
    sitemap_locs = [u['loc'] for u in all_urls]
    for topic, row in all_cornerstones.items():
        # Find the hub page for this cornerstone
        hub_url = '-'
        for loc in sitemap_locs:
            # Check for exact slug in path or filename
            if f"/{topic}/" in loc or loc.endswith(f"/{topic}") or loc.endswith(f"/{topic}.html"):
                hub_url = loc
                break
        
        # If not found via exact match, check for partial match in features or service pages
        if hub_url == '-':
            for loc in sitemap_locs:
                if topic in loc and ('/features/' in loc or '/services/' in loc):
                    hub_url = loc
                    break

        keyword = row[2] if len(row) > 2 else topic
        ideal_str = row[3] if len(row) > 3 else "15"
        try:
            ideal = int(ideal_str)
            current = cluster_stats.get(topic, {}).get('pages', 0)
            missing = ideal - current
            
            # Simple priority based on strategic importance + gap size
            is_new_service = any(k in topic for k in ['hosting', 'seo', 'nonprofit', 'automation', 'authority', 'strategy', 'roadmap'])
            priority = row[6] if len(row) > 6 else ("High" if (missing > 5 or is_new_service) else "Medium" if missing > 0 else "Low")
            
            updated_cornerstones.append([topic, hub_url, keyword, ideal, current, max(0, missing), priority])
            
            # Populate Expansion_Engine (Gap Analysis)
            if missing > 0 and total_expansion_count < 20:
                # 1. Filter SUBPAGE_PLAN_EXAMPLES for this cluster
                planned_for_cluster = [s for s in SUBPAGE_PLAN_EXAMPLES if s[0] == topic]
                
                # 2. Find pages that don't exist yet
                existing_slugs = [get_slug(loc) for loc in sitemap_locs]
                potential_additions = []
                for s in planned_for_cluster:
                    # s[1] is the suggested page title, s[2] is type, s[3] is target keyword
                    slug = get_slug(s[1])
                    if slug not in existing_slugs:
                        potential_additions.append([topic, s[1], s[3], "N/A (Gap Analysis)", "cluster growth"])
                
                # 3. Add descriptive suggestions
                pages_to_add = min(missing, len(potential_additions))
                for i in range(pages_to_add):
                    if total_expansion_count >= 20: break
                    expansion_suggestions.append(potential_additions[i])
                    total_expansion_count += 1
                
                # 4. Fallback if no specific planned pages are left but gap remains
                remaining_gap = missing - pages_to_add
                if remaining_gap > 0 and total_expansion_count < 20:
                    fallbacks = [
                        "2026 Strategy Guide", "Advanced Implementation", "Professional Checklist",
                        "Performance Optimization", "Future Trends & Insights", "Market Analysis",
                        "Case Study & Success Guide", "Common Pitfalls to Avoid"
                    ]
                    for i in range(min(len(fallbacks), remaining_gap)):
                        if total_expansion_count >= 20: break
                        prefix = fallbacks[i]
                        fallback_title = f"{keyword} {prefix}" if keyword != topic else f"{topic} {prefix}"
                        expansion_suggestions.append([topic, fallback_title, f"{keyword} focus", "N/A (Gap Analysis)", "cluster growth"])
                        total_expansion_count += 1
        except: continue

    urls_by_category['Cornerstone_Map'] = updated_cornerstones
    urls_by_category['Expansion_Engine'] = expansion_suggestions

    # 3. Authority Radar & Visual Cluster Map
    radar_rows = []
    # Use the combined list of all discovered clusters + strategic cornerstones
    active_clusters = set(cluster_stats.keys()).union(set(all_cornerstones.keys()))
    
    for cluster in active_clusters:
        s = cluster_stats.get(cluster, {'pages': 0, 'internal': 0, 'external': 0, 'impressions': 0, 'positions': []})
        avg_pos = sum(s['positions']) / len(s['positions']) if s['positions'] else 0
        gravity_score = (s['pages'] * 2) + (s['internal'] * 1.5) + (s['external'] * 4) + (s['impressions'] / 40)
        opportunity_score = s['impressions'] / s['pages'] if s['pages'] > 0 else 0
        priority = "Dominant" if gravity_score > 80 else "Growth" if gravity_score > 40 else "Expansion Needed"
        
        radar_rows.append([
            cluster, s['pages'], s['internal'], s['external'], s['impressions'], 
            f"{avg_pos:.1f}" if avg_pos > 0 else "-", round(gravity_score, 1), 
            round(opportunity_score, 1), priority
        ])

    radar_rows.sort(key=lambda x: x[6], reverse=True)
    urls_by_category['Authority_Radar'] = radar_rows
    
    # 3. Create Cluster_Map (Visual Summary)
    # Expected: Cluster, URL, Pages, Gravity, Opportunity, Priority, Action
    cluster_map_data = []
    # Use updated_cornerstones for the base, and merge with radar stats
    # updated_cornerstones is urls_by_category['Cornerstone_Map']
    # updated_radar is radar_rows (urls_by_category['Authority_Radar'])
    
    for row in urls_by_category['Cornerstone_Map']: # Use updated_cornerstones
        # row: [topic, hub_url, keyword, ideal, current, missing, priority]
        topic = row[0]
        hub_url = row[1]
        priority_from_cornerstone = row[6] # This is the strategic priority
        
        # Get stats from radar if available
        stats = {}
        for r_row in radar_rows: # Use radar_rows (which is updated_radar)
            if r_row[0] == topic:
                stats = {
                    'pages': r_row[1],
                    'gravity': r_row[6],
                    'opportunity': r_row[7],
                    'radar_priority': r_row[8] # Priority from radar calculation
                }
                break
        
        # Default stats if not found in radar (e.g., new cornerstones)
        if not stats:
            stats = {'pages': row[4], 'gravity': 0.0, 'opportunity': 0.0, 'radar_priority': 'Expansion Needed'}
            
        # Determine the final priority and action based on both strategic and radar analysis
        final_priority = stats['radar_priority'] # Default to radar's priority
        if priority_from_cornerstone == "High" and stats['radar_priority'] == "Expansion Needed":
            final_priority = "Growth" # Strategic override for new/important clusters
        elif priority_from_cornerstone == "High" and stats['radar_priority'] == "Growth":
            final_priority = "Dominant" # Push growth clusters if strategically high
            
        action = "Reinforce" if final_priority == "Dominant" else "Expand" if final_priority == "Growth" else "Build Cluster"
        
        cluster_map_data.append([topic, hub_url, stats['pages'], stats['gravity'], stats['opportunity'], final_priority, action])
    
    urls_by_category['Cluster_Map'] = cluster_map_data

    # 1. Cleanup: Remove duplicate/unused tabs
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    existing_sheets = spreadsheet.get('sheets', [])
    
    whitelist = list(SEO_GROWTH_TABS.keys())
    delete_requests = []
    
    for s in existing_sheets:
        title = s['properties']['title']
        sheet_id = s['properties']['sheetId']
        if title not in whitelist:
            print(f"Cleanup: Removing redundant tab '{title}'")
            delete_requests.append({'deleteSheet': {'sheetId': sheet_id}})
    
    if delete_requests:
        # We must ensure at least one sheet exists before deleting others
        # (Though in our case, we'll be adding the missing whitelist sheets next)
        try:
            service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': delete_requests}).execute()
        except Exception as e:
            print(f"Cleanup Error (likely tried to delete last sheet): {e}")

    # 2. Add missing tabs
    existing_titles = [s['properties']['title'] for s in service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute().get('sheets', [])]
    add_requests = []
    for category in whitelist:
        if category not in existing_titles:
            add_requests.append({'addSheet': {'properties': {'title': category}}})
    
    if add_requests:
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': add_requests}).execute()

    # 3. Subpage Strategy & Roadmap Seeding
    print("Seeding subpage roadmap...")
    try:
        subpage_data = get_sheet_values(service, SPREADSHEET_ID, "'Subpage_Plan'!A2:E")
    except Exception:
        subpage_data = []
    
    all_subpages = {}
    # Load examples first
    for row in SUBPAGE_PLAN_EXAMPLES:
        parent = get_slug(row[0])
        topic = str(row[1]).strip()
        all_subpages[(parent, topic)] = row

    for row in subpage_data:
        if not row: continue
        parent = get_slug(row[0])
        topic = str(row[1]).strip()
        all_subpages[(parent, topic)] = row
        # Ensure row starts with slug
        all_subpages[(parent, topic)][0] = parent
        
    updated_subpages = []
    sitemap_locs = {u['loc'] for u in all_urls}
    
    for key, row in all_subpages.items():
        parent, topic = row[0], row[1]
        slug = get_slug(topic)
        
        status = row[4] if len(row) > 4 else 'planned'
        # Check if actually live
        for loc in sitemap_locs:
            if slug in loc:
                status = 'exists'
                break
        
        updated_subpages.append([parent, topic, row[2] if len(row) > 2 else 'blog', row[3] if len(row) > 3 else topic, status])

    urls_by_category['Subpage_Plan'] = updated_subpages

    # 4. Update tabs with fresh data and apply formatting
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_meta = {s['properties']['title']: s['properties']['sheetId'] for s in spreadsheet.get('sheets', [])}

    for category, values in urls_by_category.items():
        if not values and category not in MARKET_INTEL: continue
        
        # Determine priority colors for Cluster_Map formatting
        p_colors = None
        if category == 'Cluster_Map':
            p_colors = [row[4] for row in values]

        headers = SEO_GROWTH_TABS[category]
        data = headers + values
        range_name = f"'{category}'!A1"
        
        # Clear and update (Clear columns A to Z to remove old corrupted data)
        service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range=f"'{category}'!A:Z").execute()
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=range_name,
            valueInputOption='RAW', body={'values': data}).execute()
        
        apply_formatting(service, SPREADSHEET_ID, sheet_meta[category], len(headers[0]), priority_colors=p_colors)
        
        # Custom Conditional Formatting for Sitemap Inventory Link Floor
        if category == 'Sitemap Inventory':
            last_row = len(data)
            format_req = [{
                'addConditionalFormatRule': {
                    'rule': {
                        'ranges': [{'sheetId': sheet_meta[category], 'startRowIndex': 1, 'endRowIndex': last_row, 'startColumnIndex': 4, 'endColumnIndex': 5}],
                        'booleanRule': {
                            'condition': {'type': 'NUMBER_LESS', 'values': [{'userEnteredValue': '3'}]},
                            'format': {'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.8}} # Red
                        }
                    },
                    'index': 0
                }
            }, {
                'addConditionalFormatRule': {
                    'rule': {
                        'ranges': [{'sheetId': sheet_meta[category], 'startRowIndex': 1, 'endRowIndex': last_row, 'startColumnIndex': 4, 'endColumnIndex': 5}],
                        'booleanRule': {
                            'condition': {'type': 'NUMBER_GREATER', 'values': [{'userEnteredValue': '2'}]},
                            'format': {'backgroundColor': {'red': 0.8, 'green': 1.0, 'blue': 0.8}} # Green
                        }
                    },
                    'index': 1
                }
            }]
            try:
                service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': format_req}).execute()
            except Exception as e:
                print(f"Warning: Could not apply link floor formatting: {e}")

        time.sleep(2) # Prevent Google Sheets API Quota Error

    # 6. Global Dashboard Intelligence Export
    export_dashboard_json(urls_by_category)
    print("Full SEO Factory Cycle Complete.")
    return service

def export_dashboard_json(data_by_tab):
    """Exports SEO intelligence to a structured JSON file for dashboards and AI."""
    print("Exporting dashboard data to JSON...")
    
    # Ensure data directory exists
    data_dir = os.path.join(ROOT_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)

    dashboard = {
        "site": {
            "total_pages": len(data_by_tab.get('Sitemap Inventory', [])),
            "clusters": len(data_by_tab.get('Cluster_Map', [])),
            "last_sync": datetime.now().isoformat()
        },
        "clusters": [],
        "opportunities": [],
        "reinforcement_tasks": []
    }

    # Map Clusters
    for row in data_by_tab.get('Cluster_Map', []):
        # Cluster, URL, Pages, Gravity Score, Opportunity Score, Priority, Recommended Action
        dashboard['clusters'].append({
            "name": row[0],
            "url": row[1],
            "pages": row[2],
            "gravity": row[3],
            "opportunity": row[4],
            "status": row[5],
            "recommended_action": row[6]
        })

    # Map Opportunities
    for row in data_by_tab.get('Expansion_Engine', []):
        # Cluster, Suggested Page, Target Keyword, Impressions, Opportunity Type
        dashboard['opportunities'].append(row[2]) # Target Keyword

    # Map Reinforcement Tasks
    for row in data_by_tab.get('Reinforcement_Queue', []):
        # URL, Action, Reason, Priority
        dashboard['reinforcement_tasks'].append(row[0]) # URL

    export_path = os.path.join(data_dir, 'seo_dashboard.json')
    with open(export_path, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"Dashboard intelligence exported to {export_path}")
    print("SYNC COMPLETE")

def cmd_autopilot():
    """Runs the full SEO growth loop in sequence."""
    print("STARTING SEO AUTOPILOT...")
    service = cmd_sync() # Sync returns the service object now
    print("SYNC COMPLETE")
    cmd_discover(service_instance=service)
    print("DISCOVERY COMPLETE")
    cmd_reinforce(service_instance=service)
    print("REINFORCEMENT COMPLETE")
    cmd_internal(service_instance=service)
    print("INTERNAL LINKING COMPLETE")
    print("AUTOPILOT RUN FINISHED")

def cmd_reinforce(service_instance=None):
    """Identifies search opportunities and queues reinforcement tasks."""
    print("Starting SEO Reinforcement analysis...")
    if not service_instance:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        service = build('sheets', 'v4', credentials=creds)
    else:
        service = service_instance

    # 1. Read Performance and Inventory data
    perf_data = get_sheet_values(service, SPREADSHEET_ID, "'🔑 CONTENT PERFORMANCE'!A2:E")
    inventory = get_sheet_values(service, SPREADSHEET_ID, "'Sitemap Inventory'!A2:E")
    
    opportunities = []
    for row in perf_data:
        if len(row) < 5: continue
        url = row[3]  # Target Page column in CONTENT PERFORMANCE
        try:
            impressions = int(row[4])
            # Based on user instruction: Impressions > 50, Clicks < 10
            # For now, we assume Clicks < 10 if we're identifying these as opportunities
            if impressions > 50:
                opportunities.append({'url': url, 'impressions': impressions})
        except: continue

    if not opportunities:
        print("No reinforcement opportunities found based on current sheet data.")
        return

    # 2. Analyze Internal Linking from Inventory
    tasks = []
    for opp in opportunities[:10]: # Limit to 10
        url = opp['url']
        path_parts = url.rstrip('/').split('/')
        topic = path_parts[3] if len(path_parts) > 3 else "main"
        
        # Possible actions
        actions = ["expand content", "add FAQ section", "improve headings", "add internal links", "add schema", "update meta description"]
        action = actions[opportunities.index(opp) % len(actions)]
        
        reason = f"High Impressions ({opp['impressions']}) with low engagement."
        
        # Internal linking check
        related = []
        for inv in inventory:
            if inv[0] != url and inv[2] == topic:
                related.append(inv[0])
        
        if related:
            link_note = f" Link from: {', '.join(related[:2])}"
            reason += link_note

        tasks.append([url, action, reason, 'High'])

    # 3. Update Reinforcement_Queue tab
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_meta = {s['properties']['title']: s['properties']['sheetId'] for s in spreadsheet.get('sheets', [])}
    
    if 'Reinforcement_Queue' not in sheet_meta:
        # Add tab if missing
        add_req = [{'addSheet': {'properties': {'title': 'Reinforcement_Queue'}}}]
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': add_req}).execute()
        # Re-fetch meta
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_meta = {s['properties']['title']: s['properties']['sheetId'] for s in spreadsheet.get('sheets', [])}

    headers = SEO_GROWTH_TABS['Reinforcement_Queue']
    values = headers + tasks
    range_name = "'Reinforcement_Queue'!A1"
    service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=range_name,
        valueInputOption='RAW', body={'values': values}).execute()

    apply_formatting(service, SPREADSHEET_ID, sheet_meta['Reinforcement_Queue'], len(headers[0]))

    print(f"\n--- Reinforcement Summary ---")
    print(f"Pages analyzed: {len(opportunities)}")
    print(f"Reinforcement tasks created: {len(tasks)}")
    print(f"Internal link opportunities found: {sum(1 for t in tasks if 'Link from' in t[2])}")
    print(f"Check the 'Reinforcement_Queue' tab for details.")
    print("REINFORCEMENT COMPLETE")

def _generate_page(name, type, dry_run=False):
    """Internal helper to generate a single page without triggering a full sync."""
    slug = get_slug(name)
    
    # 1. Conflict Check (Slugs)
    get_sitemap_urls_data = get_sitemap_urls()
    existing_urls = [u['loc'].rstrip('/') for u in get_sitemap_urls_data]
    
    # Check if the name/slug exists ANYWHERE in the current sitemap to prevent "Idea" conflicts
    for url in existing_urls:
        url_parts = url.replace('https://swapp.church', '').strip('/').split('/')
        if slug in url_parts:
            # If it already exists, skipping is safer than erroring in a batch run
            return None, f"SKIPPED: '{slug}' already exists in sitemap."

    new_url = f"{DOMAIN}"
    if type == 'location':
        target_dir = os.path.join(ROOT_DIR, 'locations', slug)
        new_url += f"/locations/{slug}/"
    elif type == 'service':
        target_dir = os.path.join(ROOT_DIR, 'features', slug)
        new_url += f"/features/{slug}/"
    elif type == 'blog':
        target_dir = os.path.join(ROOT_DIR, 'blog', slug)
        new_url += f"/blog/{slug}/"
    else:
        return None, f"ERROR: Unknown type '{type}'"

    if os.path.exists(target_dir):
        return None, f"SKIPPED: Directory already exists for '{slug}'."

    # 2. Template Selection (From Engine's Internal Templates Folder)
    template_path = os.path.join(ENGINE_ROOT, 'core', 'templates', f"{type}.html")
    if type == 'blog' and not os.path.exists(template_path):
        template_path = os.path.join(ENGINE_ROOT, 'core', 'templates', 'blog.html')

    if not os.path.exists(template_path):
        return None, f"ERROR: Template not found at {template_path}"

    with open(template_path, 'r') as f:
        content = f.read()

    # 3. Fill Template
    if type == 'location':
        content = content.replace('{{LOCATION}}', name).replace('{{SLUG}}', slug)
    else:
        # Check if name is in SUBPAGE_PLAN_EXAMPLES to get better context
        topic_info = next((s for s in SUBPAGE_PLAN_EXAMPLES if s[1].lower() == name.lower()), None)
        description = f"Learn more about AI Pilots' {name} solution for modern businesses."
        subtitle = f"The ultimate {name} for modern digital growth."
        
        if topic_info:
            target_keyword = topic_info[3]
            description = f"Discover how AI Pilots' {name} elevates your brand with advanced {target_keyword} capabilities."
            subtitle = f"Professional {name} built for business growth."

        content = content.replace('{{TITLE}}', name.title())
        content = content.replace('{{SLUG}}', slug)
        content = content.replace('{{DESCRIPTION}}', description)
        content = content.replace('{{SUBTITLE}}', subtitle)
        content = content.replace('{{CONTENT}}', f"<p>AI Pilots' {name} is a mission-critical tool designed to help your business scale by automating repetitive tasks and deepening customer engagement.</p>")

    # 4. Write File
    if dry_run:
        return new_url, "[DRY RUN] Success"
    else:
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, 'index.html'), 'w') as f:
            f.write(content)
        update_sitemap(new_url)
        return new_url, "CREATED"

def cmd_generate(args):
    """CLI wrapper for single page generation."""
    new_url, result = _generate_page(args.name, args.type, args.dry_run)
    print(f"{result}: {new_url if new_url else ''}")
    if result == "CREATED" and not args.dry_run:
        print("Triggering Google Sheet sync...")
        cmd_sync()
    print("GENERATE COMPLETE")

def cmd_produce_subpages():
    """Mass generates all 150+ planned subpages from SUBPAGE_PLAN_EXAMPLES."""
    print(f"🚀 Mass Materializing {len(SUBPAGE_PLAN_EXAMPLES)} Strategic Subpages...")
    created_count = 0
    skipped_count = 0
    
    for i, s in enumerate(SUBPAGE_PLAN_EXAMPLES):
        hub_name, topic_name, topic_type, topic_keyword, status = s
        print(f"[{i+1}/{len(SUBPAGE_PLAN_EXAMPLES)}] Processing: {topic_name} ({topic_type})...", end=" ", flush=True)
        
        new_url, result = _generate_page(topic_name, topic_type)
        if result == "CREATED":
            print("✅ CREATED")
            created_count += 1
        else:
            print(f"🟡 {result}")
            skipped_count += 1
            
    print(f"\n--- Mass Generation Summary ---")
    print(f"Total Processed: {len(SUBPAGE_PLAN_EXAMPLES)}")
    print(f"Newly Created: {created_count}")
    print(f"Skipped/Existing: {skipped_count}")
    
    if created_count > 0:
        print("\nTriggering final sync to index the new strategic network...")
        cmd_sync()
    print("PRODUCE SUBPAGES COMPLETE")

def cmd_discover(service_instance=None):
    """Identifies new keyword opportunities from Google Search Console data."""
    print("Starting SEO discovery process...")
    if not service_instance:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        service = build('sheets', 'v4', credentials=creds)
    else:
        service = service_instance

    # 1. Fetch GSC Data and Sitemap Inventory
    gsc_data = get_gsc_data() # Queries > 50 impressions
    inventory = get_sheet_values(service, SPREADSHEET_ID, "'Sitemap Inventory'!A2:C")
    existing_urls = {row[0] for row in inventory if len(row) > 0}
    
    # Map topics to clusters for discovery
    cluster_map = {row[0]: row[2] for row in inventory if len(row) >= 3}

    # 2. Identify queries with High Impressions but no page
    new_opportunities = []
    seen_queries = set()
    
    for row in gsc_data:
        # Expected structure: {'keys': ['query', 'page'], 'impressions': 100, ...}
        if 'keys' not in row or len(row['keys']) == 0: continue
        query = row['keys'][0]
        impressions = row.get('impressions', 0)
        
        if impressions > 50:
            # Basic query-to-topic heuristic
            is_existing = False
            for url in existing_urls:
                slug = url.rstrip('/').split('/')[-1].replace('-', ' ')
                if query in slug or slug in query:
                    is_existing = True
                    break
            
            if not is_existing and query not in seen_queries:
                # Find matching cluster
                cluster = "General"
                for keyword, topic in cluster_map.items():
                    if topic in query:
                        cluster = topic
                        break
                
                new_opportunities.append([
                    cluster,
                    get_slug(query),
                    query,
                    impressions,
                    "new demand"
                ])
                seen_queries.add(query)
                if len(new_opportunities) >= 20: break

    if not new_opportunities:
        print("No new discovery opportunities found.")
        return

    # 3. Update Expansion_Engine tab
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_meta = {s['properties']['title']: s['properties']['sheetId'] for s in spreadsheet.get('sheets', [])}
    
    if 'Expansion_Engine' not in sheet_meta:
        add_req = [{'addSheet': {'properties': {'title': 'Expansion_Engine'}}}]
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': add_req}).execute()
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_meta = {s['properties']['title']: s['properties']['sheetId'] for s in spreadsheet.get('sheets', [])}

    headers = SEO_GROWTH_TABS['Expansion_Engine']
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range="'Expansion_Engine'!A1",
        valueInputOption='RAW', body={'values': headers + new_opportunities}).execute()

    apply_formatting(service, SPREADSHEET_ID, sheet_meta['Expansion_Engine'], len(headers[0]))

    print(f"Discovery complete. Added {len(new_opportunities)} opportunities to Expansion_Engine.")
    print("DISCOVERY COMPLETE")

def cmd_internal(service_instance=None):
    """Optimizes internal linking between related pages within topic clusters."""
    print("Starting Strategic Internal Link Analysis...")
    if not service_instance:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        service = build('sheets', 'v4', credentials=creds)
    else:
        service = service_instance

    # 1. Read Data
    inventory = get_sheet_values(service, SPREADSHEET_ID, "'Sitemap Inventory'!A2:C")
    backlink_data = get_sheet_values(service, SPREADSHEET_ID, "'Backlink_Audit'!A2:C")
    
    # Load Cornerstones for pillar prioritization
    pill_data = []
    if os.path.exists(CORNERSTONE_FILE):
        with open(CORNERSTONE_FILE, 'r') as f:
            pill_data = json.load(f)
    
    # Map normalized slug to keyword
    pillar_map = {}
    for row in pill_data:
        if not row: continue
        topic_slug_map = {
            'website maintenance and care': 'website-care',
            'local seo antelope valley': 'local-seo-av',
            'nonprofit digital solutions': 'nonprofit-digital',
            'website build roadmap': 'website-build-roadmap',
            'ai authority content strategy': 'ai-authority-content',
            'daycare marketing bundle': 'daycare-bundle',
            'social media marketing': 'social-media-marketing',
            'managed hosting for business': 'managed-hosting'
        }
        slug = topic_slug_map.get(row[0].lower(), get_slug(row[0]))
        pillar_map[slug] = row[2]

    # 2. Group pages by Parent Topic
    clusters = {}
    for row in inventory:
        if len(row) < 3: continue
        url, page_type, parent_topic = row[0], row[1], row[2]
        
        # NORMALIZATION: Map readable topic names to slugs for matching
        topic_slug_map = {
            'website maintenance and care': 'website-care',
            'local seo antelope valley': 'local-seo-av',
            'nonprofit digital solutions': 'nonprofit-digital',
            'website build roadmap': 'website-build-roadmap',
            'ai authority content strategy': 'ai-authority-content',
            'daycare marketing bundle': 'daycare-bundle',
            'social media marketing': 'social-media-marketing',
            'managed hosting for business': 'managed-hosting'
        }
        topic_normalized = topic_slug_map.get(parent_topic.lower(), parent_topic)

        if topic_normalized not in clusters:
            clusters[topic_normalized] = []
        clusters[topic_normalized].append({'url': url, 'type': page_type})

    # 3. Strategic Opportunity Identification
    opportunities = []
    
    # A. Hub & Spoke: Ensure every subpage links to its Pillar
    for topic, pages in clusters.items():
        if topic in pillar_map:
            # Find the pillar URL
            pillar_url = None
            for p in pages:
                # Check if it's the exact pillar slug
                if p['url'].rstrip('/').split('/')[-1] == topic:
                    pillar_url = p['url']
                    break
            
            if pillar_url:
                keyword = pillar_map[topic]
                for p in pages:
                    if p['url'] != pillar_url:
                        opportunities.append([
                            p['url'], pillar_url, keyword.title(), topic, 
                            f"Pillar Support: Link to '{topic}' cornerstone"
                        ])

    # B. Cluster Density: Ensure low-authority subpages get support
    under_linked = []
    for row in backlink_data:
        if len(row) < 3: continue
        url = row[0]
        try:
            icount = int(row[2]) if str(row[2]).isdigit() else 0
            if icount < 3: under_linked.append(url)
        except: continue

    # C. Authority Floor Enforcement (Global Fallbacks)
    GLOBAL_AUTHORITY_HUBS = [
        {'url': f"{DOMAIN}/services/", 'anchor': 'Professional AI Services'},
        {'url': f"{DOMAIN}/pricing/", 'anchor': 'View Pricing & Plans'},
        {'url': f"{DOMAIN}/blog/local-seo-av/", 'anchor': 'Antelope Valley Local SEO Hub'}
    ]

    # Map existing opportunities to count links per source
    links_per_source = {}
    for opp in opportunities:
        src = opp[0]
        links_per_source[src] = links_per_source.get(src, 0) + 1

    # Ensure every page in the inventory has at least 3 links
    for row in inventory:
        if len(row) < 1: continue
        source_url = row[0]
        current_links = links_per_source.get(source_url, 0)
        
        if current_links < 3:
            # Need more links to hit authority floor
            needed = 3 - current_links
            for i in range(needed):
                # Pull from global hubs, prioritizing variety
                hub = GLOBAL_AUTHORITY_HUBS[i % len(GLOBAL_AUTHORITY_HUBS)]
                if hub['url'] == source_url: continue # Don't link to self
                
                opportunities.append([
                    source_url, hub['url'], hub['anchor'], "Global Authority",
                    f"Authority Floor: Mandating min 3 links for crawlability"
                ])
                current_links += 1
                if current_links >= 3: break

    # 4. Update Internal_Link_Queue tab
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_meta = {s['properties']['title']: s['properties']['sheetId'] for s in spreadsheet.get('sheets', [])}
    
    if 'Internal_Link_Queue' not in sheet_meta:
        add_req = [{'addSheet': {'properties': {'title': 'Internal_Link_Queue'}}}]
        service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': add_req}).execute()
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_meta = {s['properties']['title']: s['properties']['sheetId'] for s in spreadsheet.get('sheets', [])}

    headers = SEO_GROWTH_TABS['Internal_Link_Queue']
    # Filter to avoid too many links at once (increased to 1500 for full coverage)
    final_values = headers + opportunities[:1500]
    
    print(f"Syncing {len(final_values) - 1} strategic links to 'Internal_Link_Queue'...")
    # Trace specific urls if found
    for r in final_values:
        if 'website-care' in r[0] or 'website-care' in r[1]:
            print(f"  [CLUSTER-TRACE] {r[0]} -> {r[1]} ({r[2]})")

    range_name = "'Internal_Link_Queue'!A1"
    service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=range_name,
        valueInputOption='RAW', body={'values': final_values}).execute()

    apply_formatting(service, SPREADSHEET_ID, sheet_meta['Internal_Link_Queue'], len(headers[0]))
    print(f"STRATEGIC INTERNAL LINKING COMPLETE. Found {len(opportunities)} opportunities.")

def cmd_update_internal():
    """Reads Internal_Link_Queue from Google Sheets and applies links to the HTML files."""
    print("Applying Internal Links from Queue...")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=creds)

    # 1. Read the link queue
    queue_data = get_sheet_values(service, SPREADSHEET_ID, "'Internal_Link_Queue'!A2:E")
    if not queue_data:
        print("No internal link opportunities found in queue.")
        return

    # 2. Group opportunities by Source Page
    link_map = {}
    for row in queue_data:
        if len(row) < 3: continue
        source_url, target_url, anchor = row[0], row[1], row[2]
        if source_url not in link_map:
            link_map[source_url] = []
        link_map[source_url].append({'target': target_url, 'anchor': anchor})

    # 3. Apply links for each source page
    applied_count = 0
    pill_data = []
    if os.path.exists(CORNERSTONE_FILE):
        with open(CORNERSTONE_FILE, 'r') as f:
            pill_data = json.load(f)
    
    # Normalize pillar URLs with domain for matching
    pillar_urls = set()
    for row in pill_data:
        if len(row) > 1 and row[1] != '-':
            p_url = row[1]
            if not p_url.startswith('http'):
                p_url = DOMAIN.rstrip('/') + '/' + p_url.lstrip('/')
            pillar_urls.add(p_url)

    for source_url, links in link_map.items():
        # Map URL to local file path
        rel_path = source_url.replace(DOMAIN, '').strip('/')
        if not rel_path:
            file_path = os.path.join(ROOT_DIR, 'index.html')
        else:
            file_path = os.path.join(ROOT_DIR, rel_path, 'index.html')

        if not os.path.exists(file_path):
            print(f"Skipping: File not found at {file_path}")
            continue

        with open(file_path, 'r') as f:
            content = f.read()

        # Build the link block with authority-first design
        unique_links = {l['target']: l['anchor'] for l in links if l['target'] != source_url}
        if not unique_links: continue

        print(f"Updating: {file_path} with {len(unique_links)} links")
        link_html = '\n    <div class="seo-authority-block" style="margin: 4rem 0; padding: 3rem; background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); backdrop-filter: blur(10px); border-radius: 24px; font-family: var(--font-primary); position: relative; overflow: hidden;">\n'
        link_html += '        <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(to bottom, var(--primary-color), var(--accent-color));"></div>\n'
        
        # Check if we have any pillar links
        contains_pillar = any(t in pillar_urls for t in unique_links.keys())
        header = "Strategic Resources" if contains_pillar else "Related Reading"
        
        link_html += f'        <h4 style="margin: 0 0 2rem 0; color: white; font-family: var(--font-display); font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em;">{header}</h4>\n'
        link_html += '        <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 1.25rem;">\n'
        
        for target, anchor in unique_links.items():
            is_pillar = target in pillar_urls
            prefix = "⭐ " if is_pillar else ""
            weight = "600" if is_pillar else "500"
            color = "var(--primary-color)" if is_pillar else "var(--text-secondary)"
            
            link_html += f'            <li style="transition: transform 0.2s ease;">\n'
            link_html += f'                <a href="{target}" class="authority-link" style="display: flex; align-items: center; gap: 0.75rem; color: {color}; text-decoration: none; font-weight: {weight}; font-size: 1.1rem; transition: all 0.2s ease;">\n'
            link_html += f'                    <span style="display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: rgba(37, 99, 235, 0.1); border-radius: 6px; color: var(--primary-color); font-size: 0.8rem;">→</span>\n'
            link_html += f'                    <span>{prefix}{anchor}</span>\n'
            link_html += f'                </a>\n'
            link_html += f'            </li>\n'
            
        link_html += '        </ul>\n'
        link_html += '    </div>\n'
        link_html += '    <style>\n'
        link_html += '        .authority-link:hover {\n'
        link_html += '            color: white !important;\n'
        link_html += '            transform: translateX(8px);\n'
        link_html += '        }\n'
        link_html += '        .authority-link:hover span:first-child {\n'
        link_html += '            background: var(--primary-color) !important;\n'
        link_html += '            color: white !important;\n'
        link_html += '        }\n'
        link_html += '    </style>\n'
        
        block = f"<!-- SEO_INTERNAL_LINKS_START -->{link_html}<!-- SEO_INTERNAL_LINKS_END -->"

        if "<!-- SEO_INTERNAL_LINKS_START -->" in content:
            content = re.sub(r"<!-- SEO_INTERNAL_LINKS_START -->.*?<!-- SEO_INTERNAL_LINKS_END -->", block, content, flags=re.DOTALL)
        else:
            # Semantic injection logic - try to find the best spot above footer or inside main
            if "</article>" in content:
                content = content.replace("</article>", f"{block}\n</article>")
            elif "</main>" in content:
                content = content.replace("</main>", f"{block}\n</main>")
            elif re.search(r'<footer[^>]*>', content):
                content = re.sub(r'(<footer[^>]*>)', f"{block}\n\\1", content)
            else:
                content = content.replace("</body>", f"{block}\n</body>")

        with open(file_path, 'w') as f:
            f.write(content)
        applied_count += 1

    print(f"Strategic internal links applied to {applied_count} pages.")
    print("UPDATE INTERNAL COMPLETE")

HUB_CONTENT = {
    "local-seo-av": {
        "hero_title": "Antelope Valley Local SEO Dominance",
        "hero_subtitle": "Put your business on the map in Palmdale, Lancaster, and the surrounding High Desert area.",
        "impact": [
            ("Map Pack Ranking", "We specialize in getting High Desert service businesses into the top 3 spots on Google Maps."),
            ("Keyword Authority", "Target specific service areas from Quartz Hill to Rosamond with localized landing pages."),
            ("Google Business Optimization", "Fully managed profile optimization to drive calls and leads without ad spend.")
        ],
        "faqs": [
            ("Why is local SEO important in the AV?", "With Lancaster and Palmdale growing, competition for mobile searches is at an all-time high."),
            ("How long to see results?", "Most local businesses see an increase in map impressions within 30-60 days."),
            ("Do you handle reviews?", "Yes, we implement automated systems to help you capture and display customer proof.")
        ]
    },
    "nonprofit-digital": {
        "hero_title": "Nonprofit Digital Growth & TechSoup Support",
        "hero_subtitle": "Helping charitable organizations leverage Google Grants and modern tech to change more lives.",
        "impact": [
            ("Google Ad Grants", "Secure up to $10,000/month in free search advertising to reach donors and volunteers."),
            ("Donation Optimization", "Modern, low-friction giving platforms that integrate directly with your website."),
            ("TechSoup Approval", "We guide you through the TechSoup validation process to unlock massive software discounts.")
        ],
        "faqs": [
            ("What are Google Grants?", "Google provides free search ad credit to 501(c)(3) organizations to promote their mission."),
            ("Can small nonprofits apply?", "Yes, as long as you have valid tax-exempt status, we can help you apply."),
            ("Is technical support included?", "Absolutely. We manage the technical overhead so you can focus on your cause.")
        ]
    },
    "website-build-roadmap": {
        "hero_title": "Strategic Website Build Roadmap",
        "hero_subtitle": "A forensic approach to building high-performance, authority-driven digital properties.",
        "impact": [
            ("Discovery & Planning", "We map your industry vertical and competitor landscape before a single line of code is written."),
            ("Authority Architecture", "Built-in topic clusters and semantic internal linking from day one."),
            ("Conversion Optimization", "Every element is designed to move users from discovery to meaningful engagement.")
        ],
        "faqs": [
            ("How long does a build take?", "Our 'Factory' engine allows us to deploy production-ready sites in 2-4 weeks."),
            ("Is it mobile friendly?", "We follow a mobile-first philosophy ensuring perfect performance on all devices."),
            ("Do I own the code?", "Yes, we build on modern, open standards. You own your digital assets 100%.")
        ]
    },
    "managed-hosting": {
        "hero_title": "Premium Managed Hosting for Business",
        "hero_subtitle": "Lightning-fast speed, hardened security, and zero-config maintenance for your brand.",
        "impact": [
            ("Edge Performance", "Global CDN delivery ensures your site loads in under 1 second anywhere in the world."),
            ("Security Hardening", "Enterprise-grade WAF and 24/7 monitoring to keep hackers and bots away."),
            ("Automated Backups", "Daily snapshots and instant recovery so your business data is never at risk.")
        ],
        "faqs": [
            ("What is Managed Hosting?", "It means we handle all the technical updates, speed tuning, and security for you."),
            ("Do you offer email?", "Yes, we integrate with professional Google Workspace or O365 for your domain."),
            ("Can you migrate my old site?", "Yes, we provide free white-glove migration from WordPress or generic hosts.")
        ]
    },
    "website-care": {
        "hero_title": "Pro-Grade Website Care & Maintenance",
        "hero_subtitle": "Protect your digital investment with 24/7 monitoring, security hardening, and performance optimization.",
        "impact": [
            ("Uptime Security", "We monitor your site every 60 seconds. If it goes down, we're on it before you even notice."),
            ("Performance Speed", "Weekly optimizations ensure your site stays lightning fast for both users and search engines."),
            ("Peace of Mind", "Regular backups and security patches mean you never have to worry about data loss or hackers.")
        ],
        "faqs": [
            ("What is a website care plan?", "It's a comprehensive service that handles technical updates, security, and performance for you."),
            ("Do you support WordPress?", "Yes, we specialize in hardening and maintaining WordPress sites for maximum reliability."),
            ("Can I cancel anytime?", "Absolutely. Our plans are month-to-month with no long-term contracts required.")
        ]
    }
}

def cmd_hubs():
    """Systematically generates or refreshes all 11 cornerstone hub pages with rich content."""
    print("🚀 Rebuilding Strategic Authority Hubs with Rich Content Engine...")
    template_path = os.path.join(ROOT_DIR, 'templates/feature_hub.html')
    if not os.path.exists(template_path):
        print(f"Error: Template not found at {template_path}")
        return

    with open(template_path, 'r') as f:
        master_template = f.read()

    for row in CORNERSTONE_MAP_EXAMPLES:
        hub_name = row[0]
        slug = get_slug(hub_name)
        target_keyword = row[2]
        target_dir = os.path.join(ROOT_DIR, slug)
        
        print(f"--- Generating Rich Hub: {hub_name} ---")
        
        # Get specific content or fallback
        rich = HUB_CONTENT.get(hub_name, HUB_CONTENT["church-app"])
        
        # 1. Feature Cards
        subpages = [s for s in SUBPAGE_PLAN_EXAMPLES if s[0] == hub_name]
        feature_cards_html = ""
        icons = {
            'scheduling': 'fa-calendar-check', 'check-in': 'fa-user-check', 'management': 'fa-users-cog',
            'giving': 'fa-hand-holding-heart', 'tracking': 'fa-chart-line', 'automation': 'fa-robot',
            'outreach': 'fa-hands-helping', 'mass texting': 'fa-comment-sms', 'newsletter': 'fa-envelope-open-text',
            'engagement': 'fa-heart-pulse', 'onboarding': 'fa-user-plus', 'planning': 'fa-pen-to-square'
        }

        if not subpages:
            feature_cards_html = f"""
                <div class="feature-card">
                    <i class="fas fa-star"></i>
                    <h3>Premium {hub_name.replace('-', ' ').title()}</h3>
                    <p>Experience the most advanced {target_keyword} tools built for competitive business advantage.</p>
                </div>
            """
        else:
            for s in subpages[:6]:
                topic, keyword = s[1], s[3]
                icon = next((v for k, v in icons.items() if k in topic.lower()), "fa-star")
                feature_cards_html += f"""
                    <div class="feature-card">
                        <i class="fas {icon}"></i>
                        <h3>{topic.title()}</h3>
                        <p>Streamline your business with high-performance {keyword} solutions.</p>
                    </div>
                """

        # 2. Business Impact
        impact_html = ""
        for title, desc in rich["impact"]:
            impact_html += f"""
                <div class="impact-item">
                    <div class="impact-icon"><i class="fas fa-check"></i></div>
                    <div>
                        <h4 style="color: #065f46; font-size: 20px; font-weight: 700; margin-bottom: 8px;">{title}</h4>
                        <p style="color: #475569; line-height: 1.6;">{desc}</p>
                    </div>
                </div>
            """

        # 3. Cluster Roadmap
        roadmap_html = ""
        for s in [sub for sub in SUBPAGE_PLAN_EXAMPLES if sub[0] == hub_name]:
            topic_name, topic_type, topic_keyword, status = s[1], s[2], s[3], s[4]
            topic_slug = get_slug(topic_name)
            
            # Check if live
            is_live = False
            check_path = os.path.join(ROOT_DIR, 'features', topic_slug, 'index.html')
            if topic_type == 'blog':
                check_path = os.path.join(ROOT_DIR, 'blog', topic_slug, 'index.html')
            
            if os.path.exists(check_path):
                is_live = True
            
            badge_class = "badge-live" if is_live else "badge-planned"
            badge_text = "Live Guide" if is_live else "Planned"
            url = f"/{'blog' if topic_type == 'blog' else 'features'}/{topic_slug}/"
            
            roadmap_html += f"""
                <a href="{url if is_live else '#'}" class="roadmap-item">
                    <span class="roadmap-badge {badge_class}">{badge_text}</span>
                    <h4>{topic_name.title()}</h4>
                    <p>Strategic {topic_type.title()} focusing on {topic_keyword} for modern businesses.</p>
                </a>
            """

        # 4. FAQs
        faq_html = ""
        for q, a in rich["faqs"]:
            faq_html += f"""
                <div class="faq-item">
                    <h4>{q}</h4>
                    <p>{a}</p>
                </div>
            """

        # 5. Fill Template
        # Extract NAV and FOOTER from index.html for consistency
        try:
            with open(os.path.join(ROOT_DIR, 'index.html'), 'r') as index_f:
                index_content = index_f.read()
                nav_match = re.search(r'<\s*nav[^>]*>(.*?)<\s*/\s*nav\s*>', index_content, re.DOTALL | re.IGNORECASE)
                footer_match = re.search(r'<\s*footer[^>]*>(.*?)<\s*/\s*footer\s*>', index_content, re.DOTALL | re.IGNORECASE)
                nav_html = nav_match.group(1) if nav_match else ""
                footer_html = footer_match.group(1) if footer_match else ""
        except Exception as e:
            print(f"Warning: Could not extract Nav/Footer: {e}")
            nav_html = ""
            footer_html = ""

        content = master_template
        replacements = {
            '{{TITLE}}': f"{rich['hero_title']} | AI Pilots",
            '{{SLUG}}': slug,
            '{{DESCRIPTION}}': f"Strategic {target_keyword} solutions for businesses. High-performance {hub_name.replace('-', ' ')} optimization.",
            '{{HERO_TITLE}}': rich['hero_title'],
            '{{HERO_SUBTITLE}}': rich['hero_subtitle'],
            '{{FEATURE_CARDS}}': feature_cards_html,
            '{{MINISTRY_IMPACT}}': impact_html,
            '{{SUBPAGE_ROADMAP}}': roadmap_html,
            '{{FAQ_SECTION}}': faq_html,
            '{{NAV}}': nav_html,
            '{{FOOTER}}': footer_html
        }
        for k, v in replacements.items():
            content = content.replace(k, v)

        # 6. Write File
        os.makedirs(target_dir, exist_ok=True)
        with open(os.path.join(target_dir, 'index.html'), 'w') as f:
            f.write(content)
        print(f"Success: {slug}/index.html")

    print("\n✅ All Authority Hubs have been enriched with roadmap connectivity.")
    cmd_sync()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SEO Factory: Audit, Sync, and Growth Engine")
    
    # Simple Positional Command
    parser.add_argument('command', choices=['audit', 'sync', 'generate', 'discover', 'internal', 'update-internal', 'reinforce', 'autopilot', 'hubs', 'produce-subpages', 'sitemap'], help='Command to run')
    
    # Optional Arguments for 'generate'
    parser.add_argument('--type', choices=['location', 'service', 'blog', 'newsletter'], help='Type of page to generate')
    parser.add_argument('--name', help='Name/Title of the page')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making changes')

    args = parser.parse_args()

    if args.command == 'audit':
        cmd_audit()
    elif args.command == 'sync':
        cmd_sync()
    elif args.command == 'generate':
        if not args.type or not args.name:
            print("Error: --type and --name are required for 'generate' command.")
            sys.exit(1)
        cmd_generate(args)
    elif args.command == 'discover':
        cmd_discover()
    elif args.command == 'internal':
        cmd_internal()
    elif args.command == 'update-internal':
        cmd_update_internal()
    elif args.command == 'reinforce':
        cmd_reinforce()
    elif args.command == 'hubs':
        cmd_hubs()
    elif args.command == 'produce-subpages':
        cmd_produce_subpages()
    elif args.command == 'sitemap':
        cmd_sitemap()
    elif args.command == 'autopilot':
        print("Starting SEO Factory Autopilot...")
        cmd_sync()
        cmd_discover()
        cmd_reinforce()
        cmd_internal()
        print("AUTOPILOT COMPLETE")
    else:
        parser.print_help()
