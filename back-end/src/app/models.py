from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Integer, DateTime, delete, or_, select, literal
from sqlalchemy.dialects.postgresql import UUID as UUIDCOLUMN
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import NotFoundException, SnippetException, crud_factory as crud
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

    playlist: Mapped["Playlist"] = relationship(back_populates="playlist_tracks", lazy="joined")
    track: Mapped["Track"] = relationship(back_populates="playlist_tracks", lazy="joined")


class Track(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tracks"

    title: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    yt_id: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)

    playlist_tracks: Mapped[list["PlaylistTrack"]] = relationship(back_populates="track")
    features: Mapped["TrackFeature"] = relationship(back_populates="track")


class TrackFeature(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "track_features"
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

    spectral_flatness_mean: Mapped[float]
    spectral_flatness_var: Mapped[float]
    harmonic_percussive_ratio: Mapped[float]
    mel_entropy_mean: Mapped[float]
    mel_entropy_var: Mapped[float]

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

    def as_vector(self) -> list[float]:
        return [
            self.chroma_mean,
            self.chroma_var,
            self.rms_mean,
            self.rms_var,
            self.spectral_centroids_mean,
            self.spectral_centroids_var,
            self.spectral_bandwidth_mean,
            self.spectral_bandwidth_var,
            self.spectral_rolloff_mean,
            self.spectral_rolloff_var,
            self.spectral_contrast_mean,
            self.spectral_contrast_var,
            self.zero_crossing_rate_mean,
            self.zero_crossing_rate_var,
            self.tempo,
            self.spectral_flatness_mean,
            self.spectral_flatness_var,
            self.harmonic_percussive_ratio,
            self.mel_entropy_mean,
            self.mel_entropy_var,
            self.mfcc_1_mean,
            self.mfcc_1_var,
            self.mfcc_2_mean,
            self.mfcc_2_var,
            self.mfcc_3_mean,
            self.mfcc_3_var,
            self.mfcc_4_mean,
            self.mfcc_4_var,
            self.mfcc_5_mean,
            self.mfcc_5_var,
            self.mfcc_6_mean,
            self.mfcc_6_var,
            self.mfcc_7_mean,
            self.mfcc_7_var,
            self.mfcc_8_mean,
            self.mfcc_8_var,
            self.mfcc_9_mean,
            self.mfcc_9_var,
            self.mfcc_10_mean,
            self.mfcc_10_var,
            self.mfcc_11_mean,
            self.mfcc_11_var,
            self.mfcc_12_mean,
            self.mfcc_12_var,
            self.mfcc_13_mean,
            self.mfcc_13_var,
            self.mfcc_14_mean,
            self.mfcc_14_var,
            self.mfcc_15_mean,
            self.mfcc_15_var,
            self.mfcc_16_mean,
            self.mfcc_16_var,
            self.mfcc_17_mean,
            self.mfcc_17_var,
            self.mfcc_18_mean,
            self.mfcc_18_var,
            self.mfcc_19_mean,
            self.mfcc_19_var,
            self.mfcc_20_mean,
            self.mfcc_20_var,
        ]


class StatTrack(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tracks_stat"
    yt_id: Mapped[str] = mapped_column(ForeignKey("tracks.yt_id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    track_playback: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


crud_user = crud(User)
crud_playlist = crud(Playlist)

crud_session = crud(Session)


class crud_stat(crud(StatTrack)):
    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        yt_id: str,
        user_id: UUID,
    ):
        q = select(cls.model_class).where(cls.model_class.user_id == user_id).where(cls.model_class.yt_id == yt_id)

        result = await session.execute(q)
        entity = result.unique().scalar_one_or_none()
        if entity is None:
            raise NotFoundException("Not found")

        return entity


class crud_track(crud(Track)):
    @classmethod
    async def query_tracks(
        cls,
        session: AsyncSession,
        title: str,
    ):
        q = select(Track).where(
            or_(
                Track.title == title,
                Track.title.ilike(f"%{title}%"),
                literal(title).cast(String).ilike(f"%{{}}%".format(Track.title)),
            )
        )

        result = await session.execute(q)
        entity_list = result.unique().scalars().all()
        if entity_list is None or len(entity_list) == 0:
            raise NotFoundException(f"Not found tracks with: {title}")

        return entity_list


class crud_features(crud(TrackFeature)):
    @classmethod
    async def get_by_playlist(
        cls,
        session: AsyncSession,
        playlist_id: UUID,
    ):
        q = (
            select(TrackFeature)
            .join(Track, TrackFeature.track)  # join track_features → tracks
            .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)  # join tracks → playlist_tracks
            .join(Playlist, Playlist.id == PlaylistTrack.playlist_id)  # join playlist_tracks → playlists
            .where(Playlist.id == playlist_id)
        )
        result = await session.execute(q)
        entity_list = result.unique().scalars().all()
        if entity_list is None or len(entity_list) == 0:
            raise NotFoundException(f"Not found tracks features for playlist id: {playlist_id}")

        return entity_list


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
