from fastapi import APIRouter

from app.models.user import AuthResponse, UserLoginRequest, UserRegisterRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post("/register", response_model=AuthResponse)
async def register(payload: UserRegisterRequest) -> AuthResponse:
    return await auth_service.register(payload)


@router.post("/login", response_model=AuthResponse)
async def login(payload: UserLoginRequest) -> AuthResponse:
    return await auth_service.login(payload)
