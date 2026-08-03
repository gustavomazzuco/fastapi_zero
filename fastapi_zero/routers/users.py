from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session=Depends(get_session)):
    db_user = session.scalar(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    # Se não der o erro, cria um novo user
    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int, session=Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado!')

    return user


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user: UserSchema,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para atualizar este usuário',
        )

    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )

    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Você não tem permissão para atualizar este usuário',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'Usuário excluído com sucesso!'}
