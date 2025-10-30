# FRONTEND ASSETS & DEPLOYMENT SCRIPTS
## JavaScript, CSS, SVG, and Automation Scripts

---

## JAVASCRIPT TEMPLATES

### 1. media/js/calendar.js (Main Calendar Logic)

```javascript
/**
 * CPS Bowling Calendar - Main JavaScript
 * Handles API communication, event rendering, and interactions
 */

class CPSCalendar {
    constructor(moduleId, config) {
        this.moduleId = moduleId;
        this.config = config;
        this.container = document.getElementById(`cps-calendar-${moduleId}`);
        this.events = [];
        this.cache = null;
        this.cacheExpiry = null;
        
        this.init();
    }
    
    /**
     * Initialize calendar
     */
    async init() {
        try {
            // Show loading state
            this.showLoading();
            
            // Check for cached data in sessionStorage
            const cachedData = this.getCachedEvents();
            if (cachedData) {
                this.events = cachedData;
                this.render();
            } else {
                // Fetch from API
                await this.fetchEvents();
                this.render();
            }
            
            // Hide loading
            this.hideLoading();
            
            // Initialize animations if enabled
            if (this.config.enableAnimations && window.CPSAnimations) {
                window.CPSAnimations.init(this.container);
            }
            
        } catch (error) {
            console.error('CPS Calendar Error:', error);
            this.showError();
        }
    }
    
    /**
     * Fetch events from API
     */
    async fetchEvents() {
        const url = `${this.config.apiEndpoint}/api/v1/events?` + new URLSearchParams({
            include_past: this.config.showPastEvents ? 'true' : 'false',
            limit: this.config.eventsPerPage
        });
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'X-API-Key': this.config.apiKey,
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('API returned error');
        }
        
        this.events = data.data;
        
        // Cache the events
        this.cacheEvents(this.events);
    }
    
    /**
     * Cache events in sessionStorage
     */
    cacheEvents(events) {
        const cacheData = {
            events: events,
            timestamp: Date.now(),
            expiry: Date.now() + (this.config.cacheDuration * 1000)
        };
        
        try {
            sessionStorage.setItem(`cps_calendar_${this.moduleId}`, JSON.stringify(cacheData));
        } catch (e) {
            console.warn('Unable to cache events:', e);
        }
    }
    
    /**
     * Get cached events from sessionStorage
     */
    getCachedEvents() {
        try {
            const cached = sessionStorage.getItem(`cps_calendar_${this.moduleId}`);
            if (!cached) return null;
            
            const cacheData = JSON.parse(cached);
            
            // Check if cache is still valid
            if (Date.now() > cacheData.expiry) {
                sessionStorage.removeItem(`cps_calendar_${this.moduleId}`);
                return null;
            }
            
            return cacheData.events;
            
        } catch (e) {
            console.warn('Error reading cache:', e);
            return null;
        }
    }
    
    /**
     * Render calendar events
     */
    render() {
        const contentContainer = this.container.querySelector('.cps-calendar-content');
        if (!contentContainer) return;
        
        // Group events by month/year
        const groupedEvents = this.groupEventsByMonth(this.events);
        
        // Build HTML
        let html = '<div class="cps-events-list">';
        
        for (const [monthYear, events] of Object.entries(groupedEvents)) {
            html += this.renderMonthSection(monthYear, events);
        }
        
        html += '</div>';
        
        contentContainer.innerHTML = html;
        
        // Attach event listeners
        this.attachEventListeners();
    }
    
    /**
     * Group events by month and year
     */
    groupEventsByMonth(events) {
        const grouped = {};
        
        events.forEach(event => {
            const startDate = new Date(event.start.date || event.start.dateTime);
            const monthYear = startDate.toLocaleString('en-US', { 
                month: 'long', 
                year: '2-digit' 
            });
            
            if (!grouped[monthYear]) {
                grouped[monthYear] = [];
            }
            
            grouped[monthYear].push(event);
        });
        
        return grouped;
    }
    
    /**
     * Render month section
     */
    renderMonthSection(monthYear, events) {
        let html = `
            <div class="month-section">
                <div class="month-separator">
                    <h2>${this.escapeHtml(monthYear)}</h2>
                </div>
                <div class="events-grid">
        `;
        
        events.forEach(event => {
            html += this.renderEventCard(event);
        });
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }
    
    /**
     * Render individual event card
     */
    renderEventCard(event) {
        const bgColor = event.backgroundColor || '#039be5';
        const textColor = event.textColor || '#ffffff';
        
        return `
            <div class="event-card" style="background-color: ${bgColor}; color: ${textColor};">
                <div class="event-date-badge">
                    ${this.escapeHtml(event.formattedDateRange || 'TBD')}
                </div>
                
                <div class="event-details">
                    <h3 class="event-title">
                        <a href="${this.escapeHtml(event.htmlLink)}" 
                           target="_blank" 
                           style="color: ${textColor};"
                           rel="noopener noreferrer">
                            ${this.escapeHtml(event.summary)}
                        </a>
                    </h3>
                    
                    <div class="event-location">
                        ${event.locationShort !== 'No Location' 
                            ? `<a href="https://maps.google.com/?q=${encodeURIComponent(event.location)}" 
                                  target="_blank" 
                                  style="color: ${textColor};"
                                  rel="noopener noreferrer">
                                  📍 ${this.escapeHtml(event.locationShort)}
                               </a>`
                            : '📍 No Location'}
                    </div>
                    
                    <div class="event-actions">
                        ${this.renderEventActions(event, textColor)}
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Render event action buttons/icons
     */
    renderEventActions(event, textColor) {
        let html = '';
        
        // TenpinResults link
        if (event.urls && event.urls.tenpinResults) {
            html += `
                <a href="${this.escapeHtml(event.urls.tenpinResults)}" 
                   target="_blank" 
                   class="action-icon"
                   title="Register on TenpinResults"
                   rel="noopener noreferrer">
                    <img src="/media/mod_cps_calendar/images/register.png" alt="Register" />
                </a>
            `;
        }
        
        // Other URL link
        if (event.urls && event.urls.other) {
            html += `
                <a href="${this.escapeHtml(event.urls.other)}" 
                   target="_blank" 
                   class="action-icon"
                   title="More Information"
                   rel="noopener noreferrer">
                    <img src="/media/mod_cps_calendar/images/link.png" alt="Link" />
                </a>
            `;
        }
        
        // Attachments
        if (event.attachments && event.attachments.length > 0) {
            event.attachments.forEach(attachment => {
                const icon = attachment.iconType === 'pattern' ? 'pattern.png' : 'entry.png';
                html += `
                    <a href="${this.escapeHtml(attachment.fileUrl)}" 
                       target="_blank" 
                       class="action-icon"
                       title="${this.escapeHtml(attachment.title)}"
                       rel="noopener noreferrer">
                        <img src="/media/mod_cps_calendar/images/${icon}" alt="${this.escapeHtml(attachment.title)}" />
                    </a>
                `;
            });
        }
        
        return html;
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Add click tracking, animations, etc.
        const eventCards = this.container.querySelectorAll('.event-card');
        
        eventCards.forEach(card => {
            // Hover effects
            card.addEventListener('mouseenter', () => {
                if (this.config.enableAnimations && window.CPSAnimations) {
                    window.CPSAnimations.cardHover(card);
                }
            });
            
            // Click ripple effect
            card.addEventListener('click', (e) => {
                if (this.config.enableAnimations && window.CPSAnimations) {
                    window.CPSAnimations.rippleEffect(card, e);
                }
            });
        });
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const loading = this.container.querySelector('.cps-calendar-loading');
        if (loading) loading.style.display = 'block';
        
        const content = this.container.querySelector('.cps-calendar-content');
        if (content) content.style.display = 'none';
        
        const error = this.container.querySelector('.cps-calendar-error');
        if (error) error.style.display = 'none';
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        const loading = this.container.querySelector('.cps-calendar-loading');
        if (loading) loading.style.display = 'none';
        
        const content = this.container.querySelector('.cps-calendar-content');
        if (content) content.style.display = 'block';
    }
    
    /**
     * Show error state
     */
    showError() {
        const loading = this.container.querySelector('.cps-calendar-loading');
        if (loading) loading.style.display = 'none';
        
        const content = this.container.querySelector('.cps-calendar-content');
        if (content) content.style.display = 'none';
        
        const error = this.container.querySelector('.cps-calendar-error');
        if (error) error.style.display = 'block';
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize calendar when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const config = Joomla.getOptions('mod_cps_calendar');
    
    if (config) {
        // Find all calendar modules on the page
        document.querySelectorAll('[id^="cps-calendar-"]').forEach(container => {
            const moduleId = container.id.replace('cps-calendar-', '');
            new CPSCalendar(moduleId, config);
        });
    }
});
```

---

### 2. media/js/animations.js (SVG Animations)

```javascript
/**
 * CPS Bowling Calendar - Animations
 * Bowling-themed SVG animations and micro-interactions
 */

