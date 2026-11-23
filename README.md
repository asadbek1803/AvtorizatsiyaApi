# Avtorizatsiya API (FastAPI + SQLite)

Ro'yxatdan o'tish, login, JWT `access_token` / `refresh_token` va himoyalangan endpoint.

## Ishga tushirish

```bash
cd "Avtorizatsiya API"
source env/bin/activate          # mavjud virtual muhit
pip install -r requirements.txt  # agar paketlar o'rnatilmagan bo'lsa
uvicorn app.main:app --reload
```

Swagger UI: **http://127.0.0.1:8000/docs** (ReDoc: `/redoc`)

## Endpointlar

| Method | URL | Tavsif |
|--------|-----|--------|
| POST | `/register` | `username`, `full_name`, `password`, `phone_number` bilan ro'yxatdan o'tish + darhol tokenlar |
| POST | `/login` | Username/parol (form-data), Swagger **Authorize** tugmasi bilan mos |
| POST | `/login/json` | Username/parol (JSON) |
| POST | `/refresh` | `refresh_token` bilan yangi access/refresh token olish |
| GET | `/me` | Access token talab qiladigan foydalanuvchi ma'lumoti |

`register`, `login`, `login/json` va `refresh` javoblari:

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "alisher",
    "full_name": "Alisher Navoiy",
    "phone_number": "+998901234567",
    "created_at": "2026-11-23T20:00:00Z"
  }
}
```

> Parol hech qachon javobda qaytarilmaydi — u bazada faqat bcrypt xesi sifatida saqlanadi.

## Misollar

```bash
# Ro'yxatdan o'tish
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alisher","full_name":"Alisher Navoiy","password":"secret123","phone_number":"+998901234567"}'

# Login (JSON)
curl -X POST http://127.0.0.1:8000/login/json \
  -H "Content-Type: application/json" \
  -d '{"username":"alisher","password":"secret123"}'

# Himoyalangan endpoint
curl http://127.0.0.1:8000/me -H "Authorization: Bearer <access_token>"

# Refresh
curl -X POST http://127.0.0.1:8000/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

## Sozlamalar (muhit o'zgaruvchilari)

| O'zgaruvchi | Standart qiymat |
|-------------|-----------------|
| `SECRET_KEY` | `dev-only-secret-key-change-me-in-production` (production da albatta o'zgartiring) |
| `DATABASE_PATH` | `./auth.db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |

Baza fayli `auth.db` birinchi ishga tushirishda avtomatik yaratiladi.
