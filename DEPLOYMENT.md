# Deployment: Bluehost cPanel (Git-Based)

This repository is configured for deployment via **Bluehost cPanel**, not AWS S3.

## Hosting Indication
The presence of `.cpanel.yml` indicates that a cPanel "Git Version Control" or "Push to Deploy" mechanism is in use.

**File:** `.cpanel.yml`
```yaml
deployment:
  tasks:
    - export DEPLOYPATH=/home1/spreaeb3/public_html/website_b823468b/
    - /bin/cp -R * $DEPLOYPATH
```

## Workflow
1.  **Develop Locally:** Make changes on your machine.
2.  **Commit & Push:** Push changes to GitHub (`main` branch).
    ```bash
    git add .
    git commit -m "Update site content"
    git push origin main
    ```
3.  **Deploy (Automatic or Manual):** 
    -   Depending on your cPanel configuration, Bluehost will either automatically pull these changes or you may need to log in to cPanel and click "Update from Repository" (or a similar "Pull" button) in the Git Version Control section.
    -   The `.cpanel.yml` script then copies the files to the public `website_b823468b` directory.

## Current Status
-   **Local Repo:** Connected to `https://github.com/Dronesmiths/Working-Class-HVAC.git`
-   **Branch:** `main` (Synced with remote)
-   **Hosting:** Bluehost (Verified via DNS and config file)
