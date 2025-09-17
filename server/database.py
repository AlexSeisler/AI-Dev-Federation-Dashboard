from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.config import settings
import logging

# Setup logger
logger = logging.getLogger(__name__)

# SQLAlchemy engine
engine = create_engine(settings.database_url, future=True, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", exc_info=e)
        raise
    finally:
        db.close()
