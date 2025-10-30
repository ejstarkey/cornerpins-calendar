# CODE TEMPLATES & EXAMPLES
## Bowling Calendar System - Ready-to-Use Code Snippets

**Purpose:** Provide developers with working code templates to accelerate development

---

## BACKEND CODE TEMPLATES

### 1. passenger_wsgi.py (cPanel Entry Point)

```python
"""
WSGI Entry Point for cPanel Python Application
Place in: /home/username/cps-calendar-api/passenger_wsgi.py
"""
import sys
import os

# Add application directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Import Flask application
from app.main import app as application

# Optional: Log startup
import logging
logging.basicConfig(level=logging.INFO)
logging.info("CPS Calendar API starting...")
```

---

### 2. app/main.py (Flask Application)

```python
"""
Main Flask Application
Handles API routing and request/response
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
import logging
import traceback

from app.config import Config
from app.auth import validate_jwt, validate_api_key, require_auth
from app.calendar_service import CalendarService
from app.cache import CacheManager

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS
CORS(app, origins=Config.ALLOWED_ORIGINS, 
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-API-Key'])

# Initialize services
calendar_service = CalendarService()
cache_manager = CacheManager()

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Error handler decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An internal error occurred'
                }
            }), 500
    return decorated_function

# Routes
@app.route('/api/v1/health', methods=['GET'])
def health():
    """Health check endpoint - no authentication required"""
    return jsonify({
        'status': 'ok',
        'version': Config.API_VERSION,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

@app.route('/api/v1/events', methods=['GET'])
@require_auth
@handle_errors
def get_events():
    """Get calendar events - requires authentication"""
    # Get query parameters
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    include_past = request.args.get('include_past', 'false').lower() == 'true'
    limit = min(int(request.args.get('limit', 100)), Config.MAX_EVENTS_PER_REQUEST)
    
    # Generate cache key
    cache_key = f"events:{from_date}:{to_date}:{include_past}:{limit}"
    
    # Check cache
    cached_data = cache_manager.get(cache_key)
    if cached_data:
        logger.info(f"Cache hit for key: {cache_key}")
        return jsonify({
            'success': True,
            'data': cached_data['events'],
            'meta': {
                'count': len(cached_data['events']),
                'cached': True,
                'cacheAge': cached_data.get('age', 0),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        })
    
    # Fetch from Google Calendar
    logger.info(f"Cache miss, fetching from Google Calendar")
    events = calendar_service.get_events(
        from_date=from_date,
        to_date=to_date,
        include_past=include_past,
        max_results=limit
    )
    
    # Cache the result
    cache_data = {
        'events': events,
        'age': 0
    }
    cache_manager.set(cache_key, cache_data, Config.CACHE_DEFAULT_TIMEOUT)
    
    return jsonify({
        'success': True,
        'data': events,
        'meta': {
            'count': len(events),
            'cached': False,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    })

@app.route('/api/v1/colors', methods=['GET'])
@require_auth
@handle_errors
def get_colors():
    """Get Google Calendar color mappings"""
    colors = calendar_service.get_color_mapping()
    return jsonify({
        'success': True,
        'data': colors
    })

@app.route('/api/v1/cache/clear', methods=['POST'])
@require_auth
@handle_errors
def clear_cache():
    """Clear all cached data - admin only"""
    cache_manager.clear()
    logger.info("Cache cleared manually")
    return jsonify({
        'success': True,
        'message': 'Cache cleared successfully'
    })

@app.route('/api/v1/stats', methods=['GET'])
@require_auth
@handle_errors
def get_stats():
    """Get API statistics"""
    # Implement statistics tracking as needed
    return jsonify({
        'success': True,
        'data': {
            'uptime': 'N/A',
            'cacheHitRate': 'N/A',
            'lastSync': datetime.now(timezone.utc).isoformat()
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Endpoint not found'
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'Internal server error'
        }
    }), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)
```

---

### 3. app/config.py (Configuration)

