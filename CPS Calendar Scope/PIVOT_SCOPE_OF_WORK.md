# BOWLING CALENDAR SYSTEM - PIVOT SCOPE OF WORK
## Joomla Module Frontend + cPanel Python Backend Migration

**Project:** Corner Pin Standings - Bowling Tournament Calendar  
**Version:** 2.0  
**Date:** October 30, 2025  
**Status:** Professional Implementation Scope

---

## EXECUTIVE SUMMARY

This document outlines the complete scope of work for migrating the existing Ubuntu-based bowling tournament calendar system to a professional Joomla module architecture with a cPanel Python backend. The system will feature a modern, sophisticated design with bowling-themed SVG animations while maintaining all existing functionality with enhanced security and scalability.

---

## 1. CURRENT ARCHITECTURE ANALYSIS

### 1.1 Existing System Components

**Python Application (cps_calendar.py)**
- **Runtime Environment:** Ubuntu server with continuous execution
- **Update Frequency:** 15-second polling loop
- **Google Calendar Integration:** OAuth 2.0 authentication
- **Output Method:** Static HTML generation via FTP upload
- **Calendar Source:** tyson@cornerpins.com.au

**Core Functionality:**
- Real-time Google Calendar event synchronization
- Color-coded event display based on Google Calendar colors
- Automatic luminance calculation for text contrast
- Location extraction and Google Maps integration
- Hyperlink extraction from event descriptions
- TenpinResults URL detection and icon display
- Attachment handling with custom icons (pattern.png, entry.png, register.png, link.png)
- Month/year grouping with visual separators
- Responsive design (mobile/desktop breakpoints)
- Popup blocker warning system with animated banner

**Security Considerations:**
- Credentials stored in plaintext files (credentials.json, credentials, token.pickle)
- FTP credentials in unencrypted file
- No access controls or authentication
- Direct file system access

**Dependencies:**
```
google-auth-oauthlib
google-api-python-client
google-auth
python-dateutil
ftplib (standard library)
```

---

## 2. TARGET ARCHITECTURE

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      JOOMLA CMS (Frontend)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Custom Joomla Module: mod_cps_calendar         │ │
│  │  - AJAX-based calendar display                         │ │
│  │  - SVG bowling animations                              │ │
│  │  - Responsive design                                   │ │
│  │  - Caching layer                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↕ REST API (JSON)
┌─────────────────────────────────────────────────────────────┐
│              cPanel Python Application (Backend)             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Python WSGI Application (Flask/FastAPI)        │ │
│  │  - RESTful API endpoints                               │ │
│  │  - Google Calendar service                             │ │
│  │  - Redis caching layer                                 │ │
│  │  - JWT authentication                                  │ │
│  │  - Rate limiting                                       │ │
│  │  - Logging & monitoring                                │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Scheduled Task (cron via cPanel)               │ │
│  │  - Periodic cache warmup (every 5 minutes)             │ │
│  │  - Token refresh management                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↕ OAuth 2.0
┌─────────────────────────────────────────────────────────────┐
│                    Google Calendar API                       │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

**Frontend (Joomla Module):**
- Joomla 4.x/5.x compatible module
- PHP 8.1+
- JavaScript (ES6+) with async/await
- SVG animations (GSAP or native CSS animations)
- CSS3 with custom properties
- AJAX for dynamic content loading

**Backend (cPanel Python):**
- Python 3.9+ with WSGI (Flask or FastAPI)
- Redis for caching (or file-based alternative)
- Google Calendar API v3
- JWT for API authentication
- Environment-based configuration
- Structured logging

