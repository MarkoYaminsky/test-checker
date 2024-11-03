from typing import Any, Optional

from sqlalchemy import BinaryExpression
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query, Session

from app.auth.types import JWTTokenType
from app.common.services import get_all_entities_query
from app.users.api.schemas import UserLoginOutputSchema
from app.users.exceptions import (
    InvalidUserCredentialsException,
    UserDoesNotExistException,
    UserUsernameNotQniqueException,
)
from app.users.models import User


def get_all_users_query(db: Session, *, condition: Optional[BinaryExpression] = None, **filters: Any) -> Query[User]:
    return get_all_entities_query(db, User, condition=condition, **filters)


def create_user(db: Session, username: str, password: str) -> Optional[User]:
    from app.auth.services import hash_password

    try:
        user = User(username=username, password=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        raise UserUsernameNotQniqueException(username=username)
    return user


def login_user(db: Session, username: str, password: str) -> UserLoginOutputSchema:
    from app.auth.services import create_jwt_token, verify_password

    user = get_all_users_query(db, username=username).scalar()
    if user is None:
        raise UserDoesNotExistException(username=username)
    if not verify_password(password, user.password):
        raise InvalidUserCredentialsException()
    return UserLoginOutputSchema(
        access_token=create_jwt_token(user_id=user.id, token_type=JWTTokenType.access),
        refresh_token=create_jwt_token(user_id=user.id, token_type=JWTTokenType.refresh),
    )