```python
"""
Application Configuration
Loads settings from environment variables
"""
import os
from datetime import timedelta

class Config:
    # Environment
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = ENV == 'development'
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    JWT_SECRET = os.getenv('JWT_SECRET', 'change-this-in-production')
    JWT_EXPIRATION = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 1)))
    API_KEY = os.getenv('API_KEY', 'change-this-in-production')
    
    # Google Calendar
    CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'tyson@cornerpins.com.au')
    SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'file')  # 'redis' or 'file'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DIR = os.getenv('CACHE_DIR', '/tmp/cps_cache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))
    
    # CORS
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 3600))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/tmp/cps_api.log')
    
    # Application
    API_VERSION = '2.0.0'
    MAX_EVENTS_PER_REQUEST = int(os.getenv('MAX_EVENTS', 500))
    DEFAULT_TIMEZONE = os.getenv('TIMEZONE', 'Australia/Brisbane')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ['SECRET_KEY', 'JWT_SECRET', 'API_KEY', 'SERVICE_ACCOUNT_FILE']
        missing = [key for key in required if not getattr(cls, key) or getattr(cls, key).startswith('change-this')]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
```

---

### 4. app/auth.py (Authentication)

```python
"""
Authentication and Authorization
Handles JWT and API key validation
"""
from functools import wraps
from flask import request, jsonify
import jwt
import logging
from datetime import datetime, timezone, timedelta

from app.config import Config

logger = logging.getLogger(__name__)

def generate_jwt(payload, expiration_hours=1):
    """Generate a JWT token"""
    payload['exp'] = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
    payload['iat'] = datetime.now(timezone.utc)
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')

def validate_jwt(token):
    """Validate JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        return None

def validate_api_key(api_key):
    """Validate API key"""
    return api_key == Config.API_KEY

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_API_KEY',
                    'message': 'X-API-Key header is required'
                }
            }), 401
        
        # Validate API key
        if not validate_api_key(api_key):
            logger.warning(f"Invalid API key attempt from {request.remote_addr}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_API_KEY',
                    'message': 'Invalid API key'
                }
            }), 401
        
        # Optional: JWT validation (if you want both)
        # auth_header = request.headers.get('Authorization')
        # if auth_header and auth_header.startswith('Bearer '):
        #     token = auth_header.split(' ')[1]
        #     payload = validate_jwt(token)
        #     if not payload:
        #         return jsonify({
        #             'success': False,
        #             'error': {
        #                 'code': 'INVALID_TOKEN',
        #                 'message': 'Invalid or expired JWT token'
        #             }
        #         }), 401
        
        return f(*args, **kwargs)
    return decorated_function
```

---

### 5. app/calendar_service.py (Google Calendar Integration)

