#!/bin/bash

echo "🚀 Vercel Deployment Script"
echo "============================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit for Vercel deployment"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📥 Installing Vercel CLI..."
    npm install -g vercel
    echo "✅ Vercel CLI installed"
else
    echo "✅ Vercel CLI already installed"
fi

echo ""
echo "🔐 Please login to Vercel..."
vercel login

echo ""
echo "🚀 Deploying to Vercel..."
vercel

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Test your deployment URL"
echo "2. Add environment variables in Vercel Dashboard (if needed)"
echo "3. Deploy to production with: vercel --prod"
echo ""
