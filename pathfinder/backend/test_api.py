from fastapi.testclient import TestClient
from app import app
import pytest

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_get_courses():
    response = client.get("/api/courses")
    assert response.status_code == 200
    data = response.json()
    assert "courses" in data
    assert "total" in data
    assert type(data["courses"]) == list

def test_career_paths():
    response = client.get("/api/career-paths")
    assert response.status_code == 200
    data = response.json()
    assert "career_paths" in data
    assert len(data["career_paths"]) > 0

def test_knowledge_graph():
    response = client.get("/api/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data

def test_chat_fallback():
    # Test chat endpoint
    response = client.post("/api/chat", json={"message": "hello", "user_id": "test_user"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
