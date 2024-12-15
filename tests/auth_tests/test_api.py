import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.parametrize("id, first_name, last_name, username, photo_url, auth_date, hash, status_code", [
    (123456789, "Alice", "Smith", "alice_smith", "https://t.me/i/userpic/320/alice_smith.jpg", 1700000000,
     "8148c1689fdc140a4a7b6c2182718f49d80b69588986c9412d37bcef5e974c5a", 200),
    (123456789, "Alice", "Smith", "alice_smith", "https://t.me/i/userpic/320/alice_smith.jpg", 1700000000,
     "invalid_hash", 400),
    (123456789, None, "Alice", "alice_smith", "https://t.me/i/userpic/320/alice_smith.jpg", 1700000000,
     "8148c1689fdc140a4a7b6c2182718f49d80b69588986c9412d37bcef5e974c5a", 422),
])
async def test_auth_token(
        id: int,
        first_name: str,
        last_name: str,
        username: str,
        photo_url: str,
        auth_date: int,
        hash: str,
        status_code: int,
        async_client: AsyncClient,
):
    response = await async_client.post(url="/auth/token", json={
        "id": id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "photo_url": photo_url,
        "auth_date": auth_date,
        "hash": hash,
    })
    assert response.status_code == status_code


async def test_get_me(
        async_client: AsyncClient,
        authenticated_async_client: AsyncClient,
):
    response = await async_client.get(url="/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = await authenticated_async_client.get(url="/auth/me")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "Alice"


async def test_update_me(
        async_client: AsyncClient,
        authenticated_async_client: AsyncClient,
):
    body = {"name": "George", "age": 29, "sex": "M"}
    response = await async_client.put(url="/auth/me", json=body)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response = await authenticated_async_client.put(url="/auth/me", json=body)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "George"
    body = {"name": "David"}
    response = await authenticated_async_client.put(url="/auth/me", json=body)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "David"
