# QUICK START IMPLEMENTATION GUIDE
## Bowling Calendar System - Joomla + cPanel Python Pivot

**Target Audience:** Professional Developer  
**Estimated Implementation Time:** 6-8 weeks

---

## AT A GLANCE

### Current State
- Ubuntu server with continuous Python script
- FTP upload of static HTML
- 15-second polling interval
- Plaintext credentials
- Single monolithic application

### Target State
- cPanel Python WSGI application (backend API)
- Joomla module (frontend)
- REST API architecture
- JWT + API key authentication
- Cached responses (5-minute default)
- Professional security standards
- Modern UI with bowling-themed SVG animations

---

## ARCHITECTURE OVERVIEW

```
User Browser
     ↓
Joomla Module (PHP/JS/CSS)
     ↓ HTTPS/JSON
Python API (Flask/FastAPI on cPanel)
     ↓ OAuth 2.0
Google Calendar API
```

---

## PHASE 1: BACKEND (Week 1-2)

### Setup cPanel Python App

**cPanel Configuration:**
```
Python Version: 3.9+
App Root: /home/username/cps-calendar-api
App URL: api.yourdomain.com or /cps-api
Startup File: passenger_wsgi.py
Entry Point: application
```

**Required Files:**
```
cps-calendar-api/
├── app/
│   ├── main.py              # Flask app with routes
│   ├── config.py            # Environment config
│   ├── auth.py              # JWT + API key validation
│   ├── calendar_service.py  # Google Calendar integration
│   ├── cache.py             # Caching layer (file/Redis)
│   └── utils.py             # Helper functions
├── passenger_wsgi.py        # WSGI entry point
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
└── scripts/
    ├── warmup_cache.py      # Cron: cache warmup
    └── refresh_token.py     # Cron: token refresh
```

**Environment Variables:**
```bash
FLASK_ENV=production
SECRET_KEY=<generate-32-char-random>
JWT_SECRET=<generate-32-char-random>
API_KEY=<generate-32-char-random>
GOOGLE_CALENDAR_ID=tyson@cornerpins.com.au
SERVICE_ACCOUNT_FILE=/home/username/cps-calendar-api/service-account.json
CACHE_TYPE=file
CACHE_TIMEOUT=300
ALLOWED_ORIGINS=https://yourdomain.com
```

**API Endpoints to Implement:**
```
GET  /api/v1/health          → Health check
GET  /api/v1/events          → Fetch calendar events (auth required)
GET  /api/v1/colors          → Get color mappings
POST /api/v1/cache/clear     → Manual cache clear (admin only)
```

**Cron Jobs:**
```
*/5 * * * * python warmup_cache.py    # Every 5 minutes
0 * * * * python refresh_token.py     # Every hour
```

### Key Implementation Details

**calendar_service.py - Core Logic:**
```python
class CalendarService:
    def get_events(self, from_date=None, limit=100):
        # 1. Fetch from Google Calendar API
        # 2. Process each event:
        #    - Extract location (first part before comma)
        #    - Parse description for URLs
        #    - Identify TenpinResults links
        #    - Process attachments (pattern vs entry)
        #    - Calculate text color based on bg luminance
        # 3. Return enriched event data
```

**Event Data Structure:**
```json
{
  "id": "event_id",
  "summary": "Event Title",
  "start": {"date": "2026-11-21"},
  "end": {"date": "2026-11-22"},
  "locationShort": "Venue Name",
  "backgroundColor": "#d60000",
  "textColor": "#ffffff",
  "urls": {
    "tenpinResults": "https://...",
    "other": "https://..."
  },
  "attachments": [...]
}
```

---

## PHASE 2: FRONTEND (Week 3-4)

### Joomla Module Structure

```
mod_cps_calendar/
├── mod_cps_calendar.php     # Entry point
├── mod_cps_calendar.xml     # Manifest
├── helper.php               # PHP helper class
├── tmpl/
│   └── default.php          # Display template
├── media/
│   ├── css/
│   │   └── calendar.css     # Styles
│   ├── js/
│   │   ├── calendar.js      # Main logic
│   │   └── animations.js    # SVG animations
│   ├── images/
│   │   ├── register.png
│   │   ├── link.png
│   │   ├── pattern.png
│   │   └── entry.png
│   └── svg/
│       ├── bowling-pins.svg
│       ├── bowling-ball.svg
│       └── pin-strike.svg
└── language/
    └── en-GB/
        └── en-GB.mod_cps_calendar.ini
```

### Design Implementation

