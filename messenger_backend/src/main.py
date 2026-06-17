import uvicorn
from fastapi import FastAPI
from .core.config import settings

app = FastAPI()


@app.get("/")
def health():
    return {"status": "ok", "db": settings.db_async_url}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
