from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from app.enum import CurrencyEnum


class OperationRequest(BaseModel):
    wallet_name: str = Field(..., max_length=127)
    amount: Decimal
    description: str | None = Field(None, max_length=255)

    @field_validator("amount")
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")

        return v

    @field_validator("wallet_name")
    def wallet_name_not_empty(cls, v: str) -> str:
        # remove spaces on the sides
        v = v.strip()
        # check if the name is empty
        if not v:
            raise ValueError("Wallet name cannot be empty")

        return v  # returns the new value as an attribute


class CreateWalletRequest(BaseModel):
    name: str = Field(..., max_length=127)
    initial_balance: Decimal = Decimal(0)
    currency: CurrencyEnum = CurrencyEnum.KZT

    @field_validator("initial_balance")
    def balance_not_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Amount cannot be negative")

        return v

    @field_validator("name")
    def name_not_empty(cls, v: str) -> str:
        # remove spaces on the sides
        v = v.strip()
        # check if the name is empty
        if not v:
            raise ValueError("Wallet name cannot be empty")

        return v  # returns the new value as an attribute


class WalletUpdateRequest(BaseModel):
    name: str = Field(..., max_length=127)
    balance: Decimal = Decimal(0)

    @field_validator("balance")
    def balance_not_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Amount cannot be negative")

        return v

    @field_validator("name")
    def name_not_empty(cls, v: str) -> str:
        # remove spaces on the sides
        v = v.strip()
        # check if the name is empty
        if not v:
            raise ValueError("Wallet name cannot be empty")

        return v  # returns the new value as an attribute


class UserRequest(BaseModel):
    login: str = Field(..., max_length=127)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    # from_attributes=True → allows ORM model → Pydantic model conversion
    id: int
    login: str = Field(..., max_length=127)


class Token(BaseModel):
    access_token: str
    token_type: str


class WalletResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    balance: Decimal
    currency: CurrencyEnum


class OperationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    wallet_id: int
    type: str
    amount: Decimal
    currency: CurrencyEnum
    new_balance: Decimal | None
    category: str | None
    sub_category: str | None
    created_at: datetime


class TransferCreateSchema(BaseModel):
    from_wallet_id: int
    to_wallet_id: int
    amount: Decimal

    @field_validator("to_wallet_id")
    @classmethod
    def wallets_must_differ(cls, v: int, info) -> int:
        # info - special object that Pydantic gives you containing information about all the fields in the request.
        if "from_wallet_id" in info.data and v == info.data["from_wallet_id"]:
            raise ValueError("Same wallet ids!")
        return v

    @field_validator("amount")
    def amount_gt_zero(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class InterestDuration(BaseModel):
    duration_in_months: int = 1

    @field_validator("duration_in_months")
    def duration_gt_one(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Duration cannot be less than 1 month")
        return v


class InterestResponse(BaseModel):
    interest: Decimal
    new_balance: Decimal
    currency: CurrencyEnum
    wallet_id: int


class AllInterestResponse(BaseModel):
    total_interest: Decimal
    wallet_interest_list: list[InterestResponse]


class TotalBalance(BaseModel):
    total_balance: Decimal
