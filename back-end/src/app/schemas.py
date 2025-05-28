from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime


class UUID_(BaseModel):
    id: UUID | str


class StatCreate(BaseModel):
    yt_id: str
    user_id: UUID


class StatTrackPlaybackRead(BaseModel):
    track_playback: int


class StatUpdate(BaseModel):
    track_playback: int


class SessionCreate(BaseModel):
    user_id: UUID
    expires_at: datetime


class Login(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: UUID
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
    id: UUID
    yt_id: str
    title: str | None = None
    artist: str | None = None
    duration: int | None = None

    model_config = ConfigDict(from_attributes=True)


class TrackRecommendRead(TrackRead):
    score: float


class TrackSwap(BaseModel):
    track_1_pos: int
    track_2_pos: int


class PlaylistRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    tracks_amount: int
    # traks: list[TrackRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PlaylistCreate(BaseModel):
    name: str
    owner_id: UUID | None = None


class PlaylistNewname(BaseModel):
    name: str


class PlaylistUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    tracks_amount: int | None = None


class PlaylistID(BaseModel):
    id: UUID


class AddTrackToPlaylist(BaseModel):
    yt_url: str
    playlist_id: UUID


class PlaylistTrackCreate(BaseModel):
    playlist_id: UUID
    track_id: UUID
    position: int


class PlaylistTrackRead(BaseModel):
    playlist_id: UUID
    track_id: UUID


class PlaylistTrackUpdate(BaseModel):
    position: int | None = None


class PlaylistTrackDelete(BaseModel):
    playlist_id: UUID
    track_id: UUID


class TrackFeatures(BaseModel):
    yt_id: str

    chroma_mean: float
    chroma_var: float
    rms_mean: float
    rms_var: float
    spectral_centroids_mean: float
    spectral_centroids_var: float
    spectral_bandwidth_mean: float
    spectral_bandwidth_var: float
    spectral_rolloff_mean: float
    spectral_rolloff_var: float
    spectral_contrast_mean: float
    spectral_contrast_var: float
    zero_crossing_rate_mean: float
    zero_crossing_rate_var: float
    tempo: float

    spectral_flatness_mean: float
    spectral_flatness_var: float
    harmonic_percussive_ratio: float
    mel_entropy_mean: float
    mel_entropy_var: float

    mfcc_1_mean: float
    mfcc_1_var: float
    mfcc_2_mean: float
    mfcc_2_var: float
    mfcc_3_mean: float
    mfcc_3_var: float
    mfcc_4_mean: float
    mfcc_4_var: float
    mfcc_5_mean: float
    mfcc_5_var: float
    mfcc_6_mean: float
    mfcc_6_var: float
    mfcc_7_mean: float
    mfcc_7_var: float
    mfcc_8_mean: float
    mfcc_8_var: float
    mfcc_9_mean: float
    mfcc_9_var: float
    mfcc_10_mean: float
    mfcc_10_var: float
    mfcc_11_mean: float
    mfcc_11_var: float
    mfcc_12_mean: float
    mfcc_12_var: float
    mfcc_13_mean: float
    mfcc_13_var: float
    mfcc_14_mean: float
    mfcc_14_var: float
    mfcc_15_mean: float
    mfcc_15_var: float
    mfcc_16_mean: float
    mfcc_16_var: float
    mfcc_17_mean: float
    mfcc_17_var: float
    mfcc_18_mean: float
    mfcc_18_var: float
    mfcc_19_mean: float
    mfcc_19_var: float
    mfcc_20_mean: float
    mfcc_20_var: float
