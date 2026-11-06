from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import engine, get_db
from app.models import Base, RackMetric
from app.schemas import MetricIn, MetricOut, AlertOut
from app.alerts import check_alerts

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Datacenter Monitor",
    description="Receives and stores rack metrics; raises alerts when values exceed thresholds.",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/metrics", response_model=MetricOut, status_code=201)
def ingest_metric(payload: MetricIn, db: Session = Depends(get_db)):
    row = RackMetric(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/metrics", response_model=list[MetricOut])
def list_metrics(
    rack_id: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 1000")
    q = db.query(RackMetric).order_by(desc(RackMetric.recorded_at))
    if rack_id:
        q = q.filter(RackMetric.rack_id == rack_id)
    return q.limit(limit).all()


@app.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    rack_id: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 1000")
    q = db.query(RackMetric).order_by(desc(RackMetric.recorded_at))
    if rack_id:
        q = q.filter(RackMetric.rack_id == rack_id)
    rows = q.limit(limit).all()

    alerts: list[AlertOut] = []
    for row in rows:
        alerts.extend(check_alerts(row))
    return alerts
