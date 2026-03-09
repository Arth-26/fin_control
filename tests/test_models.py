from datetime import datetime

from sqlalchemy import select

from fin_control.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(User):
        new_user = User(username='teste', email='teste@example.com', password='secret')

        session.add(new_user)
        session.commit()

        first_user = session.scalar(select(User).where(User.username == 'teste'))

    assert first_user.username == 'teste'
    assert first_user.email == 'teste@example.com'
    assert first_user.password == 'secret'
    assert first_user.created_at == datetime(2026, 1, 1, 0, 0, 0)
    assert first_user.updated_at == datetime(2026, 1, 1, 0, 0, 0)
