import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import time

# Configuration
SITEMAP_PATH = "/Users/mediusa/NOVA/Repos/AI-Pilots/sitemap.xml"
BASE_URL = "https://aipilots.site"
REPO_ROOT = "/Users/mediusa/NOVA/Repos/AI-Pilots"

def get_sitemap_urls():
    urls = []
    try:
        tree = ET.parse(SITEMAP_PATH)
        root = tree.getroot()
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for loc in root.findall('.//ns:loc', ns):
            urls.append(loc.text.strip())
    except Exception as e:
        print(f"Error parsing sitemap: {e}")
    return urls

def url_to_local_path(url):
    parsed = urlparse(url)
    path = parsed.path
    if not path or path == "/":
        return os.path.join(REPO_ROOT, "index.html")
    
    # Remove leading slash
    rel_path = path.lstrip("/")
    
    # Handle directories (assume index.html)
    if not rel_path.endswith(".html"):
        local_path = os.path.join(REPO_ROOT, rel_path, "index.html")
    else:
        local_path = os.path.join(REPO_ROOT, rel_path)
    
    return local_path

def check_404s():
    urls = get_sitemap_urls()
    print(f"Found {len(urls)} URLs in sitemap. Starting audit...\n")
    
    broken_live = []
    missing_local = []
    success_count = 0
    
    for url in urls:
        print(f"Checking: {url}", end="\r")
        
        # Check Live Status
        try:
            # Using HEAD first for efficiency
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code >= 400:
                # Retry with GET just in case HEAD is not supported correctly
                response = requests.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code >= 400:
                broken_live.append((url, response.status_code))
                print(f"\n[BROKEN LIVE] {url} - Status: {response.status_code}")
        except Exception as e:
            broken_live.append((url, str(e)))
            print(f"\n[ERROR LIVE] {url} - {e}")

        # Check Local File
        local_path = url_to_local_path(url)
        if not os.path.exists(local_path):
            missing_local.append((url, local_path))
            print(f"\n[MISSING LOCAL] {url} - Expected: {local_path}")
        
        success_count += 1
        time.sleep(0.1) # Be polite

    print("\n" + "="*50)
    print("AUDIT SUMMARY")
    print("="*50)
    print(f"Total URLs Checked: {len(urls)}")
    print(f"Broken Live URLs: {len(broken_live)}")
    print(f"Missing Local Files: {len(missing_local)}")
    print("="*50)

    if broken_live:
        print("\nBroken Live Details:")
        for url, status in broken_live:
            print(f"- {url} ({status})")
            
    if missing_local:
        print("\nMissing Local Details:")
        for url, path in missing_local:
             print(f"- {url} --> {path}")

if __name__ == "__main__":
    check_404s()
