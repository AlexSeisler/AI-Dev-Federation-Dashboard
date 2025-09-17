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

print("DEBUG: jwt_utils initialized with SECRET_KEY prefix =", SECRET_KEY[:5] + "...")

# OAuth2 scheme (optional so query params can work too)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token with optional custom expiration."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {**data, "exp": expire}

    print("DEBUG: create_access_token called with data =", data, "exp =", expire.isoformat())

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("JWT created", extra={"data": data, "exp": expire.isoformat()})
        print("DEBUG: JWT successfully created, prefix =", encoded_jwt[:10])
        return encoded_jwt
    except Exception as e:
        logger.error("JWT creation failed", exc_info=e, extra={"data": data})
        print("ERROR in create_access_token:", str(e))
        raise


def decode_access_token(token: str):
    """Decode a JWT token, return payload or None if invalid."""
    print("DEBUG: decode_access_token called, token prefix =", token[:10], "...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("JWT decoded", extra={"payload": payload})
        print("DEBUG: JWT successfully decoded, payload =", payload)
        return payload
    except JWTError as e:
        logger.warning("JWT decode failed", exc_info=e, extra={"token": token[:12] + '...'})
        print("ERROR in decode_access_token:", str(e))
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """FastAPI dependency that validates the JWT and returns the DB user."""
    print("DEBUG: get_current_user called with token prefix", token[:10] if token else None)

    if not token:
        logger.warning("Missing JWT in request")
        print("DEBUG: Missing JWT in request")
        raise HTTPException(status_code=401, detail="Missing token")

    payload = decode_access_token(token)
    print("DEBUG: payload decoded in get_current_user =", payload)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    email = payload.get("sub")
    print("DEBUG: email extracted from JWT =", email)
    if not email:
        logger.warning("JWT missing subject", extra={"payload": payload})
        print("DEBUG: JWT missing subject")
        raise HTTPException(status_code=401, detail="Invalid token: missing subject")

    user = db.query(User).filter(User.email == email).first()
    print("DEBUG: user fetched from DB in get_current_user =", user)
    if not user:
        logger.warning("JWT user not found in DB", extra={"email": email})
        print("DEBUG: No user found for email =", email)
        raise HTTPException(status_code=401, detail="User not found")

    logger.info("JWT validated + user loaded", extra={"user_id": user.id, "email": email})
    print("DEBUG: get_current_user returning user =", user.email)
    return {"id": user.id, "email": user.email, "role": user.role}


def decode_token(token: str) -> dict:
    """Manually decode a JWT token (used for query param auth in SSE)."""
    print("DEBUG: decode_token called, token prefix =", token[:10], "...")
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Manual decode failed", extra={"token": token[:12] + '...'})
        print("DEBUG: Manual decode failed")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    print("DEBUG: decode_token success, payload =", payload)
    return payload


# --- 🔄 Refresh Token Support --- #
def refresh_access_token(token: str):
    """
    Refresh an expired JWT by re-issuing it with a new expiry.
    Does not validate exp claim (so it works with expired tokens).
    """
    print("DEBUG: refresh_access_token called, token prefix =", token[:10], "...")
    try:
        # Decode without verifying exp
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        logger.debug("Refresh decode success", extra={"payload": payload})
        print("DEBUG: Refresh decode success, payload =", payload)

        # Strip old expiry
        payload.pop("exp", None)

        # Issue new token
        new_token = create_access_token(payload)
        logger.info("JWT refreshed", extra={"sub": payload.get("sub")})
        print("DEBUG: JWT refreshed for sub =", payload.get("sub"))
        return new_token

    except JWTError as e:
        logger.warning("JWT refresh failed", exc_info=e, extra={"token": token[:12] + '...'})
        print("ERROR in refresh_access_token:", str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