**Infrastructure:**
- cPanel with Python application support
- SSL/TLS certificates (Let's Encrypt)
- Scheduled tasks via cPanel cron
- Secure credential storage (environment variables or encrypted)

---

## 3. SECURITY REQUIREMENTS

### 3.1 Authentication & Authorization

**API Security:**
- ✅ JWT-based authentication for all API requests
- ✅ API key rotation capability
- ✅ IP whitelisting option for production
- ✅ Rate limiting per IP/API key (100 requests/hour default)
- ✅ CORS configuration (restricted to Joomla domain)

**Google OAuth 2.0:**
- ✅ Service account credentials (preferred) or OAuth 2.0 flow
- ✅ Encrypted credential storage
- ✅ Automatic token refresh with error handling
- ✅ Scoped permissions (calendar.readonly only)

**Joomla Integration:**
- ✅ Module access control via Joomla ACL
- ✅ XSS prevention (input sanitization)
- ✅ CSRF token validation
- ✅ SQL injection prevention (parameterized queries if applicable)

### 3.2 Data Protection

**Credentials Management:**
- ✅ Environment variables for all sensitive data
- ✅ No plaintext credentials in code or config files
- ✅ Separate credentials for dev/staging/production
- ✅ Credential rotation documentation

**Transport Security:**
- ✅ HTTPS-only communication (enforce)
- ✅ TLS 1.2+ minimum
- ✅ Secure headers (HSTS, CSP, X-Frame-Options)

**Data Handling:**
- ✅ No sensitive data logging
- ✅ Cache encryption (if Redis used)
- ✅ Secure session management
- ✅ Input validation and sanitization

### 3.3 Infrastructure Security

**cPanel Configuration:**
- ✅ Restricted file permissions (644 files, 755 directories)
- ✅ Python application isolation
- ✅ Disable directory listing
- ✅ Custom error pages (no information disclosure)

**Logging & Monitoring:**
- ✅ Structured logging with rotation
- ✅ Error tracking (with sensitive data redaction)
- ✅ Security event logging
- ✅ Monitoring for unauthorized access attempts

---

## 4. FUNCTIONAL REQUIREMENTS

### 4.1 Core Features (Must Maintain)

**Calendar Event Display:**
- [x] Fetch events from Google Calendar (tyson@cornerpins.com.au)
- [x] Display future events only (from current date/time forward)
- [x] Group events by month/year with visual separators
- [x] Color-coded events based on Google Calendar color IDs
- [x] Automatic text color contrast (light/dark) based on background luminance
- [x] Date range display (start to end, or single date)
- [x] Event title with link to Google Calendar event
- [x] Location with Google Maps integration
- [x] Multi-day event support

**Event Metadata Processing:**
- [x] Extract first location component (before first comma)
- [x] Parse hyperlinks from event descriptions
- [x] Identify TenpinResults URLs with custom icon
- [x] Display other URLs with generic link icon
- [x] Process attachments with custom icons:
  - Pattern files → pattern.png icon
  - Other files → entry.png icon
- [x] Handle events without locations gracefully

**User Interface:**
- [x] Responsive design (mobile and desktop)
- [x] Grid layout on desktop (4 columns: date, title, location, actions)
- [x] Stacked layout on mobile
- [x] Click-through links with popup warning
- [x] Animated redirect banner for popup blockers
- [x] Icon-based action buttons

**Performance:**
- [x] Efficient pagination handling (nextPageToken support)
- [x] Cache calendar data (5-minute cache recommended)
- [x] Lazy loading for long lists (optional enhancement)

### 4.2 New Features (Enhancements)

**Modern UI/UX:**
- [x] Bowling-themed SVG animations
  - Animated bowling pins on page load
  - Rolling bowling ball cursor trail (subtle)
  - Pin strike animation for month transitions
  - Smooth fade-in animations for events
- [x] Dark theme with purple/cyan accents (per theme.jpg)
- [x] Card-based event layout with hover effects
- [x] Smooth transitions and micro-interactions
- [x] Loading skeleton states
- [x] Empty state messaging (no upcoming events)

**Enhanced Functionality:**
- [x] Filter events by month (dropdown or tabs)
- [x] Search/filter by event name or location
- [x] Export to iCal option
- [x] "Add to my calendar" quick action
- [x] Countdown timer for next event
- [x] Past events view (toggle/separate page)

**Admin Features:**
- [x] Joomla module configuration options:
  - Calendar ID selection
  - Cache duration setting
  - Display options (show/hide icons, colors, etc.)
  - Animation toggle (enable/disable)
  - Custom CSS override field
- [x] Backend health check endpoint
- [x] Manual cache clear action

---

## 5. DESIGN REQUIREMENTS

### 5.1 Visual Design (Based on theme.jpg)

**Color Palette:**
```css
Primary Background: #2d3e50 (dark navy/charcoal)
Secondary Background: #3a4f63 (lighter navy for cards)
Primary Accent: #8B7BC4 (purple - headings)
Secondary Accent: #4ecdc4 (cyan/turquoise - subheadings)
Text Primary: #ffffff (white)
Text Secondary: #b0b8c1 (light gray)
Card Background: #34495e (dark cards)
Border/Divider: #4a5f7a (subtle borders)
Success/Action: #33d9b2 (green for actions)
Warning/Alert: #ff6b6b (red for alerts)
```

**Typography:**
- **Primary Font:** "Ubuntu", "Segoe UI", Arial, sans-serif
- **Heading Font:** "Montserrat" or "Poppins" (bold, modern)
- **Size Scale:** 
  - H1 (What's On): 3rem (48px)
  - H2 (Month): 2rem (32px)
  - Event Title: 1.25rem (20px)
  - Body: 1rem (16px)
  - Metadata: 0.875rem (14px)

**Layout:**
- Maximum content width: 1400px
- Card spacing: 16px margin
- Border radius: 12px for cards
- Event cards: Dark background with subtle shadow
- Date badges: Purple background, rounded corners
- Logo badges: Circular or rounded square containers

### 5.2 SVG Animations

**Bowling Pin Background:**
- Line art bowling pins (outline only) in header
- Subtle parallax effect on scroll
- Fade-in animation on page load (0.8s ease-in-out)

**Bowling Ball Animation:**
- Small animated bowling ball (24x24px)
- Rolls across screen on month change
- Optional: cursor trail effect (performance optimized)

**Strike Animation:**
- Pins falling animation when transitioning months
- Duration: 1.2s
- Easing: cubic-bezier(0.68, -0.55, 0.265, 1.55)

**Event Card Animations:**
- Staggered fade-in on load (0.3s delay per card)
- Hover: Scale 1.02 + shadow increase
- Click: Ripple effect

**Loading States:**
- Skeleton cards with shimmer effect
- Spinning bowling ball loader

### 5.3 Responsive Design

**Breakpoints:**
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

**Desktop Layout:**
```
┌─────────────────────────────────────────────────┐
│  Header: "WHAT'S ON" + Bowling Decorations     │
├─────────────────────────────────────────────────┤
│  [November 2026]                                │
│  ┌──────────┬─────────┬──────────┬──────────┐  │
│  │  Date    │ Title   │ Location │ Actions  │  │
│  ├──────────┼─────────┼──────────┼──────────┤  │
│  │ 21-22 Nov│ Event 1 │ Venue A  │ [icons]  │  │
│  │ 29 Nov   │ Event 2 │ Venue B  │ [icons]  │  │
│  └──────────┴─────────┴──────────┴──────────┘  │
│                                                 │
│  [December 2026]                                │
│  [Event cards continue...]                      │
└─────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌──────────────────┐
│  WHAT'S ON       │
│  [Bowling Pins]  │
├──────────────────┤
│ [November 2026]  │
│ ┌──────────────┐ │
│ │ 21-22 Nov    │ │
│ │ Event Title  │ │
│ │ Venue Name   │ │
│ │ [Icons Row]  │ │
│ └──────────────┘ │
│ ┌──────────────┐ │
│ │ [Event 2]    │ │
│ └──────────────┘ │
└──────────────────┘
```

---

## 6. TECHNICAL SPECIFICATIONS

### 6.1 Joomla Module Structure

**Directory Structure:**
```
mod_cps_calendar/
├── mod_cps_calendar.php          # Entry point
├── mod_cps_calendar.xml          # Manifest file
├── helper.php                    # Helper class
├── tmpl/
│   └── default.php               # Display template
├── language/
│   └── en-GB/
│       └── en-GB.mod_cps_calendar.ini
├── media/
│   ├── css/
│   │   ├── calendar.css          # Main styles
│   │   └── calendar.min.css      # Minified
│   ├── js/
│   │   ├── calendar.js           # Main JavaScript
│   │   ├── calendar.min.js       # Minified
│   │   └── animations.js         # SVG animations
│   ├── images/
│   │   ├── register.png
│   │   ├── link.png
│   │   ├── pattern.png
│   │   ├── entry.png
│   │   └── bowling-pins.svg      # Background decoration
│   └── svg/
│       ├── bowling-ball.svg
│       ├── pin-strike.svg
│       └── loader.svg
└── sql/
    └── install.mysql.utf8.sql    # Optional DB table for settings
```

**Module XML Configuration (mod_cps_calendar.xml):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<extension type="module" version="4.0" client="site" method="upgrade">
    <name>CPS Bowling Calendar</name>
    <author>Corner Pin Standings</author>
    <version>2.0.0</version>
    <description>MOD_CPS_CALENDAR_XML_DESCRIPTION</description>
    
    <files>
        <filename module="mod_cps_calendar">mod_cps_calendar.php</filename>
        <filename>helper.php</filename>
        <folder>tmpl</folder>
        <folder>language</folder>
    </files>
    
    <media destination="mod_cps_calendar" folder="media">
        <folder>css</folder>
        <folder>js</folder>
        <folder>images</folder>
        <folder>svg</folder>
    </media>
    
    <config>
        <fields name="params">
            <fieldset name="basic">
                <field name="api_endpoint" type="text" 
                       label="MOD_CPS_CALENDAR_API_ENDPOINT_LABEL"
                       description="MOD_CPS_CALENDAR_API_ENDPOINT_DESC"
                       default="https://yourdomain.com/cps-api" />
                
                <field name="api_key" type="password"
                       label="MOD_CPS_CALENDAR_API_KEY_LABEL"
                       description="MOD_CPS_CALENDAR_API_KEY_DESC" />
                
                <field name="cache_duration" type="number"
                       label="MOD_CPS_CALENDAR_CACHE_DURATION_LABEL"
                       description="MOD_CPS_CALENDAR_CACHE_DURATION_DESC"
                       default="300" />
                
                <field name="enable_animations" type="radio"
                       label="MOD_CPS_CALENDAR_ENABLE_ANIMATIONS_LABEL"
                       default="1">
                    <option value="0">JNO</option>
                    <option value="1">JYES</option>
                </field>
                
                <field name="show_past_events" type="radio"
                       label="MOD_CPS_CALENDAR_SHOW_PAST_EVENTS_LABEL"
                       default="0">
                    <option value="0">JNO</option>
                    <option value="1">JYES</option>
                </field>
                
                <field name="events_per_page" type="number"
                       label="MOD_CPS_CALENDAR_EVENTS_PER_PAGE_LABEL"
                       default="50" />
                
                <field name="custom_css" type="textarea"
                       label="MOD_CPS_CALENDAR_CUSTOM_CSS_LABEL"
                       rows="10" cols="50" />
            </fieldset>
            
            <fieldset name="advanced">
                <field name="moduleclass_sfx" type="textarea"
                       label="COM_MODULES_FIELD_MODULECLASS_SFX_LABEL" />
                
                <field name="cache" type="list"
                       label="COM_MODULES_FIELD_CACHING_LABEL"
                       default="1">
                    <option value="0">COM_MODULES_FIELD_VALUE_NOCACHING</option>
                    <option value="1">COM_MODULES_FIELD_VALUE_USEGLOBAL</option>
                </field>
            </fieldset>
        </fields>
    </config>
</extension>
```

**Helper Class Methods:**
```php
class ModCpsCalendarHelper
{
    public static function getEvents($params)
    public static function makeApiRequest($endpoint, $apiKey)
    public static function getCachedEvents($cacheKey, $duration)
    public static function setCachedEvents($cacheKey, $data, $duration)
    public static function formatDate($dateString)
    public static function extractLocation($location)
    public static function calculateTextColor($backgroundColor)
    public static function sanitizeOutput($html)
}
```

### 6.2 Python Backend Application

**Directory Structure:**
```
cps-calendar-api/
├── app/
│   ├── __init__.py
│   ├── main.py                   # WSGI entry point
│   ├── config.py                 # Configuration management
│   ├── auth.py                   # JWT authentication
│   ├── calendar_service.py       # Google Calendar integration
│   ├── cache.py                  # Caching layer
│   ├── models.py                 # Data models
│   └── utils.py                  # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_calendar.py
│   └── test_api.py
├── .env.example                  # Environment template
├── .gitignore
├── requirements.txt
├── passenger_wsgi.py             # cPanel WSGI entry
└── README.md
```

**API Endpoints:**

```
GET  /api/v1/health
     Response: {"status": "ok", "version": "2.0.0"}
     
GET  /api/v1/events
     Query Params:
       - from_date (ISO 8601, optional)
       - to_date (ISO 8601, optional)
       - include_past (boolean, default: false)
       - limit (integer, default: 100, max: 500)
     Headers:
       - Authorization: Bearer {JWT_TOKEN}
       - X-API-Key: {API_KEY}
     Response: {
       "success": true,
       "data": [
         {
           "id": "event_id",
           "summary": "Event Title",
           "start": {"date": "2026-11-21", "dateTime": null, "timeZone": "Australia/Brisbane"},
           "end": {"date": "2026-11-22", "dateTime": null, "timeZone": "Australia/Brisbane"},
           "location": "Caboolture Bowl & Mini Golf",
           "description": "Event description...",
           "htmlLink": "https://calendar.google.com/...",
           "colorId": "11",
           "backgroundColor": "#d60000",
           "textColor": "#ffffff",
           "attachments": [
             {
               "fileUrl": "https://...",
               "title": "Entry Form",
               "iconType": "entry"
             }
           ],
           "urls": {
             "tenpinResults": "https://tenpinresults.com/...",
             "other": "https://example.com/..."
           }
         }
       ],
       "meta": {
         "count": 25,
         "cached": true,
         "cacheAge": 120
       }
     }

GET  /api/v1/colors
     Response: {
       "success": true,
       "data": {
         "1": "#7986cb",
         "2": "#33b679",
         ...
       }
     }

POST /api/v1/cache/clear
     Headers:
       - Authorization: Bearer {ADMIN_JWT_TOKEN}
     Response: {"success": true, "message": "Cache cleared"}

GET  /api/v1/stats
     Response: {
       "uptime": 86400,
       "requestCount": 1250,
       "cacheHitRate": 0.87,
       "lastSync": "2025-10-30T14:30:00Z"
     }
```

**Core Python Files:**

**main.py (Flask/FastAPI Application):**
```python
from flask import Flask, jsonify, request
from flask_cors import CORS
from app.config import Config
from app.auth import require_auth
from app.calendar_service import CalendarService
from app.cache import CacheManager
import logging

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.ALLOWED_ORIGINS)

# Initialize services
calendar_service = CalendarService()
cache_manager = CacheManager()

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "version": "2.0.0"})

