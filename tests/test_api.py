import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base

TEST_DB_URL = "sqlite:///./test_metrics.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

GOOD_METRIC = {
    "rack_id": "rack-01",
    "temperature_c": 22.5,
    "power_draw_w": 1200.0,
    "fan_speed_rpm": 1800,
    "coolant_status": "ok",
}

HOT_METRIC = {
    "rack_id": "rack-02",
    "temperature_c": 42.0,
    "power_draw_w": 6000.0,
    "fan_speed_rpm": 300,
    "coolant_status": "critical",
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ingest_metric():
    r = client.post("/metrics", json=GOOD_METRIC)
    assert r.status_code == 201
    data = r.json()
    assert data["rack_id"] == "rack-01"
    assert data["temperature_c"] == 22.5
    assert "id" in data
    assert "recorded_at" in data


def test_list_metrics_empty():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.json() == []


def test_list_metrics():
    client.post("/metrics", json=GOOD_METRIC)
    client.post("/metrics", json=HOT_METRIC)
    r = client.get("/metrics")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_metrics_filter_by_rack():
    client.post("/metrics", json=GOOD_METRIC)
    client.post("/metrics", json=HOT_METRIC)
    r = client.get("/metrics?rack_id=rack-01")
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["rack_id"] == "rack-01"


def test_no_alerts_for_normal_metric():
    client.post("/metrics", json=GOOD_METRIC)
    r = client.get("/alerts")
    assert r.status_code == 200
    assert r.json() == []


def test_alerts_for_bad_metric():
    client.post("/metrics", json=HOT_METRIC)
    r = client.get("/alerts")
    assert r.status_code == 200
    alerts = r.json()
    alert_types = {a["alert_type"] for a in alerts}
    assert "HIGH_TEMPERATURE" in alert_types
    assert "HIGH_POWER_DRAW" in alert_types
    assert "LOW_FAN_SPEED" in alert_types
    assert "COOLANT_ISSUE" in alert_types


def test_invalid_limit():
    r = client.get("/metrics?limit=0")
    assert r.status_code == 400


def test_invalid_temperature():
    bad = {**GOOD_METRIC, "temperature_c": 200}
    r = client.post("/metrics", json=bad)
    assert r.status_code == 422
