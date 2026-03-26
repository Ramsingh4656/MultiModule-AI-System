import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Application
    APP_NAME = "AI Productivity Suite"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False") == "True"
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    
    # Database - Use /tmp for serverless environments
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_productivity.db")
    
    # File Upload - keep uploads inside the backend folder
    UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    # ResumeAnalyzer supports PDF/TXT only
    ALLOWED_EXTENSIONS = {".pdf", ".txt"}
    
    # CORS - Allow all origins for Vercel
    CORS_ORIGINS = ["*"]
    
    # AI Models - Optimized for serverless
    CHATBOT_MODEL = "distilgpt2"  # Lightweight GPT-2 model
    MAX_CONTEXT_LENGTH = 5  # Number of previous messages to remember
    MAX_RESPONSE_LENGTH = 150
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = str((Path(__file__).resolve().parent / "app.log"))

settings = Settings()

# Create necessary directories
try:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create upload directory: {e}")
