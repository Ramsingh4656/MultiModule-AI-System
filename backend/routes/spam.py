from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from database.database import get_db
from models.models import SpamCheck
from utils.logger import logger
from services.spam_service import SpamDetectorService

router = APIRouter(prefix="/spam", tags=["Spam Detector"])

spam_service = SpamDetectorService()

class EmailCheck(BaseModel):
    email_text: str

@router.post("/check")
async def check_spam(
    email_data: EmailCheck,
    db: Session = Depends(get_db)
):
    """Check if email is spam or phishing"""
    try:
        # Detect spam
        result = spam_service.detect_spam(email_data.email_text)
        
        # Save to database (using demo user ID = 1)
        spam_check = SpamCheck(
            user_id=1,  # Demo user
            email_text=email_data.email_text[:1000],  # Store first 1000 chars
            is_spam=result['is_spam'],
            confidence=result['confidence'],
            features=json.dumps(result['features'])
        )
        
        db.add(spam_check)
        db.commit()
        db.refresh(spam_check)
        
        # Log activity
        logger.info(f"Spam check - Result: {result['classification']}")
        
        logger.info(f"Spam check: {result['classification']}")
        
        return {
            "success": True,
            "check_id": spam_check.id,
            "is_spam": result['is_spam'],
            "classification": result['classification'],
            "confidence": result['confidence'],
            "risk_level": result['risk_level'],
            "reasons": result['reasons'],
            "features": {
                "spam_keywords": result['features']['spam_keyword_count'],
                "phishing_patterns": result['features']['phishing_pattern_count'],
                "suspicious_patterns": result['features']['suspicious_patterns'][:3]  # Top 3
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking spam: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_spam_history(db: Session = Depends(get_db)):
    """Get spam check history"""
    checks = db.query(SpamCheck).filter(
        SpamCheck.user_id == 1  # Demo user
    ).order_by(SpamCheck.created_at.desc()).limit(20).all()
    
    return {
        "success": True,
        "count": len(checks),
        "checks": [
            {
                "id": c.id,
                "email_preview": c.email_text[:100] + "..." if len(c.email_text) > 100 else c.email_text,
                "is_spam": c.is_spam,
                "confidence": c.confidence,
                "created_at": c.created_at.isoformat()
            }
            for c in checks
        ]
    }

@router.get("/stats")
async def get_spam_stats(db: Session = Depends(get_db)):
    """Get spam detection statistics"""
    total_checks = db.query(SpamCheck).filter(
        SpamCheck.user_id == 1  # Demo user
    ).count()
    
    spam_count = db.query(SpamCheck).filter(
        SpamCheck.user_id == 1,  # Demo user
        SpamCheck.is_spam == True
    ).count()
    
    legitimate_count = total_checks - spam_count
    
    return {
        "success": True,
        "stats": {
            "total_checks": total_checks,
            "spam_detected": spam_count,
            "legitimate": legitimate_count,
            "spam_percentage": round((spam_count / total_checks * 100), 2) if total_checks > 0 else 0
        }
    }