```python
"""
Google Calendar Service
Handles all interactions with Google Calendar API
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone
import logging
import re
from dateutil.parser import parse

from app.config import Config

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self):
        self.credentials = self._load_credentials()
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.colors = self._get_color_mapping()
    
    def _load_credentials(self):
        """Load service account credentials"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                Config.SERVICE_ACCOUNT_FILE,
                scopes=Config.SCOPES
            )
            logger.info("Google Calendar credentials loaded successfully")
            return credentials
        except Exception as e:
            logger.error(f"Failed to load credentials: {str(e)}")
            raise
    
    def get_events(self, from_date=None, to_date=None, include_past=False, max_results=100):
        """Fetch events from Google Calendar"""
        try:
            # Set time_min
            if from_date:
                time_min = from_date
            elif include_past:
                time_min = None
            else:
                time_min = datetime.now(timezone.utc).isoformat()
            
            # Build request parameters
            params = {
                'calendarId': Config.CALENDAR_ID,
                'singleEvents': True,
                'orderBy': 'startTime',
                'maxResults': max_results
            }
            
            if time_min:
                params['timeMin'] = time_min
            if to_date:
                params['timeMax'] = to_date
            
            # Fetch events
            events_result = self.service.events().list(**params).execute()
            events = events_result.get('items', [])
            
            logger.info(f"Fetched {len(events)} events from Google Calendar")
            
            # Process and enrich events
            return self._process_events(events)
            
        except Exception as e:
            logger.error(f"Error fetching calendar events: {str(e)}")
            raise
    
    def _process_events(self, events):
        """Process and enrich event data"""
        processed = []
        
        for event in events:
            try:
                processed_event = {
                    'id': event.get('id'),
                    'summary': event.get('summary', 'No Title'),
                    'start': event.get('start'),
                    'end': event.get('end'),
                    'description': event.get('description', ''),
                    'htmlLink': event.get('htmlLink'),
                    'colorId': event.get('colorId', 'undefined'),
                }
                
                # Process location
                location = event.get('location', '')
                processed_event['location'] = location
                processed_event['locationShort'] = self._extract_location(location)
                
                # Add colors
                color_id = processed_event['colorId']
                bg_color = self.colors.get(color_id, self.colors['undefined'])
                processed_event['backgroundColor'] = bg_color
                processed_event['textColor'] = self._calculate_text_color(bg_color)
                
                # Extract URLs from description
                urls = self._extract_urls(processed_event['description'])
                processed_event['urls'] = urls
                
                # Process attachments
                if 'attachments' in event:
                    processed_event['attachments'] = self._process_attachments(event['attachments'])
                else:
                    processed_event['attachments'] = []
                
                # Format date range
                processed_event['formattedDateRange'] = self._format_date_range(
                    processed_event['start'],
                    processed_event['end']
                )
                
                processed.append(processed_event)
                
            except Exception as e:
                logger.error(f"Error processing event {event.get('id')}: {str(e)}")
                continue
        
        return processed
    
    def _extract_location(self, location):
        """Extract short location name (first part before comma)"""
        if not location:
            return 'No Location'
        return location.split(',')[0].strip()
    
    def _extract_urls(self, description):
        """Extract URLs from event description"""
        urls = {
            'tenpinResults': None,
            'other': None
        }
        
        if not description:
            return urls
        
        # Find all URLs
        url_pattern = r'href="(https?://\S+)"'
        found_urls = re.findall(url_pattern, description)
        
        for url in found_urls:
            if 'tenpinresults' in url.lower():
                urls['tenpinResults'] = url
            else:
                urls['other'] = url  # Last one wins
        
        return urls
    
    def _process_attachments(self, attachments):
        """Process event attachments"""
        processed = []
        
        for attachment in attachments:
            if 'fileUrl' in attachment:
                icon_type = 'entry'
                title = attachment.get('title', '').lower()
                
                if 'pattern' in title:
                    icon_type = 'pattern'
                
                processed.append({
                    'fileUrl': attachment['fileUrl'],
                    'title': attachment.get('title', 'Attachment'),
                    'iconType': icon_type,
                    'mimeType': attachment.get('mimeType', '')
                })
        
        return processed
    
    def _calculate_text_color(self, bg_color):
        """Calculate appropriate text color based on background luminance"""
        # Remove # if present
        bg_color = bg_color.lstrip('#')
        
        # Convert to RGB
        rgb = tuple(int(bg_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate luminance
        def channel_luminance(channel):
            channel = channel / 255
            if channel <= 0.03928:
                return channel / 12.92
            else:
                return ((channel + 0.055) / 1.055) ** 2.4
        
        luminance = (
            0.2126 * channel_luminance(rgb[0]) +
            0.7152 * channel_luminance(rgb[1]) +
            0.0722 * channel_luminance(rgb[2])
        )
        
        # Return black for light backgrounds, white for dark
        return '#000000' if luminance > 0.5 else '#FFFFFF'
    
    def _format_date_range(self, start, end):
        """Format date range for display"""
        start_date_str = start.get('dateTime') or start.get('date')
        end_date_str = end.get('dateTime') or end.get('date')
        
        start_date = parse(start_date_str).date()
        end_date = parse(end_date_str).date()
        
        start_formatted = start_date.strftime('%d %b')
        end_formatted = end_date.strftime('%d %b')
        
        if start_formatted == end_formatted:
            return start_formatted
        else:
            return f"{start_formatted} to {end_formatted}"
    
    def _get_color_mapping(self):
        """Get Google Calendar color ID to hex color mapping"""
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
    
    def get_color_mapping(self):
        """Public method to get color mapping"""
        return self.colors
```

---

### 6. app/cache.py (Caching Layer)

