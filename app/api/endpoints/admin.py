import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.crud.auth import (
    create_access_control,
    create_business_element,
    create_permission,
    create_role,
    get_access_control_by_id,
    get_access_control_by_role_and_resource,
    get_access_controls_by_role,
    get_all_business_elements,
    get_all_permissions,
    get_all_roles,
    get_business_element_by_id,
    get_permission_by_id,
    get_role_by_id,
    toggle_access_permission,
    update_access_control,
)
from app.crud.user import get_user_by_id
from app.database import get_db
from app.models.auth import AccessControl
from app.models.user import User
from app.schemas.access import (
    AccessControlCreate,
    AccessControlResponse,
    AccessControlUpdate,
    AccessRuleResponse,
    BusinessElementCreate,
    BusinessElementResponse,
    PermissionCreate,
    PermissionResponse,
    RoleCreate,
    RoleDetailResponse,
    RoleResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RoleResponse:
    db_role = create_role(db, role)
    return db_role


@router.get("/roles", response_model=list[RoleDetailResponse])
async def list_roles(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
) -> list[RoleDetailResponse]:
    roles = get_all_roles(db)
    result = []
    for role in roles:
        access_controls = get_access_controls_by_role(db, role.id)
        role_dict = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
            "access_controls": access_controls,
        }
        result.append(RoleDetailResponse(**role_dict))
    return result


@router.get("/roles/{role_id}", response_model=RoleDetailResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RoleDetailResponse:
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    access_controls = get_access_controls_by_role(db, role.id)
    role_dict = {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_active": role.is_active,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "access_controls": access_controls,
    }
    return RoleDetailResponse(**role_dict)


@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    if role in user.roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already has this role"
        )
    user.roles.append(role)
    db.commit()
    logger.info("Role '%s' assigned to user id=%s by admin id=%s", role.name, user_id, current_user.id)
    return {"message": f"Role '{role.name}' assigned to user '{user.username}'"}


@router.post(
    "/permissions",
    response_model=AccessControlResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_update_access_control(
    access_control: AccessControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AccessControlResponse:
    role = get_role_by_id(db, access_control.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    existing = get_access_control_by_role_and_resource(
        db, access_control.role_id, access_control.resource_type
    )
    if existing:
        update_data = AccessControlUpdate(
            can_create=access_control.can_create,
            can_read=access_control.can_read,
            can_update=access_control.can_update,
            can_delete=access_control.can_delete,
            can_read_all=access_control.can_read_all,
            can_export=access_control.can_export,
            can_admin=access_control.can_admin,
        )
        result = update_access_control(db, existing.id, update_data)
        return result
    else:
        result = create_access_control(db, access_control)
        return result


@router.get("/permissions", response_model=list[AccessControlResponse])
async def list_access_controls(
    role_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[AccessControlResponse]:
    if role_id:
        controls = get_access_controls_by_role(db, role_id)
    else:
        controls = db.query(AccessControl).all()
    return controls


@router.get("/permissions/{control_id}", response_model=AccessControlResponse)
async def get_access_control(
    control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AccessControlResponse:
    control = get_access_control_by_id(db, control_id)
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Access control not found"
        )
    return control


@router.patch("/permissions/{control_id}")
async def toggle_permission(
    control_id: int,
    permission: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    control = get_access_control_by_id(db, control_id)
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Access control not found"
        )
    result = toggle_access_permission(db, control_id, permission)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission name: {permission}",
        )
    return {
        "id": result.id,
        "role_id": result.role_id,
        "resource_type": result.resource_type,
        f"toggled_{permission}": getattr(
            result, f"can_{permission}" if permission not in ("read_all_permission", "update_all_permission") else (
                "can_read_all" if permission == "read_all_permission" else "can_admin"
            )
        ),
        "message": f"Permission '{permission}' toggled successfully",
    }


@router.put("/permissions/{control_id}", response_model=AccessControlResponse)
async def update_access_control_full(
    control_id: int,
    update_data: AccessControlUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AccessControlResponse:
    control = get_access_control_by_id(db, control_id)
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Access control not found"
        )
    result = update_access_control(db, control_id, update_data)
    return result


@router.post(
    "/business-elements",
    response_model=BusinessElementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_business_element(
    element: BusinessElementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BusinessElementResponse:
    db_element = create_business_element(db, element)
    return db_element


@router.get("/business-elements", response_model=list[BusinessElementResponse])
async def list_business_elements(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
) -> list[BusinessElementResponse]:
    elements = get_all_business_elements(db)
    return elements


@router.get("/business-elements/{element_id}", response_model=BusinessElementResponse)
async def get_business_element(
    element_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BusinessElementResponse:
    element = get_business_element_by_id(db, element_id)
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business element not found"
        )
    return element
