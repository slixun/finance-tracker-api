from typing import Annotated, Generator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.repository import users as users_repository
from auth import oauth2_scheme, verify_access_token

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db),
# ) -> User:

#     login = credentials.credentials
#     user = users_repository.get_user(db, login)

#     if not user:
#         raise HTTPException(status_code=401, detail="Unauthorized")

#     return user


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
) -> User:
    """Get the currently authenticated user."""
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # validate user_id is a valid integer
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = db.execute(
        select(User).where(User.id == user_id_int),
    )

    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
