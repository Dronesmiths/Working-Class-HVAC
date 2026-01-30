# DNS Configuration for workingclasshvac.com

## Current DNS Setup

**Domain**: `workingclasshvac.com`  
**Registrar**: (Check where you purchased the domain)  
**Hosting**: Bluehost  
**Status**: ✅ Currently pointing to Bluehost

---

## DNS Records Overview

### Essential DNS Records for Your Site

#### 1. **A Record** (Primary Domain)
Points your domain to your server's IP address.

```
Type: A
Host: @
Points to: [Bluehost Server IP]
TTL: 14400 (4 hours) or Auto
```

#### 2. **A Record** (WWW Subdomain)
Points www.workingclasshvac.com to the same server.

```
Type: A
Host: www
Points to: [Bluehost Server IP]
TTL: 14400 or Auto
```

#### 3. **CNAME Record** (WWW Alternative)
Alternative to A record for www subdomain.

```
Type: CNAME
Host: www
Points to: workingclasshvac.com
TTL: 14400 or Auto
```

---

## How to Check Your Current DNS

### Option 1: Command Line
```bash
# Check A record
dig workingclasshvac.com A

# Check nameservers
dig workingclasshvac.com NS

# Check all records
dig workingclasshvac.com ANY
```

### Option 2: Online Tools
- **WhatsMyDNS**: https://www.whatsmydns.net/
- **DNS Checker**: https://dnschecker.org/
- **MXToolbox**: https://mxtoolbox.com/SuperTool.aspx

---

## Common DNS Records You Might Need

### Email Records (if using email)

#### MX Records (Mail Exchange)
```
Type: MX
Host: @
Points to: mail.workingclasshvac.com
Priority: 10
TTL: 14400
```

#### SPF Record (Prevent Email Spoofing)
```
Type: TXT
Host: @
Value: v=spf1 include:_spf.bluehost.com ~all
TTL: 14400
```

#### DKIM Record (Email Authentication)
```
Type: TXT
Host: default._domainkey
Value: [Provided by Bluehost]
TTL: 14400
```

#### DMARC Record (Email Security)
```
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=none; rua=mailto:admin@workingclasshvac.com
TTL: 14400
```

### Subdomains

#### Example: blog.workingclasshvac.com
```
Type: CNAME
Host: blog
Points to: workingclasshvac.com
TTL: 14400
```

#### Example: app.workingclasshvac.com
```
Type: A
Host: app
Points to: [Server IP]
TTL: 14400
```

---

## How to Update DNS Records

### If Using Bluehost DNS:
1. Log into Bluehost cPanel
2. Go to **Domains** → **Zone Editor**
3. Find `workingclasshvac.com`
4. Click **Manage**
5. Add/Edit/Delete records as needed

### If Using External DNS (Cloudflare, etc.):
1. Log into your DNS provider
2. Find DNS management for `workingclasshvac.com`
3. Add/Edit records
4. Save changes
5. Wait for propagation (5 minutes to 48 hours)

---

## DNS Propagation

After making DNS changes:
- **Local**: 5-30 minutes
- **Regional**: 1-4 hours
- **Global**: 24-48 hours (worst case)

**Check propagation**: https://www.whatsmydns.net/

---

## Recommended DNS Setup for Performance

### Use Cloudflare (Free CDN + DNS)

**Benefits**:
- ✅ Faster DNS resolution
- ✅ Free SSL/TLS
- ✅ DDoS protection
- ✅ CDN (Content Delivery Network)
- ✅ Caching for faster load times
- ✅ Analytics

**How to Set Up**:
1. Create free account at https://cloudflare.com
2. Add your domain `workingclasshvac.com`
3. Cloudflare will scan your existing DNS records
4. Update nameservers at your domain registrar to Cloudflare's:
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```
5. Configure SSL/TLS to "Full" or "Full (Strict)"
6. Enable "Always Use HTTPS"
7. Your site will be faster and more secure!

---

## Troubleshooting DNS Issues

### Site Not Loading
1. Check if domain is registered and not expired
2. Verify nameservers are correct
3. Check A record points to correct IP
4. Clear browser cache
5. Try different browser/device

### WWW Not Working
- Add CNAME record for `www` pointing to `@` or root domain
- Or add A record for `www` with same IP as root

### Email Not Working
- Verify MX records are correct
- Check SPF, DKIM, DMARC records
- Contact hosting provider for email server details

---

## Current Status Check

Run this command to see your current DNS setup:
```bash
dig workingclasshvac.com ANY +noall +answer
```

---

**Last Updated**: January 29, 2026  
**DNS Status**: ✅ Active and pointing to Bluehost

## Next Steps

1. ✅ Verify current DNS records in Bluehost cPanel
2. ⏸️ Consider Cloudflare for improved performance (optional)
3. ⏸️ Set up email DNS records if needed
4. ⏸️ Add any subdomains you need
