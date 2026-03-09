#!/usr/bin/env python3
"""
Add comprehensive schema markup to all AI Pilots pages for SEO and LLM optimization
"""

import os
import json
from pathlib import Path

# Base directory
BASE_DIR = Path("/Users/mediusa/NOVA/Repos/AI-Pilots")

# Organization schema (used on all pages)
ORGANIZATION_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "AI Pilots",
    "alternateName": "AI Pilots - Brian Smith",
    "description": "AI-powered web design and automation studio that builds fast, secure, and SEO-optimized websites for small and local businesses. We specialize in custom website development, cloud hosting, search engine optimization, and AI-driven workflows.",
    "url": "https://aipilots.site",
    "logo": "https://aipilots.site/images/branding/logo.png",
    "image": "https://aipilots.site/images/branding/logo.png",
    "telephone": "+16619936669",
    "email": "Dronesmiths2@gmail.com",
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "Lancaster",
        "addressRegion": "CA",
        "addressCountry": "US"
    },
    "areaServed": [
        {
            "@type": "City",
            "name": "Lancaster",
            "containedInPlace": {"@type": "State", "name": "California"}
        },
        {
            "@type": "City",
            "name": "Palmdale",
            "containedInPlace": {"@type": "State", "name": "California"}
        },
        {
            "@type": "City",
            "name": "Santa Clarita",
            "containedInPlace": {"@type": "State", "name": "California"}
        },
        {
            "@type": "City",
            "name": "Los Angeles",
            "containedInPlace": {"@type": "State", "name": "California"}
        }
    ],
    "priceRange": "$$",
    "founder": {
        "@type": "Person",
        "name": "Brian Smith",
        "jobTitle": "Founder & Lead Developer",
        "email": "Dronesmiths2@gmail.com",
        "telephone": "+16619936669"
    },
    "sameAs": [
        "https://github.com/Dronesmiths/AI-Pilots"
    ]
}

# Service definitions
SERVICES = {
    "custom-website-design": {
        "name": "Custom Website Design",
        "description": "Professional custom website design services for small businesses. We build fast, modern, SEO-optimized websites from scratch."
    },
    "website-redesign": {
        "name": "Website Redesign",
        "description": "Transform your outdated website into a modern, fast, and mobile-friendly site that ranks on Google."
    },
    "website-maintenance": {
        "name": "Website Maintenance",
        "description": "Ongoing website maintenance, updates, security patches, and technical support to keep your site running smoothly."
    },
    "seo-foundation": {
        "name": "SEO Foundation",
        "description": "Complete SEO setup including technical optimization, on-page SEO, schema markup, and search console configuration."
    },
    "google-business": {
        "name": "Google Business Profile Optimization",
        "description": "Google Business Profile setup, optimization, and management to dominate local search and the Map Pack."
    },
    "agency-white-label": {
        "name": "Agency White Label Services",
        "description": "White label web development services for agencies. We build websites under your brand while you focus on clients."
    },
    "nonprofit-solutions": {
        "name": "Nonprofit Website & Google Ads Grant",
        "description": "Complete nonprofit website solutions including design, Google Ads Grant management ($10k/month free advertising), and ongoing support."
    },
    "managed-hosting": {
        "name": "Managed Cloud Hosting",
        "description": "Fast, secure cloud hosting on AWS with automatic backups, SSL certificates, and 99.9% uptime guarantee."
    },
    "content-updates": {
        "name": "Content Updates",
        "description": "Professional content updates for your website including text changes, image updates, and new page creation."
    }
}

def create_service_schema(service_slug, service_info):
    """Create Service schema for a service page"""
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": service_info["name"],
        "provider": {
            "@type": "ProfessionalService",
            "name": "AI Pilots",
            "url": "https://aipilots.site"
        },
        "areaServed": {
            "@type": "State",
            "name": "California"
        },
        "description": service_info["description"],
        "offers": {
            "@type": "Offer",
            "availability": "https://schema.org/InStock",
            "url": f"https://aipilots.site/services/{service_slug}"
        }
    }

