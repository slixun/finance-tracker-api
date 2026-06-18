from typing import Generator
from datetime import timedelta
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database import Base
from app.dependency import get_db
from app.enum import CurrencyEnum
from app.models import User, Wallet
from main import app
from fastapi.testclient import TestClient
from auth import create_access_token, hash_password
from config import settings

TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def get_test_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Whenever any route asks for get_db() dependency, gives them get_test_db() dependency instead.
app.dependency_overrides[get_db] = get_test_db


@pytest.fixture()
def client():
    yield TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    # recreate all the tables before the test
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def user_factory(db_session):
    def _create_user(login: str = "test", password: str = "password123") -> User:
        user = User(login=login, password_hash=hash_password(password))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture()
def auth_headers():
    def _auth_headers(user: User) -> dict[str, str]:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return {"Authorization": f"Bearer {access_token}"}

    return _auth_headers


@pytest.fixture()
def wallet_factory(db_session):
    def _create_wallet(
        user: User,
        name: str = "card",
        balance: Decimal = Decimal("200"),
        currency: CurrencyEnum = CurrencyEnum.KZT,
    ) -> Wallet:
        wallet = Wallet(
            name=name,
            balance=balance,
            user_id=user.id,
            currency=currency,
        )
        db_session.add(wallet)
        db_session.commit()
        db_session.refresh(wallet)
        return wallet

    return _create_wallet
