from datetime import datetime, timedelta
from decimal import Decimal
from app.enum import CurrencyEnum, OperationType
from app.models import Operation, User, Wallet
from auth import create_access_token, hash_password
from config import settings


def test_add_expense_success(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=200, user_id=user.id, currency=CurrencyEnum.KZT
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
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": 50.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["type"] == "expense"
    assert response.json()["wallet_id"] == wallet.id
    assert Decimal(str(response.json()["amount"])) == Decimal(50)
    assert Decimal(str(response.json()["new_balance"])) == Decimal(150)
    assert response.json()["category"] == "bubblegum"
    assert response.json()["currency"] == CurrencyEnum.KZT


def test_add_expense_negative_amount(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=200, user_id=user.id, currency=CurrencyEnum.KZT
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
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": -50.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Assert
    assert response.status_code == 422


def test_add_expense_name_is_empty(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=200, user_id=user.id, currency=CurrencyEnum.KZT
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
        "/api/v1/operations/expense",
        json={"wallet_name": "  ", "amount": 50.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Assert
    assert response.status_code == 422


def test_add_expense_wallet_not_existing(db_session, client):
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
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": 50.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Assert
    assert response.status_code == 404


def test_add_expense_unauthorized(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=200, user_id=user.id, currency=CurrencyEnum.KZT
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
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": 50.0, "description": "bubblegum"},
        headers={"Authorization": "Bearer notexists"},
    )

    # Assert
    assert response.status_code == 401


def test_add_expense_insufficient_funds(db_session, client):
    # Arrange
    user = User(login="test", password_hash=hash_password("123"))
    db_session.add(user)
    db_session.flush()
    wallet = Wallet(
        name="card", balance=200, user_id=user.id, currency=CurrencyEnum.KZT
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
        "/api/v1/operations/expense",
        json={"wallet_name": "card", "amount": 300.0, "description": "bubblegum"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Assert
    assert response.status_code == 400


def test_add_income_success(
    db_session, client, user_factory, wallet_factory, auth_headers
):
    # Arrange
    user = user_factory()
    wallet = wallet_factory(user, name="card", balance=Decimal("200"))

    # Act
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": "card", "amount": "50", "description": "salary"},
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["type"] == OperationType.INCOME
    assert response.json()["wallet_id"] == wallet.id
    assert Decimal(str(response.json()["amount"])) == Decimal("50")
    assert Decimal(str(response.json()["new_balance"])) == Decimal("250")
    assert response.json()["category"] == "salary"

    db_session.refresh(wallet)
    assert wallet.balance == Decimal("250")


def test_add_income_wallet_not_existing(client, user_factory, auth_headers):
    # Arrange
    user = user_factory()

    # Act
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": "card", "amount": "50", "description": "salary"},
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 400


def test_list_operations_success(
    db_session, client, user_factory, wallet_factory, auth_headers
):
    # Arrange
    user = user_factory(login="alice")
    other_user = user_factory(login="bob")
    wallet = wallet_factory(user, name="card")
    other_wallet = wallet_factory(other_user, name="hidden")
    operation = Operation(
        wallet_id=wallet.id,
        type=OperationType.INCOME,
        amount=Decimal("100"),
        currency=CurrencyEnum.KZT,
        new_balance=Decimal("300"),
        category="salary",
        created_at=datetime(2026, 1, 15, 12, 0, 0),
    )
    other_operation = Operation(
        wallet_id=other_wallet.id,
        type=OperationType.INCOME,
        amount=Decimal("999"),
        currency=CurrencyEnum.KZT,
        new_balance=Decimal("999"),
        category="hidden",
    )
    db_session.add(operation)
    db_session.add(other_operation)
    db_session.commit()

    # Act
    response = client.get("/api/v1/operations", headers=auth_headers(user))

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["wallet_id"] == wallet.id
    assert response.json()[0]["category"] == "salary"


def test_list_operations_filters_by_wallet_and_date(
    db_session, client, user_factory, wallet_factory, auth_headers
):
    # Arrange
    user = user_factory()
    card = wallet_factory(user, name="card")
    cash = wallet_factory(user, name="cash")
    included = Operation(
        wallet_id=card.id,
        type=OperationType.INCOME,
        amount=Decimal("100"),
        currency=CurrencyEnum.KZT,
        new_balance=Decimal("300"),
        category="included",
        created_at=datetime(2026, 1, 15, 12, 0, 0),
    )
    old_operation = Operation(
        wallet_id=card.id,
        type=OperationType.INCOME,
        amount=Decimal("50"),
        currency=CurrencyEnum.KZT,
        new_balance=Decimal("250"),
        category="old",
        created_at=datetime(2025, 1, 15, 12, 0, 0),
    )
    other_wallet_operation = Operation(
        wallet_id=cash.id,
        type=OperationType.INCOME,
        amount=Decimal("75"),
        currency=CurrencyEnum.KZT,
        new_balance=Decimal("275"),
        category="cash",
        created_at=datetime(2026, 1, 15, 12, 0, 0),
    )
    db_session.add_all([included, old_operation, other_wallet_operation])
    db_session.commit()

    # Act
    response = client.get(
        f"/api/v1/operations?wallet_id={card.id}"
        "&date_from=2026-01-01T00:00:00"
        "&date_to=2026-12-31T23:59:59",
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "included"


def test_list_operations_wallet_not_found(client, user_factory, auth_headers):
    # Arrange
    user = user_factory()

    # Act
    response = client.get(
        "/api/v1/operations?wallet_id=999",
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 404


def test_create_transfer_success_same_currency(
    db_session, client, user_factory, wallet_factory, auth_headers
):
    # Arrange
    user = user_factory()
    from_wallet = wallet_factory(user, name="from", balance=Decimal("200"))
    to_wallet = wallet_factory(user, name="to", balance=Decimal("50"))

    # Act
    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": "75",
        },
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["type"] == OperationType.TRANSFER
    assert response.json()["wallet_id"] == to_wallet.id
    assert Decimal(str(response.json()["amount"])) == Decimal("75")
    assert Decimal(str(response.json()["new_balance"])) == Decimal("125")

    db_session.refresh(from_wallet)
    db_session.refresh(to_wallet)
    assert from_wallet.balance == Decimal("125")
    assert to_wallet.balance == Decimal("125")


def test_create_transfer_converts_currency(
    monkeypatch, db_session, client, user_factory, wallet_factory, auth_headers
):
    # Arrange
    async def fake_get_exchange_rate(base, target):
        assert base == CurrencyEnum.USD
        assert target == CurrencyEnum.KZT
        return Decimal("500")

    monkeypatch.setattr(
        "app.service.operations.get_exchange_rate", fake_get_exchange_rate
    )
    user = user_factory()
    from_wallet = wallet_factory(
        user, name="from", balance=Decimal("10"), currency=CurrencyEnum.USD
    )
    to_wallet = wallet_factory(
        user, name="to", balance=Decimal("100"), currency=CurrencyEnum.KZT
    )

    # Act
    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": "2",
        },
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 200
    assert Decimal(str(response.json()["amount"])) == Decimal("1000")
    assert Decimal(str(response.json()["new_balance"])) == Decimal("1100")

    db_session.refresh(from_wallet)
    db_session.refresh(to_wallet)
    assert from_wallet.balance == Decimal("8")
    assert to_wallet.balance == Decimal("1100")


def test_create_transfer_insufficient_funds(
    client, user_factory, wallet_factory, auth_headers
):
    # Arrange
    user = user_factory()
    from_wallet = wallet_factory(user, name="from", balance=Decimal("50"))
    to_wallet = wallet_factory(user, name="to", balance=Decimal("100"))

    # Act
    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "amount": "75",
        },
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 400


def test_create_transfer_missing_wallet(
    client, user_factory, wallet_factory, auth_headers
):
    # Arrange
    user = user_factory()
    from_wallet = wallet_factory(user, name="from", balance=Decimal("50"))

    # Act
    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": 999,
            "amount": "10",
        },
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 404


def test_create_transfer_same_wallet_validation(
    client, user_factory, wallet_factory, auth_headers
):
    # Arrange
    user = user_factory()
    wallet = wallet_factory(user, name="card", balance=Decimal("50"))

    # Act
    response = client.post(
        "/api/v1/operations/transfer",
        json={
            "from_wallet_id": wallet.id,
            "to_wallet_id": wallet.id,
            "amount": "10",
        },
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 422
