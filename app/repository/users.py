from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User
from auth import hash_password


def get_user(db: Session, login: str) -> User | None:
    return db.query(User).filter(func.lower(User.login) == login.lower()).scalar()


def create_user(db: Session, login: str, password: str) -> User:
    user = User(login=login, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    return user
