from typing import Generator, Optional
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate the currently authenticated user from Bearer header or cookie."""
    token: Optional[str] = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if not token:
        raise UnauthorizedException("Authentication token required.")

    try:
        payload = decode_token(token)
    except Exception:
        raise UnauthorizedException("Invalid or expired authentication token.")

    token_type = payload.get("type")
    if token_type != "access":
        raise UnauthorizedException("Invalid token type. Expected access token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token payload missing subject.")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid token subject format.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("User not found.")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive.")

    return user
