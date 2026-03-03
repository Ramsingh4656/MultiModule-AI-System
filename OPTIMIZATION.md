# Vercel Serverless Optimization Guide

## Cold Start Optimization

### Problem
Serverless functions have "cold starts" - the first request after inactivity takes longer because the function needs to initialize.

### Solutions Implemented

#### 1. Lazy Loading (Recommended)
```python
# Instead of loading all services at startup
from services.chatbot_service import ChatbotService
chatbot = ChatbotService()  # Loads immediately

# Use lazy loading
from services.lazy_loader import lazy_loader
chatbot = lazy_loader.get_chatbot_service()  # Loads only when called
```

#### 2. Model Caching
Models are cached between warm invocations using `@lru_cache`:
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_model():
    return load_heavy_model()
```

#### 3. Lightweight Models
- Using `distilgpt2` instead of full GPT-2 (40% smaller)
- Consider switching to API-based models for production:
  - OpenAI GPT-3.5/4
  - Anthropic Claude
  - Google PaLM

### Cold Start Times
- **Without optimization**: 15-30 seconds
- **With lazy loading**: 3-5 seconds (first endpoint)
- **Warm invocations**: <1 second

## Memory Optimization

### Current Configuration
```json
{
  "functions": {
    "api/index.py": {
      "memory": 3008,  // 3GB for AI models
      "maxDuration": 60  // 60 seconds timeout
    }
  }
}
```

### Memory Usage by Module
- **Chatbot**: ~500MB (DistilGPT-2 model)
- **Spam Detection**: ~50MB (scikit-learn)
- **Resume Analysis**: ~100MB (NLTK + PyPDF2)
- **Text Summarization**: ~100MB (NLTK)

### Optimization Tips
1. **Reduce memory allocation** if not using chatbot:
   ```json
   "memory": 1024  // 1GB sufficient without AI models
   ```

2. **Split heavy endpoints** into separate functions:
   ```
   /api/chatbot/index.py  // Heavy (3GB)
   /api/spam/index.py     // Light (512MB)
   ```

## Database Optimization

### SQLite Limitations
- Data stored in `/tmp` (ephemeral)
- Lost on cold starts
- Not suitable for production

### PostgreSQL Setup (Recommended)

#### Option 1: Vercel Postgres
```bash
# In Vercel Dashboard
1. Go to Storage tab
2. Create Postgres Database
3. Copy connection string
4. Add to Environment Variables: DATABASE_URL
```

#### Option 2: External Provider
- **Supabase**: Free tier with 500MB
- **Neon**: Serverless Postgres
- **Railway**: Simple deployment
- **AWS RDS**: Enterprise solution

#### Update Configuration
```python
# backend/config.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:pass@host:5432/dbname"
)
```

## File Storage Optimization

### Current: Ephemeral Storage
```python
UPLOAD_DIR = Path("/tmp/uploads")  # Lost on cold start
```

### Solution: Persistent Storage

#### Option 1: Vercel Blob Storage
```bash
npm install @vercel/blob
```

```python
from vercel_blob import put, get

# Upload file
blob = await put('resume.pdf', file_content, {
    'access': 'public',
    'token': os.getenv('BLOB_READ_WRITE_TOKEN')
})

# Get URL
url = blob['url']
```

#### Option 2: AWS S3
```python
import boto3

s3 = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)

s3.upload_fileobj(file, 'bucket-name', 'resume.pdf')
```

#### Option 3: Cloudinary
```python
import cloudinary.uploader

result = cloudinary.uploader.upload(file,
    folder="resumes",
    resource_type="raw"
)
```

## API Response Optimization

### 1. Enable Compression
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 2. Add Caching Headers
```python
from fastapi.responses import JSONResponse

@app.get("/api/data")
async def get_data():
    return JSONResponse(
        content={"data": "value"},
        headers={
            "Cache-Control": "public, max-age=3600",
            "CDN-Cache-Control": "public, max-age=86400"
        }
    )
```

### 3. Pagination
```python
@app.get("/api/items")
async def get_items(skip: int = 0, limit: int = 10):
    return items[skip:skip + limit]
```

## Frontend Optimization

### 1. Code Splitting
```javascript
// Lazy load pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Chatbot = lazy(() => import('./pages/Chatbot'));
```

### 2. Image Optimization
```javascript
// Use Vercel Image Optimization
import Image from 'next/image'  // If using Next.js

// Or optimize manually
<img 
  src="/image.jpg" 
  loading="lazy" 
  width="800" 
  height="600"
