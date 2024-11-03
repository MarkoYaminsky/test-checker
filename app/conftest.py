from app.common.test_factories import UserFactory
from app.common.utilities import get_user_model

User = get_user_model()


def user() -> User:
    return UserFactory()
