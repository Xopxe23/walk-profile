from app.repositories.postgres import ProfilesPostgresRepository
from tests.dependensies.database import get_test_session_maker


def get_test_profiles_pg_repository() -> ProfilesPostgresRepository:
    session_maker = get_test_session_maker()
    return ProfilesPostgresRepository(
        session_maker=session_maker,
    )
