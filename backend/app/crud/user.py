"""CRUD helpers for user authentication and account management."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Return a user by email address."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data: dict) -> User:
    """Create a new user record."""
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
