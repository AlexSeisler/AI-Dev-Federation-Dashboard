from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.config import settings

# Mask DB URL password for safety in logs
db_url_safe = settings.database_url
try:
    # hide password but keep host/db visible
    if "@" in db_url_safe:
        prefix, suffix = db_url_safe.split("@", 1)
        db_url_safe = "*****@" + suffix
except Exception:
    db_url_safe = settings.database_url  # fallback

print("DEBUG: Initializing database with URL =", db_url_safe)

# SQLAlchemy engine
engine = create_engine(settings.database_url, future=True, echo=True)
print("DEBUG: SQLAlchemy engine created")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("DEBUG: SessionLocal factory created")

# Dependency for FastAPI routes
def get_db():
    print("DEBUG: get_db called - opening new session")
    db = SessionLocal()
    try:
        yield db
        print("DEBUG: get_db yielded successfully")
    except Exception as e:
        print("ERROR in get_db:", str(e))
        raise
    finally:
        db.close()
        print("DEBUG: get_db closed")
