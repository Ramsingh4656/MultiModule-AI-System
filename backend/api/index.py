"""
Vercel Serverless Function Entry Point for FastAPI Backend
This file wraps the FastAPI app for Vercel's serverless environment
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import configuration and routes
from config import settings
from database.database import init_db

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

# Configure CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Vercel
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

# Root endpoint
@app.get("/api")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Productivity Suite API",
        "version": settings.VERSION,
        "docs": "/api/docs",
        "status": "running"
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION
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

# Initialize database on cold start
try:
    init_db()
except Exception as e:
    print(f"Database initialization warning: {e}")

# Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
