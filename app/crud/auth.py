from sqlalchemy.orm import Session

from app.models.auth import AccessControl, BusinessElement, Permission, Role
from app.schemas.access import (
    AccessControlCreate,
    AccessControlUpdate,
    BusinessElementCreate,
    PermissionCreate,
    RoleCreate,
)


def get_role_by_id(db: Session, role_id: int) -> Role:
    return db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()


def get_role_by_name(db: Session, name: str) -> Role:
    return db.query(Role).filter(Role.name == name, Role.is_active == True).first()


def get_all_roles(db: Session) -> list[Role]:
    return db.query(Role).filter(Role.is_active == True).all()


def create_role(db: Session, role: RoleCreate) -> Role:
    db_role = Role(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_permission_by_id(db: Session, permission_id: int) -> Permission:
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_all_permissions(db: Session) -> list[Permission]:
    return db.query(Permission).all()


def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    db_permission = Permission(
        name=permission.name,
        action=permission.action,
        description=permission.description,
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def get_business_element_by_id(db: Session, element_id: int) -> BusinessElement:
    return db.query(BusinessElement).filter(BusinessElement.id == element_id).first()


def get_business_element_by_name(db: Session, name: str) -> BusinessElement:
    return db.query(BusinessElement).filter(BusinessElement.name == name).first()


def get_all_business_elements(db: Session) -> list[BusinessElement]:
    return db.query(BusinessElement).all()


def create_business_element(
    db: Session, element: BusinessElementCreate
) -> BusinessElement:
    db_element = BusinessElement(
        name=element.name,
        description=element.description,
        resource_type=element.resource_type,
    )
    db.add(db_element)
    db.commit()
    db.refresh(db_element)
    return db_element


def get_access_control_by_id(db: Session, control_id: int) -> AccessControl:
    return db.query(AccessControl).filter(AccessControl.id == control_id).first()


def get_access_controls_by_role(db: Session, role_id: int) -> list[AccessControl]:
    return db.query(AccessControl).filter(AccessControl.role_id == role_id).all()


def get_access_control_by_role_and_resource(
    db: Session, role_id: int, resource_type: str
) -> AccessControl:
    return (
        db.query(AccessControl)
        .filter(
            AccessControl.role_id == role_id,
            AccessControl.resource_type == resource_type,
        )
        .first()
    )


def create_access_control(db: Session, control: AccessControlCreate) -> AccessControl:
    existing = get_access_control_by_role_and_resource(
        db, control.role_id, control.resource_type
    )
    if existing:
        return existing
    db_control = AccessControl(
        role_id=control.role_id,
        resource_type=control.resource_type,
        can_create=control.can_create,
        can_read=control.can_read,
        can_update=control.can_update,
        can_delete=control.can_delete,
        can_read_all=control.can_read_all,
        can_export=control.can_export,
        can_admin=control.can_admin,
    )
    db.add(db_control)
    db.commit()
    db.refresh(db_control)
    return db_control


def update_access_control(
    db: Session, control_id: int, control_update: AccessControlUpdate
) -> AccessControl:
    db_control = get_access_control_by_id(db, control_id)
    if not db_control:
        return None
    if control_update.can_create is not None:
        db_control.can_create = control_update.can_create
    if control_update.can_read is not None:
        db_control.can_read = control_update.can_read
    if control_update.can_update is not None:
        db_control.can_update = control_update.can_update
    if control_update.can_delete is not None:
        db_control.can_delete = control_update.can_delete
    if control_update.can_read_all is not None:
        db_control.can_read_all = control_update.can_read_all
    if control_update.can_export is not None:
        db_control.can_export = control_update.can_export
    if control_update.can_admin is not None:
        db_control.can_admin = control_update.can_admin
    if control_update.is_enabled is not None:
        db_control.is_enabled = control_update.is_enabled
    db.commit()
    db.refresh(db_control)
    return db_control


def toggle_access_permission(
    db: Session, control_id: int, permission_name: str
) -> AccessControl:
    db_control = get_access_control_by_id(db, control_id)
    if not db_control:
        return None
    permission_field = {
        "create": "can_create",
        "read": "can_read",
        "update": "can_update",
        "delete": "can_delete",
        "read_all": "can_read_all",
        "export": "can_export",
        "admin": "can_admin",
    }.get(permission_name.lower())
    if permission_field and hasattr(db_control, permission_field):
        current_value = getattr(db_control, permission_field)
        setattr(db_control, permission_field, not current_value)
        db.commit()
        db.refresh(db_control)
    return db_control


def get_access_controls_for_user(db: Session, user_id: int) -> list[AccessControl]:
    from app.models.auth import Role, user_roles
    from app.models.user import User

    return (
        db.query(AccessControl)
        .join(Role, AccessControl.role_id == Role.id)
        .join(user_roles, Role.id == user_roles.c.role_id)
        .filter(user_roles.c.user_id == user_id)
        .all()
    )
