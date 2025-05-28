from datetime import datetime, date
import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from hnswlib import Index
from pytubefix.exceptions import VideoUnavailable


from src.config import Config
from src.repository import NotFoundException
from src.database import get_async_session

from src.app.services import RecomendationService, YTService, get_artist_popularity_by_date, plst_owned_by_user
from src.app.tasks import track_features
from src.app.models import (
    crud_features,
    crud_playlist_track,
    crud_playlist,
    crud_user,
    crud_track,
    User,
    crud_stat,
    crud_history,
)
from src.app.auth import auth_handler
from src.app.schemas import (
    UUID_,
    AddTrackToPlaylist,
    Login,
    PlaylistNewname,
    HistoryRead,
    StatCreate,
    StatTrackPlaybackRead,
    StatUpdate,
    UserRead,
    UserCreate,
    TrackRead,
    TrackRecommendRead,
    TrackCreate,
    TrackSwap,
    PlaylistRead,
    PlaylistCreate,
    PlaylistUpdate,
    PlaylistTrackCreate,
    PlaylistTrackUpdate,
    ArtistPopylarity,
)

router = APIRouter(prefix="/app", tags=["app"])


@router.post("/login")
async def login(
    data: Login,
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRead:
    session_id, user = await auth_handler.create_session(db_session, data)

    response.set_cookie("session_id", str(session_id), max_age=Config.SESSION_LIVE_TIME, secure=True, httponly=True)

    return UserRead.model_validate(user)


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


@router.post("/regestration", status_code=201)
async def create_user(
    user_scheme: UserCreate,
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRead:
    user = await crud_user.create(db_session, user_scheme)
    return UserRead.model_validate(user)


@router.get("/user", response_model=UserRead, status_code=200)
async def get_user(
    user: Annotated[User, Depends(auth_handler.get_current_user)],
):
    return UserRead.model_validate(user)


@router.get("/user/history", response_model=list[HistoryRead], status_code=200)
async def get_user_history(
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    history = await crud_history.get_many_by_value(db_session, value=user.id, column="user_id")
    tracks = await crud_track.get_many_by_ids(db_session, ids=[i.yt_id for i in history], column="yt_id")

    result = []
    for i in history:
        track = next(x for x in tracks if x.yt_id == i.yt_id)
        result.append(HistoryRead(datetime=i.created_at, track=TrackRead.model_validate(track)))
    return result


@router.post("/user/history", status_code=200)
async def send_user_history(
    yt_id: UUID_,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    await crud_history.create(db_session, StatCreate(yt_id=yt_id.id, user_id=user.id))


# ---------------- ---------------- ---------------- ---------------- ----------------


@router.get("/artist/popularity", status_code=200)
async def get_artist_popularity(
    start_date: date,
    end_date: date,
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    print(
        datetime(
            start_date.year,
            start_date.month,
            start_date.day,
        ),
        datetime(
            end_date.year,
            end_date.month,
            end_date.day,
        ),
    )
    popular_artists = await get_artist_popularity_by_date(
        db_session,
        datetime(
            start_date.year,
            start_date.month,
            start_date.day,
        ),
        datetime(
            end_date.year,
            end_date.month,
            end_date.day,
            23,
            59,
        ),
    )
    return [ArtistPopylarity(artist=artist, play_count=play_count) for artist, play_count in popular_artists]


@router.post("/playlists", status_code=201)
async def create_playlist(
    playlist_scheme: PlaylistCreate,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlist_scheme.owner_id = user.id
    playlist = await crud_playlist.create(db_session, playlist_scheme)
    return PlaylistRead.model_validate(playlist)


@router.get("/playlists", status_code=200)
async def get_playlists(
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlists = await crud_playlist.get_many_by_value(db_session, user.id, "owner_id")
    return [PlaylistRead.model_validate(playlist) for playlist in playlists]


@router.get("/tracks", status_code=200)
async def get_tracks_by_query(
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
    query: str = "",
):
    tracks = await crud_track.query_tracks(db_session, query)
    return [TrackRead.model_validate(track) for track in tracks]


@router.post("/track/stat", status_code=200)
async def add_listen(
    yt_id: UUID_,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    try:
        stat_obj = await crud_stat.get(db_session, yt_id.id, user.id)  # type: ignore
        await crud_stat.update_by_id(db_session, StatUpdate(track_playback=stat_obj + 1), stat_obj.id)
    except NotFoundException:
        await crud_stat.create(db_session, StatCreate(yt_id=yt_id.id, user_id=user.id))  # type: ignore


@router.get("/track/stat", status_code=200)
async def get_stat_track_playback(
    yt_id: str,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    try:
        stat_obj = await crud_stat.get(db_session, yt_id, user.id)  # type: ignore
        return StatTrackPlaybackRead(
            track_playback=stat_obj.track_playback,
        )
    except NotFoundException:
        return StatTrackPlaybackRead(
            track_playback=0,
        )


@router.get("/track_plst/stat", status_code=200)
async def get_stat_date_add_to_plst(
    playlist_id: UUID,
    track_id: UUID,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> dict[str, datetime]:
    playlist = await plst_owned_by_user(db_session, playlist_id, user.id)
    try:
        stat_obj = await crud_playlist_track.select_by_track_and_playlist(db_session, track_id, playlist_id)  # type: ignore
        return {"in_playlist_since": stat_obj.created_at}
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.get("/playlists/{plst_id}", status_code=200)
async def get_tracks(
    plst_id: UUID,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlist = await plst_owned_by_user(db_session, plst_id, user.id)

    # TODO sorting by position
    tracks_rel = await crud_playlist_track.get_many_by_value(db_session, playlist.id, "playlist_id")
    return [
        TrackRead(
            id=track_rel.track.id,
            yt_id=track_rel.track.yt_id,
            title=track_rel.track.title,
            artist=track_rel.track.artist,
            duration=track_rel.track.duration,
        )
        for track_rel in tracks_rel
    ]


@router.put("/playlists/{plst_id}", status_code=200)
async def rename_playlist(
    plst_id: UUID,
    new_name: PlaylistNewname,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlist = await plst_owned_by_user(db_session, plst_id, user.id)

    upd_playlist = await crud_playlist.update_by_id(db_session, new_name, playlist.id)
    return PlaylistRead.model_validate(upd_playlist)


@router.post("/playlists/add_track")
async def add_track_to_playlist(
    schema: AddTrackToPlaylist,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlist = await plst_owned_by_user(db_session, schema.playlist_id, user.id)

    try:
        yt_id = YTService.extract_youtube_video_id(schema.yt_url)
        track_meta = YTService.get_basic_track_details(yt_id)
        track = await crud_track.get_one_by_id(db_session, yt_id, column="yt_id")

    except (ValueError, VideoUnavailable) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundException:
        track = await crud_track.create(
            db_session,
            TrackCreate(
                yt_id=track_meta.yt_id,  # type: ignore
                title=track_meta.title,  # type: ignore
                artist=track_meta.artist,  # type: ignore
                duration=track_meta.duration,  # type: ignore
            ),
        )
        await track_features.kiq(yt_id)  # type: ignore

    playlist_track = PlaylistTrackCreate(
        playlist_id=playlist.id, track_id=track.id, position=playlist.tracks_amount + 1
    )
    await crud_playlist_track.create(db_session, playlist_track)
    await crud_playlist.update_by_id(db_session, PlaylistUpdate(tracks_amount=playlist.tracks_amount + 1), playlist.id)
    return TrackRead.model_validate(track)


@router.delete("/playlists/{plst_id}/remove_track", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track_from_playlist(
    track_id: UUID,
    plst_id: UUID,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    playlist = await plst_owned_by_user(db_session, plst_id, user.id)
    try:
        await crud_playlist_track.remove_by_track_and_playlist(db_session, track_id, playlist.id)
        await crud_playlist.update_by_id(
            db_session, PlaylistUpdate(tracks_amount=playlist.tracks_amount - 1), playlist.id
        )
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@router.put("/playlists/{plst_id}/swap_tracks", status_code=status.HTTP_200_OK)
async def swap_tracks_positions(
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
    schema: TrackSwap,
    plst_id: UUID,
):
    playlist = await plst_owned_by_user(db_session, plst_id, user.id)
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


@router.get("/playlists/{plst_id}/recommendations", status_code=status.HTTP_200_OK)
async def playlist_recomendations(
    plst_id: UUID,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    try:
        playlist = await plst_owned_by_user(db_session, plst_id, user.id)
        features = await crud_features.get_by_playlist(db_session, playlist.id)
        playlist_features = list(features)

        model = Index(space="cosine", dim=60)
        model.load_index("recommendations_cache/index.bin")

        id_lookup: dict[int, str] = {}
        with open("recommendations_cache/id_lookup.json", "r") as f:
            id_lookup_raw = json.loads(f.read())
            id_lookup = {int(k): v for k, v in id_lookup_raw.items()}

        service = RecomendationService()
        playlist_recomendations = service.recommend_tracks_for_playlist(
            playlist_features, model, id_lookup, with_scores=True
        )
        tracks = await crud_track.get_many_by_ids(db_session, [item[0] for item in playlist_recomendations], "yt_id")

        result = []

        for item in playlist_recomendations:
            track = next(x for x in tracks if x.yt_id == item[0])
            track.score = item[1]
            result.append(track)

        return [TrackRecommendRead.model_validate(track) for track in result]
    except NotFoundException:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
