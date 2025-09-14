from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from server import database, models

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------- Schemas --------
class UserSignup(BaseModel):
    email: EmailStr
    password: str


# -------- Endpoints --------
@router.post("/signup")
def signup(user: UserSignup, db: Session = Depends(database.get_db)):
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_pw = pwd_context.hash(user.password)

    # Create user (pending approval)
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
