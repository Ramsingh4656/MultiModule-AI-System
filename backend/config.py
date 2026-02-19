import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Application
    APP_NAME = "AI Productivity Suite"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_productivity.db")
    
    # File Upload
    UPLOAD_DIR = Path("uploads")
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # AI Models
    CHATBOT_MODEL = "distilgpt2"  # Lightweight GPT-2 model
    MAX_CONTEXT_LENGTH = 5  # Number of previous messages to remember
    MAX_RESPONSE_LENGTH = 150
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "app.log"

settings = Settings()

# Create necessary directories
settings.UPLOAD_DIR.mkdir(exist_ok=True)
