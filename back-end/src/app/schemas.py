from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime


class SessionCreate(BaseModel):
    user_id: UUID
    expires_at: datetime


class Login(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    email: EmailStr | None = None


class TrackCreate(BaseModel):
    yt_id: str
    title: str
    artist: str
    duration: int


class TrackRead(BaseModel):
    yt_id: str
    title: str | None = None
    artist: str | None = None
    duration: int | None = None

    model_config = ConfigDict(from_attributes=True)


class TrackSwap(BaseModel):
    track_1_pos: int
    track_2_pos: int


class PlaylistRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    tracks_amount: int
    traks: list[TrackRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PlaylistCreate(BaseModel):
    name: str
    description: str | None = None
    owner_id: UUID | None = None


class PlaylistUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    tracks_amount: int | None = None


class PlaylistDelete(BaseModel):
    uuid: UUID


class AddTrackToPlaylist(BaseModel):
    yt_id: str
    playlist_id: UUID


class PlaylistTrackCreate(BaseModel):
    playlist_id: UUID
    track_id: UUID
    position: int


class PlaylistTrackUpdate(BaseModel):
    position: int | None = None


class PlaylistTrackDelete(BaseModel):
    playlist_id: UUID
    track_id: UUID
