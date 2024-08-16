# tests/test_movies.py
import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Create a new engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()  # Create a session
    try:
        yield db  # Provide the session to tests
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)  # Drop tables after tests

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

@pytest.fixture
def token(client):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def create_movie(client, token):
    logger.info("Creating a new movie...")
    response = client.post(
        "/movies/",
        json={
            "title": "Inception",
            "description": "A mind-bending thriller",
            "release_year": 2010,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    logger.info(f"Movie creation response: {response.status_code}")
    assert response.status_code == 200
    return response.json()

def test_read_movie(client, create_movie, token):
    movie_id = create_movie["id"]
    logger.info(f"Attempting to read movie with ID: {movie_id}")
    response = client.get(f"/movies/{movie_id}", headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Read movie response: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["title"] == "Inception"

def test_update_movie(client, create_movie, token):
    movie_id = create_movie["id"]
    logger.info(f"Attempting to update movie with ID: {movie_id}")
    response = client.put(
        f"/movies/{movie_id}",
        json={
            "title": "Inception Updated",
            "description": "A mind-bending thriller",
            "release_year": 2010,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    logger.info(f"Update movie response: {response.status_code}")
    assert response.status_code == 200
    assert response.json()["title"] == "Inception Updated"

def test_delete_movie(client, create_movie, token):
    movie_id = create_movie["id"]
    logger.info(f"Attempting to delete movie with ID: {movie_id}")
    response = client.delete(f"/movies/{movie_id}", headers={"Authorization": f"Bearer {token}"})
    logger.info(f"Delete movie response: {response.status_code}")
    assert response.status_code == 200
