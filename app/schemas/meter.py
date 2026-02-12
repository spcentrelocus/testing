from pydantic import BaseModel, UUID4, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class DataSource(str, Enum):
    API = "API"
    CSV = "CSV"
    MANUAL = "MANUAL"

class MeterReadingBase(BaseModel):
    time: datetime
    building_id: UUID4
    value_kwh: float
    source: DataSource = DataSource.API


class MeterReadingCreate(MeterReadingBase):
    pass

class MeterReading(MeterReadingBase):
    pass # No ID for time-series usually, or composite

class MeterReadingResponse(BaseModel):
    status: str
    count: int
