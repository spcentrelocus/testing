from pydantic import BaseModel, UUID4
from typing import Optional

class EmissionFactorBase(BaseModel):
    region_id: str
    region_name: str
    factor_kg_per_kwh: float
    year: int
    source: str

class EmissionFactorCreate(EmissionFactorBase):
    pass

class EmissionFactorUpdate(BaseModel):
    region_id: Optional[str] = None
    region_name: Optional[str] = None
    factor_kg_per_kwh: Optional[float] = None
    year: Optional[int] = None
    source: Optional[str] = None

class EmissionFactor(EmissionFactorBase):
    id: UUID4

    class Config:
        from_attributes = True
