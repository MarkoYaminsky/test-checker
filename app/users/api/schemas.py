from uuid import UUID

from pydantic import BaseModel


class UserSchema(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True


class UserRegistrationInputSchema(BaseModel):
    username: str
    password: str


class UserLoginInputSchema(BaseModel):
    username: str
    password: str


class UserLoginOutputSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenRefreshInputSchema(BaseModel):
    refresh_token: str


class TokenObtainByRefreshOutputSchema(BaseModel):
    access_token: str


class WebsocketTokenOutputSchema(BaseModel):
    websocket_token: str
