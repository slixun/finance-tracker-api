from decimal import Decimal
from app.enum import CurrencyEnum
from app.models import User, Wallet


def test_add_expense_success(db_session, client):
    # Arrange
    user = User(login="test")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=200, user_id=user.id, currency=CurrencyEnum.KZT
    )
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": 50.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {user.login}"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["type"] == "expense"
    assert response.json()["wallet_id"] == wallet.id
    assert Decimal(str(response.json()["amount"])) == Decimal(50)
    # assert Decimal(str(response.json()["new_balance"])) == Decimal(150)
    assert response.json()["category"] == "bubblegum"


def test_add_expense_negative_amount(db_session, client):
    # Arrange
    user = User(login="test")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="card", balance=200, user_id=user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": -50.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {user.login}"},
    )

    # Assert
    assert response.status_code == 422


def test_add_expense_name_is_empty(db_session, client):
    # Arrange
    user = User(login="test")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="card", balance=200, user_id=user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "  ", "amount": 50.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {user.login}"},
    )

    # Assert
    assert response.status_code == 422


def test_add_expense_wallet_not_existing(db_session, client):
    # Arrange
    user = User(login="test")
    db_session.add(user)
    db_session.commit()

    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": 50.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {user.login}"},
    )

    # Assert
    assert response.status_code == 404


def test_add_expense_unauthorized(db_session, client):
    # Arrange
    user = User(login="test")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="card", balance=200, user_id=user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": 50.0, "description": "bubblegum"},
        headers={"Authorization": "Bearer notexists"},
    )

    # Assert
    assert response.status_code == 401


def test_add_expense_insufficient_funds(db_session, client):
    # Arrange
    user = User(login="test")
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(name="card", balance=200, user_id=user.id)
    db_session.add(wallet)
    db_session.commit()
    db_session.refresh(wallet)
    # Act
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": 300.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {user.login}"},
    )

    # Assert
    assert response.status_code == 400
