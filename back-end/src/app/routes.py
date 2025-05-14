from typing import Annotated, Tuple
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import NotFoundException
from app.services import TrackMeta, YTService
from src.database import get_async_session
from src.app.models import Playlist, crud_playlist_track, crud_playlist, crud_user, crud_track, User
from src.app.auth import auth_handler
from src.app.depend import plst_by_user
from src.app.schemas import (
    Login,
    UserRead,
    UserCreate,
    UserLogin,
    UserUpdate,
    TrackRead,
    TrackCreate,
    TrackSwap,
    PlaylistRead,
    PlaylistCreate,
    PlaylistUpdate,
    PlaylistDelete,
    PlaylistTrackCreate,
    PlaylistTrackUpdate,
    PlaylistTrackDelete,
)

router = APIRouter(prefix="/app", tags=["app"])


@router.post("/login")
async def login(
    data: Login,
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    session_id = await auth_handler.create_session(db_session, data)
    response = Response()
    response.set_cookie("session_id", str(session_id))
    return response


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    session_id=Cookie("session_id"),
):
    if session_id in [session.id for session in user.sessions]:
        await auth_handler.delete_session(db_session, session_id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logined")


@router.post("/user", status_code=201)
async def create_user(
    user_scheme: UserCreate,
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    await crud_user.create(db_session, user_scheme)
    return {"message": "User created successfully"}


@router.get("/user", response_model=UserRead, status_code=200)
async def get_user(
    username: str,
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    user = await crud_user.get_one_by_id(db_session, username, column="username")
    return UserRead.model_validate(user)


# ---------------- ---------------- ---------------- ---------------- ----------------


@router.post("/playlists/create", status_code=201)
async def create_playlist(
    playlist_scheme: PlaylistCreate,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlist_scheme.owner_id = user.id
    await crud_playlist.create(db_session, playlist_scheme)
    return {"message": "Playlist created successfully"}


@router.get("/playlists/getall", status_code=200)
async def get_playlists(
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlists = await crud_playlist.get_many_by_value(db_session, user.id, "owner_id")
    return [PlaylistRead.model_validate(playlist) for playlist in playlists]


@router.post("/playlists/add_track")
async def add_track_to_playlist(
    yt_url: str,
    data: Annotated[Tuple[Playlist, User], Depends(plst_by_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlist, user = data
    try:
        yt_id = YTService.extract_youtube_video_id(yt_url)
        track_meta = YTService.get_basic_track_details(yt_id)
        track = await crud_track.get_one_by_id(db_session, yt_id, column="yt_id")

    except NotFoundException:
        track = await crud_track.create(db_session, TrackCreate(**track_meta._asdict()))  # type: ignore

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    playlist_track = PlaylistTrackCreate(
        playlist_id=playlist.id, track_id=track.id, position=playlist.tracks_amount + 1
    )
    await crud_playlist_track.create(db_session, playlist_track)
    await crud_playlist.update_by_id(db_session, PlaylistUpdate(tracks_amount=playlist.tracks_amount + 1), playlist.id)


@router.delete("/playlists/remove_track", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track_from_playlist(
    yt_id: str,
    data: Annotated[Tuple[Playlist, User], Depends(plst_by_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    try:
        playlist, user = data

        track = await crud_track.get_one_by_id(db_session, yt_id, column="yt_id")

        await crud_playlist_track.remove_by_track_and_playlist(db_session, track.id, playlist.id)
        return
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.put("/playlist/swap_tracks", status_code=status.HTTP_200_OK)
async def swap_tracks_positions(
    data: Annotated[Tuple[Playlist, User], Depends(plst_by_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
    schema: TrackSwap,
):
    playlist, user = data

    try:
        item1 = None
        item2 = None
        for item in playlist.playlist_tracks:
            if item.position == schema.track_1_pos:
                item1 = item
            elif item.position == schema.track_2_pos:
                item2 = item

            if item1 and item2:
                break

        if not (item1 and item2):
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        await crud_playlist_track.update_by_id(db_session, PlaylistTrackUpdate(position=item1.position), item2.id)
        await crud_playlist_track.update_by_id(db_session, PlaylistTrackUpdate(position=item2.position), item1.id)

    except NotFoundException:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
