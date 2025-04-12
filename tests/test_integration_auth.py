from unittest.mock import Mock, AsyncMock
import pytest
from sqlalchemy import select
from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "Yuliia",
    "email": "yul@gmail.com",
    "password": "11223344",
    "role": "user",
}

user_data_unique_email = {
    "username": "Yuliia",
    "email": "yulia@gmail.com",
    "password": "12345678",
    "role": "user",
}

user_data_unique = {
    "username": "Yulia",
    "email": "yulia@gmail.com",
    "password": "12345678",
    "role": "user",
}


def test_signup_same_email(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    assert (
        response.json()["detail"] == "Користувач з таким email вже існує"
    )


def test_signup_same_username(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data_unique_email)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "Користувач з таким іменем вже існує"


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data_unique.get("username"),
            "password": user_data_unique.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_confirm_email(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=Mock(confirmed=False))
    mock_user_service.confirmed_email = AsyncMock(return_value=True)
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirmed_email/token")
    assert response.status_code == 200
    assert response.json()["message"] == "Електронну пошту підтверджено"

    mock_get_email_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    mock_user_service.confirmed_email.assert_called_once_with("test_user@gmail.com")


@pytest.mark.asyncio
async def test_confirm_email_already_confirmed(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=Mock(confirmed=True))
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirmed_email/token")

    assert response.status_code == 200
    assert response.json()["message"] == "Ваша електронна пошта вже підтверджена"

    mock_get_email_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    mock_user_service.confirmed_email.assert_not_called()


@pytest.mark.asyncio
async def test_request_email(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)

    client.post("api/auth/register", json=user_data_unique)
    response = client.post(
        "api/auth/request_email", json={"email": user_data_unique["email"]}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Перевірте свою електронну пошту для підтвердження"


@pytest.mark.asyncio
async def test_request_email_already_confirmed(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.api.auth.send_confirm_email", mock_send_email)

    response = client.post("api/auth/request_email", json={"email": user_data["email"]})

    assert response.status_code == 200
    assert response.json()["message"] == "Ваша електронна пошта вже підтверджена"


@pytest.mark.asyncio
async def test_confirm_reset_password(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    mock_get_password_from_token = AsyncMock(return_value="new_hashed_password")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.api.auth.get_password_from_token", mock_get_password_from_token
    )

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(
        return_value=Mock(id=1, email="test_user@gmail.com")
    )
    mock_user_service.reset_password = AsyncMock(return_value=None)
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirm_reset_password/token")

    assert response.status_code == 200
    assert response.json()["message"] == "Пароль успішно змінено"

    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")
    mock_user_service.reset_password.assert_called_once_with(1, "new_hashed_password")


@pytest.mark.asyncio
async def test_confirm_reset_password_invalid_token(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value=None)
    mock_get_password_from_token = AsyncMock(return_value=None)
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.api.auth.get_password_from_token", mock_get_password_from_token
    )

    response = client.get("api/auth/confirm_reset_password/token")

    assert response.status_code == 400
    assert response.json()["detail"] == "Недійсний або прострочений токен"

    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")


@pytest.mark.asyncio
async def test_confirm_reset_password_user_not_found(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="test_user@gmail.com")
    mock_get_password_from_token = AsyncMock(return_value="new_hashed_password")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.api.auth.get_password_from_token", mock_get_password_from_token
    )

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=None)
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirm_reset_password/token")

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Користувача з такою електронною адресою не знайдено"
    )

    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("test_user@gmail.com")