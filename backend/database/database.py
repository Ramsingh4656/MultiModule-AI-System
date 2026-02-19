from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from models import models  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)
    
    # Create demo user if not exists
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        demo_user = db.query(models.User).filter(models.User.id == 1).first()
        if not demo_user:
            from utils.security import get_password_hash
            demo_user = models.User(
                id=1,
                email="demo@example.com",
                username="Demo User",
                hashed_password=get_password_hash("demo123")
            )
            db.add(demo_user)
            db.commit()
    except Exception as e:
        print(f"Error creating demo user: {e}")
    finally:
        db.close()
