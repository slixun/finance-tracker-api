from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from app.dependency import get_db, get_current_user
from app.models import User
from app.repository.users import get_user
from app.schemas import UserRequest, UserResponse, Token
from app.service import users as users_service
from sqlalchemy.orm import Session
from datetime import timedelta
from auth import (
    create_access_token,
    hash_password,
    verify_password,
    oauth2_scheme,
    verify_access_token,
)
from config import settings

router = APIRouter()


@router.post("/users", response_model=UserResponse)
def create_user(payload: UserRequest, db: Session = Depends(get_db)):
    return users_service.create_user(db, payload.login, payload.password)


@router.get("/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/users/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = get_user(db=db, login=form_data.username)

    # Verify user exists and password is correct
    # Don't reveal which one failed
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