@app.route('/api/v1/events', methods=['GET'])
@require_auth
def get_events():
    # Implementation details
    pass

# Additional endpoints...

if __name__ == '__main__':
    app.run()
```

**config.py:**
```python
import os
from datetime import timedelta

class Config:
    # Environment
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = ENV == 'development'
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET = os.getenv('JWT_SECRET')
    JWT_EXPIRATION = timedelta(hours=1)
    API_KEY = os.getenv('API_KEY')
    
    # Google Calendar
    CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
    GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')
    SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
    
    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'file')  # 'redis' or 'file'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    CACHE_DIR = os.getenv('CACHE_DIR', '/tmp/cps_cache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))
    
    # CORS
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'https://yourdomain.com').split(',')
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 3600))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/home/username/logs/cps_api.log')
```

**calendar_service.py:**
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone
import logging

class CalendarService:
    def __init__(self):
        self.credentials = self._load_credentials()
        self.service = build('calendar', 'v3', credentials=self.credentials)
        
    def _load_credentials(self):
        # Service account authentication
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            Config.SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return credentials
    
    def get_events(self, from_date=None, to_date=None, max_results=100):
        """Fetch events from Google Calendar"""
        try:
            time_min = from_date or datetime.now(timezone.utc).isoformat()
            
            events_result = self.service.events().list(
                calendarId=Config.CALENDAR_ID,
                timeMin=time_min,
                timeMax=to_date,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return self._process_events(events)
            
        except Exception as e:
            logging.error(f"Error fetching calendar events: {str(e)}")
            raise
    
    def _process_events(self, events):
        """Process and enrich event data"""
        processed = []
        colors = self._get_color_mapping()
        
        for event in events:
            processed_event = {
                'id': event.get('id'),
                'summary': event.get('summary', 'No Title'),
                'start': event.get('start'),
                'end': event.get('end'),
                'location': self._extract_location(event.get('location')),
                'description': event.get('description', ''),
                'htmlLink': event.get('htmlLink'),
                'colorId': event.get('colorId', 'undefined'),
            }
            
            # Add color
            color_id = processed_event['colorId']
            bg_color = colors.get(color_id, colors['undefined'])
            processed_event['backgroundColor'] = bg_color
            processed_event['textColor'] = self._calculate_text_color(bg_color)
            
            # Extract URLs
            urls = self._extract_urls(processed_event['description'])
            processed_event['urls'] = urls
            
            # Process attachments
            if 'attachments' in event:
                processed_event['attachments'] = self._process_attachments(event['attachments'])
            
            processed.append(processed_event)
        
        return processed
    
    def _get_color_mapping(self):
        return {
            'undefined': '#039be5',
            '1': '#7986cb',
            '2': '#33b679',
            '3': '#8e24aa',
            '4': '#e67c73',
            '5': '#f6c026',
            '6': '#f5511d',
            '7': '#039be5',
            '8': '#616161',
            '9': '#3f51b5',
            '10': '#0b8043',
            '11': '#d60000',
        }
    
    # Additional helper methods...
```

