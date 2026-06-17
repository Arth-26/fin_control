"""TEST CRUD"""

from http import HTTPStatus

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


def test_read_users_return_user_list(client, superuser, supertoken):
    user_public = UserPublic.model_validate(superuser).model_dump()
    response = client.get('/users/', headers={'Authorization': f'Bearer {supertoken}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_public]}


def test_get_user_return_user_object(client, superuser, supertoken):
    user_public = UserPublic.model_validate(superuser).model_dump()

    response = client.get('/users/1', headers={'Authorization': f'Bearer {supertoken}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_patch_user_username_return_user_updated(client, superuser, supertoken):
    update_username = {
        'username': 'user_test_update',
    }

    response = client.patch(f'/users/{superuser.id}', json=update_username, headers={'Authorization': f'Bearer {supertoken}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': superuser.id,
        'username': 'user_test_update',
        'email': superuser.email,
    }


def test_patch_user_email_return_user_updated(client, superuser, supertoken):
    update_email = {
        'email': 'teste_update@example.com',
    }

    response = client.patch(f'/users/{superuser.id}', json=update_email, headers={'Authorization': f'Bearer {supertoken}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': superuser.id,
        'username': superuser.username,
        'email': 'teste_update@example.com',
    }


def test_delete_user_return_success_message(client, supertoken, populate_users):
    deleted_user = client.get('/users/2', headers={'Authorization': f'Bearer {supertoken}'})

    delete_response = client.delete('/users/2', headers={'Authorization': f'Bearer {supertoken}'})

    get_response = client.get('/users', headers={'Authorization': f'Bearer {supertoken}'})

    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json() == {'message': 'Operation successfully'}
    assert deleted_user not in get_response.json().get('users')


""" TEST REQUEST USER ERROR"""


def test_request_user_token_invalid(client):
    response = client.get('/users/', headers={'Authorization': 'Bearer token-invalid'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Could not validate credentials'


def test_request_user_without_sub(client):
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\\n'
        'eyJzdWIiOiIiLCJuYW1lIjoiSm9obiBEb2UiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoxNTE2MjM5MDIyfQ.\\n'
        '9js-tKmy6VI5Fi4ZH9R4G2KEI-0zSztSbFnrAqWhU-0'
    )
    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Could not validate credentials'


def test_request_user_user_not_found(client):
    token = (
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\\n'
        'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.\\n'
        'lglybL41yaANzCILZllayO4qYQdBV1MvhVeo57eBYb0'
    )
    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Could not validate credentials'


""" TEST PERMISSIONS ERROR"""


def test_read_user_not_request_user(client, token):
    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Not Enough Permissions'


def test_get_user_unauthorized_action(client, token, populate_users):
    response = client.get('/users/2', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Not Enough Permissions'


def test_update_user_request_user_not_equal_updated_user(client, token, populate_users):
    update_email = {
        'email': 'teste_update@example.com',
    }

    response = client.patch('/users/2', json=update_email, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Not Enough Permissions'


def test_delete_user_request_user_not_superuser(client, token, populate_users):
    response = client.delete('/users/2', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json().get('detail') == 'Not Enough Permissions'


""" TEST CONCLIFT ERROR AND NOT FOUND ERROR"""


def test_create_user_username_already_exists(client, user):
    body = {
        'username': user.username,
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
        'email': user.email,
        'password': '123456',
    }

    response = client.post('/users/', json=body)

    assert response.status_code == HTTPStatus.CONFLICT

    assert response.json() == {
        'detail': 'Email already exists',
    }


def test_get_user_raise_user_not_found(client, token):
    response = client.get('/users/0', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_patch_user_username_already_exists(client, user, token, populate_users):
    update_username = {
        'username': 'test2',
    }

    response = client.patch(f'/users/{user.id}', json=update_username, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_patch_user_email_already_exists(client, user, token, populate_users):
    update_email = {
        'email': 'test2@example.com',
    }

    response = client.patch(f'/users/{user.id}', json=update_email, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_delete_user_raise_user_not_found(client, supertoken):
    response = client.delete('/users/0', headers={'Authorization': f'Bearer {supertoken}'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
