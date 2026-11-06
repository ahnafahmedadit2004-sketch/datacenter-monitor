from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class MetricIn(BaseModel):
    rack_id: str
    temperature_c: float = Field(..., ge=-10, le=100)
    power_draw_w: float = Field(..., ge=0)
    fan_speed_rpm: int = Field(..., ge=0)
    coolant_status: Literal["ok", "warning", "critical"]


class MetricOut(MetricIn):
    id: int
    recorded_at: datetime

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    rack_id: str
    alert_type: str
    value: float | int | str
    threshold: float | int | str
    recorded_at: datetime
