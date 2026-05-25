"""TEST CRUD"""

from http import HTTPStatus
import pytest

from fin_control.schemas.user_schemas import UserPublic


def test_create_user_return_user_objects(client):
    body = {
        'username': 'user_test',
        'email': 'example@gmail.com',
        'password': '123456',
    }

    response = client.post('/users/', json=body)

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'id': 1,
        'username': 'user_test',
        'email': 'example@gmail.com',
    }


def test_read_users_return_user_list(client, user, token):
    user_public = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_public]}


def test_get_user_return_user_object(client, user):
    user_public = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_patch_user_username_return_user_updated(client, user):
    update_username = {
        'username': 'user_test_update',
    }

    user_id = 1
    response = client.patch(f'/users/{user_id}', json=update_username)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user_id,
        'username': 'user_test_update',
        'email': user.email,
    }


def test_patch_user_email_return_user_updated(client, user):
    update_email = {
        'email': 'teste_update@example.com',
    }

    user_id = 1
    response = client.patch(f'/users/{user_id}', json=update_email)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user_id,
        'username': user.username,
        'email': 'teste_update@example.com',
    }


def test_delete_user_return_success_message(client, user, token, populate_users):
    get_user_for_delete = client.get('/users/2')

    delete_response = client.delete('/users/2')

    get_response = client.get('/users', headers={'Authorization': f'Bearer {token}'})

    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json() == {'message': 'Operation successfully'}
    assert get_user_for_delete not in get_response.json().get('users')


""" TEST PERMISSION ERROR"""


def test_read_users_token_invalid(client):
    response = client.get('/users/', headers={'Authorization': 'Bearer token-invalid'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Could not validate credentials'


def test_read_users_without_sub(client):
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\\n'
        'eyJzdWIiOiIiLCJuYW1lIjoiSm9obiBEb2UiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoxNTE2MjM5MDIyfQ.\\n'
        '9js-tKmy6VI5Fi4ZH9R4G2KEI-0zSztSbFnrAqWhU-0'
    )
    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Could not validate credentials'


def test_read_users_user_not_found(client):
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\\n'
        'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.\\n'
        'lglybL41yaANzCILZllayO4qYQdBV1MvhVeo57eBYb0'
    )
    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Could not validate credentials'


""" TEST CONCLIFT ERROR AND NOT FOUND ERROR"""


def test_create_user_username_already_exists(client, user):
    body = {
        'username': 'teste',
        'email': 'example@gmail.com',
        'password': '123456',
    }

    response = client.post('/users/', json=body)

    assert response.status_code == HTTPStatus.CONFLICT

    assert response.json() == {
        'detail': 'Username already exists',
    }


def test_create_user_email_already_exists(client, user):
    body = {
        'username': 'user_test',
        'email': 'teste@example.com',
        'password': '123456',
    }

    response = client.post('/users/', json=body)

    assert response.status_code == HTTPStatus.CONFLICT

    assert response.json() == {
        'detail': 'Email already exists',
    }


def test_get_user_raise_user_not_found(client):
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_patch_user_username_already_exists(client, user):
    new_user_json = {
        'username': 'test2',
        'email': 'test2@example.com',
        'password': '123456',
    }

    client.post('/users', json=new_user_json)

    update_username = {
        'username': 'test2',
    }

    user_id = 1
    response = client.patch(f'/users/{user_id}', json=update_username)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_patch_user_email_already_exists(client, user):
    new_user_json = {
        'username': 'test2',
        'email': 'test2@example.com',
        'password': '123456',
    }

    client.post('/users', json=new_user_json)

    update_email = {
        'email': 'test2@example.com',
    }

    user_id = 1
    response = client.patch(f'/users/{user_id}', json=update_email)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_patch_user_raise_user_not_found(client):
    body = {
        'username': 'user_test_update',
    }

    response = client.patch('/users/0', json=body)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_raise_user_not_found(client):
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
