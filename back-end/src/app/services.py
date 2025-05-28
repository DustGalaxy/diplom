from datetime import datetime
import re
import io
import json
from collections import Counter, namedtuple
from typing import List
from urllib.parse import urlparse, parse_qs
from uuid import UUID

from fastapi import HTTPException, status
from icecream import ic
from loguru import logger

import librosa as lr
import numpy as np
from sklearn.preprocessing import normalize
import soundfile as sf
from pytubefix import YouTube as YT
from pydub import AudioSegment
from sklearn.neighbors import NearestNeighbors
from hnswlib import Index
from sqlalchemy import and_, func, outerjoin, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import NotFoundException
from src.app.models import StatUserhistory, Track, crud_playlist, TrackFeature


TrackMeta = namedtuple("TrackDTO", ["yt_id", "title", "duration", "artist"])
AudioData = namedtuple("AudioDataDTO", ["audio_data", "sr"])


async def plst_owned_by_user(db_session, plst_id: UUID, user_id: UUID):
    try:
        playlist = await crud_playlist.get_one_by_id(db_session, plst_id)
        if playlist.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return playlist
    except NotFoundException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


async def get_artist_popularity_by_date(db_session: AsyncSession, start_date: datetime, end_date: datetime):
    # Сначала получаем статистику прослушиваний
    subquery = (
        select(StatUserhistory.yt_id, func.count().label("play_count"))
        .where(and_(StatUserhistory.created_at >= start_date, StatUserhistory.created_at <= end_date))
        .group_by(StatUserhistory.yt_id)
        .subquery()
    )

    # Затем джойним с треками
    stmt = (
        select(Track.artist, func.sum(subquery.c.play_count).label("total_plays"))
        .select_from(Track.__table__.join(subquery, Track.yt_id == subquery.c.yt_id))
        .group_by(Track.artist)
        .order_by(func.sum(subquery.c.play_count).desc())
    )

    result = await db_session.execute(stmt)
    return result.all()


class YTService:
    @classmethod
    def extract_youtube_video_id(cls, url: str) -> str:
        parsed_url = urlparse(url)

        # Если это короткая ссылка вида youtu.be/<id>
        if parsed_url.netloc in ("youtu.be", "www.youtu.be"):
            video_id = parsed_url.path.lstrip("/")
            if re.fullmatch(r"[0-9A-Za-z_-]{11}", video_id):
                return video_id

        # Если это ссылка с параметрами, типа youtube.com/watch?v=<id>
        if parsed_url.path == "/watch":
            query_params = parse_qs(parsed_url.query)
            if "v" in query_params:
                video_id = query_params["v"][0]
                if re.fullmatch(r"[0-9A-Za-z_-]{11}", video_id):
                    return video_id

        # Если это ссылка на embed или shorts
        match = re.search(r"/(embed|shorts)/([0-9A-Za-z_-]{11})", parsed_url.path)
        if match:
            return match.group(2)

        raise ValueError(f"Youtube url is invalid | url: {url}")

    @classmethod
    def get_basic_track_details(cls, yt_id: str) -> Track:
        track_data = YT.from_id(yt_id)
        track = Track(yt_id=yt_id, title=track_data.title, duration=track_data.length, artist=track_data.author)

        return track


