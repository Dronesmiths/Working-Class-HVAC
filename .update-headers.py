#!/usr/bin/env python3
"""
Script to update headers and footers in all HTML files with Working Class HVAC branding
"""

import os
import re
from pathlib import Path

# Define the base directory
base_dir = Path("/Users/briansmith/Documents/GitHub/Working-Class-HVAC")

# Header replacements
header_replacements = [
    (r'<a href="/" class="logo">AV Tree <span>Pros</span></a>',
     '<a href="/" class="logo">Working Class <span>HVAC</span></a>'),
    (r'href="tel:6614984444"', 'href="tel:6614948075"'),
    (r'\(661\) 498-4444', '(661) 494-8075'),
]

# Footer brand replacement
footer_brand = (
    r'<h3>AV Tree <span>Pros</span></h3>',
    '<h3>Working Class <span>HVAC</span></h3>'
)

# Footer copyright replacement
footer_copyright = (
    r'© <span id="year"></span> AV Tree Pros\. All rights reserved\. \| Serving the Antelope Valley with pride\.',
    '© <span id="year"></span> Working Class Heating & Air. All rights reserved. | C-20 License #1024283 | <a href="https://www.google.com/maps/place/Working+Class+HVAC/@34.6599102,-118.171233,17z" target="_blank" rel="noopener" style="color: inherit; text-decoration: underline;">Find Us on Google</a>'
)

def update_file(filepath):
    """Update a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply header replacements
        for old, new in header_replacements:
            content = re.sub(old, new, content)
        
        # Apply footer replacements
        content = re.sub(footer_brand[0], footer_brand[1], content)
        content = re.sub(footer_copyright[0], footer_copyright[1], content)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {filepath.relative_to(base_dir)}")
            return True
        else:
            print(f"- Skipped (no changes): {filepath.relative_to(base_dir)}")
            return False
    except Exception as e:
        print(f"✗ Error updating {filepath}: {e}")
        return False

def main():
    """Main function to update all HTML files"""
    files_to_update = []
    
    # Add all location pages
    locations_dir = base_dir / "locations"
    if locations_dir.exists():
        for subdir in locations_dir.iterdir():
            if subdir.is_dir():
                index_file = subdir / "index.html"
                if index_file.exists():
                    files_to_update.append(index_file)
    
    # Add all service pages (excluding services/index.html which is already done)
    services_dir = base_dir / "services"
    if services_dir.exists():
        for subdir in services_dir.iterdir():
            if subdir.is_dir():
                index_file = subdir / "index.html"
                if index_file.exists():
                    files_to_update.append(index_file)
    
    print(f"\nFound {len(files_to_update)} files to update\n")
    
    updated_count = 0
    for filepath in files_to_update:
        if update_file(filepath):
            updated_count += 1
    
    print(f"\n✓ Complete! Updated {updated_count} of {len(files_to_update)} files")

if __name__ == "__main__":
    main()
