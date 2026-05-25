from http import HTTPStatus

import pytest

""" TEST AUTH REQUESTS """


def test_login_for_access_token(client, user):
    form_data = {'username': 'teste@example.com', 'password': '123456'}

    response = client.post('/auth/login', data=form_data)

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()
    assert response.json()['token_type'] == 'Bearer'


""" TEST RAISES """

def test_raise_login_for_access_token_invalid_email(client, user):
    form_data = {'username': 'teste@example.net', 'password': '123456'}

    response = client.post('/auth/login', data=form_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Invalid email or password'


def test_raise_login_for_access_token_invalid_password(client, user):
    form_data = {'username': 'teste@example.com', 'password': '123456789'}

    response = client.post('/auth/login', data=form_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Invalid email or password'
