from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BusinessElementBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    resource_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class BusinessElementCreate(BusinessElementBase):
    pass


class BusinessElementResponse(BusinessElementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    business_element_id: Optional[int] = None


class PermissionResponse(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_element_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class AccessRuleResponse(PermissionResponse):
    pass


class AssignRoleToUserRequest(BaseModel):
    user_id: int
    role_id: int


class AssignPermissionToRoleRequest(BaseModel):
    role_id: int
    permission_id: int


class AccessControlBase(BaseModel):
    resource_type: str = Field(..., min_length=1, max_length=100)
    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False
    can_read_all: bool = False
    can_export: bool = False
    can_admin: bool = False


class AccessControlCreate(AccessControlBase):
    role_id: int


class AccessControlUpdate(BaseModel):
    can_create: Optional[bool] = None
    can_read: Optional[bool] = None
    can_update: Optional[bool] = None
    can_delete: Optional[bool] = None
    can_read_all: Optional[bool] = None
    can_export: Optional[bool] = None
    can_admin: Optional[bool] = None
    is_enabled: Optional[bool] = None


class AccessControlResponse(AccessControlBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime


class RoleDetailResponse(RoleResponse):
    access_controls: List[AccessControlResponse] = []
