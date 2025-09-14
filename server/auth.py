from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from server import database, models
from server.jwt_utils import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------- Schemas --------
class UserSignup(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------- Endpoints --------
@router.post("/signup")
def signup(user: UserSignup, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
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
    }


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(database.get_db)):
    # Look up user
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Verify password
    if not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Ensure user is approved
    if db_user.status != "approved":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not approved")

    # Generate JWT
    token_data = {"sub": db_user.email, "role": db_user.role}
    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.role,
    }
