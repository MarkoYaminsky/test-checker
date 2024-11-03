from typing import Type

from app.users.models import User


def get_user_model() -> Type[User]:
    return User
