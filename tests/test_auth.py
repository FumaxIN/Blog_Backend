from fastapi.testclient import TestClient
import pytest
from main import app

from httpx import AsyncClient

client = TestClient(app)


async def login(client: AsyncClient, username: str, password: str):
    response = await client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    return token


@pytest.mark.anyio
async def test_create_user_a(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "testuserA@gmail.com",
            "first_name": "Test",
            "last_name": "UserA",
            "password": "password",
            "username": "testuserA"
        }
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_create_user_b(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
             "email": "testuserB@gmail.com",
             "first_name": "Test",
             "last_name": "UserB",
             "tags": ["tag3"],
             "password": "password",
             "username": "testuserB"
        }
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_create_user_duplicate(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
                 "email": "testuserA@gmail.com",
                 "first_name": "Test",
                 "last_name": "UserA",
                 "password": "password",
                 "username": "testuserA"
             }
    )
    assert response.status_code == 400
