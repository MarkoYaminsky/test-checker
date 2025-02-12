from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.common.decorators import expects_exceptions
from app.common.dependencies import get_db_session, get_http_authenticated_user
from app.common.utilities import get_user_model
from app.users.exceptions import (
    UserDoesNotExistException,
    UserUsernameNotQniqueException,
)
from app.users.schemas import (
    TokenObtainByRefreshOutputSchema,
    TokenRefreshInputSchema,
    UserLoginInputSchema,
    UserLoginOutputSchema,
    UserOutputSchema,
    UserRegistrationInputSchema,
)
from app.users.services import create_user, login_user

users_router = APIRouter()

User = get_user_model()


@users_router.get("/self/", response_model=UserOutputSchema)
async def get_self_route(user: User = Depends(get_http_authenticated_user)):
    return user


@users_router.post("/register/", response_model=UserOutputSchema)
@expects_exceptions({UserUsernameNotQniqueException: status.HTTP_400_BAD_REQUEST})
async def register_user_route(registration_data: UserRegistrationInputSchema, db: Session = Depends(get_db_session)):
    return create_user(db, username=registration_data.username, password=registration_data.password)


@users_router.post("/login/", response_model=UserLoginOutputSchema)
@expects_exceptions(
    {
        UserDoesNotExistException: status.HTTP_404_NOT_FOUND,
    }
)
async def login_user_route(credentials: UserLoginInputSchema, db: Session = Depends(get_db_session)):
    return login_user(db, username=credentials.username, password=credentials.password)


@users_router.post("/tokens/obtain/", response_model=TokenObtainByRefreshOutputSchema)
async def obtain_access_token_route(token_info: TokenRefreshInputSchema):
    from app.auth.services import issue_access_token_by_refresh_token

    return {"access_token": issue_access_token_by_refresh_token(token_info.refresh_token)}
