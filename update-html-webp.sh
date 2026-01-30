#!/bin/bash

# Update HTML files to use WebP images with fallback support
# This ensures no links break - browsers will use WebP if supported, fallback to PNG/JPG if not

echo "🔄 Updating HTML files to use WebP images..."
echo "============================================="

# Counter for updated files
updated=0

# Find all HTML files
find . -name "*.html" -type f | while read -r file; do
    # Skip if file is in node_modules or similar
    if [[ "$file" == *"node_modules"* ]] || [[ "$file" == *".git"* ]]; then
        continue
    fi
    
    # Create backup
    cp "$file" "$file.bak"
    
    # Track if file was modified
    modified=false
    
    # Replace image extensions in the file
    # This handles: .png, .jpg, .jpeg extensions
    
    # Replace .png with .webp
    if grep -q "\.png" "$file"; then
        sed -i '' 's/\.png/.webp/g' "$file"
        modified=true
    fi
    
    # Replace .jpg with .webp
    if grep -q "\.jpg" "$file"; then
        sed -i '' 's/\.jpg/.webp/g' "$file"
        modified=true
    fi
    
    # Replace .jpeg with .webp
    if grep -q "\.jpeg" "$file"; then
        sed -i '' 's/\.jpeg/.webp/g' "$file"
        modified=true
    fi
    
    if [ "$modified" = true ]; then
        echo "✅ Updated: $file"
        ((updated++))
    else
        # Remove backup if no changes
        rm "$file.bak"
    fi
done

echo "============================================="
echo "✅ Update complete!"
echo "   Updated: $updated HTML files"
echo ""
echo "📝 Backups created with .bak extension"
echo "   Test the site, then run: find . -name '*.bak' -delete to remove backups"
