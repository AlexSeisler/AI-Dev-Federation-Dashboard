from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from server.config import settings
from server.database import get_db
from server.models import User
import logging

# Setup local logger for jwt_utils
logger = logging.getLogger("jwt_utils")

# JWT settings
SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2 scheme (optional so query params can work too)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token with optional custom expiration."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {**data, "exp": expire}

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("JWT created", extra={"data": data, "exp": expire.isoformat()})
        return encoded_jwt
    except Exception as e:
        logger.error("JWT creation failed", exc_info=e, extra={"data": data})
        raise


def decode_access_token(token: str):
    """Decode a JWT token, return payload or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("JWT decoded", extra={"payload": payload})
        return payload
    except JWTError as e:
        logger.warning("JWT decode failed", exc_info=e, extra={"token": token[:12] + '...'})
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """FastAPI dependency that validates the JWT and returns the DB user."""
    if not token:
        logger.warning("Missing JWT in request")
        raise HTTPException(status_code=401, detail="Missing token")

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    email = payload.get("sub")
    if not email:
        logger.warning("JWT missing subject", extra={"payload": payload})
        raise HTTPException(status_code=401, detail="Invalid token: missing subject")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning("JWT user not found in DB", extra={"email": email})
        raise HTTPException(status_code=401, detail="User not found")

    logger.info("JWT validated + user loaded", extra={"user_id": user.id, "email": email})
    return {"id": user.id, "email": user.email, "role": user.role}


def decode_token(token: str) -> dict:
    """Manually decode a JWT token (used for query param auth in SSE)."""
    logger.debug("Manual JWT decode requested", extra={"token": token[:12] + '...'})
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Manual decode failed", extra={"token": token[:12] + '...'})
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload
