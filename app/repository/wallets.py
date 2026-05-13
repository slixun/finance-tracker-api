from decimal import Decimal
from app.enum import CurrencyEnum
from app.models import Wallet
from sqlalchemy.orm import Session


def is_wallet_existing(db: Session, user_id: int, wallet_name: str) -> bool:
    return (
        db.query(Wallet)
        .filter(Wallet.name == wallet_name, Wallet.user_id == user_id)
        .first()
        is not None
    )


def add_income(db: Session, user_id: int, wallet_name: str, amount: Decimal) -> Wallet:
    wallet = (
        db.query(Wallet)
        .filter(Wallet.name == wallet_name, Wallet.user_id == user_id)
        .first()
    )
    wallet.balance += amount  # type: ignore
    return wallet


def add_expense(db: Session, user_id: int, wallet_name: str, amount: Decimal) -> Wallet:
    wallet = (
        db.query(Wallet)
        .filter(Wallet.name == wallet_name, Wallet.user_id == user_id)
        .first()
    )
    wallet.balance -= amount  # type: ignore
    return wallet


def get_wallet_balance_by_name(db: Session, user_id: int, wallet_name: str) -> Wallet:
    wallet = (
        db.query(Wallet)
        .filter(Wallet.name == wallet_name, Wallet.user_id == user_id)
        .first()
    )
    return wallet


def get_all_wallets(db: Session, user_id: int) -> list[Wallet]:
    wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
    return wallets


def create_wallet(
    db: Session,
    user_id: int,
    wallet_name: str,
    initial_balance: Decimal,
    currency: CurrencyEnum,
) -> Wallet:
    wallet = Wallet(
        name=wallet_name, balance=initial_balance, user_id=user_id, currency=currency
    )
    db.add(wallet)
    db.flush()
    return wallet


def get_wallet_by_id(db: Session, user_id: int, wallet_id: int) -> Wallet | None:
    return (
        db.query(Wallet)
        .filter(Wallet.id == wallet_id, Wallet.user_id == user_id)
        .scalar()
    )
