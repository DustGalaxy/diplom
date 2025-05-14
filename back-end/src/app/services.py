import re
import io
from collections import namedtuple
from urllib.parse import urlparse, parse_qs

import librosa as lr
import pandas as pd
import numpy as np

from pytubefix import YouTube as YT
from pydub import AudioSegment
import soundfile as sf
from sklearn.neighbors import NearestNeighbors
from hnswlib import Index
from src.app.models import Track

TrackMeta = namedtuple("TrackDTO", ["yt_id", "title", "duration", "artist"])
AudioData = namedtuple("AudioDataDTO", ["audio_data", "sr"])


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
    model: NearestNeighbors

    def get_sample_features(self, track: AudioData) -> pd.DataFrame:
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

        return pd.DataFrame([feature_data], columns=feature_names)

    def download_audio(self, yt_id: str) -> AudioData | None:
        SR = 22050
        try:
            yt = YT.from_id(yt_id)
            audio_stream = yt.streams.filter(only_audio=True).first()
            if not audio_stream:
                print(f"Не удалось найти аудиопоток для {yt_id}")
                return None

            print(f"🔽 Скачивание: {yt.title}")
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
            print(f"❌ Ошибка при обработке {yt_id}: {e}")
            return None

    def recommend_similar_tracks(
        self, input_track_id: int, input_feature, top_n: int = 5, randomness: float = 0.1
    ) -> list[int]:
        """
        Рекомендует похожие треки с использованием UMAP и HNSWlib.

        Args:
            input_track_id (int): ID трека для рекомендаций
            top_n (int): Сколько треков рекомендовать
            randomness (float): Степень случайности в выдаче (0=без случайности, 1=максимальная)

        Returns:
            list[int]: Список рекомендованных track_id
        """
        input_feature = input_feature.reshape(1, -1)
        model = NearestNeighbors(metric="cosine")
        reduced_feature = reducer.transform(input_feature)

        # Ищем ближайшие треки
        distances, indices = model.kneighbors([target_feature_vector], n_neighbors=5)

        # Исключаем сам трек
        recommended_ids = [track_ids[label] for label in labels if track_ids[label] != input_track_id]

        # Немного случайности: перетасовываем, но ближние имеют больше шансов
        if randomness > 0:
            np.random.shuffle(recommended_ids)
            mix_count = int(len(recommended_ids) * randomness)
            recommended_ids[:mix_count] = np.random.choice(recommended_ids, size=mix_count, replace=False)

        return recommended_ids[:top_n]

    def recommend_for_playlist_knn(
        self,
        playlist: list[Track],
        model: Index,
        id_to_track: dict[int, "Track"],
        top_n: int = 10,
    ) -> list:
        if not playlist:
            raise ValueError("playlist не может быть пустым")

        playlist_vecs = np.array([track.features.as_vector() for track in playlist])
        avg_vec = playlist_vecs.mean(axis=0)

        labels, distances = model.knn_query(avg_vec, k=top_n * 5)
        labels = labels[0]

        playlist_ids = set(track.id for track in playlist)

        recommended = []
        for track_id in labels:
            if track_id not in playlist_ids:
                track = id_to_track.get(track_id)
                if track:
                    recommended.append(track)
            if len(recommended) >= top_n:
                break

        return recommended
