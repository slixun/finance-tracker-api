from decimal import Decimal

from app.enum import CurrencyEnum
from app.models import Wallet


def test_create_wallet_success(user_factory, auth_headers, client):
    # Arrange
    user = user_factory()

    # Act
    response = client.post(
        "/api/v1/wallets",
        json={"name": "cash", "initial_balance": "100.50", "currency": "usd"},
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "cash"
    assert Decimal(str(response.json()["balance"])) == Decimal("100.50")
    assert response.json()["currency"] == CurrencyEnum.USD


def test_create_wallet_duplicate_name(user_factory, wallet_factory, auth_headers, client):
    # Arrange
    user = user_factory()
    wallet_factory(user, name="cash")

    # Act
    response = client.post(
        "/api/v1/wallets",
        json={"name": "cash", "initial_balance": "100.50", "currency": "usd"},
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 400


def test_create_wallet_negative_initial_balance(user_factory, auth_headers, client):
    # Arrange
    user = user_factory()

    # Act
    response = client.post(
        "/api/v1/wallets",
        json={"name": "cash", "initial_balance": "-1", "currency": "kzt"},
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 422


def test_create_wallet_unauthorized(client):
    # Act
    response = client.post(
        "/api/v1/wallets",
        json={"name": "cash", "initial_balance": "100.50", "currency": "usd"},
    )

    # Assert
    assert response.status_code == 401


def test_list_wallets_only_current_user(
    user_factory, wallet_factory, auth_headers, client
):
    # Arrange
    user = user_factory(login="alice")
    other_user = user_factory(login="bob")
    wallet_factory(user, name="cash", balance=Decimal("100"))
    wallet_factory(user, name="card", balance=Decimal("200"))
    wallet_factory(other_user, name="hidden", balance=Decimal("999"))

    # Act
    response = client.get("/api/v1/wallets", headers=auth_headers(user))

    # Assert
    assert response.status_code == 200
    assert [wallet["name"] for wallet in response.json()] == ["cash", "card"]


def test_update_wallet_success(
    db_session, user_factory, wallet_factory, auth_headers, client
):
    # Arrange
    user = user_factory()
    wallet = wallet_factory(user, name="cash", balance=Decimal("100"))

    # Act
    response = client.put(
        f"/api/v1/wallets/{wallet.id}",
        json={"name": "card", "balance": "250.75"},
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "card"
    assert Decimal(str(response.json()["balance"])) == Decimal("250.75")

    db_session.refresh(wallet)
    assert wallet.name == "card"
    assert wallet.balance == Decimal("250.75")


def test_update_wallet_not_found(user_factory, auth_headers, client):
    # Arrange
    user = user_factory()

    # Act
    response = client.put(
        "/api/v1/wallets/999",
        json={"name": "card", "balance": "250.75"},
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 404


def test_delete_wallet_success(
    db_session, user_factory, wallet_factory, auth_headers, client
):
    # Arrange
    user = user_factory()
    wallet = wallet_factory(user, name="cash", balance=Decimal("100"))

    # Act
    response = client.delete(
        f"/api/v1/wallets/{wallet.id}",
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == wallet.id
    assert db_session.query(Wallet).filter(Wallet.id == wallet.id).first() is None


def test_delete_wallet_not_found(user_factory, auth_headers, client):
    # Arrange
    user = user_factory()

    # Act
    response = client.delete(
        "/api/v1/wallets/999",
        headers=auth_headers(user),
    )

    # Assert
    assert response.status_code == 404


def test_get_total_balance_converts_to_kzt(
    monkeypatch, user_factory, wallet_factory, auth_headers, client
):
    # Arrange
    async def fake_get_exchange_rate(base, target):
        assert base == CurrencyEnum.USD
        assert target == CurrencyEnum.KZT
        return Decimal("500")

    monkeypatch.setattr(
        "app.service.exchange_service.get_exchange_rate", fake_get_exchange_rate
    )
    user = user_factory()
    wallet_factory(user, name="cash", balance=Decimal("100"), currency=CurrencyEnum.KZT)
    wallet_factory(user, name="dollar", balance=Decimal("2"), currency=CurrencyEnum.USD)

    # Act
    response = client.get("/api/v1/balance", headers=auth_headers(user))

    # Assert
    assert response.status_code == 200
    assert Decimal(str(response.json()["total_balance"])) == Decimal("1100")
