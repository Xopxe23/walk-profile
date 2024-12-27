from sqlite3 import IntegrityError

from app.database import async_session_maker
from app.exceptions.auth import MatchExistsException
from app.models.matches import Matches
from app.schemas.matches import MatchCreateSchema, MatchSchema


class MatchesRepository:

    def __init__(self):
        self.model = Matches

    async def create_match(self, match_data: MatchCreateSchema) -> MatchSchema:
        match = self.model(
            **match_data.dict()
        )
        async with async_session_maker() as session:
            try:
                session.add(match)
                await session.commit()
            except IntegrityError:
                raise MatchExistsException
        return MatchSchema.model_validate(match)


def get_matches_repository() -> MatchesRepository:
    return MatchesRepository()
