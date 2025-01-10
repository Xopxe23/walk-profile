import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_token_success(async_client: AsyncClient):
    response = await async_client.post(url="/auth/token", json={
        "id": 123456789,
        "first_name": "Alice",
        "last_name": "Smith",
        "username": "alice_smith",
        "photo_url": "https://t.me/i/userpic/320/alice_smith.jpg",
        "auth_date": 1700000000,
        "hash": "8148c1689fdc140a4a7b6c2182718f49d80b69588986c9412d37bcef5e974c5a",
    })
    assert response.status_code == 200
    assert response.json().get("access_token")


@pytest.mark.asyncio
async def test_auth_token_invalid_hash(async_client: AsyncClient):
    response = await async_client.post(url="/auth/token", json={
        "id": 123456789,
        "first_name": "Alice",
        "last_name": "Smith",
        "username": "alice_smith",
        "photo_url": "https://t.me/i/userpic/320/alice_smith.jpg",
        "auth_date": 1700000000,
        "hash": "invalid_hash",
    })
    assert response.status_code == 400
    assert response.json().get("detail") == "Invalid telegram auth data"


@pytest.mark.asyncio
async def test_auth_token_missing_first_name(async_client: AsyncClient):
    response = await async_client.post(url="/auth/token", json={
        "id": 123456789,
        "first_name": None,
        "last_name": "Smith",
        "username": "alice_smith",
        "photo_url": "https://t.me/i/userpic/320/alice_smith.jpg",
        "auth_date": 1700000000,
        "hash": "8148c1689fdc140a4a7b6c2182718f49d80b69588986c9412d37bcef5e974c5a",
    })
    assert response.status_code == 422
