import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum

class DataSource(str, enum.Enum):
    API = "API"
    CSV = "CSV"
    MANUAL = "MANUAL"

class MeterReading(Base):
    __tablename__ = "meter_readings"

    # For TimescaleDB, the primary key must usually include the time column and partition key.
    # However, for pure insert speed, sometimes no PK is defined. 
    # Here we define a composite PK for uniqueness if needed, or just standard columns.
    
    time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), primary_key=True)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), primary_key=True)
    
    value_kwh: Mapped[float] = mapped_column(Float)
    source: Mapped[DataSource] = mapped_column(String)


    building = relationship("Building", back_populates="meter_readings")
