# Deployment: AWS S3 + CloudFront

This repository is deployed to **AWS S3** and served via **CloudFront**.

## Infrastructure
-   **S3 Bucket:** `workingclasshvac`
-   **CloudFront Distribution:** `ERF0TEQGFAZA`
-   **AWS Profile:** `mediusa`

## How to Deploy
Run the included deployment script from the project root:

```bash
./deploy.sh
```

This script will:
1.  Sync all site files to the S3 bucket (deleting removed files).
2.  Invalidate the CloudFront cache to ensure users see the latest version immediately.

## Prerequisites
-   AWS CLI installed.
-   `mediusa` profile configured with permissions for the bucket and distribution.
