from enum import StrEnum, auto


class CurrencyEnum(StrEnum):
    KZT = auto()
    RUB = auto()
    USD = auto()
    EUR = auto()
    BTC = auto()


class OperationType(StrEnum):
    EXPENSE = auto()
    INCOME = auto()
    TRANSFER = auto()
