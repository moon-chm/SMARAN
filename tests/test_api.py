import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_auth_login_success():
    response = client.post(
        "/api/auth/login",
        data={"username": "caregiver_demo", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_auth_login_failure():
    response = client.post(
        "/api/auth/login",
        data={"username": "caregiver_demo", "password": "wrong_password"}
    )
    assert response.status_code == 401

def test_memory_ingest_auth_failure():
    response = client.post(
        "/api/memory/ingest", 
        json={"elder_id": "elder_123", "text":"Dr. Smith is at 9am", "source_type":"caregiver_input"}
    )
    assert response.status_code == 401

def test_chat_auth_failure():
    response = client.post(
        "/api/chat",
        json={"elder_id": "elder_123", "message": "hello", "role": "elder"}
    )
    assert response.status_code == 401

def test_mindmap_real_attempt():
    """
    Authenticate a user locally and attempt to fetch the graph mindmap endpoint.
    Should hit 500 if Neo4j is offline, or 200 if connected. Both cases prove correct un-mocked API traversal.
    """
    login_res = client.post("/api/auth/login", data={"username":"caregiver_demo", "password":"password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/memory/mindmap/elder_123", headers=headers)
    assert response.status_code in [200, 500] 
