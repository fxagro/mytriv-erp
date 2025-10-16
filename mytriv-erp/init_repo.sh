#!/bin/bash

# MyTriv ERP - GitHub Repository Initialization Script
# This script initializes and pushes the MyTriv ERP project to GitHub

set -e

# Configuration
REPO_URL="https://github.com/fxagro/mytriv-erp.git"
BRANCH_NAME="main"

echo "🧱 Initializing MyTriv ERP repository..."
echo "📁 Repository URL: $REPO_URL"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed. Please install git and try again."
    exit 1
fi

# Check if we're in the correct directory
if [ ! -f "README.md" ] || [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the mytriv-erp root directory."
    exit 1
fi

# Check if .git directory already exists
if [ -d ".git" ]; then
    echo "⚠️  Warning: .git directory already exists."
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 Operation cancelled."
        exit 0
    fi
fi

echo "🚀 Initializing git repository..."

# Initialize git repository
git init
git branch -M $BRANCH_NAME

echo "📦 Adding files to git..."

# Add all files
git add .

echo "💾 Creating initial commit..."

# Create initial commit
git commit -m "🚀 Initial commit - MyTriv ERP full-stack boilerplate

🎯 Features:
✅ Odoo 17 backend with REST API
✅ Next.js 15 React frontend  
✅ PostgreSQL database
✅ Docker containerization
✅ GitHub Actions CI/CD
✅ Complete documentation
✅ Production-ready architecture

🏗️ Stack:
• Frontend: Next.js 15, TypeScript, TailwindCSS, shadcn/ui
• Backend: Odoo 17, Python 3.11, PostgreSQL 15
• DevOps: Docker, Docker Compose, GitHub Actions
• API: RESTful endpoints for all Odoo models

📚 Documentation:
• README.md - Project overview and setup
• ARCHITECTURE.md - System architecture guide
• CONTRIBUTING.md - Contribution guidelines
• MODULE_GUIDE.md - Custom module development

🔧 Quick Start:
docker-compose up

🌐 Repository: $REPO_URL"

echo "🔗 Connecting to GitHub repository..."

# Add remote origin
if git remote get-url origin &> /dev/null; then
    echo "📡 Remote origin already exists. Removing and re-adding..."
    git remote remove origin
fi

git remote add origin $REPO_URL

echo "⬆️  Pushing to GitHub..."

# Push to GitHub
git push -u origin $BRANCH_NAME

echo ""
echo "✅ SUCCESS! MyTriv ERP has been successfully pushed to GitHub!"
echo ""
echo "🌐 Repository URL: $REPO_URL"
echo "📖 Next steps:"
echo "   1. Visit the repository URL above"
echo "   2. Enable GitHub Pages if needed"
echo "   3. Set up branch protection rules"
echo "   4. Configure repository settings"
echo ""
echo "🔧 To start the application locally:"
echo "   docker-compose up"
echo ""
echo "📚 For more information, see the README.md file"
echo ""
echo "🎉 Happy coding with MyTriv ERP!"