import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.redis import online_redis, redis_manager
from src.exceptions import exception_handler
from src.api.v1 import router as api_v1_router
from src.core.websocket import websocket_manager
from src.utils.logging.config import setup_logging


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.debug("START BACKEND")
    logger.info(f"APP ID : {id(app)}")
    await redis_manager.connect()
    await websocket_manager.initialize(server_id=f"server-{id(app)}")
    logger.info(f"Кто онлайн: {await online_redis.get_all_online()}")
    yield
    await websocket_manager.shutdown()
    await redis_manager.disconnect()
    logger.debug("STOP BACKEND")


app = FastAPI(lifespan=lifespan)
app.include_router(api_v1_router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешённые источники
    allow_credentials=True,  # Разрешить отправку учётных данных (куки, Authorization)
    allow_methods=["*"],  # Разрешить все HTTP-методы
    allow_headers=["*"],  # Разрешить все заголовки
)
exception_handler(app)


@app.get("/app")
def health():
    return {"status": "ok", "db": settings.db.db_async_url}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