**cache.py:**
```python
import redis
import json
import os
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self):
        if Config.CACHE_TYPE == 'redis':
            self.backend = RedisCache()
        else:
            self.backend = FileCache()
    
    def get(self, key):
        return self.backend.get(key)
    
    def set(self, key, value, timeout=None):
        timeout = timeout or Config.CACHE_DEFAULT_TIMEOUT
        return self.backend.set(key, value, timeout)
    
    def delete(self, key):
        return self.backend.delete(key)
    
    def clear(self):
        return self.backend.clear()

class RedisCache:
    def __init__(self):
        self.client = redis.from_url(Config.CACHE_REDIS_URL)
    
    def get(self, key):
        value = self.client.get(key)
        return json.loads(value) if value else None
    
    def set(self, key, value, timeout):
        return self.client.setex(key, timeout, json.dumps(value))
    
    def delete(self, key):
        return self.client.delete(key)
    
    def clear(self):
        return self.client.flushdb()

class FileCache:
    def __init__(self):
        self.cache_dir = Config.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
    
    # File-based cache implementation...
```

**requirements.txt:**
```
Flask==3.0.0
Flask-CORS==4.0.0
google-auth==2.25.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.110.0
PyJWT==2.8.0
python-dateutil==2.8.2
redis==5.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
```

**passenger_wsgi.py (cPanel WSGI Entry):**
```python
import sys
import os

# Add application directory to system path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Flask application
from app.main import app as application
```

### 6.3 cPanel Configuration

**Python Application Setup:**

1. **Create Python Application in cPanel:**
   - Python Version: 3.9+
   - Application Root: `/home/username/cps-calendar-api`
   - Application URL: `/cps-api` or subdomain `api.yourdomain.com`
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`

2. **Environment Variables (via cPanel):**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key-here
   JWT_SECRET=your-jwt-secret-here
   API_KEY=your-api-key-here
   GOOGLE_CALENDAR_ID=tyson@cornerpins.com.au
   SERVICE_ACCOUNT_FILE=/home/username/cps-calendar-api/service-account.json
   CACHE_TYPE=file
   CACHE_DIR=/home/username/cps-calendar-api/cache
   CACHE_TIMEOUT=300
   ALLOWED_ORIGINS=https://yourdomain.com
   LOG_FILE=/home/username/logs/cps_api.log
   RATE_LIMIT_ENABLED=true
   ```

3. **Scheduled Tasks (Cron Jobs):**
   ```bash
   # Cache warmup every 5 minutes
   */5 * * * * /home/username/cps-calendar-api/venv/bin/python /home/username/cps-calendar-api/scripts/warmup_cache.py

   # Token refresh check every hour
   0 * * * * /home/username/cps-calendar-api/venv/bin/python /home/username/cps-calendar-api/scripts/refresh_token.py

   # Log rotation daily
   0 0 * * * /home/username/cps-calendar-api/scripts/rotate_logs.sh
   ```

4. **File Permissions:**
   ```bash
   chmod 644 *.py
   chmod 755 scripts/
   chmod 700 service-account.json
   chmod 755 cache/
   chmod 755 logs/
   ```

---

## 7. IMPLEMENTATION PHASES

### Phase 1: Backend Development (Week 1-2)

**Week 1: Core API Development**
- [ ] Set up cPanel Python application environment
- [ ] Create project structure and virtual environment
- [ ] Implement configuration management with environment variables
- [ ] Develop Google Calendar service integration
  - [ ] Service account authentication
  - [ ] Event fetching with pagination
  - [ ] Event data processing and enrichment
  - [ ] Error handling and retry logic
- [ ] Implement caching layer (file-based initially)
- [ ] Create RESTful API endpoints:
  - [ ] /health endpoint
  - [ ] /events endpoint with query parameters
  - [ ] /colors endpoint
- [ ] Set up logging infrastructure

**Week 2: Security & Optimization**
- [ ] Implement JWT authentication
- [ ] Add API key validation
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Add input validation and sanitization
- [ ] Create cache warmup script
- [ ] Create token refresh script
- [ ] Write unit tests for core functionality
- [ ] Performance testing and optimization
- [ ] Set up cron jobs
- [ ] Deploy to cPanel staging environment

**Deliverables:**
- Fully functional Python API
- API documentation (Swagger/OpenAPI)
- Deployment scripts
- Environment configuration template
- Test coverage report

### Phase 2: Frontend Development (Week 3-4)

**Week 3: Joomla Module Core**
- [ ] Create Joomla module structure
- [ ] Develop module manifest (XML)
- [ ] Implement helper class:
  - [ ] API communication methods
  - [ ] Caching integration
  - [ ] Data transformation
  - [ ] Security functions
- [ ] Create module template (default.php)
- [ ] Implement basic event display (no styling)
- [ ] Add module configuration options
- [ ] Integrate with backend API
- [ ] Test in Joomla 4.x and 5.x

**Week 4: Design & Animations**
- [ ] Implement CSS design per theme.jpg
  - [ ] Color scheme and typography
  - [ ] Responsive layouts
  - [ ] Card designs
  - [ ] Date badges
- [ ] Create SVG assets:
  - [ ] Bowling pins background
  - [ ] Bowling ball animation
  - [ ] Strike animation
  - [ ] Loading spinner
- [ ] Implement JavaScript functionality:
  - [ ] AJAX event loading
  - [ ] Infinite scroll / pagination
  - [ ] Filter and search
  - [ ] Animation triggers
- [ ] Add bowling-themed animations:
  - [ ] Page load animations
  - [ ] Month transition effects
  - [ ] Hover interactions
  - [ ] Loading states
- [ ] Optimize for performance:
  - [ ] Minify CSS/JS
  - [ ] Lazy load images
  - [ ] Debounce scroll events
- [ ] Cross-browser testing
- [ ] Mobile responsiveness testing

**Deliverables:**
- Installable Joomla module package
- Module documentation
- User guide
- Admin configuration guide

### Phase 3: Integration & Testing (Week 5)

**Integration Testing:**
- [ ] End-to-end workflow testing
- [ ] API-to-frontend integration verification
- [ ] Cache behavior testing
- [ ] Authentication flow testing
- [ ] Error handling scenarios
- [ ] Performance benchmarking
  - [ ] Page load times < 2s
  - [ ] API response times < 500ms
  - [ ] Animation frame rates > 30fps

**Security Testing:**
- [ ] Penetration testing (OWASP Top 10)
- [ ] XSS vulnerability scanning
- [ ] SQL injection testing (if applicable)
- [ ] CSRF token validation
- [ ] API authentication bypass attempts
- [ ] Rate limiting effectiveness
- [ ] Credential exposure checks

**User Acceptance Testing:**
- [ ] Admin configuration workflow
- [ ] Event display accuracy
- [ ] Link functionality (Google Calendar, Maps, attachments)
- [ ] Responsive design on real devices
- [ ] Animation performance on low-end devices
- [ ] Browser compatibility (Chrome, Firefox, Safari, Edge)

**Bug Fixes & Refinements:**
- [ ] Address all critical and high-priority bugs
- [ ] Performance optimizations
- [ ] UX improvements based on testing feedback

**Deliverables:**
- Test reports
- Bug tracking documentation
- Performance benchmarks
- Security audit report

### Phase 4: Deployment & Documentation (Week 6)

**Production Deployment:**
- [ ] Set up production environment on cPanel
- [ ] Configure environment variables
- [ ] Deploy Python API to production
- [ ] Install SSL certificate
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Create production cron jobs
- [ ] Deploy Joomla module to production site
- [ ] Configure module settings
- [ ] Verify all integrations

