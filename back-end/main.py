from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import Admin

from icecream import ic  # noqa: F401

from src.admin import authentication_backend
from src.database import engine, async_session_maker, get_async_session
from src.database import drop_db, create_db  # noqa: F401

from src.app.models import User, Playlist, Track, crud_playlist, crud_user, crud_track
from src.app.schemas import UserCreate
from src.app.routes import router as app_router


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

app.include_router(app_router)


@app.get("/ping")
async def ping(db_session: Annotated[AsyncSession, Depends(get_async_session)]):
    user = await crud_user.create(db_session, UserCreate(username="test", password="test", email="test@gmail.com"))
    ic(user.id)
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