**Color Palette (from theme.jpg):**
```css
:root {
  --bg-primary: #2d3e50;      /* Dark navy background */
  --bg-card: #34495e;          /* Card background */
  --accent-purple: #8B7BC4;    /* Purple headings */
  --accent-cyan: #4ecdc4;      /* Cyan subheadings */
  --text-primary: #ffffff;
  --text-secondary: #b0b8c1;
  --border: #4a5f7a;
}
```

**Key CSS Classes:**
```css
.cps-calendar-wrapper { /* Main container */ }
.month-separator { /* Month heading with bowling pins */ }
.event-card { /* Individual event card */ }
.event-date-badge { /* Purple date badge */ }
.event-title { /* Event title */ }
.event-location { /* Location with map link */ }
.action-icons { /* Register/link/attachment icons */ }
```

**SVG Animations:**
1. **Page Load:** Bowling pins fade in from top
2. **Month Transition:** Bowling ball rolls across, pins fall
3. **Card Hover:** Scale up slightly with shadow
4. **Loading:** Spinning bowling ball

### JavaScript AJAX Implementation

```javascript
class CPSCalendar {
  constructor(apiEndpoint, apiKey) {
    this.apiEndpoint = apiEndpoint;
    this.apiKey = apiKey;
    this.cache = null;
    this.init();
  }

  async fetchEvents() {
    // AJAX call to API endpoint
    // Handle errors gracefully
    // Cache response locally (sessionStorage)
    // Return processed data
  }

  renderEvents(events) {
    // Group by month/year
    // Create month separators
    // Render event cards
    // Attach event listeners
    // Trigger animations
  }

  initAnimations() {
    // GSAP or CSS animations
    // Staggered card fade-in
    // Bowling ball effects
  }
}
```

---

## PHASE 3: SECURITY IMPLEMENTATION

### Authentication Flow

```
1. Joomla module configured with API_KEY
2. Module makes request: Authorization: Bearer JWT + X-API-Key: KEY
3. Backend validates both
4. If valid, return data
5. If invalid, return 401 Unauthorized
```

### Security Checklist

**Backend:**
- [x] JWT validation on all protected endpoints
- [x] API key validation
- [x] Rate limiting (100 req/hour per IP)
- [x] CORS restricted to Joomla domain
- [x] HTTPS enforced
- [x] No sensitive data in logs
- [x] Environment variables for secrets
- [x] Service account file permissions: 600

**Frontend:**
- [x] XSS prevention (sanitize all output)
- [x] CSRF tokens for form submissions
- [x] No API keys in client-side code (store in module config)
- [x] Input validation
- [x] Secure headers (CSP, X-Frame-Options)

---

## PHASE 4: TESTING

### Test Scenarios

**Functional Tests:**
1. Events display correctly
2. Color coding works
3. Text contrast is readable
4. Links are functional
5. Attachments display correct icons
6. Date ranges format properly
7. Month grouping works
8. Responsive design functions

**Performance Tests:**
1. Page load < 2s
2. API response < 500ms (cached)
3. Animations run at 30+ fps
4. No JavaScript errors
5. Cache hit rate > 80%

**Security Tests:**
1. Unauthorized API access blocked
2. Rate limiting works
3. XSS attempts blocked
4. CORS properly configured
5. HTTPS enforced

**Compatibility Tests:**
1. Chrome, Firefox, Safari, Edge (latest 2 versions)
2. Mobile browsers (iOS Safari, Chrome Mobile)
3. Joomla 4.x and 5.x
4. PHP 8.1, 8.2, 8.3

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation complete
- [ ] SSL certificate installed
- [ ] Backup strategy in place

### Backend Deployment

1. Upload files to `/home/username/cps-calendar-api`
2. Create virtual environment and install dependencies
3. Configure environment variables in cPanel
4. Upload service account JSON file (chmod 600)
5. Configure Python app in cPanel
6. Set up cron jobs
7. Test API health endpoint
8. Test events endpoint with authentication

### Frontend Deployment

1. Create ZIP package of Joomla module
2. Install via Joomla Extensions manager
3. Create new module instance
4. Configure API endpoint and key
5. Assign to menu items
6. Publish module
7. Clear Joomla cache
8. Test frontend display

### Post-Deployment

- [ ] Monitor logs for errors
- [ ] Check cache is working
- [ ] Verify cron jobs running
- [ ] Test all links
- [ ] Verify animations
- [ ] Performance testing
- [ ] Mobile testing

---

## MAINTENANCE

### Daily
- Monitor error logs
- Check API health

### Weekly
- Review performance metrics
- Check cache hit rate

### Monthly
- Update dependencies
- Review security logs
- Test backups
- Check SSL expiration

---

## TROUBLESHOOTING QUICK REFERENCE

**Problem:** API returns 500 error  
**Solution:** Check logs, verify Google credentials, restart app

**Problem:** Events not displaying  
**Solution:** Check browser console, verify API endpoint, test with curl

