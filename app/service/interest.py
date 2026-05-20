from decimal import Decimal
from sqlalchemy.orm import Session
from app.enum import CurrencyEnum
from app.models import User
from app.repository import wallets as wallets_repository
from fastapi import HTTPException

from app.schemas import InterestResponse


def calculate_interest(
    db: Session, current_user: User, wallet_id: int, duration_in_months: int
) -> InterestResponse:
    wallet = wallets_repository.get_wallet_by_id(
        db=db, user_id=current_user.id, wallet_id=wallet_id
    )
    if not wallet:
        raise HTTPException(
            status_code=404, detail=f"Wallet id '{wallet_id}' does not exist"
        )
    wallet_balance = wallet.balance
    wallet_currency = wallet.currency

    if (
        wallet_currency == CurrencyEnum.BTC
        or wallet_currency == CurrencyEnum.RUB
        or wallet_currency == CurrencyEnum.EUR
    ):
        raise HTTPException(
            status_code=400, detail="Interest only for USD and KZT wallets"
        )

    if wallet_currency == CurrencyEnum.KZT:
        interest = round(
            wallet_balance
            * pow(
                Decimal("1") + ((Decimal("0.141") * Decimal("30")) / Decimal("360")),
                duration_in_months,
            )
            - wallet_balance,
            2,
        )
        new_balance = wallet_balance + interest

        response = InterestResponse(
            interest=Decimal(str(interest)),
            new_balance=Decimal(str(new_balance)),
            currency=wallet_currency,
            wallet_id=wallet_id,
        )
        return response

    elif wallet_currency == CurrencyEnum.USD:
        interest = round(
            wallet_balance
            * pow(
                Decimal("1") + ((Decimal("0.01") * Decimal("30")) / Decimal("360")),
                duration_in_months,
            )
            - wallet_balance,
            2,
        )
        new_balance = wallet_balance + interest

        response = InterestResponse(
            interest=Decimal(str(interest)),
            new_balance=Decimal(str(new_balance)),
            currency=wallet_currency,
            wallet_id=wallet_id,
        )

        return response
