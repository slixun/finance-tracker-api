from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import User
from app.dependency import get_current_user, get_db
from app.schemas import AllInterestResponse, InterestDuration, InterestResponse
from app.service import interest as interest_service

router = APIRouter()


@router.post("/interest/{wallet_id}", response_model=InterestResponse)
def calculate_interest(
    wallet_id: int,
    duration_in_months: InterestDuration,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return interest_service.calculate_interest(
        db, current_user, wallet_id, duration_in_months.duration_in_months
    )


@router.post("/interest", response_model=AllInterestResponse)
async def calculate_all_interest(
    duration_in_months: InterestDuration,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await interest_service.calculate_all_interest(
        db, current_user, duration_in_months.duration_in_months
    )
