import sys
import os

# Add current directory to path so we can import api.cron
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api.cron import fetch_news, fetch_reddit_sentiment, analyze_and_report, send_notification
except ImportError:
    # Handle case where user runs from inside api/ folder
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    from api.cron import fetch_news, fetch_reddit_sentiment, analyze_and_report, send_notification

def main():
    print("=== SIP WATCH Gemini: Local Test Runner ===")
    
    # Check for keys, prompt if missing
    if not os.environ.get("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = input("Enter Gemini API Key: ").strip()
        
    if not os.environ.get("NEWS_API_KEY"):
        print("Note: You can get a free key at newsapi.org")
        os.environ["NEWS_API_KEY"] = input("Enter NewsAPI Key (press Enter to skip): ").strip()

    if not os.environ.get("RESEND_API_KEY"):
        os.environ["RESEND_API_KEY"] = input("Enter Resend API Key (press Enter to skip Email): ").strip()
        if os.environ["RESEND_API_KEY"]:
             os.environ["RECIPIENT_EMAIL"] = input("Enter Recipient Email: ").strip()

    print("\n[1/3] Fetching Data...")
    news = fetch_news()
    print(f"  > Fetched {len(news.splitlines())} news items.")
    
    social = fetch_reddit_sentiment()
    print(f"  > Fetched content from Reddit.")

    print("\n[2/3] Analyzing with Gemini...")
    from api.cron import genai # Re-import to ensure config is picked up
    if os.environ.get("GEMINI_API_KEY"):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        report = analyze_and_report(news, social)
        print("\n=== GENERATED REPORT ===\n")
        print(report)
        print("\n========================\n")
    else:
        print("Skipping analysis (No Gemini Key).")
        report = "Local Test: No analysis performed."

    print("\n[3/3] Sending Notification...")
    if os.environ.get("RESEND_API_KEY"):
        from api.cron import resend
        resend.api_key = os.environ["RESEND_API_KEY"]
        # Need to re-set the global variable in the module or pass it, 
        # but api.cron uses env var RECIPIENT_EMAIL directly.
        # simpler to just call the function which checks the logic.
        status = send_notification(report)
        print(f"  > {status}")
    else:
        print("Skipping email (No Resend Key).")

    print("\nDone.")

if __name__ == "__main__":
    main()
