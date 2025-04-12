from unittest import mock
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status


test_user = {
    "id": 1,
    "username": "Yuliia",
    "email": "yul@gmail.com",
    "password": "11223344",
    "role": "user",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}

def test_get_me(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data


@pytest.mark.asyncio
async def test_me_unauthenticated(client, monkeypatch):
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не автентифіковано",
        )
    )
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_current_user)

    response = client.get("/api/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"