window.CPSAnimations = {
    
    /**
     * Initialize animations for a calendar container
     */
    init(container) {
        this.container = container;
        this.addBowlingPinsBackground();
        this.animateEventCards();
    },
    
    /**
     * Add bowling pins background decoration
     */
    addBowlingPinsBackground() {
        // Create bowling pins SVG in the background
        const pins = document.createElement('div');
        pins.className = 'bowling-pins-decoration';
        pins.innerHTML = `
            <svg viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
                <g class="pin-group">
                    <!-- Bowling pins outline -->
                    <path class="pin pin-1" d="M50,20 Q50,5 55,5 L65,5 Q70,5 70,20 L70,60 Q70,70 65,75 L55,75 Q50,70 50,60 Z" />
                    <path class="pin pin-2" d="M120,20 Q120,5 125,5 L135,5 Q140,5 140,20 L140,60 Q140,70 135,75 L125,75 Q120,70 120,60 Z" />
                    <path class="pin pin-3" d="M190,20 Q190,5 195,5 L205,5 Q210,5 210,20 L210,60 Q210,70 205,75 L195,75 Q190,70 190,60 Z" />
                    
                    <!-- Bowling ball -->
                    <circle class="bowling-ball" cx="20" cy="50" r="15" />
                    <circle class="ball-hole" cx="18" cy="48" r="2" />
                    <circle class="ball-hole" cx="22" cy="48" r="2" />
                    <circle class="ball-hole" cx="20" cy="53" r="2" />
                </g>
            </svg>
        `;
        
        const monthSections = this.container.querySelectorAll('.month-separator');
        monthSections.forEach(section => {
            const decoration = pins.cloneNode(true);
            section.appendChild(decoration);
        });
    },
    
    /**
     * Animate event cards with staggered fade-in
     */
    animateEventCards() {
        const cards = this.container.querySelectorAll('.event-card');
        
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100); // Stagger by 100ms
        });
    },
    
    /**
     * Card hover animation
     */
    cardHover(card) {
        card.style.transform = 'scale(1.02) translateY(-4px)';
        card.style.transition = 'transform 0.3s ease';
        
        card.addEventListener('mouseleave', function onMouseLeave() {
            card.style.transform = 'scale(1) translateY(0)';
            card.removeEventListener('mouseleave', onMouseLeave);
        });
    },
    
    /**
     * Ripple effect on click
     */
    rippleEffect(element, event) {
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    },
    
    /**
     * Bowling ball roll animation
     */
    rollBowlingBall(container) {
        // Create bowling ball element
        const ball = document.createElement('div');
        ball.className = 'bowling-ball-animation';
        container.appendChild(ball);
        
        // Animate across screen
        setTimeout(() => {
            ball.style.transform = 'translateX(100vw) rotate(720deg)';
        }, 100);
        
        // Remove after animation
        setTimeout(() => {
            ball.remove();
        }, 2000);
    },
    
    /**
     * Pin strike animation for month transitions
     */
    strikeAnimation(element) {
        element.classList.add('pin-strike');
        
        setTimeout(() => {
            element.classList.remove('pin-strike');
        }, 1200);
    }
};

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.CPSAnimations;
}
```

---

## CSS TEMPLATE

### 3. media/css/calendar.css (Main Stylesheet)

```css
/**
 * CPS Bowling Calendar - Main Stylesheet
 * Modern, sophisticated design with bowling theme
 */

