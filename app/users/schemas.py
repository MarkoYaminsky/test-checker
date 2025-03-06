from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints


class UserOutputSchema(BaseModel):
    id: UUID
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserRegistrationInputSchema(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3)]
    password: Annotated[str, StringConstraints(min_length=3)]


class UserLoginInputSchema(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3)]
    password: Annotated[str, StringConstraints(min_length=3)]


class UserLoginOutputSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenRefreshInputSchema(BaseModel):
    refresh_token: str


class TokenObtainByRefreshOutputSchema(BaseModel):
    access_token: str
