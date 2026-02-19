from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database.database import get_db
from models.models import Summary
from utils.logger import logger
from services.summary_service import SummarizerService

router = APIRouter(prefix="/summary", tags=["Summarizer"])

summary_service = SummarizerService()

class SummarizeRequest(BaseModel):
    text: str
    summary_ratio: Optional[float] = 0.3
    max_length: Optional[int] = None

@router.post("/create")
async def create_summary(
    request: SummarizeRequest,
    db: Session = Depends(get_db)
):
    """Generate summary from text"""
    try:
        # Validate input
        if len(request.text) < 100:
            raise HTTPException(
                status_code=400,
                detail="Text too short. Minimum 100 characters required."
            )
        
        # Generate summary
        if request.max_length:
            result = summary_service.summarize_with_length(request.text, request.max_length)
        else:
            result = summary_service.generate_summary(request.text, request.summary_ratio)
        
        # Save to database (using demo user ID = 1)
        summary = Summary(
            user_id=1,  # Demo user
            original_text=request.text[:2000],  # Store first 2000 chars
            summary_text=result['summary'],
            compression_ratio=result['compression_ratio']
        )
        
        db.add(summary)
        db.commit()
        db.refresh(summary)
        
        # Log activity
        logger.info(f"Created summary - Compression: {result['compression_ratio']}")
        
        logger.info(f"Summary created")
        
        return {
            "success": True,
            "summary_id": summary.id,
            "summary": result['summary'],
            "bullet_points": result['bullet_points'],
            "metrics": {
                "original_length": result['original_length'],
                "summary_length": result['summary_length'],
                "compression_ratio": result['compression_ratio'],
                "sentences_original": result['sentences_original'],
                "sentences_summary": result['sentences_summary']
            },
            "key_terms": result['key_terms']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_summary_history(db: Session = Depends(get_db)):
    """Get summary history"""
    summaries = db.query(Summary).filter(
        Summary.user_id == 1  # Demo user
    ).order_by(Summary.created_at.desc()).limit(10).all()
    
    return {
        "success": True,
        "count": len(summaries),
        "summaries": [
            {
                "id": s.id,
                "original_preview": s.original_text[:100] + "..." if len(s.original_text) > 100 else s.original_text,
                "summary_preview": s.summary_text[:100] + "..." if len(s.summary_text) > 100 else s.summary_text,
                "compression_ratio": s.compression_ratio,
                "created_at": s.created_at.isoformat()
            }
            for s in summaries
        ]
    }

@router.get("/detail/{summary_id}")
async def get_summary_detail(
    summary_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed summary"""
    summary = db.query(Summary).filter(
        Summary.id == summary_id,
        Summary.user_id == 1  # Demo user
    ).first()
    
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    return {
        "success": True,
        "summary": {
            "id": summary.id,
            "original_text": summary.original_text,
            "summary_text": summary.summary_text,
            "compression_ratio": summary.compression_ratio,
            "created_at": summary.created_at.isoformat()
        }
    }
