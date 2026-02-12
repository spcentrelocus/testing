# from typing import List, Any
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from pydantic import UUID4

# from app.api import deps
# from app.schemas.building import Building, BuildingCreate, BuildingUpdate
# from app.models.user import User
# from app.services import building_service

# router = APIRouter()

# @router.get("/", response_model=List[Building], summary="List Buildings", description="Retrieve all buildings owned by the current user.")
# async def read_buildings(
#     db: AsyncSession = Depends(deps.get_db),
#     skip: int = 0,
#     limit: int = 100,
#     current_user: User = Depends(deps.get_current_user),
# ) -> Any:
#     """
#     Retrieve buildings.
#     """
#     buildings = await building_service.get_user_buildings(
#         db, user_id=current_user.id, skip=skip, limit=limit
#     )
#     return buildings

# @router.post("/", response_model=dict, summary="Create Building", description="Create a new building entry.")
# async def create_building(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     building_in: BuildingCreate,
#     current_user: User = Depends(deps.get_current_user),
# ) -> Any:
#     """
#     Create new building.
#     """
#     building = await building_service.create_building(
#         db, building=building_in, user_id=current_user.id
#     )
#     return {
#         "building_id": building.id,
#         "status": "created"
#     }

# @router.get("/{building_id}", response_model=Building)
# async def read_building(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     building_id: UUID4,
#     current_user: User = Depends(deps.get_current_user),
# ) -> Any:
#     """
#     Get building by ID.
#     """
#     building = await building_service.get_building(db, building_id=building_id)
#     if not building:
#         raise HTTPException(status_code=404, detail="Building not found")
#     if building.user_id != current_user.id:
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     return building

# @router.patch("/{building_id}", response_model=Building)
# async def update_building(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     building_id: UUID4,
#     building_in: BuildingUpdate,
#     current_user: User = Depends(deps.get_current_user),
# ) -> Any:
#     """
#     Update a building.
#     """
#     building = await building_service.get_building(db, building_id=building_id)
#     if not building:
#         raise HTTPException(status_code=404, detail="Building not found")
#     if building.user_id != current_user.id:
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     building = await building_service.update_building(
#         db, db_building=building, building_update=building_in
#     )
#     return building

# @router.delete("/{building_id}", response_model=Building)
# async def delete_building(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     building_id: UUID4,
#     current_user: User = Depends(deps.get_current_user),
# ) -> Any:
#     """
#     Delete a building.
#     """
#     building = await building_service.get_building(db, building_id=building_id)
#     if not building:
#         raise HTTPException(status_code=404, detail="Building not found")
#     if building.user_id != current_user.id:
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     building = await building_service.delete_building(db, building_id=building_id)
#     return building



from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4, BaseModel
 
from app.api import deps
from app.schemas.building import Building, BuildingCreate, BuildingUpdate
from app.models.user import User
from app.services import building_service
from app.schemas.building import SuccessResponse, ErrorResponse
router = APIRouter()
 
 
 
@router.get("/", response_model=SuccessResponse, summary="List Buildings", description="Retrieve all buildings owned by the current user.")
async def read_buildings(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve buildings.
    """
    buildings = await building_service.get_user_buildings(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return SuccessResponse(
        code=status.HTTP_200_OK,
        message="Buildings retrieved successfully",
        data=[Building.model_validate(b).model_dump() for b in buildings]
    )
 
@router.post("/", response_model=SuccessResponse, summary="Create Building", description="Create a new building entry.")
async def create_building(
    *,
    db: AsyncSession = Depends(deps.get_db),
    building_in: BuildingCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new building.
    """
    building = await building_service.create_building(
        db, building=building_in, user_id=current_user.id
    )
    return SuccessResponse(
        code=status.HTTP_201_CREATED,
        message="Building created successfully",
        data={
            "building_id": building.id,
            "status": "created"
        }
    )
 
@router.get("/{building_id}", response_model=Any)
async def read_building(
    *,
    db: AsyncSession = Depends(deps.get_db),
    building_id: UUID4,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get building by ID.
    """
    building = await building_service.get_building(db, building_id=building_id)
    if not building:
        return ErrorResponse(
            code=status.HTTP_404_NOT_FOUND,
            message="Building not found"
        )
    if building.user_id != current_user.id:
        return ErrorResponse(
            code=status.HTTP_403_FORBIDDEN,
            message="Not enough permissions"
        )
    return SuccessResponse(
        code=status.HTTP_200_OK,
        message="Building details retrieved successfully",
        data=Building.model_validate(building).model_dump()
    )
 
@router.patch("/{building_id}", response_model=Any)
async def update_building(
    *,
    db: AsyncSession = Depends(deps.get_db),
    building_id: UUID4,
    building_in: BuildingUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a building.
    """
    building = await building_service.get_building(db, building_id=building_id)
    if not building:
        return ErrorResponse(
            code=status.HTTP_404_NOT_FOUND,
            message="Building not found"
        )
    if building.user_id != current_user.id:
        return ErrorResponse(
            code=status.HTTP_403_FORBIDDEN,
            message="Not enough permissions"
        )
    building = await building_service.update_building(
        db, db_building=building, building_update=building_in
    )
    return SuccessResponse(
        code=status.HTTP_200_OK,
        message="Building updated successfully",
        data=Building.model_validate(building).model_dump()
    )
 
@router.delete("/{building_id}", response_model=Any)
async def delete_building(
    *,
    db: AsyncSession = Depends(deps.get_db),
    building_id: UUID4,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a building.
    """
    building = await building_service.get_building(db, building_id=building_id)
    if not building:
        return ErrorResponse(
            code=status.HTTP_404_NOT_FOUND,
            message="Building not found"
        )
    if building.user_id != current_user.id:
        return ErrorResponse(
            code=status.HTTP_403_FORBIDDEN,
            message="Not enough permissions"
        )
    await building_service.delete_building(db, building_id=building_id)
    return SuccessResponse(
        code=status.HTTP_200_OK,
        message="Building deleted successfully"
    )