def create_breadcrumb_schema(items):
    """Create BreadcrumbList schema"""
    list_items = []
    for i, (name, url) in enumerate(items, 1):
        list_items.append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": url
        })
    
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": list_items
    }

def format_schema(schema_dict):
    """Format schema as pretty JSON for HTML insertion"""
    json_str = json.dumps(schema_dict, indent=2, ensure_ascii=False)
    return f'<script type="application/ld+json">\n{json_str}\n</script>'

def insert_schema_before_head_close(html_content, schema_html):
    """Insert schema markup before </head>"""
    if "</head>" in html_content:
        return html_content.replace("</head>", f"\n    {schema_html}\n</head>")
    return html_content

def add_schema_to_homepage():
    """Add Organization + WebSite schema to homepage"""
    file_path = BASE_DIR / "index.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if schema already exists
    if 'application/ld+json' in content and '@type":"ProfessionalService"' in content:
        print(f"✓ Schema already exists in {file_path.name}")
        return
    
    # WebSite schema with search action
    website_schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "AI Pilots",
        "url": "https://aipilots.site",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": "https://aipilots.site/search?q={search_term_string}"
            },
            "query-input": "required name=search_term_string"
        }
    }
    
    # Combine schemas
    combined_schema = format_schema(ORGANIZATION_SCHEMA) + "\n    " + format_schema(website_schema)
    
    # Insert before </head>
    new_content = insert_schema_before_head_close(content, combined_schema)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Added Organization + WebSite schema to {file_path.name}")

def add_schema_to_service_pages():
    """Add Service schema to all service pages"""
    services_dir = BASE_DIR / "services"
    
    for service_slug, service_info in SERVICES.items():
        file_path = services_dir / f"{service_slug}.html"
        
        if not file_path.exists():
            print(f"✗ File not found: {file_path.name}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if schema already exists
        if 'application/ld+json' in content and f'"{service_info["name"]}"' in content:
            print(f"✓ Schema already exists in {file_path.name}")
            continue
        
        # Create schemas
        service_schema = create_service_schema(service_slug, service_info)
        breadcrumb_schema = create_breadcrumb_schema([
            ("Home", "https://aipilots.site"),
            ("Services", "https://aipilots.site/services"),
            (service_info["name"], f"https://aipilots.site/services/{service_slug}")
        ])
        
        # Combine
        combined_schema = (format_schema(ORGANIZATION_SCHEMA) + "\n    " + 
                          format_schema(service_schema) + "\n    " +
                          format_schema(breadcrumb_schema))
        
        # Insert
        new_content = insert_schema_before_head_close(content, combined_schema)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Added Service + Breadcrumb schema to {file_path.name}")

def add_schema_to_start_flight():
    """Add Person + Organization schema to Start Your Flight page"""
    file_path = BASE_DIR / "start-your-flight.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if schema already exists
    if 'application/ld+json' in content and '@type":"Person"' in content:
        print(f"✓ Schema already exists in {file_path.name}")
        return
    
    # Person schema for Brian
    person_schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Brian Smith",
        "jobTitle": "Founder & Lead Developer",
        "worksFor": {
            "@type": "Organization",
            "name": "AI Pilots"
        },
        "email": "Dronesmiths2@gmail.com",
        "telephone": "+16619936669",
        "url": "https://aipilots.site/start-your-flight",
        "description": "Solo web developer specializing in SEO-optimized websites for small businesses in Southern California"
    }
    
    # Combine
    combined_schema = format_schema(ORGANIZATION_SCHEMA) + "\n    " + format_schema(person_schema)
    
    # Insert
    new_content = insert_schema_before_head_close(content, combined_schema)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Added Organization + Person schema to {file_path.name}")

def main():
    print("=" * 60)
    print("Adding Schema Markup to AI Pilots Website")
    print("=" * 60)
    print()
    
    print("Phase 1: Homepage")
    add_schema_to_homepage()
    print()
    
    print("Phase 2: Start Your Flight Page")
    add_schema_to_start_flight()
    print()
    
    print("Phase 3: Service Pages")
    add_schema_to_service_pages()
    print()
    
    print("=" * 60)
    print("Schema markup implementation complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
