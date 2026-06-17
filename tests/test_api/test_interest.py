from datetime import timedelta
from decimal import Decimal
from app.enum import CurrencyEnum
from app.models import User, Wallet
from auth import create_access_token, hash_password
from config import settings


def test_calculate_interest_success(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=20000, user_id=user.id, currency=CurrencyEnum.KZT
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # Act
    response = client.post(
        "/api/v1/interest/1",
        json={"duration_in_months": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Assert
    assert response.status_code == 200
    assert Decimal(str(response.json()["interest"])) == Decimal(235.00)
    assert Decimal(str(response.json()["new_balance"])) == Decimal(20235.00)
    assert response.json()["currency"] == CurrencyEnum.KZT
    assert response.json()["wallet_id"] == 1


def test_calculate_interest_unathourized(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=20000, user_id=user.id, currency=CurrencyEnum.KZT
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # Act
    response = client.post(
        "/api/v1/interest/1",
        json={"duration_in_months": 1},
        headers={"Authorization": "Bearer notexists"},
    )
    # Assert
    assert response.status_code == 401


def test_calculate_interest_duration_below_one(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=20000, user_id=user.id, currency=CurrencyEnum.KZT
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # Act
    response = client.post(
        "/api/v1/interest/1",
        json={"duration_in_months": -1},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Assert
    assert response.status_code == 422


def test_calculate_interest_duration_not_integer(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=20000, user_id=user.id, currency=CurrencyEnum.KZT
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # Act
    response = client.post(
        "/api/v1/interest/1",
        json={"duration_in_months": 2.5},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Assert
    assert response.status_code == 422


def test_calculate_interest_wallet_not_found(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=20000, user_id=user.id, currency=CurrencyEnum.KZT
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # Act
    response = client.post(
        "/api/v1/interest/2",
        json={"duration_in_months": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Assert
    assert response.status_code == 404


def test_calculate_all_interest_success(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=20000, user_id=user.id, currency=CurrencyEnum.KZT
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    wallet = Wallet(
        name="dollar", balance=266, user_id=user.id, currency=CurrencyEnum.USD
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    wallet = Wallet(
        name="crypto", balance=0.001, user_id=user.id, currency=CurrencyEnum.BTC
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # Act
    response = client.post(
        "/api/v1/interest",
        json={"duration_in_months": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Assert
    assert response.status_code == 200
    assert Decimal(str(response.json()["total_interest"])) == Decimal("342.35")
    assert Decimal(
        str(response.json()["wallet_interest_list"][0]["interest"])
    ) == Decimal(235.00)
    assert Decimal(
        str(response.json()["wallet_interest_list"][0]["new_balance"])
    ) == Decimal(20235.00)
    assert response.json()["wallet_interest_list"][0]["currency"] == CurrencyEnum.KZT
    assert response.json()["wallet_interest_list"][0]["wallet_id"] == 1
    assert Decimal(
        str(response.json()["wallet_interest_list"][1]["interest"])
    ) == Decimal("0.22")
    assert Decimal(
        str(response.json()["wallet_interest_list"][1]["new_balance"])
    ) == Decimal("266.22")
    assert response.json()["wallet_interest_list"][1]["currency"] == CurrencyEnum.USD
    assert response.json()["wallet_interest_list"][1]["wallet_id"] == 2


def test_calculate_all_interest_unauthorized(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=20000, user_id=user.id, currency=CurrencyEnum.KZT
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    wallet = Wallet(
        name="dollar", balance=266, user_id=user.id, currency=CurrencyEnum.USD
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    wallet = Wallet(
        name="crypto", balance=0.1, user_id=user.id, currency=CurrencyEnum.BTC
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # Act
    response = client.post(
        "/api/v1/interest",
        json={"duration_in_months": 1},
        headers={"Authorization": "Bearer notexists"},
    )
    # Assert
    assert response.status_code == 401


def test_calculate_all_interest_no_wallets(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    db_session.commit()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    # Act
    response = client.post(
        "/api/v1/interest",
        json={"duration_in_months": 1},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Assert
    assert response.status_code == 200
    assert Decimal(str(response.json()["total_interest"])) == Decimal("0.00")
