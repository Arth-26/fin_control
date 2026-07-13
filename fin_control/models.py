from datetime import date, datetime
from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from fin_control.enums import TransactionType

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())
    transactions: Mapped[List['Transactions']] = relationship(
        back_populates='user', cascade='all, delete-orphan', lazy='selectin', default_factory=list, init=False
    )


@table_registry.mapped_as_dataclass
class Transactions:
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, init=False, server_default=func.now())
    user: Mapped[User] = relationship(back_populates='transactions', lazy='selectin', init=False)
