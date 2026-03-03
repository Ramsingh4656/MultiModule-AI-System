"""
Lazy Loading Service for Serverless Optimization
Reduces cold start time by loading heavy dependencies only when needed
"""
from functools import lru_cache
from typing import Optional

class LazyLoader:
    """Singleton pattern for lazy loading heavy services"""
    
    _chatbot_service: Optional[object] = None
    _spam_service: Optional[object] = None
    _resume_service: Optional[object] = None
    _summary_service: Optional[object] = None
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_chatbot_service(cls):
        """Lazy load chatbot service"""
        if cls._chatbot_service is None:
            from services.chatbot_service import ChatbotService
            cls._chatbot_service = ChatbotService()
        return cls._chatbot_service
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_spam_service(cls):
        """Lazy load spam detection service"""
        if cls._spam_service is None:
            from services.spam_service import SpamDetectionService
            cls._spam_service = SpamDetectionService()
        return cls._spam_service
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_resume_service(cls):
        """Lazy load resume analysis service"""
        if cls._resume_service is None:
            from services.resume_service import ResumeAnalyzer
            cls._resume_service = ResumeAnalyzer()
        return cls._resume_service
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_summary_service(cls):
        """Lazy load text summarization service"""
        if cls._summary_service is None:
            from services.summary_service import TextSummarizer
            cls._summary_service = TextSummarizer()
        return cls._summary_service

# Export singleton instance
lazy_loader = LazyLoader()
