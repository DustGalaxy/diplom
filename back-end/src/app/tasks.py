from loguru import logger

from src.broker_taskiq import broker
from src.database import async_session_maker

from src.app.models import crud_features
from src.app.schemas import TrackFeatures
from src.app.services import RecomendationService


@broker.task
async def track_features(yt_id: str):
    service = RecomendationService()
    a_dta = service.download_audio(yt_id)
    if not a_dta:
        raise ValueError(f"yt_id is invalid: {yt_id}")
    logger.info("✅ Track download complete. Start analysis...")

    features = service.get_sample_features(a_dta)
    logger.info("✅ Track analysis complete. Saving results...")
    features["yt_id"] = yt_id

    async with async_session_maker() as session:
        await crud_features.create(session, TrackFeatures.model_validate(features))
        logger.info("✅ Result seved.")

    logger.info("✅ Task complete.")


@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def build_recommendation_index():
    logger.info("Start build recommendation index. Fetch analisys data...")
    async with async_session_maker() as session:
        tracks = await crud_features.get_all(session)

    logger.info("✅ Fetch analisys data complete. Prepare data...")
    service = RecomendationService()
    service.build_recommendation_index(list(tracks[0]))

    logger.info("✅ Task complete.")