**Documentation:**
- [ ] **Technical Documentation:**
  - [ ] Architecture overview
  - [ ] API reference documentation
  - [ ] Code documentation (inline and external)
  - [ ] Database schema (if applicable)
  - [ ] Security protocols
- [ ] **Deployment Guide:**
  - [ ] cPanel setup instructions
  - [ ] Python environment configuration
  - [ ] Joomla module installation
  - [ ] Configuration checklist
  - [ ] Troubleshooting guide
- [ ] **User Guide:**
  - [ ] Module configuration options
  - [ ] Content management best practices
  - [ ] FAQ section
- [ ] **Maintenance Guide:**
  - [ ] Update procedures
  - [ ] Backup strategies
  - [ ] Monitoring and logging
  - [ ] Troubleshooting common issues

**Training:**
- [ ] Admin training session (if required)
- [ ] Walkthrough video creation
- [ ] Support contact establishment

**Deliverables:**
- Live production system
- Complete documentation suite
- Backup and rollback plan
- Support and maintenance plan

---

## 8. TESTING REQUIREMENTS

### 8.1 Unit Testing

**Backend (Python):**
- Google Calendar service methods
- Cache operations
- Authentication functions
- Data processing utilities
- API endpoint logic
- Error handling scenarios

**Frontend (JavaScript):**
- API communication functions
- Data transformation
- Animation trigger logic
- Event handling

**Target Coverage:** 80%+ code coverage

### 8.2 Integration Testing

- API endpoint responses
- Joomla module to API communication
- Cache integration
- Error propagation and handling
- OAuth token refresh flow

### 8.3 Performance Testing

**Metrics to Test:**
- API response time < 500ms (cached)
- API response time < 2s (uncached)
- Page load time < 2s
- First contentful paint < 1s
- Animation frame rate > 30fps
- Time to interactive < 3s

**Load Testing:**
- 100 concurrent users
- 1000 requests/minute
- Cache hit rate > 80%

### 8.4 Security Testing

**OWASP Top 10 Coverage:**
1. Injection attacks (XSS, SQL if applicable)
2. Broken authentication
3. Sensitive data exposure
4. XML external entities (if applicable)
5. Broken access control
6. Security misconfiguration
7. Cross-site scripting (XSS)
8. Insecure deserialization
9. Using components with known vulnerabilities
10. Insufficient logging and monitoring

**Additional Security Tests:**
- CSRF protection
- CORS policy validation
- Rate limiting effectiveness
- API key security
- Credential storage security
- HTTPS enforcement

### 8.5 Compatibility Testing

**Browsers:**
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

**Devices:**
- Desktop (1920x1080, 1366x768)
- Tablet (iPad, Android tablets)
- Mobile (iPhone, Android phones)

**Joomla Versions:**
- Joomla 4.x (latest stable)
- Joomla 5.x (latest stable)

**PHP Versions:**
- PHP 8.1
- PHP 8.2
- PHP 8.3

---

## 9. DEPLOYMENT INSTRUCTIONS

### 9.1 Pre-Deployment Checklist

**Infrastructure:**
- [ ] cPanel access credentials
- [ ] SSH access (if available)
- [ ] Domain name and SSL certificate
- [ ] Sufficient disk space (2GB minimum)
- [ ] Python 3.9+ support verified
- [ ] Redis available (optional, for caching)

**Credentials & Keys:**
- [ ] Google Calendar Service Account JSON file
- [ ] API secret keys generated
- [ ] JWT secret generated
- [ ] Database credentials (if using database for cache)

**Code Preparation:**
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Version tagged in Git
- [ ] CSS/JS minified
- [ ] Production configuration prepared
- [ ] Documentation complete

### 9.2 Backend Deployment Steps

**Step 1: Prepare cPanel Environment**
```bash
# Log into cPanel
# Navigate to: Setup Python App

# Create new Python application:
App Name: CPS Calendar API
Python Version: 3.9 (or latest available)
App Root: /home/username/cps-calendar-api
App URL: Choose subdomain (api.yourdomain.com) or path (/cps-api)
App startup file: passenger_wsgi.py
App Entry point: application
```

**Step 2: Upload Application Files**
```bash
# Via SSH or File Manager, upload:
/home/username/cps-calendar-api/
├── app/
├── scripts/
├── tests/
├── passenger_wsgi.py
├── requirements.txt
├── .env.example
└── README.md

# Create required directories:
mkdir -p /home/username/cps-calendar-api/cache
mkdir -p /home/username/cps-calendar-api/logs
chmod 755 cache/ logs/
```

**Step 3: Install Dependencies**
```bash
# Activate virtual environment (cPanel automatically creates this)
source /home/username/virtualenv/cps-calendar-api/3.9/bin/activate

# Install requirements
cd /home/username/cps-calendar-api
pip install -r requirements.txt
```

**Step 4: Configure Environment Variables**
```bash
# In cPanel Python App interface, add environment variables:
# Or create .env file (ensure it's not web-accessible):

FLASK_ENV=production
SECRET_KEY=<generate strong key>
JWT_SECRET=<generate strong key>
API_KEY=<generate strong key>
GOOGLE_CALENDAR_ID=tyson@cornerpins.com.au
SERVICE_ACCOUNT_FILE=/home/username/cps-calendar-api/service-account.json
CACHE_TYPE=file
CACHE_DIR=/home/username/cps-calendar-api/cache
CACHE_TIMEOUT=300
ALLOWED_ORIGINS=https://yourdomain.com
LOG_FILE=/home/username/cps-calendar-api/logs/api.log
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600
```

**Step 5: Upload Google Service Account**
```bash
# Upload service-account.json to:
/home/username/cps-calendar-api/service-account.json

# Set strict permissions:
chmod 600 /home/username/cps-calendar-api/service-account.json
```

**Step 6: Configure SSL**
```bash
# In cPanel SSL/TLS:
# - Install Let's Encrypt certificate for api subdomain
# - Force HTTPS redirect
```

**Step 7: Set Up Cron Jobs**
```bash
# In cPanel > Cron Jobs, add:

# Cache warmup (every 5 minutes)
*/5 * * * * source /home/username/virtualenv/cps-calendar-api/3.9/bin/activate && python /home/username/cps-calendar-api/scripts/warmup_cache.py >> /home/username/cps-calendar-api/logs/cron.log 2>&1

# Token refresh (hourly)
0 * * * * source /home/username/virtualenv/cps-calendar-api/3.9/bin/activate && python /home/username/cps-calendar-api/scripts/refresh_token.py >> /home/username/cps-calendar-api/logs/cron.log 2>&1

# Log rotation (daily at midnight)
0 0 * * * /home/username/cps-calendar-api/scripts/rotate_logs.sh
```

**Step 8: Start Application**
```bash
# In cPanel Python App interface:
# Click "Restart" or "Start" button

# Verify application is running:
curl https://api.yourdomain.com/api/v1/health

# Expected response:
# {"status": "ok", "version": "2.0.0"}
```

**Step 9: Test API Endpoints**
```bash
# Test events endpoint (with authentication):
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "X-API-Key: YOUR_API_KEY" \
     https://api.yourdomain.com/api/v1/events

# Verify response contains event data
```

### 9.3 Frontend Deployment Steps

**Step 1: Prepare Joomla Module Package**
```bash
# Create installable ZIP:
cd mod_cps_calendar/
zip -r mod_cps_calendar_v2.0.0.zip *

# Verify package contains:
# - mod_cps_calendar.php
# - mod_cps_calendar.xml
# - helper.php
# - tmpl/
# - media/
# - language/
```

