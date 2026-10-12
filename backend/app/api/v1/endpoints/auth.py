from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
)
from app.schemas.common import SuccessMessageResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    BadRequestException,
)
from app.core.rate_limit import limiter
from app.api.deps import get_current_user

router = APIRouter()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    # Refresh token cookie (httpOnly, secure in prod)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        samesite="lax",
        secure=(settings.ENVIRONMENT == "production"),
        path="/api/v1/auth",
    )
    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=(settings.ENVIRONMENT == "production"),
        path="/",
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH_PER_MINUTE)
def register(
    request: Request,
    payload: UserRegisterRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing:
        raise ConflictException(f"User with email '{payload.email}' already exists.")

    user = User(
        email=payload.email.lower().strip(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=str(user.id), extra_claims={"email": user.email})
    refresh_token = create_refresh_token(subject=str(user.id))

    _set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH_PER_MINUTE)
def login(
    request: Request,
    payload: UserLoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password.")

    if not user.is_active:
        raise UnauthorizedException("User account is disabled.")

    access_token = create_access_token(subject=str(user.id), extra_claims={"email": user.email})
    refresh_token = create_refresh_token(subject=str(user.id))

    _set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH_PER_MINUTE)
def refresh_token(
    request: Request,
    response: Response,
    body: Optional[RefreshTokenRequest] = None,
    db: Session = Depends(get_db)
):
    token: Optional[str] = None
    if body and body.refresh_token:
        token = body.refresh_token
    elif "refresh_token" in request.cookies:
        token = request.cookies.get("refresh_token")

    if not token:
        raise UnauthorizedException("Refresh token required.")

    try:
        payload = decode_token(token)
    except Exception:
        raise UnauthorizedException("Invalid or expired refresh token.")

    if payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid token type. Expected refresh token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token payload missing subject.")

    user = db.query(User).filter(User.id == int(user_id_str)).first()
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive.")

    new_access_token = create_access_token(subject=str(user.id), extra_claims={"email": user.email})
    new_refresh_token = create_refresh_token(subject=str(user.id))

    _set_auth_cookies(response, new_access_token, new_refresh_token)

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=SuccessMessageResponse)
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    return SuccessMessageResponse(message="Successfully logged out.")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
