from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.auth.types import JWTTokenType
from app.common.decorators import expects_exceptions
from app.common.dependencies import get_db, get_http_authenticated_user
from app.common.utilities import get_user_model
from app.users.api.schemas import (
    TokenObtainByRefreshOutputSchema,
    TokenRefreshInputSchema,
    UserLoginInputSchema,
    UserLoginOutputSchema,
    UserRegistrationInputSchema,
    UserSchema,
    WebsocketTokenOutputSchema,
)
from app.users.exceptions import (
    UserDoesNotExistException,
    UserUsernameNotQniqueException,
)
from app.users.services import create_user, login_user

user_http_router = APIRouter()

User = get_user_model()


@user_http_router.get("/self/", response_model=UserSchema)
async def get_self_route(user: User = Depends(get_http_authenticated_user)):
    return user


@user_http_router.post("/register/", response_model=UserSchema)
@expects_exceptions({UserUsernameNotQniqueException: status.HTTP_400_BAD_REQUEST})
async def register_user_route(registration_data: UserRegistrationInputSchema, db: Session = Depends(get_db)):
    return create_user(db, username=registration_data.username, password=registration_data.password)


@user_http_router.post("/login/", response_model=UserLoginOutputSchema)
@expects_exceptions(
    {
        UserDoesNotExistException: status.HTTP_404_NOT_FOUND,
    }
)
async def login_user_route(credentials: UserLoginInputSchema, db: Session = Depends(get_db)):
    return login_user(db, username=credentials.username, password=credentials.password)


@user_http_router.post("/tokens/obtain/", response_model=TokenObtainByRefreshOutputSchema)
async def obtain_access_token_route(token_info: TokenRefreshInputSchema):
    from app.auth.services import issue_access_token_by_refresh_token

    return {"access_token": issue_access_token_by_refresh_token(token_info.refresh_token)}


@user_http_router.post("/tokens/websocket/", response_model=WebsocketTokenOutputSchema)
async def obtain_websocket_token_route(user: User = Depends(get_http_authenticated_user)):
    from app.auth.services import create_jwt_token

    return {"websocket_token": create_jwt_token(user.id, token_type=JWTTokenType.websocket)}
