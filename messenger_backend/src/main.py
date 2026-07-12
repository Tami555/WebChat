from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.redis import redis_helper
from src.exceptions import exception_handler
from src.api.v1 import router as api_v1_router
from src.core.websocket import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("START BACKEND")
    print(f"APP ID : {id(app)}")
    await redis_helper.connect()
    await websocket_manager.initialize(server_id=f"server-{id(app)}")
    print(f"Кто онлайн: {await redis_helper.client.smembers(redis_helper.namespace.users_online)}")
    yield
    await redis_helper.disconnect()
    print("STOP BACKEND")


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
    return {"status": "ok", "db": settings.db_async_url}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