**Problem:** Slow loading  
**Solution:** Check cache, optimize queries, enable CDN

**Problem:** Animations janky  
**Solution:** Disable on low-end devices, use CSS transforms, lazy load

**Problem:** Token expired  
**Solution:** Run refresh script manually, verify cron job

---

## CRITICAL REQUIREMENTS SUMMARY

**Must Have:**
✅ JWT + API key authentication  
✅ HTTPS only  
✅ Caching (5-minute minimum)  
✅ Responsive design  
✅ All current features maintained  
✅ Modern design per theme.jpg  
✅ Error handling  
✅ Logging  

**Should Have:**
✅ SVG bowling animations  
✅ Rate limiting  
✅ Redis caching (file-based acceptable)  
✅ Admin cache clear  
✅ Monitoring/alerting  

**Nice to Have:**
⭕ Advanced animations  
⭕ Search/filter  
⭕ Export to iCal  
⭕ Multi-calendar support  
⭕ Real-time updates (websockets)  

---

## KEY CONTACTS & RESOURCES

**Google Calendar API:**
- Docs: https://developers.google.com/calendar
- Console: https://console.cloud.google.com
- Service Account Setup: Create in GCP Console

**Joomla:**
- Module Dev Docs: https://docs.joomla.org/
- Extensions Directory: https://extensions.joomla.org/

**cPanel:**
- Python App Setup: Check hosting provider docs
- Support: Via hosting provider

**Tools:**
- JWT Debugger: https://jwt.io
- API Testing: Postman or curl
- Performance: Chrome DevTools

---

## FILES TO CREATE

**Backend (9 files):**
1. `app/main.py` - Flask application
2. `app/config.py` - Configuration
3. `app/auth.py` - Authentication
4. `app/calendar_service.py` - Google Calendar
5. `app/cache.py` - Caching layer
6. `app/utils.py` - Utilities
7. `passenger_wsgi.py` - WSGI entry
8. `requirements.txt` - Dependencies
9. `.env.example` - Env template

**Frontend (11+ files):**
1. `mod_cps_calendar.php` - Entry
2. `mod_cps_calendar.xml` - Manifest
3. `helper.php` - Helper class
4. `tmpl/default.php` - Template
5. `media/css/calendar.css` - Styles
6. `media/js/calendar.js` - Logic
7. `media/js/animations.js` - Animations
8. `media/svg/bowling-pins.svg` - SVG
9. `media/svg/bowling-ball.svg` - SVG
10. `media/svg/pin-strike.svg` - SVG
11. `language/en-GB/en-GB.mod_cps_calendar.ini` - Translations
12. Plus: 4 image files (register.png, link.png, pattern.png, entry.png)

**Scripts (3 files):**
1. `scripts/warmup_cache.py` - Cache warmup
2. `scripts/refresh_token.py` - Token refresh
3. `scripts/rotate_logs.sh` - Log rotation

**Documentation (4 files):**
1. `README.md` - Project overview
2. `INSTALLATION.md` - Setup guide
3. `API.md` - API documentation
4. `TROUBLESHOOTING.md` - Common issues

**Total:** 27+ files

---

## ESTIMATED TIMELINE

```
Week 1: Backend Core (40 hours)
├── API setup (16h)
├── Google Calendar integration (12h)
├── Authentication (8h)
└── Initial testing (4h)

Week 2: Backend Complete (40 hours)
├── Caching (8h)
├── Security hardening (12h)
├── cPanel deployment (12h)
└── Testing & docs (8h)

Week 3: Frontend Core (40 hours)
├── Module structure (8h)
├── API integration (12h)
├── Basic display (12h)
└── Testing (8h)

Week 4: Frontend Design (40 hours)
├── CSS implementation (16h)
├── SVG creation (8h)
├── Animations (12h)
└── Polish & testing (4h)

Week 5: Integration & Testing (30 hours)
├── End-to-end testing (10h)
├── Security testing (8h)
├── UAT & bug fixes (12h)

Week 6: Deployment & Docs (30 hours)
├── Production deployment (12h)
├── Documentation (12h)
├── Training & handover (6h)

Total: ~220 hours over 6 weeks
```

---

## SUCCESS METRICS

After deployment, verify:

✅ **Functional:** All events display correctly  
✅ **Performance:** Page load < 2s, API < 500ms  
✅ **Security:** All endpoints authenticated, HTTPS enforced  
✅ **UX:** Animations smooth, mobile responsive  
✅ **Reliability:** 99.9% uptime, cache hit rate > 80%  

---

**For detailed specifications, see: PIVOT_SCOPE_OF_WORK.md**

---

**Quick Start Version 1.0** | Last Updated: October 30, 2025
