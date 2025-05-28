from contextlib import asynccontextmanager
import sys
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import Admin

from loguru import logger
from icecream import ic  # noqa: F401

from src.admin import authentication_backend
from src.database import engine, async_session_maker, get_async_session
from src.database import drop_db, create_db  # noqa: F401

from src.app.models import crud_features, crud_track, crud_user
from src.app.schemas import UserCreate
from src.app.routes import router as app_router
from src.app.tasks import track_features
from src.broker_taskiq import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await drop_db()
    # await create_db()
    logger.add(
        sys.stderr,
        colorize=True,
        format="<green>{time}</green> <level>{level}</level> {message}",
        filter="my_module",
        level="INFO",
    )
    logger.add("file_{time}.log", rotation="12:00", compression="zip")

    await broker.startup()
    yield
    await broker.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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


@app.get("/rebuild_all_audio")
async def rebuild_all(db_session: Annotated[AsyncSession, Depends(get_async_session)]):
    tracks = await crud_track.get_all(db_session, limit=None)
    f_tracks = await crud_features.get_all(db_session, limit=None)
    ids = [item.yt_id for item in f_tracks[0]]

    for track in tracks[0]:
        if track.yt_id not in ids:
            print(track.yt_id)
            await track_features.kiq(track.yt_id)

    return {"message": "pong"}


@app.get("/rebuild_one_audio")
async def rebuild_one(db_session: Annotated[AsyncSession, Depends(get_async_session)]):
    tracks = await crud_track.get_all(db_session, limit=10)

    await track_features.kiq(tracks[0][0].yt_id)
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
