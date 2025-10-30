const express = require('express');
const cors = require('cors');
const fs = require('fs');
const app = express();

app.use(cors());

const COLORS = {
    'undefined': '#039be5', '1': '#7986cb', '2': '#33b679', '3': '#8e24aa',
    '4': '#e67c73', '5': '#f6c026', '6': '#f5511d', '7': '#039be5',
    '8': '#616161', '9': '#3f51b5', '10': '#0b8043', '11': '#d60000'
};

function luminance(hex) {
    hex = hex.replace('#', '');
    const r = parseInt(hex.substring(0, 2), 16) / 255;
    const g = parseInt(hex.substring(2, 4), 16) / 255;
    const b = parseInt(hex.substring(4, 6), 16) / 255;
    const calc = (c) => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    return 0.2126 * calc(r) + 0.7152 * calc(g) + 0.0722 * calc(b);
}

function textColor(bg) {
    return luminance(bg) > 0.5 ? '#000000' : '#FFFFFF';
}

function extractLocation(loc) {
    return loc ? loc.split(',')[0].trim() : 'No Location';
}

function extractUrls(desc) {
    if (!desc) return { tenpin: '', other: '' };
    const regex = /href="(https?:\/\/[^"]+)"/g;
    let tenpin = '', other = '', match;
    while ((match = regex.exec(desc))) {
        if (match[1].includes('tenpinresults')) tenpin = match[1];
        else other = match[1];
    }
    return { tenpin, other };
}

let calendar = null;
let calendarError = null;

try {
    const { google } = require('googleapis');
    const credentials = JSON.parse(fs.readFileSync('./credentials.json'));
    const token = JSON.parse(fs.readFileSync('./token.json'));
    
    const oauth2Client = new google.auth.OAuth2(
        credentials.installed.client_id,
        credentials.installed.client_secret,
        credentials.installed.redirect_uris[0]
    );
    
    oauth2Client.setCredentials(token);
    calendar = google.calendar({ version: 'v3', auth: oauth2Client });
} catch (err) {
    calendarError = err.message;
    console.error('Calendar init failed:', err);
}

app.get('/api', (req, res) => {
    res.send('<h1>CPS Calendar API</h1><p>Status: Running</p>');
});

app.get('/api/', (req, res) => {
    res.send('<h1>CPS Calendar API</h1><p>Status: Running</p>');
});

app.get('/api/v1/health', (req, res) => {
    res.json({ 
        status: 'ok',
        calendar: calendar ? 'initialized' : 'failed',
        error: calendarError || null
    });
});

app.get('/api/v1/events', async (req, res) => {
    if (!calendar) {
        return res.status(500).json({ 
            success: false, 
            error: 'Calendar not initialized: ' + calendarError 
        });
    }
    
    try {
        const response = await calendar.events.list({
            calendarId: 'tyson@cornerpins.com.au',
            timeMin: new Date().toISOString(),
            singleEvents: true,
            orderBy: 'startTime',
            maxResults: 100
        });
        
        const events = (response.data.items || []).map(e => {
            const colorId = e.colorId || 'undefined';
            const bg = COLORS[colorId];
            const urls = extractUrls(e.description);
            
            return {
                id: e.id,
                summary: e.summary || 'No Title',
                start: e.start,
                end: e.end,
                location: e.location || '',
                locationShort: extractLocation(e.location),
                htmlLink: e.htmlLink,
                backgroundColor: bg,
                textColor: textColor(bg),
                urls: { tenpinResults: urls.tenpin, other: urls.other },
                attachments: e.attachments || []
            };
        });
        
        res.json({ success: true, data: events });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log('API running on port ' + PORT);
});