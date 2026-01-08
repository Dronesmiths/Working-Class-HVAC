#!/usr/bin/env python3
"""
Script to update all HTML files to use the image logo instead of text logo
"""

import os
import re
from pathlib import Path

# Define the base directory
base_dir = Path("/Users/briansmith/Documents/GitHub/Working-Class-HVAC")

# Old logo pattern (text-based)
old_logo_pattern = r'<a href="/" class="logo">Working Class <span>HVAC</span></a>'

# New logo (image-based) - with proper path handling for subdirectories
def get_new_logo(depth=0):
    """Generate new logo HTML with correct path based on directory depth"""
    prefix = "../" * depth if depth > 0 else "/"
    return f'''<a href="/" class="logo logo-image">
                <img src="{prefix}images/working-class-logo.png" alt="Working Class HVAC" class="logo-img">
            </a>'''

def update_file(filepath, depth=0):
    """Update a single HTML file with image logo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace text logo with image logo
        content = re.sub(old_logo_pattern, get_new_logo(depth), content)
        
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
    
    # Add root level pages (depth 0)
    for page in ['about', 'contact']:
        index_file = base_dir / page / "index.html"
        if index_file.exists():
            files_to_update.append((index_file, 1))  # depth 1 for /about/, /contact/
    
    # Add all location pages (depth 2)
    locations_dir = base_dir / "locations"
    if locations_dir.exists():
        for subdir in locations_dir.iterdir():
            if subdir.is_dir():
                index_file = subdir / "index.html"
                if index_file.exists():
                    files_to_update.append((index_file, 2))  # depth 2 for /locations/city/
    
    # Add all service pages (depth 2)
    services_dir = base_dir / "services"
    if services_dir.exists():
        # Services index
        services_index = services_dir / "index.html"
        if services_index.exists():
            files_to_update.append((services_index, 1))  # depth 1 for /services/
        
        # Individual service pages
        for subdir in services_dir.iterdir():
            if subdir.is_dir():
                index_file = subdir / "index.html"
                if index_file.exists():
                    files_to_update.append((index_file, 2))  # depth 2 for /services/service-name/
    
    print(f"\nFound {len(files_to_update)} files to update\n")
    
    updated_count = 0
    for filepath, depth in files_to_update:
        if update_file(filepath, depth):
            updated_count += 1
    
    print(f"\n✓ Complete! Updated {updated_count} of {len(files_to_update)} files")

if __name__ == "__main__":
    main()
