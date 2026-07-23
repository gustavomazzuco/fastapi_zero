from sqlalchemy import select

from fastapi_zero.models import User


def test_create_user(session):
    new_user = User(
        username='test', email='test@example.com', password='secret'
    )

    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'test'))

    assert user.username == 'test'
