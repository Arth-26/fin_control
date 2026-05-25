from datetime import datetime

import pytest
from sqlalchemy import select

from fin_control.models import User


@pytest.mark.asyncio
async def test_table_user_create_object(session, mock_db_time):
    with mock_db_time(User):
        new_user = User(username='teste', email='teste@example.com', password='secret')

        session.add(new_user)
        await session.commit()

        first_user = await session.scalar(select(User).where(User.username == 'teste'))

    assert first_user.username == 'teste'
    assert first_user.email == 'teste@example.com'
    assert first_user.password == 'secret'
    assert first_user.created_at == datetime(2026, 1, 1, 0, 0, 0)
    assert first_user.updated_at == datetime(2026, 1, 1, 0, 0, 0)
