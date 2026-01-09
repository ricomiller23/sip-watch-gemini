#!/bin/bash
cd "$(dirname "$0")"

echo "=========================================="
echo "   SIP WATCH GEMINI - SETUP & DEPLOY"
echo "=========================================="
echo ""

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not found."
    echo "👉 Please install the Xcode Command Line Tools when prompted, or download Python from python.org"
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

echo "✅ Python 3 found."

# 2. Check for Pip/Dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Pip install failed. You might need to run 'python3 -m ensurepip' or install pip manually."
else
    echo "✅ Dependencies installed."
fi

# 3. Git Setup
if [ ! -d ".git" ]; then
    echo ""
    echo "--- GitHub Setup ---"
    read -p "Do you want to initialize a Git repository and push to GitHub? (y/n): " DO_GIT
    if [[ "$DO_GIT" =~ ^[Yy]$ ]]; then
        git init
        git add .
        git commit -m "Initial commit of Sip Watch Gemini"
        git branch -M main
        echo "Please create a repository on GitHub (https://github.com/new) and copy the HTTPS URL."
        read -p "Enter your GitHub Repository URL: " REPO_URL
        if [ ! -z "$REPO_URL" ]; then
            git remote add origin "$REPO_URL"
            git push -u origin main
        else
            echo "Skipping push (No URL provided)."
        fi
    fi
fi

# 4. Vercel Deploy
echo ""
echo "--- Vercel Deployment ---"
if ! command -v vercel &> /dev/null; then
    echo "First, we need to install Vercel CLI."
    if command -v npm &> /dev/null; then
        npm install -g vercel
    else
        echo "❌ NPM not found. Cannot install Vercel CLI automaticallly."
        echo "👉 Please install Node.js from https://nodejs.org/"
    fi
fi

if command -v vercel &> /dev/null; then
    read -p "Ready to deploy to Vercel? (y/n): " DO_DEPLOY
    if [[ "$DO_DEPLOY" =~ ^[Yy]$ ]]; then
        vercel login
        vercel
    fi
else
    echo "⚠️  Vercel CLI missing. Skipping deployment."
fi

echo ""
echo "=========================================="
echo "   DONE! "
echo "=========================================="
echo "To run locally: python3 test_local.py"
echo "Press any key to close..."
read -n 1
