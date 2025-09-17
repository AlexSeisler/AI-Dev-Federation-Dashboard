from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime
import logging

from server import database, models
from server.jwt_utils import create_access_token, decode_access_token, refresh_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Setup logger
logger = logging.getLogger(__name__)


# -------- Schemas --------
class UserSignup(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRequest(BaseModel):
    token: str


# -------- Helpers --------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(models.User).filter(models.User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def require_admin(user: models.User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def log_action(db: Session, user_id: int, action: str):
    log = models.AuditLog(user_id=user_id, action=action, timestamp=datetime.utcnow())
    db.add(log)
    db.commit()


# -------- Endpoints --------
@router.post("/signup")
def signup(user: UserSignup, db: Session = Depends(database.get_db)):
    try:
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please log in."
            )

        hashed_pw = pwd_context.hash(user.password)

        new_user = models.User(
            email=user.email,
            password_hash=hashed_pw,
            role="member",
            status="pending"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role,
            "status": new_user.status,
            "created_at": new_user.created_at,
            "message": "Account created! Awaiting admin approval."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup failed for {user.email}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed due to server error. Please try again."
        )


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(database.get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        try:
            valid = pwd_context.verify(user.password, db_user.password_hash)
        except Exception:
            raise HTTPException(status_code=500, detail="Password verification error")

        if not valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token_data = {
            "sub": db_user.email,
            "role": db_user.role,
            "status": db_user.status
        }

        access_token = create_access_token(token_data)

        log_action(db, db_user.id, "login")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": db_user.role,
            "status": db_user.status,
            "message": "Logged in with demo access — awaiting admin approval."
                      if db_user.status == "pending"
                      else "Login successful."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error. Please try again."
        )


@router.get("/me")
def me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "status": current_user.status,
        "created_at": current_user.created_at,
    }


@router.post("/approve/{user_id}")
def approve_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    admin_user: models.User = Depends(require_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.status = "approved"
    db.commit()
    db.refresh(user)

    log_action(db, admin_user.id, f"approved user {user.email}")

    return {"message": f"User {user.email} approved", "id": user.id}


@router.post("/refresh")
def refresh_token(body: TokenRequest):
    try:
        new_token = refresh_access_token(body.token)
        return {"access_token": new_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
@router.post("/check-email")
def check_email(email: EmailStr = Depends(), db: Session = Depends(database.get_db)):
    """
    Check if the email exists in the database, allowing pending users to access the DevBot demo.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if user:
        return {"exists": True}  # Email exists
    else:
        return {"exists": False}  # Email does not exist

