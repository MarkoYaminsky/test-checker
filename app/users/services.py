from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services import verify_password
from app.auth.types import JWTTokenType
from app.common.services import quick_select
from app.common.utilities import get_user_model
from app.users.exceptions import (
    InvalidUserCredentialsException,
    UserDoesNotExistException,
    UserUsernameNotQniqueException,
)
from app.users.schemas import UserLoginOutputSchema

User = get_user_model()


def create_user(session: AsyncSession, username: str, password: str) -> User | None:
    from app.auth.services import hash_password

    try:
        user = User(username=username, password=hash_password(password))
        session.add(user)
        session.commit()
        session.refresh(user)
    except IntegrityError:
        raise UserUsernameNotQniqueException(username=username)
    return user


async def login_user(session: AsyncSession, username: str, password: str) -> UserLoginOutputSchema:
    from app.auth.services import create_jwt_token

    user = (
        await quick_select(
            session=session,
            model=User,
        )
    ).scalar()
    if user is None:
        raise UserDoesNotExistException(username=username)
    if not verify_user_password(user, password):
        raise InvalidUserCredentialsException()
    return UserLoginOutputSchema(
        access_token=create_jwt_token(user_id=user.id, token_type=JWTTokenType.access),
        refresh_token=create_jwt_token(user_id=user.id, token_type=JWTTokenType.refresh),
    )


def verify_user_password(user: User, plain_password: str) -> bool:
    return verify_password(plain_password, user.password)
