#!/bin/bash
# Quick setup script for Research Paper Agent

echo "🔬 Research Paper Agent — Quick Setup"
echo "======================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first."
    exit 1
fi

# Check if we're in the right folder
if [ ! -f "agent.py" ]; then
    echo "❌ agent.py not found. Please run this script from the project folder."
    exit 1
fi

echo "✅ Git found"
echo "✅ agent.py found"
echo ""

# Initialize and push
git init
git add .
git commit -m "Initial commit: Research Paper Agent"

read -p "Enter your GitHub repo URL (e.g., https://github.com/ahsanfiaz15/research-paper-agent.git): " REPO_URL

git remote add origin "$REPO_URL"
git branch -M main
git push -u origin main

echo ""
echo "🎉 Code pushed successfully!"
echo ""
echo "Next steps:"
echo "1. Go to your repo on GitHub"
echo "2. Settings → Secrets and variables → Actions"
echo "3. Add these 3 secrets:"
echo "   - EMAIL_SENDER = ahsan.firebase15@gmail.com"
echo "   - EMAIL_PASSWORD = olvq jmzs ezly pdpu"
echo "   - EMAIL_RECIPIENT = ahsan.firebase15@gmail.com"
echo ""
echo "4. Go to Actions tab → Run workflow manually to test!"
