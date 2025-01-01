from httpx import AsyncClient
from starlette import status


async def test_like_profile(
        authenticated_async_client: AsyncClient,
):
    liked_user_id = "503138d1-c175-401e-bd4f-f3ed543f7abf"
    body = {"liked_user_id": liked_user_id}
    response = await authenticated_async_client.post(url="/profile/like", json=body)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("liked_user_id") == liked_user_id


async def test_my_likes(
        authenticated_async_client: AsyncClient,
):
    response = await authenticated_async_client.get(url="/profile/likes")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
