#!/bin/bash

# Configuration
PROFILE="mediusa"
BUCKET="s3://workingclasshvac"
DISTRIBUTION_ID="ERF0TEQGFAZA"

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment to AWS...${NC}"

# 1. Sync to S3
echo -e "${GREEN}Syncing files to S3 bucket: $BUCKET${NC}"
aws s3 sync . $BUCKET --profile $PROFILE --delete --exclude ".git/*" --exclude ".gitignore" --exclude "deploy.sh" --exclude "DEPLOYMENT.md" --exclude ".DS_Store" --exclude "README.md" --exclude ".cpanel.yml"

# 2. Invalidate CloudFront
echo -e "${GREEN}Invalidating CloudFront cache: $DISTRIBUTION_ID${NC}"
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*" --profile $PROFILE

echo -e "${GREEN}Deployment Complete!${NC}"