```python
"""
Caching Layer
Supports both file-based and Redis caching
"""
import json
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta

from app.config import Config

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        if Config.CACHE_TYPE == 'redis':
            try:
                import redis
                self.backend = RedisCache()
                logger.info("Using Redis cache backend")
            except ImportError:
                logger.warning("Redis not available, falling back to file cache")
                self.backend = FileCache()
        else:
            self.backend = FileCache()
            logger.info("Using file cache backend")
    
    def get(self, key):
        """Get value from cache"""
        return self.backend.get(key)
    
    def set(self, key, value, timeout=None):
        """Set value in cache"""
        timeout = timeout or Config.CACHE_DEFAULT_TIMEOUT
        return self.backend.set(key, value, timeout)
    
    def delete(self, key):
        """Delete key from cache"""
        return self.backend.delete(key)
    
    def clear(self):
        """Clear all cache"""
        return self.backend.clear()

class FileCache:
    """File-based caching implementation"""
    def __init__(self):
        self.cache_dir = Path(Config.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"File cache directory: {self.cache_dir}")
    
    def _get_cache_path(self, key):
        """Get file path for cache key"""
        # Sanitize key for filename
        safe_key = key.replace('/', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key):
        """Get value from file cache"""
        try:
            cache_file = self._get_cache_path(key)
            
            if not cache_file.exists():
                return None
            
            # Read cache file
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check expiration
            expires_at = cache_data.get('expires_at')
            if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                # Cache expired
                cache_file.unlink()
                return None
            
            # Update age
            created_at = datetime.fromisoformat(cache_data.get('created_at'))
            age = (datetime.now() - created_at).total_seconds()
            
            value = cache_data.get('value')
            if isinstance(value, dict):
                value['age'] = int(age)
            
            return value
            
        except Exception as e:
            logger.error(f"Error reading cache for key {key}: {str(e)}")
            return None
    
    def set(self, key, value, timeout):
        """Set value in file cache"""
        try:
            cache_file = self._get_cache_path(key)
            
            expires_at = datetime.now() + timedelta(seconds=timeout)
            
            cache_data = {
                'value': value,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            logger.error(f"Error writing cache for key {key}: {str(e)}")
            return False
    
    def delete(self, key):
        """Delete key from file cache"""
        try:
            cache_file = self._get_cache_path(key)
            if cache_file.exists():
                cache_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Error deleting cache for key {key}: {str(e)}")
            return False
    
    def clear(self):
        """Clear all file cache"""
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
            logger.info("File cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False

class RedisCache:
    """Redis caching implementation"""
    def __init__(self):
        import redis
        self.client = redis.from_url(Config.CACHE_REDIS_URL)
        logger.info(f"Redis cache connected: {Config.CACHE_REDIS_URL}")
    
    def get(self, key):
        """Get value from Redis"""
        try:
            value = self.client.get(key)
            if value:
                data = json.loads(value)
                # Calculate age
                created_at = data.get('created_at')
                if created_at:
                    age = (datetime.now() - datetime.fromisoformat(created_at)).total_seconds()
                    if isinstance(data.get('value'), dict):
                        data['value']['age'] = int(age)
                return data.get('value')
            return None
        except Exception as e:
            logger.error(f"Error reading from Redis for key {key}: {str(e)}")
            return None
    
    def set(self, key, value, timeout):
        """Set value in Redis"""
        try:
            data = {
                'value': value,
                'created_at': datetime.now().isoformat()
            }
            self.client.setex(key, timeout, json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Error writing to Redis for key {key}: {str(e)}")
            return False
    
    def delete(self, key):
        """Delete key from Redis"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from Redis for key {key}: {str(e)}")
            return False
    
    def clear(self):
        """Clear all Redis cache"""
        try:
            self.client.flushdb()
            logger.info("Redis cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {str(e)}")
            return False
```

---

### 7. requirements.txt

```
Flask==3.0.0
Flask-CORS==4.0.0
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.111.0
PyJWT==2.8.0
python-dateutil==2.8.2
redis==5.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
```

---

### 8. .env.example

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=generate-random-32-char-string
DEBUG=false

# Authentication
JWT_SECRET=generate-random-32-char-string
JWT_EXPIRATION_HOURS=1
API_KEY=generate-random-32-char-string

# Google Calendar
GOOGLE_CALENDAR_ID=tyson@cornerpins.com.au
SERVICE_ACCOUNT_FILE=/home/username/cps-calendar-api/service-account.json

# Cache Configuration
CACHE_TYPE=file
CACHE_REDIS_URL=redis://localhost:6379/0
CACHE_DIR=/home/username/cps-calendar-api/cache
CACHE_TIMEOUT=300

# CORS
ALLOWED_ORIGINS=https://yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/username/cps-calendar-api/logs/api.log

