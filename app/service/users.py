from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repository import users as users_repository
from app.schemas import UserResponse


def create_user(db: Session, login: str, password: str) -> UserResponse:
    if users_repository.get_user(db, login):
        raise HTTPException(status_code=400, detail="User already exists")

    user = users_repository.create_user(db, login, password)

    db.commit()

    return UserResponse.model_validate(user)
    # model_validate converts sqlalchemy User model into a pydantic UserResponse model
