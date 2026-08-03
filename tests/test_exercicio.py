from http import HTTPStatus

from fastapi_zero.schemas import UserPublic
from fastapi_zero.security import create_access_token


def test_create_user_username_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_email_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': user.email,
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_update_user_not_found(client, token):
    response = client.put(
        '/users/100',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Você não tem permissão para atualizar este usuário'}


def test_delete_user_not_found(client, token):
    response = client.delete(
        '/users/3',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Você não tem permissão para atualizar este usuário'}


def test_read_user_not_found(client):
    response = client.get('/users/333')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado!'}


def test_read_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    respose = client.get('/users/1')

    assert respose.status_code == HTTPStatus.OK
    assert respose.json() == user_schema


def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_not_exists(client):
    data = {'sub': 'nonexistent@example.com'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_token_user_invalid(client, user):
    response = client.post(
        '/token',
        data={'username': 'nonexistent@example.com', 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert token == {'detail': 'Email ou senha inválidos'}


def test_get_token_password_invalid(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert token == {'detail': 'Email ou senha inválidos'}
