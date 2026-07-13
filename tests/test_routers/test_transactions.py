from http import HTTPStatus

from fin_control.enums import TransactionType
from fin_control.schemas.user_schemas import UserPublic

"""TEST CRUD"""

def test_read_user_transactions_return_transactions_list(client, token, user, transactions_user_factory):
    user_public = UserPublic.model_validate(user).model_dump()
    response = client.get('/transactions/', headers={'Authorization': f'Bearer {token}'})

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(data['transactions']) == 10
    for idx, transaction in enumerate(data['transactions']):
        assert transaction['id'] == idx + 1
        assert transaction['user'] == user_public


def test_read_user_transactions_filter_type_return_transactions_list(client, token, user, transactions_user_factory):
    user_public = UserPublic.model_validate(user).model_dump()
    response = client.get('/transactions/?type=INCOME', headers={'Authorization': f'Bearer {token}'})

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    for transaction in data['transactions']:
        assert transaction['type'] == TransactionType.INCOME


def test_get_user_transaction_return_transaction_object(client, user, token, transactions_user_factory):
    user_public = UserPublic.model_validate(user).model_dump()

    response = client.get('/transactions/1', headers={'Authorization': f'Bearer {token}'})

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data['id'] == 1
    assert data['user'] == user_public


def test_post_user_transactions_return_transaction_object(client, user, token):
    user_public = UserPublic.model_validate(user).model_dump()

    body = {
        'user_id': user.id,
        'description': f'Test POST transactions user {user.username}',
        'amount': 2000.00,
        'type': TransactionType.EXPENSE,
        'transaction_date': '2026-01-01',
    }

    response = client.post('/transactions/', json=body, headers={'Authorization': f'Bearer {token}'})
    data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert data['amount'] == '2000.0'
    assert data['type'] == TransactionType.EXPENSE
    assert data['transaction_date'] == '2026-01-01'
    assert data['user'] == user_public


def test_delete_user_transaction_return_status_ok(client, token, transactions_user_factory):
    response = client.delete('/transactions/10', headers={'Authorization': f'Bearer {token}'})

    transactions_response = client.get('/transactions/', headers={'Authorization': f'Bearer {token}'}).json()

    assert response.status_code == HTTPStatus.OK
    assert len(transactions_response['transactions']) == 9
    assert transactions_response['transactions'][-1]['id'] == 9


""" TEST CONCLIFT ERROR AND NOT FOUND ERROR"""

def test_get_user_transaction_not_found_error(client, token):
    response = client.get('/transactions/1', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json().get('detail') == 'Transaction not found'


def test_delete_user_transaction_not_found_error(client, token):
    response = client.delete('/transactions/1', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json().get('detail') == 'Transaction not found'
