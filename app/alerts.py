from app.models import RackMetric
from app.schemas import AlertOut

THRESHOLDS = {
    "temperature_c": 35.0,
    "power_draw_w": 5000.0,
    "fan_speed_rpm": 500,
    "coolant_status": "ok",
}


def check_alerts(metric: RackMetric) -> list[AlertOut]:
    alerts = []

    if metric.temperature_c > THRESHOLDS["temperature_c"]:
        alerts.append(AlertOut(
            rack_id=metric.rack_id,
            alert_type="HIGH_TEMPERATURE",
            value=metric.temperature_c,
            threshold=THRESHOLDS["temperature_c"],
            recorded_at=metric.recorded_at,
        ))

    if metric.power_draw_w > THRESHOLDS["power_draw_w"]:
        alerts.append(AlertOut(
            rack_id=metric.rack_id,
            alert_type="HIGH_POWER_DRAW",
            value=metric.power_draw_w,
            threshold=THRESHOLDS["power_draw_w"],
            recorded_at=metric.recorded_at,
        ))

    if metric.fan_speed_rpm < THRESHOLDS["fan_speed_rpm"]:
        alerts.append(AlertOut(
            rack_id=metric.rack_id,
            alert_type="LOW_FAN_SPEED",
            value=metric.fan_speed_rpm,
            threshold=THRESHOLDS["fan_speed_rpm"],
            recorded_at=metric.recorded_at,
        ))

    if metric.coolant_status != THRESHOLDS["coolant_status"]:
        alerts.append(AlertOut(
            rack_id=metric.rack_id,
            alert_type="COOLANT_ISSUE",
            value=metric.coolant_status,
            threshold=THRESHOLDS["coolant_status"],
            recorded_at=metric.recorded_at,
        ))

    return alerts