**Step 2: Install Module in Joomla**
```
1. Log into Joomla Administrator
2. Navigate to: System > Install > Extensions
3. Upload mod_cps_calendar_v2.0.0.zip
4. Click "Install"
5. Verify success message
```

**Step 3: Configure Module**
```
1. Navigate to: Content > Site Modules
2. Click "New"
3. Select "CPS Bowling Calendar"
4. Configure settings:
   - Title: "What's On - Bowling Tournaments"
   - Position: Choose appropriate position
   - Status: Published
   - Access: Public
   
5. In "Module" tab:
   - API Endpoint: https://api.yourdomain.com/cps-api
   - API Key: [enter API key from backend]
   - Cache Duration: 300 (seconds)
   - Enable Animations: Yes
   - Show Past Events: No
   - Events Per Page: 50

6. In "Menu Assignment" tab:
   - Select pages where module should appear

7. Click "Save & Close"
```

**Step 4: Verify Frontend Display**
```
1. Navigate to public page where module is displayed
2. Verify:
   - Events are loading
   - Styling matches theme
   - Animations are working
   - Links are functional
   - Responsive design works on mobile
```

**Step 5: Performance Optimization**
```
1. Enable Joomla caching:
   System > Global Configuration > System > Cache
   Cache: ON
   Cache Handler: File
   
2. Enable Gzip compression:
   System > Global Configuration > Server > Server Settings
   Gzip Page Compression: Yes

3. Optimize images:
   - Ensure all PNG icons are compressed
   - Use SVG for vector graphics
```

### 9.4 Post-Deployment Verification

**Health Checks:**
- [ ] API health endpoint responds
- [ ] Events API returns data
- [ ] Joomla module displays events
- [ ] All links are functional
- [ ] Animations are smooth
- [ ] Mobile layout is correct
- [ ] SSL certificate is valid
- [ ] HTTPS redirect works
- [ ] Cron jobs are running
- [ ] Logs are being written
- [ ] Cache is working (check cache hit rate)

**Performance Verification:**
- [ ] Page load time < 2 seconds
- [ ] API response time < 500ms (cached)
- [ ] No JavaScript errors in console
- [ ] No CSS rendering issues
- [ ] Animations run at 60fps

**Security Verification:**
- [ ] API requires authentication
- [ ] CORS is properly configured
- [ ] Rate limiting is working
- [ ] No sensitive data in logs
- [ ] Service account file has correct permissions
- [ ] Environment variables are not exposed

---

## 10. MAINTENANCE & SUPPORT

### 10.1 Regular Maintenance Tasks

**Daily:**
- Monitor error logs for issues
- Check API health endpoint
- Verify cron jobs executed successfully

**Weekly:**
- Review performance metrics
- Check cache hit rate
- Review API usage statistics
- Test event display for accuracy

**Monthly:**
- Update Python dependencies
- Update Joomla module if needed
- Review security logs
- Rotate and archive old logs
- Test backup restoration
- Review SSL certificate expiration

**Quarterly:**
- Security audit
- Performance optimization review
- User feedback review
- Feature enhancement planning

### 10.2 Backup Strategy

**What to Backup:**
- Python application code
- Service account credentials
- Environment configuration
- Joomla module files
- Cache data (optional)
- Logs (for forensics)

**Backup Frequency:**
- Daily: Automated via cPanel backup
- Weekly: Manual backup verification
- Before updates: Pre-deployment snapshot

**Backup Storage:**
- On-site: cPanel backup directory
- Off-site: External backup service (recommended)
- Version control: Git repository for code

### 10.3 Update Procedures

**Python Application Updates:**
```bash
1. Create backup of current version
2. Test updates in staging environment
3. Update dependencies in requirements.txt
4. Run test suite
5. Deploy to production during low-traffic period
6. Monitor logs for 24 hours
7. Rollback if issues detected
```

**Joomla Module Updates:**
```
1. Increment version number in XML
2. Create new ZIP package
3. Test in staging Joomla instance
4. Upload to production
5. Clear Joomla cache
6. Verify module still functions correctly
```

**Google Calendar API Updates:**
```
- Monitor Google Calendar API changelog
- Test API changes in staging
- Update code if breaking changes occur
```

### 10.4 Monitoring & Alerting

**Key Metrics to Monitor:**
- API uptime (target: 99.9%)
- API response times
- Error rate (target: < 0.1%)
- Cache hit rate (target: > 80%)
- Disk space usage
- Memory usage
- CPU usage
- Request rate

**Alerting Thresholds:**
- API downtime > 5 minutes → Critical alert
- Error rate > 5% → Warning alert
- Cache hit rate < 50% → Warning alert
- Disk space > 90% → Warning alert
- Response time > 2s → Warning alert

**Monitoring Tools:**
- cPanel built-in monitoring
- Custom health check script (cron-based)
- Third-party uptime monitoring (e.g., UptimeRobot)
- Google Calendar API quota monitoring

### 10.5 Troubleshooting Guide

**Common Issues:**

**Issue: API returns 500 error**
```
Diagnosis:
- Check API logs: /home/username/cps-calendar-api/logs/api.log
- Verify Google Calendar credentials are valid
- Check service account permissions
- Verify environment variables are set

Solution:
- Rotate service account keys if expired
- Restart Python application
- Check Google Calendar API quotas
```

**Issue: Events not displaying in Joomla**
```
Diagnosis:
- Check browser console for errors
- Verify API endpoint is accessible
- Check API key configuration in module settings
- Test API endpoint directly with curl

Solution:
- Update API endpoint in module configuration
- Verify CORS settings allow Joomla domain
- Clear Joomla cache
- Check module is published and assigned to correct menu items
```

**Issue: Slow page load times**
```
Diagnosis:
- Check API response time
- Review cache hit rate
- Analyze waterfall chart in browser DevTools
- Check server resource usage

Solution:
- Increase cache duration
- Optimize database queries (if applicable)
- Enable CDN for static assets
- Compress images and minify CSS/JS
```

**Issue: Animations are janky**
```
Diagnosis:
- Check browser console for JavaScript errors
- Monitor frame rate using DevTools Performance tab
- Test on different devices

Solution:
- Disable complex animations on low-end devices
- Use CSS transforms instead of position changes
- Implement requestAnimationFrame for JS animations
- Lazy load animations
```

**Issue: OAuth token expired**
```
Diagnosis:
- Check logs for "invalid_grant" or "token_expired" errors
- Verify token refresh script is running

Solution:
- Manually run token refresh script
- Regenerate service account credentials
- Ensure cron job for token refresh is active
```

### 10.6 Support Contacts

**Technical Support:**
- Primary Developer: [Contact information]
- System Administrator: [Contact information]
- Emergency Hotline: [24/7 support number]

**External Support:**
- cPanel Support: [Hosting provider support]
- Google Calendar API Support: https://developers.google.com/calendar/support
- Joomla Community: https://forum.joomla.org/

---

## 11. SUCCESS CRITERIA

### 11.1 Functional Requirements

- ✅ All events from Google Calendar display correctly
- ✅ Real-time updates (within 5 minutes of calendar changes)
- ✅ Color-coded events with proper contrast
- ✅ All links functional (Google Calendar, Maps, attachments)
- ✅ Responsive design works on all devices
- ✅ Month/year grouping displays correctly
- ✅ Animations enhance UX without hindering performance

