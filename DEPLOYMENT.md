# Deployment Documentation

## Hosting & Deployment Configuration

### Hosting Provider
**Cloudflare Pages**

### Domain
- **Primary Domain**: `workingclasshvac.com`
- **DNS**: Typically managed by Cloudflare or pointed to the Pages project via CNAME.

### Deployment Method
This site uses **Cloudflare Wrangler CLI** for deployments, replacing the previous Bluehost cPanel Git integration.

#### Prerequisites
- Node.js & npm (installed)
- Cloudflare Account (access to `working-class-hvac` project)
- Wrangler installed locally (`npm install`)

### How to Deploy

1. **Install Dependencies** (if not already done):
   ```bash
   npm install
   ```

2. **Login to Cloudflare** (first time only):
   ```bash
   npx wrangler login
   ```
   This will open a browser window to authenticate.

3. **Deploy to Production**:
   ```bash
   npm run deploy
   ```
   This command executes `wrangler pages deploy . --project-name working-class-hvac --branch main` which uploads the current directory to Cloudflare Pages.

### Configuration Files

- **`wrangler.toml`**: Defines the project name (`working-class-hvac`) and compatibility date.
- **`_redirects`**: Handles static 301 redirects (migrated from `.htaccess`).
  - Includes legacy WordPress paths, specific page redirects, and location-based redirects.
- **`_headers`**: Sets security headers (HSTS, X-Frame-Options) and caching rules.
- **`functions/_middleware.js`**: A Cloudflare Pages Function that handles legacy date-based blog URLs (e.g., `/2024/05/15/slug/`) by redirecting them to the new `/blog/slug/` structure.
- **`.gitignore`**: Excludes `node_modules`, `.wrangler`, and other non-production files from the deployment.

### Legacy Configuration (Bluehost) - DEPRECATED
The `.cpanel.yml` file has been removed, and `.htaccess` has been renamed to `.htaccess.bak` as they are no longer used for deployment or routing.

