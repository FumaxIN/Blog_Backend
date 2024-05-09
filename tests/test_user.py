from fastapi.testclient import TestClient
import pytest
from main import app
from httpx import AsyncClient

from tests.test_auth import login

client = TestClient(app)


@pytest.mark.anyio
async def test_update_user(client: AsyncClient):
    token = await login(client, "testuserA", "password")
    response = await client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "newmail@gmail.com"
        }
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_add_tags(client: AsyncClient):
    token = await login(client, "testuserA", "password")
    response = await client.put(
        "/api/users/tags/add",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tags": ["tag1", "tag2"]
        }
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_remove_tags(client: AsyncClient):
    token = await login(client, "testuserA", "password")
    response = await client.put(
        "/api/users/tags/remove",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tags": ["tag1"]
        }
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_remove_invalid_tags(client: AsyncClient):
    token = await login(client, "testuserA", "password")
    response = await client.put(
        "/api/users/tags/remove",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "tags": ["tag3"]
        }
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_follow_user(client: AsyncClient):
    token = await login(client, "testuserA", "password")
    response = await client.post(
        "/api/users/follow",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "username": "testuserB"
        }
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_follow_invalid_user(client: AsyncClient):
    token = await login(client, "testuserA", "password")
    response = await client.post(
        "/api/users/follow",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "username": "testuserB"
        }
    )