# Application
MAX_EVENTS=500
TIMEZONE=Australia/Brisbane
```

---

## FRONTEND CODE TEMPLATES

### 9. mod_cps_calendar.xml (Joomla Module Manifest)

```xml
<?xml version="1.0" encoding="utf-8"?>
<extension type="module" version="4.0" client="site" method="upgrade">
    <name>CPS Bowling Calendar</name>
    <author>Corner Pin Standings</author>
    <creationDate>October 2025</creationDate>
    <copyright>Copyright (C) 2025</copyright>
    <license>GNU General Public License version 2 or later</license>
    <authorEmail>tyson@cornerpins.com.au</authorEmail>
    <authorUrl>https://cornerpinstandings.com.au</authorUrl>
    <version>2.0.0</version>
    <description>Modern bowling tournament calendar with real-time Google Calendar integration</description>
    
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
            <fieldset name="basic" label="MOD_CPS_CALENDAR_BASIC_FIELDSET_LABEL">
                
                <field
                    name="api_endpoint"
                    type="text"
                    label="API Endpoint URL"
                    description="Full URL to the Python API (e.g., https://api.yourdomain.com/cps-api)"
                    default="https://yourdomain.com/cps-api"
                    required="true"
                    size="60"
                />
                
                <field
                    name="api_key"
                    type="password"
                    label="API Key"
                    description="Secret API key for authentication"
                    required="true"
                    size="60"
                />
                
                <field
                    name="cache_duration"
                    type="number"
                    label="Cache Duration (seconds)"
                    description="How long to cache calendar data locally (300 = 5 minutes)"
                    default="300"
                    min="60"
                    max="3600"
                />
                
                <field
                    name="enable_animations"
                    type="radio"
                    label="Enable Animations"
                    description="Turn on/off bowling-themed animations"
                    default="1"
                    class="btn-group btn-group-yesno">
                    <option value="0">JNO</option>
                    <option value="1">JYES</option>
                </field>
                
                <field
                    name="show_past_events"
                    type="radio"
                    label="Show Past Events"
                    description="Display events that have already occurred"
                    default="0"
                    class="btn-group btn-group-yesno">
                    <option value="0">JNO</option>
                    <option value="1">JYES</option>
                </field>
                
                <field
                    name="events_per_page"
                    type="number"
                    label="Events Per Page"
                    description="Number of events to display (0 = show all)"
                    default="50"
                    min="0"
                    max="500"
                />
                
                <field
                    name="custom_css"
                    type="textarea"
                    label="Custom CSS"
                    description="Add custom CSS to override default styling"
                    rows="10"
                    cols="60"
                    filter="raw"
                />
                
            </fieldset>
            
            <fieldset name="advanced">
                <field
                    name="moduleclass_sfx"
                    type="textarea"
                    label="COM_MODULES_FIELD_MODULECLASS_SFX_LABEL"
                    rows="3"
                />
                
                <field
                    name="cache"
                    type="list"
                    label="COM_MODULES_FIELD_CACHING_LABEL"
                    default="1"
                    filter="integer">
                    <option value="1">JGLOBAL_USE_GLOBAL</option>
                    <option value="0">COM_MODULES_FIELD_VALUE_NOCACHING</option>
                </field>
            </fieldset>
            
        </fields>
    </config>
</extension>
```

---

### 10. mod_cps_calendar.php (Entry Point)

```php
<?php
/**
 * @package     CPS Bowling Calendar
 * @version     2.0.0
 * @author      Corner Pin Standings
 * @copyright   Copyright (C) 2025
 * @license     GNU/GPL
 */

defined('_JEXEC') or die;

use Joomla\CMS\Helper\ModuleHelper;

// Include the helper
require_once __DIR__ . '/helper.php';

// Get module parameters
$params = $module->params;

// Get helper instance
$helper = new ModCpsCalendarHelper($params);

// Load module CSS and JS
$wa = $app->getDocument()->getWebAssetManager();
$wa->registerAndUseStyle('mod_cps_calendar', 'media/mod_cps_calendar/css/calendar.css');
$wa->registerAndUseScript('mod_cps_calendar', 'media/mod_cps_calendar/js/calendar.js', [], ['defer' => true]);

if ($params->get('enable_animations', 1)) {
    $wa->registerAndUseScript('mod_cps_calendar_animations', 'media/mod_cps_calendar/js/animations.js', [], ['defer' => true]);
}

// Pass configuration to JavaScript
$config = [
    'apiEndpoint' => $params->get('api_endpoint'),
    'apiKey' => $params->get('api_key'),
    'cacheDuration' => $params->get('cache_duration', 300),
    'enableAnimations' => $params->get('enable_animations', 1),
    'showPastEvents' => $params->get('show_past_events', 0),
    'eventsPerPage' => $params->get('events_per_page', 50),
];

