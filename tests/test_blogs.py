from fastapi.testclient import TestClient
import pytest
from main import app
from httpx import AsyncClient

from tests.test_auth import login

client = TestClient(app)


@pytest.mark.anyio
async def test_create_blog_a(client: AsyncClient):
    token = await login(client, "testuserB", "password")
    response = await client.post(
        "/api/blogs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Blog",
            "content": "This is a test blog",
            "tags": ["tag1", "tag2"]
        }
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test Blog"


@pytest.mark.anyio
async def test_create_blog_b(client: AsyncClient):
    token = await login(client, "testuserB", "password")
    response = await client.post(
        "/api/blogs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Blog 2",
            "content": "This is a test blog",
            "tags": ["tag3"]
        }
    )

    assert response.status_code == 201


@pytest.mark.anyio
async def test_list_blogs_by_tag_preference(client: AsyncClient):
    token = await login(client, "testuserB", "password")
    response = await client.get(
        "/api/dashboard/blogs",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data[0]["title"] == "Test Blog 2"

