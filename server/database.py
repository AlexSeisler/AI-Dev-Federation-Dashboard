from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.config import settings

# SQLAlchemy engine
engine = create_engine(settings.DB_URL, future=True, echo=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()