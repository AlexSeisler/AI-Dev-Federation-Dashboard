from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server import database, models

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup():
    return {"message": "Signup endpoint placeholder"}


@router.post("/login")
def login():
    return {"message": "Login endpoint placeholder"}


@router.get("/me")
def me():
    return {"message": "Me endpoint placeholder"}


@router.post("/approve/{user_id}")
def approve_user(user_id: int):
    return {"message": f"Approve user {user_id} placeholder"}