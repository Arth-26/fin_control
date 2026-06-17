from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import select

from fin_control.enums import TransactionType
from fin_control.models import Transactions


@pytest.mark.asyncio
async def test_table_transaction_create_object(session, user, mock_db_time):
    with mock_db_time(Transactions):
        new_transaction = Transactions(
            user_id=user.id,
            description='Teste de criação de movimentação',
            amount=Decimal(2000.00),
            type=TransactionType.INCOME,
            transaction_date=datetime(2026, 1, 1),
        )

        session.add(new_transaction)
        await session.commit()

        first_transaction = await session.scalar(select(Transactions).where(Transactions.user_id == user.id))

    assert first_transaction.user_id == user.id
    assert first_transaction.description == 'Teste de criação de movimentação'
    assert first_transaction.amount == Decimal(2000.00)
    assert first_transaction.type == 'INCOME'
    assert first_transaction.transaction_date == datetime(2026, 1, 1, 0, 0, 0)
    assert first_transaction.created_at == datetime(2026, 1, 1, 0, 0, 0)
