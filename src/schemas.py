from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.database.models import UserRole


class ContactModel(BaseModel):
    """
        Модель для створення або оновлення контакту.
    """
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(min_length=7, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    birthday: date
    info: Optional[str] = None


class ContactResponse(ContactModel):
    """
        Модель для відповіді при отриманні контакту з бази даних.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """
        Модель для представлення користувача.
    """
    id: int
    username: str
    email: str
    avatar: str | None
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
        Модель для створення нового користувача.
    """
    username: str
    email: str
    password: str
    role: UserRole


class Token(BaseModel):
    """
        Модель для повернення токену доступу.
    """
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
       Модель для запиту електронної пошти для відновлення паролю.
    """
    email: EmailStr

class ResetPassword(BaseModel):
    """
        Модель для скидання паролю.
    """
    email: EmailStr
    password: str = Field(min_length=4, max_length=128, description="Новий пароль")