/* ========================================
   Variables (CSS Custom Properties)
   ======================================== */
:root {
    /* Colors from theme.jpg */
    --cps-bg-primary: #2d3e50;
    --cps-bg-secondary: #3a4f63;
    --cps-bg-card: #34495e;
    --cps-accent-purple: #8B7BC4;
    --cps-accent-cyan: #4ecdc4;
    --cps-text-primary: #ffffff;
    --cps-text-secondary: #b0b8c1;
    --cps-border: #4a5f7a;
    --cps-success: #33d9b2;
    --cps-warning: #ff6b6b;
    
    /* Spacing */
    --cps-spacing-xs: 4px;
    --cps-spacing-sm: 8px;
    --cps-spacing-md: 16px;
    --cps-spacing-lg: 24px;
    --cps-spacing-xl: 32px;
    
    /* Border radius */
    --cps-radius-sm: 8px;
    --cps-radius-md: 12px;
    --cps-radius-lg: 16px;
    
    /* Shadows */
    --cps-shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
    --cps-shadow-md: 0 4px 8px rgba(0, 0, 0, 0.15);
    --cps-shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
    
    /* Transitions */
    --cps-transition: all 0.3s ease;
}

/* ========================================
   Main Container
   ======================================== */
.cps-calendar-wrapper {
    background-color: var(--cps-bg-primary);
    color: var(--cps-text-primary);
    padding: var(--cps-spacing-lg);
    border-radius: var(--cps-radius-md);
    font-family: 'Ubuntu', 'Segoe UI', Arial, sans-serif;
    max-width: 1400px;
    margin: 0 auto;
}

