from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def get_all_active_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.password is not None:
        db_user.hashed_password = hash_password(user_update.password)
    db.commit()
    db.refresh(db_user)
    return db_user


def soft_delete_user(db: Session, user_id: int) -> User:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