### 11.2 Performance Requirements

- ✅ Page load time < 2 seconds (cached)
- ✅ API response time < 500ms (cached)
- ✅ API response time < 2s (uncached)
- ✅ Animations run at 30+ fps
- ✅ Cache hit rate > 80%
- ✅ Zero JavaScript errors

### 11.3 Security Requirements

- ✅ API requires authentication (JWT + API Key)
- ✅ HTTPS enforced for all traffic
- ✅ No sensitive data exposed in client-side code
- ✅ Rate limiting prevents abuse
- ✅ CORS properly configured
- ✅ Service account credentials encrypted/protected
- ✅ Passes OWASP Top 10 security audit

### 11.4 User Experience Requirements

- ✅ Intuitive navigation
- ✅ Clear visual hierarchy
- ✅ Professional, modern design matching theme
- ✅ Bowling-themed animations add visual interest
- ✅ Loading states provide feedback
- ✅ Error messages are helpful
- ✅ Accessibility standards met (WCAG 2.1 AA minimum)

### 11.5 Maintainability Requirements

- ✅ Code is well-documented
- ✅ Architecture is modular and scalable
- ✅ Logging provides actionable insights
- ✅ Easy to update and deploy
- ✅ Comprehensive documentation provided
- ✅ Monitoring and alerting in place

---

## 12. BUDGET & TIMELINE ESTIMATE

### 12.1 Effort Estimate

**Backend Development:** 60-80 hours
- API development: 30 hours
- Security implementation: 15 hours
- Testing & optimization: 15 hours
- cPanel deployment: 10 hours

**Frontend Development:** 60-80 hours
- Joomla module core: 20 hours
- Design implementation: 25 hours
- SVG animations: 15 hours
- Testing & refinement: 20 hours

**Integration & Testing:** 20-30 hours
- Integration testing: 10 hours
- Security testing: 8 hours
- UAT & bug fixes: 12 hours

**Documentation & Deployment:** 20-30 hours
- Technical documentation: 10 hours
- User documentation: 8 hours
- Production deployment: 8 hours
- Training & handover: 4 hours

**Total Estimated Hours:** 160-220 hours

### 12.2 Timeline

**Total Project Duration:** 6-8 weeks (assuming full-time work)

**Milestones:**
- Week 2: Backend API complete
- Week 4: Frontend module complete
- Week 5: Integration and testing complete
- Week 6: Production deployment and documentation complete

### 12.3 Cost Breakdown (Estimate)

*Note: Actual costs depend on developer rates and location*

- Senior Full-Stack Developer: 160-220 hours @ $75-150/hour = $12,000 - $33,000
- Infrastructure (cPanel, SSL, domains): $100-300/year
- Tools & Services (testing, monitoring): $50-200/month
- Google Calendar API: Free (within quota limits)

**Total Project Cost:** $12,150 - $33,500 (one-time)  
**Annual Maintenance Cost:** $600 - $2,400 (ongoing)

---

## 13. RISK ASSESSMENT & MITIGATION

### 13.1 Technical Risks

**Risk: cPanel Python limitations**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** 
  - Verify Python version and capabilities before starting
  - Test WSGI application in cPanel staging
  - Have fallback plan (VPS or Docker if needed)

**Risk: Google Calendar API quota limits**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Implement aggressive caching (5-minute minimum)
  - Monitor API usage
  - Request quota increase if needed
  - Use service account (higher quotas)

**Risk: Performance degradation with large event lists**
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:**
  - Implement pagination
  - Use virtual scrolling for large lists
  - Optimize database queries
  - Load test with 500+ events

**Risk: Browser compatibility issues with animations**
- **Probability:** Low
- **Impact:** Low
- **Mitigation:**
  - Use polyfills for older browsers
  - Progressive enhancement approach
  - Disable complex animations on low-end devices
  - Test on all target browsers

### 13.2 Security Risks

**Risk: API key exposure**
- **Probability:** Low
- **Impact:** Critical
- **Mitigation:**
  - Never commit keys to version control
  - Use environment variables
  - Implement key rotation
  - Monitor for unauthorized access

**Risk: XSS attacks via event descriptions**
- **Probability:** Medium
- **Impact:** High
- **Mitigation:**
  - Sanitize all user-generated content
  - Use Content Security Policy headers
  - Escape output properly
  - Regular security audits

**Risk: DDoS attacks on API**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Implement rate limiting
  - Use cPanel IP blocking
  - Enable Cloudflare (optional)
  - Monitor for unusual traffic

### 13.3 Operational Risks

**Risk: Developer unavailability during critical issues**
- **Probability:** Low
- **Impact:** High
- **Mitigation:**
  - Comprehensive documentation
  - Code comments and README files
  - Knowledge transfer sessions
  - Multiple contact methods

**Risk: cPanel hosting downtime**
- **Probability:** Low
- **Impact:** High
- **Mitigation:**
  - Choose reliable hosting provider
  - Implement monitoring and alerting
  - Have backup/rollback plan
  - Consider multi-region deployment (future)

**Risk: Breaking changes in Google Calendar API**
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:**
  - Subscribe to API changelog
  - Use stable API version
  - Test in staging before production updates
  - Maintain backward compatibility

---

## 14. DELIVERABLES CHECKLIST

### 14.1 Code Deliverables

- [ ] Python backend application (complete source code)
- [ ] Joomla module (complete source code)
- [ ] Configuration files and templates
- [ ] Database migration scripts (if applicable)
- [ ] Deployment scripts
- [ ] Cron job scripts
- [ ] Test suite (unit and integration tests)

### 14.2 Design Deliverables

- [ ] SVG assets (bowling pins, ball, animations)
- [ ] Icon files (pattern.png, entry.png, register.png, link.png)
- [ ] CSS stylesheets (minified and source)
- [ ] Responsive design templates
- [ ] Animation specifications

### 14.3 Documentation Deliverables

- [ ] Technical Architecture Document
- [ ] API Reference Documentation
- [ ] Installation Guide (Backend)
- [ ] Installation Guide (Frontend)
- [ ] Configuration Guide
- [ ] User Manual
- [ ] Administrator Guide
- [ ] Maintenance & Troubleshooting Guide
- [ ] Security Best Practices Document
- [ ] Codebase README files
- [ ] Inline code documentation

### 14.4 Testing Deliverables

- [ ] Test Plan
- [ ] Test Cases
- [ ] Test Reports (unit, integration, UAT)
- [ ] Performance Benchmark Report
- [ ] Security Audit Report
- [ ] Browser Compatibility Report
- [ ] Bug Tracking Log (resolved issues)

### 14.5 Deployment Deliverables

- [ ] Production-ready backend application
- [ ] Production-ready Joomla module package
- [ ] Environment configuration templates
- [ ] SSL certificates setup guide
- [ ] Cron job configuration
- [ ] Monitoring setup guide
- [ ] Backup and restore procedures
- [ ] Rollback plan

---

## 15. APPENDICES

### Appendix A: Environment Variables Reference

