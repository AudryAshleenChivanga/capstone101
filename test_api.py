from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["screen_model_loaded"] is True

def test_recommend_screen_only():
    payload = {"age":30, "sex":"female", "epigastric_pain":1, "nausea":1}
    r = client.post("/recommend", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "screen_prob" in data
    assert "recommendations" in data
