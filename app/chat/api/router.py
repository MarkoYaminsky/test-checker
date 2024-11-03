from fastapi import APIRouter

from app.chat.api.http_handlers import chat_http_router
from app.chat.api.websocket_handlers import chat_websocket_router

chat_router = APIRouter()

chat_router.include_router(chat_websocket_router, prefix="/ws/chat")
chat_router.include_router(chat_http_router, prefix="/chat")
