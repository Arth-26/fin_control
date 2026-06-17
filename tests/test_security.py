import pytest
from jwt import decode

from fin_control.security import create_access_token, decode_token, get_request_user


def test_create_jwt(settings):
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_decode_token(user, token):
    decode = decode_token(token)

    assert 'sub' in decode
    assert 'exp' in decode
    assert 'type' in decode
    assert decode.get('sub') == user.email
    assert decode.get('type') == 'access'


@pytest.mark.asyncio
async def test_get_request_user_return_user(session, user, token):
    request_user = await get_request_user(session, token)

    assert user.id == request_user.id
