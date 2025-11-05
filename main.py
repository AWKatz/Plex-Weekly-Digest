#pip install plexapi required before running/scheduling script
from plexapi.server import PlexServer
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuration
PLEX_URL = 'http://XXX.XXX.XXX:32400'
PLEX_TOKEN = 'follow these instructions to get your token: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/'
EMAIL_FROM = 'email@gmail.com'
EMAIL_TO = ['email@gmail.com', 'email1@gmail.com']
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'email@gmail.com'
SMTP_PASS = 'XXXXXXX'
DAYS_BACK = 7

# Connect to Plex
plex = PlexServer(PLEX_URL, PLEX_TOKEN)
cutoff = datetime.now() - timedelta(days=DAYS_BACK)

# Collect new media (store full Plex media objects)
new_items = []

for section in plex.library.sections():
    if section.type in ['movie', 'show']:
        for item in section.recentlyAdded():
            if item.addedAt >= cutoff:
                new_items.append(item)
#                new_items.append({
#                    'title': item.title,
#                    'type': section.type,
#                    'added': item.addedAt.strftime('%Y-%m-%d'),
#                    'year': getattr(item, 'year', 'N/A')
#                })

# Count summary
movie_count = sum(1 for item in new_items if item.type == 'movie')
show_count = sum(1 for item in new_items if item.type == 'show')

# Group items by type using item.TYPE
movies = [item for item in new_items if item.type == 'movie']
shows = [item for item in new_items if item.type == 'show']

# Generate dark-themed HTML content
html_content = f"""
<html>
<head>
  <style>
    body {{
      background-color: #1e1e2f;
      color: #f0f0f0;
      font-family: 'Segoe UI', sans-serif;
      padding: 30px;
      line-height: 1.6;
    }}
    h2 {{
      color: #82aaff;
      font-size: 28px;
      margin-bottom: 10px;
    }}
    h3 {{
      color: #f78c6c;
      font-size: 22px;
      margin-top: 40px;
      margin-bottom: 15px;
    }}
    .summary {{
      font-size: 16px;
      margin-bottom: 30px;
      color: #c3c3c3;
    }}
    .item {{
      background-color: #2a2a3d;
      border-radius: 12px;
      padding: 15px;
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      transition: transform 0.2s ease;
    }}
    .item:hover {{
      transform: scale(1.02);
    }}
    .thumb {{
      flex: 0 0 100px;
      margin-right: 20px;
    }}
    .thumb img {{
      border-radius: 8px;
      width: 100px;
      height: 150px;
      object-fit: cover;
    }}
    .details {{
      flex: 1;
      min-width: 200px;
    }}
    .details a {{
      color: #bb86fc;
      font-size: 18px;
      text-decoration: none;
      font-weight: bold;
    }}
    .details a:hover {{
      text-decoration: underline;
    }}
    .description {{
      font-size: 14px;
      margin-top: 8px;
      color: #b0bec5;
    }}
    @media (max-width: 600px) {{
      .item {{
        flex-direction: column;
        align-items: center;
      }}
      .thumb {{
        margin-right: 0;
        margin-bottom: 10px;
      }}
    }}
  </style>
</head>
<body>
  <h2>🎬 Weekly Plex Digest</h2>
  <div class="summary">
    <p><strong>{len(movies)}</strong> new movie(s) and <strong>{len(shows)}</strong> new show(s) added this week to Plex.</p>
  </div>
"""

def render_items(items):
    html = ""
    for item in items:
        thumb_url = item.thumbUrl
        plex_url = item.getWebURL()
        summary = item.summary or "No description available."
        html += f"""
        <div class="item">
          <div class="thumb">
            <a href="{plex_url}">
              <img src="{thumb_url}" alt="{item.title}">
            </a>
          </div>
          <div class="details">
            <a href="{plex_url}">{item.title}</a> ({getattr(item, 'year', 'N/A')})<br>
            <div class="description">{summary}</div>
          </div>
        </div>
        """
    return html

# Movies section
if movies:
    html_content += "<h3>🎥 Movies</h3>"
    html_content += render_items(movies)

# Shows section
if shows:
    html_content += "<h3>📺 TV Shows</h3>"
    html_content += render_items(shows)

if not new_items:
    html_content += "<p>No new media added this week.</p>"

html_content += """
  <p style="margin-top: 40px;">Enjoy!</p>
</body>
</html>
"""

# Send email
msg = MIMEMultipart('alternative')
msg['Subject'] = "Weekly Plex Digest"
msg['From'] = EMAIL_FROM
# Set recipients in the email header
msg['To'] = ", ".join(EMAIL_TO)
msg.attach(MIMEText(html_content, 'html'))

with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

print("✅ Weekly digest email sent successfully.")
