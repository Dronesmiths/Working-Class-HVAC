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

**Last Updated**: January 29, 2026  
**Deployment Status**: ✅ Active and Verified
