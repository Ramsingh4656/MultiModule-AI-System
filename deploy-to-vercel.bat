@echo off
echo 🚀 Vercel Deployment Script
echo ============================
echo.

REM Check if git is initialized
if not exist .git (
    echo 📦 Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit for Vercel deployment"
    echo ✅ Git repository initialized
) else (
    echo ✅ Git repository already exists
)

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 📥 Installing Vercel CLI...
    npm install -g vercel
    echo ✅ Vercel CLI installed
) else (
    echo ✅ Vercel CLI already installed
)

echo.
echo 🔐 Please login to Vercel...
call vercel login

echo.
echo 🚀 Deploying to Vercel...
call vercel

echo.
echo ✅ Deployment complete!
echo.
echo 📝 Next steps:
echo 1. Test your deployment URL
echo 2. Add environment variables in Vercel Dashboard (if needed)
echo 3. Deploy to production with: vercel --prod
echo.
pause
