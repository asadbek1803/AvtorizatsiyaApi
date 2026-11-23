"""Registratsiya, login, refresh va himoyalangan endpointlar."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..database import get_connection
from ..schemas import LoginRequest, RefreshRequest, TokenResponse, UserPublic, UserRegister
from ..security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(tags=["Avtorizatsiya"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def _public_user(row: sqlite3.Row) -> UserPublic:
    """Faqat xavfsiz ma'lumotlarni qaytaradi (parol hech qachon chiqmaydi)."""
    return UserPublic(
        id=row["id"],
        username=row["username"],
        full_name=row["full_name"],
        phone_number=row["phone_number"],
        created_at=row["created_at"],
    )


def _token_response(row: sqlite3.Row) -> dict:
    return {
        "access_token": create_access_token(row["id"]),
        "refresh_token": create_refresh_token(row["id"]),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": _public_user(row),
    }


def _user_by_username(username: str) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()


def _user_by_id(user_id: int) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def _authenticate(username: str, password: str) -> dict:
    row = _user_by_username(username)
    if row is None or not verify_password(password, row["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username yoki parol noto'g'ri",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _token_response(row)


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    """Access token orqali foydalanuvchini aniqlaydi."""
    payload = decode_token(token, expected_type="access")
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token yaroqsiz")

    row = _user_by_id(user_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")
    return _public_user(row)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yangi foydalanuvchi ro'yxatdan o'tkazish",
)
def register(payload: UserRegister):
    hashed_password = hash_password(payload.password)
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """INSERT INTO users (username, full_name, phone_number, hashed_password)
                   VALUES (?, ?, ?, ?)""",
                (payload.username, payload.full_name, payload.phone_number, hashed_password),
            )
            row = connection.execute(
                "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
    except sqlite3.IntegrityError:
        if _user_by_username(payload.username) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Bu username allaqachon band"
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Bu telefon raqami allaqachon band"
        )

    # Ro'yxatdan o'tgach darhol tokenlar ham qaytariladi
    return _token_response(row)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login (Swagger 'Authorize' tugmasi uchun form ma'lumotlari)",
)
def login(form: OAuth2PasswordRequestForm = Depends()):
    return _authenticate(form.username, form.password)


@router.post(
    "/login/json",
    response_model=TokenResponse,
    summary="Login (JSON ko'rinishida)",
)
def login_json(payload: LoginRequest):
    return _authenticate(payload.username, payload.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh token orqali yangi token olish",
)
def refresh(payload: RefreshRequest):
    claims = decode_token(payload.refresh_token, expected_type="refresh")
    try:
        user_id = int(claims["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token yaroqsiz")

    row = _user_by_id(user_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")

    # access va refresh tokenlarning ikkalasi ham yangilanadi
    return _token_response(row)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Joriy foydalanuvchi ma'lumotlari (access token talab qiladi)",
)
def me(current_user: UserPublic = Depends(get_current_user)):
    return current_user
