from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import verify_password


def get_user_by_username_or_email(db: Session, identifier: str) -> Optional[User]:
    """
    Lookup user by exact username or email address.
    """
    clean_identifier = identifier.strip().lower()
    return db.query(User).filter(
        or_(
            User.username == identifier.strip(),
            User.email == clean_identifier
        )
    ).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Lookup user by primary key ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, identifier: str, password: str) -> User:
    """
    Verifies user credentials.
    Returns User if valid and active.
    Raises HTTP 401 for invalid credentials or inactive accounts.
    """
    user = get_user_by_username_or_email(db, identifier)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
