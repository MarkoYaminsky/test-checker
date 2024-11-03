from fastapi import FastAPI

from app.chat.api.router import chat_router
from app.core.db import Base, engine
from app.users.api.router import users_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(chat_router)
app.include_router(users_router)
