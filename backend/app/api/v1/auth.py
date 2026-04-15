"""Auth эндпоинты."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SendOTPRequest,
    TokenResponse,
    VerifyOTPRequest,
)
from app.schemas import MessageResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/send", status_code=status.HTTP_200_OK)
async def send_otp(body: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    result = await auth_service.send_otp(db, body.phone, body.purpose)
    dev_code = result.get("dev_code")
    if dev_code:
        return {"message": f"OTP (dev): {dev_code}", "dev_code": dev_code}
    return {"message": "OTP отправлен"}


@router.post("/otp/verify", status_code=status.HTTP_200_OK)
async def verify_otp(body: VerifyOTPRequest, request: Request, db: AsyncSession = Depends(get_db)):
    # Сначала проверяем, зарегистрирован ли пользователь
    from sqlalchemy import select
    from app.models.user import User
    result = await db.execute(
        select(User).where(User.phone == body.phone, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    is_registered = bool(user and user.is_active)

    # Если зарегистрирован — помечаем код использованным; если нет — оставляем для /register
    await auth_service.verify_otp(db, body.phone, body.code, body.purpose, mark_used=is_registered)

    if is_registered:
        ip = request.client.host if request.client else None
        tokens = await auth_service._create_session(db, user, ip_address=ip)
        return {
            "is_registered": True,
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": "bearer",
        }
    return {"is_registered": False}


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    user, tokens = await auth_service.register_user(db, body)
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip = request.client.host if request.client else None
    if body.otp_code:
        _user, tokens = await auth_service.login_with_otp(db, body.phone, body.otp_code, ip)
    elif body.password:
        _user, tokens = await auth_service.login_with_password(db, body.phone, body.password, ip)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Необходимо указать password или otp_code")
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_tokens(db, body.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.logout(db, body.refresh_token)
    return MessageResponse(message="Выход выполнен")


@router.post("/logout/all", response_model=MessageResponse)
async def logout_all(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    # Получаем user_id из токена
    from app.core.security import decode_token
    try:
        payload = decode_token(body.refresh_token, expected_type="refresh")
        user_id = payload.get("sub")
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Недействительный токен")
    await auth_service.logout_all(db, user_id)
    return MessageResponse(message="Все сессии завершены")
