import asyncio
import json
import os
import sys

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from app.database import Base
from app.main import app as fastapi_app
from app.models.users import Users
from app.services.profile import get_profiles_service
from tests.dependensies.database import async_session_maker, engine
from tests.dependensies.services import get_test_profiles_service

fastapi_app.dependency_overrides[get_profiles_service] = get_test_profiles_service


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f'tests/mocks/{model}.json', "r") as file:
            return json.load(file)

    users = open_mock_json("users")

    async with async_session_maker() as session:
        add_users = insert(Users).values(users)
        await session.execute(add_users)
        await session.commit()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="function")
async def authenticated_async_client():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as async_client:
        response = await async_client.post("/auth/token", json={
            "id": 123456789,
            "first_name": "Alice",
            "last_name": "Smith",
            "username": "alice_smith",
            "photo_url": "https://t.me/i/userpic/320/alice_smith.jpg",
            "auth_date": 1700000000,
            "hash": "8148c1689fdc140a4a7b6c2182718f49d80b69588986c9412d37bcef5e974c5a"
        })
        token = response.json().get("access_token")
        async_client.headers = {
            **async_client.headers,
            "Authorization": token,
        }
        yield async_client
