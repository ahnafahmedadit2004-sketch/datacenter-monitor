from sqlalchemy import Column, Integer, Float, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class RackMetric(Base):
    __tablename__ = "rack_metrics"

    id = Column(Integer, primary_key=True, index=True)
    rack_id = Column(String, index=True, nullable=False)
    temperature_c = Column(Float, nullable=False)
    power_draw_w = Column(Float, nullable=False)
    fan_speed_rpm = Column(Integer, nullable=False)
    coolant_status = Column(String, nullable=False)  # "ok" | "warning" | "critical"
    recorded_at = Column(DateTime, server_default=func.now(), nullable=False)
