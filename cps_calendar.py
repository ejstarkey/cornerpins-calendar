import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import time
import os
from pathlib import Path
import pickle
from dateutil.parser import parse
import re
import ftplib

# Scopes required
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_ID = 'tyson@cornerpins.com.au'  # Replace with your actual calendar ID
CREDENTIALS_FILE = Path('credentials.json')  # Path to your credentials file
TOKEN_FILE = Path('token.pickle')
REDIRECT_URI = 'https://atherton.nqtenpin.com.au'  # Replace with your redirect URI

def format_date(date_str):
    date_obj = parse(date_str).date()
    return date_obj.strftime('%d %b')

def extract_location_name(location):
    if not location:
        return 'No Location'
    return location.split(',')[0].strip()

def extract_hyperlinks(description):
    # Returns all URLs and specifically tenpinresults URL if present
    urls = re.findall(r'href="(https?://\S+)"', description)
    tenpin_url = ''
    other_url = ''
    for url in urls:
        if "tenpinresults" in url:
            tenpin_url = url
        else:
            other_url = url  # Assumes last found URL if multiple
    return tenpin_url, other_url

def fetch_colors():
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

def luminance(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    def channel_luminance(channel):
        channel /= 255
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel_luminance(rgb[0]) + 0.7152 * channel_luminance(rgb[1]) + 0.0722 * channel_luminance(rgb[2])

def text_color_for_background(bg_color):
    return '#000000' if luminance(bg_color) > 0.5 else '#FFFFFF'

def fetch_and_generate_html(service, colors):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    html_content = '''
    <html>
    <head>
        <link rel="stylesheet" type="text/css" href="/events-calendar/css/calendar_style.css">
        <style>
            .event-container { position: relative; }
            .redirect-banner { display: none; background-color: red; color: white; text-align: center; padding: 10px; width: 100%; position: absolute; top: 0; left: 0; z-index: 1001; animation: blinker 1s linear infinite; }
            @keyframes blinker { 50% { opacity: 0; } }
            ul { list-style-type: none; padding: 0; margin: 0; }
            .event { background-color: #ffffff; margin-bottom: 10px; padding: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .event div { display: flex; align-items: center; justify-content: center; }
            .icon-container { display: flex; gap: 5px; }
            /* Style for the month/year separator */
            .month-separator {
                text-align: center;
                margin: 20px 0;
                font-weight: bold;
                font-size: 1.5em;
                color: #333;
            }
            @media (min-width: 601px) { .event { display: grid; grid-template-columns: auto auto auto auto; } }
            @media (max-width: 600px) { .event { display: flex; flex-direction: column; } }
        </style>
<script>
    function handleClick(url, eventContainerId, event) {
        event.preventDefault();
        var redirectBanner = document.getElementById('redirectBanner-' + eventContainerId);
        redirectBanner.style.display = 'block';
        setTimeout(function() {
            window.open(url, '_blank');
            redirectBanner.style.display = 'none';
        }, 5000);
    }
</script>
    </head>
    <body>
        <ul>
    '''
    last_month_year = None
    page_token = None
    while True:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            pageToken=page_token,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        if not events:
            break
        
        for index, event in enumerate(events):
            event_start_str = event['start'].get('dateTime', event['start'].get('date'))
            event_start_dt = parse(event_start_str)
            # Format as "Month YY" (e.g., "February 25" for February 2025)
            current_month_year = event_start_dt.strftime("%B %y")
            if current_month_year != last_month_year:
                html_content += f'<div class="month-separator"><h2>{current_month_year}</h2></div>'
                last_month_year = current_month_year

            event_container_id = f"event-container-{index}"
            
            start_date = format_date(event_start_str)
            end_date = format_date(event['end'].get('dateTime', event['end'].get('date')))
            date_range = f'{start_date} to {end_date}' if start_date != end_date else start_date
            summary = event.get('summary', 'No Title')
            event_link = f'<a href="{event.get("htmlLink")}" style="text-decoration: none; color: inherit;" onclick="handleClick(\'{event.get("htmlLink")}\', \'{event_container_id}\', event);">{summary}</a>'
            
            location = extract_location_name(event.get('location', ''))
            location_link = f'<a href="http://maps.google.com/?q={location}" onclick="handleClick(\'http://maps.google.com/?q={location}\', \'{event_container_id}\', event);">{location}</a>' if location != 'No Location' else 'No Location'
            
            description = event.get('description', '')
            tenpin_url, other_url = extract_hyperlinks(description)
            tenpin_html = f'<a href="{tenpin_url}" target="_blank" onclick="handleClick(\'{tenpin_url}\', \'{event_container_id}\', event);"><img src="register.png" alt="Register" style="border:0;"></a>' if tenpin_url else ''
            other_url_html = f'<a href="{other_url}" target="_blank" onclick="handleClick(\'{other_url}\', \'{event_container_id}\', event);"><img src="link.png" alt="Link" style="border:0;"></a>' if other_url else ''
            
            attachment_links = ''
            if 'attachments' in event:
                for attachment in event['attachments']:
                    if 'fileUrl' in attachment:
                        if 'pattern' in attachment['title'].lower():
                            attachment_links += f'<a href="{attachment["fileUrl"]}" target="_blank" onclick="handleClick(\'{attachment["fileUrl"]}\', \'{event_container_id}\', event);"><img src="pattern.png" alt="Pattern" style="border:0;"></a>'
                        else:
                            attachment_links += f'<a href="{attachment["fileUrl"]}" target="_blank" onclick="handleClick(\'{attachment["fileUrl"]}\', \'{event_container_id}\', event);"><img src="entry.png" alt="Attachment" style="border:0;"></a>'
            
            event_color = colors.get(event.get('colorId'), '#ffffff')
            text_color = text_color_for_background(event_color)
            
            icons_html = ''.join([tenpin_html, other_url_html, attachment_links])
            icon_container_html = f'<div class="icon-container">{icons_html}</div>' if icons_html else ''
            
            redirect_banner_html = f'<div id="redirectBanner-{event_container_id}" class="redirect-banner">Redirecting, please ensure popups are enabled...</div>'
            
            html_content += f'''
            <div id="{event_container_id}" class="event-container">
                {redirect_banner_html}
                <li class="event" style="background-color: {event_color}; color: {text_color};">
                    <div>{date_range}</div>
                    <div>{event_link}</div>
                    <div>{location_link}</div>
                    {icon_container_html}
                </li>
            </div>
            '''
        
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break
    
    html_content += '</ul></body></html>'
    upload_html_to_ftp(html_content)

def upload_html_to_ftp(html_content):
    try:
        # Read FTP credentials from the credentials file
        with open('credentials', 'r') as f:
            credentials = f.read().strip().split('\n')
        ftp_host = credentials[0]
        ftp_user = credentials[1]
        ftp_pass = credentials[2]
        ftp_path = credentials[3]

        # Connect and upload the file
        ftp = ftplib.FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        ftp.cwd(ftp_path)

        # Write HTML content to a file
        temp_html_file = Path('calendar.html')
        temp_html_file.write_text(html_content)

        # Upload the HTML content
        with temp_html_file.open('rb') as f:
            ftp.storbinary('STOR calendar.html', f)
        
        ftp.quit()
        temp_html_file.unlink()  # Remove the temporary file

    except ftplib.all_errors as e:
        print(f"FTP error: {e}")

def load_credentials():
    creds = None
    if TOKEN_FILE.exists():
        with TOKEN_FILE.open('rb') as token:
            creds = pickle.load(token)
    return creds

def save_credentials(creds):
    with TOKEN_FILE.open('wb') as token:
        pickle.dump(creds, token)

def authenticate_google_calendar():
    creds = load_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        save_credentials(creds)
    return build('calendar', 'v3', credentials=creds)

def main():
    try:
        service = authenticate_google_calendar()
        colors = fetch_colors()
        while True:
            fetch_and_generate_html(service, colors)
            time.sleep(15)  # Interval between updates
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