$app->getDocument()->addScriptOptions('mod_cps_calendar', $config);

// Add custom CSS if provided
$customCss = $params->get('custom_css', '');
if (!empty($customCss)) {
    $app->getDocument()->addStyleDeclaration($customCss);
}

// Include the template
require ModuleHelper::getLayoutPath('mod_cps_calendar', $params->get('layout', 'default'));
```

---

### 11. helper.php (PHP Helper Class)

```php
<?php
/**
 * Helper class for CPS Bowling Calendar Module
 */

defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\CMS\Http\HttpFactory;
use Joomla\CMS\Cache\CacheController;

class ModCpsCalendarHelper
{
    protected $params;
    protected $cache;
    
    public function __construct($params)
    {
        $this->params = $params;
        
        // Initialize cache
        $cacheOptions = [
            'defaultgroup' => 'mod_cps_calendar',
            'caching' => true,
            'lifetime' => $params->get('cache_duration', 300) / 60, // Convert to minutes
        ];
        $this->cache = Factory::getCache('mod_cps_calendar', '', $cacheOptions);
    }
    
    /**
     * Make API request to backend
     */
    public function makeApiRequest($endpoint, $queryParams = [])
    {
        try {
            $apiEndpoint = rtrim($this->params->get('api_endpoint'), '/');
            $apiKey = $this->params->get('api_key');
            
            if (empty($apiEndpoint) || empty($apiKey)) {
                throw new RuntimeException('API endpoint or key not configured');
            }
            
            // Build URL
            $url = $apiEndpoint . $endpoint;
            if (!empty($queryParams)) {
                $url .= '?' . http_build_query($queryParams);
            }
            
            // Make HTTP request
            $http = HttpFactory::getHttp();
            $headers = [
                'X-API-Key' => $apiKey,
                'Accept' => 'application/json',
            ];
            
            $response = $http->get($url, $headers);
            
            if ($response->code !== 200) {
                throw new RuntimeException('API returned status ' . $response->code);
            }
            
            return json_decode($response->body, true);
            
        } catch (Exception $e) {
            Factory::getApplication()->enqueueMessage(
                'Error connecting to calendar API: ' . $e->getMessage(),
                'error'
            );
            return null;
        }
    }
    
    /**
     * Get events from API (with caching)
     */
    public function getEvents()
    {
        $cacheKey = 'events_' . md5($this->params->toString());
        
        // Try to get from cache
        $cachedData = $this->cache->get($cacheKey);
        if ($cachedData !== false) {
            return $cachedData;
        }
        
        // Fetch from API
        $queryParams = [
            'include_past' => $this->params->get('show_past_events', 0) ? 'true' : 'false',
            'limit' => $this->params->get('events_per_page', 50),
        ];
        
        $result = $this->makeApiRequest('/api/v1/events', $queryParams);
        
        if ($result && isset($result['success']) && $result['success']) {
            $events = $result['data'];
            
            // Cache the result
            $this->cache->store($events, $cacheKey);
            
            return $events;
        }
        
        return [];
    }
    
    /**
     * Sanitize output for display
     */
    public static function sanitizeOutput($text)
    {
        return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    }
}
```

---

### 12. tmpl/default.php (Template)

```php
<?php
/**
 * Default template for CPS Bowling Calendar Module
 */

defined('_JEXEC') or die;
?>

<div class="cps-calendar-wrapper" id="cps-calendar-<?php echo $module->id; ?>">
    
    <!-- Loading State -->
    <div class="cps-calendar-loading">
        <div class="bowling-ball-loader"></div>
        <p>Loading tournament calendar...</p>
    </div>
    
    <!-- Error State (hidden by default) -->
    <div class="cps-calendar-error" style="display: none;">
        <p>Unable to load calendar events. Please try again later.</p>
    </div>
    
    <!-- Calendar Container (populated by JavaScript) -->
    <div class="cps-calendar-content">
        <!-- JavaScript will populate this -->
    </div>
    
</div>

<?php
// Note: The actual event rendering is handled by JavaScript
// This provides a cleaner separation and allows for dynamic updates
?>
```

---

I'll continue with the JavaScript and CSS templates in the next message due to length...

Would you like me to continue with:
1. JavaScript templates (calendar.js, animations.js)
2. CSS template (calendar.css)
3. SVG assets
4. Deployment scripts

Let me know and I'll create those next!