/>
```

### 3. Bundle Size Reduction
```bash
# Analyze bundle
npm run build -- --analyze

# Remove unused dependencies
npm prune
```

## Monitoring & Debugging

### 1. Enable Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Function invoked")
```

### 2. View Logs
```bash
# Real-time logs
vercel logs YOUR_DEPLOYMENT_URL --follow

# Filter by function
vercel logs YOUR_DEPLOYMENT_URL --filter=api/index.py
```

### 3. Performance Monitoring
```python
import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Cost Optimization

### Vercel Pricing Tiers
- **Hobby**: Free (100GB bandwidth, 100 hours function execution)
- **Pro**: $20/month (1TB bandwidth, 1000 hours execution)
- **Enterprise**: Custom pricing

### Reduce Costs
1. **Cache aggressively**: Reduce function invocations
2. **Optimize cold starts**: Faster = cheaper
3. **Use Edge Functions**: For simple endpoints (faster, cheaper)
4. **Compress responses**: Reduce bandwidth usage
5. **Implement rate limiting**: Prevent abuse

### Edge Functions Example
```python
# api/health.py (Edge Function)
def handler(request):
    return {
        'statusCode': 200,
        'body': '{"status": "healthy"}'
    }
```

```json
// vercel.json
{
  "functions": {
    "api/health.py": {
      "runtime": "edge"
    }
  }
}
```

## Security Optimization

### 1. Environment Variables
```bash
# Never commit secrets
# Add in Vercel Dashboard -> Settings -> Environment Variables

SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://...
AWS_ACCESS_KEY=...
```

### 2. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/endpoint")
@limiter.limit("10/minute")
async def endpoint():
    return {"data": "value"}
```

### 3. CORS Configuration
```python
# Development: Allow all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

# Production: Restrict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://www.your-domain.com"
    ]
)
```

## Testing Before Deployment

### 1. Local Testing
```bash
# Install Vercel CLI
npm install -g vercel

# Run locally
vercel dev
```

### 2. Preview Deployments
```bash
# Deploy to preview URL
vercel

# Test preview URL before production
# Then deploy to production
vercel --prod
```

### 3. Load Testing
```bash
# Install Apache Bench
apt-get install apache2-utils

# Test endpoint
ab -n 1000 -c 10 https://your-app.vercel.app/api/health
```

## Troubleshooting Common Issues

### Issue: Function Timeout
```
Error: Function execution timed out after 60 seconds
```

**Solution**: Increase timeout or optimize code
```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 300  // 5 minutes (Pro plan only)
    }
  }
}
```

### Issue: Out of Memory
```
Error: Function exceeded memory limit
```

**Solution**: Increase memory or optimize
```json
{
  "functions": {
    "api/index.py": {
      "memory": 3008  // Maximum available
    }
  }
}
```

### Issue: Module Not Found
```
ModuleNotFoundError: No module named 'transformers'
```

**Solution**: Verify requirements.txt
```bash
# Ensure all dependencies are listed
pip freeze > api/requirements.txt
```

### Issue: Database Connection Failed
```
Error: could not connect to server
```

**Solution**: Check DATABASE_URL environment variable
```bash
# Verify in Vercel Dashboard
# Format: postgresql://user:pass@host:5432/dbname
```

## Performance Benchmarks

### Target Metrics
- **Cold Start**: <5 seconds
- **Warm Response**: <1 second
- **API Latency**: <500ms
- **Frontend Load**: <2 seconds
- **Time to Interactive**: <3 seconds

### Monitoring Tools
- Vercel Analytics (built-in)
- Google Lighthouse
- WebPageTest
- New Relic
- Datadog

## Recommended Architecture for Scale

```
┌─────────────────┐
│   Vercel CDN    │  (Frontend + Static Assets)
└────────┬────────┘
         │
┌────────▼────────┐
│  Edge Functions │  (Health checks, simple APIs)
└────────┬────────┘
         │
┌────────▼────────┐
│ Serverless API  │  (FastAPI + Mangum)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ DB   │  │ Blob │  (Vercel Postgres + Blob Storage)
└──────┘  └──────┘
```

## Next Steps

1. ✅ Deploy to Vercel
2. ⚡ Implement lazy loading
3. 🗄️ Migrate to PostgreSQL
4. 📦 Set up blob storage
5. 📊 Enable monitoring
6. 🔒 Configure security
7. 🚀 Optimize performance
8. 💰 Monitor costs

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/)
- [Mangum Documentation](https://mangum.io/)
- [Serverless Best Practices](https://www.serverless.com/blog/serverless-best-practices)
