from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid

from database.database import get_db
from models.models import ChatSession, ChatMessage
from utils.logger import logger
from services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

# Initialize chatbot service (singleton)
chatbot_service = ChatbotService()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    confidence: float
    metadata: dict

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send message to AI chatbot and get response"""
    try:
        # Get or create session
        if request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.session_id == request.session_id,
                ChatSession.user_id == 1  # Demo user
            ).first()
            
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            # Create new session
            session = ChatSession(
                user_id=1,  # Demo user
                session_id=str(uuid.uuid4())
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Get conversation history
        history_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        # Build conversation history for context
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in history_messages
        ]
        
        # Generate AI response
        ai_response = chatbot_service.chat(request.message, conversation_history)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        
        # Save assistant response
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_response['response'],
            confidence=ai_response['confidence'],
            intent=ai_response['intent']
        )
        db.add(assistant_message)
        
        db.commit()
        
        # Log activity
        logger.info(f"Chat message processed, session {session.session_id}")
        
        logger.info(f"Chat message processed, session {session.session_id}")
        
        return ChatResponse(
            response=ai_response['response'],
            session_id=session.session_id,
            intent=ai_response['intent'],
            confidence=ai_response['confidence'],
            metadata={
                "has_context": ai_response['has_context'],
                "model_used": ai_response['model_used'],
                "context_length": ai_response['context_length'],
                "message_count": len(conversation_history) + 1
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_chat_sessions(db: Session = Depends(get_db)):
    """Get chat sessions"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == 1  # Demo user
    ).order_by(ChatSession.updated_at.desc()).limit(10).all()
    
    return {
        "success": True,
        "count": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "message_count": len(s.messages),
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
                "last_message": s.messages[-1].content[:50] + "..." if s.messages else None
            }
            for s in sessions
        ]
    }

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == 1  # Demo user
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return {
        "success": True,
        "session_id": session_id,
        "message_count": len(messages),
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "confidence": m.confidence,
                "intent": m.intent,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    }

@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == 1  # Demo user
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"success": True, "message": "Session deleted"}

@router.get("/model-info")
async def get_model_info():
    """Get information about the AI model"""
    info = chatbot_service.get_model_info()
    return {
        "success": True,
        "model_info": info
    }
