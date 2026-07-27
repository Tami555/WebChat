from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.users import router as users_router
from .endpoints.websocket import router as websocket_router
from .endpoints.chats import router as chatting_router
from .endpoints.groups import router as groups_router
from .endpoints.dialogs import router as dialogs_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(websocket_router, prefix="/websocket", tags=["Websocket"])
router.include_router(chatting_router, prefix="/chats", tags=["Chats"])
router.include_router(groups_router, prefix="/groups", tags=["Groups"])
router.include_router(dialogs_router, prefix="/dialogs", tags=["Dialogs"])


__all__ = ("router",)
