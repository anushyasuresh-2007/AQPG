"""Authentication endpoints for user login and registration."""

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.user import create_user, get_user_by_email
from app.database.database import get_db
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError, Exception):
        return False



def hash_password(password: str) -> str:
    """Hash a plain password for storage."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict) -> str:
    """Create a JWT access token for an authenticated user."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, str(user_data.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(user_data.password)

    created_user = create_user(
        db,
        {
            "name": user_data.name,
            "email": str(user_data.email),
            "password": hashed_password,
            "role": user_data.role,
        },
    )

    return created_user


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK, tags=["Auth"])
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, str(user_data.email))

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token({"sub": user.email, "role": user.role})
    return TokenResponse(access_token=access_token)