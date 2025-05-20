from datetime import datetime, timedelta, UTC
from typing import Annotated
from uuid import UUID

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Config
from src.database import get_async_session
from src.app.schemas import Login, SessionCreate, UserRead
from src.app.models import User, crud_session, crud_user
from src.repository import NotFoundException


class AuthHandler:
    security = APIKeyCookie(name="session_id")

    async def create_session(
        self,
        db_session: Annotated[AsyncSession, Depends(get_async_session)],
        login_schema: Login,
    ) -> tuple[UUID, User]:
        try:
            user = await crud_user.get_one_by_id(db_session, login_schema.email, column="email")
        except NotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        session = await crud_session.create(
            db_session,
            SessionCreate(user_id=user.id, expires_at=datetime.now(tz=UTC) + timedelta(days=1)),  # type: ignore
        )
        return session.id, session.user

    async def delete_session(
        self,
        db_session: Annotated[AsyncSession, Depends(get_async_session)],
        session_id: UUID,
    ) -> None:
        try:
            await crud_session.remove_by_id(db_session, session_id, raise_not_found=True)
        except NotFoundException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def get_current_user(
        self,
        db_session: Annotated[AsyncSession, Depends(get_async_session)],
        session_id: str = Security(security),
    ) -> User:
        try:
            session = await crud_session.get_one_by_id(db_session, session_id)
            if session.expires_at < datetime.now(tz=UTC):  # type: ignore
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            user = await crud_user.get_one_by_id(db_session, session.user_id)  # type: ignore
            return user

        except NotFoundException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )


auth_handler = AuthHandler()
