import os
import json

# Configuration
SITE_URL = "https://aipilots.site"
ROOT_DIR = "."

def generate_breadcrumb_schema(relative_path):
    """
    Generates JSON-LD BreadcrumbList based on the file path.
    """
    path_parts = relative_path.strip("/").split("/")
    
    # Remove index.html from parts if present
    if "index.html" in path_parts:
        path_parts.remove("index.html")
    
    # Handle root case
    if not path_parts:
        return None

    breadcrumbs = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": SITE_URL + "/"
        }
    ]

    current_path = ""
    for i, part in enumerate(path_parts):
        current_path += f"/{part}"
        
        # Format name: "av-web-designers" -> "Av Web Designers"
        # Special handling for "av" -> "AV"
        name = part.replace("-", " ").title().replace("Av ", "AV ")
        
        # Intermediate Path or Leaf
        # Note: Google recommends the item URL for the last item too
        breadcrumbs.append({
            "@type": "ListItem",
            "position": i + 2,
            "name": name,
            "item": f"{SITE_URL}{current_path}/"
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumbs
    }
    
    return json.dumps(schema, indent=2)

def inject_schema(file_path):
    """
    Injects the schema into the <head> of the HTML file using string replacement.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip if already has BreadcrumbList
        if "BreadcrumbList" in content:
            print(f"Skipping {file_path} (Schema already exists)")
            return
        
        # Get relative path for schema generation
        # We need to compute relative path from the script execution location (root)
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        
        # Skip root index.html
        if rel_path == "index.html":
            return

        json_ld_string = generate_breadcrumb_schema(rel_path)
        
        if not json_ld_string:
            return

        # Prepare the script block
        script_block = f'\n    <!-- JSON-LD Breadcrumb Schema -->\n    <script type="application/ld+json">\n{json_ld_string}\n    </script>'

        # Inject before closing head tag
        if "</head>" in content:
            new_content = content.replace("</head>", f"{script_block}\n</head>")
            
            print(f"Injecting schema into {file_path}")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        else:
            print(f"Warning: No </head> found in {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    # Target directories
    target_dirs = [
        "services",
        "industries",
        "portfolio",
        "blog"
    ]

    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            print(f"Directory not found: {target_dir}")
            continue
            
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".html"):
                    file_path = os.path.join(root, file)
                    inject_schema(file_path)

if __name__ == "__main__":
    main()
