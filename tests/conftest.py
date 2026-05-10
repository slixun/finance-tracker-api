from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database import Base
from app.dependency import get_db
from main import app
from fastapi.testclient import TestClient

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
