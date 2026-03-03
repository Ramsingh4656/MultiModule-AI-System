# Vercel Deployment Guide

## Project Structure for Vercel

```
/
├── api/                    # Backend serverless functions
│   ├── index.py           # FastAPI entry point with Mangum wrapper
│   └── requirements.txt   # Python dependencies
├── backend/               # Backend source code
│   ├── routes/           # API routes
│   ├── services/         # Business logic
│   ├── database/         # Database models
│   └── utils/            # Utilities
├── frontend/             # React frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── vercel.json           # Vercel configuration
└── .vercelignore         # Files to ignore during deployment
```

## Deployment Steps

### 1. Prerequisites
- GitHub account
- Vercel account (sign up at vercel.com)
- Git repository with your code

### 2. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit for Vercel deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 3. Deploy to Vercel

#### Option A: Using Vercel Dashboard (Recommended)
1. Go to https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: Leave empty (uses project root)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `npm install`
5. Add Environment Variables (if needed):
   - `SECRET_KEY`: Your secret key
   - `DATABASE_URL`: PostgreSQL URL (optional, defaults to SQLite)
6. Click "Deploy"

#### Option B: Using Vercel CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

### 4. Verify Deployment

After deployment, test these endpoints:

- **Frontend**: `https://your-project.vercel.app`
- **API Health**: `https://your-project.vercel.app/api/health`
- **API Docs**: `https://your-project.vercel.app/api/docs`
- **API Info**: `https://your-project.vercel.app/api/info`

### 5. Environment Variables in Vercel

Add these in Vercel Dashboard → Settings → Environment Variables:

```
SECRET_KEY=your-production-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/dbname  # Optional
```

## Important Notes

### Serverless Limitations
1. **Cold Starts**: First request may be slow (3-10 seconds) due to model loading
2. **Execution Time**: Max 60 seconds per request (configured in vercel.json)
3. **Memory**: 3GB allocated for AI models (configured in vercel.json)
4. **Storage**: Use `/tmp` directory (ephemeral, cleared between invocations)

### Database Considerations
- **SQLite**: Works but data is lost between cold starts (stored in `/tmp`)
- **PostgreSQL**: Recommended for production (use Vercel Postgres or external provider)
- **Vercel Postgres**: Add from Vercel Dashboard → Storage → Create Database

### AI Model Optimization
- Using `distilgpt2` (lightweight model) to reduce cold start time
- Models are cached between warm invocations
- Consider using external API (OpenAI, Anthropic) for production

### File Uploads
- Files stored in `/tmp` (ephemeral)
- For persistent storage, use:
  - Vercel Blob Storage
  - AWS S3
  - Cloudinary

## Troubleshooting

### Issue: API returns 404
- Check `vercel.json` routes configuration
- Verify API endpoints start with `/api`
- Check Vercel deployment logs

### Issue: Cold start timeout
- Increase `maxDuration` in `vercel.json`
- Consider using smaller AI models
- Use external AI API instead of local models

### Issue: CORS errors
- Verify CORS middleware in `api/index.py`
- Check browser console for specific errors
- Ensure `allow_origins=["*"]` is set

### Issue: Database errors
- Check DATABASE_URL environment variable
- Verify database connection string
- For SQLite, data resets on cold starts (use PostgreSQL)

### Issue: Module import errors
- Verify `PYTHONPATH` in `vercel.json`
- Check all dependencies in `api/requirements.txt`
- Review Vercel build logs

## Performance Optimization

### 1. Reduce Cold Starts
```python
# In api/index.py, lazy load heavy dependencies
from functools import lru_cache

@lru_cache()
def get_model():
    from services.chatbot_service import ChatbotService
    return ChatbotService()
```

### 2. Use Edge Functions (for simple endpoints)
```json
// In vercel.json
{
  "functions": {
    "api/health.py": {
      "runtime": "edge"
    }
  }
}
```

### 3. Enable Caching
```python
# Add cache headers
from fastapi.responses import JSONResponse

@app.get("/api/data")
async def get_data():
    return JSONResponse(
        content={"data": "value"},
        headers={"Cache-Control": "public, max-age=3600"}
    )
```

## Monitoring

### View Logs
```bash
vercel logs YOUR_DEPLOYMENT_URL
```

### View Analytics
- Go to Vercel Dashboard → Your Project → Analytics
- Monitor response times, errors, and usage

## Updating Deployment

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push

# Vercel automatically redeploys on push to main branch
```

## Local Development

```bash
# Backend (from project root)
cd backend
pip install -r requirements.txt
python main.py

# Frontend (from project root)
cd frontend
npm install
npm run dev
```

## Production Checklist

- [ ] Change SECRET_KEY in environment variables
- [ ] Set DEBUG=False
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper CORS origins (not "*")
- [ ] Set up persistent file storage
- [ ] Enable monitoring and logging
- [ ] Test all API endpoints
- [ ] Test frontend functionality
- [ ] Check mobile responsiveness
- [ ] Review security settings
- [ ] Set up custom domain (optional)

## Support

For issues:
1. Check Vercel deployment logs
2. Review browser console errors
3. Test API endpoints directly
4. Verify environment variables
5. Check Vercel status page

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Mangum Documentation](https://mangum.io/)
- [Vite Documentation](https://vitejs.dev/)