```bash
# Flask Configuration
FLASK_ENV=production|development
SECRET_KEY=<random 32-char string>
DEBUG=false

# Authentication
JWT_SECRET=<random 32-char string>
JWT_EXPIRATION_HOURS=1
API_KEY=<random 32-char string>

# Google Calendar
GOOGLE_CALENDAR_ID=tyson@cornerpins.com.au
SERVICE_ACCOUNT_FILE=/path/to/service-account.json
GOOGLE_API_SCOPES=https://www.googleapis.com/auth/calendar.readonly

# Cache Configuration
CACHE_TYPE=file|redis
CACHE_REDIS_URL=redis://localhost:6379/0
CACHE_DIR=/path/to/cache
CACHE_DEFAULT_TIMEOUT=300

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# Logging
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
LOG_FILE=/path/to/logs/api.log
LOG_FORMAT=json|text
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Application
API_VERSION=2.0.0
API_PREFIX=/api/v1
MAX_EVENTS_PER_REQUEST=500
DEFAULT_TIMEZONE=Australia/Brisbane
```

### Appendix B: Color Mapping Reference

```python
GOOGLE_CALENDAR_COLORS = {
    'undefined': '#039be5',  # Light Blue
    '1': '#7986cb',          # Lavender
    '2': '#33b679',          # Sage
    '3': '#8e24aa',          # Grape
    '4': '#e67c73',          # Flamingo
    '5': '#f6c026',          # Banana
    '6': '#f5511d',          # Tangerine
    '7': '#039be5',          # Peacock
    '8': '#616161',          # Graphite
    '9': '#3f51b5',          # Blueberry
    '10': '#0b8043',         # Basil
    '11': '#d60000',         # Tomato
}

# New theme colors
THEME_COLORS = {
    'background_primary': '#2d3e50',
    'background_secondary': '#3a4f63',
    'background_card': '#34495e',
    'accent_primary': '#8B7BC4',     # Purple
    'accent_secondary': '#4ecdc4',   # Cyan
    'text_primary': '#ffffff',
    'text_secondary': '#b0b8c1',
    'border': '#4a5f7a',
    'success': '#33d9b2',
    'warning': '#ff6b6b',
}
```

### Appendix C: API Response Examples

**GET /api/v1/events - Success Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "abc123def456",
      "summary": "Grand Youth Eliminator",
      "start": {
        "date": "2026-11-21",
        "dateTime": null,
        "timeZone": "Australia/Brisbane"
      },
      "end": {
        "date": "2026-11-22",
        "dateTime": null,
        "timeZone": "Australia/Brisbane"
      },
      "location": "Caboolture Bowl & Mini Golf, 207 Morayfield Road, Morayfield, QLD",
      "locationShort": "Caboolture Bowl & Mini Golf",
      "description": "Annual youth tournament...",
      "htmlLink": "https://www.google.com/calendar/event?eid=...",
      "colorId": "11",
      "backgroundColor": "#d60000",
      "textColor": "#ffffff",
      "attachments": [
        {
          "fileUrl": "https://drive.google.com/file/d/.../view",
          "title": "Entry Form",
          "iconType": "entry",
          "mimeType": "application/pdf"
        },
        {
          "fileUrl": "https://drive.google.com/file/d/.../view",
          "title": "Pattern Sheet",
          "iconType": "pattern",
          "mimeType": "application/pdf"
        }
      ],
      "urls": {
        "tenpinResults": "https://www.tenpinresults.com/tournament/12345",
        "other": "https://caboolturebowl.com.au"
      },
      "formattedDateRange": "21 Nov to 22 Nov"
    }
  ],
  "meta": {
    "count": 1,
    "cached": true,
    "cacheAge": 120,
    "timestamp": "2025-10-30T14:30:00Z"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid API key",
    "details": null
  },
  "meta": {
    "timestamp": "2025-10-30T14:30:00Z"
  }
}
```

### Appendix D: Joomla Module Configuration Options

```xml
<field name="api_endpoint" 
       type="text" 
       label="API Endpoint URL"
       description="Full URL to the Python API (e.g., https://api.yourdomain.com/cps-api)"
       default="https://yourdomain.com/cps-api"
       required="true" />

<field name="api_key"
       type="password"
       label="API Key"
       description="Secret API key for authentication"
       required="true" />

<field name="cache_duration"
       type="number"
       label="Cache Duration (seconds)"
       description="How long to cache calendar data (300 = 5 minutes)"
       default="300"
       min="60"
       max="3600" />

<field name="enable_animations"
       type="radio"
       label="Enable Animations"
       description="Turn on/off bowling-themed animations"
       default="1">
    <option value="0">No</option>
    <option value="1">Yes</option>
</field>

<field name="animation_speed"
       type="list"
       label="Animation Speed"
       description="Control animation timing"
       default="normal"
       showon="enable_animations:1">
    <option value="slow">Slow</option>
    <option value="normal">Normal</option>
    <option value="fast">Fast</option>
</field>

<field name="show_past_events"
       type="radio"
       label="Show Past Events"
       description="Display events that have already occurred"
       default="0">
    <option value="0">No</option>
    <option value="1">Yes</option>
</field>

<field name="events_per_page"
       type="number"
       label="Events Per Page"
       description="Number of events to display (0 = show all)"
       default="50"
       min="0"
       max="500" />

<field name="show_location_links"
       type="radio"
       label="Enable Location Links"
       description="Make locations clickable (Google Maps)"
       default="1">
    <option value="0">No</option>
    <option value="1">Yes</option>
</field>

<field name="show_icons"
       type="radio"
       label="Show Action Icons"
       description="Display icons for attachments and links"
       default="1">
    <option value="0">No</option>
    <option value="1">Yes</option>
</field>

<field name="date_format"
       type="list"
       label="Date Format"
       description="How to display event dates"
       default="short">
    <option value="short">21 Nov</option>
    <option value="medium">21 Nov 2026</option>
    <option value="long">November 21, 2026</option>
</field>

<field name="custom_css"
       type="textarea"
       label="Custom CSS"
       description="Add custom CSS to override default styling"
       rows="10"
       cols="50"
       filter="raw" />

<field name="debug_mode"
       type="radio"
       label="Debug Mode"
       description="Show debug information (only for administrators)"
       default="0">
    <option value="0">No</option>
    <option value="1">Yes</option>
</field>
```

---

## DOCUMENT CONTROL

**Document Version:** 1.0  
**Last Updated:** October 30, 2025  
**Author:** [Your Name/Company]  
**Status:** Final for Client Review  
**Next Review:** Upon project acceptance

**Version History:**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-30 | [Author] | Initial comprehensive scope of work |

**Approval:**
- [ ] Client Review
- [ ] Technical Review
- [ ] Security Review
- [ ] Budget Approval
- [ ] Project Kickoff

---

## NOTES FOR DEVELOPER

1. **Priority Features:** Focus on core functionality first (API + basic module), then enhance with animations and advanced features.

2. **Security First:** Never compromise on security even if it adds development time. All API endpoints must be authenticated.

3. **Performance:** Cache aggressively. The calendar data doesn't change frequently, so 5-minute cache is reasonable.

4. **Mobile First:** Design for mobile first, then enhance for desktop. Most users will view on mobile devices.

5. **Accessibility:** Ensure keyboard navigation works, proper ARIA labels, and sufficient color contrast.

6. **Browser Support:** Focus on modern browsers (last 2 versions). Don't spend time supporting IE11.

7. **Documentation:** Document as you go. It's easier than trying to remember later.

8. **Testing:** Write tests for critical functionality. It saves time in the long run.

9. **Version Control:** Use Git with meaningful commit messages. Tag releases properly.

10. **Communication:** Keep stakeholders updated on progress. Flag issues early.

---

**END OF SCOPE OF WORK DOCUMENT**

For questions or clarifications, contact: [Your Contact Information]
