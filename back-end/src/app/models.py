from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Integer, DateTime, delete, select
from sqlalchemy.dialects.postgresql import UUID as UUIDCOLUMN
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.repository import NotFoundException, SnippetException, crud_factory as crud, PydanticSchema
from src.database import TimestampMixin, UUIDMixin
from src.database import Base


class Session(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sessions"

    user_id: Mapped[UUID] = mapped_column(
        UUIDCOLUMN(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    playlists: Mapped[list["Playlist"]] = relationship(
        "Playlist",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Playlist(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "playlists"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
    )
    tracks_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        insert_default=0,
    )
    owner_id: Mapped[UUID] = mapped_column(
        UUIDCOLUMN(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    owner: Mapped[User] = relationship("User", back_populates="playlists")
    playlist_tracks: Mapped[list["PlaylistTrack"]] = relationship(back_populates="playlist")


class PlaylistTrack(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "playlist_tracks"

    playlist_id: Mapped[UUID] = mapped_column(ForeignKey("playlists.id"), nullable=False)
    track_id: Mapped[UUID] = mapped_column(ForeignKey("tracks.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    playlist: Mapped["Playlist"] = relationship(back_populates="playlist_tracks")
    track: Mapped["Track"] = relationship(back_populates="playlist_tracks")


class Track(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tracks"

    title: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    yt_id: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)

    playlist_tracks: Mapped[list["PlaylistTrack"]] = relationship(back_populates="track")
    features: Mapped["TrackFeatures"] = relationship(back_populates="track")


class TrackFeatures(Base, UUIDMixin, TimestampMixin):
    yt_id: Mapped[str] = mapped_column(String, ForeignKey("tracks.yt_id"))
    track: Mapped["Track"] = relationship(back_populates="features")

    chroma_mean: Mapped[float]
    chroma_var: Mapped[float]
    rms_mean: Mapped[float]
    rms_var: Mapped[float]
    spectral_centroids_mean: Mapped[float]
    spectral_centroids_var: Mapped[float]
    spectral_bandwidth_mean: Mapped[float]
    spectral_bandwidth_var: Mapped[float]
    spectral_rolloff_mean: Mapped[float]
    spectral_rolloff_var: Mapped[float]
    spectral_contrast_mean: Mapped[float]
    spectral_contrast_var: Mapped[float]
    zero_crossing_rate_mean: Mapped[float]
    zero_crossing_rate_var: Mapped[float]
    tempo: Mapped[float]

    mfcc_1_mean: Mapped[float]
    mfcc_1_var: Mapped[float]

    mfcc_2_mean: Mapped[float]
    mfcc_2_var: Mapped[float]

    mfcc_3_mean: Mapped[float]
    mfcc_3_var: Mapped[float]

    mfcc_4_mean: Mapped[float]
    mfcc_4_var: Mapped[float]

    mfcc_5_mean: Mapped[float]
    mfcc_5_var: Mapped[float]

    mfcc_6_mean: Mapped[float]
    mfcc_6_var: Mapped[float]

    mfcc_7_mean: Mapped[float]
    mfcc_7_var: Mapped[float]

    mfcc_8_mean: Mapped[float]
    mfcc_8_var: Mapped[float]

    mfcc_9_mean: Mapped[float]
    mfcc_9_var: Mapped[float]

    mfcc_10_mean: Mapped[float]
    mfcc_10_var: Mapped[float]

    mfcc_11_mean: Mapped[float]
    mfcc_11_var: Mapped[float]

    mfcc_12_mean: Mapped[float]
    mfcc_12_var: Mapped[float]

    mfcc_13_mean: Mapped[float]
    mfcc_13_var: Mapped[float]

    mfcc_14_mean: Mapped[float]
    mfcc_14_var: Mapped[float]

    mfcc_15_mean: Mapped[float]
    mfcc_15_var: Mapped[float]

    mfcc_16_mean: Mapped[float]
    mfcc_16_var: Mapped[float]

    mfcc_17_mean: Mapped[float]
    mfcc_17_var: Mapped[float]

    mfcc_18_mean: Mapped[float]
    mfcc_18_var: Mapped[float]

    mfcc_19_mean: Mapped[float]
    mfcc_19_var: Mapped[float]

    mfcc_20_mean: Mapped[float]
    mfcc_20_var: Mapped[float]


crud_user = crud(User)
crud_playlist = crud(Playlist)
crud_track = crud(Track)
crud_session = crud(Session)
crud_features = crud(TrackFeatures)


class crud_playlist_track(crud(PlaylistTrack)):
    @classmethod
    async def select_by_track_and_playlist(
        cls,
        session: AsyncSession,
        track_id: UUID,
        playlist_id: UUID,
    ):
        q = (
            select(cls.model_class)
            .where(cls.model_class.playlist_id == playlist_id)
            .where(cls.model_class.track_id == track_id)
        )
        result = await session.execute(q)
        entity = result.unique().scalar_one_or_none()
        if entity is None:
            raise NotFoundException(f"playlist_tracks with playlist_id={playlist_id} and track_id={track_id} not found")

        return entity

    @classmethod
    async def remove_by_track_and_playlist(
        cls,
        session: AsyncSession,
        track_id: UUID,
        playlist_id: UUID,
        raise_not_found: bool = False,
    ):
        q = (
            delete(cls.model_class)
            .where(cls.model_class.playlist_id == playlist_id)
            .where(cls.model_class.track_id == track_id)
        )
        try:
            result = await session.execute(q)
            await session.commit()

            if result.rowcount == 0 and raise_not_found:
                raise NotFoundException(
                    f"{cls.model_class.__tablename__} with track_id={track_id} and playlist_id={playlist_id} not found"
                )

            return result.rowcount
        except Exception as e:
            await session.rollback()
            if not isinstance(e, SnippetException):
                raise SnippetException(f"Failed to remove {cls.model_class.__tablename__}: {e}") from e
            raise