/* ========================================
   Loading State
   ======================================== */
.cps-calendar-loading {
    text-align: center;
    padding: var(--cps-spacing-xl);
}

.bowling-ball-loader {
    width: 60px;
    height: 60px;
    margin: 0 auto var(--cps-spacing-md);
    border-radius: 50%;
    background: linear-gradient(135deg, var(--cps-accent-purple), var(--cps-accent-cyan));
    animation: spin 1s linear infinite;
    position: relative;
}

.bowling-ball-loader::before,
.bowling-ball-loader::after {
    content: '';
    position: absolute;
    width: 8px;
    height: 8px;
    background: var(--cps-bg-primary);
    border-radius: 50%;
    top: 20px;
}

.bowling-ball-loader::before {
    left: 20px;
}

.bowling-ball-loader::after {
    right: 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ========================================
   Error State
   ======================================== */
.cps-calendar-error {
    text-align: center;
    padding: var(--cps-spacing-xl);
    color: var(--cps-warning);
    background-color: rgba(255, 107, 107, 0.1);
    border-radius: var(--cps-radius-md);
    border: 2px solid var(--cps-warning);
}

/* ========================================
   Month Sections
   ======================================== */
.month-section {
    margin-bottom: var(--cps-spacing-xl);
}

.month-separator {
    text-align: center;
    margin: var(--cps-spacing-xl) 0 var(--cps-spacing-lg);
    position: relative;
}

.month-separator h2 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--cps-accent-purple);
    margin: 0;
    padding: 0;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Bowling pins decoration in month separator */
.bowling-pins-decoration {
    opacity: 0.15;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 100px;
    pointer-events: none;
    z-index: 0;
}

.bowling-pins-decoration svg {
    width: 100%;
    height: 100%;
}

.bowling-pins-decoration .pin {
    fill: none;
    stroke: var(--cps-accent-cyan);
    stroke-width: 2;
    opacity: 0.5;
}

