from decimal import Decimal
from fastapi import HTTPException


from app.enum import CurrencyEnum
from app.models import User, Wallet
from app.schemas import (
    CreateWalletRequest,
    TotalBalance,
    WalletResponse,
    WalletUpdateRequest,
)
from app.repository import wallets as wallets_repository
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.service import exchange_service


async def get_total_balance(db: Session, current_user: User) -> TotalBalance:
    wallets = wallets_repository.get_all_wallets(db, current_user.id)
    total_balance = Decimal(0)
    for wallet in wallets:
        if wallet.currency != CurrencyEnum.KZT:
            rate = await exchange_service.get_exchange_rate(
                wallet.currency, CurrencyEnum.KZT
            )
            total_balance += wallet.balance * rate
        else:
            total_balance += wallet.balance

    return TotalBalance(total_balance=total_balance)


def create_wallet(
    db: Session, current_user: User, wallet: CreateWalletRequest
) -> WalletResponse:
    if wallets_repository.is_wallet_existing(db, current_user.id, wallet.name):
        raise HTTPException(
            status_code=400, detail=f"Wallet '{wallet.name}'already exists "
        )

    wallet = wallets_repository.create_wallet(
        db, current_user.id, wallet.name, wallet.initial_balance, wallet.currency
    )

    db.commit()

    return WalletResponse.model_validate(wallet)


def update_wallet(
    db: Session, current_user: User, wallet_id: int, payload: WalletUpdateRequest
) -> WalletResponse:
    wallet = wallets_repository.get_wallet_by_id(
        db=db, user_id=current_user.id, wallet_id=wallet_id
    )
    if not wallet:
        raise HTTPException(
            status_code=404, detail=f"Wallet id '{wallet_id}' does not exist"
        )
    wallet.balance = payload.balance
    wallet.name = payload.name

    db.commit()
    db.refresh(wallet)
    return WalletResponse.model_validate(wallet)


def delete_wallet(db: Session, current_user: User, wallet_id: int):
    wallet = wallets_repository.get_wallet_by_id(
        db=db, user_id=current_user.id, wallet_id=wallet_id
    )
    if not wallet:
        raise HTTPException(
            status_code=404, detail=f"Wallet id '{wallet_id}' does not exist"
        )
    try:
        db.delete(wallet)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Cannot delete wallet with existing operations"
        )
    return WalletResponse.model_validate(wallet)


def list_wallets(db: Session, current_user: User) -> list[WalletResponse]:
    wallets = wallets_repository.get_all_wallets(db, current_user.id)
    return [WalletResponse.model_validate(wallet) for wallet in wallets]
