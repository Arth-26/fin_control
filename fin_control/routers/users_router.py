from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import Select

from fin_control.depends import Request_User, T_Filter_Page, T_Session
from fin_control.models import User
from fin_control.schemas.user_schemas import UserList, UserPublic, UserSchema, UserUpdate
from fin_control.security import get_password_hash

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(session: T_Session, request_user: Request_User, pagination: T_Filter_Page):
    if not request_user.superuser:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Not Enough Permissions')

    offset = (pagination.page - 1) * pagination.limit
    users = await session.scalars(Select(User).limit(pagination.limit).offset(offset).order_by('id'))

    return {'users': users}


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def get_user(user_id: int, session: T_Session, request_user: Request_User):
    user = await session.scalar(Select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    if not request_user.superuser and user_id != request_user.id:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Not Enough Permissions')

    return user


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session):
    db_user = await session.scalar(Select(User).where((User.email == user.email) | (User.username == user.username)))

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    db_user = User(username=user.username, email=user.email, password=get_password_hash(user.password))

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.patch('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(user_id: int, user: UserUpdate, session: T_Session, request_user: Request_User):
    if user_id != request_user.id:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Not Enough Permissions')

    user_object = request_user

    if user.username:
        user_exists = await session.scalar(Select(User).where(User.username == user.username))
        if user_exists:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )

        user_object.username = user.username

    if user.email:
        user_exists = await session.scalar(Select(User).where(User.email == user.email))
        if user_exists:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

        user_object.email = user.email

    session.add(user_object)
    await session.commit()
    await session.refresh(user_object)

    return user_object


@router.delete('/{user_id}', status_code=HTTPStatus.OK)
async def delete_user(user_id: int, session: T_Session, request_user: Request_User):
    if not request_user.superuser:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Not Enough Permissions')

    user_object = await session.scalar(Select(User).where(User.id == user_id))

    if not user_object:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    await session.delete(user_object)
    await session.commit()

    return {'message': 'Operation successfully'}
