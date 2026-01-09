from http.server import BaseHTTPRequestHandler
import os
import json
import requests
import google.generativeai as genai
import resend
from datetime import datetime

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")  # Get free key from newsapi.org
# RECIPIENT_EMAIL = "eric@example.com" # Configure this or use env var
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")

# Initialize Clients
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

def fetch_news():
    """Fetches beverage industry news."""
    if not NEWS_API_KEY:
        return "No NewsAPI Key provided. Skipping news fetch."
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "RTD spirits OR energy drink OR wine trends OR beverage industry",
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])[:10] # Top 10 recent articles
        return "\n".join([f"- {a['title']} ({a['source']['name']}): {a['url']}" for a in articles])
    except Exception as e:
        return f"Error fetching news: {e}"

def fetch_reddit_sentiment():
    """Fetches top posts from relevant subreddits (Accessing public JSON)."""
    subreddits = ["energydrinks", "wine", "alcohol"]
    summary = []
    
    headers = {"User-Agent": "SipWatchGemini/1.0"}
    
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                posts = response.json()["data"]["children"]
                summary.append(f"--- r/{sub} ---")
                for post in posts:
                    p = post["data"]
                    summary.append(f"- {p['title']} (Score: {p['score']})")
        except Exception as e:
            summary.append(f"Error reading r/{sub}: {e}")
            
    return "\n".join(summary)

def analyze_and_report(news_data, social_data):
    """Uses Gemini to analyze the data and generate a report."""
    if not GEMINI_API_KEY:
        return "Gemini API Key missing. Cannot analyze."
        
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are SIP WATCH, a 24/7 beverage industry watchdog. 
    Analyze the following raw data streams for RTD spirits, wine, and energy drinks.
    
    Identify:
    1. Emerging Trends
    2. Competitor Moves
    3. Viral Sentiments
    4. Sales/Forecasting implications (based on news)
    
    RAW DATA:
    === INDUSTRY NEWS ===
    {news_data}
    
    === SOCIAL SENTIMENT (REDDIT) ===
    {social_data}
    
    Output a concise, professional executive summary suitable for email. 
    Include a 'Watchlist' of brands or keywords gaining traction.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Analysis Failed: {e}"

def send_notification(content):
    """Sends the report via Email."""
    if not RESEND_API_KEY or not RECIPIENT_EMAIL:
        return "Email configuration missing (Resend API Key or Recipient)."
        
    try:
        r = resend.Emails.send({
            "from": "SipWatch <onboarding@resend.dev>",
            "to": RECIPIENT_EMAIL,
            "subject": f"SIP WATCH Report: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "html": f"<pre>{content}</pre>"
        })
        return f"Email sent: {r}"
    except Exception as e:
        return f"Email failed: {e}"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        # 1. Ingest
        news = fetch_news()
        social = fetch_reddit_sentiment()
        
        # 2. Analyze
        report = analyze_and_report(news, social)
        
        # 3. Notify
        email_status = send_notification(report)
        
        output = f"Execution Complete.\n\nEmail Status: {email_status}\n\nReport:\n{report}"
        self.wfile.write(output.encode('utf-8'))
        return
