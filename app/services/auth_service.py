from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.database.mongodb import get_database
from app.models.user import AuthResponse, UserLoginRequest, UserRegisterRequest
from app.services.security_service import create_access_token, hash_password, verify_password


class AuthService:
    async def register(self, payload: UserRegisterRequest) -> AuthResponse:
        db = get_database()
        users_collection = db["users"]

        existing_user = await users_collection.find_one({"email": payload.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists.",
            )

        hashed_password = hash_password(payload.password)
        await users_collection.insert_one(
            {
                "email": payload.email,
                "full_name": payload.full_name,
                "password_hash": hashed_password,
                "created_at": datetime.now(timezone.utc),
            }
        )

        token = create_access_token(payload.email)
        return AuthResponse(access_token=token, user_email=payload.email)

    async def login(self, payload: UserLoginRequest) -> AuthResponse:
        db = get_database()
        users_collection = db["users"]

        user = await users_collection.find_one({"email": payload.email})
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        token = create_access_token(payload.email)
        return AuthResponse(access_token=token, user_email=payload.email)
