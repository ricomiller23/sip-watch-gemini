# SIP WATCH Gemini

A 24/7 Beverage Industry Watchdog powered by Google Gemini.

## Overview
This agent monitors:
- **Industry News**: RTD spirits, energy drinks, wine trends (via NewsAPI).
- **Social Sentiment**: Reddit communities (r/energydrinks, r/wine).

It analyzes this data using **Gemini 1.5 Flash** to identify trends and sends an email report every hour.

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A Vercel Account
- API Keys:
    - [Google AI Studio](https://aistudio.google.com/) (Gemini API)
    - [NewsAPI](https://newsapi.org/)
    - [Resend](https://resend.com/) (for Emails)

### 2. Installation
Open your terminal in this folder and run:
```bash
pip install -r requirements.txt
```

### 3. Local Testing
Run the test script to see it in action immediately:
```bash
python3 test_local.py
```
It will prompt you for your API keys one-by-one.

### 4. Deploying to Vercel
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. Deploy:
   ```bash
   vercel
   ```
3. **Set Environment Variables**:
   Go to your Vercel Project Settings > Environment Variables and add:
   - `GEMINI_API_KEY`
   - `NEWS_API_KEY`
   - `RESEND_API_KEY`
   - `RECIPIENT_EMAIL`

4. **Cron Jobs**:
   Vercel will automatically detect the cron job in `vercel.json` and start running it once deployed.
