from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from fin_control.enums import TransactionType
from fin_control.schemas.base_schemas import FilterPage
from fin_control.schemas.user_schemas import UserPublic


class TransactionSchema(BaseModel):
    description: str = Field(max_length=255)
    amount: Decimal = Field(gt=0, decimal_places=2)
    type: TransactionType
    transaction_date: date


class TransactionUpdateSchema(BaseModel):
    description: Optional[str] = Field(default=None, max_length=255)
    amount: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    type: Optional[TransactionType] = None
    transaction_date: Optional[date] = None


class TransactionPublicSchema(BaseModel):
    id: int
    user: UserPublic
    description: str
    amount: Decimal
    type: TransactionType
    transaction_date: date

    model_config = ConfigDict(from_attributes=True)


class TransactionList(BaseModel):
    transactions: list[TransactionPublicSchema]


class FilterTransictions(FilterPage):
    type: TransactionType | None = None
    transaction_date: date | None = None
