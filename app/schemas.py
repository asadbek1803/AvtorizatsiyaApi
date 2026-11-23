"""So'rov va javob sxemalari (Pydantic v2)."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["alisher"])
    full_name: str = Field(..., min_length=2, max_length=100, examples=["Alisher Navoiy"])
    password: str = Field(..., min_length=6, max_length=72, examples=["secret123"])
    phone_number: str = Field(..., min_length=5, max_length=30, examples=["+998901234567"])

    @field_validator("username", "full_name", "password", "phone_number")
    @classmethod
    def strip_value(cls, value: str) -> str:
        return value.strip()

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        allowed = set("+0123456789 -()")
        if set(value) - allowed or sum(char.isdigit() for char in value) < 5:
            raise ValueError("Telefon raqami noto'g'ri formatda")
        return value


class LoginRequest(BaseModel):
    """JSON orqali login qilish uchun (/login/json)."""

    username: str = Field(..., examples=["alisher"])
    password: str = Field(..., examples=["secret123"])


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class UserPublic(BaseModel):
    id: int
    username: str
    full_name: str
    phone_number: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token yashash muddati, soniyada")
    user: UserPublic
