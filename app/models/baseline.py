import uuid
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class BaselineHistory(Base):
    __tablename__ = "baseline_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"))
    period: Mapped[str] = mapped_column(String) # YYYY-MM
    
    raw_kwh: Mapped[float] = mapped_column(Float)
    adjusted_kwh: Mapped[float] = mapped_column(Float)
    weather_factor: Mapped[float] = mapped_column(Float, default=1.0)
    occupancy_factor: Mapped[float] = mapped_column(Float, default=1.0)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    building = relationship("Building")
