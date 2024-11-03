from fastapi import APIRouter

from app.users.api.http_handlers import user_http_router

users_router = APIRouter()

users_router.include_router(user_http_router, prefix="/users")
