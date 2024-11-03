import factory

from app.auth.services import hash_password
from app.common.utilities import get_user_model

User = get_user_model()


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    default_password = "password"

    username = factory.Faker("user_name")

    @classmethod
    def create(cls, **kwargs) -> User:
        if "password" in kwargs:
            password = hash_password(kwargs.pop("password"))
        else:
            password = hash_password(cls.default_password)
        return super().create(password=password, **kwargs)
