from typing import Optional
import logging

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.crud.user import get_user_by_id
from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id: int = payload.get("user_id")
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


def check_permission(resource_type: str, required_action: str):
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User has no roles. Permission denied for {required_action}:{resource_type}",
            )
        permission_field_map = {
            "read": "can_read",
            "create": "can_create",
            "update": "can_update",
            "delete": "can_delete",
            "read_all_permission": "can_read_all",
            "export": "can_export",
            "update_all_permission": "can_admin",
        }
        permission_field = permission_field_map.get(required_action.lower())
        if not permission_field:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown permission action: {required_action}",
            )
        from app.crud.auth import get_access_controls_for_user

        access_controls = get_access_controls_for_user(db, current_user.id)
        for control in access_controls:
            if control.resource_type == resource_type and control.is_enabled:
                if getattr(control, permission_field, False):
                    return current_user
        logger.warning(
            "Permission denied for user id=%s: action=%s resource=%s",
            current_user.id, required_action, resource_type,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. Action '{required_action}' not allowed for resource '{resource_type}'",
        )

    return permission_checker
