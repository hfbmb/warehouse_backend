from fastapi.testclient import TestClient
from fast_api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {"success": "hellow world"}