import pytest
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
