from app.common.exceptions import BaseCustomException


class UserUsernameNotQniqueException(BaseCustomException):
    def __init__(self, username):
        super().__init__(description=f"Username {username} is already taken.", code="username-taken")


class UserDoesNotExistException(BaseCustomException):
    def __init__(self, username):
        super().__init__(description=f"User with username {username} does not exist.", code="user-not-exists")


class InvalidUserCredentialsException(BaseCustomException):
    def __init__(self):
        super().__init__(description="Invalid user credentials.", code="invalid-credentials")
