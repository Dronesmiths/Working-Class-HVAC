#!/bin/bash

# WebP Image Conversion Script for Working Class HVAC
# Converts all PNG and JPG images to WebP format for better performance

echo "🖼️  Converting images to WebP format..."
echo "========================================="

# Check if cwebp is installed
if ! command -v cwebp &> /dev/null; then
    echo "❌ Error: cwebp is not installed"
    echo "Installing via Homebrew..."
    brew install webp
fi

# Create backup directory
BACKUP_DIR="images/originals"
mkdir -p "$BACKUP_DIR"

# Counter for converted images
converted=0
skipped=0

# Find all PNG and JPG files in images directory
find images -maxdepth 1 -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) | while read -r image; do
    # Get filename without extension
    filename=$(basename "$image")
    name="${filename%.*}"
    ext="${filename##*.}"
    
    # Output WebP filename
    webp_file="images/${name}.webp"
    
    # Skip if WebP already exists
    if [ -f "$webp_file" ]; then
        echo "⏭️  Skipping $filename (WebP already exists)"
        ((skipped++))
        continue
    fi
    
    echo "🔄 Converting: $filename → ${name}.webp"
    
    # Convert to WebP with quality 85 (good balance of quality and size)
    cwebp -q 85 "$image" -o "$webp_file"
    
    if [ $? -eq 0 ]; then
        # Get file sizes
        original_size=$(du -h "$image" | cut -f1)
        webp_size=$(du -h "$webp_file" | cut -f1)
        
        echo "   ✅ Success! Original: $original_size → WebP: $webp_size"
        
        # Move original to backup
        cp "$image" "$BACKUP_DIR/"
        echo "   📦 Original backed up to $BACKUP_DIR/"
        
        ((converted++))
    else
        echo "   ❌ Failed to convert $filename"
    fi
    
    echo ""
done

echo "========================================="
echo "✅ Conversion complete!"
echo "   Converted: $converted images"
echo "   Skipped: $skipped images"
echo ""
echo "📝 Next steps:"
echo "   1. Update HTML files to use .webp extensions"
echo "   2. Test the website locally"
echo "   3. Delete original images if satisfied (backed up in images/originals/)"
