import logging
from config import settings
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_activity(db, user_id: int, module: str, action: str, details: str = None):
    """Log user activity to database"""
    from models.models import ActivityLog
    try:
        log_entry = ActivityLog(
            user_id=user_id,
            module=module,
            action=action,
            details=details
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log activity: {str(e)}")
        db.rollback()
