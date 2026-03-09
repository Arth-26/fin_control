from http import HTTPStatus

from fin_control.schemas import UserPublic


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


def test_read_user_return_user_list(client, user):
    user_public = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_public]}


def test_get_user_return_user_object(client, user):
    user_public = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_public


def test_get_user_raise_user_not_found(client):
    response = client.get('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


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


def test_delete_user_return_success_message(client, user):
    delete_response = client.delete('/users/1')
    
    get_response = client.get('/users')

    assert delete_response.status_code == HTTPStatus.OK
    assert delete_response.json() == {'message': 'Operation successfully'}
    assert get_response.json() == {'users': []}


def test_delete_user_raise_user_not_found(client):
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}

