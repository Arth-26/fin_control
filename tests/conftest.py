from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from random import randint

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import Select, event, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import StaticPool

from fin_control.app import app
from fin_control.database import get_session
from fin_control.enums import TransactionType
from fin_control.models import Transactions, User, table_registry
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


async def create_user(session, superuser=False):
    password = '123456'
    random_idx = randint(1, 1000)
    user = User(username=f'teste_{random_idx}', superuser=superuser, email=f'teste_{random_idx}@example.com', password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    user = await session.scalar(Select(User).options(selectinload(User.transactions)).where(User.id == user.id))

    return user


@pytest_asyncio.fixture
async def user(session):
    user = await create_user(session)
    return user


@pytest_asyncio.fixture
async def superuser(session):
    user = await create_user(session, superuser=True)
    return user


@pytest_asyncio.fixture
async def transaction(session, user):
    new_transaction = Transactions(
        user_id=user.id,
        description='Teste de criação de movimentação',
        amount=Decimal(2000.00),
        type=TransactionType.INCOME,
        transaction_date=datetime(2026, 1, 1),
    )

    session.add(new_transaction)
    await session.commit()
    transaction = await session.scalars(
        Select(Transactions).options(selectinload(Transactions.user)).where(Transactions.id == new_transaction.id).limit(1)
    )

    return transaction.first()


@pytest_asyncio.fixture
async def populate_users(session: AsyncSession):
    password = '123456'
    users = []
    for i in range(1, 10 + 1):
        user = {'username': f'test{i}', 'email': f'test{i}@example.com', 'password': get_password_hash(password)}
        users.append(user)

    await session.execute(insert(User), users)
    await session.commit()


@pytest_asyncio.fixture
async def transactions_user_factory(user, session: AsyncSession):
    transactions = []
    for i in range(1, 10 + 1):
        transaction = {
            'user_id': user.id,
            'description': f'Teste de criação de movimentação {i}',
            'amount': Decimal(randint(1, 10000000)),
            'type': 'INCOME',
            'transaction_date': datetime(2026, randint(1, 12), randint(1, 28)),
        }
        transactions.append(transaction)

    await session.execute(insert(Transactions), transactions)
    await session.commit()


def token_factory(client, recieved_user):
    response = client.post('/auth/login', data={'username': recieved_user.email, 'password': recieved_user.clean_password})
    return response.json()['access_token']


@pytest.fixture
def token(client, user):
    token = token_factory(client, user)
    return token


@pytest.fixture
def supertoken(client, superuser):
    token = token_factory(client, superuser)
    return token


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
