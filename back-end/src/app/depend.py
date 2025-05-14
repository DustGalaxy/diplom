from typing import Annotated
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from src.app.models import User, crud_playlist
from src.app.auth import auth_handler
from src.database import get_async_session
from src.repository import NotFoundException


async def plst_by_user(
    playlist_id: UUID,
    user: Annotated[User, Depends(auth_handler.get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
):
    try:
        playlist = await crud_playlist.get_one_by_id(db_session, playlist_id)
        if not playlist.owner_id == user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return playlist, user
