from app.dependency import get_current_user, get_db
from app.models import User
from app.service import wallets as wallets_service
from fastapi import APIRouter, Depends
from app.schemas import CreateWalletRequest, TotalBalance, WalletResponse
from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/balance", response_model=TotalBalance)
async def get_total_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await wallets_service.get_total_balance(db, current_user)


@router.get("/wallets", response_model=list[WalletResponse])
def list_wallets(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return wallets_service.list_wallets(db, current_user)


@router.post("/wallets", response_model=WalletResponse)
def create_wallet(
    wallet: CreateWalletRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return wallets_service.create_wallet(db, current_user, wallet)


@router.delete("/wallets")
def delete_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return wallets_service.delete_wallet(db, current_user, wallet_id)
