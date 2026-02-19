from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import settings
from database.database import init_db
from utils.logger import logger

# Import routers
from routes import resume, spam, summary, chatbot, analytics

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered productivity platform with multiple automation modules",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router, prefix="/api")
app.include_router(spam.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    logger.info("Starting AI Productivity Suite...")
    init_db()
    logger.info("Database initialized")
    logger.info(f"Server running on http://localhost:8000")
    logger.info(f"API docs available at http://localhost:8000/api/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Productivity Suite...")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Productivity Suite API",
        "version": settings.VERSION,
        "docs": "/api/docs",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": "2024-01-01T00:00:00Z"
    }

# API info endpoint
@app.get("/api/info")
async def api_info():
    """Get API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "modules": [
            "Resume Analyzer",
            "Spam/Phishing Detector",
            "Notes Summarizer",
            "AI Chatbot",
            "Analytics Dashboard"
        ],
        "features": {
            "authentication": "JWT-based",
            "ai_model": settings.CHATBOT_MODEL,
            "database": "SQLite (PostgreSQL-ready)"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
