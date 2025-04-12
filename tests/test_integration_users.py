from unittest import mock
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status


user_data_admin = {
    "id": 1,
    "username": "Tima",
    "email": "tima@gmail.com",
    "password": "0991112233",
    "role": "admin",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}

user_data_not_admin = {
    "id": 1,
    "username": "Tima",
    "email": "tima@gmail.com",
    "password": "0991112233",
    "role": "user",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}


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