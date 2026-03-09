#!/usr/bin/env python3
"""
Generate Open Graph images for all AI Pilots pages
Creates simple, professional OG images with page titles
"""

import os
from pathlib import Path

# Pages that need OG images (excluding ones we already have)
pages_to_update = {
    # Main pages
    'index.html': 'Websites Built Fast, Clean, Smart',
    'services.html': 'Professional Web Development Services',
    'blog.html': 'Web Development Insights & Tips',
    
    # Service pages
    'services/custom-website-design.html': 'Custom Website Design',
    'services/website-redesign.html': 'Website Redesign Services',
    'services/website-maintenance.html': 'Website Maintenance',
    'services/seo-foundation.html': 'SEO Foundation Services',
    'services/google-business.html': 'Google Business Profile Optimization',
    'services/agency-white-label.html': 'Agency White Label Services',
    'services/nonprofit-solutions.html': 'Nonprofit Website Solutions',
    'services/managed-hosting.html': 'Managed Website Hosting',
    'services/content-updates.html': 'Website Content Updates',
    
    # Blog posts
    'blog/google-business-setup.html': 'Google Business Profile Setup Guide',
    'blog/google-business-advanced.html': 'Advanced Google Business Strategies',
    'blog/map-pack-ranking.html': 'How to Rank in Google Map Pack',
    'blog/google-reviews-strategy.html': 'Google Reviews Strategy',
    'blog/nonprofit-technology-guide.html': 'Nonprofit Technology Guide',
}

def update_og_image(filepath, image_name):
    """Update og:image meta tags in HTML file"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if og:image already exists
    if 'property="og:image"' in content:
        # Replace existing og:image
        import re
        content = re.sub(
            r'<meta property="og:image" content="[^"]*">',
            f'<meta property="og:image" content="https://aipilots.site/images/branding/{image_name}">',
            content
        )
        content = re.sub(
            r'<meta name="twitter:image" content="[^"]*">',
            f'<meta name="twitter:image" content="https://aipilots.site/images/branding/{image_name}">',
            content
        )
    else:
        # Add og:image after description meta tag
        og_tags = f'''    <meta property="og:image" content="https://aipilots.site/images/branding/{image_name}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="https://aipilots.site/images/branding/{image_name}">'''
        
        # Find description tag and insert after it
        if 'name="description"' in content:
            content = content.replace(
                'content="',
                'content="',
                1
            )
            # Find the end of description tag
            desc_end = content.find('>', content.find('name="description"'))
            if desc_end != -1:
                content = content[:desc_end+1] + '\n' + og_tags + content[desc_end+1:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {filepath}")

def main():
    print("=" * 70)
    print("Setting Default OG Images for AI Pilots Pages")
    print("=" * 70)
    print()
    print("For now, using logo.png as default OG image for all pages.")
    print("You can replace with custom screenshots later.")
    print()
    
    updated = 0
    for filepath, title in pages_to_update.items():
        if os.path.exists(filepath):
            # Use logo.png as default for now
            update_og_image(filepath, 'logo.png')
            updated += 1
        else:
            print(f"⚠ File not found: {filepath}")
    
    print()
    print("=" * 70)
    print(f"✅ Updated {updated} pages with OG image tags")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Take screenshots of hero sections for each page")
    print("2. Save as: images/branding/[page-name]-og-image.png")
    print("3. Update the og:image paths to point to custom images")
    print()

if __name__ == '__main__':
    main()
