from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import Select

from fin_control.depends import T_Session
from fin_control.models import User
from fin_control.schemas.base_schemas import Token
from fin_control.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['Auth'])

LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/login', response_model=Token)
async def login_for_access_token(form_data: LoginForm, session: T_Session):
    user = await session.scalar(Select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid email or password')

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid email or password')

    access_token = create_access_token({'sub': user.email})

    return {'token_type': 'Bearer', 'access_token': access_token}
