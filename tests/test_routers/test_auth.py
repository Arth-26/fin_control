from http import HTTPStatus

from freezegun import freeze_time

""" TEST AUTH REQUESTS """


def test_login(client, user):
    form_data = {'username': user.email, 'password': '123456'}

    response = client.post('/auth/login', data=form_data)

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()
    assert 'token_type' in response.json()
    assert response.json()['token_type'] == 'Bearer'


def test_refresh_token(client, user, token):
    form_data = {'username': user.email, 'password': '123456'}

    response = client.post('/auth/login', data=form_data)

    body = {'refresh_token': response.json().get('refresh_token')}
    response = client.post('/auth/refresh', json=body)

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()
    assert 'token_type' in response.json()
    assert response.json()['token_type'] == 'Bearer'


""" TEST RAISES """


def test_raise_login_invalid_email(client, user):
    form_data = {'username': 'teste@example.net', 'password': '123456'}

    response = client.post('/auth/login', data=form_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Invalid email or password'


def test_raise_login_invalid_password(client, user):
    form_data = {'username': 'teste@example.com', 'password': '123456789'}

    response = client.post('/auth/login', data=form_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Invalid email or password'


def test_raise_request_unauthorized_expire_token(client, user):
    with freeze_time('2026-06-10 16:00:00'):
        response = client.post(
            '/auth/login',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-06-10 16:40:00'):
        response = client.get(f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_raise_request_unauthorized_expire_refresh_token(client, user):
    with freeze_time('2026-06-10 16:00:00'):
        response = client.post(
            '/auth/login',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        refresh_token = response.json()['refresh_token']

    with freeze_time('2026-06-18 16:00:00'):
        response = client.post('/auth/refresh', json={'refresh_token': refresh_token})
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Expired refresh token'}


def test_raise_request_unauthorize_type_token_not_refresh(client, token):
    response = client.post('/auth/refresh', json={'refresh_token': token})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid refresh token'}
