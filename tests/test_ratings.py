# tests/test_ratings.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.database import Base, get_db
import logging

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"  # Use a separate test database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)  # Create tables
    db = TestingSessionLocal()  # Create the session
    yield db  # Provide the session to tests
    db.close()  # Close the session after tests
    Base.metadata.drop_all(bind=engine)  # Drop tables after tests

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def test_user(client):
    user_data = {"username": "testuser", "password": "testpassword","email": "testuser@example.com"}
    
    existing_user_response = client.post("/login", data={"username": user_data["username"], "password": user_data["password"]})
    if existing_user_response.status_code == 200:
        logger.info("User already exists, using existing user.")
        return existing_user_response.json()  # Return existing user data
    else:
        # Create the user if it doesn't exist
        response = client.post("/signup", json=user_data)
        if response.status_code != 200:
            logger.error(f"Error creating user: {response.json()}")
            raise AssertionError("Failed to create test user")
        else:
            logger.info(f"User created successfully: {response.json()}")
        return response.json()
    

@pytest.fixture(scope="function")
def test_movie(client, test_user):
    movie_data = {"title": "Test Movie", "description": "Test Description"}
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.post("/movies/", json=movie_data, headers=headers)
    logger.info(f"Movie creation response: {response.status_code}")
    assert response.status_code == 200
    return response.json()

def test_create_and_read_ratings(client, test_user, test_movie):
    # Create a rating first
    rating_data = {"score": 5.0, "movie_id": test_movie['id']}  # Use the correct key names for your schema
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    
    logger.info(f"Creating a rating for movie ID {test_movie['id']}")
    create_response = client.post(f"/movies/{test_movie['id']}/ratings", json=rating_data, headers=headers)
    logger.info(f"Rating creation response: {create_response.status_code}, {create_response.json()}")
    
    assert create_response.status_code == 200
    
    # Now read the ratings
    logger.info(f"Reading ratings for movie ID {test_movie['id']}")
    read_response = client.get(f"/movies/{test_movie['id']}/ratings", headers=headers)
    logger.info(f"Read ratings response: {read_response.status_code}, {read_response.json()}")
    
    assert read_response.status_code == 200
    ratings = read_response.json()
    assert isinstance(ratings, list)
    assert len(ratings) > 0  # Ensure that the list is not empty
    assert ratings[0]["score"] == 5.0  # Check if the rating is as expected
