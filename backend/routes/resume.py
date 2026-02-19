from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from pathlib import Path
import shutil

from database.database import get_db
from models.models import ResumeAnalysis
from utils.logger import logger
from services.resume_service import ResumeAnalyzerService
from config import settings

router = APIRouter(prefix="/resume", tags=["Resume Analyzer"])

resume_service = ResumeAnalyzerService()

@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    required_skills: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Analyze uploaded resume"""
    try:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Save uploaded file
        file_path = settings.UPLOAD_DIR / f"demo_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse required skills
        skills_list = []
        if required_skills:
            skills_list = [s.strip() for s in required_skills.split(',') if s.strip()]
        
        # Analyze resume
        analysis_result = resume_service.analyze_resume(file_path, skills_list)
        
        # Save to database (using demo user ID = 1)
        resume_analysis = ResumeAnalysis(
            user_id=1,  # Demo user
            filename=file.filename,
            extracted_text=analysis_result['extracted_text'],
            skills_found=json.dumps(analysis_result['skills_found']),
            match_score=analysis_result['match_score'],
            missing_skills=json.dumps(analysis_result['missing_skills'])
        )
        
        db.add(resume_analysis)
        db.commit()
        db.refresh(resume_analysis)
        
        # Log activity
        logger.info(f"Resume analyzed: {file.filename}")
        
        # Clean up file
        file_path.unlink()
        
        logger.info(f"Resume analyzed: {file.filename}")
        
        return {
            "success": True,
            "analysis_id": resume_analysis.id,
            "filename": file.filename,
            "skills_found": analysis_result['skills_found'],
            "total_skills_found": analysis_result['total_skills_found'],
            "match_score": analysis_result['match_score'],
            "missing_skills": analysis_result['missing_skills'],
            "contact_info": analysis_result['contact_info']
        }
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_resume_history(db: Session = Depends(get_db)):
    """Get resume analysis history"""
    analyses = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == 1  # Demo user
    ).order_by(ResumeAnalysis.created_at.desc()).limit(10).all()
    
    return {
        "success": True,
        "count": len(analyses),
        "analyses": [
            {
                "id": a.id,
                "filename": a.filename,
                "match_score": a.match_score,
                "skills_found": json.loads(a.skills_found) if a.skills_found else {},
                "created_at": a.created_at.isoformat()
            }
            for a in analyses
        ]
    }

@router.get("/analysis/{analysis_id}")
async def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed analysis result"""
    analysis = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.id == analysis_id,
        ResumeAnalysis.user_id == 1  # Demo user
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "success": True,
        "analysis": {
            "id": analysis.id,
            "filename": analysis.filename,
            "extracted_text": analysis.extracted_text,
            "skills_found": json.loads(analysis.skills_found) if analysis.skills_found else {},
            "match_score": analysis.match_score,
            "missing_skills": json.loads(analysis.missing_skills) if analysis.missing_skills else [],
            "created_at": analysis.created_at.isoformat()
        }
    }
