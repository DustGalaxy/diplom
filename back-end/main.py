from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from icecream import ic  # noqa: F401

from src.admin import authentication_backend
from src.database import engine, async_session_maker
from src.database import drop_db, create_db  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await drop_db()
    # await create_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin = Admin(
    app,
    engine,
    session_maker=async_session_maker,
    authentication_backend=authentication_backend,
)


@app.get("/ping")
async def ping():
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
