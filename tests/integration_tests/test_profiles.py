from fastapi import status
from httpx import AsyncClient


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
    body = {"name": "David", "age": 29}
    response = await authenticated_async_client.put(url="/profile/me", json=body)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("name") == "David"
