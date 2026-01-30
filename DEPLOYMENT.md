# Deployment Documentation

## Hosting & Deployment Configuration

### Hosting Provider
**Bluehost** - cPanel Shared Hosting

### Domain
- **Primary Domain**: `workingclasshvac.com`
- **Nameservers**: Configured to point to Bluehost

### Git Version Control Deployment

#### Repository
- **GitHub Repository**: `https://github.com/Dronesmiths/Working-Class-HVAC.git`
- **Branch**: `main`

#### Deployment Method
This site uses **Bluehost cPanel Git Version Control** for automated deployments.

#### Configuration File
The `.cpanel.yml` file in the root directory controls the deployment process:

```yaml
---
deployment:
  tasks:
    - export DEPLOYPATH=/home1/spreaeb3/public_html/website_b823468b/
    - /bin/cp -R * $DEPLOYPATH
```

#### Deployment Details
- **cPanel Account**: `spreaeb3`
- **Deployment Path**: `/home1/spreaeb3/public_html/website_b823468b/`
- **Deployment Trigger**: Automatic on Git push to `main` branch

### How to Deploy Changes

1. **Make changes** to your local files
2. **Stage changes**: 
   ```bash
   git add .
   ```
3. **Commit changes**:
   ```bash
   git commit -m "Description of changes"
   ```
4. **Push to GitHub**:
   ```bash
   git push origin main
   ```
5. **Bluehost automatically deploys** the changes to the live site via the cPanel Git Version Control integration

### Deployment Verification
After pushing changes:
1. Wait 1-2 minutes for cPanel to process the deployment
2. Visit `https://workingclasshvac.com` to verify changes are live
3. Clear browser cache if changes don't appear immediately (Cmd+Shift+R on Mac)

### Important Notes
- All files in the repository root are copied to the deployment path
- The `.cpanel.yml` file must remain in the repository for automated deployment to work
- Changes pushed to GitHub will automatically appear on the live site
- Deployment is triggered by pushes to the `main` branch only

### SEO Configuration
- **Sitemap**: `https://workingclasshvac.com/sitemap.xml`
- **Robots.txt**: Configured to allow all crawlers
- **Meta tags**: Implemented on all pages for optimal SEO

---

## Troubleshooting

### 500 Internal Server Error

If you encounter a **500 Internal Server Error** when accessing the site:

#### Possible Causes:
1. **Git Deployment Not Configured in cPanel**
   - Log into your Bluehost cPanel
   - Navigate to **Git Version Control**
   - Ensure the repository is properly linked and deployment is enabled
   
2. **Incorrect Deployment Path**
   - Verify the path in `.cpanel.yml` matches your actual cPanel directory structure
   - The current path is: `/home1/spreaeb3/public_html/website_b823468b/`
   - You may need to adjust this to point to your domain's root directory

3. **File Permissions**
   - HTML files should be `644` (readable by all, writable by owner)
   - Directories should be `755` (executable/searchable by all)
   - Check permissions in cPanel File Manager

4. **PHP Errors** (if using PHP files)
   - Check cPanel Error Logs for specific PHP errors
   - Ensure PHP version compatibility

#### How to Fix:

**Option 1: Check cPanel Git Version Control**
1. Log into Bluehost cPanel
2. Go to **Git Version Control** under Files section
3. Click **Manage** on your repository
4. Click **Pull or Deploy** → **Deploy HEAD Commit**
5. Check for any error messages

**Option 2: Verify Deployment Path**
1. In cPanel, go to **File Manager**
2. Navigate to `public_html`
3. Verify the `website_b823468b` directory exists
4. If your domain should point to a different directory, update `.cpanel.yml`

**Option 3: Manual File Upload Test**
1. Upload `deploy-test.html` manually via cPanel File Manager
2. Try accessing it directly: `https://workingclasshvac.com/deploy-test.html`
3. If it works manually but not via Git, the issue is with Git deployment configuration

**Option 4: Check Error Logs**
1. In cPanel, go to **Metrics** → **Errors**
2. Look for recent 500 errors
3. The error log will show the specific cause

---

**Last Updated**: January 29, 2026 @ 9:30 PM PST  
**Deployment Status**: ✅ **VERIFIED AND WORKING**

### Deployment Verification Completed:
- ✅ Domain nameservers correctly pointed to Bluehost
- ✅ Git Version Control properly configured in cPanel
- ✅ Files deploying from GitHub to live server automatically
- ✅ Directory-based URL structure working correctly
- ✅ Ready for production updates via Git push
