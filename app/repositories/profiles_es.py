from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch, BadRequestError

from app.configs.main import settings
from app.exceptions.profiles import ProfileNotCompletedException
from app.interfaces.repositories import ProfilesElasticRepositoryInterface
from app.schemas.users import UserDocumentSchema, UserSchema


class ProfilesElasticRepository(ProfilesElasticRepositoryInterface):
    def __init__(
            self,
            es_client: AsyncElasticsearch,
            users_index: str = "users",
    ):
        self.es_client = es_client
        self.users_index = users_index

    async def update_user_document(self, user: UserSchema) -> None:
        user_document = UserDocumentSchema(**user.dict())
        async with self.es_client as client:
            await client.update(
                index=self.users_index,
                id=user.user_id,
                doc=user_document.dict(exclude_unset=True),
                doc_as_upsert=True,
            )

    async def get_users_queue(self, user: UserSchema) -> list[str]:
        query = {"query": {"bool": {
            "filter": [
                {"term": {"city.keyword": user.city}},
                {"bool": {"must_not": {"term": {"user_id.keyword": user.user_id}}}},
            ],
            "should": [
                {"terms": {"interests": user.interests}},
            ],
            "minimum_should_match": 0,
        }}}
        try:
            async with self.es_client as client:
                result = await client.search(
                    body=query,
                    index=self.users_index,
                )
        except BadRequestError:
            raise ProfileNotCompletedException
        users = self._get_hits(result)
        user_ids = [user["user_id"] for user in users]
        return user_ids

    @staticmethod
    def _get_hits(result: ObjectApiResponse) -> list[dict]:
        hits = result.body["hits"]["hits"]
        result = [data["_source"] for data in hits]
        return result


def get_profiles_es_repository() -> ProfilesElasticRepository:
    es_client = AsyncElasticsearch(hosts=[settings.elastic.ELASTIC_URL])
    return ProfilesElasticRepository(es_client)
