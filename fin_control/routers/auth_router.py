import os
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from sqlalchemy import Select

from fin_control.depends import T_Session
from fin_control.models import User
from fin_control.schemas.base_schemas import RefreshTokenRequest, Token
from fin_control.security import create_access_token, decode_token, verify_password
from fin_control.settings import Settings

router = APIRouter(prefix='/auth', tags=['Auth'])

LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


@router.post('/login', response_model=Token)
async def login(form_data: LoginForm, session: T_Session):
    user = await session.scalar(Select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid email or password')

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid email or password')

    access_token = create_access_token({'sub': user.email})

    expire_refresh_token = (REFRESH_TOKEN_EXPIRE_DAYS * 24) * 60
    refresh_token = create_access_token({'sub': user.email}, expire_time=expire_refresh_token, type='refresh')
    return {'token_type': 'Bearer', 'access_token': access_token, 'refresh_token': refresh_token}


@router.post('/refresh', response_model=Token)
async def refresh_access_token(
    data: RefreshTokenRequest,
):
    try:
        payload = decode_token(data.refresh_token)

        if payload.get('type') != 'refresh':
            raise HTTPException(status_code=401, detail='Invalid refresh token')

        email = payload.get('sub')

        new_access_token = create_access_token({'sub': email, 'type': 'access'})

        return {'token_type': 'Bearer', 'access_token': new_access_token, 'refresh_token': data.refresh_token}
    except InvalidTokenError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Expired refresh token', headers={'WWW-Authenticate': 'Bearer'})
