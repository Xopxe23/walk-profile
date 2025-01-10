from unittest.mock import MagicMock

from app.repositories.profiles_pg import ProfilesPostgresRepository
from tests.dependensies.database import get_test_session_maker


def get_test_profiles_pg_repository() -> ProfilesPostgresRepository:
    session_maker = get_test_session_maker()
    return ProfilesPostgresRepository(
        session_maker=session_maker,
    )


def get_mocked_es_repository():
    es_repository = MagicMock()
    es_repository.update_user_document = MagicMock()
    return es_repository


def get_mocked_s3_repository():
    es_repository = MagicMock()
    es_repository.upload_file = MagicMock()
    es_repository.get_client = MagicMock()
    return es_repository


def get_mocked_redis_repository():
    es_repository = MagicMock()
    es_repository.connect = MagicMock()
    es_repository.close = MagicMock()
    return es_repository
