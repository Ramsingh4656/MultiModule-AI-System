from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from database.database import get_db
from models.models import ActivityLog, ResumeAnalysis, SpamCheck, Summary, ChatMessage

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    # Module usage counts (using demo user ID = 1)
    resume_count = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == 1
    ).count()
    
    spam_count = db.query(SpamCheck).filter(
        SpamCheck.user_id == 1
    ).count()
    
    summary_count = db.query(Summary).filter(
        Summary.user_id == 1
    ).count()
    
    chat_count = db.query(ChatMessage).join(ChatMessage.session).filter(
        ChatMessage.role == "user"
    ).count()
    
    # Recent activity (simplified without activity logs)
    recent_activities = []
    
    return {
        "success": True,
        "stats": {
            "resume_analyses": resume_count,
            "spam_checks": spam_count,
            "summaries_created": summary_count,
            "chat_messages": chat_count,
            "total_activities": resume_count + spam_count + summary_count + chat_count
        },
        "recent_activities": []
    }

@router.get("/usage-by-module")
async def get_usage_by_module(db: Session = Depends(get_db)):
    """Get usage statistics by module"""
    # Get counts for each module (using demo user ID = 1)
    modules = {
        "Resume Analyzer": db.query(ResumeAnalysis).filter(
            ResumeAnalysis.user_id == 1
        ).count(),
        "Spam Detector": db.query(SpamCheck).filter(
            SpamCheck.user_id == 1
        ).count(),
        "Summarizer": db.query(Summary).filter(
            Summary.user_id == 1
        ).count(),
        "AI Chatbot": db.query(ChatMessage).join(ChatMessage.session).filter(
            ChatMessage.role == "user"
        ).count()
    }
    
    return {
        "success": True,
        "usage_by_module": [
            {"module": module, "count": count}
            for module, count in modules.items()
        ]
    }

@router.get("/monthly-usage")
async def get_monthly_usage(db: Session = Depends(get_db)):
    """Get monthly usage statistics"""
    # Simplified - return empty data for now
    return {
        "success": True,
        "monthly_usage": []
    }

@router.get("/activity-timeline")
async def get_activity_timeline(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get activity timeline for last N days"""
    # Simplified - return empty data for now
    return {
        "success": True,
        "days": days,
        "timeline": {}
    }
