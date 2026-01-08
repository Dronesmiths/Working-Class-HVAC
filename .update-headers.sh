#!/bin/bash

# Script to update headers and footers in all remaining HTML files

# Define the header replacement
update_header() {
    local file="$1"
    # Update logo
    sed -i '' 's|<a href="/" class="logo">AV Tree <span>Pros</span></a>|<a href="/" class="logo">Working Class <span>HVAC</span></a>|g' "$file"
    # Update phone number
    sed -i '' 's|tel:6614984444|tel:6614948075|g' "$file"
    sed -i '' 's|(661) 498-4444|(661) 494-8075|g' "$file"
}

update_footer() {
    local file="$1"
    # Update footer brand
    sed -i '' 's|<h3>AV Tree <span>Pros</span></h3>|<h3>Working Class <span>HVAC</span></h3>|g' "$file"
    # Update copyright
    sed -i '' 's|AV Tree Pros. All rights reserved. | Serving the Antelope Valley with pride.|Working Class Heating \& Air. All rights reserved. | C-20 License #1024283 | <a href="https://www.google.com/maps/place/Working+Class+HVAC/@34.6599102,-118.171233,17z" target="_blank" rel="noopener" style="color: inherit; text-decoration: underline;">Find Us on Google</a>|g' "$file"
}

# Update all location pages
for file in locations/*/index.html; do
    echo "Updating $file..."
    update_header "$file"
    update_footer "$file"
done

# Update all service pages (excluding services/index.html which is already done)
for file in services/*/index.html; do
    echo "Updating $file..."
    update_header "$file"
    update_footer "$file"
done

echo "All files updated!"
