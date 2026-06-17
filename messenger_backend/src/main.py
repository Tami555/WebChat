import uvicorn
from fastapi import FastAPI

from src.core.config import settings
from src.exceptions import exception_handler
from src.api.v1 import router as api_v1_router


app = FastAPI()
app.include_router(api_v1_router, prefix="/api/v1")
exception_handler(app)


@app.get("/app")
def health():
    return {"status": "ok", "db": settings.db_async_url}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
