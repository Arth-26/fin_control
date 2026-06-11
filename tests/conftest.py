from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fin_control.app import app
from fin_control.database import get_session
from fin_control.models import User, table_registry
from fin_control.security import get_password_hash
from fin_control.settings import Settings


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session):
    password = '123456'
    user = User(username='teste', email='teste@example.com', password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def populate_users(session: AsyncSession):
    password = '123456'
    users = []
    for i in range(1, 10 + 1):
        user = {'username': f'teste{i}', 'email': f'teste{i}@example.com', 'password': get_password_hash(password)}
        users.append(user)

    await session.execute(insert(User), users)
    await session.commit()


@pytest.fixture
def token(client, user):
    response = client.post('/auth/login', data={'username': user.email, 'password': user.clean_password})

    return response.json()['access_token']


@contextmanager
def _mock_db_time(model, time=datetime(2026, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def settings():
    return Settings()
