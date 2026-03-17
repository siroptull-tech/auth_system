from datetime import timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.database import get_db
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    db_user = get_user_by_email(db, user.email)
    if db_user:
        logger.warning("Registration failed: email already registered: %s", user.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    db_user = get_user_by_username(db, user.username)
    if db_user:
        logger.warning("Registration failed: username already taken: %s", user.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )
    db_user = create_user(db, user)
    logger.info("New user registered: id=%s email=%s", db_user.id, db_user.email)
    return db_user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning("Login failed: invalid credentials for email=%s", credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        logger.warning("Login failed: inactive user id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is not active"
        )
    access_token_expires = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email},
        expires_delta=access_token_expires,
    )
    logger.info("User logged in: id=%s email=%s", user.id, user.email)
    return TokenResponse(
        access_token=access_token, expires_in=int(access_token_expires.total_seconds())
    )


@router.post("/logout")
async def logout() -> dict:
    return {"message": "Successfully logged out"}
