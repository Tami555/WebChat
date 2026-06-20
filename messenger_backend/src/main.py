from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

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
    yield
    await redis_helper.disconnect()
    print("STOP BACKEND")

app = FastAPI(lifespan=lifespan)
app.include_router(api_v1_router, prefix="/api/v1")
exception_handler(app)


@app.get("/app")
def health():
    return {"status": "ok", "db": settings.db_async_url}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
