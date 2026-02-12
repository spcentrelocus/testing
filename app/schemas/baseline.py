from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime

class BaselineMonthData(BaseModel):
    period: str  # YYYY-MM
    kwh: float

class BaselineRequest(BaseModel):
    building_id: UUID4
    # Optional: if provided, use this data; else fetch from DB
    months: Optional[List[BaselineMonthData]] = None 
    method: str = "historical_12_months"

class BaselineNormalization(BaseModel):
    weather: bool
    occupancy: bool

class BaselineResponse(BaseModel):
    building_id: UUID4
    baseline_monthly_kwh: float
    method: str
    normalization: BaselineNormalization
