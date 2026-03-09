from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import Select
from sqlalchemy.orm import Session

from fin_control.database import get_session
from fin_control.models import User
from fin_control.schemas import UserList, UserPublic, UserSchema, UserUpdate

app = FastAPI()


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(page: int = 1, session=Depends(get_session)):
    offset = (page - 1) * 20
    users = session.scalars(Select(User).limit(20).offset(offset).order_by('id'))
    return {'users': users}


@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(user_id: int, session=Depends(get_session)):
    user = session.scalar(Select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    return user


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        Select(User).where((User.email == user.email) | (User.username == user.username))
    )

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

    db_user = User(**user.model_dump())

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.patch('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(user_id: int, user: UserUpdate, session=Depends(get_session)):
    user_object = session.scalar(Select(User).where(User.id == user_id))

    if not user_object:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    if user.username:
        user_exists = session.scalar(Select(User).where(User.username == user.username))
        if user_exists:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        
        user_object.username = user.username
        
    if user.email:
        user_exists = session.scalar(Select(User).where(User.email == user.email))
        if user_exists:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )
            
        user_object.email = user.email

    session.add(user_object)
    session.commit()
    session.refresh(user_object)

    return user_object


@app.delete('/users/{user_id}', status_code=HTTPStatus.OK)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_object = session.scalar(Select(User).where(User.id == user_id))

    if not user_object:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    session.delete(user_object)
    session.commit()

    return {'message': 'Operation successfully'}
