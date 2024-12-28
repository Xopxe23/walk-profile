from app.services.profile import ProfilesService
from tests.dependensies.brokers import get_mocked_kafka_producer
from tests.dependensies.logger import get_mocked_logger
from tests.dependensies.repositories import get_test_profiles_pg_repository


async def get_test_profiles_service() -> ProfilesService:
    profiles_pg_repository = get_test_profiles_pg_repository()
    kafka_producer = get_mocked_kafka_producer()
    logger = get_mocked_logger()

    return ProfilesService(
        profiles_pg_repository=profiles_pg_repository,
        kafka_producer=kafka_producer,
        logger=logger,
    )
