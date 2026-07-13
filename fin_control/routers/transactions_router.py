from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import Select

from fin_control.depends import Request_User, T_Session
from fin_control.models import Transactions
from fin_control.schemas.transaction_schemas import FilterTransictions, TransactionList, TransactionPublicSchema, TransactionSchema

router = APIRouter(prefix='/transactions', tags=['Transactions'])


@router.get('/', status_code=HTTPStatus.OK, response_model=TransactionList)
async def read_user_transactions(session: T_Session, request_user: Request_User, filter: Annotated[FilterTransictions, Query()]):
    offset = (filter.page - 1) * filter.limit
    query = Select(Transactions).where(Transactions.user_id == request_user.id)

    filters = [
        Transactions.user_id == request_user.id
    ]

    if filter.type:
        filters.append(Transactions.type == filter.type)

    query = (
        Select(Transactions)
        .where(*filters)
        .order_by(Transactions.id)
        .offset(offset)
        .limit(filter.limit)
    )

    transactions = await session.scalars(query)

    return {'transactions': transactions.all()}


@router.get('/{transaction_id}', status_code=HTTPStatus.OK, response_model=TransactionPublicSchema)
async def get_transaction(transaction_id: int, session: T_Session, request_user: Request_User):
    transactions = await session.scalar(
        Select(Transactions).where(
            Transactions.user_id == request_user.id, Transactions.id == transaction_id
        )
    )

    if not transactions:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Transaction not found')

    # if transactions.user_id != request_user.id:
    #     raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Not Enough Permissions')

    return transactions


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TransactionPublicSchema)
async def create_transaction(data: TransactionSchema, session: T_Session, request_user: Request_User):
    new_transaction = Transactions(
        user_id=request_user.id,
        description=data.description,
        amount=data.amount,
        type=data.type,
        transaction_date=data.transaction_date,
    )

    session.add(new_transaction)

    await session.commit()
    await session.refresh(new_transaction, attribute_names=['user'])

    # transaction = await session.scalar(Select(Transactions).options(selectinload(Transactions.user)).where(Transactions.id == new_transaction.id))

    return new_transaction


@router.delete('/{transaction_id}', status_code=HTTPStatus.OK)
async def delete_transaction(transaction_id: int, session: T_Session, request_user: Request_User):
    transaction = await session.scalar(
        Select(Transactions).where(
            Transactions.user_id == request_user.id, Transactions.id == transaction_id
        )
    )

    if not transaction:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Transaction not found')

    # if request_user.id != transaction.user_id:
    #     raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Not Enough Permissions')

    await session.delete(transaction)
    await session.commit()

    return {'message': 'Operation successfully'}
