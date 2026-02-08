import os

# Define the root directory
ROOT_DIR = "/Users/mediusa/NOVA/Repos/Working-Class-HVAC-main"

# The new list item to add
NEW_SERVICE_LINK = '                    <li><a href="/services/mini-splits/">Ductless Mini-Splits</a></li>'

# The target line to insert after (using Mobile Home HVAC as the anchor since we just added it)
ANCHOR_LINE = '                    <li><a href="/services/mobile-home-hvac/">Mobile Home HVAC</a></li>'

def update_footer(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        new_content = []
        modified = False
        
        # Check if the file already has the link to avoid duplicates
        file_str = ''.join(content)
        if "/services/mini-splits/" in file_str:
            print(f"Skipping {file_path} - already updated.")
            return

        for line in content:
            new_content.append(line)
            if ANCHOR_LINE in line and not modified:
                new_content.append(NEW_SERVICE_LINK + "\n")
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_content)
            print(f"Updated {file_path}")
        else:
            print(f"Anchor not found in {file_path}")

    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".html"):
                update_footer(os.path.join(root, file))

if __name__ == "__main__":
    main()
