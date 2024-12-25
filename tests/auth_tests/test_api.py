from fastapi import status
from httpx import AsyncClient


async def test_auth_token_success(async_client: AsyncClient):
    response = await async_client.post(url="/profile/token", json={
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


async def test_auth_token_invalid_hash(async_client: AsyncClient):
    response = await async_client.post(url="/profile/token", json={
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


async def test_auth_token_missing_first_name(async_client: AsyncClient):
    response = await async_client.post(url="/profile/token", json={
        "id": 123456789,
        "first_name": None,
        "last_name": "Smith",
        "username": "alice_smith",
        "photo_url": "https://t.me/i/userpic/320/alice_smith.jpg",
        "auth_date": 1700000000,
        "hash": "8148c1689fdc140a4a7b6c2182718f49d80b69588986c9412d37bcef5e974c5a",
    })
    assert response.status_code == 422


async def test_get_me(
        async_client: AsyncClient,
        authenticated_async_client: AsyncClient,
):
    response = await async_client.get(url="/profile/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = await authenticated_async_client.get(url="/profile/me")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "Alice"


async def test_update_me(
        async_client: AsyncClient,
        authenticated_async_client: AsyncClient,
):
    body = {"name": "George", "age": 29, "sex": "M"}
    response = await async_client.put(url="/profile/me", json=body)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = await authenticated_async_client.put(url="/profile/me", json=body)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "George"
    body = {"name": "David"}
    response = await authenticated_async_client.put(url="/profile/me", json=body)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "David"