class RecomendationService:
    def get_sample_features(self, track: AudioData) -> dict[str, float | str]:
        """Извлекает признаки из аудиофайла с оптимизациями"""
        audio_data, sr = track.audio_data, track.sr
        features = {}

        # Предобработка: trim + STFT
        y, _ = lr.effects.trim(audio_data)
        S = np.abs(lr.stft(y))
        S_db = lr.power_to_db(S**2)

        # 1. Стандартные признаки
        features["chroma_mean"] = lr.feature.chroma_stft(S=S, sr=sr).mean()
        features["chroma_var"] = lr.feature.chroma_stft(S=S, sr=sr).var()
        features["rms_mean"] = lr.feature.rms(S=S).mean()
        features["rms_var"] = lr.feature.rms(S=S).var()
        spectral_centroids = lr.feature.spectral_centroid(S=S, sr=sr)
        features["spectral_centroids_mean"] = spectral_centroids.mean()
        features["spectral_centroids_var"] = spectral_centroids.var()
        spectral_bandwidth = lr.feature.spectral_bandwidth(S=S, sr=sr)
        features["spectral_bandwidth_mean"] = spectral_bandwidth.mean()
        features["spectral_bandwidth_var"] = spectral_bandwidth.var()
        spectral_rolloff = lr.feature.spectral_rolloff(S=S, sr=sr)
        features["spectral_rolloff_mean"] = spectral_rolloff.mean()
        features["spectral_rolloff_var"] = spectral_rolloff.var()
        spectral_contrast = lr.feature.spectral_contrast(S=S, sr=sr)
        features["spectral_contrast_mean"] = spectral_contrast.mean()
        features["spectral_contrast_var"] = spectral_contrast.var()
        zcr = lr.feature.zero_crossing_rate(y)
        features["zero_crossing_rate_mean"] = zcr.mean()
        features["zero_crossing_rate_var"] = zcr.var()
        tempo, _ = lr.beat.beat_track(y=y, sr=sr)
        features["tempo"] = tempo

        # 2. MFCCs
        mfcc = lr.feature.mfcc(S=S_db, sr=sr, n_mfcc=20)
        for i in range(20):
            features[f"mfcc_{i + 1}_mean"] = mfcc[i].mean()
            features[f"mfcc_{i + 1}_var"] = mfcc[i].var()

        # 3. Дополнительные признаки

        # Спектральная плоскостность (шумность)
        flatness = lr.feature.spectral_flatness(S=S)
        features["spectral_flatness_mean"] = flatness.mean()
        features["spectral_flatness_var"] = flatness.var()

        # Гармоническая и перкуссионная энергия
        harmonic, percussive = lr.effects.hpss(y)
        features["harmonic_energy"] = np.mean(np.abs(harmonic))
        features["percussive_energy"] = np.mean(np.abs(percussive))
        features["harmonic_percussive_ratio"] = features["harmonic_energy"] / (features["percussive_energy"] + 1e-6)

        # Энтропия мелспектра
        mel = lr.feature.melspectrogram(y=y, sr=sr, S=S, n_mels=128)
        mel_norm = mel / (mel.sum(axis=0, keepdims=True) + 1e-6)
        entropy = -np.sum(mel_norm * np.log(mel_norm + 1e-6), axis=0)
        features["mel_entropy_mean"] = entropy.mean()
        features["mel_entropy_var"] = entropy.var()

        return features

    def download_audio(self, yt_id: str) -> AudioData | None:
        SR = 22050
        try:
            yt = YT.from_id(yt_id)
            audio_stream = yt.streams.filter(only_audio=True).first()
            if not audio_stream:
                logger.error(f"Not available streams for: {yt_id}")
                return None

            logger.info(f"🔽 Download: {yt.title}")
            with io.BytesIO() as memory_file:
                audio_stream.stream_to_buffer(memory_file)
                memory_file.seek(0)

                ext = audio_stream.subtype.lower()
                format_map = {
                    "m4a": "mp4",
                    "webm": "webm",
                    "mp4": "mp4",
                    "mp3": "mp3",
                }
                fmt = format_map.get(ext, ext)

                audio: AudioSegment = AudioSegment.from_file(memory_file, format=fmt)
                audio = audio.set_frame_rate(SR).set_channels(1).set_sample_width(2)

                with io.BytesIO() as raw_buffer:
                    audio.export(raw_buffer, format="wav")
                    raw_buffer.seek(0)

                    data, samplerate = sf.read(raw_buffer)

                # Если нужно точно SR=22050, ресемплируем
                if samplerate != SR:
                    import librosa

                    data = librosa.resample(data.T, orig_sr=samplerate, target_sr=SR).T
                    samplerate = SR

                return AudioData(data, samplerate)

        except Exception as e:
            logger.error(f"❌ Error on process {yt_id}: {e}")
            return None

    def recommend_tracks_for_playlist(
        self,
        playlist: List[TrackFeature],
        model: Index,
        id_lookup: dict[int, str],
        top_n: int = 10,
        diversity_k: int = 2,
        neighbors_per_track: int = 5,
        with_scores: bool = False,
    ) -> list[str] | list[tuple[str, float]]:
        if not playlist:
            return []

        playlist_vectors = np.array([track.as_vector() for track in playlist])
        mean_vector = normalize([playlist_vectors.mean(axis=0)])

        # --- Этап 1: по усреднённому вектору ---
        k1 = min(top_n * 5, model.get_current_count())
        mood_labels, distances = model.knn_query(mean_vector, k=k1)

        playlist_ids = set(track.yt_id for track in playlist)
        recommended: list[str] = []
        scores: dict[str, float] = {}

        for idx, dist in zip(mood_labels[0], distances[0]):
            track_id = id_lookup.get(idx, "")
            if track_id not in playlist_ids and track_id not in recommended:
                recommended.append(track_id)
                similarity = max(0.0, 1.0 - dist / 2.0)  # cosine ∈ [0,2]
                scores[track_id] = round(similarity * 100, 2)  # проценты
            if len(recommended) >= top_n - diversity_k:
                break

        # --- Этап 2: разнообразие через голосование ---
        vote_counter = Counter()
        for track in playlist:
            vector = normalize([track.as_vector()])
            k2 = min(neighbors_per_track, model.get_current_count())
            labels, _ = model.knn_query(vector, k=k2)
            for idx in labels[0]:
                track_id = id_lookup.get(idx)
                if track_id and track_id not in playlist_ids:
                    vote_counter[track_id] += 1

        diversity_part = []
        for track_id, _ in vote_counter.most_common():
            if track_id not in recommended:
                diversity_part.append(track_id)
            if len(diversity_part) >= diversity_k:
                break

        full_list = recommended + diversity_part
        if with_scores:
            return [(track_id, scores.get(track_id, 0.0)) for track_id in full_list]
        return full_list

    def build_recommendation_index(self, tracks: list[TrackFeature]):
        if not tracks:
            logger.warning("⚠  No track to build index.")
            return
        vectors = np.array([t.as_vector() for t in tracks])
        vectors = normalize(vectors)  # cosine

        ids = np.arange(len(tracks), dtype=np.int64)
        id_lookup = {i: str(t.yt_id) for i, t in enumerate(tracks)}

        logger.info("✅ Data prepare complete. Build index...")
        index = Index(space="cosine", dim=vectors.shape[1])
        index.init_index(max_elements=len(tracks), ef_construction=200, M=16)
        index.add_items(vectors, ids)

        logger.info("✅Index build complete. Save results...")
        index.save_index("recommendations_cache/index.bin")

        with open("recommendations_cache/id_lookup.json", "w") as f:
            json.dump(id_lookup, f)
        logger.info("✅ Result seved.")
