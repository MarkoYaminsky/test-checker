from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.auth.services import get_ws_authenticated_user
from app.common.dependencies import get_db

chat_websocket_router = APIRouter()


connections = {}


@chat_websocket_router.websocket("/{receiver_id}/")
async def message_handler_websocket_route(websocket: WebSocket, receiver_id: str, db: Session = Depends(get_db)):
    origin_user = get_ws_authenticated_user(db=db, token=websocket.query_params.get("origin"))
    origin_user_id = str(origin_user.id)
    await websocket.accept()
    connections[origin_user_id] = websocket
    try:
        while True:
            data = (await websocket.receive_text()).strip()
            if data:
                receiver_websocket = connections.get(receiver_id)
                if receiver_websocket is not None:
                    await receiver_websocket.send_text(data)
    except WebSocketDisconnect:
        del connections[origin_user_id]
        await websocket.close()
