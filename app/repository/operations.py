from datetime import datetime
from decimal import Decimal

from app.enum import CurrencyEnum
from app.models import Operation
from sqlalchemy.orm import Session


def create_operation(
    db: Session,
    wallet_id: int,
    type: str,
    amount: Decimal,
    currency: CurrencyEnum,
    new_balance: Decimal,
    category: str | None = None,
    sub_category: str | None = None,
) -> Operation:
    operation = Operation(
        wallet_id=wallet_id,
        type=type,
        amount=amount,
        currency=currency,
        new_balance=new_balance,
        category=category,
        sub_category=sub_category,
    )
    db.add(operation)
    db.flush()
    return operation


def get_operations_list(
    db: Session,
    wallets_ids: list[int],
    date_from: datetime | None,
    date_to: datetime | None,
) -> list[Operation]:

    query = db.query(Operation).filter(Operation.wallet_id.in_(wallets_ids))

    if date_from:
        query = query.filter(Operation.created_at >= date_from)

    if date_to:
        query = query.filter(Operation.created_at <= date_to)

    return query.all()
