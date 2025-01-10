from app.services.profiles import ProfilesService
from tests.dependensies.brokers import get_mocked_kafka_producer
from tests.dependensies.logger import get_mocked_logger
from tests.dependensies.repositories import (
    get_mocked_es_repository,
    get_mocked_redis_repository,
    get_mocked_s3_repository,
    get_test_profiles_pg_repository,
)


def get_test_profiles_service() -> ProfilesService:
    profiles_pg_repository = get_test_profiles_pg_repository()
    profiles_elastic_repository = get_mocked_es_repository()
    profile_queues_redis_repository = get_mocked_redis_repository()
    profiles_s3_repository = get_mocked_s3_repository()
    kafka_producer = get_mocked_kafka_producer()
    logger = get_mocked_logger()

    return ProfilesService(
        profiles_pg_repository=profiles_pg_repository,
        profiles_elastic_repository=profiles_elastic_repository,
        profile_queues_redis_repository=profile_queues_redis_repository,
        profiles_s3_repository=profiles_s3_repository,
        kafka_producer=kafka_producer,
        logger=logger,
    )
