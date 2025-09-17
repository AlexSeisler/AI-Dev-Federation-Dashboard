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
    print("DEBUG: get_current_user called with token", token[:10], "...")
    payload = decode_access_token(token)
    print("DEBUG: payload from token =", payload)
    if payload is None:
        print("DEBUG: invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(models.User).filter(models.User.email == payload.get("sub")).first()
    print("DEBUG: user fetched in get_current_user =", user)
    if not user:
        print("DEBUG: no user found for sub", payload.get("sub"))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def require_admin(user: models.User = Depends(get_current_user)):
    print("DEBUG: require_admin called for", user.email)
    if user.role != "admin":
        print("DEBUG: access denied, not admin")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def log_action(db: Session, user_id: int, action: str):
    print(f"DEBUG: log_action called user_id={user_id}, action={action}")
    log = models.AuditLog(user_id=user_id, action=action, timestamp=datetime.utcnow())
    db.add(log)
    db.commit()
    print("DEBUG: log_action committed")


# -------- Endpoints --------
@router.post("/signup")
def signup(user: UserSignup, db: Session = Depends(database.get_db)):
    print("DEBUG: /auth/signup called with email=", user.email)
    try:
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        print("DEBUG: existing_user =", existing_user)
        if existing_user:
            print("DEBUG: user already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please log in."
            )

        hashed_pw = pwd_context.hash(user.password)
        print("DEBUG: password hashed")

        new_user = models.User(
            email=user.email,
            password_hash=hashed_pw,
            role="member",
            status="pending"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("DEBUG: new_user committed id=", new_user.id)

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
        print("ERROR during signup:", str(e))
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed due to server error. Please try again."
        )


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(database.get_db)):
    print("DEBUG: /auth/login called with email=", user.email)
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        print("DEBUG: db_user =", db_user)
        if not db_user:
            print("DEBUG: no user found for", user.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        print("DEBUG: verifying password for", db_user.email)
        try:
            valid = pwd_context.verify(user.password, db_user.password_hash)
            print("DEBUG: password verification result =", valid)
        except Exception as ve:
            print("ERROR during bcrypt verify:", str(ve))
            raise HTTPException(status_code=500, detail="Password verification error")

        if not valid:
            print("DEBUG: invalid password")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token_data = {
            "sub": db_user.email,
            "role": db_user.role,
            "status": db_user.status
        }
        print("DEBUG: token_data =", token_data)

        access_token = create_access_token(token_data)
        print("DEBUG: JWT token created")

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
        print("ERROR during login:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error. Please try again."
        )


@router.get("/me")
def me(current_user: models.User = Depends(get_current_user)):
    print("DEBUG: /auth/me called for", current_user.email)
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
    print(f"DEBUG: /auth/approve called for user_id={user_id} by admin={admin_user.email}")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    print("DEBUG: user to approve =", user)
    if not user:
        print("DEBUG: user not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.status = "approved"
    db.commit()
    db.refresh(user)
    print("DEBUG: user approved:", user.email)

    log_action(db, admin_user.id, f"approved user {user.email}")

    return {"message": f"User {user.email} approved", "id": user.id}


@router.post("/refresh")
def refresh_token(body: TokenRequest):
    print("DEBUG: /auth/refresh called with token prefix", body.token[:10], "...")
    try:
        new_token = refresh_access_token(body.token)
        print("DEBUG: refresh_access_token succeeded")
        return {"access_token": new_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        print("ERROR during token refresh:", str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
