from fastapi.testclient import TestClient
import pytest
from main import app
from httpx import AsyncClient

from tests.test_auth import login

client = TestClient(app)



@pytest.mark.anyio
async def test_delete_user_a(client: AsyncClient):
    token = await login(client, "testuserA", "password")
    response = await client.delete(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_delete_user_b(client: AsyncClient):
    token = await login(client, "testuserB", "password")
    response = await client.delete(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200