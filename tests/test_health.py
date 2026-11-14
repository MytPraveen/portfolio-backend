from fastapi.testclient import TestClient
from app.main import app

# Prevent database initialization during tests
app.router.on_startup.clear()

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Portfolio Backend Running",
        "status": "healthy"
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
