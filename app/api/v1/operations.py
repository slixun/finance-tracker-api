from datetime import datetime
from fastapi import APIRouter, Depends, Query

from app.dependency import get_current_user, get_db
from app.models import User
from app.schemas import OperationRequest, OperationResponse, TransferCreateSchema
from app.service import operations as operations_service
from sqlalchemy.orm import Session

router = APIRouter()


# Depends() tells FastAPI that before doing a function it has to do another function(dependency)
# before running add_expense(), it runs get_db, gets a value and then stores it in db argument
@router.post("/operations/expense", response_model=OperationResponse)
def add_expense(
    operation: OperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return operations_service.add_expense(db, current_user, operation)


@router.post("/operations/income", response_model=OperationResponse)
def add_income(
    operation: OperationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return operations_service.add_income(db, current_user, operation)


@router.get("/operations", response_model=list[OperationResponse])
def list_operations(
    wallet_id: int | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return operations_service.get_operations_list(
        db, current_user, wallet_id, date_from, date_to
    )


@router.post("/operations/transfer", response_model=OperationResponse)
async def create_transfer(
    payload: TransferCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await operations_service.transfer_between_wallets(
        db,
        current_user.id,
        payload.from_wallet_id,
        payload.to_wallet_id,
        payload.amount,
    )
