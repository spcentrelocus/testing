from pydantic import BaseModel, UUID4
from typing import Optional, Dict, Any, List
from datetime import datetime

# Shared properties
class BuildingBase(BaseModel):
    name: str
    address: Optional[str] = None
    building_type: Optional[str] = None
    area_sqft: Optional[float] = None
    timezone: Optional[str] = "UTC"
    utility_provider: Optional[str] = None
    occupancy_profile: Optional[Dict[str, Any]] = None

# Properties to receive via API on creation
class BuildingCreate(BuildingBase):
    pass

# Properties to receive via API on update
class BuildingUpdate(BuildingBase):
    name: Optional[str] = None # Name is optional on update, required on create

# Properties to return via API
class Building(BuildingBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BuildingCreateResponse(BaseModel):
    building_id: UUID4
    status: str


class SuccessResponse(BaseModel):
    success: bool = True
    status: str = "success"
    code: int
    message: str
    data: Optional[Any] = None
 
class ErrorResponse(BaseModel):
    success: bool = False
    status: str = "error"
    code: int
    message: str
    errors: Optional[Any] = None