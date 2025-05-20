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

from src.repository import NotFoundException
from src.app.models import Track, crud_playlist, TrackFeature


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

        feature_names = (
            [
                "chroma_mean",
                "chroma_var",
                "rms_mean",
                "rms_var",
                "spectral_centroids_mean",
                "spectral_centroids_var",
                "spectral_bandwidth_mean",
                "spectral_bandwidth_var",
                "spectral_rolloff_mean",
                "spectral_rolloff_var",
                "spectral_contrast_mean",
                "spectral_contrast_var",
                "zero_crossing_rate_mean",
                "zero_crossing_rate_var",
                # "harmonic_mean",
                # "harmonic_var",
                # "percussive_mean",
                # "percussive_var",
                "tempo",
            ]
            + [f"mfcc_{i + 1}_mean" for i in range(20)]
            + [f"mfcc_{i + 1}_var" for i in range(20)]
        )

        # Убираем тишину
        audio_file, _ = lr.effects.trim(track.audio_data)

        # Общий STFT
        stft = np.abs(lr.stft(audio_file))

        # Вычисляем признаки
        zero_crossing_rate = lr.feature.zero_crossing_rate(audio_file)
        chroma_stft = lr.feature.chroma_stft(S=stft, sr=track.sr)
        rms = lr.feature.rms(S=stft)
        spectral_rolloff = lr.feature.spectral_rolloff(S=stft, sr=track.sr)
        spectral_bandwidth = lr.feature.spectral_bandwidth(S=stft, sr=track.sr)
        spectral_contrast = lr.feature.spectral_contrast(S=stft, sr=track.sr)
        spectral_centroids = lr.feature.spectral_centroid(S=stft, sr=track.sr)

        # MFCC
        mfcc = lr.feature.mfcc(S=lr.power_to_db(stft), sr=track.sr, n_mfcc=20)

        # Темп
        tempo, _ = lr.beat.beat_track(y=audio_file, sr=track.sr)

        # Убираем harmonic и percussive (ОЧЕНЬ медленные)
        # percussive = lr.effects.percussive(y=audio_file)
        # harmonic = lr.effects.harmonic(y=audio_file)

        feature_data = [
            chroma_stft.mean(),
            chroma_stft.var(),
            rms.mean(),
            rms.var(),
            spectral_centroids.mean(),
            spectral_centroids.var(),
            spectral_bandwidth.mean(),
            spectral_bandwidth.var(),
            spectral_rolloff.mean(),
            spectral_rolloff.var(),
            spectral_contrast.mean(),
            spectral_contrast.var(),
            zero_crossing_rate.mean(),
            zero_crossing_rate.var(),
            # harmonic.mean(), harmonic.var(),  # Убрали для ускорения
            # percussive.mean(), percussive.var(),
            tempo[0] if isinstance(tempo, np.ndarray) else tempo,
        ]

        for mfcc_i in mfcc:
            feature_data.append(mfcc_i.mean())
            feature_data.append(mfcc_i.var())

        result = {}
        for i, f in enumerate(feature_data):
            result[feature_names[i]] = f

        return result

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
    ) -> list[str]:
        """
        Генерация рекомендаций для всего плейлиста:
        - 70% треков по усреднённому вектору
        - 30% треков по голосованию ближайших соседей

        :param playlist: список объектов Track (каждый содержит features.to_vector())
        :param model: hnswlib.Index — обученный индекс по всем трекам
        :param id_lookup: dict[int, str] — отображение индекса → track_id
        :param top_n: общее число треков в рекомендациях
        :param diversity_k: сколько треков взять из голосования
        :param neighbors_per_track: сколько соседей использовать для голосования
        :return: список id рекомендованных треков
        """
        if not playlist:
            return []

        playlist_vectors = np.array([track.as_vector() for track in playlist])
        mean_vector = normalize([playlist_vectors.mean(axis=0)])

        # --- Этап 1: рекомендации по настроению (усреднённый вектор) ---

        mood_labels, _ = model.knn_query(mean_vector, k=top_n * 5)
        mood_candidates = mood_labels[0]

        playlist_ids = set(track.yt_id for track in playlist)
        recommended = []

        for idx in mood_candidates:
            track_id = id_lookup.get(idx)
            if track_id not in playlist_ids and track_id not in recommended:
                recommended.append(track_id)
            if len(recommended) >= top_n - diversity_k:
                break

        # --- Этап 2: рекомендации по голосованию соседей (разнообразие) ---
        vote_counter = Counter()
        for track in playlist:
            vector = normalize([track.as_vector()])
            labels, _ = model.knn_query(vector, k=neighbors_per_track)
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

        return recommended + diversity_part

    def build_recommendation_index(self, tracks: list[TrackFeature]):
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