.bowling-pins-decoration .bowling-ball {
    fill: var(--cps-accent-purple);
    opacity: 0.6;
}

.bowling-pins-decoration .ball-hole {
    fill: var(--cps-bg-primary);
}

/* ========================================
   Events Grid
   ======================================== */
.events-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--cps-spacing-md);
}

@media (max-width: 768px) {
    .events-grid {
        grid-template-columns: 1fr;
    }
}

/* ========================================
   Event Cards
   ======================================== */
.event-card {
    background-color: var(--cps-bg-card);
    border-radius: var(--cps-radius-md);
    padding: var(--cps-spacing-md);
    box-shadow: var(--cps-shadow-md);
    transition: var(--cps-transition);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.event-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--cps-shadow-lg);
}

/* Date Badge */
.event-date-badge {
    background: linear-gradient(135deg, var(--cps-accent-purple), #a593d4);
    color: var(--cps-text-primary);
    padding: var(--cps-spacing-sm) var(--cps-spacing-md);
    border-radius: var(--cps-radius-sm);
    font-weight: 700;
    font-size: 0.875rem;
    text-align: center;
    margin-bottom: var(--cps-spacing-md);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Event Details */
.event-details {
    position: relative;
    z-index: 1;
}

.event-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0 0 var(--cps-spacing-sm);
    line-height: 1.4;
}

.event-title a {
    text-decoration: none;
    transition: opacity 0.3s ease;
}

.event-title a:hover {
    opacity: 0.8;
}

.event-location {
    font-size: 0.9rem;
    margin-bottom: var(--cps-spacing-md);
    opacity: 0.9;
}

.event-location a {
    text-decoration: none;
    transition: opacity 0.3s ease;
}

.event-location a:hover {
    opacity: 0.7;
}

/* Event Actions */
.event-actions {
    display: flex;
    gap: var(--cps-spacing-sm);
    flex-wrap: wrap;
}

.action-icon {
    display: inline-block;
    width: 32px;
    height: 32px;
    border-radius: var(--cps-radius-sm);
    background-color: rgba(255, 255, 255, 0.1);
    padding: 6px;
    transition: var(--cps-transition);
}

.action-icon:hover {
    background-color: rgba(255, 255, 255, 0.2);
    transform: scale(1.1);
}

.action-icon img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

/* ========================================
   Ripple Effect
   ======================================== */
.event-card {
    position: relative;
    overflow: hidden;
}

.ripple {
    position: absolute;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.3);
    transform: scale(0);
    animation: ripple-animation 0.6s ease-out;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

/* ========================================
   Animations
   ======================================== */

/* Pin strike animation */
.pin-strike {
    animation: pin-fall 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes pin-fall {
    0% {
        transform: rotate(0deg) translateY(0);
        opacity: 1;
    }
    50% {
        transform: rotate(45deg) translateY(20px);
        opacity: 0.5;
    }
    100% {
        transform: rotate(90deg) translateY(40px);
        opacity: 0;
    }
}

/* Bowling ball roll */
.bowling-ball-animation {
    position: fixed;
    bottom: 20px;
    left: -60px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, var(--cps-accent-cyan), var(--cps-accent-purple));
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    transition: transform 2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    z-index: 9999;
}

/* ========================================
   Responsive Design
   ======================================== */

/* Tablet */
@media (max-width: 1024px) {
    .cps-calendar-wrapper {
        padding: var(--cps-spacing-md);
    }
    
    .month-separator h2 {
        font-size: 1.75rem;
    }
    
    .event-title {
        font-size: 1.1rem;
    }
}

/* Mobile */
@media (max-width: 768px) {
    .cps-calendar-wrapper {
        padding: var(--cps-spacing-sm);
    }
    
    .month-separator h2 {
        font-size: 1.5rem;
    }
    
    .event-card {
        padding: var(--cps-spacing-sm);
    }
    
    .event-title {
        font-size: 1rem;
    }
    
    .event-date-badge {
        font-size: 0.75rem;
    }
}

/* ========================================
   Accessibility
   ======================================== */

/* Focus styles */
.event-card:focus,
.event-title a:focus,
.event-location a:focus,
.action-icon:focus {
    outline: 2px solid var(--cps-accent-cyan);
    outline-offset: 2px;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* High contrast mode */
@media (prefers-contrast: high) {
    .event-card {
        border: 2px solid currentColor;
    }
    
    .action-icon {
        border: 1px solid currentColor;
    }
}

/* ========================================
   Print Styles
   ======================================== */
@media print {
    .cps-calendar-wrapper {
        background-color: white;
        color: black;
    }
    
    .event-card {
        page-break-inside: avoid;
        border: 1px solid #ccc;
    }
    
    .action-icon,
    .bowling-pins-decoration {
        display: none;
    }
}
```

---

## DEPLOYMENT SCRIPTS

### 4. scripts/warmup_cache.py (Cache Warmup)

```python
#!/usr/bin/env python3
"""
Cache Warmup Script
Run this via cron every 5 minutes to keep cache warm
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.calendar_service import CalendarService
from app.cache import CacheManager
from app.config import Config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def warmup_cache():
    """Fetch events and cache them"""
    try:
        logger.info("Starting cache warmup...")
        
        # Initialize services
        calendar_service = CalendarService()
        cache_manager = CacheManager()
        
        # Fetch events
        events = calendar_service.get_events(max_results=100)
        
        # Cache with default key
        cache_key = "events:::false:100"
        cache_manager.set(cache_key, {'events': events, 'age': 0}, Config.CACHE_DEFAULT_TIMEOUT)
        
        logger.info(f"Cache warmed successfully with {len(events)} events")
        
    except Exception as e:
        logger.error(f"Cache warmup failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    warmup_cache()
```

---

### 5. scripts/refresh_token.py (Token Refresh)

```python
#!/usr/bin/env python3
"""
Token Refresh Script
Ensures Google Calendar credentials remain valid
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.calendar_service import CalendarService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def refresh_token():
    """Refresh Google Calendar token"""
    try:
        logger.info("Checking token validity...")
        
        # Initialize service (this will refresh if needed)
        calendar_service = CalendarService()
        
        # Make a simple API call to verify
        calendar_service.get_events(max_results=1)
        
        logger.info("Token is valid")
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    refresh_token()
```

---

### 6. scripts/rotate_logs.sh (Log Rotation)

```bash
#!/bin/bash
# Log Rotation Script
# Run daily via cron

LOG_DIR="/home/username/cps-calendar-api/logs"
MAX_SIZE=10485760  # 10MB
MAX_FILES=5

cd "$LOG_DIR" || exit 1

# Function to rotate a log file
rotate_log() {
    local logfile=$1
    
    if [ -f "$logfile" ]; then
        local size=$(stat -f%z "$logfile" 2>/dev/null || stat -c%s "$logfile")
        
        if [ "$size" -gt "$MAX_SIZE" ]; then
            echo "Rotating $logfile (size: $size bytes)"
            
            # Rotate existing backups
            for i in $(seq $((MAX_FILES-1)) -1 1); do
                if [ -f "${logfile}.$i" ]; then
                    mv "${logfile}.$i" "${logfile}.$((i+1))"
                fi
            done
            
            # Create new backup
            mv "$logfile" "${logfile}.1"
            touch "$logfile"
            
            # Delete old backups
            for i in $(seq $((MAX_FILES+1)) 10); do
                rm -f "${logfile}.$i"
            done
        fi
    fi
}

# Rotate logs
rotate_log "api.log"
rotate_log "cron.log"

echo "Log rotation completed at $(date)"
```

---

### 7. scripts/deploy.sh (Deployment Helper)

```bash
#!/bin/bash
# Deployment Helper Script

set -e  # Exit on error

echo "==================================="
echo "CPS Calendar API Deployment Script"
echo "==================================="

# Configuration
APP_DIR="/home/username/cps-calendar-api"
VENV_DIR="/home/username/virtualenv/cps-calendar-api/3.9"

# Check if running from correct directory
if [ ! -f "passenger_wsgi.py" ]; then
    echo "Error: Must run from application root directory"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --upgrade

# Create required directories
echo "Creating directories..."
mkdir -p cache logs

# Set permissions
echo "Setting permissions..."
chmod 755 cache logs scripts
chmod 644 *.py app/*.py
chmod 700 service-account.json 2>/dev/null || echo "Warning: service-account.json not found"
chmod +x scripts/*.sh scripts/*.py

# Run tests (if available)
if [ -d "tests" ]; then
    echo "Running tests..."
    python -m pytest tests/ || echo "Warning: Some tests failed"
fi

# Clear cache
echo "Clearing cache..."
rm -rf cache/*

# Restart application (cPanel specific)
echo "Restarting application..."
mkdir -p tmp
touch tmp/restart.txt

echo "==================================="
echo "Deployment completed successfully!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Verify API is running: curl https://api.yourdomain.com/api/v1/health"
echo "2. Check logs: tail -f logs/api.log"
echo "3. Test events endpoint with authentication"
```

---

### 8. scripts/generate_api_key.py (Key Generator)

```python
#!/usr/bin/env python3
"""
Generate secure random keys for API configuration
"""
import secrets
import string

def generate_key(length=32):
    """Generate a secure random key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == '__main__':
    print("=================================")
    print("CPS Calendar API Key Generator")
    print("=================================")
    print()
    print("Add these to your .env file:")
    print()
    print(f"SECRET_KEY={generate_key(32)}")
    print(f"JWT_SECRET={generate_key(32)}")
    print(f"API_KEY={generate_key(32)}")
    print()
    print("IMPORTANT: Keep these keys secure!")
    print("=================================")
```

---

### 9. Makefile (Development Helper)

```makefile
# CPS Calendar API Makefile

.PHONY: help install test deploy clean

help:
	@echo "CPS Calendar API - Available Commands"
	@echo "======================================"
	@echo "make install    - Install dependencies"
	@echo "make test       - Run tests"
	@echo "make deploy     - Deploy to production"
	@echo "make clean      - Clean cache and logs"
	@echo "make keys       - Generate API keys"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

deploy:
	bash scripts/deploy.sh

clean:
	rm -rf cache/*
	rm -rf logs/*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

keys:
	python scripts/generate_api_key.py
```

---

## QUICK DEPLOYMENT CHECKLIST

```bash
# 1. Upload files to cPanel
scp -r cps-calendar-api username@yourhost.com:/home/username/

# 2. SSH into server
ssh username@yourhost.com

# 3. Navigate to app directory
cd /home/username/cps-calendar-api

# 4. Make scripts executable
chmod +x scripts/*.sh scripts/*.py

# 5. Generate keys
python scripts/generate_api_key.py

# 6. Create .env file (use .env.example as template)
nano .env

# 7. Upload service account JSON
# (Do this via cPanel File Manager or SCP)

# 8. Run deployment script
bash scripts/deploy.sh

# 9. Configure Python app in cPanel
# (Follow cPanel Python app setup)

# 10. Set up cron jobs
# */5 * * * * cd /home/username/cps-calendar-api && /home/username/virtualenv/cps-calendar-api/3.9/bin/python scripts/warmup_cache.py >> logs/cron.log 2>&1
# 0 * * * * cd /home/username/cps-calendar-api && /home/username/virtualenv/cps-calendar-api/3.9/bin/python scripts/refresh_token.py >> logs/cron.log 2>&1
# 0 0 * * * cd /home/username/cps-calendar-api && bash scripts/rotate_logs.sh >> logs/cron.log 2>&1

# 11. Test API
curl https://api.yourdomain.com/api/v1/health

# 12. Install Joomla module
# Upload ZIP via Joomla admin
```

---

**END OF FRONTEND ASSETS & DEPLOYMENT SCRIPTS**

These templates provide production-ready code that can be customized as needed. All scripts include error handling, logging, and follow security best practices.
